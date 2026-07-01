import os
import time
import argparse
import graphviz
import itertools
import subprocess
import numpy as np


def gcc_command(language: str) -> str:
    return [
        'gcc', 
        '-x', language,   # treat input as `language` file
        '-M', '-MF', '-', # dump dependency file to stdout
        '-'               # take input from stdin
    ]


def get_dependencies(header: str, language: str) -> list[str]:
    is_abs_path = header.startswith('/')

    if is_abs_path:
        src = f'#include "{header}"'
    else:
        src = f'#include <{header}>'

    try:
        res = subprocess.run(
            gcc_command(language),
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


def get_header_abs_path(header: str, language: str) -> str:
    return next(
        filter(
            lambda dep: dep.endswith(header),
            get_dependencies(header, language)
        )
    )


def build_dependency_graph(headers: list[str], language: str = 'c') -> tuple[list[str], list[tuple[int,int]]]:
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
        get_header_abs_path(header, language): i
        for (i, header) in enumerate(headers)
    }
    queue = list(labels.keys())
    edges = []

    while len(queue) > 0:
        current = queue.pop()
        i = labels[current]

        for dep in get_dependencies(current, language):
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


def build_hasse_diagram(A: np.ndarray) -> np.ndarray:
    H = A.copy()
    n = A.shape[0]

    for u in range(n):
        for i in range(n):
            for j in range(n):
                if H[i,u] and H[u,j]:
                    H[i,j] = 0

    return H


def populate_dot_graph(labels, edges, format: str = 'png'):
    dot = graphviz.Digraph(
        format=format,
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
    parser.add_argument('--language', type=str, default='c')
    parser.add_argument('--output', type=str, default='graph')
    parser.add_argument('--hasse', action='store_true')

    args = parser.parse_args()
    headers = args.header

    start_time = time.perf_counter()
    labels, edges = build_dependency_graph(headers, args.language)
    processing_time = time.perf_counter() - start_time
    print(f'Building the dependency graph: {processing_time:.2f} s')

    if args.hasse:
        start_time = time.perf_counter()
        A = build_adjacency_matrix(labels, edges)
        H = build_hasse_diagram(A)
        edges = np.argwhere(H).tolist()
        post_processing_time = time.perf_counter() - start_time
        print(f'Computing the hasse diagram: {post_processing_time:.2f} s')

    start_time = time.perf_counter()
    dot = populate_dot_graph(labels, edges, args.format)
    dot.render(args.output, view=False)
    rendering_time = time.perf_counter() - start_time
    print(f'Rendering time: {rendering_time:.2f} s')

