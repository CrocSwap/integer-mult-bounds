"""Separate Gram-intersection, integer-rank and 3+4 clique check.

This reuses only the pinned E8 root reconstruction and source binding.
It does not call the primary graph, clique, rank or support algorithms.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd

from vendor.geometry import frame_lines, require, root_lines
from verify import PACKAGE, bind_sources, read_bytes

A = (1, 0, 1, 0, 1, 0, 1, 0)


def line(row):
    divisor = gcd(*row)
    require(divisor != 0, "zero line")
    values = tuple(x // divisor for x in row)
    return values if next(x for x in values if x) > 0 else tuple(-x for x in values)


def direction_inventory():
    roots = root_lines()
    extra = {
        line(tuple(signs[i // 2] if i % 2 == choices[i // 2] else 0 for i in range(8)))
        for choices in product(range(2), repeat=4)
        for signs in product((-1, 1), repeat=4)
    }
    directions = tuple(sorted({line(r) for r in roots} | extra))
    require(len(extra) == 128 and len(directions) == 248, "independent alphabet")
    return directions


def inner(u, v):
    return sum(u[i] * v[i] for i in range(8))


def gram_vertices(directions):
    vertices = set()
    for u, v in combinations(directions, 2):
        uu, uv, vv = inner(u, u), inner(u, v), inner(v, v)
        ua, va = inner(u, A), inner(v, A)
        determinant = uu * vv - uv * uv
        require(determinant > 0, "parallel alphabet rays")
        s, t = (
            Fraction(ua * vv - va * uv, determinant),
            Fraction(va * uu - ua * uv, determinant),
        )
        if s and t and all(s * u[i] + t * v[i] == A[i] for i in range(8)):
            for coefficient, direction in ((s, u), (t, v)):
                doubled = tuple(2 * coefficient * x for x in direction)
                require(
                    all(x.denominator == 1 for x in doubled), "non-half-integral point"
                )
                vertices.add(tuple(int(x) for x in doubled))
    require(len(vertices) == 58, "independent anchored vertex inventory")
    return tuple(sorted(vertices))


def graph(vertices, directions):
    allowed = set(directions)
    adjacency = [0] * 58
    for i, j in combinations(range(58), 2):
        if line(tuple(vertices[i][k] - vertices[j][k] for k in range(8))) in allowed:
            adjacency[i] += 1 << j
            adjacency[j] += 1 << i
    return tuple(adjacency)


def split_cliques(adjacency):
    groups = {}
    for size in (3, 4):
        groups[size] = []
        for indices in combinations(range(58), size):
            if all(adjacency[i] >> j & 1 for i, j in combinations(indices, 2)):
                groups[size].append(indices)
    require(len(groups[3]) == 2114 and len(groups[4]) == 4459, "3/4 clique census")
    quads = [(indices, sum(1 << i for i in indices)) for indices in groups[4]]
    result = []
    for triple in groups[3]:
        common = adjacency[triple[0]] & adjacency[triple[1]] & adjacency[triple[2]]
        for quad, mask in quads:
            if triple[-1] < quad[0] and mask & common == mask:
                result.append(triple + quad)
    require(len(result) == len(set(result)) == 10520, "3+4 clique coverage")
    return result


def integer_rank(rows):
    matrix = [list(row) for row in rows]
    require(len(rows) == 8 and all(len(row) == 8 for row in rows), "rank dimensions")
    rank = 0
    for column in range(8):
        selected = next((i for i in range(rank, 8) if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for i in range(rank + 1, 8):
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


def census(vertices, adjacency):
    points = tuple(r for r in root_lines() if r not in frame_lines())
    anchor = tuple(2 * x for x in A)
    ranks, bounds = Counter(), Counter()
    for indices in split_cliques(adjacency):
        rows = (anchor, *(vertices[i] for i in indices))
        rank = integer_rank(rows)
        ranks[rank] += 1
        if rank == 8:
            costs = []
            for point in points:
                values = [0] + [inner(point, row) for row in rows]
                costs.append(9 - max(values.count(x) for x in values))
            bounds[sum(sorted(costs)[:80])] += 1
    return dict(sorted(ranks.items())), dict(sorted(bounds.items()))


def main():
    bind_sources()
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    directions = direction_inventory()
    vertices = gram_vertices(directions)
    adjacency = graph(vertices, directions)
    raw = json.dumps(
        {"vertices_doubled": vertices, "adjacency": adjacency},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    require(
        hashlib.sha256(raw).hexdigest() == expected["graph"]["sha256"],
        "independent graph differs",
    )
    ranks, bounds = census(vertices, adjacency)
    require(
        {str(k): v for k, v in ranks.items()} == expected["mixed"]["rank_histogram"],
        "independent exact ranks differ",
    )
    require(
        {str(k): v for k, v in bounds.items()}
        == expected["mixed"]["support_histogram"],
        "independent support histogram differs",
    )
    print(
        "PASS_INDEPENDENT_MIXED_EDGE Gram_intersections=58 split_cliques=10520 "
        "independent_rank8=608 support_lower=182"
    )


if __name__ == "__main__":
    main()
