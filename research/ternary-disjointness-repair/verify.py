#!/usr/bin/env python3
"""Exact finite corroboration of the odd-dimensional ternary repair theorem."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(0 < n <= 512, "matrix dimension outside replay bound")
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    n, inner, width = len(a), len(b), len(b[0])
    require(0 < n <= 512 and 0 < inner <= 512 and 0 < width <= 512,
            "matrix dimension outside replay bound")
    require(all(len(row) == inner for row in a), "left matrix shape")
    require(all(len(row) == width for row in b), "right matrix shape")
    out = [[0] * width for _ in range(n)]
    for i in range(n):
        for k in range(inner):
            if a[i][k]:
                for j in range(width):
                    out[i][j] += a[i][k] * b[k][j]
        out[i] = [x % 3 for x in out[i]]
    return out


def rank_mod_three(matrix):
    require(0 < len(matrix) <= 512, "rank dimension outside replay bound")
    width = len(matrix[0])
    require(0 < width <= 512 and all(len(r) == width for r in matrix),
            "rank matrix shape")
    a = [[x % 3 for x in row] for row in matrix]
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, 3)
        a[rank] = [(x * inverse) % 3 for x in a[rank]]
        for i in range(rank + 1, len(a)):
            if a[i][col]:
                scale = a[i][col]
                a[i] = [(x - scale * y) % 3 for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def tensor_entry(local, u, v, h):
    value = 1
    for bit in range(h):
        value = value * local[(u >> bit) & 1][(v >> bit) & 1] % 3
    return value


def polynomial_inverse(h):
    require(type(h) is int and 3 <= h <= 9 and h % 2 == 1,
            "replay requires odd integer h in 3..9")
    local_powers = (
        ((1, 0), (0, 1)), ((1, 1), (1, 0)),
        ((2, 1), (1, 1)), ((0, 2), (2, 1)),
    )
    n = 1 << h
    return [[2 * sum(tensor_entry(k, u, v, h) for k in local_powers) % 3
             for v in range(n)] for u in range(n)]


def repair_matrix(h):
    require(type(h) is int and 2 <= h <= 9, "repair replay h outside 2..9")
    proper = range(1, (1 << h) - 1)
    # This literal set predicate is independent of the tensor-entry evaluator.
    return [[(int(u == v) - int(u & v == 0)) % 3 for v in proper]
            for u in proper]


def corrected_inverse(r):
    boundary = (0, len(r) - 1)
    inverse_boundary = ((0, 2), (2, 1))
    interior = range(1, len(r) - 1)
    return [[(r[u][v] - sum(r[u][boundary[i]] * inverse_boundary[i][j]
                           * r[boundary[j]][v]
                           for i in range(2) for j in range(2))) % 3
             for v in interior] for u in interior]


def require_inverse(a, candidate):
    require(multiply(a, candidate) == identity(len(a)), "inverse identity failed")


def rejecting_controls(r, b):
    rejected = 0
    for bad in (True, 2, 4, 10):
        try:
            polynomial_inverse(bad)
        except ValueError:
            rejected += 1
    raw = [row[1:-1] for row in r[1:-1]]
    correct = corrected_inverse(r)
    wrong_sign = [[(2 * raw[i][j] - correct[i][j]) % 3
                   for j in range(len(b))] for i in range(len(b))]
    for candidate in (raw, wrong_sign):
        try:
            require_inverse(b, candidate)
        except ValueError:
            rejected += 1
    require(rejected == 6, "a negative control was not rejected")
    even = repair_matrix(2)
    require(rank_mod_three(even) == 1, "even-dimension counterexample lost")
    require(multiply(even, [[1], [1]]) == [[0], [0]], "even kernel witness")
    return rejected


def main():
    k = [[1, 1], [1, 0]]
    k2 = multiply(k, k)
    k3 = multiply(k2, k)
    require(k2 == [[2, 1], [1, 1]], "K squared")
    require(k3 == [[0, 2], [2, 1]], "K cubed")
    require(multiply(k3, k) == [[2, 0], [0, 2]], "K fourth power")
    cases = []
    for h in (3, 5, 7):
        n = 1 << h
        r = polynomial_inverse(h)
        m = [[(int(u == v) - int(u & v == 0)) % 3 for v in range(n)]
             for u in range(n)]
        require_inverse(m, r)
        boundary = [[r[u][v] for v in (0, n - 1)] for u in (0, n - 1)]
        require(boundary == [[2, 2], [2, 0]], "endpoint inverse block")
        b = repair_matrix(h)
        actual_rank = rank_mod_three(b)
        require(actual_rank == n - 2, "odd repair is not full rank")
        require_inverse(b, corrected_inverse(r))
        cases.append({"h": h, "dimension": n - 2, "rank": actual_rank})
    b = repair_matrix(9)
    actual_rank = rank_mod_three(b)
    require(actual_rank == 510, "h=9 repair is not full rank")
    cases.append({"h": 9, "dimension": 510, "rank": actual_rank})
    b = repair_matrix(3)
    kernel_size = 0
    for x in product(range(3), repeat=6):
        if all(sum(a * c for a, c in zip(row, x)) % 3 == 0 for row in b):
            kernel_size += 1
    require(kernel_size == 1, "independent full kernel census")
    controls = rejecting_controls(polynomial_inverse(3), b)
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    report = {"schema": "ternary-disjointness-repair-replay/1",
              "python": platform.python_version(), "cases": cases,
              "kernel_vectors": 3 ** 6, "kernel_size": kernel_size,
              "rejected_controls": controls, "even_counterexample_h": 2,
              "source_sha256": hashes}
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_TERNARY_DISJOINTNESS_REPAIR odd_h=3,5,7,9 no_new_kappa")


if __name__ == "__main__":
    main()
