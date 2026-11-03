#!/usr/bin/env python3
"""Exact corroboration of the new degree-bounded sampling formulas."""

import hashlib
import itertools
import json
import math
import platform
from fractions import Fraction
from pathlib import Path


MAX_Q = 16
MAX_N = 32
MAX_FILE_BYTES = 262144
SOURCE = "research/polynomial-cost-distribution/PROOF.md"
SOURCE_SHA256 = "946370455b5f64cfa1cee22eca97c19102aca3ef07f5da7f98eb1bf419bdbf9e"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(q, n):
    require(type(q) is int and 2 <= q <= MAX_Q, "q outside finite check domain")
    require(type(n) is int and 0 <= n <= MAX_N, "N outside finite check domain")


def source_mixture(q, n):
    """Use the cited joint count, divided by the common free-group factor."""
    domain(q, n)
    counts = [1] + [0] * n
    for degree in range(1, n + 1):
        for cost in range(1, degree + 1):
            counts[cost] += ((q + 1) * (q - 1) ** cost * q ** (degree - 1)
                             * math.comb(degree - 1, cost - 1))
    return tuple(counts)


def geometric_counts(q, n):
    """Coefficients of 1+(q^2-1)z sum_{j<N}(q+q(q-1)z)^j."""
    domain(q, n)
    result = [1] + [0] * n
    power = [1]
    for _ in range(n):
        for cost, coefficient in enumerate(power):
            result[cost + 1] += (q * q - 1) * coefficient
        following = [0] * (len(power) + 1)
        for cost, coefficient in enumerate(power):
            following[cost] += q * coefficient
            following[cost + 1] += q * (q - 1) * coefficient
        power = following
    return tuple(result)


def measured_moments(counts):
    total = sum(counts)
    require(total > 0, "empty measure")
    mean = Fraction(sum(k * count for k, count in enumerate(counts)), total)
    second = Fraction(sum(k * k * count for k, count in enumerate(counts)), total)
    return mean, second - mean * mean


def closed_moments(q, n):
    domain(q, n)
    epsilon = Fraction(1, q ** (2 * n))
    mean = Fraction((q - 1) * n, q) + (1 - epsilon) / (q + 1)
    variance = (Fraction((q - 1) * n, q * q)
                + Fraction(2 * (q - 1) * n, q * (q + 1)) * epsilon
                - (1 - epsilon) * (q - epsilon) / (q + 1) ** 2)
    return mean, variance


def evaluate(coefficients, value):
    result = Fraction(0)
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def quotient_value(q, n, value):
    base = q + q * (q - 1) * value
    geometric = n if base == 1 else (base ** n - 1) / (base - 1)
    return (1 + (q * q - 1) * value * geometric) / q ** (2 * n)


def verify_formulas():
    cases = 0
    evaluations = 0
    rows = []
    for q, n in itertools.product(range(2, MAX_Q + 1), range(MAX_N + 1)):
        counts = source_mixture(q, n)
        require(counts == geometric_counts(q, n), "PGF coefficient mismatch")
        require(sum(counts) == q ** (2 * n), "wrong bounded-degree normalization")
        require(measured_moments(counts) == closed_moments(q, n), "moment mismatch")
        require(closed_moments(q, n)[1] >= 0, "negative variance")
        for value in (Fraction(0), Fraction(1), Fraction(-1, q), Fraction(2, 3)):
            actual = evaluate(counts, value) / q ** (2 * n)
            require(actual == quotient_value(q, n, value), "quotient mismatch")
            evaluations += 1
        if n:
            exact_degree_mean = 1 + Fraction((n - 1) * (q - 1), q)
            reduction = Fraction(1, q * (q + 1)) + Fraction(1, (q + 1) * q ** (2 * n))
            require(exact_degree_mean - closed_moments(q, n)[0] == reduction,
                    "sampling-measure mean gap mismatch")
        rows.append((q, n, counts))
        cases += 1
    digest = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    return {"parameter_cases": cases, "pgf_evaluations": evaluations, "counts_sha256": digest}


def verify_digit_space():
    """Enumerate the new mixture via weighted digit strings, not matrices."""
    strings = 0
    cases = 0
    for q, n in itertools.product(range(2, 6), range(7)):
        counts = [1] + [0] * n
        for degree in range(1, n + 1):
            weight = (q * q - 1) * q ** (degree - 1)
            for digits in itertools.product(range(q), repeat=degree - 1):
                cost = 1 + sum(digit != 0 for digit in digits)
                counts[cost] += weight
                strings += 1
        require(tuple(counts) == geometric_counts(q, n), "digit-space mismatch")
        cases += 1
    return {"digit_space_cases": cases, "weighted_digit_strings": strings}


def verify_controls():
    rejected = 0
    for q, n in ((1, 0), (17, 0), (2, -1), (2, 33), (True, 0), (2, False)):
        try:
            source_mixture(q, n)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid domain accepted")
    counts = geometric_counts(2, 1)
    require(counts == (1, 3), "degree-zero boundary changed")
    require(measured_moments(counts) == (Fraction(3, 4), Fraction(3, 16)),
            "degree-one bounded measure changed")
    require(closed_moments(2, 0) == (0, 0), "constant targets have nonzero cost")
    controls = ((measured_moments((0, 3)), closed_moments(2, 1)),
                ((Fraction(1), Fraction(0)), closed_moments(2, 1)),
                ((Fraction(5, 6), Fraction(3, 16)), closed_moments(2, 1)),
                ((Fraction(3, 4), Fraction(1, 4)), closed_moments(2, 1)))
    for counterfeit, actual in controls:
        require(counterfeit != actual, "incorrect sampling formula escaped control")
        rejected += 1
    return {"rejected_controls": rejected, "boundary_fixtures": 3}


def bounded_hash(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    require(len(data) <= MAX_FILE_BYTES, "source file exceeds byte bound")
    return hashlib.sha256(data).hexdigest()


def main():
    package = Path(__file__).resolve().parent
    source_hash = bounded_hash(package.parents[1] / SOURCE)
    require(source_hash == SOURCE_SHA256, "cited proof bytes changed")
    evidence = verify_formulas() | verify_digit_space() | verify_controls()
    example = geometric_counts(2, 4)
    mean, variance = measured_moments(example)
    receipt = {
        "status": "PASS_DEGREE_BOUNDED_POLYNOMIAL_COST",
        "claim_type": "scoped counting proof with exact finite corroboration",
        "python": platform.python_version(),
        "evidence": evidence,
        "binary_degree_four_example": {
            "counts_divided_by_GL2": example,
            "mean": str(mean), "variance": str(variance),
        },
        "sha256": {name: bounded_hash(package / name) for name in FILES} | {SOURCE: source_hash},
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_DEGREE_BOUNDED_POLYNOMIAL_COST no_new_kappa")


if __name__ == "__main__":
    main()
