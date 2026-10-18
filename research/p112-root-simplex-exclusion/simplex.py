"""The six-piece incidence obstruction, with a literal sharp root fixture."""

from itertools import combinations

from geometry import canonical, dot, require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20}
SHAPES = (
    ((3, 4, 4), (6, 6, 6, 6, 6, 6)),
    ((2, 5, 5), (5, 6, 6, 6, 6, 6)),
)


def unequal_edges(values):
    require(len(values) == 6, "six affine vertices are required")
    return sum(a != b for a, b in combinations(values, 2))


def incidence_bound(small_cap, large_caps):
    require(type(small_cap) is int and 0 <= small_cap <= 112
            and len(large_caps) == 6
            and all(type(n) is int and 0 <= n <= 112 for n in large_caps),
            "invalid support bounds")
    large_caps = sorted(large_caps, reverse=True)
    require(small_cap + large_caps[0] < 53, "quotient basis is not certified")
    edge_cap = small_cap + sum(large_caps[:2])
    require(edge_cap < 70, "edge directions are not certified to be roots")
    lower = 15 * 53 - 9 * small_cap
    upper = 5 * sum(large_caps)
    return {"small_support_cap": small_cap, "large_support_sum_cap": sum(large_caps),
            "quotient_basis_support_cap": small_cap + large_caps[0],
            "edge_support_cap": edge_cap, "outside_edge_lower": lower,
            "outside_edge_upper": upper, "contradiction_margin": lower - upper,
            "excluded": lower > upper}


def obstruction(small, large):
    require(len(small) == 3 and len(large) == 6
            and all(type(w) is int and w in CAP for w in (*small, *large)),
            "expected three small and six bounded pieces")
    return {"small_weights": list(small), "large_weights": list(large),
            **incidence_bound(sum(CAP[w] for w in small), [CAP[w] for w in large])}


def simplex_receipt(roots, points):
    """Calibration only; the universal nine-edge bound is proved in PROOF.md."""
    vertices = [(0,) * 8]
    for i in range(1, 6):
        vertex = [0] * 8
        vertex[0], vertex[i] = -2, 2
        vertices.append(tuple(vertex))
    edges = [canonical(tuple(x - y for x, y in zip(a, b, strict=True)))
             for a, b in combinations(vertices, 2)]
    require(len(set(edges)) == 15 and all(e in roots for e in edges),
            "literal A5 root simplex")
    histogram = [0] * 16
    for point in points:
        values = [dot(point, vertex) for vertex in vertices]
        histogram[unequal_edges(values)] += 1
    require(max(i for i, n in enumerate(histogram) if n) == 9,
            "sharp nine-edge incidence control")
    return {"vertices": [list(v) for v in vertices],
            "incidence_histogram": {str(i): n for i, n in enumerate(histogram) if n},
            "maximum": 9}
