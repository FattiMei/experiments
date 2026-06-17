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
glmark2_bench_re = re.compile(r'(.*): FPS: (\d+) FrameTime: (.*) ms')
glmark2_score_re = re.compile(r'^\s*glmark2 Score: (\d+)\s+$')
bench_type_re = re.compile(r'[(\w+)]')


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


def extract_bench_type(bench_name: str) -> str:
    bench_type_match = bench_type_re.match(bench_name)

    return '' if bench_type_match is None else bench_type_match.group(1)


if __name__ == '__main__':
    result_files = {
        'x11'    : 'glmark2-results.txt',
        'x11-drm': 'glmark2-drm-results.txt',
        'es2'    : 'glmark2-es2-results.txt',
        'es2-drm': 'glmark2-es2-drm-results.txt'
    }

    frame_times = {}
    for label, filename in result_files.items():
        results = parse_glmark2_file(filename)
        t = np.array(list(results.benchmarks.values()))
        frame_times[label] = t

    # first plot on the speedup with respect to x11
    reference = frame_times['x11']
    for label, t in frame_times.items():
        normalized_t = reference / t
        plt.plot(normalized_t, label=label)

    plt.title('Comparison of `glmark2` flavors')
    plt.ylabel('speedup')
    plt.legend()
    plt.show()

    # second plot on comparison between es2.0 and 2.0
    plt.title('ES 2.0 speedup over OpenGL 2.0')
    plt.plot(frame_times['x11'] / frame_times['es2'], label='x11')
    plt.plot(frame_times['x11-drm'] / frame_times['es2-drm'], label='drm')
    plt.legend()
    plt.show()
