#!/usr/bin/env python3
"""Uniform five-site and eight-site covers of the P112 roots.

The checker enumerates the orthogonal pairs. It does not infer an invoice floor.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_UNIFORM_COVER_COUNTS nonframe=3 frame=945 no_new_kappa"
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


def fail(message):
    raise SystemExit("FAIL_UNIFORM_COVER_COUNTS " + message)


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
    return tuple(sorted(roots)), frame


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


def binary_rank(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def span_coordinates(rows):
    pivots = {}
    coordinates = []
    for value in rows:
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


def covers():
    roots, frame_rows = roots_and_frame()
    frame = set(frame_rows)
    points = [row for row in roots if row not in frame]
    require(len(points) == 112 and len(frame) == 8, "the frame split moved")
    matrix = tuple(zip(*SIMPLE))
    coordinates = tuple(solve(matrix, row) for row in roots)
    labels = tuple(1 | (sum((int(entry) % 2) << index for index, entry in enumerate(coordinate)) << 1) for coordinate in coordinates)
    live = sum(1 << index for index, row in enumerate(roots) if row not in frame)
    frame_mask = ((1 << 120) - 1) ^ live
    dots = tuple(tuple(sum(left * right for left, right in zip(first, second)) for second in roots) for first in roots)
    neighbors = tuple(sum(1 << index for index, value in enumerate(row) if abs(value) == 4) for row in dots)
    counts = [0] * 120
    pairs = 0
    flats = 0
    for left, right in combinations(range(120), 2):
        if dots[left][right]:
            continue
        core = neighbors[left] & neighbors[right]
        members = list(indices(core))
        dimension, local = span_coordinates(labels[index] for index in members)
        require(len(members) == 24 and dimension == 7, "a common core moved")
        pairs += 1
        for mask in range(1, 128):
            low = sum(1 << index for index, coordinate in zip(members, local) if not ((mask & coordinate).bit_count() % 2))
            if low.bit_count() != 16 or low & frame_mask:
                continue
            for normal, mate in ((left, right), (right, left)):
                high = neighbors[normal] & ~neighbors[mate] & live
                target = (neighbors[normal] | (1 << normal)) & live
                sparse = target & ~(low | high)
                floor = 5 if live >> normal & 1 else 8
                if sparse.bit_count() != floor:
                    continue
                require(high.bit_count() == 32 and not high & low, "a cover partition moved")
                ranks = [binary_rank(labels[index] for index in indices(part)) for part in (high, low, sparse)]
                require(ranks == [7, 6, 4], "a cover rank moved")
                counts[normal] += 1
                if floor == 5:
                    flats += 1
    return pairs, counts, flats, live, frame_mask


def evaluate():
    require(sha256(ROOT / GEOMETRY) == "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021", "geometry drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    pairs, counts, flats, live, frame_mask = covers()
    nonframe = [counts[index] for index in range(120) if live >> index & 1]
    frame = [counts[index] for index in range(120) if frame_mask >> index & 1]
    require(pairs == 3780 and flats == 336, "the pair count moved")
    require(nonframe == [3] * 112 and frame == [945] * 8, "a root left its cover count")
    require(sum(nonframe) == 336 and sum(frame) == 7560, "a cover total moved")
    return {"orthogonal_pairs": 3780, "nonframe_covers": 3, "frame_covers": 945, "five_site_covers": 336, "eight_site_covers": 7560, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
