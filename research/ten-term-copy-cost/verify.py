#!/usr/bin/env python3
"""COPY cost of the published ten-term two-sided factorization.

The checker rebuilds the A8 labels, the standard binding, and the ten terms.
It does not exhaust character pairs.
"""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_TEN_TERM_COPY_COST terms=10 cost=72 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_TEN_TERM_COPY_COST " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parity(value):
    return bin(value).count("1") & 1


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


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


def rational_rank(rows):
    work = [[Fraction(entry) for entry in row] for row in rows]
    rank = 0
    width = len(work[0])
    for column in range(width):
        pivot = next((index for index in range(rank, len(work)) if work[index][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        for index in range(len(work)):
            if index != rank and work[index][column]:
                factor = work[index][column] / scale
                for entry in range(column, width):
                    work[index][entry] -= factor * work[rank][entry]
        rank += 1
    return rank


def alphabet():
    roots = []
    labels = []
    full = (1 << 9) - 1
    for left, right in combinations(range(9), 2):
        row = [0] * 9
        row[left], row[right] = 3, -3
        roots.append(tuple(row))
        labels.append(full ^ (1 << left) ^ (1 << right))
    for subset in combinations(range(9), 3):
        roots.append(tuple(2 if index in subset else -1 for index in range(9)))
        labels.append(sum(1 << index for index in subset))
    require(len(set(roots)) == len(set(labels)) == 120, "the root alphabet moved")
    require(binary_rank(labels) == 9, "the labels left rank nine")
    return roots, labels


def binding(roots):
    standard = []
    for left, right in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[left], row[right] = 2, 2 * sign
            standard.append(tuple(row))
    standard.extend(
        row for row in product((-1, 1), repeat=8)
        if row[0] == 1 and sum(entry < 0 for entry in row) % 2 == 0
    )
    require(len(set(standard)) == 120, "the standard roots moved")
    star = []
    for index in range(1, 8):
        row = [0] * 8
        row[0] = row[index] = 2
        star.append(tuple(row))
    star.append((1,) * 8)

    def canonical(row):
        return row if next(entry for entry in row if entry) > 0 else tuple(-entry for entry in row)

    lookup = {canonical(row): index for index, row in enumerate(roots)}
    oriented = [None] * 120
    for root in standard:
        inner = [dot(root, other) // 4 for other in star]
        total = sum(inner)
        image = tuple(3 * value - total // 3 for value in inner) + (-total // 3,)
        index = lookup[canonical(image)]
        sign = 1 if image == roots[index] else -1
        require(oriented[index] is None, "the binding is not injective")
        oriented[index] = tuple(sign * value for value in root)
    require(all(row is not None for row in oriented), "the binding missed a root")
    for left, row in enumerate(oriented):
        for right, other in enumerate(oriented):
            require(9 * dot(row, other) == 4 * dot(roots[left], roots[right]), "the binding scale moved")
    return tuple(tuple(Fraction(entry, 2) for entry in row) for row in oriented)


def multiple(left, right):
    index = next(position for position, entry in enumerate(right) if entry)
    value = left[index] / right[index]
    if all(entry == value * other for entry, other in zip(left, right)):
        return value
    return None


def factorization():
    roots, labels = alphabet()
    standard = binding(roots)

    def code(normal):
        return tuple(dot(root, normal) for root in standard)

    def unit(index, value=1):
        return tuple(Fraction(value) if position == index else 0 for position in range(120))

    def add(left, right, scale=1):
        return tuple(entry + scale * other for entry, other in zip(left, right))

    first = (1, 1, 0, 0, 0, 0, 0, 0)
    second = (1, 0, 1, 0, 0, 0, 0, 0)
    normals = [first, (0, 1, 0, 0, 0, 0, 0, 0), (1, 0, -1, 0, 0, 0, 0, 0)]
    dual = [second, (-1, 1, -1, 0, 0, 0, 0, 0), (0, 0, -1, 0, 0, 0, 0, 0)]
    for index in range(3, 8):
        axis = tuple(int(position == index) for position in range(8))
        normals.append(axis)
        dual.append(axis)
    require(all(dot(left, right) == int(i == j) for i, left in enumerate(normals) for j, right in enumerate(dual)), "the dual basis moved")
    first_index = next(index for index, root in enumerate(standard) if root == first or root == tuple(-entry for entry in first))
    second_index = next(index for index, root in enumerate(standard) if root == second or root == tuple(-entry for entry in second))
    mark = unit(first_index, code(first)[first_index])
    left = [mark] + [add(mark, code(normal), -1) for normal in normals]
    right = [tuple(-entry / 2 for entry in code(normal)) for normal in dual]
    right = [tuple(-sum(column[index] for column in right) for index in range(120))] + right
    correction = unit(second_index)
    column = tuple(dot(root, standard[second_index]) / 2 for root in standard)
    terms = [(row, add(column_row, correction, -column_row[second_index])) for row, column_row in zip(left, right)]
    terms.append((column, correction))
    require(len(terms) == 10, "the term count moved")
    require(all(any(row) and any(column_row) for row, column_row in terms), "a factor vanished")
    for side in (0, 1):
        for i, term in enumerate(terms):
            for earlier in terms[:i]:
                require(multiple(term[side], earlier[side]) is None, "a side has proportional factors")
    cost = 0
    for row, column_row in terms:
        columns = [label for label, value in zip(labels, column_row) if value]
        cost += binary_rank(
            sum(parity(label & column) << position for position, column in enumerate(columns))
            for label, value in zip(labels, row) if value
        )
    ranks = [rational_rank([list(term[side]) for term in terms]) for side in (0, 1)]
    for i, root in enumerate(roots):
        for j, other in enumerate(roots):
            value = sum(row[i] * column_row[j] for row, column_row in terms)
            require(value == Fraction(dot(root, other), 18), "the product left the root Gram")
    return cost, ranks


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    cost, ranks = factorization()
    require(cost == 72 and ranks == [9, 9] and 9 * (10 - 1 - 1) == 72, "the equality moved")
    return {"terms": 10, "copy_cost": 72, "ranks": [9, 9], "bound": 72, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
