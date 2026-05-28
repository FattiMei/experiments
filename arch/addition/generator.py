from dataclasses import dataclass

import llvmlite.ir as ir
import llvmlite.binding as llvm


@dataclass(frozen=True)
class DType:
    typename: str
    llvm_type: object


I8   = DType(  'int8_t', ir.IntType(8))
I16  = DType( 'int16_t', ir.IntType(16))
I32  = DType( 'int32_t', ir.IntType(32))
I64  = DType( 'int64_t', ir.IntType(64))
U8   = DType( 'uint8_t', ir.IntType(8))
U16  = DType('uint16_t', ir.IntType(16))
U32  = DType('uint32_t', ir.IntType(32))
U64  = DType('uint64_t', ir.IntType(64))
I128 = DType('int128_t', ir.IntType(128))
F16  = DType( 'float16', ir.HalfType())
F32  = DType( 'float32', ir.FloatType())
F64  = DType( 'float64', ir.DoubleType())


def generate_add_function(dtype: DType) -> ir.module.Module:
    llvm_type = dtype.llvm_type

    function_type = ir.FunctionType(llvm_type, (llvm_type, llvm_type))
    function_name = f'add_{itype.typename}'

    module = ir.Module()

    func = ir.Function(module, function_type, name=function_name)
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    a, b = func.args

    match type(llvm_type):
        case ir.types.IntType:
            add_func = builder.add
        case ir.types.HalfType:
            add_func = builder.fadd
        case ir.types.FloatType:
            add_func = builder.fadd
        case ir.types.DoubleType:
            add_func = builder.fadd
        case _:
            assert(False)

    result = add_func(a, b)
    builder.ret(result)

    return module


def filter_asm(asm: str) -> str:
    return '\n'.join(
        filter(
            lambda l: not l.strip().startswith('.'),
            asm.splitlines()
        )
    )


def get_targets_data(triples: list[str]) -> dict[str, tuple[str,str]]:
    """
    To be called after having initialized all targets with
        `llvm.initialize_all_targets()`

    For the native target, we can be a little more specific with the flags
    """
    target_data = {
        triple: ('', '')
        for triple in triples
    }

    native_target = llvm.get_default_triple()
    native_features = llvm.get_host_cpu_features()

    target_data[native_target] = (
        llvm.get_host_cpu_name(),
        native_features.flatten()
    )

    return target_data


TRIPLES = [
    "x86_64-pc-linux-gnu",
    "arm-linux-gnueabihf",
    "aarch64-unknown-linux-gnu"
]


NUMERIC_TYPES = [I8, U8, I16, U16, I32, U32, I64, U64, I128, F16, F32, F64]


if __name__ == '__main__':
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()

    for triple, (cpu, features) in get_targets_data(TRIPLES).items():
        target = llvm.Target.from_triple(triple)

        # I suspect some optimizations are done at target level,
        # so at a lower level than LLVM IR, possibly at MachineIR
        target_machine = target.create_target_machine(
            cpu=cpu,
            features=features,
            opt=3
        )

        output_filename = f'{triple}.txt'
        with open(output_filename, 'w') as file:
            file.write(f'; {triple} {cpu} {features}\n\n')

            for itype in NUMERIC_TYPES:
                module = generate_add_function(itype)
                module_ir = str(module)
                binding_module = llvm.parse_assembly(module_ir)

                asm = target_machine.emit_assembly(binding_module)
                asm_small = filter_asm(asm)
                file.write(asm_small)
                file.write('\n')

