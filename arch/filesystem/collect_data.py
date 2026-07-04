import os
import argparse
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, help='Which directory to walk recursively')
    parser.add_argument('--batch', type=int, default=0, help='Batch the file reads')
    parser.add_argument('--output', type=str, default='out.csv')
    args = parser.parse_args()

    records = []
    first_run = True

    for root, dirs, files in os.walk(args.directory):
        for file in files:
            complete_name = os.path.join(root, file)

            res = subprocess.run(
                [ './fs_bench', complete_name, str(args.batch) ],
                capture_output=True,
                check=True
            )

            output = res.stdout.decode().splitlines()

            if first_run:
                first_run = False
                print(output[0])

            print(output[1])

