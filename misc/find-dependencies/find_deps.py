import os
import argparse
import graphviz
import subprocess


GCC_COMMAND = [
    'gcc', 
    '-x', 'c',        # treat input as C file
    '-M', '-MF', '-', # dump dependency file to stdout
    '-'               # take input from stdin
]


def get_dependencies(header_filename: str) -> str:
    is_abs_path = header_filename.startswith('/')

    if is_abs_path:
        src = f'#include "{header_filename}"'
    else:
        src = f'#include <{header_filename}>'

    try:
        res = subprocess.run(
            GCC_COMMAND,
            input=src.encode(),
            capture_output=True,
            check=True # this should never fail
        )

        dependency_file = res.stdout.decode()
        return dependency_file.replace('\\', '').split()[1:]

    except subprocess.CalledProcessError:
        # TODO: one may want to log what is the source of errors
        pass

    return ''


def get_header_path(header: str) -> str:
    basename = os.path.basename(header)

    for path in get_dependencies(header):
        if os.path.basename(path) == basename:
            return path

    assert(False)
    return None


def build_dependency_graph(headers: list[str], recursive: bool = False) -> list[tuple[str, str]]:
    edges = []
    queue = headers.copy()
    reached = set(queue)

    while len(queue) > 0:
        current = queue.pop()
        dependencies = get_dependencies(current)

        for dependency in dependencies:
            # this to get the absolute path of the current header file
            if dependency.endswith(current):
                current = dependency
                continue

            if recursive and dependency not in reached:
                reached.add(dependency)
                queue.append(dependency)

        # adding later the edges once we know the absolute path
        # of the source node
        for dependency in dependencies:
            # we ignore the cases in which an header depends on itself
            if dependency != current:
                edges.append((current, dependency))

    return edges


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('header', type=str, nargs='+')
    parser.add_argument('--recursive', action='store_true')
    parser.add_argument('--format', type=str, default='png')
    args = parser.parse_args()

    headers = args.header
    recursive = args.recursive

    edges = build_dependency_graph(headers, recursive)
    nodes = set(map(lambda e: e[0], edges))

    dot = graphviz.Digraph(
        format=args.format,
        graph_attr={
            'rankdir': 'TB',
        }
    )

    for node in nodes:
        dot.node(node, os.path.basename(node))

    for (h1, h2) in edges:
        dot.edge(h1, h2, '')

    dot = dot.unflatten(stagger=3)
    dot.render('graph', view=False)

