#!/usr/bin/env python3
"""Exact finite evidence for the written cyclic inverse degree obstruction."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    require(0 < len(left) <= 3329 and 0 < len(right) <= 3329,
            "polynomial capacity")
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                out[i + j] += a * b
    return out


def rudin_shapiro(level):
    require(type(level) is int and 0 <= level <= 7, "level domain")
    r, t = [1], [1]
    for _ in range(level):
        r, t = r + t, r + [-value for value in t]
    require(len(r) == 2**level, "recurrence length")
    return r, t


def check_pair(r, t):
    require(len(r) == len(t) and len(r) <= 128, "pair capacity")
    m = len(r)
    require(all(value in (-1, 1) for value in r + t), "sign alphabet")
    for lag in range(m):
        value = sum(r[j] * r[j + lag] + t[j] * t[j + lag]
                    for j in range(m - lag))
        require(value == (2 * m if lag == 0 else 0), "flat pair identity")
    return m


def parameters(s):
    require(type(s) is int and 0 <= s <= 64, "parameter domain")
    m, denominator, q = 2 ** (2 * s + 1), 2 ** (s + 2), 2 * s + 6
    length = 2 * m * (q + 1)
    require(8 * m == denominator**2, "spectral contraction budget")
    require(16 * length < 4**q, "one-quarter tail budget")
    require(2 * s + 7 <= 7 * 2**s, "uniform tail majorant")
    return m, denominator, q, length


def partial_numerator(r, denominator, q, shift):
    require(0 <= shift <= 128 and 1 <= q <= 12, "partial-sum domain")
    numerator = [1]
    for j in range(1, q + 1):
        numerator = [0] * shift + multiply(r, numerator)
        numerator[0] += denominator**j
    return numerator


def check_family(s):
    require(type(s) is int and 0 <= s <= 3, "finite family domain")
    m, denominator, q, length = parameters(s)
    r, t = rudin_shapiro(2 * s + 1)
    require(check_pair(r, t) == m, "pair size")
    independent = [(-1) ** ((j & (j >> 1)).bit_count()) for j in range(m)]
    require(r == independent, "independent binary coefficient formula")
    numerator = partial_numerator(r, denominator, q, m)
    require(len(numerator) <= length, "partial-sum wraparound")
    scale = denominator**q
    require(numerator[0] == scale, "constant coefficient")
    require(numerator[m:2 * m] == [a * (scale // denominator) for a in r],
            "uncancelled first block")
    require(sum(abs(a) for a in numerator) >= scale * (1 + Fraction(m, denominator)),
            "partial-sum row-norm floor")
    polynomial = [denominator] + [0] * (m - 1) + [-a for a in r]
    residual = multiply(polynomial, numerator)
    power = [1]
    for _ in range(q + 1):
        power = [0] * m + multiply(power, r)
    require(len(residual) == len(power) and len(power) <= length,
            "residual capacity without wraparound")
    expected = [-a for a in power]
    expected[0] += denominator ** (q + 1)
    require(residual == expected, "complete Neumann residual identity")
    return {"s": s, "degree": 2 * m - 1, "length": length,
            "q": q, "denominator": denominator,
            "certified_gap": "1/2",
            "inverse_norm_strict_floor": str(Fraction(3, 4) + Fraction(m, denominator)),
            "partial_norm": str(Fraction(sum(abs(a) for a in numerator), scale)),
            "tail_squared_bound": str(Fraction(length, 4**q)),
            "residual_coefficients": len(residual)}


def solve_first_column(polynomial, length):
    require(1 <= length <= 28 and len(polynomial) <= 4, "dense oracle domain")
    rows = [[Fraction(polynomial[(i - j) % length])
             if (i - j) % length < len(polynomial) else Fraction(0)
             for j in range(length)] + [Fraction(i == 0)] for i in range(length)]
    for col in range(length):
        pivot = next((i for i in range(col, length) if rows[i][col]), None)
        require(pivot is not None, "dense singularity")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for i in range(length):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[col], strict=True)]
    return [row[-1] for row in rows]


def check_inverse(polynomial, inverse):
    length = len(inverse)
    require(1 <= length <= 28, "inverse capacity")
    product = [sum(a * inverse[(i - j) % length]
                   for j, a in enumerate(polynomial)) for i in range(length)]
    require(product == [1] + [0] * (length - 1), "literal cyclic inverse")


def expect_rejection(label, function, *args):
    try:
        function(*args)
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def finite_evidence():
    families = [check_family(s) for s in range(4)]
    for s in range(65):
        parameters(s)
    r, t = rudin_shapiro(1)
    polynomial = [Fraction(1), Fraction(0), Fraction(-1, 4), Fraction(-1, 4)]
    inverse = solve_first_column(polynomial, 28)
    check_inverse(polynomial, inverse)
    norm = sum(abs(a) for a in inverse)
    require(norm > Fraction(5, 4), "dense finite witness lower bound")
    bad_sign = list(inverse)
    bad_sign[0] = -bad_sign[0]
    controls = [
        expect_rejection("negative level", rudin_shapiro, -1),
        expect_rejection("Boolean parameter", parameters, True),
        expect_rejection("excessive family", check_family, 4),
        expect_rejection("broken flat pair", check_pair, [-1, 1], t),
        expect_rejection("wrong inverse sign", check_inverse, polynomial, bad_sign),
        expect_rejection("wrong shift direction", check_inverse, polynomial,
                         inverse[:1] + inverse[:0:-1]),
        expect_rejection("singular inverse", solve_first_column, [1, -1], 3),
    ]
    return {"families": families, "parameter_cases": 65,
            "dense_inverse_length": 28, "dense_inverse_norm": str(norm),
            "controls": controls}


def main():
    evidence = finite_evidence()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_CYCLIC_INVERSE_DEGREE_FLOOR",
                      "evidence": evidence, "package_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
