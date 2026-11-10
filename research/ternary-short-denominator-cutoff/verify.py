#!/usr/bin/env python3
"""Exact finite corroboration of the short-decomposition denominator proof."""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement, permutations, product
import json
from pathlib import Path


IDENTITY = tuple(int(i == j) for i in range(3) for j in range(3))
SIGNS = tuple((1, a, b) for a, b in product((-1, 1), repeat=2))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def outer(u, v):
    require(len(u) == len(v) == 3, "three coordinates required")
    require(all(type(x) is int and x in (-1, 0, 1) for x in (*u, *v)),
            "ternary coordinates required")
    require(any(u) and any(v), "nonzero vectors required")
    return tuple(x * y for x in u for y in v)


def frame(u, v, exponent):
    require(type(exponent) is int and 1 <= exponent <= 256,
            "finite checker exponent must be in 1..256")
    return tuple(Fraction(x, 1 << exponent) for x in outer(u, v))


def matrix_sum(matrices):
    require(1 <= len(matrices) <= 8, "finite checker term limit exceeded")
    require(all(len(a) == 9 for a in matrices), "3 by 3 matrices required")
    return tuple(sum(a[i] for a in matrices) for i in range(9))


def check_sum(matrices, multiple):
    require(matrix_sum(matrices) == tuple(multiple * x for x in IDENTITY),
            "incorrect literal decomposition")


def check_ceiling(exponents, ceiling):
    require(all(j <= ceiling for j in exponents), "denominator ceiling exceeded")


def arithmetic_certificate():
    require(3 * Fraction(1, 8) + Fraction(1, 2) < 1, "three deepest terms fit")
    require(2 * Fraction(1, 8) + 2 * Fraction(1, 4) < 1, "two quarters fit")
    require(2 * Fraction(1, 8) + Fraction(1, 2) + Fraction(1, 4) == 1,
            "mixed case does not saturate every diagonal")
    require(2 * Fraction(1, 16) + Fraction(1, 2) + Fraction(1, 4) < 1,
            "mixed case can have a deeper exponent")
    require(2 * Fraction(1, 8) < Fraction(1, 2), "half-grid gap failed")
    require(Fraction(9, 2) > 3, "positive half square fits under the identity")
    require(3 * Fraction(1, 2) + Fraction(1, 4) + Fraction(1, 8) < 2,
            "five-term complement gap failed")
    require(Fraction(1, 8) < 1, "integer off-diagonal gap failed")
    return 8


def denominator_profiles():
    checked = 0
    surviving = []
    for length in range(1, 5):
        for js in combinations_with_replacement(range(1, 13), length):
            checked += 1
            if js[-1] < 3 or js.count(js[-1]) == 1:
                continue
            if sum(Fraction(1, 1 << j) for j in js) < 1:
                continue
            require(js == (1, 1, js[-1], js[-1]) or js == (1, 2, 3, 3),
                    "unclassified deep denominator profile")
            surviving.append(js)
    expected = [(1, 1, j, j) for j in range(3, 13)] + [(1, 2, 3, 3)]
    require(sorted(surviving) == sorted(expected), "profile coverage differs")
    return checked, len(surviving)


def binary_leading_terms():
    vectors = tuple(v for v in product((-1, 0, 1), repeat=3) if any(v))
    checked = 0
    full_diagonal = set()
    for u, v in product(vectors, repeat=2):
        a = outer(u, v)
        require(any(x % 2 for x in a), "unique deepest numerator vanished")
        if all(a[i] == 1 for i in (0, 4, 8)):
            require(u == v and all(u), "positive full diagonal is not a square")
            full_diagonal.add(a)
        checked += 1
    require(full_diagonal == {outer(w, w) for w in SIGNS},
            "full-diagonal square classification differs")
    return checked, len(full_diagonal)


def half_pair_obstructions():
    checked = 0
    for u, v in product(SIGNS, repeat=2):
        a = matrix_sum((frame(u, u, 1), frame(v, v, 1)))
        residual = tuple(t - x for t, x in zip(IDENTITY, a, strict=True))
        require(all(x.denominator == 1 for x in residual), "integer gap lost")
        require(max(map(abs, residual)) >= 1, "two rank-one halves became I3")
        for exponent in range(3, 257):
            require(max(map(abs, residual)) > Fraction(2, 1 << exponent),
                    "deep pair can cover the residual")
            checked += 1
    return checked


def mixed_case_obstructions():
    checked = 0
    for u, v, w, z in product(SIGNS, repeat=4):
        a = matrix_sum((frame(u, u, 1), frame(v, v, 2),
                        frame(w, w, 3), frame(z, z, 3)))
        quadratic = sum(u[i] * a[3 * i + j] * u[j]
                        for i in range(3) for j in range(3))
        require(quadratic >= Fraction(9, 2), "positive square contribution lost")
        require(quadratic > sum(x * x for x in u), "mixed identity escaped")
        require(a != IDENTITY, "false mixed-case exclusion")
        checked += 1
    return checked


def five_term_obstructions():
    checked = 0
    zero_remainders = 0
    for vectors in product(SIGNS, repeat=4):
        a = matrix_sum(tuple(frame(v, v, 1) for v in vectors))
        residual = tuple(2 * t - x for t, x in zip(IDENTITY, a, strict=True))
        require(all(x.denominator == 1 for x in residual), "four-half sum not integral")
        if not any(residual):
            zero_remainders += 1
        else:
            require(max(map(abs, residual)) >= 1, "nonzero integer gap lost")
        for exponent in range(3, 65):
            require(not any(residual) or max(map(abs, residual)) > Fraction(1, 1 << exponent),
                    "deep frame can cover the complement residual")
            checked += 1
    require(zero_remainders > 0, "zero-residual branch was not exercised")
    return checked, zero_remainders


def attainers():
    checked = 0
    for permutation in permutations(range(3)):
        for signs in product((-1, 1), repeat=3):
            vectors = tuple(tuple(signs[i] * w[permutation[i]] for i in range(3))
                            for w in SIGNS)
            quarter = tuple(frame(w, w, 2) for w in vectors)
            half = tuple(frame(w, w, 1) for w in vectors)
            check_sum(quarter, 1)
            check_sum((*half[:3], quarter[3], quarter[3]), 2)
            eighth = frame(vectors[3], vectors[3], 3)
            check_sum((*quarter[:3], eighth, eighth), 1)
            check_sum((*half[:3], quarter[3], eighth, eighth), 2)
            checked += 4
    return checked


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise ValueError("a false boundary was accepted")


def rejection_controls():
    w = SIGNS[0]
    quarter = tuple(frame(v, v, 2) for v in SIGNS)
    count = rejects(frame, (0, 0, 0), w, 2)
    count += rejects(frame, (2, 0, 1), w, 2)
    count += rejects(frame, (1, 1), w, 2)
    count += rejects(frame, w, w, 0)
    count += rejects(frame, w, w, True)
    count += rejects(frame, w, w, 257)
    count += rejects(check_sum, quarter[:3], 1)
    count += rejects(check_sum, (*quarter[:3], frame(w, w, 3)), 1)
    count += rejects(check_ceiling, (2, 2, 2, 2), 1)
    count += rejects(check_ceiling, (2, 2, 2, 3, 3), 2)
    count += rejects(check_ceiling, (1, 1, 1, 2, 3, 3), 2)
    count += rejects(matrix_sum, ())
    return count


def run():
    return {
        "status": "PASS_TERNARY_SHORT_DENOMINATOR_CUTOFF",
        "claim_type": "scoped written proof with exact finite corroboration",
        "arithmetic_inequalities": arithmetic_certificate(),
        "denominator_profiles": denominator_profiles(),
        "ternary_numerator_pairs": binary_leading_terms(),
        "half_pair_gap_checks": half_pair_obstructions(),
        "mixed_square_obstructions": mixed_case_obstructions(),
        "five_term_gap_checks": five_term_obstructions(),
        "sharp_attaining_decompositions": attainers(),
        "rejecting_controls": rejection_controls(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = run()
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        path = root / name
        require(path.stat().st_size <= 128 * 1024, "package file exceeds checker bound")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["sha256"] = hashes
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        target = args.receipt.resolve()
        require(root not in target.parents, "receipt must remain outside the package")
        with target.open("x", encoding="utf-8") as stream:
            require(stream.write(encoded) == len(encoded), "incomplete receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
