#!/usr/bin/env python3
"""Exact corroboration of the sharp Gaussian minor range. Apache-2.0."""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform


MAX_BAND = 12
MAX_SIZE = 7
NEGATIVE_LIMIT = 512
PARAMETERS = (Fraction(2, 5), Fraction(9, 20), Fraction(1, 2))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def kernel(size, band, parameter):
    if type(size) is not int or not 1 <= size <= MAX_SIZE:
        raise ValueError("size outside finite replay domain")
    if type(band) is not int or not 1 <= band <= MAX_BAND:
        raise ValueError("band outside finite replay domain")
    if not isinstance(parameter, Fraction) or not 0 < parameter < 1:
        raise ValueError("parameter outside finite replay domain")
    return [[parameter ** ((i - j) ** 2) if abs(i - j) <= band else Fraction(0)
             for j in range(size)] for i in range(size)]


def integer_kernel(size, band, parameter):
    """Scale every entry by denominator**band**2 before Bareiss elimination."""
    matrix = kernel(size, band, parameter)
    scale = parameter.denominator ** (band * band)
    integer = []
    for row in matrix:
        converted = [entry * scale for entry in row]
        require(all(entry.denominator == 1 for entry in converted), "integer scaling")
        integer.append([entry.numerator for entry in converted])
    return integer, scale


def determinant(matrix):
    """Integer Bareiss determinant, including row swaps and singular minors."""
    size = len(matrix)
    require(size <= MAX_SIZE and all(len(row) == size for row in matrix), "minor shape")
    if size == 0:
        return 1
    work = [row[:] for row in matrix]
    previous, sign = 1, 1
    for column in range(size - 1):
        pivot_row = next((i for i in range(column, size) if work[i][column]), None)
        if pivot_row is None:
            return 0
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            sign = -sign
        pivot = work[column][column]
        for i in range(column + 1, size):
            for j in range(column + 1, size):
                value = work[i][j] * pivot - work[i][column] * work[column][j]
                quotient, remainder = divmod(value, previous)
                require(remainder == 0, "Bareiss exact division")
                work[i][j] = quotient
            work[i][column] = 0
        previous = pivot
    return sign * work[-1][-1]


def submatrix(matrix, rows, columns):
    return [[matrix[i][j] for j in columns] for i in rows]


def check_minor(matrix, rows, columns, band):
    value = determinant(submatrix(matrix, rows, columns))
    permitted = all(abs(i - j) <= band for i, j in zip(rows, columns, strict=True))
    require(value > 0 if permitted else value == 0, "ordered minor criterion")
    return "positive" if permitted else "zero"


def polynomial_checks():
    positive, double_root, paired_tails = 0, 0, 0
    for parameter in PARAMETERS:
        for length in range(2 * MAX_BAND + 1):
            tail = sum(((-1) ** r * parameter ** (r * r)
                        for r in range(1, length + 1)), Fraction(0))
            require(tail >= -parameter, "alternating tail lower bound")
            if length >= 2:
                require(tail > -parameter, "strict paired tail")
            paired_tails += 1
        for band in range(1, MAX_BAND + 1):
            for j in range(-band, band + 1):
                z = -(parameter ** (-2 * j))
                value = sum((parameter ** (h * h) * z ** (h + band)
                             for h in range(-band, band + 1)), Fraction(0))
                normalized = value / ((-1) ** (j + band)
                                         * parameter ** (-j * j - 2 * j * band))
                if parameter == Fraction(1, 2) and band == 1 and j == 0:
                    require(normalized == 0, "exceptional endpoint evaluation")
                    double_root += 1
                else:
                    require(normalized > 0, "strict polynomial sign")
                    positive += 1
    coefficients = [Fraction(1, 2) ** (h * h) for h in (-1, 0, 1)]
    require(coefficients == [Fraction(v, 2) for v in (1, 2, 1)], "endpoint factorization")
    return {"positive_evaluations": positive, "double_root_evaluations": double_root,
            "alternating_tails": paired_tails}


def minor_checks():
    counts = {"positive": 0, "zero": 0}
    for parameter in PARAMETERS:
        for band in range(1, 4):
            matrix, _ = integer_kernel(6, band, parameter)
            for order in range(1, 7):
                subsets = tuple(combinations(range(6), order))
                for rows in subsets:
                    for columns in subsets:
                        counts[check_minor(matrix, rows, columns, band)] += 1
    return counts


def schur(matrix, eliminated):
    """Literal successive rational pivot updates; no determinant formula."""
    work = [row[:] for row in matrix]
    active = list(range(len(work)))
    for pivot in eliminated:
        diagonal = work[pivot][pivot]
        require(diagonal > 0, "positive chronological pivot")
        remaining = [i for i in active if i != pivot]
        for i in remaining:
            for j in remaining:
                work[i][j] -= work[i][pivot] * work[pivot][j] / diagonal
        active = remaining
    return work, active


def expected_entry(i, j, eliminated, band):
    if i == j:
        return 1
    lower, upper = sorted((i, j))
    inside = [e for e in eliminated if lower < e < upper]
    chain = [lower, *inside, upper]
    if any(y - x > band for x, y in zip(chain, chain[1:])):
        return 0
    return (-1) ** len(inside)


def schur_checks():
    counts = {"layouts": 0, "positive": 0, "negative": 0, "zero": 0,
              "determinant_ratios": 0}
    for parameter in PARAMETERS:
        for band in range(1, 4):
            for size in range(1, MAX_SIZE + 1):
                matrix = kernel(size, band, parameter)
                integers, scale = integer_kernel(size, band, parameter)
                for mask in range((1 << size) - 1):
                    eliminated = [i for i in range(size) if mask & (1 << i)]
                    result, survivors = schur(matrix, eliminated)
                    denominator = determinant(submatrix(integers, eliminated, eliminated))
                    require(denominator > 0, "positive full principal pivot")
                    counts["layouts"] += 1
                    for i in survivors:
                        for j in survivors:
                            value = result[i][j]
                            actual = (value > 0) - (value < 0)
                            require(actual == expected_entry(i, j, eliminated, band), "Schur sign")
                            rows, columns = [*eliminated, i], [*eliminated, j]
                            numerator = determinant(submatrix(integers, rows, columns))
                            require(value == Fraction(numerator, denominator * scale), "Schur ratio")
                            counts["determinant_ratios"] += 1
                            counts[{1: "positive", -1: "negative", 0: "zero"}[actual]] += 1
    return counts


def first_failed_principal(parameter):
    require(Fraction(1, 2) < parameter < 1, "counterexample parameter")
    previous, current = Fraction(1), Fraction(1)
    for size in range(2, NEGATIVE_LIMIT + 1):
        previous, current = current, current - parameter * parameter * previous
        if current <= 0:
            require(previous > 0, "first failed pivot has positive predecessor")
            return size, current
    raise AssertionError("finite counterexample search limit exhausted")


def obstruction_checks():
    witnesses = []
    for text in ("3/5", "2/3", "51/100", "101/200", "501/1000", "5001/10000"):
        parameter = Fraction(text)
        size, value = first_failed_principal(parameter)
        require(value < 0, "strict negative witness")
        # An independent integer recurrence clears the rational denominator.
        numerator, denominator = parameter.numerator, parameter.denominator
        previous, current = 1, denominator
        for order in range(2, size + 1):
            previous, current = current, denominator * current - numerator * numerator * previous
            if order < size:
                require(current > 0, "integer positive prefix")
        require(Fraction(current, denominator ** size) == value, "independent recurrence")
        witnesses.append({"t": text, "first_negative_order": size,
                          "determinant_numerator": str(value.numerator),
                          "determinant_denominator": str(value.denominator)})
    previous, current = Fraction(1), Fraction(1)
    for size in range(2, NEGATIVE_LIMIT + 1):
        previous, current = current, current - previous / 4
        require(current == Fraction(size + 1, 2 ** size), "endpoint principal determinant")
    return {"above_half": witnesses, "endpoint_recurrence_orders": NEGATIVE_LIMIT - 1}


def controls():
    rejected = 0
    for size, band, parameter in ((0, 1, Fraction(1, 2)), (True, 1, Fraction(1, 2)),
                                  (8, 1, Fraction(1, 2)), (3, 0, Fraction(1, 2)),
                                  (3, 13, Fraction(1, 2)), (3, 1, Fraction(0)),
                                  (3, 1, Fraction(1)), (3, 1, 0.5)):
        try:
            kernel(size, band, parameter)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid input accepted")
    mutants = []
    matrix, _ = integer_kernel(3, 1, Fraction(1, 2))
    bad_sign = [row[:] for row in matrix]
    bad_sign[0][0] = -1
    mutants.append((bad_sign, (0,), (0,)))
    bad_support = [row[:] for row in matrix]
    bad_support[0][2] = 1
    mutants.append((bad_support, (0,), (2,)))
    missing_edge = [row[:] for row in matrix]
    missing_edge[0][1] = 0
    mutants.append((missing_edge, (0,), (1,)))
    for matrix, rows, columns in mutants:
        try:
            check_minor(matrix, rows, columns, 1)
        except AssertionError as error:
            require(str(error) == "ordered minor criterion", "wrong mutant failure")
        else:
            raise AssertionError("semantic mutant accepted")
    result, _ = schur(kernel(4, 1, Fraction(1, 2)), [1, 2])
    require(result[0][3] == Fraction(1, 6), "fill beyond original band")
    result, _ = schur(kernel(3, 1, Fraction(1, 2)), [1])
    require(result[0][2] == -Fraction(1, 4), "eliminated-index parity")
    return {"input_rejections": rejected, "minor_mutants_rejected": len(mutants),
            "Schur_scope_fixtures": 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new generated receipt outside the package")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parent
    result = {"status": "PASS_SHARP_GAUSSIAN_SCHUR_RANGE", "claim_type": "scoped proof",
              "sharp_endpoint": "1/2", "python": platform.python_version(),
              "polynomial": polynomial_checks(), "ordered_minors": minor_checks(),
              "Schur": schur_checks(), "obstructions": obstruction_checks(), "controls": controls()}
    result["sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FILES}
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.receipt is not None:
        output = arguments.receipt
        if not output.is_absolute() or output.resolve().is_relative_to(root):
            parser.error("receipt must be an absolute path outside the package")
        with output.open("x", encoding="utf-8") as stream:
            written = stream.write(payload)
        require(written == len(payload), "complete receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
