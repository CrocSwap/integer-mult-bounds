#!/usr/bin/env python3
"""Exact finite corroboration of the column-capped resolvent theorem.

Copyright 2026 Nick Petalas. SPDX-License-Identifier: Apache-2.0
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(n, m, rho):
    require(type(n) is int and 1 <= n <= 128, "dimension outside 1..128")
    require(type(m) is int and 2 <= m <= 128, "branching outside 2..128")
    require(isinstance(rho, Q) and 0 < rho < 1, "invalid rational row cap")
    require(max(rho.numerator.bit_length(), rho.denominator.bit_length()) <= 32,
            "row-cap bit budget exceeded")


def levels(n, m):
    """Integer shell enumeration, with no floating logarithms."""
    parameters(n, m, Q(1, 2))
    result = [0] * n
    boundary = 1
    for depth in range(1, 8):
        following = min(n, boundary * m)
        for index in range(boundary, following):
            result[index] = depth
        boundary = following
        if boundary == n:
            break
    require(boundary == n, "shell capacity exhausted")
    return result


def envelope(n, m, rho):
    parameters(n, m, rho)
    return sum((rho ** depth for depth in levels(n, m)), Q(0)) / (1 - rho)


def witness(n, m, rho):
    parameters(n, m, rho)
    matrix = [[Q(0) for _ in range(n)] for _ in range(n)]
    for index in range(n):
        matrix[index][index // m] = rho
    return matrix


def admitted(matrix, m, rho):
    n = len(matrix)
    parameters(n, m, rho)
    require(all(len(row) == n for row in matrix), "nonsquare matrix")
    require(all(isinstance(x, Q) for row in matrix for x in row),
            "nonrational coefficient")
    require(all(sum(map(abs, row)) <= rho for row in matrix), "row cap exceeded")
    require(all(sum(abs(matrix[i][j]) for i in range(n)) <= m * rho
                for j in range(n)), "column cap exceeded")


def inverse(matrix):
    """Independent exact Gauss-Jordan inverse of I-matrix."""
    n = len(matrix)
    require(1 <= n <= 12, "dense inverse capacity exceeded")
    rows = [[Q(i == j) - matrix[i][j] for j in range(n)]
            + [Q(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, "singular matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [entry / scale for entry in rows[j]]
        for i in range(n):
            if i != j:
                factor = rows[i][j]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[j])]
    result = [row[n:] for row in rows]
    for i, j in product(range(n), repeat=2):
        actual = sum((Q(i == k) - matrix[i][k]) * result[k][j]
                     for k in range(n))
        require(actual == Q(i == j), "inverse residual")
    return result


def column_checks(matrix, inv, m, rho, nonnegative):
    n = len(matrix)
    bound = envelope(n, m, rho)
    partial_checks = 0
    for j in range(n):
        values = sorted((abs(inv[i][j]) for i in range(n)), reverse=True)
        require(sum(values) <= bound, "inverse envelope failed")
        if nonnegative:
            require(inv[j][j] == values[0], "root is not a maximum")
            for k in range(1, n + 1):
                q, r = divmod(k, m)
                rhs = 1 + rho * (m * sum(values[:q])
                                 + (r * values[q] if r else 0))
                require(sum(values[:k]) <= rhs, "transport partial-sum bound")
                require(sum(values[:k]) <= envelope(k, m, rho),
                        "partial-sum induction failed")
                partial_checks += 1
    return partial_checks


def exhaustive_grid():
    """Every nonnegative half-row-unit matrix through dimension three."""
    cases = partials = signed = 0
    maxima = {}
    for n in range(1, 4):
        choices = [row for row in product(range(3), repeat=n) if sum(row) <= 2]
        require(len(choices) <= 10, "row enumeration capacity exceeded")
        for raw in product(choices, repeat=n):
            for rho in (Q(1, 3), Q(1, 2), Q(2, 3)):
                matrix = [[rho * x / 2 for x in row] for row in raw]
                inv = inverse(matrix)
                for m in (2, 3):
                    if max(sum(matrix[i][j] for i in range(n))
                           for j in range(n)) > m * rho:
                        continue
                    admitted(matrix, m, rho)
                    partials += column_checks(matrix, inv, m, rho, True)
                    norm = max(sum(abs(inv[i][j]) for i in range(n))
                               for j in range(n))
                    key = (n, m, rho)
                    maxima[key] = max(maxima.get(key, Q(0)), norm)
                    cases += 1
                if n == 3 and all(sum(row) == 2 for row in raw):
                    changed = [[x * (-1 if (i * j + i + j) % 2 else 1)
                                for j, x in enumerate(row)]
                               for i, row in enumerate(matrix)]
                    admitted(changed, 3, rho)
                    column_checks(changed, inverse(changed), 3, rho, False)
                    signed += 1
    require(len(maxima) == 18, "missing exhaustive domains")
    for (n, m, rho), observed in maxima.items():
        require(observed == envelope(n, m, rho), "grid does not attain envelope")
    return {"matrices": cases, "partial_sums": partials,
            "signed_matrices": signed, "attained_domains": len(maxima)}


def attaining_cases():
    cases = dense = entries = recurrences = 0
    for n, m, rho in product(range(1, 65), range(2, 9),
                             (Q(1, 4), Q(1, 3), Q(1, 2), Q(2, 3), Q(3, 4))):
        matrix = witness(n, m, rho)
        admitted(matrix, m, rho)
        values = [rho ** d / (1 - rho) for d in levels(n, m)]
        for i in range(n):
            require(values[i] - rho * values[i // m] == Q(i == 0),
                    "attaining column residual")
            entries += 1
        require(sum(values) == envelope(n, m, rho), "attaining sum")
        for k in range(1, n + 1):
            q, r = divmod(k, m)
            rhs = 1 + rho * (m * sum(values[:q])
                             + (r * values[q] if r else 0))
            require(sum(values[:k]) == rhs, "attaining transport recurrence")
            recurrences += 1
        if n <= 12:
            inv = inverse(matrix)
            require([row[0] for row in inv] == values, "dense witness column")
            dense += 1
        cases += 1
    return {"matrices": cases, "dense_inverses": dense,
            "column_entries": entries, "transport_equalities": recurrences}


def rejects(thunk, text):
    try:
        thunk()
    except ValueError as error:
        require(str(error) == text, "unexpected rejection reason")
        return 1
    raise ValueError("invalid input accepted")


def controls():
    count = 0
    for args, message in (
        ((0, 2, Q(1, 2)), "dimension outside 1..128"),
        ((129, 2, Q(1, 2)), "dimension outside 1..128"),
        ((2, 1, Q(1, 2)), "branching outside 2..128"),
        ((2, 2, Q(1)), "invalid rational row cap"),
        ((2, 2, Q(0)), "invalid rational row cap"),
        ((2, 2, 0.5), "invalid rational row cap"),
        ((True, 2, Q(1, 2)), "dimension outside 1..128"),
        ((2, 2, Q(1, 2 ** 40)), "row-cap bit budget exceeded"),
    ):
        count += rejects(lambda: envelope(*args), message)
    star = [[Q(1, 2), Q(0), Q(0)] for _ in range(3)]
    count += rejects(lambda: admitted(star, 2, Q(1, 2)), "column cap exceeded")
    count += rejects(lambda: admitted([[Q(3, 4)]], 2, Q(1, 2)),
                     "row cap exceeded")
    count += rejects(lambda: admitted([[Q(0), Q(0)]], 2, Q(1, 2)),
                     "nonsquare matrix")
    count += rejects(lambda: admitted([[0]], 2, Q(1, 2)),
                     "nonrational coefficient")
    require(sum(row[0] for row in inverse(star)) == 4, "row-only star control")
    require(envelope(3, 2, Q(1, 2)) == Q(7, 2), "strict column-cap improvement")
    require(envelope(8, 2, Q(1, 2)) == 5, "eight-vertex exact example")
    require(envelope(64, 2, Q(1, 2)) == 8, "critical logarithmic example")
    require(envelope(8, 8, Q(1, 2)) == 9, "redundant column cap")
    for m in range(2, 6):
        for height in range(0, 4):
            require(envelope(m ** height, m, Q(1, m))
                    == Q(m, m - 1) + height, "critical closed form")
    return {"rejected_inputs": count, "critical_closed_forms": 16,
            "contract_and_example_controls": 5}


def bindings():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        require((package / name).stat().st_size <= 1024 * 1024,
                "package file capacity exceeded")
        data = (package / name).read_bytes()
        require(len(data) <= 1024 * 1024, "package file capacity exceeded")
        hashes[name] = sha256(data).hexdigest()
    return hashes


def main():
    result = {"status": "PASS_COLUMN_CAPPED_RESOLVENT",
              "python": platform.python_version(),
              "exhaustive_grid": exhaustive_grid(),
              "attaining_cases": attaining_cases(), "controls": controls(),
              "package_sha256": bindings()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
