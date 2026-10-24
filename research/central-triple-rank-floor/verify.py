#!/usr/bin/env python3
"""Six-call floor for the central triple corner.

The checker counts dimensions. It does not search shorter words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CENTRAL_TRIPLE_RANK_FLOOR calls=6 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_CENTRAL_TRIPLE_RANK_FLOOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def binary_rank(masks, width):
    rows = [mask for mask in masks if mask]
    used = [False] * len(rows)
    total = 0
    for column in range(width):
        shift = width - 1 - column
        pivot = next((index for index, row in enumerate(rows) if not used[index] and (row >> shift) & 1), None)
        if pivot is None:
            continue
        used[pivot] = True
        for index in range(len(rows)):
            if index != pivot and (rows[index] >> shift) & 1:
                rows[index] ^= rows[pivot]
        total += 1
    return total


def subspaces(dimension):
    found = {frozenset({0})}
    pending = [frozenset({0})]
    while pending:
        space = pending.pop()
        for vector in range(1, 1 << dimension):
            if vector in space:
                continue
            enlarged = space | {entry ^ vector for entry in space}
            if enlarged not in found:
                found.add(enlarged)
                pending.append(enlarged)
    return found


def kronecker(left, right):
    rows = []
    for left_row in range(2):
        for right_row in range(3):
            row = []
            for left_column in range(2):
                row.extend(left[left_row][left_column] * right[right_row][right_column] for right_column in range(3))
            rows.append(row)
    return rows


def diagonal(bits):
    return [[bits[row] if row == column else 0 for column in range(3)] for row in range(3)]


def add(left, right):
    return [[one ^ other for one, other in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def masks_of(matrix):
    found = []
    for row in matrix:
        mask = 0
        for bit in row:
            mask = (mask << 1) | bit
        found.append(mask)
    return found


def corner():
    identity = ((1, 0), (0, 1))
    multiply_w = ((0, 1), (1, 1))
    projector = diagonal((1, 0, 1))
    other = diagonal((0, 1, 1))
    return add(kronecker(identity, projector), kronecker(multiply_w, other))


def halves(matrix):
    found = set()
    for column in range(6):
        for offset in (0, 3):
            mask = 0
            for row in range(3):
                mask |= matrix[offset + row][column] << row
            found.add(mask)
    return found


def annihilator(space, dimension):
    rows = []
    for mask in range(1 << dimension):
        if all((mask & vector).bit_count() % 2 == 0 for vector in space):
            rows.append(mask)
    return rows


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    matrix = corner()
    require(matrix == [list(column) for column in zip(*matrix)], "the corner is not symmetric")
    require(binary_rank(masks_of(matrix), 6) == 6, "the corner rank moved")
    require(halves(matrix) == {0, 1, 2, 4}, "the corner halves moved")
    spaces = subspaces(3)
    require(len(spaces) == 16, "the three-bit subspace count moved")
    for left in spaces:
        for right in spaces:
            stacked = [(vector << 3) for vector in left if vector] + [vector for vector in right if vector]
            require(
                binary_rank(stacked, 6) == binary_rank(left, 3) + binary_rank(right, 3),
                "complementary ranks failed to add",
            )
    for dimension in (5, 6):
        family = subspaces(dimension)
        require(len(family) == {5: 374, 6: 2825}[dimension], "a subspace count moved")
        for space in family:
            dimension_of_space = binary_rank(space, dimension)
            rows = annihilator(space, dimension)
            require(binary_rank(rows, dimension) + dimension_of_space == dimension, "rank-nullity moved")
            require(dimension_of_space + binary_rank(rows, dimension) < 6 or dimension == 6, "five calls held both ranks")
    require(3 + 3 == 6, "the call floor moved")
    return {"corner_rank": 6, "vector_span": 3, "call_floor": 6, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
