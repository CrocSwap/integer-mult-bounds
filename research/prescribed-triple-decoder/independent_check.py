#!/usr/bin/env python3
"""Independently enumerate rank-three subspaces of a binary graph cut code.

This uses RREF coefficient matrices, not partition enumeration.  Vertices are
0,...,2p-1; the removed perfect matching is {(0,1),(2,3),...}.  The last
vertex's cut coefficient is fixed to zero to remove the constant-vector kernel.
Only the proper, nonempty star span is checked.  No claim about a paid supplier
or the integer multiplication exponent follows from this finite calculation.

Apache-2.0.  Eva Ayala, with substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
import itertools
import json
from pathlib import Path
import sys


def graph_edges(p):
    """Construct the graph without using the partition verifier's helpers."""
    return [
        (u, v)
        for u in range(2 * p)
        for v in range(u + 1, 2 * p)
        if u // 2 != v // 2
    ]


def rref_bases(columns):
    """Yield every rank-three binary row space exactly once in RREF."""
    for pivots in itertools.combinations(range(columns), 3):
        free = [
            (row, col)
            for row, pivot in enumerate(pivots)
            for col in range(pivot + 1, columns)
            if col not in pivots
        ]
        for assignment in range(1 << len(free)):
            rows = [1 << pivot for pivot in pivots]
            for bit, (row, col) in enumerate(free):
                if (assignment >> bit) & 1:
                    rows[row] |= 1 << col
            yield tuple(rows)


def independent_columns(a, b, c):
    """Rank three for three columns in GF(2)^3, by direct elimination."""
    pivots = [0, 0, 0]
    rank = 0
    for column in (a, b, c):
        for bit in range(2, -1, -1):
            if not ((column >> bit) & 1):
                continue
            if pivots[bit]:
                column ^= pivots[bit]
            else:
                pivots[bit] = column
                rank += 1
                break
    return rank == 3


def check_p(p):
    """Compute minimum support minus three for every prescribed target triple."""
    edges = graph_edges(p)
    n_edges = len(edges)
    triples = list(itertools.combinations(range(n_edges), 3))
    minima = {triple: None for triple in triples}
    column_triples = [
        triple
        for triple in itertools.combinations(range(1, 8), 3)
        if independent_columns(*triple)
    ]
    spaces_checked = 0
    for basis in rref_bases(2 * p - 1):
        spaces_checked += 1
        vertex_columns = [
            sum(((basis[row] >> v) & 1) << row for row in range(3))
            for v in range(2 * p - 1)
        ] + [0]
        by_column = [[] for _ in range(8)]
        for edge_index, (u, v) in enumerate(edges):
            by_column[vertex_columns[u] ^ vertex_columns[v]].append(edge_index)
        support = n_edges - len(by_column[0])
        budget = support - 3
        for a, b, c in column_triples:
            for first in by_column[a]:
                for second in by_column[b]:
                    for third in by_column[c]:
                        target = tuple(sorted((first, second, third)))
                        previous = minima[target]
                        if previous is None or budget < previous:
                            minima[target] = budget

    dimension = 2 * p - 1
    expected_spaces = (
        ((1 << dimension) - 1)
        * ((1 << dimension) - 2)
        * ((1 << dimension) - 4)
        // ((8 - 1) * (8 - 2) * (8 - 4))
    )
    if spaces_checked != expected_spaces:
        raise RuntimeError("RREF count differs from the Gaussian binomial")

    # Independent negative control: an actual graph triangle's three edge
    # differences sum to zero, so no three-dimensional subspace can decode it.
    triangles = set()
    index = {edge: i for i, edge in enumerate(edges)}
    for u, v, w in itertools.combinations(range(2 * p), 3):
        triangle_edges = ((u, v), (u, w), (v, w))
        if all(edge in index for edge in triangle_edges):
            target = tuple(sorted(index[edge] for edge in triangle_edges))
            triangles.add(target)
            if minima[target] is not None:
                raise RuntimeError("a graph triangle was incorrectly decodable")
    undecodable = {target for target, value in minima.items() if value is None}
    if undecodable != triangles:
        raise RuntimeError("undecodable target sets differ from graph triangles")

    histogram = Counter("null" if value is None else str(value)
                        for value in minima.values())
    return {
        "p": p,
        "vertices": 2 * p,
        "edges": [list(edge) for edge in edges],
        "subspaces_checked": spaces_checked,
        "target_triples_checked": len(triples),
        "undecodable_triangles": len(triangles),
        "histogram": dict(sorted(histogram.items())),
        "targets": [
            {"edge_indices": list(target), "minimum_deletions": minima[target]}
            for target in triples
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p", type=int, choices=(3, 4), default=3)
    parser.add_argument("--output", type=Path,
                        help="write the complete target table to this file")
    parser.add_argument("--compare", type=Path,
                        help="compare every target with a prior table in this schema")
    args = parser.parse_args(argv)
    result = check_p(args.p)
    if args.compare:
        expected = json.loads(args.compare.read_text())
        for field in ("p", "edges", "targets"):
            if expected.get(field) != result[field]:
                raise RuntimeError("comparison mismatch in " + field)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    summary = {key: value for key, value in result.items()
               if key not in ("edges", "targets")}
    summary["method"] = "all rank-three cut-code subspaces in RREF"
    summary["comparison"] = "passed" if args.compare else "not requested"
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
