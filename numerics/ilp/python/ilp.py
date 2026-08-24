import pulp
import numpy as np
from time import perf_counter
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


def pulp_solution() -> tuple[float, np.array]:
    prob = pulp.LpProblem("ILP problem", pulp.LpMinimize)

    x = prob.add_variable("x", 0, None, pulp.LpInteger)
    y = prob.add_variable("y", 0, None, pulp.LpInteger)

    prob += x + y, "Objective function"
    prob += 2019*x < 2020*y
    prob += 2021*y < 2020*x

    start_time = perf_counter()
    prob.solve()
    end_time = perf_counter()
    solve_time = end_time - start_time

    res = np.array([v.varValue for v in prob.variables()])

    return solve_time, res


solve_time, sol = scipy_solution()
print(f"scipy: {sol = } in {solve_time} seconds")

solve_time, sol = pulp_solution()
print(f"pulp: {sol = } in {solve_time} seconds")

