import sympy as sym


class LinearAnsatz():
    def __init__(self):
        self.C = sym.Symbol('C')
        self.args = (self.C,)

    def __call__(self, x, args: dict = {}):
        C = args.get(self.C, self.C)

        return C * x


class AffineAnsatz():
    def __init__(self):
        # is it a problem if I use the same symbol names?
        self.C, self.D = sym.symbols('C D')
        self.args = (self.C, self.D)

    def __call__(self, x, args: dict = {}):
        C = args.get(self.C, self.C)
        D = args.get(self.D, self.D)

        return C * x + D


def solve_ansatz(functional_equation, ansatz, x):
    eq = functional_equation(ansatz, x)

    sol = sym.solve(eq, *ansatz.args, dict=True)
    assert(isinstance(sol, list))

    if len(sol) == 0:
        return None

    args_dict = sol[0]
    assert(isinstance(args_dict, dict))

    return ansatz(x, sol[0])

