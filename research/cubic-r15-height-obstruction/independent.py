#!/usr/bin/env python3
"""Separate full pair census in two-query coordinates. Nick Petalas."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import gcd
import json

CAP = 64


def check(condition, message):
    if not condition:
        raise ValueError(message)


def is_dyadic(numerator, denominator):
    if numerator == 0 or denominator == 0:
        return False
    reduced = abs(denominator // gcd(numerator, denominator))
    return reduced & (reduced - 1) == 0


def transformed(u, v, target):
    a, b = u
    c, d = v
    c1, c2, c3 = target
    p0 = -c1 * d * d * c + c2 * d * c * c - c3 * c ** 3
    p1 = (c1 * (d * d * a + 2 * d * b * c)
          - c2 * (2 * d * c * a + b * c * c) + 3 * c3 * c * c * a)
    p2 = (-c1 * (2 * d * b * a + b * b * c)
          + c2 * (d * a * a + 2 * b * c * a) - 3 * c3 * c * a * a)
    p3 = c1 * b * b * a - c2 * b * a * a + c3 * a ** 3
    return a * d - b * c, (p0, p1, p2, p3)


def decide(u, v, target):
    determinant, (p0, p1, p2, p3) = transformed(u, v, target)
    check(determinant != 0, "dependent first two directions")
    if p1 == 0 or p2 == 0:
        return "zero_mixed_coefficient", None
    cube = determinant ** 3
    left = (3 * p0 * p2 - p1 * p1, 3 * cube * p2)
    right = (3 * p3 * p1 - p2 * p2, 3 * cube * p1)
    if not is_dyadic(*left) or not is_dyadic(*right):
        return "first_pair_not_dyadic_nonzero", None
    a, b = u
    c, d = v
    raw = (p1 * a + p2 * c, p1 * b + p2 * d)
    divisor = gcd(*raw)
    check(divisor > 0, "vanishing third source")
    last = (divisor ** 3, 3 * cube * p1 * p2)
    if not is_dyadic(*last):
        return "third_not_dyadic", None
    row = (raw[0] // divisor, raw[1] // divisor)
    if row[0] < 0 or (row[0] == 0 and row[1] < 0):
        row = (-row[0], -row[1])
        last = (-last[0], last[1])
    return "admissible", (row, Q(*left), Q(*right), Q(*last))


def controls():
    actual = [-15, 0, 0, 0]
    for i in range(15):
        for j, factor in enumerate((1, 3, 3, 1)):
            actual[j] += factor * i ** j
    check(actual == [0, 315, 3045, 11025], "wrong retained-child defect")
    tag, witness = decide((1, 0), (1, 1), (3, 15, 13))
    check(tag == "admissible" and witness == ((1, 2), Q(1), Q(-3), Q(2)),
          "independent positive control failed")
    check(decide((0, 1), (1, 0), (-3, -3, 1))[0] == "admissible",
          "independent pure-B control failed")
    check(decide((1, 0), (1, 3), (3, 45, 117))[0] != "admissible",
          "non-dyadic weights passed")
    tag, witness = decide((1, 0), (1, 1), (0, 49536, 2146560))
    check(tag == "admissible" and witness[0] == (1, 129),
          "unrestricted third row was truncated")
    for u, v in [((1, 0), (1, 1)), ((3, -2), (1, 4)), ((0, 1), (1, 7))]:
        det, ps = transformed(u, v, (315, 3045, 11025))
        for x, y in [(-3, 2), (0, 1), (5, -7)]:
            a, b = u
            c, d = v
            aa, bb = d * x - b * y, -c * x + a * y
            expected = 315 * aa * aa * bb + 3045 * aa * bb * bb + 11025 * bb ** 3
            check(sum(ps[j] * x ** (3 - j) * y ** j for j in range(4)) == expected,
                  "substitution coefficient error")
            check(det == a * d - b * c, "determinant error")
    return 14


def main():
    control_count = controls()
    vectors = [(0, 1)]
    for first in range(1, CAP + 1):
        for second in range(-CAP, CAP + 1):
            if gcd(first, second) == 1:
                vectors.append((first, second))
    counts = Counter()
    for u, v in combinations(vectors, 2):
        status, witness = decide(u, v, (315, 3045, 11025))
        counts[status] += 1
        check(status != "admissible", f"counterexample: {u}, {v}, {witness}")
    pairs = len(vectors) * (len(vectors) - 1) // 2
    check(sum(counts.values()) == pairs == 12698280, "pair coverage error")
    check(len(vectors) == 5040, "primitive row coverage error")
    print(json.dumps({"height": CAP, "primitive_rows": len(vectors), "pairs": pairs,
                      "classification": dict(sorted(counts.items())),
                      "admissible": 0, "controls": control_count}, sort_keys=True))
    print("PASS_CUBIC_R15_INDEPENDENT")


if __name__ == "__main__":
    main()
