#!/usr/bin/env python3
"""Exact finite evidence for the optimal 66-grade sign extraction wrapper."""

import json
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

MAX_GRADES = 68
MAX_COORDINATES = 102
MAX_BITS = 512


def require(condition, message):
    if not condition:
        raise ValueError(message)


def paley():
    """Classical Paley matrix at the fixed prime 67, including its border."""
    squares = {x * x % 67 for x in range(1, 67)}
    result = [[1] * 68]
    for row in range(67):
        core = [-1 if row == col else
                (1 if (row - col) % 67 in squares else -1)
                for col in range(67)]
        result.append([1] + core)
    return tuple(tuple(row) for row in result)


def check_signs(signs, grades):
    require(type(grades) is int and 1 <= grades <= MAX_GRADES,
            "grade capacity")
    require(type(signs) is tuple and 1 <= len(signs) <= 128,
            "execution capacity")
    require(all(type(row) is tuple and len(row) == grades for row in signs),
            "rectangular sign array")
    require(all(type(x) is int and x in (-1, 1) for row in signs for x in row),
            "literal signs")
    for a in range(grades):
        for b in range(a + 1):
            dot = sum(row[a] * row[b] for row in signs)
            require(dot == (len(signs) if a == b else 0),
                    "nonorthogonal grade columns")


def divide_by_17(value):
    """Signed exact binary long division, with a bounded 17-state remainder."""
    require(type(value) is int and abs(value).bit_length() <= MAX_BITS,
            "integer capacity")
    negative = value < 0
    magnitude = abs(value)
    quotient = remainder = 0
    for position in range(magnitude.bit_length() - 1, -1, -1):
        remainder = 2 * remainder + ((magnitude >> position) & 1)
        bit = int(remainder >= 17)
        remainder -= 17 * bit
        quotient = 2 * quotient + bit
        require(0 <= remainder < 17, "division remainder state")
    require(remainder == 0, "inexact odd division")
    result = -quotient if negative else quotient
    require(17 * result == value, "division postcondition")
    return result


def average_accumulator(value, runs):
    require(runs == 68, "this exact divider is for the 68-run wrapper")
    require(type(value) is int and value % 4 == 0, "inexact binary shift")
    return divide_by_17(value // 4)


def literal_wrapper(matrix, vector, labels, signs):
    """Execute each signed dense integer matrix-vector call before averaging."""
    n = len(vector)
    require(1 <= n <= MAX_COORDINATES and len(labels) == n, "coordinate cap")
    require(len(matrix) == n and all(len(row) == n for row in matrix),
            "square operator")
    require(all(type(x) is int for row in matrix for x in row),
            "integer common-grid operator")
    require(all(type(x) is int for x in vector), "integer common-grid input")
    require(all(type(h) is int and 0 <= h < len(signs[0]) for h in labels),
            "grade labels")
    accum = [0] * n
    for pattern in signs:
        signed_input = [pattern[labels[i]] * vector[i] for i in range(n)]
        output = [sum(a * b for a, b in zip(row, signed_input, strict=True))
                  for row in matrix]
        for i in range(n):
            accum[i] += pattern[labels[i]] * output[i]
    return tuple(average_accumulator(x, len(signs)) for x in accum)


def diagonal_reference(matrix, vector, labels):
    return tuple(sum(matrix[i][j] * vector[j] for j in range(len(vector))
                     if labels[i] == labels[j]) for i in range(len(vector)))


def fixtures(signs):
    cases = components = 0
    digest = sha256()
    for grades in (1, 3, 17, 65, 66, 67, 68):
        labels = tuple(h for h in range(grades) for _ in range(1 + h % 2))
        n = len(labels)
        patterns = tuple(tuple(row[:grades]) for row in signs)
        check_signs(patterns, grades)
        for triangular in (False, True):
            for component in (0, 1):
                matrix = tuple(tuple(
                    0 if triangular and labels[i] < labels[j] else
                    ((37 * i + 19 * j + 7 * component + i * j) % 23 - 11)
                    for j in range(n)) for i in range(n))
                vector = tuple((i * i + 3 * i + component) % 13 - 6
                               for i in range(n))
                actual = literal_wrapper(matrix, vector, labels, patterns)
                expected = diagonal_reference(matrix, vector, labels)
                require(actual == expected, "literal block extraction")
                digest.update(repr((grades, triangular, component, actual)).encode())
                cases += 1
                components += n
    return cases, components, digest.hexdigest()


def fractional_fixture(signs):
    """Compare rational averaging with integrated common-grid integer recovery."""
    labels = (0, 1, 1, 2, 2, 2)
    vector = tuple(Fraction(i - 3, 2 ** (i % 3)) for i in range(6))
    matrix = tuple(tuple(Fraction(3 * i - 2 * j + 1, 2 ** ((i + j) % 4))
                         for j in range(6)) for i in range(6))
    accumulated = [Fraction(0)] * 6
    for row in signs:
        incoming = tuple(row[labels[j]] * vector[j] for j in range(6))
        for i in range(6):
            accumulated[i] += row[labels[i]] * sum(
                matrix[i][j] * incoming[j] for j in range(6))
    expected = diagonal_reference(matrix, vector, labels)
    actual = tuple(value / 68 for value in accumulated)
    require(actual == expected, "independent fractional execution")
    scaled = tuple(value * 32 for value in accumulated)
    require(all(value.denominator == 1 for value in scaled),
            "one common exact accumulator grid")
    recovered = tuple(Fraction(average_accumulator(value.numerator, 68), 32)
                      for value in scaled)
    require(recovered == expected, "common-grid integer division recovery")
    require(all(value.denominator & (value.denominator - 1) == 0
                for value in actual), "no residual odd denominator")
    return len(actual)


def rejection_controls(signs):
    rejected = 0
    bad = [list(row[:66]) for row in signs]
    bad[0][0] *= -1
    duplicate = tuple(tuple(row[:65]) + (row[0],) for row in signs)
    candidates = (
        (tuple(tuple(row) for row in bad), 66),
        (tuple(tuple(row[:66]) for row in signs[:-1]), 66),
        (duplicate, 66),
        (tuple(tuple(row[:66]) for row in signs), 0),
        (((True,),), 1),
    )
    for candidate, grades in candidates:
        try:
            check_signs(candidate, grades)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("sign control was accepted")
    for value in (1, -1, 18, 1 << (MAX_BITS + 1), True):
        try:
            divide_by_17(value)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("division control was accepted")
    try:
        average_accumulator(17, 68)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("inexact shift accepted")
    return rejected


def main():
    signs = paley()
    check_signs(signs, 68)
    cases, components, digest = fixtures(signs)
    divisions = 0
    for quotient in range(-4096, 4097):
        require(divide_by_17(17 * quotient) == quotient, "signed exact division")
        divisions += 1
    for bits in (64, 127, 255, 500):
        for sign in (-1, 1):
            quotient = sign * ((1 << bits) - 1)
            require(divide_by_17(17 * quotient) == quotient, "wide exact division")
            divisions += 1
    # Rank plus the elementary three-column divisibility obstruction.
    candidates = tuple(k for k in range(66, 69) if k % 4 == 0)
    require(candidates == (68,), "minimum eligible execution count")
    report = {
        "status": "PASS_GRADE_SIGN_EXTRACTION",
        "grades": 66, "runs": 68, "previous_walsh_runs": 128,
        "paley_gram_entries": 68 * 69 // 2,
        "literal_cases": cases, "output_components": components,
        "fractional_output_components": fractional_fixture(signs),
        "signed_exact_divisions": divisions,
        "rejection_controls": rejection_controls(signs),
        "fixture_sha256": digest,
        "sign_array_sha256": sha256(repr(signs).encode()).hexdigest(),
        "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
