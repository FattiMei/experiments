#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', type=str)
    args = parser.parse_args()

    input_filename = args.input_csv
    df = pd.read_csv(input_filename, comment='#')

    buffer_size_bytes = df['buffer_size_bytes']
    runtime_s = df['runtime_s']

    throughput = buffer_size_bytes / runtime_s
    throughput_mb_s = throughput / (2**20)

    plt.title(f'Reduction throughput ({input_filename})')
    plt.scatter(
        buffer_size_bytes,
        throughput_mb_s,
        s=5
    )
    plt.xscale('log', base=2)
    plt.xlabel('buffer size [bytes]')
    plt.ylabel('throughput [MB/s]')
    plt.grid()
    plt.show()

