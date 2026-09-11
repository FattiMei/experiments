import sympy as sym
from ansatz import LinearAnsatz, AffineAnsatz, solve_ansatz


d = sym.Symbol('d', positive=True)
v_fly = sym.Symbol('v_F', positive=True)
v_train = sym.Symbol('v_T', positive=True)

t = sym.Symbol('t')
t_leap = sym.solve(
    sym.Eq(v_fly * t, d - v_train * t),
    t
)[0]


def flight_distance_equation(ansatz, x):
    return [
        sym.Eq(ansatz(0), 0),
        sym.Eq(
            ansatz(x),
            v_fly * t_leap + ansatz(x - 2*v_train*t_leap)
        ),
    ]


linear_solution = solve_ansatz(flight_distance_equation, LinearAnsatz(), d)
affine_solution = solve_ansatz(flight_distance_equation, AffineAnsatz(), d)

print(f'{linear_solution = }')
print(f'{affine_solution = }')

