#!/usr/bin/env python3
"""Exact finite corroboration of the written Gaussian fill-sign theorem."""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import lcm
import json
from pathlib import Path
import platform
import sys

MAX_N = 12
MAX_B = 12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def kernel(n, b, t):
    require(type(n) is int and 1 <= n <= MAX_N, "unsupported dimension")
    require(type(b) is int and 1 <= b <= MAX_B, "unsupported bandwidth")
    require(isinstance(t, Fraction) and 0 < t <= Fraction(1, 3), "t outside theorem")
    return [[t ** ((i-j)**2) if abs(i-j) <= b else Fraction(0)
             for j in range(n)] for i in range(n)]


def determinant(matrix):
    """Integer Bareiss elimination after exact denominator clearing."""
    n = len(matrix)
    if n == 0:
        return Fraction(1)
    require(n <= MAX_N and all(len(row) == n for row in matrix), "bad minor")
    denominator = 1
    for row in matrix:
        for value in row:
            denominator = lcm(denominator, value.denominator)
    a = [[int(value * denominator) for value in row] for row in matrix]
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        p = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                quotient, remainder = divmod(a[i][j]*p-a[i][k]*a[k][j], previous)
                require(remainder == 0, "inexact Bareiss division")
                a[i][j] = quotient
            a[i][k] = 0
        previous = p
    return Fraction(sign * a[-1][-1], denominator ** n)


def inverse(matrix):
    """Independent rational Gauss-Jordan inverse for Schur computation."""
    n = len(matrix)
    require(n <= MAX_N and all(len(row) == n for row in matrix), "bad inverse")
    a = [list(row) + [Fraction(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for k in range(n):
        require(a[k][k] != 0, "nonpositive-principal-pivot fixture")
        pivot = a[k][k]
        a[k] = [x / pivot for x in a[k]]
        for i in range(n):
            if i != k:
                scale = a[i][k]
                a[i] = [x - scale*y for x, y in zip(a[i], a[k])]
    require(all(a[i][j] == (i == j) for i in range(n) for j in range(n)),
            "inverse left block")
    return [row[n:] for row in a]


def minor(a, rows, columns):
    return [[a[i][j] for j in columns] for i in rows]


def schur(a, eliminated):
    n = len(a)
    survivors = [i for i in range(n) if i not in eliminated]
    inv = inverse(minor(a, eliminated, eliminated))
    s = [[a[i][j] - sum(a[i][u]*inv[r][c]*a[v][j]
                       for r, u in enumerate(eliminated)
                       for c, v in enumerate(eliminated))
          for j in survivors] for i in survivors]
    return survivors, s


def predicted_sign(i, j, eliminated, b):
    if i == j:
        return 1
    lo, hi = sorted((i, j))
    between = [e for e in eliminated if lo < e < hi]
    chain = [lo] + between + [hi]
    if any(v-u > b for u, v in zip(chain, chain[1:])):
        return 0
    return (-1) ** len(between)


def check_root_signs():
    evaluations = 0
    for t in (Fraction(1, 3), Fraction(1, 4)):
        require(2*t/(1-t*t) <= Fraction(3, 4), "root dominance")
        for b in range(1, MAX_B + 1):
            for j in range(-b, b + 1):
                z = -(t ** (-2*j))
                value = Fraction(0)
                for h in range(b, -b - 1, -1):
                    value = value*z + t ** (h*h)
                require(value * (-1)**(j+b) > 0, "root isolation sign")
                evaluations += 1
    return evaluations


def check_minors():
    counts = {"minors": 0, "positive": 0, "zero": 0, "paths": 0}
    for t in (Fraction(1, 3), Fraction(1, 4)):
        for b in range(1, 4):
            a = kernel(6, b, t)
            for size in range(1, 7):
                subsets = list(combinations(range(6), size))
                for rows in subsets:
                    for columns in subsets:
                        expected = all(abs(r-c) <= b for r, c in zip(rows, columns))
                        value = determinant(minor(a, rows, columns))
                        require(value >= 0 and (value > 0) == expected, "ordered minor")
                        counts["minors"] += 1
                        counts["positive" if value > 0 else "zero"] += 1
                        if expected:
                            path = [[max(c, r+b-(2*b-s)) for r, c in zip(rows, columns)]
                                    for s in range(2*b + 1)]
                            require(path[0] == list(columns), "path starts")
                            require(path[-1] == [r+b for r in rows], "path ends")
                            require(all(x < y for row in path for x, y in zip(row, row[1:])),
                                    "path collision")
                            require(all(path[s+1][k]-path[s][k] in (0, 1)
                                        for s in range(2*b) for k in range(size)), "path step")
                            counts["paths"] += 1
    return counts


def check_schurs():
    counts = {"layouts": 0, "entries": 0, "positive": 0, "negative": 0, "zero": 0}
    for t in (Fraction(1, 3), Fraction(1, 4)):
        for b in range(1, 4):
            for n in range(1, 9):
                a = kernel(n, b, t)
                for mask in range(2**n - 1):
                    e = [i for i in range(n) if mask >> i & 1]
                    require(determinant(minor(a, e, e)) > 0, "principal determinant")
                    survivors, s = schur(a, e)
                    counts["layouts"] += 1
                    for r, i in enumerate(survivors):
                        for c, j in enumerate(survivors):
                            expected = predicted_sign(i, j, e, b)
                            actual = (s[r][c] > 0) - (s[r][c] < 0)
                            require(actual == expected, "Schur support/sign")
                            counts["entries"] += 1
                            counts[{1: "positive", -1: "negative", 0: "zero"}[actual]] += 1
    return counts


def check_fixture_and_controls():
    a = kernel(12, 3, Fraction(1, 3))
    e = [4, 5, 6, 7]
    v, s = schur(a, e)
    value = s[v.index(1)][v.index(10)]
    require(value == Fraction(1, 9170703360), "first Gaussian fixture")
    require(v.index(10)-v.index(1) == 5, "boundary distance")
    left = [Fraction(i+1) for i in range(12)]
    right = [Fraction(1, i+2) for i in range(12)]
    gauged = [[left[i]*a[i][j]*right[j] for j in range(12)] for i in range(12)]
    w, gs = schur(gauged, e)
    require(w == v and all(gs[r][c] == left[i]*s[r][c]*right[j]
                           for r, i in enumerate(v) for c, j in enumerate(v)), "positive gauges")
    rejected = 0
    for args in ((0, 1, Fraction(1, 3)), (13, 1, Fraction(1, 3)),
                 (3, 0, Fraction(1, 3)), (3, 13, Fraction(1, 3)),
                 (3, 1, Fraction(0)), (3, 1, Fraction(1, 2))):
        try:
            kernel(*args)
        except ValueError:
            rejected += 1
    require(rejected == 6, "boundary rejections")
    require(determinant([[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]]) == 0,
            "unrestricted-t singular control")
    require(predicted_sign(0, 2, [], 1) == 0 and Fraction(1, 3)**4 > 0,
            "truncation is essential")
    require(predicted_sign(0, 2, [1], 1) == -1, "interior parity is essential")
    return {"first_entry": str(value), "boundary_distance": 5, "rejections": rejected,
            "scope_controls": 3, "positive_gauges": 1}


def main():
    require(len(sys.argv) == 1, "no command-line arguments accepted")
    result = {"root_evaluations": check_root_signs(), "minor_checks": check_minors(),
              "schur_checks": check_schurs(), "fixtures": check_fixture_and_controls()}
    package = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result["package_sha256"] = {name: sha256((package / name).read_bytes()).hexdigest()
                                for name in names}
    result["python"] = platform.python_version()
    print(json.dumps(result, sort_keys=True))
    print("PASS_GAUSSIAN_SCHUR_FILL_SIGN t<=1/3 first_entry=1/9170703360 no_new_kappa")


if __name__ == "__main__":
    main()
