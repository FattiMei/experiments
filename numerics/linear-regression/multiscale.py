import numpy as np
# from ols import linear_regression


BETA = np.array([0.1, 2.0])
NPOINTS = 1000
ERROR = np.random.normal(size=NPOINTS)


# OLS on uniformely distributed data
x = np.linspace(-1, 10, num=NPOINTS)
y = BETA[0] + BETA[1] * x + ERROR
_, residuals = linear_regression(x, y)
mse = np.mean(residuals * residuals)


# use the same model, but now work with multiscale data
x_multiscale = 2**x
y_multiscale = BETA[0] + BETA[1] * x_multiscale + ERROR
_, residuals_multiscale = linear_regression(x_multiscale, y_multiscale)
mse_multiscale = np.mean(residuals_multiscale * residuals_multiscale)


# I swear that I watched the R^2 drop after a scale transformation...
print(f'{mse = }')
print(f'{mse_multiscale = }')

