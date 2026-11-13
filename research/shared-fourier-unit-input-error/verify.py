#!/usr/bin/env python3
"""Exact finite corroboration of the unit-input Fourier norm reduction."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import isqrt, prod
from pathlib import Path
import json


# Basis: 1, sqrt(2), sqrt(3), sqrt(6), i, i sqrt(2), i sqrt(3), i sqrt(6).
Number = tuple[Fraction, ...]
Group = tuple[tuple[int, ...], ...]


def number(value: int | Fraction, basis: int = 0) -> Number:
    if not 0 <= basis < 8:
        raise ValueError("field basis")
    return tuple(Fraction(value) if j == basis else Fraction(0) for j in range(8))


ZERO = number(0)
ONE = number(1)
ROOT2 = number(1, 1)
ROOT3 = number(1, 2)
I = number(1, 4)
ROOTS = (ONE, I, number(-1), number(-1, 4))


def add(a: Number, b: Number) -> Number:
    return tuple(a[j] + b[j] for j in range(8))


def scale(a: Number, factor: int | Fraction) -> Number:
    return tuple(x * factor for x in a)


def multiply(a: Number, b: Number) -> Number:
    out = [Fraction(0) for _ in range(8)]
    for j, x in enumerate(a):
        if x:
            for k, y in enumerate(b):
                if y:
                    common = j & k
                    factor = (2 if common & 1 else 1)
                    factor *= 3 if common & 2 else 1
                    factor *= -1 if common & 4 else 1
                    out[j ^ k] += factor * x * y
    return tuple(out)


def conjugate(a: Number) -> Number:
    return tuple(x if j < 4 else -x for j, x in enumerate(a))


def real_part(a: Number) -> Number:
    return a[:4] + (Fraction(0),) * 4


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sign(a: Number) -> int:
    require(not any(a[4:]), "non-real comparison")
    if a == ZERO:
        return 0
    for bits in (32, 64, 128, 256):
        unit = 1 << bits
        s2, s3 = isqrt(2 * unit * unit), isqrt(3 * unit * unit)
        lower = (Fraction(1), Fraction(s2, unit), Fraction(s3, unit),
                 Fraction(s2 * s3, unit * unit))
        upper = (Fraction(1), Fraction(s2 + 1, unit), Fraction(s3 + 1, unit),
                 Fraction((s2 + 1) * (s3 + 1), unit * unit))
        lo = sum(a[j] * (lower[j] if a[j] >= 0 else upper[j]) for j in range(4))
        hi = sum(a[j] * (upper[j] if a[j] >= 0 else lower[j]) for j in range(4))
        if lo > 0:
            return 1
        if hi < 0:
            return -1
    raise RuntimeError("comparison precision exhausted")


def norm_squared(vector: tuple[Number, ...]) -> Number:
    total = ZERO
    for value in vector:
        total = add(total, multiply(conjugate(value), value))
    require(not any(total[4:]), "non-real squared norm")
    return total


def make_group(moduli: tuple[int, ...]) -> Group:
    if not 1 <= len(moduli) <= 4 or any(type(q) is not int or q not in (2, 4)
                                      for q in moduli) or prod(moduli) > 16:
        raise ValueError("finite checker group domain")
    return tuple(product(*(range(q) for q in moduli)))


def character(moduli: tuple[int, ...], x: tuple[int, ...],
              y: tuple[int, ...]) -> Number:
    turns = sum(x[j] * y[j] * (4 // q) for j, q in enumerate(moduli)) % 4
    return ROOTS[turns]


def validate(moduli: tuple[int, ...], b: tuple[int, ...],
             weights: tuple[Number, ...]) -> Group:
    group = make_group(moduli)
    if b not in group or not any(b) or any(2 * b[j] % q for j, q in enumerate(moduli)):
        raise ValueError("nonzero order-two translation required")
    if len(weights) != len(group):
        raise ValueError("phase length")
    if any(len(w) != 8 or multiply(conjugate(w), w) != ONE for w in weights):
        raise ValueError("unit phase required")
    return group


def fourier(moduli: tuple[int, ...], vector: tuple[Number, ...],
            direction: int) -> tuple[Number, ...]:
    group = make_group(moduli)
    require(len(vector) == len(group) and direction in (-1, 1), "Fourier domain")
    out = []
    for x in group:
        total = ZERO
        for y, value in zip(group, vector, strict=True):
            phase = character(moduli, x, y)
            total = add(total, multiply(value, phase if direction == 1 else conjugate(phase)))
        out.append(scale(total, Fraction(1, len(group))))
    return tuple(out)


def shift(moduli: tuple[int, ...], b: tuple[int, ...],
          vector: tuple[Number, ...]) -> tuple[Number, ...]:
    group = make_group(moduli)
    positions = {x: j for j, x in enumerate(group)}
    return tuple(vector[positions[tuple((x[j] + b[j]) % q
                                       for j, q in enumerate(moduli))]] for x in group)


def literal(moduli: tuple[int, ...], b: tuple[int, ...], weights: tuple[Number, ...],
            u: tuple[Number, ...], v: tuple[Number, ...], mutation: int = 0
            ) -> tuple[Number, ...]:
    require(mutation in (0, 1, 2, 3), "literal mutation domain")
    left = shift(moduli, b, fourier(moduli, u, -1))
    right = shift(moduli, b, fourier(moduli, v, -1))
    middle = tuple(multiply(multiply(w, x), multiply(w, y))
                   for w, x, y in zip(weights, left, right, strict=True))
    final = fourier(moduli, middle, 1)
    if mutation != 2:
        final = shift(moduli, b, final)
    out = tuple(multiply(w if mutation == 1 else conjugate(w), x)
                for w, x in zip(weights, final, strict=True))
    return tuple(scale(x, len(weights)) for x in out) if mutation == 3 else out


def desired(moduli: tuple[int, ...], u: tuple[Number, ...],
            v: tuple[Number, ...]) -> tuple[Number, ...]:
    group = make_group(moduli)
    positions = {x: j for j, x in enumerate(group)}
    out = [ZERO for _ in group]
    for s, x in zip(group, u, strict=True):
        for t, y in zip(group, v, strict=True):
            k = tuple((s[j] + t[j]) % q for j, q in enumerate(moduli))
            index = positions[k]
            out[index] = add(out[index], multiply(x, y))
    return tuple(scale(x, Fraction(1, len(group) ** 2)) for x in out)


def unit_character(moduli: tuple[int, ...], z: tuple[int, ...]) -> tuple[Number, ...]:
    group = make_group(moduli)
    exponent = len(group).bit_length() - 1
    if exponent % 2:
        factor = scale(ROOT2, Fraction(1, 2 ** ((exponent + 1) // 2)))
    else:
        factor = number(Fraction(1, 2 ** (exponent // 2)))
    out = tuple(multiply(factor, character(moduli, x, z)) for x in group)
    require(norm_squared(out) == ONE, "unit character normalization")
    return out


def column_errors(moduli: tuple[int, ...], b: tuple[int, ...],
                  weights: tuple[Number, ...]) -> tuple[Number, ...]:
    group = validate(moduli, b, weights)
    moment = ZERO
    for x, w in zip(group, weights, strict=True):
        moment = add(moment, multiply(character(moduli, b, x), w))
    moment = scale(moment, Fraction(1, len(group)))
    out = []
    for y, w in zip(group, weights, strict=True):
        phase = multiply(character(moduli, b, y), multiply(w, w))
        cross = real_part(multiply(conjugate(moment), phase))
        out.append(add(number(2), scale(cross, -2)))
    return tuple(out)


def error_squared(actual: tuple[Number, ...], expected: tuple[Number, ...]) -> Number:
    return norm_squared(tuple(add(x, scale(y, -1))
                              for x, y in zip(actual, expected, strict=True)))


def check_columns(moduli: tuple[int, ...], b: tuple[int, ...],
                  weights: tuple[Number, ...], counts: dict[str, int]) -> None:
    group = validate(moduli, b, weights)
    errors = column_errors(moduli, b, weights)
    for y, predicted in zip(group, errors, strict=True):
        z = tuple((y[j] + b[j]) % q for j, q in enumerate(moduli))
        u = unit_character(moduli, z)
        expected = desired(moduli, u, u)
        require(norm_squared(expected) == number(Fraction(1, len(group) ** 3)),
                "desired bilinear norm attainment")
        actual = literal(moduli, b, weights, u, u)
        require(scale(error_squared(actual, expected), len(group) ** 3) == predicted,
                "literal character / column norm disagreement")
        counts["character_pairs"] += 1
    counts["phase_assignments"] += 1


def minimizer(moduli: tuple[int, ...], b: tuple[int, ...]) -> tuple[Number, ...]:
    h, imaginary_r = scale(ROOT3, Fraction(1, 3)), number(Fraction(1, 3), 7)
    return tuple(add(h, scale(multiply(character(moduli, b, x), imaginary_r), -1))
                 for x in make_group(moduli))


SHARP_SQUARED = add(number(2), scale(ROOT3, Fraction(-8, 9)))


def check_dense(moduli: tuple[int, ...], b: tuple[int, ...], weights: tuple[Number, ...],
                counts: dict[str, int]) -> None:
    group = make_group(moduli)
    first, second = unit_character(moduli, group[0]), unit_character(moduli, group[-1])
    real_mix = tuple(add(scale(x, Fraction(3, 5)), scale(y, Fraction(4, 5)))
                     for x, y in zip(first, second, strict=True))
    complex_mix = tuple(add(scale(x, Fraction(5, 13)),
                            scale(multiply(I, y), Fraction(12, 13)))
                        for x, y in zip(first, second, strict=True))
    for u, v in ((first, second), (real_mix, real_mix),
                 (complex_mix, real_mix), (complex_mix, complex_mix)):
        require(norm_squared(u) == ONE and norm_squared(v) == ONE, "dense input norm")
        observed = scale(error_squared(literal(moduli, b, weights, u, v),
                                        desired(moduli, u, v)), len(group) ** 3)
        require(sign(add(SHARP_SQUARED, scale(observed, -1))) >= 0,
                "dense pair exceeds proved norm")
        counts["dense_pairs"] += 1


def finite_census() -> dict[str, int]:
    counts = dict(phase_assignments=0, character_pairs=0, minimizer_fixtures=0,
                  dense_pairs=0, controls=0)
    for moduli in ((2,), (4,), (2, 2)):
        group = make_group(moduli)
        for b in group[1:]:
            if all(2 * b[j] % q == 0 for j, q in enumerate(moduli)):
                for entries in product(range(4), repeat=len(group)):
                    weights = tuple(ROOTS[j] for j in entries)
                    check_columns(moduli, b, weights, counts)
    for moduli in ((2,), (4,), (2, 2), (2, 2, 2), (4, 2), (4, 4)):
        for b in make_group(moduli)[1:]:
            if all(2 * b[j] % q == 0 for j, q in enumerate(moduli)):
                weights = minimizer(moduli, b)
                check_columns(moduli, b, weights, counts)
                require(all(x == SHARP_SQUARED for x in column_errors(moduli, b, weights)),
                        "minimizer column flatness")
                check_dense(moduli, b, weights, counts)
                counts["minimizer_fixtures"] += 1
    return counts


def controls(counts: dict[str, int]) -> dict[str, str]:
    moduli, b = (2, 2), (1, 0)
    weights = minimizer(moduli, b)
    u = unit_character(moduli, (0, 0))
    target = desired(moduli, u, u)
    for mutation in (1, 2, 3):
        observed = scale(error_squared(literal(moduli, b, weights, u, u, mutation), target), 64)
        require(observed != SHARP_SQUARED, "semantic mutation survived")
        counts["controls"] += 1
    uneven = column_errors(moduli, b, (ONE, ONE, ONE, I))
    maximum = max(x[0] for x in uneven)
    mean = sum(x[0] for x in uneven) / len(uneven)
    require(all(not any(x[1:]) for x in uneven) and maximum > mean,
            "maximum must differ from mean for the control")
    counts["controls"] += 1
    cases = (((3,), (1,), (ONE,) * 3, "finite checker group domain"),
             ((2,) * 5, (1,) * 5, (ONE,) * 32, "finite checker group domain"),
             ((2,), (0,), (ONE, ONE), "nonzero order-two translation required"),
             ((4,), (1,), (ONE,) * 4, "nonzero order-two translation required"),
             ((2,), (1,), (ONE,), "phase length"),
             ((2,), (1,), (ONE, number(2)), "unit phase required"))
    for shape, translation, phases, reason in cases:
        try:
            validate(shape, translation, phases)
        except ValueError as error:
            require(str(error) == reason, "wrong rejection reason")
            counts["controls"] += 1
        else:
            raise RuntimeError("invalid fixture accepted")
    return {"squared_coefficient_error": str(mean), "squared_unit_input_error": str(maximum)}


def main() -> None:
    require(multiply(ROOT2, ROOT2) == number(2), "sqrt2 arithmetic")
    require(multiply(ROOT3, ROOT3) == number(3), "sqrt3 arithmetic")
    require(multiply(I, I) == number(-1), "imaginary arithmetic")
    counts = finite_census()
    discrimination = controls(counts)
    paths = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in paths:
        with (Path(__file__).resolve().parent / name).open("rb") as handle:
            data = handle.read(262145)
        require(len(data) <= 262144, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    print(json.dumps({"marker": "PASS_SHARED_FOURIER_UNIT_INPUT_ERROR", "counts": counts,
                      "sharp_relative_error_squared": [str(x) for x in SHARP_SQUARED],
                      "mean_vs_max_control": discrimination,
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
