from dataclasses import dataclass

import llvmlite.ir as ir
import llvmlite.binding as llvm


@dataclass(frozen=True)
class IntType:
    typename: str
    llvm_type: ir.types.IntType


I8  = IntType(  'int8_t', ir.IntType(8))
I16 = IntType( 'int16_t', ir.IntType(16))
I32 = IntType( 'int32_t', ir.IntType(32))
I64 = IntType( 'int64_t', ir.IntType(64))
U8  = IntType( 'uint8_t', ir.IntType(8))
U16 = IntType('uint16_t', ir.IntType(16))
U32 = IntType('uint32_t', ir.IntType(32))
U64 = IntType('uint64_t', ir.IntType(64))


def generate_add_function(itype: IntType) -> ir.module.Module:
    llvm_type = itype.llvm_type

    function_type = ir.FunctionType(llvm_type, (llvm_type, llvm_type))
    function_name = f'add_{itype.typename}'

    module = ir.Module()

    func = ir.Function(module, function_type, name=function_name)
    block = func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)
    a, b = func.args
    result = builder.add(a, b)
    builder.ret(result)

    return module


TARGET_TRIPLES = [
    "x86_64-pc-linux-gnu",
    "arm-linux-gnueabihf",
    "aarch64-unknown-linux-gnu"
]

INTEGER_TYPES = [I8, U8, I16, U16, I32, U32, I64, U64]


if __name__ == '__main__':
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()

    for triple in TARGET_TRIPLES:
        target = llvm.Target.from_triple(triple)
        target_machine = target.create_target_machine()

        output_filename = f'{triple}.txt'
        with open(output_filename, 'w') as file:
            for itype in INTEGER_TYPES:
                module = generate_add_function(itype)
                module_ir = str(module)
                binding_module = llvm.parse_assembly(module_ir)

                asm = target_machine.emit_assembly(binding_module)
                file.write(asm)

