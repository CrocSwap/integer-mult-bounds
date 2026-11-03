#!/usr/bin/env python3
"""Exact corroboration of the sharp real two-wire dyadic approximation floor."""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def conjugate(z):
    return z[0], -z[1]


def multiply(z, w):
    return z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0]


def inner(v, w):
    require(len(v) == len(w) <= 3, "inner-product dimension")
    terms = [multiply(conjugate(z), t) for z, t in zip(v, w)]
    return sum(z[0] for z in terms), sum(z[1] for z in terms)


def columns(matrix):
    return tuple(zip(*matrix))


def unitary_numerator(matrix):
    """All matrices here have common denominator two."""
    size = len(matrix)
    require(1 <= size <= 3, "matrix dimension")
    require(all(len(row) == size for row in matrix), "square matrix")
    cols = columns(matrix)
    return all(inner(cols[i], cols[j]) == (4 * (i == j), 0)
               for i in range(size) for j in range(size))


def first_columns():
    axes = []
    for index in range(4):
        for sign in (-2, 2):
            vector = [0] * 4
            vector[index] = sign
            axes.append(tuple(vector))
    vectors = axes + list(itertools.product((-1, 1), repeat=4))
    return tuple(((v[0], v[1]), (v[2], v[3])) for v in vectors)


def dyadic_group():
    vectors = first_columns()
    require(len(set(vectors)) == 24, "24 possible first columns")
    matrices = set()
    for v in vectors:
        z = conjugate(v[1])
        perpendicular = ((-z[0], -z[1]), conjugate(v[0]))
        for phase in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            w = tuple(multiply(phase, z) for z in perpendicular)
            matrices.add(((v[0], w[0]), (v[1], w[1])))
    blind = {((v[0], w[0]), (v[1], w[1]))
             for v in vectors for w in vectors if inner(v, w) == (0, 0)}
    require(matrices == blind and len(matrices) == 96, "complete column join")
    require(all(unitary_numerator(m) for m in matrices), "group unitarity")
    return tuple(sorted(matrices))


def real_targets():
    targets = set()
    for p in range(-12, 13):
        for q in range(1, 13):
            a, b, d = q * q - p * p, 2 * p * q, p * p + q * q
            common = math.gcd(math.gcd(a, b), d)
            targets.add((a // common, b // common, d // common))
    targets.add((-1, 0, 1))
    result = []
    for a, b, d in sorted(targets):
        require(a * a + b * b == d * d and d <= 288, "circle parametrization")
        result.append((((a, -b), (b, a)), d))
        result.append((((a, b), (b, -a)), d))
    return tuple(result)


def error_gram(target, denominator, candidate):
    """Return the Hermitian error Gram times 4*denominator**2."""
    delta = tuple(tuple((denominator * candidate[i][j][0] - 2 * target[i][j],
                         denominator * candidate[i][j][1]) for j in range(2))
                  for i in range(2))
    left, right = columns(delta)
    aa, bb = inner(left, left), inner(right, right)
    require(aa[1] == bb[1] == 0, "real Gram diagonal")
    return aa[0], bb[0], inner(left, right)


def spectral_relations(gram, threshold):
    """Use exact two-by-two principal minors, without numerical eigenvalues."""
    aa, bb, off = gram
    x, y = threshold - aa, threshold - bb
    determinant = x * y - off[0] ** 2 - off[1] ** 2
    strictly_below = x > 0 and determinant > 0
    at_most = x >= 0 and y >= 0 and determinant >= 0
    return strictly_below, at_most


def check_target(target, denominator, group, threshold=None):
    require(denominator > 0, "positive target denominator")
    maximum = max(abs(x) for row in target for x in row)
    expected = 8 * denominator * (denominator - maximum)
    threshold = expected if threshold is None else threshold
    attainments = 0
    real_attainments = 0
    for candidate in group:
        gram = error_gram(target, denominator, candidate)
        below, at_most = spectral_relations(gram, threshold)
        require(not below, "candidate improves the stated minimum")
        if at_most:
            attainments += 1
            if all(z[1] == 0 for row in candidate for z in row):
                require(gram == (threshold, threshold, (0, 0)), "scalar error Gram")
                real_attainments += 1
    require(attainments > 0 and real_attainments > 0, "sharp real attainer")
    divisor = math.gcd(expected, 4 * denominator * denominator)
    return [expected // divisor, 4 * denominator * denominator // divisor,
            attainments, real_attainments]


def restored_helper_controls(group):
    """Enumerate nonzero leakage with an exactly unchanged independent helper."""
    count = 0
    for matrix in group:
        for coupling in first_columns():
            padded = ((matrix[0][0], matrix[0][1], coupling[0]),
                      (matrix[1][0], matrix[1][1], coupling[1]),
                      ((0, 0), (0, 0), (2, 0)))
            require(not unitary_numerator(padded), "uncharged helper leakage")
            count += 1
        padded = ((matrix[0][0], matrix[0][1], (0, 0)),
                  (matrix[1][0], matrix[1][1], (0, 0)),
                  ((0, 0), (0, 0), (2, 0)))
        require(unitary_numerator(padded), "restored-helper positive control")
    return count


def expect_failure(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("mutation was not rejected")


def controls(group):
    target = ((3, -4), (4, 3))
    baseline = check_target(target, 5, group)
    require(baseline[:2] == [2, 5], "3/5,4/5 sharp example")
    expect_failure(check_target, target, 5, group, 41)
    expect_failure(check_target, target, 5, group, 39)
    expect_failure(check_target, target, 5, ())
    expect_failure(check_target, target, 0, group)
    expect_failure(unitary_numerator, (((2, 0),), ((0, 0),)))
    damaged = (((2, 0), (0, 1)), ((0, 0), (2, 0)))
    require(not unitary_numerator(damaged), "nonunitary imaginary mutation")
    # (5I+6J)/8 is dyadic and far closer, but its norm square is 61/64.
    require(5 * 5 + 6 * 6 == 61 != 64, "nonunitary dyadic escape")
    require((5 * 5 - 3 * 8) ** 2 + (6 * 5 - 4 * 8) ** 2 == 5,
            "dyadic escape squared error is 5/1600=1/320")
    require(5 * 5 + 6 * 6 != 8 * 8 and 1 * 5 < 2 * 320,
            "escape beats 2/5 only outside exact unitarity")
    return {"rejected_mutations": 6, "nonunitary_escape_squared_error": "1/320",
            "rational_unitary_escape_squared_error": "0"}


def package_hashes():
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        path = directory / name
        require(path.stat().st_size <= 1_000_000, "bounded package input")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    require(len(sys.argv) == 1, "this fixed-domain checker accepts no arguments")
    group = dyadic_group()
    transcript = []
    for target, denominator in real_targets():
        transcript.append([target, denominator, check_target(target, denominator, group)])
    payload = json.dumps(transcript, separators=(",", ":"), sort_keys=True).encode()
    result = {"status": "PASS_DYADIC_TWO_WIRE_APPROXIMATION",
              "claim_type": "scoped written proof with exact finite corroboration",
              "dyadic_unit_vectors": 24, "dyadic_unitaries": len(group),
              "rational_orthogonal_targets": len(transcript),
              "operator_comparisons": len(transcript) * len(group),
              "restored_helper_leakage_rejections": restored_helper_controls(group),
              "restored_helper_positive_controls": len(group),
              "controls": controls(group),
              "transcript_sha256": hashlib.sha256(payload).hexdigest(),
              "package_sha256": package_hashes()}
    canonical = json.dumps(result, separators=(",", ":"), sort_keys=True).encode()
    result["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
