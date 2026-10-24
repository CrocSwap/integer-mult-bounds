#!/usr/bin/env python3
"""Check the rigidity of nine E8 totals at coordinate hyperplanes.

Use only the Python standard library. Do not import repository code.
Run this file with the path to gcert1-e8-r783.json.gz as its first argument.
"""

import gzip
import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations
from math import comb


def family():
    labels, vectors, heights = [], [], []
    for triple in combinations(range(9), 3):
        labels.append(sum(1 << i for i in triple))
        vectors.append([int(i in triple) for i in range(9)])
        heights.append(1)
    for i, j in combinations(range(9), 2):
        labels.append(511 ^ (1 << i) ^ (1 << j))
        vector = [0] * 9
        vector[i], vector[j] = 1, -1
        vectors.append(vector)
        heights.append(0)
    return labels, vectors, heights


def binary_rank(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def equations(labels, vectors, extra_normal=0):
    rows = []
    descriptors = []
    for port, vector in zip(labels, vectors):
        outside = [i for i in range(9) if (port >> i) & 1]
        if extra_normal and (port & extra_normal).bit_count() % 2:
            outside = sorted(set(outside) | {0})
        basis_coeffs = [vector[i] - vector[8] for i in range(8)]
        first = outside[0]
        for second in outside[1:]:
            row = [0] * 64
            for index, sign in ((first, 1), (second, -1)):
                if index:
                    for k, value in enumerate(basis_coeffs):
                        row[8 * (index - 1) + k] += sign * value
            rows.append(row)
            descriptors.append([port, first, second])
    return rows, descriptors


def rational_kernel(rows):
    pivots = {}
    for source in rows:
        row = list(map(Fraction, source))
        for pivot in sorted(pivots):
            coefficient = row[pivot]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, pivots[pivot])]
        if any(row):
            pivot = next(i for i, value in enumerate(row) if value)
            scale = row[pivot]
            pivots[pivot] = [value / scale for value in row]
    free = [i for i in range(64) if i not in pivots]
    kernel = []
    for column in free:
        vector = [Fraction(0)] * 64
        vector[column] = Fraction(1)
        for pivot in sorted(pivots, reverse=True):
            vector[pivot] = -sum(
                pivots[pivot][i] * vector[i] for i in range(pivot + 1, 64)
            )
        assert all(sum(a * b for a, b in zip(row, vector)) == 0 for row in rows)
        kernel.append(vector)
    return len(pivots), kernel


def modular_rank(rows, prime):
    matrix = [[value % prime for value in row] for row in rows]
    rank = 0
    for column in range(64):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, prime)
        matrix[rank] = [(value * inverse) % prime for value in matrix[rank]]
        for i in range(rank + 1, len(matrix)):
            coefficient = matrix[i][column]
            if coefficient:
                matrix[i] = [(a - coefficient * b) % prime for a, b in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank


def main():
    certificate_path = sys.argv[1]
    with open(certificate_path, "rb") as handle:
        certificate_bytes = handle.read()
    certificate = json.loads(gzip.decompress(certificate_bytes))
    labels, vectors, heights = family()
    assert certificate["h"] == 9 and certificate["v"] == 120
    assert certificate["ports"] == labels

    scatter_entries = 0
    for source, source_height in zip(vectors, heights):
        scatter = [(Fraction(source[i]) - Fraction(source_height, 3)) / 2 for i in range(9)]
        assert sum(scatter) == 0
        for target, target_height in zip(vectors, heights):
            actual = sum(scatter[i] * (target[i] - target_height) for i in range(9))
            expected = Fraction(sum(a * b for a, b in zip(source, target)) - source_height * target_height, 2)
            assert actual == expected
            scatter_entries += 1
    assert scatter_entries == 14400

    expected_kernel = []
    for i in range(1, 9):
        row = [0] * 8
        row[0] = 1
        if i < 8:
            row[i] = -1
        expected_kernel.extend(row)

    results = []
    for weight in (0, 1, 3, 5, 7):
        extra_normal = sum(1 << i for i in range(1, weight + 1))
        rows, descriptors = equations(labels, vectors, extra_normal)
        rank, kernel = rational_kernel(rows)
        modular = {str(prime): modular_rank(rows, prime) for prime in (101, 103)}
        assert all(value == rank for value in modular.values())
        if weight == 0:
            assert rank == 63 and kernel == [list(map(Fraction, expected_kernel))]
        else:
            assert rank == 64 and not kernel
        results.append({
            "extra_normal_weight": weight,
            "extra_normal": extra_normal,
            "orbit_size": 1 if weight == 0 else comb(8, weight),
            "equations": len(rows),
            "rational_rank": rank,
            "nullity": 64 - rank,
            "modular_ranks": modular,
            "equations_sha256": hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest(),
        })

    supports = []
    for i in range(9):
        support = [port for port, vector, height in zip(labels, vectors, heights) if height - vector[i]]
        assert len(support) == 64 and binary_rank(support) == 8
        assert all((port >> i) & 1 == 0 for port in support)
        supports.append({"coordinate": i, "support_size": len(support), "binary_rank": binary_rank(support)})

    print(json.dumps({
        "certificate_sha256": hashlib.sha256(certificate_bytes).hexdigest(),
        "variables": 64,
        "exact_scatter_entries_checked": scatter_entries,
        "nondegenerate_tightening_frames": sum(comb(8, weight) for weight in (1, 3, 5, 7)),
        "results": results,
        "baseline_kernel_rows": [expected_kernel[8 * i:8 * (i + 1)] for i in range(8)],
        "canonical_total_supports": supports,
        "scope": "Nine rational totals, one supported in each coordinate hyperplane, whose span contains the canonical E8 rank-eight coefficient space.",
        "conclusion": "The coefficient space of all nine totals is unique. Up to nonzero individual scales, the totals are t-a_i. None can have support in a proper subspace of its coordinate hyperplane.",
    }, indent=2))


if __name__ == "__main__":
    main()
