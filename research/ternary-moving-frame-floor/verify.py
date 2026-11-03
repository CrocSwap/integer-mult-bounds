#!/usr/bin/env python3
"""Exact finite premises for the moving-frame four-term COPY bound.

Produced by Nick Petalas. Apache-2.0. See README.md for predecessor credit.
"""
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import gcd
from pathlib import Path
import platform
import sys


EXPECTED = (0, 1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 7, 7)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def primitive(vector):
    divisor = gcd(*vector)
    require(divisor != 0, "zero projective direction")
    sign = next(x for x in vector if x)
    if sign < 0:
        divisor = -divisor
    return tuple(x // divisor for x in vector)


def geometry():
    ports = tuple(v for v in product((-1, 0, 1), repeat=3)
                  if next((x for x in v if x), 0) == 1)
    require(len(ports) == 13 and len(set(ports)) == 13, "port inventory")
    directions = set()
    for a, b in combinations(ports, 2):
        cross = (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2],
                 a[0]*b[1] - a[1]*b[0])
        directions.add(primitive(cross))
    rebuilt = set()
    for v in product(range(-2, 3), repeat=3):
        if not any(v) or primitive(v) != v:
            continue
        zeros = [p for p in ports if dot(p, v) == 0]
        if len(zeros) >= 2:
            rebuilt.add(v)
    require(directions == rebuilt and len(directions) == 25,
            "independent direction inventory")
    pairing = tuple(sum(1 << j for j, q in enumerate(ports)
                        if i == j or dot(p, q) == 0)
                    for i, p in enumerate(ports))
    supports = tuple(sum(1 << i for i, p in enumerate(ports) if dot(p, d))
                     for d in sorted(directions))
    require(len(set(supports)) == 25, "distinct direction supports")
    return ports, tuple(sorted(directions)), pairing, supports


def binary_rank(rows):
    require(len(rows) <= 13 and all(0 <= r < 8192 for r in rows),
            "binary matrix capacity")
    basis = [0] * 13
    for value in rows:
        for pivot in range(12, -1, -1):
            if value & (1 << pivot):
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(bool(row) for row in basis)


def column_rank(rows):
    """A separate low-pivot elimination of explicit transposed columns."""
    columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
               for j in range(13)]
    pivots = {}
    for column in columns:
        for index in range(len(rows)):
            if column & (1 << index):
                if index in pivots:
                    column ^= pivots[index]
                else:
                    pivots[index] = column
                    break
    return len(pivots)


def envelope(pairing, supports):
    require(len(pairing) == 13 and len(supports) == 25, "envelope capacity")
    result = [13] * 14
    witnesses = [None] * 14
    checks = 0
    for support in supports:
        selected = [row for i, row in enumerate(pairing) if support >> i & 1]
        for mask in range(8192):
            rows = [row & mask for row in selected]
            value = binary_rank(rows)
            require(value == column_rank(rows), "row/column rank disagreement")
            size = mask.bit_count()
            if value < result[size]:
                result[size] = value
                witnesses[size] = [support, mask]
            checks += 1
    require(tuple(result) == EXPECTED, "restriction-rank envelope")
    require(checks == 204800, "complete restriction inventory")
    return result, witnesses, checks


def support_relaxation(values):
    best = 53
    witness = None
    feasible = 0
    for sizes in product(range(1, 14), repeat=4):
        if sum(sizes) < 22:
            continue
        feasible += 1
        value = sum(values[n] for n in sizes)
        if value < best:
            best, witness = value, sizes
    require(best == 14 and witness == (1, 1, 7, 13),
            "four-term support relaxation")
    require(min(values[9:]) == 6, "three-term code support bound")
    return {"minimum": best, "witness_sizes": witness,
            "tuples_checked": 13**4, "feasible_tuples": feasible,
            "three_term_floor": 18}


def rational_rank(matrix):
    require(len(matrix) <= 13 and all(len(r) <= 13 for r in matrix),
            "rational matrix capacity")
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][column]:
                factor = rows[i][column]
                rows[i] = [x-factor*y for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def factor_cost(left, right, gram, pairing):
    require(len(left) == len(right) == 13, "factor row count")
    width = len(left[0])
    require(1 <= width <= 4 and all(len(r) == width for r in left+right),
            "one through four factors required")
    for i, j in product(range(13), repeat=2):
        require(dot(left[i], right[j]) == gram[i][j], "factorization identity")
    cost = 0
    for term in range(width):
        active = sum(1 << i for i in range(13) if right[i][term])
        rows = [pairing[i] & active for i in range(13) if left[i][term]]
        cost += binary_rank(rows)
    require(cost >= 14, "four-term theorem violated")
    return cost


def positive_fixtures(ports, pairing):
    gram = [[dot(p, q) for q in ports] for p in ports]
    require(rational_rank(gram) == 3, "Gram rank")
    require(all(dot([p[i] for p in ports], [p[j] for p in ports])
                == (9 if i == j else 0) for i, j in product(range(3), repeat=2)),
            "evaluation code Gram")
    coordinate = [list(p) for p in ports]
    costs = [factor_cost(coordinate, coordinate, gram, pairing)]
    for chosen in (0, 4, 12):
        left = [list(p) + [p[0]] for p in ports]
        right = [[p[0] - int(i == chosen), p[1], p[2], int(i == chosen)]
                 for i, p in enumerate(ports)]
        require(rational_rank(left) == 3 and rational_rank(right) == 4,
                "one-sided outside-code fixture")
        costs.append(factor_cost(left, right, gram, pairing))
        costs.append(factor_cost(right, left, gram, pairing))
    require(costs[0] == 18, "coordinate control")
    return gram, coordinate, costs


def expect_rejection(operation, message):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("ineffective rejection control: " + message)


def rejection_controls(ports, directions, pairing, supports, gram, coordinate):
    expect_rejection(lambda: primitive((0, 0, 0)), "zero direction")
    expect_rejection(lambda: binary_rank([8192]), "rank capacity")
    expect_rejection(lambda: envelope(pairing, supports[:-1]), "missing direction")
    identity = tuple(1 << i for i in range(13))
    expect_rejection(lambda: envelope(identity, supports), "changed pairing")
    lowered = list(EXPECTED)
    lowered[13] = 6
    expect_rejection(lambda: support_relaxation(lowered), "underpriced envelope")
    bad = [r.copy() for r in coordinate]
    bad[0][0] += 1
    expect_rejection(lambda: factor_cost(bad, coordinate, gram, pairing), "bad identity")
    five = [list(p) + [0, 0] for p in ports]
    expect_rejection(lambda: factor_cost(five, five, gram, pairing), "five factors")
    require(binary_rank([3, 5, 6]) == 2 and
            rational_rank([[1, 1, 0], [1, 0, 1], [0, 1, 1]]) == 3,
            "binary tariff versus rational scalar rank")
    require(all(sum(dot(p, d) == 0 for p in ports) >= 2 for d in directions),
            "direction intersection condition")
    return 7


def main():
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    ports, directions, pairing, supports = geometry()
    values, witnesses, checked = envelope(pairing, supports)
    relaxation = support_relaxation(values)
    gram, coordinate, costs = positive_fixtures(ports, pairing)
    controls = rejection_controls(ports, directions, pairing, supports, gram, coordinate)
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    root = Path(__file__).resolve().parent
    receipt = {"status": "PASS_TERNARY_MOVING_FRAME_FLOOR", "claim_type": "scoped proof",
               "ports": ports, "directions": directions, "support_sizes": sorted(set(
                   mask.bit_count() for mask in supports)), "rank_envelope": values,
               "envelope_witnesses": witnesses, "restrictions_checked": checked,
               "relaxation": relaxation, "fixture_costs": costs,
               "rejected_controls": controls, "python": platform.python_version(),
               "source_sha256": {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
                                 for name in names}}
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_TERNARY_MOVING_FRAME_FLOOR four_term_cost>=14 three_term_cost>=18")


if __name__ == "__main__":
    main()
