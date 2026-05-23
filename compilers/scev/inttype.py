from dataclasses import dataclass


@dataclass(frozen=True)
class IntType:
    typename: str
    sizeof:   int
    signed:   bool
    format:   str

    def intmax(self) -> int:
        total_bits = 8 * self.sizeof
        available_bits = total_bits-1 if self.signed else total_bits
        return (1 << available_bits) - 1

    def downcast(self, n: int) -> int:
        assert(n >= 0)
        base = 1 << (8 * self.sizeof)
        n = n % base

        if not self.signed: return n
        elif n < self.intmax(): return n
        else: return n - base

    def format_constant(self, n: int) -> str:
        m = self.downcast(n)
        return f'{self.format}({m})'


# table based programming
I8  = IntType(  'int8_t', 1, True ,   'INT8_C')
I16 = IntType( 'int16_t', 2, True ,  'INT16_C')
I32 = IntType( 'int32_t', 4, True ,  'INT32_C')
I64 = IntType( 'int64_t', 8, True ,  'INT64_C')
U8  = IntType( 'uint8_t', 1, False,  'UINT8_C')
U16 = IntType('uint16_t', 2, False, 'UINT16_C')
U32 = IntType('uint32_t', 4, False, 'UINT32_C')
U64 = IntType('uint64_t', 8, False, 'UINT64_C')


if __name__ == '__main__':
    assert(I8.intmax() == 127)
    assert(U8.intmax() == 255)
    assert(U8.downcast(256+69) == 69)
    assert(I32.format_constant(69420) == 'INT32_C(69420)')
