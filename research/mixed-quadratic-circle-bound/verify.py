#!/usr/bin/env python3
"""Exact finite corroboration for the mixed-quadratic circle bound."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from itertools import product
from math import isqrt
from pathlib import Path

G = tuple[F, F]
ZERO: G = (F(0), F(0))
ONE: G = (F(1), F(0))
PHASES: tuple[G, ...] = (ONE, (F(-1), F(0)), (F(0), F(1)), (F(0), F(-1)))
HERE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(a: G, b: G) -> G:
    return a[0] + b[0], a[1] + b[1]


def neg(a: G) -> G:
    return -a[0], -a[1]


def mul(a: G, b: G) -> G:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def abs2(a: G) -> F:
    return a[0] ** 2 + a[1] ** 2


def scale(a: G, value: F) -> G:
    return a[0] * value, a[1] * value


def inverse(a: G) -> G:
    norm = abs2(a)
    need(norm != 0, "singular scalar")
    return a[0] / norm, -a[1] / norm


def power(a: G, exponent: int) -> G:
    need(0 <= exponent <= 64, "power bound")
    result = ONE
    for _ in range(exponent):
        result = mul(result, a)
    return result


def contract(a: G, b: G) -> None:
    need(abs2(a) < 1 and 0 < abs2(b) < 1, "mixed-root domain")


def sqrt_bounds(value: F) -> tuple[F, F]:
    need(value >= 0, "nonnegative square")
    numerator, denominator = isqrt(value.numerator), isqrt(value.denominator)
    if numerator**2 == value.numerator and denominator**2 == value.denominator:
        exact = F(numerator, denominator)
        return exact, exact
    bits = 1 << 96
    lower = isqrt(value.numerator * bits**2 // value.denominator)
    return F(lower, bits), F(lower + 1, bits)


def circle_checks() -> int:
    count = 0
    for A, B, alpha, beta in product(
        (F(0), F(1, 4), F(1, 2), F(3, 4)),
        (F(1, 4), F(1, 2), F(3, 4)), PHASES, PHASES
    ):
        a, b = scale(alpha, A), scale(beta, B)
        contract(a, b)
        wiener2 = ((1 - A * B) / ((1 - A) * (1 - B))) ** 2
        wiener2 /= abs2(add(ONE, neg(mul(a, b))))
        z = alpha if A >= B else (beta[0], -beta[1])
        endpoint2 = abs2(mul(add(z, neg(a)), add(ONE, neg(mul(b, z)))))
        m = min(A, B)
        cap = (1 + m) ** 2 / (1 + m * m)
        need(endpoint2 * wiener2 <= cap**2, "sharp endpoint inequality")
        count += 1
    return count


def kernel(a: G, b: G, length: int, stride: int, tau: G) -> list[G]:
    need(1 <= length <= 6 and -1 <= stride <= 2, "finite cyclic domain")
    contract(a, b)
    need(abs2(tau) == 1, "unit gauge")
    coefficients = [neg(a), add(ONE, mul(a, b)), neg(b)]
    row = [ZERO] * length
    for degree, coefficient in enumerate(coefficients):
        slot = degree * stride % length
        row[slot] = add(row[slot], mul(coefficient, power(tau, degree)))
    return row


def convolution(a: list[G], b: list[G]) -> list[G]:
    need(len(a) == len(b) and 1 <= len(a) <= 6, "convolution shape")
    length = len(a)
    result = [ZERO] * length
    for i in range(length):
        for j in range(length):
            slot = (i + j) % length
            result[slot] = add(result[slot], mul(a[i], b[j]))
    return result


def geometric_inverse(a: G, b: G, length: int, stride: int, tau: G) -> list[G]:
    contract(a, b)
    need(1 <= length <= 6 and -1 <= stride <= 2 and abs2(tau) == 1,
         "geometric cyclic domain")
    left, right = [ZERO] * length, [ZERO] * length
    left_den = inverse(add(power(tau, length), neg(power(a, length))))
    right_den = inverse(add(ONE, neg(mul(power(b, length), power(tau, length)))))
    for k in range(length):
        slot = k * stride % length
        left_term = mul(mul(power(a, length - 1 - k), power(tau, k)), left_den)
        right_term = mul(mul(power(b, k), power(tau, k)), right_den)
        left[slot] = add(left[slot], left_term)
        right[slot] = add(right[slot], right_term)
    return convolution(left, right)


def dense_inverse(row: list[G]) -> list[G]:
    length = len(row)
    need(1 <= length <= 6, "dense size bound")
    matrix = [[row[(i - j) % length] for j in range(length)]
              + [ONE if i == 0 else ZERO] for i in range(length)]
    for column in range(length):
        pivot = next((i for i in range(column, length) if matrix[i][column] != ZERO), None)
        need(pivot is not None, "singular cyclic polynomial")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = inverse(matrix[column][column])
        matrix[column] = [mul(value, divisor) for value in matrix[column]]
        for i in range(length):
            if i != column:
                coefficient = matrix[i][column]
                matrix[i] = [add(x, neg(mul(coefficient, y)))
                             for x, y in zip(matrix[i], matrix[column])]
    return [matrix[i][-1] for i in range(length)]


def cyclic_checks() -> dict[str, int]:
    root_pairs = ((ZERO, (F(1, 2), F(0))),
                  ((F(1, 2), F(0)), (F(-1, 2), F(0))),
                  ((F(3, 4), F(0)), (F(-3, 4), F(0))),
                  ((F(1, 4), F(0)), (F(1, 2), F(0))),
                  ((F(0), F(1, 2)), (F(1, 4), F(0))),
                  ((F(1, 4), F(0)), (F(0), F(3, 4))),
                  ((F(0), F(1, 2)), (F(0), F(1, 2))),
                  ((F(0), F(-1, 2)), (F(1, 2), F(0))))
    count, entries, antipodal = 0, 0, 0
    for (a, b), length, stride, tau in product(root_pairs, range(1, 7), range(-1, 3), PHASES):
        row = kernel(a, b, length, stride, tau)
        oracle = geometric_inverse(a, b, length, stride, tau)
        need(dense_inverse(row) == oracle, "dense/geometric disagreement")
        identity = [ONE] + [ZERO] * (length - 1)
        need(convolution(row, oracle) == identity, "right inverse")
        need(convolution(oracle, row) == identity, "left inverse")
        a_bounds, b_bounds = sqrt_bounds(abs2(a)), sqrt_bounds(abs2(b))
        need(a_bounds[0] == a_bounds[1] and b_bounds[0] == b_bounds[1],
             "fixture radii must be rational")
        A, B = a_bounds[0], b_bounds[0]
        wiener2 = ((1 - A * B) / ((1 - A) * (1 - B))) ** 2
        wiener2 /= abs2(add(ONE, neg(mul(a, b))))
        norm_upper = sum(sqrt_bounds(abs2(value))[1] for value in oracle)
        need(norm_upper**2 <= wiener2, "cyclic norm exceeds exact Wiener norm")
        if a[1] == 0 and a[0] > 0 and b == neg(a):
            delta = 1 - a[0] ** 2
            cap = (1 + a[0]) ** 2 / (1 + a[0] ** 2)
            need(norm_upper * delta <= cap, "antipodal sharp bound")
            antipodal += 1
        count += 1
        entries += length
    return {"cases": count, "inverse_entries": entries, "antipodal_cases": antipodal}


def sharpness_checks() -> dict[str, object]:
    ratios = []
    for denominator in range(2, 65):
        r = F(denominator - 1, denominator)
        delta = 1 - r * r
        wiener = (1 + r) / ((1 - r) * (1 + r * r))
        ratio = delta * wiener
        need(ratio == (1 + r)**2 / (1 + r * r), "attainment formula")
        need(2 - ratio == (1 - r)**2 / (1 + r * r), "sharp limit identity")
        need((1 + r*r)**2 - 4*r*r == delta**2, "circle minimum identity")
        ratios.append(str(ratio))
    return {"cases": len(ratios), "last_ratio": ratios[-1]}


def controls() -> int:
    count = 0
    invalid = ((ONE, (F(1, 2), F(0))), (ZERO, ONE), (ZERO, ZERO))
    for a, b in invalid:
        try:
            contract(a, b)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid root pair accepted")
    a, b = (F(1, 2), F(0)), (F(-1, 2), F(0))
    row = kernel(a, b, 5, 1, ONE)
    result = geometric_inverse(a, b, 5, 1, ONE)
    need(result != geometric_inverse(a, neg(b), 5, 1, ONE), "wrong-sign control")
    need(convolution(row, list(reversed(result))) != [ONE] + [ZERO]*4,
         "wrong-direction control")
    need(geometric_inverse(a, b, 5, 1, PHASES[2]) != result, "gauge control")
    norm_lower = sum(sqrt_bounds(abs2(value))[0] for value in result)
    omitted_negative_norm = F(1, 2) / ((1 - F(1, 2)) * (1 + F(1, 4)))
    need(norm_lower > omitted_negative_norm, "missing-negative-frequency control")
    need(norm_lower * F(3, 4) > 1, "finite cyclic factor-one counterexample")
    return count + 5


def result() -> dict[str, object]:
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in names}
    return {"schema_version": 1, "claim_type": "scoped proof with finite corroboration",
            "circle_cases": circle_checks(), "cyclic": cyclic_checks(),
            "sharpness": sharpness_checks(), "controls": controls(),
            "source_sha256": hashes, "no_new_kappa": True}


def read_receipt(path: Path) -> object:
    need(path.stat().st_size <= 1 << 20, "receipt size limit")

    def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        need(len(pairs) <= 256, "receipt object size limit")
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate receipt key")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    parser.add_argument("--check-receipt", type=Path)
    args = parser.parse_args()
    payload = result()
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check_receipt:
        actual = read_receipt(args.check_receipt)
        need(json.dumps(actual, sort_keys=True) == json.dumps(payload, sort_keys=True),
             "receipt differs from recomputed result and source hashes")
    if args.emit_to:
        destination = args.emit_to.resolve()
        need(not destination.is_relative_to(HERE.parent.parent), "receipt must be outside checkout")
        with destination.open("x", encoding="utf-8") as output:
            need(output.write(serialized) == len(serialized), "short receipt write")
    print("PASS_MIXED_QUADRATIC_CIRCLE_BOUND", serialized.strip())


if __name__ == "__main__":
    main()
