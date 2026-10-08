import numpy as np
import matplotlib.pyplot as plt


def linear_regression(x: np.array, y: np.array) -> tuple[np.array, np.array]:
    X = np.concatenate((
        np.ones((x.shape[0], 1)),
        x.reshape(-1,1),
    ), axis=1)

    beta = np.linalg.lstsq(X, y)[0]
    residuals = y - X @ beta

    return beta, residuals


if __name__ == '__main__':
    x = np.linspace(-2, 100, num=1000)
    y = 4.0 - 1.5 * x + np.random.normal(size=len(x))
    beta, residuals = linear_regression(x, y)


    # we perform an affine map of the predictors
    # according to the math the computed residuals should be the same
    z = 300.0 * x - 7.0
    beta_z, residuals_z = linear_regression(z, y)
    assert(np.allclose(residuals, residuals_z))

