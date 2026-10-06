#!/usr/bin/env python3

import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', type=str)
    parser.add_argument('--save-img', action='store_true')
    args = parser.parse_args()

    input_filename = args.input_csv
    df = pd.read_csv(input_filename, comment='#')

    buffer_size_bytes = df['buffer_size_bytes']
    runtime_s = df['runtime_s']

    throughput = buffer_size_bytes / runtime_s
    throughput_mb_s = throughput / (2**20)

    fig, ax = plt.subplots()

    ax.set_title(f'Reduction throughput ({input_filename})')
    plt.scatter(
        buffer_size_bytes,
        throughput_mb_s,
        s=5
    )
    ax.set_xscale('log', base=2)
    ax.set_xlabel('buffer size [bytes]')
    ax.set_ylabel('throughput [MB/s]')
    ax.grid()

    if args.save_img:
        FORMAT = 'png'
        stem = Path(input_filename).stem
        output_filename = f'{stem}.{FORMAT}'
        fig.savefig(output_filename, format=FORMAT)

        print(f'Saved plot to {output_filename}')
    else:
        plt.show()

