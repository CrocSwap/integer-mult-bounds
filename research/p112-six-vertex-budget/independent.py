"""Check the six-vertex census with Gram solves, edge-pair joins and integer rank."""

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
    require(divisor != 0, "zero projective line")
    result = tuple(x // divisor for x in row)
    return max(result, tuple(-x for x in result))


def inner(u, v):
    return sum(u[i] * v[i] for i in range(8))


def inventory():
    extra = {
        line(tuple(signs[i // 2] if i % 2 == choices[i // 2] else 0 for i in range(8)))
        for choices in product(range(2), repeat=4)
        for signs in product((-1, 1), repeat=4)
    }
    directions = tuple(sorted({line(r) for r in root_lines()} | extra))
    require(len(extra) == 128 and len(directions) == 248, "direction inventory")
    return directions


def gram_vertices(directions):
    vertices = set()
    for u, v in combinations(directions, 2):
        uu, uv, vv = inner(u, u), inner(u, v), inner(v, v)
        ua, va = inner(u, A), inner(v, A)
        determinant = uu * vv - uv * uv
        require(determinant > 0, "parallel rays")
        s = Fraction(ua * vv - va * uv, determinant)
        t = Fraction(va * uu - ua * uv, determinant)
        if s and t and all(s * u[i] + t * v[i] == A[i] for i in range(8)):
            for coefficient, ray in ((s, u), (t, v)):
                row = tuple(2 * coefficient * x for x in ray)
                require(all(x.denominator == 1 for x in row), "half-integral vertex")
                vertices.add(tuple(int(x) for x in row))
    require(len(vertices) == 58, "Gram vertex count")
    return tuple(sorted(vertices))


def edges(vertices, directions):
    allowed = set(directions)
    result = []
    for i, j in combinations(range(58), 2):
        if line(tuple(vertices[i][k] - vertices[j][k] for k in range(8))) in allowed:
            result.append((i, j))
    require(len(result) == 595, "edge inventory")
    return tuple(result)


def pair_join(edge_list):
    edge_set = set(edge_list)
    result = []
    for (a, b), (c, d) in combinations(edge_list, 2):
        if b < c and all((i, j) in edge_set for i in (a, b) for j in (c, d)):
            result.append((a, b, c, d))
    require(len(result) == len(set(result)) == 4459, "2+2 clique inventory")
    return result


def integer_rank(rows):
    require(len(rows) == 5 and all(len(row) == 8 for row in rows), "rank shape")
    matrix = [list(row) for row in rows]
    rank = 0
    for column in range(8):
        selected = next((i for i in range(rank, 5) if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for i in range(rank + 1, 5):
            if matrix[i][column]:
                a, b = matrix[rank][column], matrix[i][column]
                matrix[i] = [
                    a * x - b * y for x, y in zip(matrix[i], matrix[rank], strict=True)
                ]
                divisor = gcd(*matrix[i])
                if divisor:
                    matrix[i] = [x // divisor for x in matrix[i]]
                require(all(abs(x) < 1 << 128 for x in matrix[i]), "rank integer bound")
        rank += 1
    return rank


def census(vertices, edge_list):
    points = tuple(r for r in root_lines() if r not in frame_lines())
    ranks, bounds = Counter(), Counter()
    for indices in pair_join(edge_list):
        rows = (tuple(2 * x for x in A), *(vertices[i] for i in indices))
        rank = integer_rank(rows)
        ranks[rank] += 1
        if rank == 5:
            costs = []
            for point in points:
                values = [0] + [inner(point, row) for row in rows]
                costs.append(6 - max(values.count(x) for x in values))
            bounds[sum(sorted(costs)[:82])] += 1
    return dict(sorted(ranks.items())), dict(sorted(bounds.items()))


def root_spectrum():
    # An explicit norm-eight A5 star, independent of stabilizer representatives.
    rows = []
    for j in range(1, 6):
        row = [0] * 8
        row[0], row[j] = 2, 2
        rows.append(tuple(row))
    require(integer_rank(rows) == 5, "explicit A5 rank")
    costs = []
    for point in root_lines():
        values = [0] + [inner(point, row) for row in rows]
        costs.append(6 - max(values.count(x) for x in values))
    require(Counter(costs) == {0: 4, 1: 36, 2: 60, 3: 20}, "explicit A5 spectrum")
    return sum(sorted(costs)[:82])


def main():
    bind_sources()
    receipt = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    directions = inventory()
    vertices = gram_vertices(directions)
    edge_list = edges(vertices, directions)
    require(
        [list(row) for row in vertices] == receipt["vertices_doubled"],
        "vertex equality",
    )
    adjacency = [0] * 58
    for i, j in edge_list:
        adjacency[i] |= 1 << j
        adjacency[j] |= 1 << i
    require(adjacency == receipt["adjacency"], "graph equality")
    ranks, bounds = census(vertices, edge_list)
    require(
        {str(k): v for k, v in ranks.items()} == receipt["mixed"]["rank_histogram"],
        "independent ranks",
    )
    require(
        {str(k): v for k, v in bounds.items()} == receipt["mixed"]["support_histogram"],
        "independent support bounds",
    )
    require(root_spectrum() == 120, "independent root support bound")
    print(
        "PASS_INDEPENDENT_SIX_VERTEX Gram=58 pair_join=4459 rank5=3136 "
        "mixed=121 root=120"
    )


if __name__ == "__main__":
    main()
