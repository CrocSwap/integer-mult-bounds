"""Exact E8/P112 geometry; coordinates follow PR3162's retained convention.

Root and label reconstruction derive from Nick Petalas's PR3161/PR3162,
with the E8/P112 lineage retained in SOURCES.json. Apache-2.0.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm

SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def canonical(row):
    return max(tuple(row), tuple(-x for x in row))


def primitive(row):
    denominator = lcm(*(x.denominator for x in row))
    integers = tuple(int(x * denominator) for x in row)
    divisor = gcd(*integers)
    require(divisor != 0, "zero projective direction")
    return canonical(tuple(x // divisor for x in integers))


def root_lines():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[j] = 2, sign
            roots.add(canonical(row))
    for row in product((-1, 1), repeat=8):
        if sum(x == -1 for x in row) % 2 == 0:
            roots.add(canonical(row))
    require(len(roots) == 120, "E8 root-line count")
    return tuple(sorted(roots))


def frame_lines():
    frame = []
    for i in range(0, 8, 2):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[i + 1] = 2, sign
            frame.append(canonical(row))
    return tuple(frame)


def solve(matrix, rhs):
    """Exact eight-dimensional elimination, also used by the chamber check."""
    require(len(matrix) == len(rhs) == 8, "linear-system dimension")
    rows = [[Fraction(x) for x in row] + [Fraction(y)]
            for row, y in zip(matrix, rhs, strict=True)]
    require(all(len(row) == 9 for row in rows), "linear-system row dimension")
    for col in range(8):
        pivot = next((i for i in range(col, 8) if rows[i][col]), None)
        require(pivot is not None, "singular linear system")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(8):
            if i != col:
                scale = rows[i][col]
                rows[i] = [x - scale * y
                           for x, y in zip(rows[i], rows[col], strict=True)]
    return tuple(row[8] for row in rows)


def root_data():
    roots, frame = root_lines(), frame_lines()
    points = tuple(row for row in roots if row not in frame)
    matrix = tuple(zip(*SIMPLE, strict=True))
    coordinates = tuple(solve(matrix, row) for row in roots)
    require(all(x.denominator == 1 for row in coordinates for x in row),
            "nonintegral simple-root coordinates")
    by_root = dict(zip(roots, coordinates, strict=True))
    labels = tuple(1 | sum((int(x) % 2) << (i + 1)
                          for i, x in enumerate(by_root[row])) for row in points)
    require(len(points) == len(set(labels)) == 112, "P112 inventory")
    require(all(0 < x < 512 and x & 1 for x in labels), "odd binary labels")
    require(all(sum(r[i] * r[j] for r in points) == 112 * (i == j)
                for i in range(8) for j in range(8)), "P112 spans eight dimensions")
    return roots, points, labels, coordinates


def chamber_receipt(roots, points, coordinates):
    for root in roots:
        for simple in SIMPLE:
            pairing = dot(root, simple)
            require(dot(simple, simple) == 8 and pairing % 4 == 0,
                    "simple reflection normalization")
            reflected = canonical(tuple(x - (pairing // 4) * y
                                        for x, y in zip(root, simple, strict=True)))
            require(reflected in roots, "root system is not reflection closed")
    require(all(all(x >= 0 for x in c) or all(x <= 0 for x in c)
                for c in coordinates), "simple system positivity")
    six_counts = [sum(all(c[i] == 0 for i in omitted) for c in coordinates)
                  for omitted in combinations(range(8), 2)]
    rays = [primitive(solve(SIMPLE, [int(i == j) for i in range(8)]))
            for j in range(8)]
    ray_zeros = [sum(dot(h, r) == 0 for r in roots) for h in rays]
    require(max(six_counts) == 36, "rank-six parabolic cap")
    require(ray_zeros == [42, 28, 22, 14, 16, 23, 37, 63], "chamber rays")
    root_directions = {primitive(tuple(map(Fraction, r))) for r in roots}
    require(rays[7] in root_directions, "qualifying ray is not a root")
    support_sizes = [sum(dot(r, t) != 0 for t in points) for r in roots]
    require(sorted(support_sizes) == [53] * 112 + [56] * 8, "root support sizes")
    # These finite facts support the Weyl-chamber proof in PROOF.md.
    return {"simple_reflection_checks": 960,
            "rank_six_parabolic_counts": six_counts, "ray_zero_counts": ray_zeros,
            "root_support_histogram": {"53": 112, "56": 8}}


def root_plane_receipt(roots):
    """Every third root line in a root plane is the A2 sum/difference."""
    require(len(roots) == len(set(roots)) == 120
            and all(len(r) == 8 and dot(r, r) == 8 for r in roots),
            "normalized root-plane input")
    gram = tuple(tuple(dot(a, b) for b in roots) for a in roots)
    histogram = {2: 0, 3: 0}
    for i, j in combinations(range(120), 2):
        d = gram[i][j]
        require(d in (-4, 0, 4), "nonparallel root inner product")
        in_plane = []
        for k in range(120):
            x, y = gram[i][k], gram[j][k]
            determinant = 512 + 2 * d * x * y - 8 * (d*d + x*x + y*y)
            if determinant == 0:
                in_plane.append(k)
        expected = {i, j}
        if d:
            third = canonical(tuple(a - (d // 4) * b
                                    for a, b in zip(roots[i], roots[j], strict=True)))
            require(third in roots, "missing A2 root")
            expected.add(roots.index(third))
        require(set(in_plane) == expected, "unexpected third root line")
        histogram[len(in_plane)] += 1
    return {str(k): v for k, v in histogram.items()}


def flat_capacity(labels, dimension):
    require(dimension in (5, 6), "only five/six-flat capacities are supported")
    require(len(labels) == len(set(labels)) == 112
            and all(type(x) is int and 0 < x < 512 and x & 1 for x in labels),
            "invalid P112 labels")
    all_lines = (1 << 112) - 1
    kernels = tuple(all_lines ^ sum(1 << i for i, label in enumerate(labels)
                                   if (label & x).bit_count() & 1) for x in range(512))
    histogram = [0] * 113
    annihilator_dimension = 9 - dimension
    for pivots in combinations(range(9), annihilator_dimension):
        row_kernels = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            rows = tuple((1 << pivot) | sum(((code >> i) & 1) << col
                                           for i, col in enumerate(free))
                         for code in range(1 << len(free)))
            row_kernels.append(tuple(kernels[row] for row in rows))
        for chosen in product(*row_kernels):
            mask = all_lines
            for row in chosen:
                mask &= row
            histogram[mask.bit_count()] += 1
    expected = {5: (3309747, 12), 6: (788035, 20)}[dimension]
    require(sum(histogram) == expected[0], "incomplete annihilator census")
    maximum = max(i for i, n in enumerate(histogram) if n)
    require(maximum == expected[1], "flat capacity changed")
    return {"dimension": dimension, "subspaces": sum(histogram), "maximum": maximum,
            "histogram": {str(i): n for i, n in enumerate(histogram) if n}}
