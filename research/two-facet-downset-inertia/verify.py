#!/usr/bin/env python3
"""Exact finite corroboration of the two-facet inertia construction.

Produced by Nick Petalas. Apache-2.0.
Standard library only. No files are written.
"""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


MAX_GROUND = 6
MAX_ORDER = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    require(left and right and len(left[0]) == len(right), "matrix shape")
    columns = tuple(zip(*right))
    return [[sum(x * y for x, y in zip(row, col)) for col in columns]
            for row in left]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def zeta(width, nonempty=False):
    require(0 <= width <= MAX_GROUND, "zeta width")
    labels = range(int(nonempty), 1 << width)
    return [[int(t & s == t) for t in labels] for s in labels]


def inertia(matrix):
    """Symmetric rational elimination, including zero-diagonal 2x2 pivots."""
    size = len(matrix)
    require(1 <= size <= MAX_ORDER, "inertia size")
    require(all(len(row) == size for row in matrix), "square matrix")
    require(matrix == transpose(matrix), "symmetric matrix")
    work = [list(map(Fraction, row)) for row in matrix]
    positive = negative = zero = 0
    determinant = Fraction(1)
    for _ in range(size):
        if not work:
            break
        pivot = next((i for i in range(len(work)) if work[i][i]), None)
        if pivot is not None:
            work[0], work[pivot] = work[pivot], work[0]
            for row in work:
                row[0], row[pivot] = row[pivot], row[0]
            value = work[0][0]
            positive += value > 0
            negative += value < 0
            determinant *= value
            work = [[work[i][j] - work[i][0] * work[0][j] / value
                     for j in range(1, len(work))]
                    for i in range(1, len(work))]
            continue
        pair = next(((i, j) for i in range(len(work))
                     for j in range(i + 1, len(work)) if work[i][j]), None)
        if pair is None:
            zero += len(work)
            determinant = Fraction(0)
            break
        order = list(pair) + [i for i in range(len(work)) if i not in pair]
        work = [[work[i][j] for j in order] for i in order]
        value = work[0][1]
        positive += 1
        negative += 1
        determinant *= -value * value
        work = [[work[i][j] - (work[i][0] * work[1][j]
                              + work[i][1] * work[0][j]) / value
                 for j in range(2, len(work))]
                for i in range(2, len(work))]
    require(positive + negative + zero == size, "inertia exhausted")
    return (positive, negative, zero), determinant


def base_matrix(a, b, weighted=True):
    require(0 <= b <= a and a + b <= MAX_GROUND, "exclusive sizes")
    labels = [(s, 0) for s in range(1 << a)]
    labels += [(0, t) for t in range(1, 1 << b)]
    split = 1 << a
    matrix = []
    for i, (s, t) in enumerate(labels):
        row = []
        for j, (u, v) in enumerate(labels):
            if i < split and j < split:
                value = int(s & u == 0)
            elif i >= split and j >= split:
                value = int(t & v == 0)
            else:
                count = ((s & v) if i < split else (u & t)).bit_count()
                value = max(1, (1 << count) - 1) if weighted else 1
            row.append(value)
        matrix.append(row)
    return labels, matrix


def certificate(a, b, c):
    require(0 <= c and 1 <= a + b + c <= MAX_GROUND, "ground size")
    base_labels, base = base_matrix(a, b)
    labels = [core | (s << c) | (t << (c + a))
              for core in range(1 << c) for s, t in base_labels]
    size = len(base)
    matrix = [[int(x & y == 0) * base[i][j]
               for y in range(1 << c) for j in range(size)]
              for x in range(1 << c) for i in range(size)]
    return labels, matrix


def check_congruence(a, b):
    """Check the claimed zeta factorization by literal integer products."""
    _, matrix = base_matrix(a, b)
    first = 1 << a
    size = len(matrix)
    left = [[0] * size for _ in range(size)]
    for i, row in enumerate(zeta(a)):
        left[i][:first] = row
    if b:
        for i, row in enumerate(zeta(b, nonempty=True), start=first):
            left[i][first:] = row
    normal = [[0] * size for _ in range(size)]
    for s in range(first):
        normal[s][s] = (-1) ** s.bit_count()
    for t in range(1, 1 << b):
        j = first + t - 1
        normal[j][j] = (-1) ** t.bit_count()
        for u in range(1, 1 << b):
            normal[j][first + u - 1] += (
                (-1) ** (t.bit_count() + u.bit_count()))
        normal[0][j] = normal[j][0] = (-1) ** (t.bit_count() + 1)
        if t.bit_count() % 2 == 0:
            normal[t][j] = normal[j][t] = 2
    require(multiply(multiply(left, normal), transpose(left)) == matrix,
            "zeta congruence")


def expected(a, b, c, size):
    positive = size // 2 if c else 1 << (a - 1)
    exponent = ((1 << (b - 1)) - 1) * (1 << c) if b else 0
    negative = size - positive
    return (positive, negative, 0), (-1) ** negative * 3 ** exponent


def check_case(a, b, c):
    labels, matrix = certificate(a, b, c)
    size = len(matrix)
    require(len(set(labels)) == size, "distinct set labels")
    require(all(value >= 0 and isinstance(value, int)
                for row in matrix for value in row), "nonnegative integers")
    for i, s in enumerate(labels):
        for j, t in enumerate(labels):
            require(not s & t or matrix[i][j] == 0, "disjointness support")
    star = max(sum(bool(s & (1 << i)) for s in labels)
               for i in range(a + b + c))
    wanted, determinant = expected(a, b, c, size)
    require(star == wanted[0], "largest star")
    actual, direct_det = inertia(matrix)
    require(actual == wanted and direct_det == determinant, "exact inertia")
    return {"a": a, "b": b, "c": c, "order": size,
            "inertia": actual, "determinant": int(direct_det), "star": star}


def rejection_controls():
    _, plain = base_matrix(2, 2, weighted=False)
    controls = {"unweighted": inertia(plain)[0] == (3, 4, 0)}
    _, good = base_matrix(2, 2)
    controls["first_fixture"] = inertia(good) == ((2, 5, 0), Fraction(-3))
    good[3][6] = good[6][3] = 2
    controls["coupling_threshold"] = inertia(good)[0] == (2, 4, 1)
    controls["off_diagonal_pivot"] = (
        inertia([[0, 1], [1, 0]]) == ((1, 1, 0), Fraction(-1)))
    controls["zero_multiplicity"] = (
        inertia([[0, 0], [0, 0]]) == ((0, 0, 2), Fraction(0)))
    for name, value in (("asymmetric", [[1, 2], [0, 1]]),
                        ("nonsquare", [[1], [2]])):
        controls[name] = False
        try:
            inertia(value)
        except ValueError:
            controls[name] = True
    controls["invalid_sizes"] = False
    try:
        certificate(1, 2, 0)
    except ValueError:
        controls["invalid_sizes"] = True
    require(all(controls.values()), "control failure")
    return controls


def main():
    rows = []
    for ground in range(1, MAX_GROUND + 1):
        for c in range(ground + 1):
            for b in range((ground - c) // 2 + 1):
                a = ground - c - b
                if b > a:
                    continue
                check_congruence(a, b)
                rows.append(check_case(a, b, c))
    controls = rejection_controls()
    package = Path(__file__).resolve().parent
    files = [package / name for name in (
        "README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")]
    result = {"status": "PASS_TWO_FACET_DOWNSET_INERTIA",
              "claim_type": "scoped proof with finite exact corroboration",
              "cases": rows, "case_count": len(rows), "controls": controls,
              "control_count": len(controls),
              "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest()
                                for p in files}}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
