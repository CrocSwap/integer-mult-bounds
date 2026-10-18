#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dense binary elimination and iterative chordless-path reconstruction."""

import gzip
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import require, sources  # noqa: E402


def dense_rank(matrix):
    require(len(matrix) <= 112 and all(len(r) <= 112 for r in matrix), "dense bounds")
    rows = [list(r) for r in matrix]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def parity(a, b):
    return sum(((a >> j) & 1) * ((b >> j) & 1) for j in range(9)) % 2


def rank(left, right):
    return dense_rank([[parity(x, y) for y in right] for x in left])


def cycle_sets(planes):
    adj = [
        {j for j in range(56) if j != i and rank(planes[i], planes[j]) == 0}
        for i in range(56)
    ]
    paths = [(i,) for i in range(56)]
    for length in range(1, 5):
        extended = []
        for path in paths:
            for vertex in adj[path[-1]]:
                if vertex <= path[0] or vertex in path:
                    continue
                if any(vertex in adj[i] for i in path[1:-1]):
                    continue
                if length > 1 and (vertex in adj[path[0]]) != (length == 4):
                    continue
                require(len(extended) < 100_000, "bounded simple paths")
                extended.append(path + (vertex,))
        paths = extended
    found = {tuple(sorted(p)) for p in paths}
    require(len(found) == 23, "independent 23 cycles")
    return sorted(found)


def main():
    raw = sources()
    recipes = json.loads(gzip.decompress(raw["DATA-PHASES.json.gz"]))["recipes"]
    labels = {r["port"]: r["q"] for r in recipes}
    matching = json.loads(raw["MATCHING.json"])["matching"]
    planes = [[labels[p] for p in pair] for pair in matching]
    rows = []
    for cycle in cycle_sets(planes):
        values = [v for i in cycle for v in planes[i]]
        rows.append((cycle, rank(values, values)))
    receipt = json.loads((HERE / "RESULT.json").read_bytes())
    expected = sorted(
        (tuple(sorted(r["cycle"])), r["full_support_rank"]) for r in receipt["cycles"]
    )
    require(rows == expected, "independent local rank vector")
    full = [v for pair in planes for v in pair]
    require(rank(full, full) == receipt["global_full_support_rank"] == 9, "global rank")
    require(Counter(r for _, r in rows) == {7: 4, 8: 6, 9: 13}, "rank histogram")
    # Solve the one-test dual bound directly, independently of obstruction().
    ratios = [Fraction(20, r) for _, r in rows]
    require(
        9 * max(ratios) == Fraction(receipt["certificate_ceiling"]) == Fraction(180, 7),
        "exact dual inequality",
    )
    # A different signed Gram extension includes the same full-support J term.
    # I = J - sum_{i<j}(e_i+e_j)(e_i+e_j)^T + (n-1) sum_i e_i e_i^T.
    n = 112
    matrix = [[1] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            for a in (i, j):
                for b in (i, j):
                    matrix[a][b] -= 1
        matrix[i][i] += n - 1
    require(
        all(matrix[i][j] == int(i == j) for i in range(n) for j in range(n)),
        "independent signed Gram strict fit",
    )
    print("PASS_INDEPENDENT_C5_CHARGING dense_ranks=24 cycles=23 ceiling=180/7")


if __name__ == "__main__":
    main()
