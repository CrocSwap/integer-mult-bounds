#!/usr/bin/env python3
"""Exact F4 intersection certificate. Produced by Nick Petalas. Apache-2.0.

Independent human and formal proof-kernel review are unclaimed.
The all-dimension statement is proved in README.md; this is finite evidence.
"""

import hashlib
import itertools
import json
from pathlib import Path


MAX_PAIR_DIMENSION = 5
MAX_NORM_DIMENSION = 7
CONJUGATE = (0, 1, 3, 2)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    """Polynomial basis 1,t with t^2=t+1; elements are two-bit integers."""
    low = (a & 1) * (b & 1)
    middle = ((a & 1) * (b >> 1)) ^ ((a >> 1) * (b & 1))
    high = (a >> 1) * (b >> 1)
    return (low ^ high) | ((middle ^ high) << 1)


def hermitian(u, v):
    result = 0
    for a, b in zip(u, v, strict=True):
        result ^= multiply(CONJUGATE[a], b)
    return result


def rref(matrix, columns):
    need(0 <= columns <= 10 and len(matrix) <= 10, "matrix size bound")
    need(all(len(row) == columns for row in matrix), "rectangular matrix")
    rows = [list(row) for row in matrix]
    need(all(0 <= x < 4 for row in rows for x in row), "F4 entries")
    pivots = []
    for column in range(columns):
        candidates = [i for i in range(len(pivots), len(rows)) if rows[i][column]]
        if not candidates:
            continue
        index = len(pivots)
        rows[index], rows[candidates[0]] = rows[candidates[0]], rows[index]
        inverse = CONJUGATE[rows[index][column]]
        rows[index] = [multiply(inverse, x) for x in rows[index]]
        for i in range(len(rows)):
            if i != index and rows[i][column]:
                coefficient = rows[i][column]
                rows[i] = [x ^ multiply(coefficient, y)
                           for x, y in zip(rows[i], rows[index], strict=True)]
        pivots.append(column)
    return rows, pivots


def kernel(matrix, columns):
    rows, pivots = rref(matrix, columns)
    basis = []
    for free in range(columns):
        if free not in pivots:
            vector = [int(j == free) for j in range(columns)]
            for row, pivot in zip(rows, pivots):
                vector[pivot] = row[free]
            basis.append(tuple(vector))
    return basis


def binary_rank(rows):
    need(len(rows) <= 10, "binary rank dimension")
    pivots = [0] * 10
    result = 0
    for row in rows:
        need(0 <= row < 1024, "binary row bound")
        value = row
        for column in range(9, -1, -1):
            if value & (1 << column):
                if pivots[column]:
                    value ^= pivots[column]
                else:
                    pivots[column] = value
                    result += 1
                    break
    return result


def restriction_ranks(basis):
    gram = [[hermitian(u, v) for v in basis] for u in basis]
    rank4 = len(rref(gram, len(basis))[1])
    binary_basis = [tuple(multiply(a, x) for x in v)
                    for v in basis for a in (1, 2)]
    binary_rows = []
    for u in binary_basis:
        row = 0
        for j, v in enumerate(binary_basis):
            value = hermitian(u, v)
            trace = value ^ CONJUGATE[value]
            need(trace in (0, 1), "trace lies in F2")
            row |= trace << j
        binary_rows.append(row)
    return rank4, binary_rank(binary_rows)


def intersection(u, v):
    n = len(u)
    need(2 <= n <= MAX_PAIR_DIMENSION and len(v) == n, "pair dimension")
    need(hermitian(u, u) == hermitian(v, v) == 1, "nonisotropic normals")
    basis = kernel([[CONJUGATE[x] for x in u], [CONJUGATE[x] for x in v]], n)
    need(len(basis) == n - 2, "distinct normal lines")
    need(all(hermitian(u, x) == hermitian(v, x) == 0 for x in basis),
         "literal common kernel")
    rank4, rank2 = restriction_ranks(basis)
    return n - 2 - rank4, 2 * (n - 2) - rank2


def norm_counts(n):
    return ((4**n + (-2)**n) // 2, (4**n - (-2)**n) // 2)


def hyperplane_count(n):
    return (4**n - (-2)**n) // 6


def norm_one_lines(n):
    return [v for v in itertools.product(range(4), repeat=n)
            if next((x for x in v if x), 0) == 1 and hermitian(v, v) == 1]


def field_and_norm_checks():
    field_cases = 0
    for a, b, c in itertools.product(range(4), repeat=3):
        need(multiply(a, b ^ c) == (multiply(a, b) ^ multiply(a, c)),
             "field distributivity")
        need(multiply(multiply(a, b), c) == multiply(a, multiply(b, c)),
             "field associativity")
        need(multiply(a, b) == multiply(b, a), "field commutativity")
        need(multiply(a, a) == CONJUGATE[a], "field conjugation")
        need(multiply(CONJUGATE[a], a) == int(a != 0), "field norm")
        field_cases += 1
    vector_cases = 0
    for n in range(MAX_NORM_DIMENSION + 1):
        observed = [0, 0]
        for v in itertools.product(range(4), repeat=n):
            norm = hermitian(v, v)
            need(norm in (0, 1), "Hermitian norm in F2")
            observed[norm] += 1
            vector_cases += 1
        need(tuple(observed) == norm_counts(n), "closed norm counts")
    return field_cases, vector_cases


def census():
    results = []
    for n in range(2, MAX_PAIR_DIMENSION + 1):
        lines = norm_one_lines(n)
        need(len(lines) == hyperplane_count(n), "hyperplane count")
        counts = [0, 0]
        for u in lines:
            per_normal = [0, 0]
            for v in lines:
                if u == v:
                    continue
                radical4, radical2 = intersection(u, v)
                predicted = int(hermitian(u, v) != 0)
                need(radical4 == predicted, "F4 radical criterion")
                need(radical2 == 2 * predicted, "binary radical criterion")
                per_normal[radical4] += 1
            expected = [hyperplane_count(n - 1), norm_counts(n - 1)[0] - 1]
            need(per_normal == expected, "counts for every individual normal")
            counts = [a + b for a, b in zip(counts, per_normal, strict=True)]
        need(sum(counts) == len(lines) * (len(lines) - 1), "complete pair domain")
        results.append({"dimension": n, "hyperplanes": len(lines),
                        "nondegenerate_ordered_pairs": counts[0],
                        "degenerate_ordered_pairs": counts[1]})
    return results


def orthogonal_families():
    """Exhaust every subset of the twelve normal lines in dimension three."""
    lines = norm_one_lines(3)
    sizes = [0] * 13
    for mask in range(1 << len(lines)):
        chosen = [v for j, v in enumerate(lines) if mask & (1 << j)]
        safe = all(hermitian(u, v) == 0 for u, v in itertools.combinations(chosen, 2))
        if not safe:
            continue
        need(len(chosen) <= 3, "pairwise-safe family size")
        basis = kernel([[CONJUGATE[x] for x in v] for v in chosen], 3)
        rank4, rank2 = restriction_ranks(basis)
        need(rank4 == len(basis) and rank2 == 2 * len(basis),
             "higher intersection nondegenerate")
        sizes[len(chosen)] += 1
    need(sizes[3] > 0 and sum(sizes[4:]) == 0, "sharp dimension-three cap")
    return sizes[:4]


def must_reject(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def controls():
    u, v = (1, 0, 0), (1, 1, 1)
    need(intersection(u, v) == (1, 2), "smallest failing witness")
    for normal in (u, v):
        basis = kernel([[CONJUGATE[x] for x in normal]], 3)
        need(restriction_ranks(basis) == (2, 4), "nondegenerate input planes")
    need(intersection((1, 0), (0, 1)) == (0, 0), "dimension-two safe control")
    need(intersection(u, (0, 1, 0)) == (0, 0), "orthogonal safe control")
    must_reject(lambda: intersection(u, u), "duplicate hyperplane")
    must_reject(lambda: intersection(u, (0, 1, 1)), "isotropic normal")
    must_reject(lambda: intersection((1,), (1,)), "dimension below domain")
    must_reject(lambda: rref([[4]], 1), "invalid field entry")
    must_reject(lambda: need(intersection(u, v) == (0, 0), "false closure"),
                "nondegeneracy inherited by intersection")
    must_reject(lambda: need(hyperplane_count(3) == (4**3 + (-2)**3) // 6,
                             "count sign mutation"), "wrong count sign")
    must_reject(lambda: need(multiply(2, 2) == hermitian((2,), (2,)),
                             "unconjugated norm"), "missing conjugation")
    must_reject(lambda: need(intersection(u, v)[1] == 1, "binary radical"),
                "missing binary dimension doubling")
    need(intersection(u, (1, 2, 1)) == (1, 2), "nonbinary coefficient witness")
    return 8


def receipt(result):
    package = Path(__file__).resolve().parent
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in files}
    print(json.dumps({"result": result, "package_sha256": hashes}, sort_keys=True))


def main():
    field_cases, vector_cases = field_and_norm_checks()
    result = {"field_triples": field_cases, "norm_vectors": vector_cases,
              "census": census(), "safe_family_counts_dimension_three": orthogonal_families(),
              "rejecting_controls": controls()}
    receipt(result)
    print("PASS_HERMITIAN_HYPERPLANE_INTERSECTIONS")


if __name__ == "__main__":
    main()
