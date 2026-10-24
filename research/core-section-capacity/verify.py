#!/usr/bin/env python3
"""Hyperplane capacities of the orthogonal P112 cores.

The checker counts section sizes. It does not infer an invoice floor.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CORE_SECTION_CAPACITY pairs=3780 sections=127 no_new_kappa"
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)
EXPECTED = {0: 1, 8: 15, 12: 96, 16: 15}


def fail(message):
    raise SystemExit("FAIL_CORE_SECTION_CAPACITY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(row):
    return max(tuple(row), tuple(-entry for entry in row))


def roots_and_frame():
    roots = set()
    for left, right in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[left], row[right] = 2, sign
            roots.add(canonical(row))
    for row in product((-1, 1), repeat=8):
        if sum(entry == -1 for entry in row) % 2 == 0:
            roots.add(canonical(row))
    require(len(roots) == 120, "the root count moved")
    frame = []
    for index in range(0, 8, 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[index], row[index + 1] = 2, sign
            frame.append(canonical(row))
    return tuple(sorted(roots)), set(frame)


def solve(matrix, rhs):
    rows = [[Fraction(entry) for entry in row] + [Fraction(value)] for row, value in zip(matrix, rhs)]
    for column in range(8):
        pivot = next(index for index in range(column, 8) if rows[index][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [entry / scale for entry in rows[column]]
        for index in range(8):
            if index != column and rows[index][column]:
                factor = rows[index][column]
                rows[index] = [entry - factor * other for entry, other in zip(rows[index], rows[column])]
    return tuple(row[8] for row in rows)


def span_coordinates(values):
    pivots = {}
    coordinates = []
    for value in values:
        coordinate = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot][0]
                coordinate ^= pivots[pivot][1]
            else:
                bit = 1 << len(pivots)
                pivots[pivot] = (value, coordinate ^ bit)
                coordinate = bit
                break
        coordinates.append(coordinate)
    return len(pivots), coordinates


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def histogram():
    roots, frame = roots_and_frame()
    matrix = tuple(zip(*SIMPLE))
    coordinates = tuple(solve(matrix, row) for row in roots)
    labels = tuple(1 | (sum((int(entry) % 2) << index for index, entry in enumerate(coordinate)) << 1) for coordinate in coordinates)
    dots = tuple(tuple(sum(left * right for left, right in zip(first, second)) for second in roots) for first in roots)
    neighbors = tuple(sum(1 << index for index, value in enumerate(row) if abs(value) == 4) for row in dots)
    aggregate = Counter()
    pairs = 0
    for left, right in combinations(range(120), 2):
        if dots[left][right]:
            continue
        members = list(indices(neighbors[left] & neighbors[right]))
        dimension, local = span_coordinates(labels[index] for index in members)
        require(len(members) == 24 and dimension == 7, "a common core moved")
        sections = Counter(sum(1 << index for index, coordinate in zip(members, local) if not ((mask & coordinate).bit_count() % 2)).bit_count() for mask in range(1, 128))
        require(dict(sections) == EXPECTED, "a section histogram moved")
        aggregate.update(sections)
        pairs += 1
    require(pairs == 3780, "the pair count moved")
    return pairs, dict(sorted(aggregate.items()))


def evaluate():
    require(sha256(ROOT / GEOMETRY) == "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021", "geometry drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    pairs, aggregate = histogram()
    require(sum(EXPECTED.values()) == 127, "the section total moved")
    require(aggregate == {0: 3780, 8: 56700, 12: 362880, 16: 56700}, "the aggregate histogram moved")
    return {"orthogonal_pairs": pairs, "sections_per_pair": 127, "aggregate": {str(key): value for key, value in aggregate.items()}, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
