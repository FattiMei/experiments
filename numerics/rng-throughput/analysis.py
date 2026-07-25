import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("rng_throughput_raspi.csv")
DIST    = 'dist'
RNG     = 'rng'
N_ITER  = 'nit'
TIME_S  = 'time_s'


throughput_MB_s = 8 * (df[N_ITER] / df[TIME_S]) / (2**20)
THROUGHPUT_MB_S = 'throughput_MB_s'
df[THROUGHPUT_MB_S] = throughput_MB_s


def throughput_boxplot(df: pd.DataFrame, title: str, ax=None, tick_angle: float = 90):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10,6))

    tick_labels = []
    X = []

    for rng, local_df in df.groupby(RNG):
        tick_labels.append(rng)
        X.append(local_df[THROUGHPUT_MB_S])

    ax.boxplot(X, tick_labels=tick_labels)
    ax.set_title(title)
    ax.set_ylabel('throughtput [MB/s]')
    ax.tick_params('x', rotation=tick_angle)


for dist, local_df in df.groupby(DIST):
    throughput_boxplot(
            local_df,
            title=f'Sampling from {dist}',
            tick_angle=60)
    plt.tight_layout()
plt.show()

