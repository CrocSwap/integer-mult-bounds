#!/usr/bin/env python3
"""Exact finite corroboration of the written sharp square-zero envelope.

Produced by Nick Petalas. Apache-2.0. Read-only, standard library only.
"""
from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from algebra import (add, determinant, identity, inverse, multiply, need,
                     norm_at_most, orthogonal, scale, shape, shear_error,
                     transpose, validate_error)

RATIOS = (F(1), F(6, 5), F(5, 4), F(4, 3), F(3, 2), F(5, 3), F(2), F(3))


def apply(a, vector):
    n = shape(a)
    need(len(vector) == n, "vector dimension")
    return tuple(sum((a[i][j] * vector[j] for j in range(n)), F(0))
                 for i in range(n))


def exact_norm_witness(a, bound, vector):
    need(any(vector), "zero witness")
    gram = multiply(transpose(a), a)
    need(apply(gram, vector) == tuple(bound * bound * x for x in vector),
         "sharp Gram eigenvector")
    need(norm_at_most(a, bound), "sharp norm upper bound")


def sqrt_interval(value):
    value = F(value)
    need(0 <= value <= 1000, "square-root interval domain")
    denominator = 1 << 128
    root = isqrt(value.numerator * denominator * denominator // value.denominator)
    low = F(root, denominator)
    high = low if low * low == value else low + F(1, denominator)
    need(low * low <= value <= high * high, "square-root enclosure")
    return low, high


def envelope_interval(total, length):
    need(type(length) is int and 1 <= length <= 32, "envelope length")
    total = F(total)
    need(0 <= total <= 100, "envelope budget")
    average = total / length
    low, high = sqrt_interval(average * average + 4)
    return ((low + average) / 2) ** length, ((high + average) / 2) ** length


def sharp_words():
    counts = {"words": 0, "prefixes": 0, "nonzero_words": 0,
              "strict_old_bounds": 0}
    for t in RATIOS:
        delta = t - 1 / t
        for n in (2, 3, 4):
            for length in range(1, 13):
                word = identity(n)
                for index in range(length):
                    error = shear_error(n, delta, lower=bool(index % 2))
                    validate_error(error, delta)
                    word = multiply(add(identity(n), error), word)
                    bound = t ** (index + 1)
                    vector = (F(1), t) + (F(0),) * (n - 2)
                    exact_norm_witness(word, bound, vector)
                    need(determinant(word) == 1, "word determinant")
                    inv = inverse(word)
                    need(norm_at_most(inv, bound), "inverse upper bound")
                    witness = (word[0][0] * -t + word[0][1],
                               word[1][0] * -t + word[1][1]) + (F(0),) * (n - 2)
                    exact_norm_witness(inv, bound, witness)
                    counts["prefixes"] += 1
                rho = length * delta
                low, high = envelope_interval(rho, length)
                need(low <= t ** length <= high, "fixed-budget equality enclosure")
                counts["words"] += 1
                if delta:
                    need(t ** length < (1 + delta) ** length, "strict predecessor improvement")
                    counts["nonzero_words"] += 1
                    counts["strict_old_bounds"] += 1
    return counts


def complex_error(delta, lower):
    # Realification of i*delta*E_01, or its real transpose.
    matrix = [[F(0) for _ in range(4)] for _ in range(4)]
    matrix[0][3], matrix[2][1] = -delta, delta
    result = tuple(tuple(row) for row in matrix)
    return transpose(result) if lower else result


def complex_unitary(mode):
    # Realification of one real orthogonal 2x2 matrix, on C^2.
    base = orthogonal(2, mode)
    result = tuple(tuple(base[i % 2][j % 2] if i // 2 == j // 2 else F(0)
                         for j in range(4)) for i in range(4))
    need(multiply(transpose(result), result) == identity(4), "complex unitary residual")
    return result


def varied_words():
    counts = {"words": 0, "prefixes": 0, "large_budget_words": 0,
              "complex_realification_fixtures": 0, "rank_two_error_factors": 0}
    for n in (2, 3, 4):
        for seed in range(8):
            for variant in range(4):
                word, bound, total = identity(n), F(1), F(0)
                length = 1 + seed % 6
                for index in range(length):
                    t = RATIOS[(seed + 3 * index + variant) % len(RATIOS)]
                    delta = t - 1 / t
                    rank_two = n == 4 and variant == 2
                    error = (complex_error(delta, bool(index % 2))
                             if n == 4 and variant == 3 else
                             shear_error(n, delta, bool(index % 2), rank_two))
                    mode = (index + variant) % 4
                    unitary = (complex_unitary(mode) if n == 4 and variant == 3
                               else orthogonal(n, mode))
                    error = multiply(multiply(unitary, error), transpose(unitary))
                    validate_error(error, delta)
                    counts["rank_two_error_factors"] += n == 4 and variant >= 2 and delta > 0
                    word = multiply(add(identity(n), error), word)
                    bound *= t
                    total += delta
                    need(norm_at_most(word, bound), "varied forward product")
                    need(norm_at_most(inverse(word), bound), "varied inverse product")
                    counts["prefixes"] += 1
                low, high = envelope_interval(total, length)
                need(bound <= high, "aggregate envelope interval")
                indices = [(seed + 3 * i + variant) % len(RATIOS) for i in range(length)]
                if len(set(indices)) > 1:
                    need(bound < low, "strict concavity for unequal budgets")
                counts["words"] += 1
                counts["large_budget_words"] += total >= 1
                counts["complex_realification_fixtures"] += n == 4 and variant == 3
    return counts


def smoothing_checks():
    pairs = 0
    for a in RATIOS:
        for b in RATIOS:
            da, db = a - 1 / a, b - 1 / b
            average, product = (da + db) / 2, a * b
            difference = average * average * product - (product - 1) ** 2
            need(difference >= 0, "independent two-slot smoothing inequality")
            need((difference == 0) == (a == b), "strict smoothing equality case")
            pairs += 1
    return pairs


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("missing rejection: " + message)


def controls():
    checks = 0
    for call, message in (
        (lambda: validate_error(((F(1), F(0)), (F(0), F(0))), 1), "non-square-zero"),
        (lambda: validate_error(((F(-1), F(0)), (F(0), F(0))), 1), "singular general error"),
        (lambda: validate_error(((0, 2), (0, 0)), 1), "insufficient budget"),
        (lambda: validate_error(((0, 0),), 1), "nonsquare"),
        (lambda: validate_error(((0.0, 1), (0, 0)), 1), "floating entries"),
        (lambda: validate_error(((0, 1 << 8193), (0, 0)), 1), "capacity"),
        (lambda: shear_error(1, 1), "one-dimensional attainment"),
        (lambda: envelope_interval(1, 0), "zero gate count"),
        (lambda: envelope_interval(-1, 2), "negative budget"),
        (lambda: inverse(((1, 1), (1, 1))), "singular inverse"),
    ):
        rejected(call, message)
        checks += 1
    delta, t = F(3, 2), F(2)
    upper = add(identity(2), shear_error(2, delta))
    lower = transpose(upper)
    need(not norm_at_most(upper, 1), "spectral-radius substitute must fail")
    need(not norm_at_most(upper, 1 + delta / 2), "linearized Phi is not an upper bound")
    need(not norm_at_most(multiply(lower, upper), t), "maximum is not total budget")
    need(multiply(lower, upper) != multiply(upper, lower), "ordered product control")
    same_direction = multiply(upper, upper)
    need(norm_at_most(same_direction, F(7, 2)), "same-direction control cap")
    need(not norm_at_most(multiply(lower, upper), F(7, 2)), "alignment changes growth")
    need(1 + delta > t, "infinity norm does not obey the Euclidean factor")
    rejected(lambda: need(F(1) < envelope_interval(0, 2)[1], "zero-budget equality"),
             "false strictness at zero")
    return checks + 7


def main():
    need(len(sys.argv) == 1, "this fixed verifier accepts no arguments")
    sharp = sharp_words()
    varied = varied_words()
    pairs = smoothing_checks()
    negative_controls = controls()
    here = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "algebra.py", "verify.py")
    result = {"status": "PASS_SHARP_SQUARE_ZERO_CONDITIONING", "claim_type": "scoped proof",
              "sharp": sharp, "varied": varied, "smoothing_pairs": pairs,
              "controls": negative_controls, "no_new_kappa": True,
              "source_sha256": {name: sha256((here / name).read_bytes()).hexdigest()
                                for name in files}}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
