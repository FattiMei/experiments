import os
import time
import argparse
import graphviz
import itertools
import subprocess
import numpy as np


GCC_COMMAND = [
    'gcc', 
    '-x', 'c',        # treat input as C file
    '-M', '-MF', '-', # dump dependency file to stdout
    '-'               # take input from stdin
]


def get_dependencies(header: str) -> list[str]:
    is_abs_path = header.startswith('/')

    if is_abs_path:
        src = f'#include "{header}"'
    else:
        src = f'#include <{header}>'

    try:
        res = subprocess.run(
            GCC_COMMAND,
            input=src.encode(),
            capture_output=True,
            check=True
        )

        dependency_file = res.stdout.decode()
        return dependency_file.replace('\\', '').split()[1:]

    except subprocess.CalledProcessError:
        # TODO: one may want to log what is the source of errors
        pass

    return []


def get_header_abs_path(header: str) -> str:
    return next(
        filter(
            lambda dep: dep.endswith(header),
            get_dependencies(header)
        )
    )


def build_dependency_graph(headers: list[str]) -> tuple[list[str], list[tuple[int,int]]]:
    """
    Returns the dependency graph (V,E) starting from a list of headers.
    This graph is supposed to be closed under the transitive relation.
    In simple terms if there exists a path from i to j, then (i,j) in E

    The user can provide header names like "stdio.h" or "stdlib.h" or
    complete header paths like "/usr/include/zstd.h".

    This solution contains redundancies as every header in `headers` is
    checked twice for dependencies. The alternative would have been
    complicating the algorithm by adding more data structures and hidden
    invariants
    """
    labels = {
        get_header_abs_path(header): i
        for (i, header) in enumerate(headers)
    }
    queue = list(labels.keys())
    edges = []

    while len(queue) > 0:
        current = queue.pop()
        i = labels[current]

        for dep in get_dependencies(current):
            if dep in labels:
                j = labels[dep]
            else:
                j = len(labels)
                labels[dep] = j
                queue.append(dep)

            if i != j:
                edges.append((i,j))

    return list(labels.keys()), edges


def build_adjacency_matrix(labels: list[str], edges: list[tuple[int,int]]) -> np.ndarray:
    n = len(labels)
    A = np.zeros((n,n), dtype=np.int32)

    for (i,j) in edges:
        A[i,j] = 1

    return A


def populate_dot_graph(labels, edges, format: str = 'png'):
    dot = graphviz.Digraph(
        format=args.format,
        graph_attr={
            'rankdir': 'TB',
        }
    )

    for i, label in enumerate(labels):
        dot.node(str(i), os.path.basename(label))

    for (i,j) in edges:
        dot.edge(str(i), str(j), '')

    dot = dot.unflatten(stagger=3)
    return dot


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('header', type=str, nargs='+')
    parser.add_argument('--format', type=str, default='png')

    args = parser.parse_args()
    headers = args.header

    start_time = time.perf_counter()
    labels, edges = build_dependency_graph(headers)
    processing_time = time.perf_counter() - start_time
    print(f'Processing time: {processing_time:.2f} s')

    start_time = time.perf_counter()
    dot = populate_dot_graph(labels, edges, args.format)
    dot.render('graph', view=False)
    rendering_time = time.perf_counter() - start_time
    print(f'Rendering time: {rendering_time:.2f} s')

