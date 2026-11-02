#!/usr/bin/env python3
"""Exact finite corroboration of the square-zero tensor-error theorem.

Produced by Nick Petalas. Apache-2.0.
The all-dimension and all-k claims are proved in PROOF.md.
"""

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= 256, "matrix capacity")
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left, right):
    rows, inner, cols = len(left), len(right), len(right[0])
    require(1 <= rows <= 256 and 1 <= inner <= 256 and 1 <= cols <= 256,
            "matrix capacity")
    require(all(len(row) == inner for row in left), "matrix product shape")
    return [[sum((left[i][h] * right[h][j] for h in range(inner)), Q(0))
             for j in range(cols)] for i in range(rows)]


def kronecker(left, right):
    require(len(left) * len(right) <= 256, "tensor capacity")
    return [[x * y for x in row_left for y in row_right]
            for row_left in left for row_right in right]


def subtract_identity(matrix):
    return [[value - (i == j) for j, value in enumerate(row)]
            for i, row in enumerate(matrix)]


def tensor_error(k, a):
    require(type(k) is int and 1 <= k <= 8 and isinstance(a, Q) and a >= 0,
            "tensor domain")
    result = [[Q(1)]]
    for _ in range(k):
        result = kronecker(result, [[Q(1), a], [Q(0), Q(1)]])
    return subtract_identity(result)


def subset_error(k, a):
    size = 1 << k
    return [[a ** (column.bit_count() - row.bit_count())
             if row != column and row & column == row else Q(0)
             for column in range(size)] for row in range(size)]


def compressed_error(k, a):
    """Constant-on-level coordinates, with squared norms binomial(k, i)."""
    require(type(k) is int and 1 <= k <= 64 and isinstance(a, Q) and a >= 0,
            "compression domain")
    return [[comb(k - i, j - i) * a ** (j - i) if i < j else Q(0)
             for j in range(k + 1)] for i in range(k + 1)]


def weighted_gram(matrix, weights):
    size = len(weights)
    return [[sum((matrix[h][i] * weights[h] * matrix[h][j]
                  for h in range(size)), Q(0)) / weights[i]
             for j in range(size)] for i in range(size)]


def action(matrix, vector):
    return [sum((x * y for x, y in zip(row, vector, strict=True)), Q(0))
            for row in matrix]


def check_compression(full, compressed, k):
    size = len(full)
    weights = [comb(k, i) for i in range(k + 1)]
    gram = weighted_gram(compressed, weights)
    backward = transpose(full)
    checked = 0
    for level in range(k + 1):
        vector = [Q(column.bit_count() == level) for column in range(size)]
        image = action(full, vector)
        require(image == [compressed[row.bit_count()][level]
                          for row in range(size)], "compressed endpoint")
        image = action(backward, image)
        require(image == [gram[row.bit_count()][level]
                          for row in range(size)], "compressed Gram")
        checked += 2 * size
    return checked


def exact_endpoints():
    entries, compressed_entries, orientation_entries = 0, 0, 0
    for k in range(1, 7):
        for a in (Q(1, 3), Q(1, 2), Q(1), Q(2)):
            full = tensor_error(k, a)
            require(full == subset_error(k, a), "literal tensor versus subsets")
            entries += len(full) ** 2
            compressed_entries += check_compression(full, compressed_error(k, a), k)
            # Inverse transpose has the same singular norm by parity conjugation.
            signed = [[(-1) ** (i.bit_count() + j.bit_count()) * full[j][i]
                       for j in range(len(full))] for i in range(len(full))]
            inverse = [[Q(1)]]
            for _ in range(k):
                inverse = kronecker(inverse, [[Q(1), Q(0)], [-a, Q(1)]])
            require(subtract_identity(inverse) == signed, "inverse transpose sign")
            orientation_entries += len(full) ** 2
    return entries, compressed_entries, orientation_entries


def first_order_and_precision():
    incidence_cases, precision_cases = 0, 0
    for k in range(1, 65):
        gamma_squared = max(j * (k - j + 1) for j in range(1, k + 1))
        require(gamma_squared == ((k + 1) ** 2) // 4, "sharp first-order coefficient")
        incidence_cases += k
        for delta in (Q(1), Q(1, 2), Q(1, 16)):
            a = delta / (2 * k)
            upper = (1 + a) ** k - 1
            require(upper <= delta, "sufficient parameter choice")
            require(4 * k * k <= 16 * gamma_squared, "two-bit precision gap")
            precision_cases += 1
    # Fixed epsilon cannot provide a dimension-independent small tensor error.
    require((1 + Q(1, 32)) ** 64 - 1 > 1, "fixed-parameter error growth")
    return incidence_cases, precision_cases


def mixed_square_zero():
    """A rank-two error mixed by an exact rational orthogonal matrix."""
    half = Q(1, 2)
    rotation = [[half * x for x in row] for row in
                ((1, 1, 1, 1), (1, -1, 1, -1),
                 (1, 1, -1, -1), (1, -1, -1, 1))]
    require(multiply(rotation, transpose(rotation)) == identity(4), "orthogonal fixture")
    raw = [[Q(0), Q(2), Q(0), Q(0)], [Q(0)] * 4,
           [Q(0), Q(0), Q(0), Q(1)], [Q(0)] * 4]
    mixed = multiply(multiply(rotation, raw), transpose(rotation))
    require(multiply(mixed, mixed) == [[Q(0)] * 4 for _ in range(4)], "square zero")
    eps = Q(1, 4)
    positive = [[Q(i == j) + eps * mixed[i][j] for j in range(4)] for i in range(4)]
    negative = [[Q(i == j) - eps * mixed[i][j] for j in range(4)] for i in range(4)]
    require(multiply(positive, negative) == identity(4), "inverse endpoint")
    require(multiply(negative, positive) == identity(4), "reverse inverse endpoint")
    tensor_rotation = kronecker(rotation, rotation)
    raw_endpoint = [[Q(i == j) + eps * raw[i][j] for j in range(4)] for i in range(4)]
    transformed = multiply(multiply(tensor_rotation, kronecker(raw_endpoint, raw_endpoint)),
                           transpose(tensor_rotation))
    require(transformed == kronecker(positive, positive), "mixed tensor similarity")
    return 256


def rejection_controls():
    rejected = 0
    wrong = compressed_error(2, Q(1, 2))
    wrong[0][1] = Q(1, 2)
    try:
        check_compression(tensor_error(2, Q(1, 2)), wrong, 2)
    except ValueError:
        rejected += 1
    require(tensor_error(1, Q(1, 2)) != [[Q(1), Q(1, 2)], [Q(0), Q(1)]],
            "missing identity subtraction control")
    rejected += 1
    for k, a in ((0, Q(1)), (True, Q(1)), (9, Q(1)), (1, Q(-1)), (1, 0.5)):
        try:
            tensor_error(k, a)
        except ValueError:
            rejected += 1
    # For k=2 and a>0, linearization is strictly smaller than the exact norm.
    # det(B*B - 2a^2 I) on its two-dimensional active input block is -2a^6.
    for a in (Q(1, 3), Q(1, 2), Q(1), Q(2)):
        gram = weighted_gram(compressed_error(2, a), [1, 2, 1])
        determinant = ((gram[1][1] - 2 * a * a) * (gram[2][2] - 2 * a * a)
                       - gram[1][2] * gram[2][1])
        require(determinant == -2 * a ** 6 < 0, "false exact linear-error control")
        rejected += 1
    require(rejected == 11, "rejection count")
    return rejected


def write_receipt(path, result):
    package = Path(__file__).resolve().parent
    checkout = package.parents[1]
    require(not path.resolve().is_relative_to(checkout), "receipt must be outside checkout")
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VALIDATION.md", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    receipt = {"result": result, "package_sha256": hashes}
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    entries, compressed_entries, orientation_entries = exact_endpoints()
    incidence_cases, precision_cases = first_order_and_precision()
    result = {
        "status": "PASS_SQUARE_ZERO_TENSOR_ERROR",
        "literal_entries": entries,
        "compressed_action_entries": compressed_entries,
        "inverse_transpose_entries": orientation_entries,
        "first_order_level_cases": incidence_cases,
        "precision_cases": precision_cases,
        "mixed_rank_two_entries": mixed_square_zero(),
        "rejection_controls": rejection_controls(),
        "claim_type": "scoped proof with exact finite corroboration",
        "no_new_kappa": True,
    }
    if args.receipt is not None:
        write_receipt(args.receipt, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
