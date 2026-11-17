"""Exact endpoint checks, produced by Nick Petalas. Apache-2.0."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import random
import sys

from band_inverse import inverse, require, rounded_candidate


def dense_inverse(matrix):
    """Full Gauss-Jordan oracle; it knows nothing about band support."""
    n = len(matrix)
    rows = [[F(v) for v in row] + [F(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    operations = 0
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][k]
        rows[k] = [x / value for x in rows[k]]
        operations += 2 * n
        for i in range(n):
            if i != k and rows[i][k]:
                value = rows[i][k]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[k])]
                operations += 4 * n
    return [row[n:] for row in rows], operations


def endpoint(matrix, answer):
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            left = sum(matrix[i][k] * answer[k][j] for k in range(n))
            right = sum(answer[i][k] * matrix[k][j] for k in range(n))
            require(left == right == (i == j), "two-sided inverse failed")
    return 2 * n * n


def check_case(matrix, width):
    try:
        oracle, _ = dense_inverse(matrix)
    except ValueError:
        try:
            inverse(matrix, width)
        except ValueError as error:
            require(str(error) == "singular matrix", "wrong singular rejection")
            return {"singular": 1, "invertible": 0, "entries": 0, "swaps": 0}
        raise ValueError("singular matrix accepted")
    answer, counts = inverse(matrix, width)
    require(answer == oracle, "dense oracle disagreement")
    entries = endpoint(matrix, answer)
    for entry_bits, output_bits in ((0, 0), (3, 7), (11, 16)):
        rounded, _ = rounded_candidate(matrix, width, entry_bits, output_bits)
        scale = 1 << (entry_bits + output_bits)
        expected = [[(2 * x.numerator * scale + x.denominator)
                     // (2 * x.denominator) for x in row] for row in oracle]
        require(rounded == expected, "rounded complete candidate changed")
    return {"singular": 0, "invertible": 1, "entries": entries,
            "swaps": counts["swaps"]}


def small_cases():
    for n in range(1, 4):
        width = min(1, n - 1)
        positions = [(i, j) for i in range(n) for j in range(n)
                     if abs(i - j) <= width]
        for values in product((-1, 0, 1), repeat=len(positions)):
            matrix = [[0] * n for _ in range(n)]
            for (i, j), value in zip(positions, values):
                matrix[i][j] = value
            yield matrix, width


def larger_cases():
    rng = random.Random(56771113)
    for n in range(4, 17):
        for width in sorted({0, 1, min(3, n - 1), n - 1}):
            for sample in range(3):
                matrix = [[rng.randrange(-3, 4) if abs(i-j) <= width else 0
                           for j in range(n)] for i in range(n)]
                if sample == 0:
                    for i in range(n):
                        matrix[i][i] = 1 + sum(abs(x) for x in matrix[i])
                yield matrix, width
    for n in (8, 16, 32):
        matrix = [[int(i == j) for j in range(n)] for i in range(n)]
        for i in range(0, n, 2):
            matrix[i], matrix[i + 1] = matrix[i + 1], matrix[i]
        yield matrix, 1


def expect_rejection(matrix, width, entry_bits=0, output_bits=0):
    try:
        rounded_candidate(matrix, width, entry_bits, output_bits)
    except ValueError:
        return 1
    raise ValueError("invalid input accepted")


def controls():
    count = 0
    fixtures = (([], 0), ([[1, 2]], 0), ([[True]], 0), ([[1]], -1),
                ([[1]], True), ([[1 << 4096]], 0),
                ([[1, 1], [0, 1]], 0), ([[1]], 1))
    for matrix, width in fixtures:
        count += expect_rejection(matrix, width)
    for entry, output in ((-1, 0), (0, -1), (4097, 0), (0, 4097), (True, 0)):
        count += expect_rejection([[1]], 0, entry, output)
    count += expect_rejection([[1] * 257 for _ in range(257)], 0)
    answer, _ = inverse([[0, 1], [1, 1]], 1)
    answer[0][0] += 1
    try:
        endpoint([[0, 1], [1, 1]], answer)
    except ValueError:
        count += 1
    else:
        raise ValueError("corrupt inverse accepted")
    for value, expected in ((2, 1), (-2, 0)):
        rounded, _ = rounded_candidate([[value]], 0, 0, 0)
        require(rounded == [[expected]], "signed half tie convention changed")
    return count


def operation_examples():
    rows = []
    for n in (8, 16, 32):
        matrix = [[4 if i == j else int(abs(i-j) == 1)
                   for j in range(n)] for i in range(n)]
        answer, band = inverse(matrix, 1)
        oracle, dense = dense_inverse(matrix)
        require(answer == oracle, "counted methods compute different inverses")
        endpoint(matrix, answer)
        require(band["operations"] < dense, "tridiagonal count did not improve")
        rows.append({"dimension": n, "band_operations": band["operations"],
                     "dense_operations": dense, "band_bound": band["bound"]})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    totals = dict(singular=0, invertible=0, entries=0, swaps=0)
    for matrix, width in small_cases():
        for key, value in check_case(matrix, width).items():
            totals[key] += value
    for matrix, width in larger_cases():
        for key, value in check_case(matrix, width).items():
            totals[key] += value
    totals["controls"] = controls()
    totals["operation_examples"] = operation_examples()
    root = Path(__file__).resolve().parent
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(root.iterdir()) if p.is_file()}
    report = {"status": "PASS_BANDED_DYADIC_INVERSE_FALLBACK", "results": totals,
              "sha256": hashes, "python": sys.version,
              "platform": platform.platform()}
    if args.receipt:
        with args.receipt.open("x") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
