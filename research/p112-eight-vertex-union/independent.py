"""Separate Gram, integer-rank, 3+3 clique and set-union checks.

Adapted from Nick Petalas's PR3176 independent.py. Apache-2.0.
Root reconstruction and written classification premises remain shared.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import gcd

from vendor.geometry import require, root_lines

A = (1, 0, 1, 0, 1, 0, 1, 0)


def line(row):
    divisor = gcd(*row)
    require(divisor != 0, "zero line")
    values = tuple(x // divisor for x in row)
    return values if next(x for x in values if x) > 0 else tuple(-x for x in values)


def vertices_and_graph():
    extra = {
        line(tuple(signs[i // 2] if i % 2 == choices[i // 2] else 0 for i in range(8)))
        for choices in product(range(2), repeat=4)
        for signs in product((-1, 1), repeat=4)
    }
    directions = tuple(sorted({line(r) for r in root_lines()} | extra))
    require(len(directions) == 248 and len(extra) == 128, "independent alphabet")
    vertices = set()
    for u, v in combinations(directions, 2):
        uu, uv, vv = inner(u, u), inner(u, v), inner(v, v)
        ua, va = inner(u, A), inner(v, A)
        determinant = uu * vv - uv * uv
        require(determinant > 0, "parallel alphabet rays")
        s = Fraction(ua * vv - va * uv, determinant)
        t = Fraction(va * uu - ua * uv, determinant)
        if s and t and all(s * u[i] + t * v[i] == A[i] for i in range(8)):
            for coefficient, direction in ((s, u), (t, v)):
                doubled = tuple(2 * coefficient * x for x in direction)
                require(
                    all(x.denominator == 1 for x in doubled), "non-half-integral vertex"
                )
                vertices.add(tuple(int(x) for x in doubled))
    require(len(vertices) == 58, "independent vertex inventory")
    vertices, allowed = tuple(sorted(vertices)), set(directions)
    adjacency = [0] * 58
    for i, j in combinations(range(58), 2):
        if line(tuple(vertices[i][k] - vertices[j][k] for k in range(8))) in allowed:
            adjacency[i] += 1 << j
            adjacency[j] += 1 << i
    return vertices, tuple(adjacency)


def inner(u, v):
    return sum(u[i] * v[i] for i in range(8))


def split_cliques(adjacency):
    require(len(adjacency) == 58, "independent graph domain")
    triples = tuple(
        ids
        for ids in combinations(range(58), 3)
        if all(adjacency[i] >> j & 1 for i, j in combinations(ids, 2))
    )
    require(len(triples) == 2114, "three-clique census")
    masks = tuple(sum(1 << i for i in ids) for ids in triples)
    result = []
    for first in triples:
        common = adjacency[first[0]] & adjacency[first[1]] & adjacency[first[2]]
        for second, mask in zip(triples, masks, strict=True):
            if first[-1] < second[0] and mask & common == mask:
                result.append(first + second)
    require(len(result) == len(set(result)) == 9737, "3+3 clique coverage")
    return result


def integer_rank(rows):
    require(
        1 <= len(rows) <= 8 and all(len(row) == 8 for row in rows), "rank dimensions"
    )
    matrix, rank = [list(row) for row in rows], 0
    for column in range(8):
        selected = next((i for i in range(rank, len(rows)) if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for i in range(rank + 1, len(rows)):
            if matrix[i][column]:
                a, b = matrix[rank][column], matrix[i][column]
                matrix[i] = [
                    a * x - b * y for x, y in zip(matrix[i], matrix[rank], strict=True)
                ]
                divisor = gcd(*matrix[i])
                if divisor:
                    matrix[i] = [x // divisor for x in matrix[i]]
                require(
                    all(abs(x) < 1 << 128 for x in matrix[i]), "integer rank capacity"
                )
        rank += 1
    return rank


def mixed_census(vertices, adjacency, points):
    ranks, bounds = Counter(), Counter()
    for ids in split_cliques(adjacency):
        rows = (tuple(2 * x for x in A), *(vertices[i] for i in ids))
        rank = integer_rank(rows)
        ranks[rank] += 1
        if rank == 7:
            costs = []
            for point in points:
                values = [0] + [inner(point, row) for row in rows]
                costs.append(8 - max(values.count(x) for x in values))
            bounds[sum(sorted(costs)[:80])] += 1
    return dict(ranks), dict(bounds)


def union_maximum(fours, fives, costs):
    require(
        len(fours) <= 150 and len(fives) <= 150 and len(costs) == 120,
        "independent union capacity",
    )
    sets4 = [frozenset(i for i in range(120) if mask >> i & 1) for mask in fours]
    sets5 = [frozenset(i for i in range(120) if mask >> i & 1) for mask in fives]
    best = 0
    for b, c in combinations_with_replacement(sets5, 2):
        pair = b | c
        pair_cost = sum(costs[i] for i in pair)
        for a in sets4:
            best = max(best, pair_cost + sum(costs[i] for i in a.difference(pair)))
    return best
