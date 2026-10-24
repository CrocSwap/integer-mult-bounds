#!/usr/bin/env python3
"""Exact, read-only corroboration of the fixed weighted-Gram obstruction."""
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path

P = ((1, 1, 0), (3, -1, 2), (3, -1, -6), (1, 0, 1))
D = (1, 3, 1)
EXPECTED = ((4, 0, 0, 1), (0, 16, 0, 5),
            (0, 0, 48, -3), (1, 5, -3, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def shape(rows):
    need(1 <= len(rows) <= 4, "one to four rows required")
    need(all(len(row) == 3 for row in rows), "three columns required")
    for row in rows:
        for value in row:
            need(type(value) in (int, Fraction), "exact rational required")
            value = Fraction(value)
            need(max(abs(value.numerator).bit_length(),
                     value.denominator.bit_length()) <= 32, "input capacity")


def valuation(value):
    value = Fraction(value)
    need(value != 0, "zero has no finite valuation")
    a, b = abs(value.numerator), value.denominator
    return (a & -a).bit_length() - (b & -b).bit_length()


def two_power(exponent):
    need(-128 <= exponent <= 128, "exponent capacity")
    return Fraction(2 ** max(0, exponent), 2 ** max(0, -exponent))


def anchors(left, right):
    shape(left)
    shape(right)
    need(len(left) == len(right), "factor row mismatch")
    active = tuple(j for j in range(3)
                   if any(row[j] for row in left)
                   and any(row[j] for row in right))
    need(bool(active), "no active column")
    m = {j: min(valuation(row[j]) for row in left if row[j]) for j in active}
    n = {j: min(valuation(row[j]) for row in right if row[j]) for j in active}
    gamma = min(m[j] + n[j] for j in active)
    a = tuple(sum(1 << j for j in active if row[j]
                  and valuation(row[j]) - m[j] == 0) for row in left)
    b = tuple(sum(1 << j for j in active if row[j]
                  and valuation(row[j]) + m[j] - gamma == 0) for row in right)
    return a, b, gamma


def matrix(left, right):
    shape(left)
    shape(right)
    need(len(left) == len(right), "factor row mismatch")
    return tuple(tuple(sum(Fraction(x) * y for x, y in zip(p, q))
                       for q in right) for p in left)


def dot(a, b):
    return (a & b).bit_count() % 2


def accepts(m, a, b, order, labels):
    size = len(m)
    if len(order) != len(labels) or len(set(order)) != len(order):
        return False
    if any(type(i) is not int or not 0 <= i < size for i in order):
        return False
    for i, (x, y) in zip(order, labels):
        if not 1 <= x < 8 or not 1 <= y < 8:
            return False
        if x & ~a[i] or y & ~b[i] or dot(x, y) != 1:
            return False
    return all(m[i][j] != 0 or dot(labels[u][0], labels[v][1]) == 0
               for u, i in enumerate(order)
               for v, j in enumerate(order) if u < v)


def enumerate_boxes(m, a, b):
    size = len(m)
    need(1 <= size <= 4 and len(a) == len(b) == size, "oracle capacity")
    need(all(m[i][i] != 0 for i in range(size)), "nonzero diagonal required")
    choices = tuple(tuple((x, y) for x in range(1, 8) for y in range(1, 8)
                          if not x & ~a[i] and not y & ~b[i] and dot(x, y))
                    for i in range(size))
    tested, valid = [0] * (size + 1), [0] * (size + 1)
    # At most sum_{k=0}^4 (4!/(4-k)!) * 28^k assignments.
    for k in range(size + 1):
        for order in permutations(range(size), k):
            for labels in product(*(choices[i] for i in order)):
                tested[k] += 1
                if accepts(m, a, b, order, labels):
                    valid[k] += 1
    return tested, valid


def check_result(left, weights):
    shape(left)
    need(len(weights) == 3 and all(x > 0 for x in weights), "positive metric")
    right = tuple(tuple(x * d for x, d in zip(row, weights)) for row in left)
    m = matrix(left, right)
    need(m == EXPECTED, "weighted matrix mismatch")
    a, b, gamma = anchors(left, right)
    need((a, b, gamma) == ((3, 3, 3, 5), (3, 3, 3, 5), 0), "anchor mismatch")
    need(all(m[i][j] == 0 for i in range(3) for j in range(3) if i != j),
         "principal triple must be mutually zero")
    need(m[0][0] * m[1][1] * m[2][2] == 3072, "rank-three minor mismatch")
    need(accepts(m, a, b, (0, 1, 3), ((1, 1), (2, 2), (1, 1))),
         "attaining witness rejected")
    return right, m, a, b


def expect_rejection(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError(message)


def controls(right, m, a, b):
    expect_rejection(lambda: check_result(P, (1, 1, 1)), "unweighted mutation")
    expect_rejection(lambda: check_result(P, (1, -3, 1)), "negative metric")
    expect_rejection(lambda: anchors(P, right[:-1]), "factor shape")
    need(not accepts(m, a, b, (0, 0), ((1, 1), (1, 1))), "duplicate row")
    need(not accepts(m, a, b, (0,), ((4, 4),)), "unsupported label")
    need(not accepts(m, a, b, (0,), ((1, 2),)), "diagonal parity")
    need(not accepts(m, a, b, (0, 1), ((1, 1), (1, 1))), "zero constraint")
    dm = ((1, 0), (1, 1))
    need(not accepts(dm, (1, 1), (1, 1), (0, 1), ((1, 1), (1, 1))),
         "directed zero not checked")
    need(accepts(dm, (1, 1), (1, 1), (1, 0), ((1, 1), (1, 1))),
         "reverse direction incorrectly constrained")
    expect_rejection(lambda: enumerate_boxes(((0,),), (1,), (1,)),
                     "zero diagonal accepted")
    for exponents in product(range(-2, 3), repeat=3):
        lp = tuple(tuple(x * two_power(e) for x, e in zip(row, exponents))
                   for row in P)
        rq = tuple(tuple(x / two_power(e) for x, e in zip(row, exponents))
                   for row in right)
        need(matrix(lp, rq) == m, "dual rescaling changed matrix")
        need(anchors(lp, rq) == (a, b, 0), "canonical rescaling failed")
    return 10, 125


def receipt(payload):
    root = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    payload["file_sha256"] = {name: sha256((root / name).read_bytes()).hexdigest()
                              for name in names}
    print(json.dumps(payload, sort_keys=True))


def main():
    right, m, a, b = check_result(P, D)
    tested, valid = enumerate_boxes(m, a, b)
    need(tested == [1, 24, 432, 5184, 31104], "enumeration coverage")
    need(valid == [1, 24, 288, 1296, 0], "admissible assignment counts")
    groups, rescalings = controls(right, m, a, b)
    receipt({"status": "PASS_WEIGHTED_GRAM_BOX", "box": 3, "rows": 4,
             "tested_by_size": tested, "valid_by_size": valid,
             "controls": groups, "dual_rescalings": rescalings,
             "claim_type": "scoped proof with finite exact corroboration"})


if __name__ == "__main__":
    main()
