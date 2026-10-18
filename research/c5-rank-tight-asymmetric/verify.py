#!/usr/bin/env python3
"""Exact physical fixtures for the rank-tight asymmetric C5 theorem.

Apache-2.0. Geometry and full-plane tariff: PR2782 and its retained sources.
The universal dimension argument is in README.md; fixtures do not prove it.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(rows):
    basis = [0] * 10
    for value in rows:
        require(type(value) is int and 0 <= value < 1024, "ten-bit binary row")
        for pivot in range(9, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(bool(value) for value in basis)


def dot(left, right):
    return (left & right).bit_count() % 2


def tariff(planes, left, right):
    sources = [q for i in range(5) if left >> i & 1 for q in planes[i]]
    targets = [q for i in range(5) if right >> i & 1 for q in planes[i]]
    rows = [sum(dot(q, r) << j for j, r in enumerate(targets)) for q in sources]
    return binary_rank(rows)


def load_planes():
    data = {}
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "input hash")
            data[pin["path"]] = raw
    require(
        set(data) == {INPUT + "DATA-PHASES.json.gz", INPUT + "MATCHING.json"},
        "two geometry inputs",
    )
    recipes = json.loads(gzip.decompress(data[INPUT + "DATA-PHASES.json.gz"]))[
        "recipes"
    ]
    labels = {row["port"]: row["q"] for row in recipes}
    require(
        len(labels) == len(recipes) == 112 and sorted(labels) == list(range(112)),
        "112 distinct scalar ports",
    )
    require(all(type(q) is int and 0 < q < 512 for q in labels.values()), "labels")
    matching = json.loads(data[INPUT + "MATCHING.json"])["matching"]
    require(
        len(matching) == 56
        and all(len(pair) == 2 for pair in matching)
        and sorted(p for pair in matching for p in pair) == list(range(112)),
        "56-plane partition",
    )
    planes = [[labels[p] for p in pair] for pair in matching]
    require(
        all(
            [[dot(q, r) for r in plane] for q in plane] == [[1, 0], [0, 1]]
            for plane in planes
        ),
        "nondegenerate orthonormal full planes",
    )
    return planes


def orthogonal(left, right):
    return all(dot(q, r) == 0 for q in left for r in right)


def cycle_order(planes, group):
    neighbors = {
        i: [j for j in group if i != j and orthogonal(planes[i], planes[j])]
        for i in group
    }
    require(all(len(value) == 2 for value in neighbors.values()), "induced C5")
    order = [min(group)]
    for _ in range(4):
        choices = [j for j in neighbors[order[-1]] if j not in order]
        require(bool(choices), "cycle walk continues")
        order.append(min(choices))
    require(order[0] in neighbors[order[-1]], "cycle closes")
    return order


def cycles(planes):
    neighbors = [
        sum(1 << j for j in range(56) if i != j and orthogonal(planes[i], planes[j]))
        for i in range(56)
    ]
    found = []
    for group in combinations(range(56), 5):
        mask = sum(1 << i for i in group)
        if all((neighbors[i] & mask).bit_count() == 2 for i in group):
            found.append(cycle_order(planes, group))
    require(len(found) == 23, "23 physical cycles")
    return found


def multiply(left, right):
    return [
        [
            sum(a * b for a, b in zip(row, column, strict=True))
            for column in zip(*right, strict=True)
        ]
        for row in left
    ]


def transpose(matrix):
    return [list(column) for column in zip(*matrix, strict=True)]


def identity(size):
    return [[Fraction(i == j) for j in range(size)] for i in range(size)]


def inverse(matrix):
    size = len(matrix)
    require(0 < size <= 10 and all(len(row) == size for row in matrix), "small square")
    rows = [
        [Fraction(x) for x in row] + tail
        for row, tail in zip(matrix, identity(size), strict=True)
    ]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        require(pivot is not None, "invertible scalar basis")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(size):
            if i != column:
                scale = rows[i][column]
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[column], strict=True)
                ]
    return [row[size:] for row in rows]


def baseline():
    rows = [[Fraction(0)] * 5 for _ in range(10)]
    for i in range(5):
        rows[2 * i + 1][i] = 1
        rows[2 * ((i + 1) % 5)][i] = 1
    return rows


def inspect_fit(planes, left, right):
    require(len(planes) == 5 and len(left) == len(right) == 10, "C5 fixture shapes")
    width = len(left[0])
    require(
        1 <= width <= 8 and all(len(row) == width for row in left + right),
        "bounded fixture term count",
    )
    matrix = multiply(left, transpose(right))
    for i in range(10):
        for j in range(10):
            if i == j or not orthogonal(planes[i // 2], planes[j // 2]):
                require(matrix[i][j] == int(i == j), "strict scalar fit")
    terms = []
    for t in range(width):
        masks = [
            sum(1 << i for i in range(5) if rows[2 * i][t] or rows[2 * i + 1][t])
            for rows in [left, right]
        ]
        require(all(masks), "nonzero scalar factors")
        shared_edges = [
            i
            for i in range(5)
            if all(mask >> i & 1 and mask >> ((i + 1) % 5) & 1 for mask in masks)
        ]
        terms.append(
            {
                "left": masks[0],
                "right": masks[1],
                "tariff": tariff(planes, *masks),
                "shared_edges": shared_edges,
            }
        )
    return {"terms": terms, "cost": sum(term["tariff"] for term in terms)}


def six_term_fixture():
    # Split one baseline source column into its two scalar entries.
    left, right = baseline(), baseline()
    for i in range(10):
        left[i].append(Fraction(0))
        right[i].append(right[i][0])
    left[2][5], left[2][0] = left[2][0], Fraction(0)
    return left, right


def build():
    planes = load_planes()
    change = identity(5)
    change[0][1], change[2][4] = Fraction(2, 3), Fraction(-3, 2)
    left = multiply(baseline(), change)
    right = multiply(baseline(), transpose(inverse(change)))
    records = []
    for cycle in cycles(planes):
        local = [planes[i] for i in cycle]
        direct = inspect_fit(local, baseline(), baseline())
        transformed = inspect_fit(local, left, right)
        split = inspect_fit(local, *six_term_fixture())
        require(direct["cost"] == split["cost"] == 20, "sharp and split fits")
        require(
            transformed["cost"] >= 20
            and all(
                term["shared_edges"] and term["tariff"] >= 4
                for term in transformed["terms"]
            ),
            "rank-tight edge certificate",
        )
        require(
            any(term["left"] != term["right"] for term in transformed["terms"]),
            "genuinely unequal support control",
        )
        require(
            any(
                term["tariff"] == 2 and not term["shared_edges"]
                for term in split["terms"]
            ),
            "six-term scope boundary",
        )
        records.append(
            {
                "cycle": cycle,
                "direct": direct,
                "asymmetric": transformed,
                "six_term_boundary": split,
            }
        )
    return {
        "schema_version": 1,
        "status": "SHARP_RANK_TIGHT_ASYMMETRIC_C5_COST_20",
        "cycle_count": len(records),
        "minimum_scalar_terms": 5,
        "five_term_cost_floor": 20,
        "cycles": records,
    }


if __name__ == "__main__":
    require(build() == json.loads((HERE / "RESULT.json").read_bytes()), "exact receipt")
    print(
        "PASS_C5_RANK_TIGHT_ASYMMETRIC cycles=23 min_terms=5 "
        "five_term_cost=20 six_term_controls=23"
    )
