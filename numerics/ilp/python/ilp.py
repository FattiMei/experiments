import numpy as np
from time import perf_counter
from mip import Model, INTEGER, MINIMIZE
from scipy.optimize import LinearConstraint, milp


def scipy_solution() -> tuple[float, np.array]:
    c = np.array([1, 1])
    A = np.array([
        [2019, -2020],
        [-2020, 2021]
    ])
    b_l = np.array([-np.inf, -np.inf])
    b_u = np.array([-1, -1])

    integrality = np.ones_like(c)
    constraints = LinearConstraint(A, b_l, b_u)

    start_time = perf_counter()
    res = milp(c=c, constraints=constraints, integrality=integrality)
    end_time = perf_counter()
    solve_time = end_time - start_time

    return solve_time, res.x


def mip_solution() -> tuple[float, np.array]:
    prob = Model(sense=MINIMIZE)

    x = prob.add_var("x", lb=0, var_type=INTEGER)
    y = prob.add_var("y", lb=0, var_type=INTEGER)

    prob.objective = x + y
    prob += (2019*x - 2020*y) <= -1
    prob += (-2020*x + 2021*y) <= -1

    start_time = perf_counter()
    prob.optimize()
    end_time = perf_counter()
    solve_time = end_time - start_time

    res = np.array([v.x for v in prob.vars])

    return solve_time, res


solve_time, sol = scipy_solution()
print(f"scipy: {sol = } in {solve_time} seconds")

solve_time, sol = mip_solution()
print(f"mip: {sol = } in {solve_time} seconds")

