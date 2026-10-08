import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


NSEGMENTS = 2
NKNOTS = NSEGMENTS + 1
L = 10.0
NPOINTS = 10000


knots_x = np.sort(np.random.uniform(-L, L, NKNOTS))
knots_y = np.random.uniform(-2, 2, NKNOTS)
slopes = np.diff(knots_y) / np.diff(knots_x)
q = knots_y[:-1] - slopes*knots_x[:-1]


# generation of points that are guaranteed to be inside the segments
x = np.linspace(
    knots_x[0]  + 1e-6,
    knots_x[-1] - 1e-6,
    NPOINTS
)


# evaluation of the piecewise linear function
mask = (x[:,np.newaxis] >= knots_x[:-1]) & (x[:,np.newaxis] < knots_x[1:])
y = np.sum(
    mask * (knots_y[:-1] + (x[:,np.newaxis] - knots_x[:-1])*slopes),
    axis=-1
)


# for now the error is modeled the same across segments
target = y # + 0.1*np.random.normal(size=NPOINTS)
X = np.stack((
    np.ones_like(x),
    x
)).T


# perform a local fitting
WINDOW_SIZE = 50
beta = np.zeros((len(target), X.shape[-1]))

for i in range(len(target) - WINDOW_SIZE):
    X_slice = X[i:(i+WINDOW_SIZE)]
    y_slice = target[i:(i+WINDOW_SIZE)]
    beta[i,:] = np.linalg.lstsq(X_slice, y_slice, rcond=None)[0]

    # x_slice = x[i:(i+WINDOW_SIZE)]
    # y_slice = y[i:(i+WINDOW_SIZE)]
    # beta[i] = sm.OLS(y_slice, sm.add_constant(x_slice)).fit().params


fig, axs = plt.subplots(1, 2)
axs[0].set_title('Piecewise linear dataset')
axs[0].scatter(x, y, s=4)
axs[1].set_title(f'Local linear fitting - (w={WINDOW_SIZE})')
axs[1].scatter(beta[:,0], beta[:,1], s=4, alpha=0.3)
axs[1].scatter(q, slopes, s=4, marker='x', label='real params')
plt.show()

