import sympy as sym
from sympy import sqrt
from ansatz import (
    LinearAnsatz,
    AffineAnsatz,
    solve_ansatz,
)


z = sym.Symbol('z')
n = sym.Symbol('n')


def functional_equation(ansatz, n):
    return sym.Eq(
        ansatz(n),
        ansatz(2*n) + z / sqrt(2*n)
    )


class Ansatz:
    def __init__(self):
        self.C = sym.Symbol('C')
        self.args = (self.C,)

    def __call__(self, n, args: dict = {}):
        C = args.get(self.C, self.C)

        return C / sqrt(n)


class ComplicatedAnsatz:
    def __init__(self):
        self.A = sym.Symbol('A')
        self.B = sym.Symbol('B')
        self.C = sym.Symbol('C')
        self.D = sym.Symbol('D', positive=True)
        self.args = (self.A, self.B, self.C, self.D)

    def __call__(self, n, args: dict = {}):
        A = args.get(self.A, self.A)
        B = args.get(self.B, self.B)
        C = args.get(self.C, self.C)
        D = args.get(self.D, self.D)

        return (A + B*sqrt(n)) / (C + D*sqrt(n))


solution = solve_ansatz(functional_equation, Ansatz(), n)
complicated_solution = solve_ansatz(functional_equation, ComplicatedAnsatz(), n)

print(f'{solution = }')
print(f'{complicated_solution = }')

