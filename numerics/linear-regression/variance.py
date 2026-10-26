import numpy as np
import matplotlib.pyplot as plt


LOW = -1
HIGH = 1
NPOINTS = 1000

BETA = np.array([1.0, 0.5])
SIGMA = 0.1

x = np.linspace(LOW, HIGH, NPOINTS)
y = BETA[0] + BETA[1]*x + SIGMA*np.random.normal(size=NPOINTS)
X = np.stack((np.ones_like(x), x)).T

WINDOW_SIZE = 50
NWINDOWS = len(x) - WINDOW_SIZE


# fitting local models, locality is controlled by window size
beta = np.zeros((NWINDOWS, 2))
for i in range(len(beta)):
    X_slice = X[i:(i+WINDOW_SIZE)]
    y_slice = y[i:(i+WINDOW_SIZE)]

    beta[i] = np.linalg.lstsq(X_slice, y_slice, rcond=None)[0]


# models are plotted in the hope that they cluster, but
# gaussian errors will inevitably introduce errors in the model
# parameters
#
# the parameter errors depend on the position of the x samples
# when samples are far from 0, small errors in the slope amplify
# errors in the intercept
fig, axs = plt.subplots(1, 2)
axs[0].set_title('Piecewise linear dataset')
axs[0].scatter(x, y, s=4)
axs[1].set_title(f'Local linear fitting - (w={WINDOW_SIZE})')
axs[1].scatter(beta[:,0], beta[:,1], s=4, alpha=0.3)
axs[1].scatter(BETA[0], BETA[1], s=20, marker='x', label='real params')
plt.show()


# fitting local models, using local coordinates
beta_local = np.zeros((NWINDOWS, 2))
for i in range(len(beta_local)):
    x_slice = x[i:(i+WINDOW_SIZE)]
    y_slice = y[i:(i+WINDOW_SIZE)]

    x_local = x_slice - x_slice[0]
    X_local = np.stack((np.ones_like(x_local), x_local)).T
    y_local = y_slice - y_slice[0]

    beta_local[i] = np.linalg.lstsq(X_local, y_local, rcond=None)[0]

fig, axs = plt.subplots(1, 2)
axs[0].set_title('Piecewise linear dataset')
axs[0].scatter(x, y, s=4)
axs[1].set_title(f'Local linear fitting - (w={WINDOW_SIZE})')
axs[1].scatter(beta_local[:,0], beta_local[:,1], s=4, alpha=0.3)

# we don't plot the real parameters because they are not in the same coordinate system as the local models
# axs[1].scatter(BETA[0], BETA[1], s=20, marker='x', label='real params')
plt.show()

