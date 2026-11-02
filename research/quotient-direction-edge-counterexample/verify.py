#!/usr/bin/env python3
"""Exact six-line certificate for the failed q-direction quotient bound."""

import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from math import gcd
from pathlib import Path
import sys


P = ((6, -5, 1), (-6, 8, -2), (2, -3, 1),
     (-2, 6, -2), (-10, 10, -2), (14, -16, 4))
Q = ((1, 1, 1), (1, 2, 4), (1, 3, 9),
     (2, 3, 5), (2, 5, 13), (2, 4, 10))
B = (7, 7, 7, 56, 56, 56)
SIZE = 6


def require(condition, message):
    if not condition:
        raise ValueError(message)


def direction(vector):
    require(len(vector) == 3 and all(type(x) is int for x in vector),
            "integer three-vector required")
    divisor = gcd(*vector)
    require(divisor != 0, "nonzero vector required")
    first = next(x for x in vector if x)
    return tuple(x // (divisor if first > 0 else -divisor) for x in vector)


def validate(p, q, rows):
    require(len(p) == len(q) == len(rows) == SIZE, "six lines required")
    for family in (p, q):
        require(len({direction(v) for v in family}) == SIZE,
                "projectively distinct directions required")
        require(all(all(x != 0 for x in v) for v in family),
                "full coordinate supports required")
    dots = tuple(tuple(sum(a * b for a, b in zip(x, y)) for y in q) for x in p)
    for i, row in enumerate(rows):
        require(type(row) is int and 0 <= row < 1 << SIZE, "binary row required")
        require(dots[i][i] != 0, "nonzero rational diagonal required")
        require((row >> i) & 1, "unit binary diagonal required")
        for j in range(SIZE):
            if i != j and (row >> j) & 1:
                require(dots[i][j] == 0, "inadmissible off-diagonal one")
    return dots


def binary_rank(rows):
    basis = [0] * SIZE
    result = 0
    for row in rows:
        value = row
        for pivot in range(SIZE - 1, -1, -1):
            if (value >> pivot) & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    result += 1
                    break
    return result


def rowspace_rank(rows):
    space = {0}
    for row in rows:
        space |= {x ^ row for x in tuple(space)}
    require(len(space) & (len(space) - 1) == 0, "row space size is a power of two")
    return len(space).bit_length() - 1


def edge_optimum(edges):
    best = [-1] * (1 << SIZE)
    best[0] = 0
    for mask in range(1 << SIZE):
        for last in range(SIZE):
            if (mask >> last) & 1:
                previous = mask ^ (1 << last)
                incoming = sum(((previous >> i) & 1) for i, j in edges if j == last)
                best[mask] = max(best[mask], best[previous] + incoming)
    return best[-1]


def graph_checks(edges):
    scores = Counter()
    for order in permutations(range(SIZE)):
        position = {v: i for i, v in enumerate(order)}
        scores[sum(position[i] < position[j] for i, j in edges)] += 1
    require(sum(scores.values()) == 720, "all six-vertex orders enumerated")
    require(max(scores) == edge_optimum(edges) == 9, "acyclic edge optimum nine")
    return dict(sorted(scores.items()))


def pairing_census(edges):
    require(len(edges) == 15, "fifteen admissible off-diagonal bits")
    histogram = Counter()
    for mask in range(1 << len(edges)):
        rows = [1 << i for i in range(SIZE)]
        for bit, (i, j) in enumerate(edges):
            if (mask >> bit) & 1:
                rows[i] |= 1 << j
        rank = binary_rank(rows)
        require(rank == rowspace_rank(rows), "elimination and row-space ranks agree")
        histogram[3 * rank] += 1
    require(sum(histogram.values()) == 32768, "all admissible pairings enumerated")
    require(min(histogram) == 6, "minimum coordinate-block rank cost six")
    return dict(sorted(histogram.items()))


def rejection_controls():
    cases = []
    repeated = list(Q)
    repeated[5] = tuple(2 * x for x in Q[0])
    cases.append((P, repeated, B))
    sparse = list(P)
    sparse[0] = (0, -5, 1)
    cases.append((sparse, Q, B))
    zero = list(Q)
    zero[0] = (0, 0, 0)
    cases.append((P, zero, B))
    orthogonal = list(P)
    orthogonal[0] = (1, 1, -2)
    cases.append((orthogonal, Q, B))
    missing = list(B)
    missing[0] ^= 1
    cases.append((P, Q, missing))
    illegal = list(B)
    illegal[0] |= 1 << 3
    cases.append((P, Q, illegal))
    bad_type = list(B)
    bad_type[0] = True
    cases.append((P, Q, bad_type))
    for p, q, rows in cases:
        try:
            validate(p, q, rows)
        except ValueError:
            continue
        raise ValueError("invalid witness accepted")
    return len(cases)


def certificate():
    dots = validate(P, Q, B)
    edges = tuple((i, j) for i in range(SIZE) for j in range(SIZE)
                  if i != j and dots[i][j] == 0)
    internal = {(i, j) for i in range(SIZE) for j in range(SIZE)
                if i != j and i // 3 == j // 3}
    require(set(edges) == internal | {(0, 4), (1, 5), (2, 3)}, "literal wild graph")
    require(binary_rank(B) == rowspace_rank(B) == 2, "attaining pairing rank two")
    orders = graph_checks(edges)
    census = pairing_census(edges)
    controls = rejection_controls()
    reduced = tuple(edge for edge in edges if edge != (0, 4))
    require(edge_optimum(reduced) == 8, "deleted cross edge changes optimum")
    require(binary_rank((1, 2, 4, 8, 16, 32)) == 6, "identity rank control")
    require(binary_rank((63,) * SIZE) == 1, "all-ones rank control")
    return {"lines": SIZE, "distinct_p_directions": SIZE, "distinct_q_directions": SIZE,
            "dot_matrix": dots, "wild_edges": edges, "pairing_rows": B,
            "minimum_cost": 6, "quotient_acyclic_edges": 9, "gap": 3,
            "order_score_histogram": orders, "pairing_cost_histogram": census,
            "orders": 720, "admissible_pairings": 32768,
            "rank_crosschecks": 32768, "controls": controls + 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = certificate()
    here = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(here.iterdir()) if p.is_file()}
    receipt = {"status": "PASS_QUOTIENT_DIRECTION_EDGE_COUNTEREXAMPLE",
               "claim_type": "finite counterexample with exact scoped proof",
               "result": result, "package_sha256": hashes,
               "python": sys.version.split()[0]}
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        require(here not in args.receipt.resolve().parents, "receipt must be outside package")
        with args.receipt.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    print(receipt["status"])
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
