#!/usr/bin/env python3
"""Exact corroboration of the sharp P112 diagonal-completion boundary.

SPDX-License-Identifier: Apache-2.0
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    need(len(left) == len(right) <= 112, "dot dimensions")
    return sum(a * b for a, b in zip(left, right))


def exact_rank(matrix):
    """Rational elimination, with a fixed input capacity and no tolerance."""
    need(len(matrix) <= 112, "rank row capacity")
    if not matrix:
        return 0
    width = len(matrix[0])
    need(width <= 112 and all(len(row) == width for row in matrix), "rank shape")
    need(all(type(x) is int and abs(x) <= 224 for row in matrix for x in row),
         "bounded integer rank input")
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            if scale:
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def geometry():
    lines = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            value = tuple(row)
            lines.add(max(value, tuple(-x for x in value)))
    for row in product((-1, 1), repeat=8):
        if sum(x < 0 for x in row) % 2 == 0:
            lines.add(max(row, tuple(-x for x in row)))
    frame = set()
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.add(tuple(row))
    roots = sorted(lines)
    live = [row for row in roots if row not in frame]
    need(len(roots) == 120 and len(live) == 112, "root and puncture sizes")
    need(all(dot(row, row) == 8 for row in roots), "doubled-root normalization")
    return roots, live


def pair_intersections(roots):
    """Finite premise for the new unchanged-row argument, not a flat audit."""
    zeros = [sum(1 << i for i, row in enumerate(roots) if dot(row, alpha) == 0)
             for alpha in roots]
    histogram = Counter((a & b).bit_count() for a, b in combinations(zeros, 2))
    need(histogram == {30: 3780, 36: 3360}, "distinct root-hyperplane intersections")
    return {str(size): count for size, count in sorted(histogram.items())}


def changed_diagonal(gram, support, coefficient):
    need(type(coefficient) is int and 1 <= abs(coefficient) <= 112, "diagonal coefficient")
    need(all(type(i) is int and 0 <= i < len(gram) for i in support), "diagonal support")
    return [[value + (coefficient if i == j and i in support else 0)
             for j, value in enumerate(row)] for i, row in enumerate(gram)]


def validate_diagonal(gram, changed):
    need(len(changed) == len(gram), "completion rows")
    need(all(len(row) == len(gram) for row in changed), "completion columns")
    need(all(changed[i][j] == gram[i][j]
             for i in range(len(gram)) for j in range(len(gram)) if i != j),
         "off-diagonal entries must be unchanged")


def witness(live):
    gram = [[dot(a, b) for b in live] for a in live]
    covariance = [[sum(row[i] * row[j] for row in live) for j in range(8)]
                  for i in range(8)]
    need(covariance == [[112 * (i == j) for j in range(8)] for i in range(8)],
         "tight-frame scale for the projection witness")
    alpha = (1,) * 8
    need(alpha in live, "specified live normal")
    values = [dot(row, alpha) for row in live]
    support = {i for i, value in enumerate(values) if value}
    unchanged = [row for i, row in enumerate(live) if i not in support]
    need(len(support) == 53 and exact_rank(unchanged) == 7, "witness support and complement")
    need(all(dot(row, values) == 112 * value for row, value in zip(gram, values)),
         "root-code eigenvector")
    changed = changed_diagonal(gram, support, -112)
    validate_diagonal(gram, changed)
    need(all(dot(row, values) == 0 for row in changed), "new kernel direction")
    rank = exact_rank(changed)
    need(rank == 59, "sharp rational completion rank")
    return gram, support, values, changed, {
        "normal": list(alpha), "support": sorted(support), "diagonal_coefficient": -112,
        "unchanged_root_rank": 7, "completion_rank": rank,
        "additive_prediction": 61,
    }


def new_range_fixtures(gram, live):
    results = []
    for size in (21, 31, 40, 50):
        for stride, coefficient in ((1, 1), (17, -3)):
            support = {(stride * i) % 112 for i in range(size)}
            need(len(support) == size, "fixture distinct positions")
            unchanged = [row for i, row in enumerate(live) if i not in support]
            rank = exact_rank(changed_diagonal(gram, support, coefficient))
            need(exact_rank(unchanged) == 8 and rank == 8 + size, "extended-range fixture")
            results.append({"size": size, "stride": stride, "coefficient": coefficient,
                            "completion_rank": rank})
    return results


def schur_bound_fixtures():
    rows = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (0, 1, 1))
    gram = [[dot(a, b) for b in rows] for a in rows]
    count = 0
    for mask in range(32):
        support = {i for i in range(5) if mask >> i & 1}
        unchanged_rank = exact_rank([row for i, row in enumerate(rows) if i not in support])
        for coefficient in (-3, -1, 1, 2):
            rank = exact_rank(changed_diagonal(gram, support, coefficient))
            need(rank >= len(support) + 2 * unchanged_rank - 3, "Schur rank lower bound")
            if unchanged_rank == 3:
                need(rank == 3 + len(support), "full unchanged-rank equality")
            count += 1
    return count


def rejection_controls(gram, support, values, changed):
    rejected = []
    try:
        need(exact_rank(changed) == 58, "false rank-58 witness")
    except ValueError:
        rejected.append("false boundary rank")
    try:
        need(exact_rank(changed) == 8 + len(support), "false rank-59 additivity")
    except ValueError:
        rejected.append("invalid extension through rank 59")
    wrong = changed_diagonal(gram, support, -111)
    need(any(dot(row, values) for row in wrong) and exact_rank(wrong) == 60,
         "changed scale must lose the claimed kernel")
    rejected.append("wrong projection scale")
    missing = changed_diagonal(gram, support - {min(support)}, -112)
    need(exact_rank(missing) == 60, "missing diagonal must lose sharp rank")
    rejected.append("omitted correction")
    off_diagonal = [row[:] for row in changed]
    off_diagonal[0][1] += 1
    try:
        validate_diagonal(gram, off_diagonal)
    except ValueError:
        rejected.append("forbidden off-diagonal edit")
    need(any(changed[i][i] != gram[i][i] for i in range(112)),
         "witness cannot satisfy the distinct odd-only mask")
    rejected.append("confusion with the odd-only mask")
    need(len(rejected) == 6, "all six controls must execute")
    return rejected


def run():
    roots, live = geometry()
    intersections = pair_intersections(roots)
    gram, support, values, changed, sharp = witness(live)
    return {
        "status": "PASS_P112_DIAGONAL_RANK_BOUNDARY",
        "claim_type": "scoped proof with exact finite corroboration",
        "additive_rank_range": [8, 58], "first_nonadditive_rank": 59,
        "witness": sharp, "root_hyperplane_pair_intersections": intersections,
        "extended_range_fixtures": new_range_fixtures(gram, live),
        "schur_bound_fixtures": schur_bound_fixtures(),
        "controls": rejection_controls(gram, support, values, changed),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new receipt outside the package")
    args = parser.parse_args()
    if args.receipt:
        destination = args.receipt.resolve()
        need(HERE not in destination.parents, "receipt must be outside the package")
        need(not destination.exists(), "receipt must be new")
    result = run()
    hashes = {}
    for name in PACKAGE_FILES:
        path = HERE / name
        need(path.stat().st_size <= 131072, "package file capacity")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {"result": result, "package_sha256": hashes}
    payload = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            need(stream.write(payload) == len(payload), "complete receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
