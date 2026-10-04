import llvmlite
import llvmlite.ir as ir
import llvmlite.binding as llvm
from kernel_gen import (
    generate_reduction_kernel,
    wrap_kernel
)

import time
import ctypes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    dtype = i32
    func = generate_reduction_kernel(dtype)
    wrapped = wrap_kernel(func)

    mod = func.module
    modref = llvm.parse_assembly(str(mod))
    modref.verify()

    triple = llvm.get_default_triple()
    target = llvm.Target.from_triple(triple)
    target_machine = target.create_target_machine()

    # application of a standard optimization pass
    # note that we don't really check if the benchmark code has been removed
    pto = llvm.create_pipeline_tuning_options(speed_level=2)
    pass_builder = llvm.create_pass_builder(target_machine, pto)
    mpm = pass_builder.getModulePassManager()
    mpm.run(modref, pass_builder)

    # JIT compilation of the module, copied from the llvmlite documentation
    engine = llvm.create_mcjit_compiler(modref, target_machine)
    engine.finalize_object()
    engine.run_static_constructors()

    # we assume the signature to be (ptr, T, int32) -> T
    benchmark_function_name = wrapped.name
    benchmark_function_address = engine.get_function_address(benchmark_function_name)
    benchmark_function_signature = create_ctypes_signature(wrapped)
    benchmark_function = benchmark_function_signature(benchmark_function_address)

    NPOINTS = 5
    NRUNS = 1
    MIN_EXPONENT = 10
    MAX_EXPONENT = 23
    exponents = np.linspace(MIN_EXPONENT, MAX_EXPONENT, NPOINTS)
    buffer_sizes = np.int32(np.floor(2 ** exponents))
    max_buffer_size = buffer_sizes[-1]

    runtimes = np.zeros_like(buffer_sizes)
    xs = np.random.randint(low=0, high=1000, size=max_buffer_size)

    for i in range(len(buffer_sizes)):
        n = buffer_sizes[i]
        buffer_slice = xs[:n]
        print(f'run with {n} elements')

        checksum = np.bitwise_xor.reduce(buffer_slice)

        start_time = time.perf_counter()
        res = benchmark_function(
            xs.ctypes.data_as(ctypes.c_void_p),
            ctypes.c_int32(n),
            ctypes.c_int32(NRUNS)
        )
        end_time = time.perf_counter()
        assert(res == checksum)

        runtimes[i] = (end_time - start_time) / NRUNS

    runtimes = buffer_sizes
    plt.plot(buffer_sizes, runtimes)
    plt.xscale('log')
    plt.show()

