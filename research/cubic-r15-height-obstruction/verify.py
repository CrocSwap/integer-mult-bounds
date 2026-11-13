#!/usr/bin/env python3
"""Exact finite apolar-pair exclusion. Produced by Nick Petalas."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import gcd
import json

HEIGHT = 64
TARGET = (105, 1015, 11025)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def primitive(row):
    a, b = row
    divisor = gcd(a, b)
    require(divisor != 0, "zero source row")
    sign = 1 if a > 0 or (a == 0 and b > 0) else -1
    return sign * a // divisor, sign * b // divisor


def dyadic(value):
    denominator = value.denominator
    return denominator & (denominator - 1) == 0


def coefficients(rows, weights):
    return tuple(sum(q * a ** (3 - j) * b ** j
                     for (a, b), q in zip(rows, weights, strict=True))
                 for j in range(4))


def third_row(u, v, target):
    a, b = u
    c, d = v
    s1, s2, s3 = target
    e = s1 * b * d - s2 * (b * c + a * d) + s3 * a * c
    f = s1 * (b * c + a * d) - s2 * a * c
    if e == f == 0:
        return None
    return primitive((f, -e))


def solve_weights(rows, target):
    s1, s2, s3 = target
    weights = [Fraction(0)] * 3
    for j, (a, b) in enumerate(rows):
        if a == 0:
            continue
        c, d = rows[(j + 1) % 3]
        e, f = rows[(j + 2) % 3]
        numerator = s2 * c * e - s1 * (d * e + c * f)
        denominator = a * (b * c - d * a) * (b * e - f * a)
        if numerator == 0 or denominator == 0:
            return "degenerate", None
        reduced = abs(denominator // gcd(numerator, denominator))
        if reduced & (reduced - 1):
            return "odd_denominator", None
        weights[j] = Fraction(numerator, denominator)
    for j, (a, b) in enumerate(rows):
        if a == 0:
            weights[j] = s3 - sum(weights[k] * rows[k][1] ** 3
                                  for k in range(3) if k != j)
    if any(q == 0 for q in weights):
        return "zero_weight", None
    if not all(dyadic(q) for q in weights):
        return "odd_denominator", None
    require(coefficients(rows, weights) == (0, s1, s2, s3),
            "coefficient reconstruction failed")
    return "admissible", tuple(weights)


def classify(u, v, target):
    w = third_row(u, v, target)
    if w is None:
        return "undetermined", None, None
    if w == u or w == v:
        return "repeated_direction", w, None
    tag, weights = solve_weights((u, v, w), target)
    return tag, w, weights


def controls():
    actual = tuple(sum(i ** j for i in range(15)) for j in range(1, 4))
    require(actual == TARGET, "wrong literal reader defect")
    u, v = (1, 0), (1, 1)
    tag, w, weights = classify(u, v, (1, 5, 13))
    require((tag, w, weights) ==
            ("admissible", (1, 2), (Fraction(1), Fraction(-3), Fraction(2))),
            "dyadic positive control failed")
    require(classify((0, 1), u, (-1, -1, 1))[0] == "admissible",
            "pure-B positive control failed")
    require(classify(u, (1, 3), (1, 15, 117))[0] == "odd_denominator",
            "odd denominator was accepted")
    target = (0, 16512, 2146560)
    require(classify(u, v, target)[1] == (1, 129),
            "third direction was bounded by the pair box")
    require(classify(u, v, (1, 1, 1))[0] == "undetermined",
            "rank-two degeneracy was hidden")
    require(coefficients((u, v, (1, 2)), (1, -3, 2)) != (0, 1, 5, 14),
            "changed B-cube coefficient was accepted")
    require(primitive((-6, -9)) == (2, 3), "primitive normalization failed")
    return 8


def scan():
    rows = [(0, 1)] + [(a, b) for a in range(1, HEIGHT + 1)
                          for b in range(-HEIGHT, HEIGHT + 1) if gcd(a, b) == 1]
    counts = Counter()
    for u, v in combinations(rows, 2):
        tag, w, weights = classify(u, v, TARGET)
        counts[tag] += 1
        require(tag != "admissible", f"counterexample: {u}, {v}, {w}, {weights}")
        require(tag != "undetermined", "unexpected unconstrained third direction")
    pairs = len(rows) * (len(rows) - 1) // 2
    require(sum(counts.values()) == pairs, "pair coverage mismatch")
    require(len(rows) == 5040 and pairs == 12698280, "wrong finite domain")
    return {"height": HEIGHT, "primitive_rows": len(rows), "pairs": pairs,
            "classification": dict(sorted(counts.items())), "admissible": 0}


def main():
    control_count = controls()
    result = scan()
    result["controls"] = control_count
    print(json.dumps(result, sort_keys=True))
    print("PASS_CUBIC_R15_HEIGHT_OBSTRUCTION")


if __name__ == "__main__":
    main()
