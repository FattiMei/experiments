import llvmlite.ir as ir
import llvmlite.binding as llvm
from kernel_gen import generate_reduction_kernel

import time
import ctypes
import argparse
import numpy as np


i32 = ir.IntType(32)
LLVM_TYPE_TO_CTYPES = {
    i32: ctypes.c_int32,
    ir.PointerType(): ctypes.c_void_p
}


def create_ctypes_signature(func: ir.Function) -> "_ctypes.PyCFuncPtrType":
    return_type = func.ftype.return_type
    args = func.ftype.args

    type_cast = lambda t: LLVM_TYPE_TO_CTYPES[t]

    return ctypes.CFUNCTYPE(
        type_cast(return_type),
        *map(type_cast, args)
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='reduction benchmark'
    )
    parser.add_argument('--npoints', type=int, help='numbers of data points', default=200)
    parser.add_argument('--min-exponent', type=int, default=10)
    parser.add_argument('--max-exponent', type=int, default=30)
    parser.add_argument('--disable-vectorization', action='store_true')
    parser.add_argument('--shuffle-iterations', action='store_true')
    args = parser.parse_args()


    # llvm initialization, including the JIT compilation
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    triple = llvm.get_default_triple()
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine()

    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)


    # generation of optimized reduction kernel, a standard optimization
    # pipeline is applied, based on the user requirements we could also
    # disable the vectorization
    func = generate_reduction_kernel(i32)
    mod = func.module
    modref = llvm.parse_assembly(str(mod))
    modref.verify()
    pto = llvm.create_pipeline_tuning_options(speed_level=3)
    pass_builder = llvm.create_pass_builder(target_machine, pto)
    mpm = pass_builder.getModulePassManager()
    mpm.run(modref, pass_builder)

    engine.add_module(modref)
    engine.finalize_object()
    engine.run_static_constructors()


    # wrapping the jitted function, assuming the signature is (ptr, T) -> T
    benchmark_function_name = func.name
    benchmark_function_address = engine.get_function_address(benchmark_function_name)
    benchmark_function_signature = create_ctypes_signature(func)
    benchmark_function = benchmark_function_signature(benchmark_function_address)


    # performing the benchmarking logic. For now, only a single run is profiled
    # for each buffer size.
    exponents = np.linspace(args.min_exponent, args.max_exponent, args.npoints)
    buffer_sizes = np.int32(2 ** exponents)
    max_buffer_size = buffer_sizes[-1]

    # the dtype of the buffer needs to be coupled with the dtype of the reduction!
    xs = np.random.randint(0, 1000, size=max_buffer_size, dtype=np.int32)
    runtimes = np.zeros(len(buffer_sizes))

    if args.shuffle_iterations:
        np.random.shuffle(runtimes)

    for (i,n) in enumerate(buffer_sizes):
        buffer_slice = xs[:n]
        expected = np.bitwise_xor.reduce(buffer_slice)

        start_time = time.perf_counter()
        actual = benchmark_function(
            xs.ctypes.data_as(ctypes.c_void_p),
            ctypes.c_int32(n)
        )
        end_time = time.perf_counter()

        assert(expected == actual)
        runtimes[i] = end_time - start_time


    # a final csv is printed to stdout. I have chosen to separate data generation
    # from data analysis as the generation phase could be long and I want to collect
    # data across many machines
    #
    # I should also write the generation parameters like the vectorization flag
    print('buffer_size_bytes,runtime_s')
    for (s,t) in zip(buffer_sizes, runtimes):
        print(f'{s},{t}')

