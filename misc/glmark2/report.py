import re
import argparse
from tabulate import tabulate
from dataclasses import dataclass


@dataclass
class TimedResult:
    fps: int
    frame_time: float


@dataclass
class Glmark2Results:
    score: int
    benchmarks: dict[str, TimedResult]


score_regex = re.compile(r'glmark2 Score: (\d)')
bench_regex = re.compile(r'(\[.*): FPS: (\d+) FrameTime: (.*) ms')


def parse_results(contents: str) -> Glmark2Results:
    score = None
    benchmarks = {}

    for line in contents.splitlines():
        line = line.strip()

        score_result = score_regex.match(line)
        if score_result is not None:
            score = score_result.group(1)

        bench_result = bench_regex.match(line)
        if bench_result is not None:
            # if it matches, it's guaranteed that it's well formed
            bench_name = bench_result.group(1)
            fps        = bench_result.group(2)
            frame_time = bench_result.group(3)
            benchmarks[bench_name] = TimedResult(fps, frame_time)

    return Glmark2Results(score, benchmarks)


def format_table(runs: list[Glmark2Results], use_fps: bool = False):
    table = []
    reference = runs[0]

    extract_fps = lambda data, key: data[key].fps
    extract_frame_time = lambda data, key: data[key].frame_time
    extract_val = extract_fps if use_fps else extract_frame_time

    for bench_name in reference.benchmarks.keys():
        row = [bench_name] + [extract_val(run.benchmarks, bench_name) for run in runs]
        table.append(row)

    return table


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('glmark2_files', type=str, nargs='+')
    parser.add_argument('-fps', action='store_true')
    args = parser.parse_args()

    runs = []
    headers = ['benchmark name']
    for filename in args.glmark2_files:
        with open(filename, 'r') as file:
            contents = file.read()

        runs.append(parse_results(contents))
        headers.append(filename)

    print(tabulate(format_table(runs, args.fps), headers=headers))
