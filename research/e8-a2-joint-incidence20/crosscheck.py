"""Separate dense/norm reconstruction and extremal basis check. Apache-2.0."""

import json
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
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


def check(condition, message):
    if not condition:
        raise ValueError(message)


def dense_basis(values):
    check(len(values) <= 120, "bounded dense input")
    rows = [[v >> i & 1 for i in range(9)] for v in values]
    pivot = 0
    for col in range(9):
        selected = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return tuple(sum(bit << i for i, bit in enumerate(row)) for row in rows[:pivot])


def rebuilt_labels():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            roots.add(max(tuple(row), tuple(-x for x in row)))
    roots.update(
        max(row, tuple(-x for x in row))
        for row in product((-1, 1), repeat=8)
        if row.count(-1) % 2 == 0
    )
    matrix = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if matrix[i][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        divisor = matrix[col][col]
        matrix[col] = [x / divisor for x in matrix[col]]
        for i in range(8):
            if i != col:
                factor = matrix[i][col]
                matrix[i] = [
                    a - factor * b for a, b in zip(matrix[i], matrix[col], strict=True)
                ]
    labels = []
    for root in sorted(roots):
        coords = [sum(matrix[i][8 + j] * root[j] for j in range(8)) for i in range(8)]
        check(all(x.denominator == 1 for x in coords), "integral coordinates")
        labels.append(1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(coords)))
    check(len(set(labels)) == 120, "root label reconstruction")
    return tuple(labels)


def basis_closures(A, labels):
    closures = set()
    for chosen in combinations(A, 5):
        rows = dense_basis(chosen)
        if len(rows) != 5:
            continue
        values = {0}
        for row in rows:
            values |= {x ^ row for x in values}
        closures.add(tuple(sorted(set(labels).intersection(values))))
    check(all(len(c) <= 10 for c in closures), "fiber-contained full root cap")
    tight = {c for c in closures if len(c) == 10 and set(c) <= set(A)}
    check(len(tight) == 216, "all equality closures by five-label bases")
    return tight


def main():
    result = json.loads((HERE / "RESULT.json").read_text())
    labels = rebuilt_labels()
    A = tuple(labels[i] for i in result["canonical_fiber_indices"])
    check(sorted(A) == result["canonical_fiber_labels"], "canonical root ordering")
    tight = basis_closures(A, labels)
    check(
        tuple(result["attaining_support_labels"]) in tight, "actual attaining witness"
    )
    # Rebuild q by integer norms, without using the Cartan polynomial.
    table = []
    for x in range(256):
        row = [sum(SIMPLE[i][j] for i in range(8) if x >> i & 1) for j in range(8)]
        norm = sum(v * v for v in row)
        check(norm % 8 == 0, "even lattice norm")
        table.append(norm // 8 % 2)
    check(
        {v >> 1 for v in labels} == {x for x, value in enumerate(table) if value},
        "norm root bijection",
    )
    print("PASS_E8_A2_JOINT20_CROSSCHECK bases80730 equality216 norm256")


if __name__ == "__main__":
    main()
