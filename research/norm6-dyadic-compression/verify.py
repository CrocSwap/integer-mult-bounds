#!/usr/bin/env python3
"""Bounded exact diagnostics for the norm-six dyadic compression corollary."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from math import lcm
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def validate(matrix):
    need(1 <= len(matrix) <= 64, "row capacity")
    columns = len(matrix[0])
    need(1 <= columns <= 64, "column capacity")
    need(all(len(row) == columns for row in matrix), "rectangular matrix")
    result = [[Fraction(value) for value in row] for row in matrix]
    for row in result:
        for value in row:
            denominator = value.denominator
            need(denominator & (denominator - 1) == 0, "dyadic input")
            need(abs(value.numerator).bit_length() <= 64, "numerator capacity")
            need(denominator.bit_length() <= 17, "denominator capacity")
    return result


def bezout(a, b):
    old_r, r = abs(a), abs(b)
    old_s, s, old_t, t = 1, 0, 0, 1
    bound = 2 * max(old_r.bit_length(), r.bit_length()) + 3
    for _ in range(bound):
        if r == 0:
            return old_r, old_s * (1 if a >= 0 else -1), old_t * (1 if b >= 0 else -1)
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    raise ValueError("Euclidean iteration bound exhausted")


def combine_columns(work, pivot, other, row):
    a, b = work[row][pivot], work[row][other]
    if b % a == 0:
        quotient = b // a
        for values in work:
            values[other] -= quotient * values[pivot]
        return
    divisor, s, t = bezout(a, b)
    need(divisor > 0 and s * a + t * b == divisor, "Bezout identity")
    aa, bb = a // divisor, b // divisor
    for values in work:
        first, second = values[pivot], values[other]
        values[pivot] = s * first + t * second
        values[other] = -bb * first + aa * second
    need(work[row][other] == 0, "cleared pivot row")


def integer_coordinates(work, original, pivot_rows):
    columns = len(original[0])
    coordinates = [[0] * columns for _ in pivot_rows]
    for k, row in enumerate(pivot_rows):
        for column in range(columns):
            residual = original[row][column] - sum(
                work[row][j] * coordinates[j][column] for j in range(k))
            quotient, remainder = divmod(residual, work[row][k])
            need(remainder == 0, "integral lattice-basis coordinates")
            coordinates[k][column] = quotient
    return coordinates


def integer_basis(original):
    """Column-lattice basis and integral coordinates for a trusted matrix."""
    rows, columns = len(original), len(original[0])
    work = [row[:] for row in original]
    pivot_rows = []
    rank = 0
    for row in range(rows):
        if rank == columns:
            break
        candidates = [j for j in range(rank, columns) if work[row][j]]
        if not candidates:
            continue
        selected = candidates[0]
        for candidate in candidates[1:]:
            if abs(work[row][candidate]) < abs(work[row][selected]):
                selected = candidate
        for values in work:
            values[rank], values[selected] = values[selected], values[rank]
        for other in range(rank + 1, columns):
            if work[row][other]:
                combine_columns(work, rank, other, row)
        # Bound earlier-column residues without changing earlier pivot rows.
        for earlier in range(rank):
            quotient = work[row][earlier] // work[row][rank]
            for values in work:
                values[earlier] -= quotient * values[rank]
        pivot_rows.append(row)
        rank += 1
    need(all(value == 0 for row in work for value in row[rank:]), "zero tail")
    left = [row[:rank] for row in work]
    return left, integer_coordinates(work, original, pivot_rows)


def rational_coordinates(matrix):
    """M = selected_columns(M) C; rational preconditioning, not native factors."""
    work = [row[:] for row in matrix]
    rows, columns, pivots = len(work), len(work[0]), []
    for column in range(columns):
        rank = len(pivots)
        candidates = [i for i in range(rank, rows) if work[i][column]]
        if not candidates:
            continue
        selected = candidates[0]
        work[rank], work[selected] = work[selected], work[rank]
        pivot = work[rank][column]
        work[rank] = [value / pivot for value in work[rank]]
        for i in range(rows):
            if i != rank:
                coefficient = work[i][column]
                work[i] = [x - coefficient * y for x, y in zip(work[i], work[rank])]
        pivots.append(column)
        if len(pivots) == rows:
            break
    return pivots, work[:len(pivots)]


def factor(matrix):
    matrix = validate(matrix)
    pivots, coordinates = rational_coordinates(matrix)
    if not pivots:
        return [[] for _ in matrix], []
    scale = lcm(*(value.denominator for row in coordinates for value in row))
    integral = [[int(scale * value) for value in row] for row in coordinates]
    basis, right = integer_basis(integral)
    left = [[sum(row[pivots[k]] * basis[k][j] for k in range(len(pivots))) / scale
             for j in range(len(right))] for row in matrix]
    need(all(value.denominator & (value.denominator - 1) == 0
             for row in left for value in row), "dyadic after lattice reduction")
    return left, right


def rational_rank(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    rows, columns, rank = len(work), len(work[0]), 0
    for column in range(columns):
        candidates = [i for i in range(rank, rows) if work[i][column]]
        if not candidates:
            continue
        selected = candidates[0]
        work[rank], work[selected] = work[selected], work[rank]
        pivot = work[rank][column]
        work[rank] = [value / pivot for value in work[rank]]
        for i in range(rank + 1, rows):
            coefficient = work[i][column]
            work[i] = [x - coefficient * y for x, y in zip(work[i], work[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def check_product(left, right, expected):
    rank = len(right)
    for i, row in enumerate(expected):
        for j, value in enumerate(row):
            actual = sum(left[i][k] * right[k][j] for k in range(rank))
            need(actual == value, "exact factor product")


def check_factor(matrix):
    left, right = factor(matrix)
    expected = validate(matrix)
    rank = len(right)
    need(rank == rational_rank(expected), "independent rational rank")
    check_product(left, right, expected)
    need(all(isinstance(value, int) for row in right for value in row), "integer right factor")
    need(all(value.denominator & (value.denominator - 1) == 0
             for row in left for value in row), "dyadic left factor")
    return rank


def shell(dimension):
    vectors = []
    for vector in product(range(-2, 3), repeat=dimension):
        if sum(value * value for value in vector) != 6:
            continue
        leading = next(value for value in vector if value)
        if leading > 0:
            vectors.append(vector)
    return vectors


def kernel(vectors, linear=4, denominator=192):
    matrix = []
    for x in vectors:
        row = []
        for y in vectors:
            dot = sum(a * b for a, b in zip(x, y))
            row.append(Fraction(dot ** 3 - linear * dot, denominator))
        matrix.append(row)
    return matrix


def check_diagonal(matrix):
    need(all(matrix[i][i] == 1 for i in range(len(matrix))), "unit diagonal")


def controls():
    vectors = shell(3)
    invalid = ([[Fraction(1, 3)]], [[1, 2], [3]], [], [[1] * 65], kernel(vectors, linear=3))
    count = 0
    for matrix in invalid:
        try:
            factor(matrix)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid matrix was accepted")
    odd = [[3, 1], [6, 2]]
    need(check_factor(odd) == 1, "odd pivot positive control")
    need(Fraction(odd[0][1], odd[0][0]).denominator == 3, "naive pivot obstruction")
    try:
        check_diagonal(kernel(vectors, denominator=96))
    except ValueError:
        count += 1
    else:
        raise ValueError("wrong normalization was accepted")
    left, right = factor(odd)
    right[0][0] += 1
    try:
        check_product(left, right, odd)
    except ValueError:
        count += 1
    else:
        raise ValueError("changed factor was accepted")
    need(count == 7, "complete rejection inventory")
    return count


def diagnostics():
    shell_results = []
    for dimension in (3, 4):
        vectors = shell(dimension)
        matrix = kernel(vectors)
        check_diagonal(matrix)
        rank = check_factor(matrix)
        cubics = sum(1 for _ in combinations_with_replacement(range(dimension), 3))
        need(rank == cubics, "small-shell attained rank")
        shell_results.append({"dimension": dimension, "ports": len(vectors), "rank": rank})
    samples = 0
    for rows, columns in ((1, 4), (4, 1), (3, 5), (5, 3), (6, 6)):
        for seed in range(24):
            matrix = [[Fraction(((i + 2) * (j + 3) * (seed + 1)) % 17 - 8,
                                2 ** ((i + j + seed) % 5))
                       for j in range(columns)] for i in range(rows)]
            check_factor(matrix)
            samples += 1
    need(check_factor([[0, 0], [0, 0]]) == 0, "empty-rank factorization")
    return shell_results, samples


def main():
    shell_results, samples = diagnostics()
    control_count = controls()
    cubics = sum(1 for _ in combinations_with_replacement(range(48), 3))
    old_terms = 48 + 48 + 48 * 47 + sum(1 for _ in combinations(range(48), 3))
    need(cubics == 19600 and old_terms == 19648, "enumerated feature dimensions")
    need(49 * cubics == 960400 and 49 * (old_terms - cubics) == 2352, "support bounds")
    package = Path(__file__).resolve().parent
    hashes = {path.name: sha256(path.read_bytes()).hexdigest()
              for path in sorted(package.iterdir()) if path.is_file()}
    print(json.dumps({"status": "PASS_NORM6_DYADIC_COMPRESSION", "claim_type": "scoped proof",
                      "new_term_bound": cubics, "new_support_bound": 49 * cubics,
                      "saved_support_bound": 2352, "small_shells": shell_results,
                      "additional_matrices": samples, "rejection_controls": control_count,
                      "package_sha256": hashes, "full_shell_enumerated": False,
                      "new_kappa": False}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
