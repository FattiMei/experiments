import subprocess
from inttype import IntType


def sum_of_naturals(n: int) -> int:
    """
    Sum the naturals from 0 to `n` included
    """
    if n < 0: return 0
    return n*(n+1)//2


def generate_sum_function(itype: IntType, n: int, function_name: str) -> str:
    return f"""
        #include <stdint.h>
        #define IntT {itype.typename}

        IntT {function_name}(void) <%
            IntT acc = 0;

            for (IntT i = 0; i <= {itype.format_constant(n)}; ++i) <%
                acc += i;
            %>

            return acc;
        %>
    """ + "\n"


def generate_constant_function(itype: IntType, n: int, function_name: str) -> str:
    sum = sum_of_naturals(n)

    return f"""
        #include <stdint.h>
        #define IntT {itype.typename}

        IntT {function_name}(void) <%
            return {itype.format_constant(sum)};
        %>
    """ + "\n"


class Compiler:
    def __init__(self, compiler: str = 'gcc', opt: str = '-O3', enable_warnings: bool = True):
        self.compiler = compiler
        self.opt = opt
        self.enable_warnings = enable_warnings

    def compile_to_asm(self, src: str) -> str:
        cmd = [
            self.compiler,
            self.opt,
            "-xc", "-",
            "-S",
            "-o", "/dev/stdout"
        ]
        if self.enable_warnings:
            cmd.extend(["-Wall", "-Wextra", "-Wpedantic", "-Werror"])

        try:
            res = subprocess.run(cmd, input=src.encode(), capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print("Compilation failed with the following error:")
            print(e.stderr.decode())
            print(src)
            raise

        return res.stdout.decode()

    def test_optimization(self, itype: IntType, n: int) -> str:
        src = generate_sum_function(itype, n, f'test_sum<{n}>')
        return self.compile_to_asm(src)

    def __repr__(self) -> str:
        return f'{self.compiler} at {self.opt}'


def detect_optimization(compiler: Compiler, itype: IntType, n: int) -> bool:
    FUN_NAME = 'foo'
    src1 = generate_sum_function(itype, n, FUN_NAME)
    src2 = generate_constant_function(itype, n, FUN_NAME)
    asm1 = compiler.compile_to_asm(src1)
    asm2 = compiler.compile_to_asm(src2)

    return asm1 == asm2
