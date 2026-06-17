import re
import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class Glmark2Results:
    gl_version: str
    glmark2_score: int
    benchmarks: dict[str, float] # using only the frame time


gl_version_re = re.compile(r'^\s*GL_VERSION:\s+(.*)\s*$')
glmark2_bench_re = re.compile(r'\[(\w+)].*: FPS: (\d+) FrameTime: (.*) ms')
glmark2_score_re = re.compile(r'^\s*glmark2 Score: (\d+)\s+$')


def parse_glmark2_file(filename: str):
    benchmarks = {}

    with open(filename, 'r') as file:
        contents = file.read()

    for line in contents.splitlines():
        # we try every regex in our vocabulary
        # I know this is wasteful
        gl_version_match = gl_version_re.match(line)
        if gl_version_match is not None:
            gl_version = gl_version_match.group(1)
            continue

        glmark2_bench_match = glmark2_bench_re.match(line)
        if glmark2_bench_match is not None:
            bench_name = glmark2_bench_match.group(1)
            fps = glmark2_bench_match.group(2)
            frame_time = glmark2_bench_match.group(3)
            benchmarks[bench_name] = float(frame_time)
            continue

        glmark2_score_match = glmark2_score_re.match(line)
        if glmark2_score_match is not None:
            glmark2_score = glmark2_score_match.group(1)
            continue

    return Glmark2Results(gl_version, glmark2_score, benchmarks)


def plot_results(results: Glmark2Results, ax, label: str):
    y = list(results.benchmarks.values())
    ax.plot(y, label=label)


if __name__ == '__main__':
    result_files = {
        'x11'    : 'glmark2-results.txt',
        'x11-drm': 'glmark2-drm-results.txt',
        'es2'    : 'glmark2-es2-results.txt',
        'es2-drm': 'glmark2-es2-drm-results.txt'
    }

    first = True
    reference = None

    for label, filename in result_files.items():
        results = parse_glmark2_file(filename)
        frame_times = np.array(list(results.benchmarks.values()))

        if first:
            reference = frame_times
            first = False

        normalized_frame_times = reference / frame_times
        plt.plot(normalized_frame_times, label=label)

    plt.title('Comparison of `glmark2` flavors')
    plt.ylabel('speedup')
    plt.legend()
    plt.show()

