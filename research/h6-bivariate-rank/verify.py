#!/usr/bin/env python3
"""Exact support certificate for the H6 bivariate fitting-kernel theorem.

Produced by Nick Petalas. Apache-2.0.
The five E8 projectors and their ranks are cited from Ross Richardson PR3649.
This program proves the new finite support optimization, not those premises.
"""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
RANKS = (1, 8, 35, 112, 84)
SECTORS = tuple((i, j) for i, j in product(range(5), repeat=2)
                if (i in (1, 3)) != (j in (1, 3)))
WEIGHTS = tuple(RANKS[i] * RANKS[j] for i, j in SECTORS)
CONSTRAINTS = ((2, 2), (2, 0), (0, 2), (2, -2), (1, 1), (1, -1))
TARGET = (1, 0, 0, 0, 0, 0)
CUBIC = (-390, 60, -390, 90, 0, 90, 0, 60, 0, 0, 0, 0)
SOURCE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def projector(i, s):
    """Entry of the cited projector on roots of ordinary inner product s."""
    return (Q(1, 240), Q(s, 60), Q(s * s, 24) - Q(1, 48),
            Q(int(s == 2) - int(s == -2), 2) - Q(s, 60),
            Q(int(abs(s) == 2), 2) - Q(s * s, 24) + Q(1, 60))[i]


def entry(coefficients, s, t):
    return sum(value * projector(i, s) * projector(j, t)
               for value, (i, j) in zip(coefficients, SECTORS, strict=True))


def matrix_rank(rows):
    """Bounded rational elimination, at most 25 rows and 13 columns."""
    require(len(rows) <= 25, "too many rows")
    width = len(rows[0]) if rows else 0
    require(width <= 13 and all(len(row) == width for row in rows), "bad row shape")
    work = [[Q(value) for value in row] for row in rows]
    rank = 0
    for column in range(width):
        pivot = next((r for r in range(rank, len(work)) if work[r][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        divisor = work[rank][column]
        work[rank] = [value / divisor for value in work[rank]]
        for row in range(rank + 1, len(work)):
            factor = work[row][column]
            if factor:
                work[row] = [x - factor * y
                             for x, y in zip(work[row], work[rank], strict=True)]
        rank += 1
        if rank == len(work):
            break
    return rank


def constraint_matrix():
    return [[projector(i, s) * projector(j, t) for i, j in SECTORS]
            for s, t in CONSTRAINTS]


def feasible(matrix, target, active):
    restricted = [[row[j] for j in active] for row in matrix]
    augmented = [row + [Q(value)]
                 for row, value in zip(restricted, target, strict=True)]
    return matrix_rank(restricted) == matrix_rank(augmented)


def determinant(rows):
    require(len(rows) == 6 and all(len(row) == 6 for row in rows),
            "expected six-square")
    work = [[Q(value) for value in row] for row in rows]
    result = Q(1)
    for column in range(6):
        pivot = next((r for r in range(column, 6) if work[r][column]), None)
        if pivot is None:
            return Q(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        value = work[column][column]
        result *= value
        for row in range(column + 1, 6):
            factor = work[row][column] / value
            work[row] = [a - factor * b
                         for a, b in zip(work[row], work[column], strict=True)]
    return result


def support_optimization(matrix):
    histogram = Counter()
    optimum = sum(WEIGHTS) + 1
    winners = []
    feasible_count = 0
    for mask in range(1 << len(SECTORS)):
        active = tuple(j for j in range(len(SECTORS)) if mask >> j & 1)
        if not feasible(matrix, TARGET, active):
            continue
        feasible_count += 1
        cost = sum(WEIGHTS[j] for j in active)
        histogram[cost] += 1
        if cost < optimum:
            optimum, winners = cost, [mask]
        elif cost == optimum:
            winners.append(mask)
    cubic_mask = sum(1 << j for j, value in enumerate(CUBIC) if value)
    require(optimum == 800 and winners == [cubic_mask], "rank optimum/support differs")
    active = tuple(j for j, value in enumerate(CUBIC) if value)
    require(matrix_rank([[row[j] for j in active] for row in matrix]) == len(active),
            "minimum support does not determine a unique kernel")
    return {"supports_checked": 4096, "feasible_supports": feasible_count,
            "minimum_rank": optimum, "unique_minimum_support": cubic_mask,
            "feasible_cost_histogram": {str(cost): count
                                        for cost, count in sorted(histogram.items())}}


def low_family(x, y):
    """All solutions after excluding the four sectors of weight at least 3920."""
    return (14 * y - 390, 60 - 2 * y, 30 - 7 * x, x + 30,
            30 - x / 2, 90 - 2 * y, 0, x, 0, 0, y, 0)


def analytic_certificate(matrix):
    low = tuple(j for j, weight in enumerate(WEIGHTS) if weight < 3920)
    require(len(low) == 8 and matrix_rank(matrix) == 6, "constraint rank differs")
    require(matrix_rank([[row[j] for j in low] for row in matrix]) == 6,
            "low-family dimension differs")
    minor = [[57600 * row[j] for j in (0, 1, 2, 3, 5, 7)] for row in matrix]
    require(determinant(minor) == -94371840000, "displayed minor differs")
    # Affine identities at zero and two independent directions prove every x,y.
    for x, y in ((Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))):
        values = low_family(x, y)
        require(tuple(entry(values, s, t) for s, t in CONSTRAINTS) == TARGET,
                "affine family violates fitting")
    require(low_family(Q(60), Q(0)) == CUBIC, "cubic parameter differs")
    x_values = (Q(0), Q(-30), Q(30, 7), Q(60), Q(1))
    y_values = (Q(0), Q(30), Q(45), Q(195, 7), Q(1))
    # All possible zero collisions, plus one generic stratum, in each parameter.
    x_costs = [sum(WEIGHTS[j] for j in (2, 3, 4, 7) if low_family(x, Q(0))[j])
               for x in x_values]
    y_costs = [sum(WEIGHTS[j] for j in (0, 1, 5, 10) if low_family(Q(60), y)[j])
               for y in y_values]
    require(min(x_costs) == min(y_costs) == 400, "one-parameter minimum differs")
    require(x_costs.count(400) == y_costs.count(400) == 1, "minimum not unique")
    return {"constraint_rank": 6, "low_family_dimension": 2,
            "scaled_minor_determinant": -94371840000,
            "x_stratum_ranks": x_costs, "y_stratum_ranks": y_costs}


def value_checks():
    values = (-2, -1, 0, 1, 2)
    transform = [[projector(i, s) * projector(j, t) for i, j in SECTORS]
                 for s, t in product(values, repeat=2)]
    require(matrix_rank(transform) == 12, "tensor entries do not span the odd family")
    parity_checks = 0
    for k in range(12):
        vector = tuple(int(j == k) for j in range(12))
        for s, t in product(values, repeat=2):
            require(entry(vector, -s, -t) == -entry(vector, s, t), "wrong parity")
            parity_checks += 1
    for s, t in product(values, repeat=2):
        require(entry(CUBIC, s, t) == Q((s + t)**3 - 4 * (s + t), 48),
                "minimum kernel is not the inherited cubic")
        if (s + t) % 2 == 0:
            expected = 1 if (s, t) == (2, 2) else -1 if (s, t) == (-2, -2) else 0
            require(entry(CUBIC, s, t) == expected, "cubic fitting failure")
    return {"entry_basis_rank": 12, "parity_checks": parity_checks, "cubic_entries": 25}


def controls(matrix):
    # A rank-eight projector is cheaper but fails the required zero at (0,2).
    cheap = [Q(0)] * 12
    cheap[0] = Q(1) / (projector(0, 2) * projector(1, 2))
    require(entry(cheap, 2, 2) == 1 and entry(cheap, 2, 0) == 0
            and entry(cheap, 0, 2) != 0, "cheap nonfitting control ineffective")
    for j, value in enumerate(CUBIC):
        if not value:
            continue
        mutant = list(CUBIC)
        mutant[j] = 0
        require(tuple(entry(mutant, s, t) for s, t in CONSTRAINTS) != TARGET,
                "omitted minimum sector was accepted")
    swapped = list(CUBIC)
    swapped[0], swapped[2] = 0, -780
    require(entry(swapped, 2, 2) == 1
            and tuple(entry(swapped, s, t) for s, t in CONSTRAINTS) != TARGET,
            "nonsymmetric factor-weight control ineffective")
    require(not feasible(matrix, TARGET, (0,)), "rank-eight support incorrectly fits")
    require(not feasible(matrix, TARGET, ()), "zero support incorrectly fits")
    for malformed in ([[0] * 14], [[1], []], [[0]] * 26):
        try:
            matrix_rank(malformed)
        except ValueError:
            continue
        raise ValueError("invalid matrix shape accepted")
    return 13


def compute_receipt():
    matrix = constraint_matrix()
    result = {"claim_type": "scoped proof with exact finite support certificate",
              "sectors": [list(pair) for pair in SECTORS],
              "sector_ranks": list(WEIGHTS),
              "minimum_signed_eigenvalues": list(CUBIC)}
    result.update(value_checks())
    result.update(analytic_certificate(matrix))
    result.update(support_optimization(matrix))
    result["rejection_controls"] = controls(matrix)
    result["sha256"] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                        for name in SOURCE_FILES}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path,
                        help="exclusively create an external receipt")
    args = parser.parse_args()
    result = compute_receipt()
    if args.emit_to is not None:
        output = args.emit_to.resolve()
        require(not output.is_relative_to(HERE.parents[1]),
                "receipt output must be external")
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        with output.open("x", encoding="utf-8") as stream:
            require(stream.write(payload) == len(payload), "incomplete receipt write")
    else:
        receipt_path = HERE / "RESULT.json"
        require(receipt_path.stat().st_size <= 1024 * 1024,
                "receipt exceeds size bound")
        expected = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(json.dumps(result, sort_keys=True) ==
                json.dumps(expected, sort_keys=True),
                "generated receipt differs")
    print("PASS_H6_BIVARIATE_RANK minimum=800 unique=cubic supports=4096")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
