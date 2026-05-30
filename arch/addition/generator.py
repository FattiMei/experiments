import argparse
import llvmlite.ir as ir
import llvmlite.binding as llvm


I8   = (  'int8_t', ir.IntType(8))
I16  = ( 'int16_t', ir.IntType(16))
I32  = ( 'int32_t', ir.IntType(32))
I64  = ( 'int64_t', ir.IntType(64))
U8   = ( 'uint8_t', ir.IntType(8))
U16  = ('uint16_t', ir.IntType(16))
U32  = ('uint32_t', ir.IntType(32))
U64  = ('uint64_t', ir.IntType(64))
I128 = ('int128_t', ir.IntType(128))
F16  = ( 'float16', ir.HalfType())
F32  = ( 'float32', ir.FloatType())
F64  = ( 'float64', ir.DoubleType())


def generate_add_function(module: ir.module.Module, name: str, dtype):
    """
    Appends to the module the implementation of a function of signature
      (dtype, dtype) -> dtype
    """
    func = ir.Function(
        module,
        ftype=ir.FunctionType(dtype, (dtype, dtype)),
        name=f'add_{name}'
    )
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    a, b = func.args

    if type(dtype) == ir.types.IntType:
        add_func = builder.add
    elif dtype in (ir.types.HalfType(), ir.types.FloatType(), ir.types.DoubleType()):
        add_func = builder.fadd
    else:
        raise TypeError(f'Unsupported addition between {dtype}')

    result = add_func(a, b)
    builder.ret(result)


def filter_asm(asm: str) -> str:
    return '\n'.join(
        filter(
            lambda l: not l.strip().startswith('.'),
            asm.splitlines()
        )
    )


TRIPLES = [
    "x86_64-pc-linux-gnu",
    "arm-linux-gnueabihf",
    "aarch64-unknown-linux-gnu"
]


NUMERIC_TYPES = [I8, U8, I16, U16, I32, U32, I64, U64, I128, F16, F32, F64]


if __name__ == '__main__':
    parser = argparse.ArgumentParser("add_asm_gen")
    parser.add_argument(
        '--triple',
        type=str,
        help=f"for example {', '.join(TRIPLES)}"
    )
    args = parser.parse_args()

    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()

    triple = args.triple
    cpu = 'generic'
    features = ''

    if triple is None:
        triple = llvm.get_default_triple()
        cpu = llvm.get_host_cpu_name()
        features = llvm.get_host_cpu_features().flatten()

    # I suspect some optimizations are done at target level,
    # so at a lower level than LLVM IR, possibly at MachineIR
    try:
        target = llvm.Target.from_triple(triple)
    except RuntimeError as e:
        print(e)
        exit(1)

    target_machine = target.create_target_machine(
        cpu=cpu,
        features=features,
        opt=3
    )

    module = ir.Module()
    for t in NUMERIC_TYPES:
        generate_add_function(module, *t)

    binding_module = llvm.parse_assembly(str(module))
    asm = target_machine.emit_assembly(binding_module)
    asm_filtered = filter_asm(asm)

    output_filename = f'{triple}.txt'
    with open(output_filename, 'w') as file:
        file.write(f'; {triple} {cpu} {features}\n\n')
        file.write(asm_filtered)
        file.write('\n')

