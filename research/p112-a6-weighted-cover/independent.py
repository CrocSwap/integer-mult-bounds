"""Separate Gram-intersection, 2+3 clique, integer-rank and support check.

Adapted from Nick Petalas's PR3176 independent checker. It shares root
reconstruction and source binding, but not the primary graph, clique, rank,
or coordinate-multiplicity algorithms. Apache-2.0.
"""

import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd

from vendor.geometry import frame_lines, require, root_lines
from verify import PACKAGE, bind_sources, graph_digest, read_bytes

A = (1, 0, 1, 0, 1, 0, 1, 0)


def line(row):
    divisor = gcd(*row)
    require(divisor != 0, "zero projective line")
    values = tuple(x // divisor for x in row)
    return values if next(x for x in values if x) > 0 else tuple(-x for x in values)


def inner(u, v):
    return sum(u[i] * v[i] for i in range(8))


def direction_inventory():
    extra = {
        line(tuple(signs[i // 2] if i % 2 == choices[i // 2] else 0 for i in range(8)))
        for choices in product(range(2), repeat=4)
        for signs in product((-1, 1), repeat=4)
    }
    directions = tuple(sorted({line(r) for r in root_lines()} | extra))
    require(len(extra) == 128 and len(directions) == 248, "independent alphabet")
    return directions


def gram_vertices(directions):
    require(len(directions) == len(set(directions)) == 248, "Gram alphabet inventory")
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
                require(all(x.denominator == 1 for x in doubled), "non-half-integral point")
                vertices.add(tuple(int(x) for x in doubled))
    require(len(vertices) == 58, "independent anchored vertices")
    return tuple(sorted(vertices))


def graph(vertices, directions):
    require(len(vertices) == 58 and len(directions) == 248, "graph inventory")
    allowed = set(directions)
    adjacency = [0] * 58
    for i, j in combinations(range(58), 2):
        if line(tuple(vertices[i][k] - vertices[j][k] for k in range(8))) in allowed:
            adjacency[i] += 1 << j
            adjacency[j] += 1 << i
    require(sum(row.bit_count() for row in adjacency) == 1190, "independent edge count")
    return tuple(adjacency)


def split_cliques(adjacency):
    require(len(adjacency) == 58, "clique graph dimension")
    pairs = [ij for ij in combinations(range(58), 2) if adjacency[ij[0]] >> ij[1] & 1]
    triples = [ijk for ijk in combinations(range(58), 3)
               if all(adjacency[i] >> j & 1 for i, j in combinations(ijk, 2))]
    require(len(pairs) == 595 and len(triples) == 2114, "2/3 clique inventory")
    masks = [(indices, sum(1 << i for i in indices)) for indices in triples]
    result = []
    for pair in pairs:
        common = adjacency[pair[0]] & adjacency[pair[1]]
        for triple, mask in masks:
            if pair[-1] < triple[0] and mask & common == mask:
                result.append(pair + triple)
    require(len(result) == len(set(result)) == 7350, "2+3 clique coverage")
    return result


def integer_rank(rows):
    size = len(rows)
    require(1 <= size <= 8 and all(len(row) == 8 for row in rows), "rank dimensions")
    matrix = [list(row) for row in rows]
    rank = 0
    for column in range(8):
        selected = next((i for i in range(rank, size) if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for i in range(rank + 1, size):
            if matrix[i][column]:
                a, b = matrix[rank][column], matrix[i][column]
                matrix[i] = [a * x - b * y
                             for x, y in zip(matrix[i], matrix[rank], strict=True)]
                divisor = gcd(*matrix[i])
                if divisor:
                    matrix[i] = [x // divisor for x in matrix[i]]
                require(all(abs(x) < 1 << 128 for x in matrix[i]), "integer rank capacity")
        rank += 1
    return rank


def census(vertices, adjacency):
    points = tuple(r for r in root_lines() if r not in frame_lines())
    anchor = tuple(2 * x for x in A)
    ranks, bounds = Counter(), Counter()
    for indices in split_cliques(adjacency):
        rows = (anchor, *(vertices[i] for i in indices))
        rank = integer_rank(rows)
        ranks[rank] += 1
        if rank != 6:
            continue
        costs = []
        for point in points:
            values = [0] + [inner(point, row) for row in rows]
            costs.append(7 - max(values.count(x) for x in values))
        # Remove the 32 largest entries without the primary sorting routine.
        remaining, removed = Counter(costs), 32
        for cost in range(6, -1, -1):
            take = min(remaining[cost], removed)
            remaining[cost] -= take
            removed -= take
        require(removed == 0, "deletion capacity exhausted")
        bounds[sum(cost * count for cost, count in remaining.items())] += 1
    return dict(sorted(ranks.items())), dict(sorted(bounds.items()))


def root_fixture():
    roots = root_lines()
    star = tuple(tuple(2 * (j == i) - 2 * (j == 7) for j in range(8)) for i in range(6))
    require(all(line(v) in {line(r) for r in roots} for v in star), "fixture root membership")
    require(integer_rank(star) == 6, "fixture rank")
    require(all(inner(a, b) == 4 for a, b in combinations(star, 2)), "fixture root star")
    costs = []
    for root in roots:
        values = [0] + [inner(root, v) for v in star]
        costs.append(7 - max(values.count(v) for v in values))
    require(Counter(costs) == {0: 1, 1: 21, 2: 63, 3: 35}, "independent A6 spectrum")
    require(sum(costs) - 35 * 3 - 5 * 2 == 137, "independent A6 losing control")
    return dict(sorted(Counter(costs).items()))


def main():
    bind_sources()
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    directions = direction_inventory()
    vertices = gram_vertices(directions)
    adjacency = graph(vertices, directions)
    require(graph_digest(vertices, adjacency) == expected["graph"]["sha256"],
            "independent graph differs")
    ranks, bounds = census(vertices, adjacency)
    require({str(k): v for k, v in ranks.items()} == expected["mixed"]["ranks"],
            "independent exact ranks differ")
    require({str(k): v for k, v in bounds.items()} == expected["mixed"]["bounds"],
            "independent support histogram differs")
    require({str(k): v for k, v in root_fixture().items()} == expected["all_root"]["spectrum"],
            "independent root spectrum differs")
    print("PASS_INDEPENDENT_A6_MIXED cliques=7350 rank6=3360 mixed=142")


if __name__ == "__main__":
    main()
