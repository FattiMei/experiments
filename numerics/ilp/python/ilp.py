import numpy as np
from time import perf_counter
from scipy.optimize import LinearConstraint, milp

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

print(f'x = {res.x}')
print(f'{solve_time = } s')

