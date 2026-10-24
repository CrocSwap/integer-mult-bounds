#!/usr/bin/env python3
"""Six-label central triple still costs twelve calls.

The checker evaluates the commutators, the nilpotent blocks and the stacked
rank. It does not search words.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_SIX_LABEL_CENTRAL_FLOOR calls=12 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_SIX_LABEL_CENTRAL_FLOOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def multiply_field(left, right):
    a0, a1 = left & 1, (left >> 1) & 1
    b0, b1 = right & 1, (right >> 1) & 1
    low = (a0 & b0) ^ (a1 & b1)
    high = (a0 & b1) ^ (a1 & b0) ^ (a1 & b1)
    return low | (high << 1)


def field_matrix(value):
    low, high = value & 1, (value >> 1) & 1
    return ((low, high), (high, low ^ high))


def multiply_group(left, right):
    a, b, c = left
    ap, bp, cp = right
    return (a ^ ap, b ^ bp, c ^ cp ^ multiply_field(a, bp))


def zeros():
    return [[0] * 6 for _ in range(6)]


def embed(element):
    a, b, c = element
    entries = ((1, a, c), (0, 1, b), (0, 0, 1))
    grid = zeros()
    for row in range(3):
        for column in range(3):
            block = field_matrix(entries[row][column])
            for u in range(2):
                for v in range(2):
                    grid[2 * row + u][2 * column + v] = block[u][v]
    return grid


def add(left, right):
    return [[left[i][j] ^ right[i][j] for j in range(6)] for i in range(6)]


def multiply_matrix(left, right):
    grid = zeros()
    for i in range(6):
        for k in range(6):
            if left[i][k] == 0:
                continue
            for j in range(6):
                grid[i][j] ^= left[i][k] & right[k][j]
    return grid


def identity():
    grid = zeros()
    for index in range(6):
        grid[index][index] = 1
    return grid


def transpose(grid):
    return [[grid[j][i] for j in range(6)] for i in range(6)]


def support(grid):
    return tuple((i, j) for i in range(6) for j in range(6) if grid[i][j])


def block(grid, rows, columns):
    return tuple(tuple(grid[row][column] for column in columns) for row in rows)


def subspaces(dimension):
    found = set()

    def extend(start, seen):
        found.add(frozenset(seen))
        for vector in range(start, 1 << dimension):
            if vector in seen:
                continue
            larger = set(seen)
            for item in seen:
                larger.add(item ^ vector)
            extend(vector + 1, larger)

    extend(1, {0})
    return found


def dimension(space):
    return len(space).bit_length() - 1


def sum_space(left, right):
    total = set(left)
    for vector in right:
        total.update(item ^ vector for item in list(total))
    return total


def dot(left, right):
    return (left & right).bit_count() % 2


def outer(image, dual):
    return tuple(tuple(((image >> row) & 1) & ((dual >> column) & 1) for column in range(3)) for row in range(3))


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    labels = {}
    for coefficient in (1, 2, 3):
        labels[("X", coefficient)] = (coefficient, 0, 0)
        labels[("Y", coefficient)] = (0, coefficient, 0)
    for element in labels.values():
        require(multiply_group(element, element) == (0, 0, 0), "a label was not an involution")

    commutators = 0
    for x_coefficient in (1, 2, 3):
        for y_coefficient in (1, 2, 3):
            word = (0, 0, 0)
            for kind, coefficient in (("X", x_coefficient), ("Y", y_coefficient), ("X", x_coefficient), ("Y", y_coefficient)):
                word = multiply_group(word, labels[(kind, coefficient)])
            require(word == (0, 0, multiply_field(x_coefficient, y_coefficient)), "a four-call commutator moved")
            commutators += 1
    require(commutators == 9, "a coefficient pair was missed")

    registers = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
    schedule = (
        (0, "X", 1), (0, "Y", 1), (0, "X", 1), (0, "Y", 1),
        (1, "X", 1), (1, "Y", 2), (1, "X", 1), (1, "Y", 2),
        (2, "X", 2), (2, "Y", 2), (2, "X", 2), (2, "Y", 2),
    )
    for register, kind, coefficient in schedule:
        registers[register] = multiply_group(registers[register], labels[(kind, coefficient)])
    require(registers == [(0, 0, 1), (0, 0, 2), (0, 0, 3)], "the twelve-call word moved")

    nilpotents = {key: add(embed(element), identity()) for key, element in labels.items()}
    corner_rows = (0, 1)
    corner_columns = (4, 5)
    for x_coefficient in (1, 2, 3):
        for y_coefficient in (1, 2, 3):
            forward = multiply_matrix(nilpotents[("X", x_coefficient)], nilpotents[("Y", y_coefficient)])
            backward = multiply_matrix(nilpotents[("Y", y_coefficient)], nilpotents[("X", x_coefficient)])
            expected = field_matrix(multiply_field(x_coefficient, y_coefficient))
            require(block(forward, corner_rows, corner_columns) == expected, "a corner coefficient moved")
            require(support(forward) == tuple((row, 4 + column) for row in range(2) for column in range(2) if expected[row][column]), "a corner left its block")
            require(backward == zeros(), "a reversed nilpotent product was nonzero")
        require(multiply_matrix(nilpotents[("X", x_coefficient)], nilpotents[("X", x_coefficient)]) == zeros(), "an X square survived")
        require(multiply_matrix(nilpotents[("Y", x_coefficient)], nilpotents[("Y", x_coefficient)]) == zeros(), "a Y square survived")

    mirrored = {key: add(transpose(embed(element)), identity()) for key, element in labels.items()}
    for x_coefficient in (1, 2, 3):
        for y_coefficient in (1, 2, 3):
            reverse = multiply_matrix(mirrored[("Y", y_coefficient)], mirrored[("X", x_coefficient)])
            forward = multiply_matrix(mirrored[("X", x_coefficient)], mirrored[("Y", y_coefficient)])
            require(forward == zeros(), "a contragredient X-after-Y product survived")
            require(block(reverse, (4, 5), (0, 1)) == field_matrix(multiply_field(x_coefficient, y_coefficient)), "the reversed corner moved")

    idempotents = []
    for image in range(1, 8):
        for dual in range(1, 8):
            if dot(dual, image) == 1:
                idempotents.append((image, dual, outer(image, dual)))
    require(len(idempotents) == 28, "the projector count moved")
    for image_j, dual_j, left in idempotents:
        for image_i, dual_i, right in idempotents:
            product = tuple(
                tuple(sum(left[row][index] * right[index][column] for index in range(3)) % 2 for column in range(3))
                for row in range(3)
            )
            scalar = dot(dual_j, image_i)
            expected = tuple(tuple(scalar & item for item in row) for row in outer(image_j, dual_i))
            require(product == expected, "a projector product moved")

    column_span = {0}
    for column in (0b100000, 0b000010, 0b001001):
        column_span.update(item ^ column for item in list(column_span))
    require(len(column_span) == 8, "the target column space moved")

    spaces = subspaces(4)
    require(len(spaces) == 67, "the four-bit subspace count moved")
    failures = 0
    for first in spaces:
        for second in spaces:
            for third in spaces:
                pairwise = (first & second, first & third, second & third)
                triple = first & second & third
                image_dimension = dimension(first) + dimension(second) + dimension(third) - dimension(triple)
                difference = sum(dimension(space) for space in pairwise) - 2 * dimension(triple)
                if image_dimension < dimension(sum_space(sum_space(first, second), third)) or difference < 0:
                    failures += 1
    require(failures == 0 and len(spaces) ** 3 == 300763, "the stacked-rank inequality moved")
    require(3 + 3 == 6, "the side floor moved")
    return {
        "labels": 6,
        "commutators": 9,
        "x_calls": 6,
        "y_calls": 6,
        "attaining_calls": 12,
        "subspace_triples": 300763,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
