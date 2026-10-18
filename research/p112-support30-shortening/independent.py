"""Separate Gram intersections, direct quadruples, integer ranks and frame orbit.

Shares only the authenticated E8 reconstruction and source-bound receipt loader.
Gram-intersection method follows Nick Petalas/PR3176's independent check.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd

# Importing verify authenticates sources and locates the inherited geometry.
from verify import PACKAGE, read_bytes, require

# isort: split
from vendor.geometry import SIMPLE, canonical, frame_lines, root_lines

ANCHOR = (1, 0, 1, 0, 1, 0, 1, 0)


def inner(a, b):
    return sum(a[i] * b[i] for i in range(8))


def line(row):
    divisor = gcd(*row)
    require(divisor > 0, "zero projective vector")
    return canonical(tuple(x // divisor for x in row))


def gram_vertices():
    roots = root_lines()
    extra = {
        line(
            tuple(signs[i // 2] if i % 2 == positions[i // 2] else 0 for i in range(8))
        )
        for signs in product((-1, 1), repeat=4)
        for positions in product(range(2), repeat=4)
    }
    directions = tuple(sorted({line(r) for r in roots} | extra))
    require(len(extra) == 128 and len(directions) == 248, "independent alphabet")
    vertices = set()
    for u, v in combinations(directions, 2):
        uu, uv, vv = inner(u, u), inner(u, v), inner(v, v)
        ua, va = inner(u, ANCHOR), inner(v, ANCHOR)
        determinant = uu * vv - uv * uv
        require(determinant > 0, "parallel projective rays")
        s = Fraction(ua * vv - va * uv, determinant)
        t = Fraction(va * uu - ua * uv, determinant)
        if s and t and all(s * u[i] + t * v[i] == ANCHOR[i] for i in range(8)):
            for scale, ray in ((s, u), (t, v)):
                doubled = tuple(2 * scale * x for x in ray)
                require(all(x.denominator == 1 for x in doubled), "nonintegral vertex")
                vertices.add(tuple(int(x) for x in doubled))
    require(len(vertices) == 58, "independent vertex count")
    return directions, tuple(sorted(vertices))


def integer_rank(rows):
    require(
        1 <= len(rows) <= 8 and all(len(row) == 8 for row in rows),
        "invalid rank dimensions",
    )
    matrix, rank = [list(row) for row in rows], 0
    for column in range(8):
        selected = next((i for i in range(rank, len(rows)) if matrix[i][column]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for i in range(rank + 1, len(rows)):
            a, b = matrix[rank][column], matrix[i][column]
            matrix[i] = [
                a * x - b * y for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
            divisor = gcd(*matrix[i])
            if divisor:
                matrix[i] = [x // divisor for x in matrix[i]]
            require(all(abs(x) < 1 << 128 for x in matrix[i]), "integer rank capacity")
        rank += 1
    return rank


def direct_mixed(directions, vertices):
    allowed = set(directions)
    edges = {
        (i, j)
        for i, j in combinations(range(58), 2)
        if line(tuple(vertices[i][k] - vertices[j][k] for k in range(8))) in allowed
    }
    require(len(edges) == 595, "independent graph count")
    points = tuple(r for r in root_lines() if r not in frame_lines())
    anchor = tuple(2 * x for x in ANCHOR)
    evaluations = [
        (0, inner(p, anchor), *(inner(p, v) for v in vertices)) for p in points
    ]
    ranks, bounds = Counter(), Counter()
    for chosen in combinations(range(58), 4):  # Exactly 424,270 quadruples.
        if not all(pair in edges for pair in combinations(chosen, 2)):
            continue
        rank = integer_rank((anchor, *(vertices[i] for i in chosen)))
        ranks[rank] += 1
        if rank != 5:
            continue
        costs = []
        for row in evaluations:
            values = row[:2] + tuple(row[i + 2] for i in chosen)
            costs.append(6 - max(values.count(x) for x in values))
        # Allocate the retained coordinates by cost class, without sorting.
        counts = [costs.count(k) for k in range(6)]
        remaining, total = 82, 0
        for k in range(6):
            taken = min(counts[k], remaining)
            total += k * taken
            remaining -= taken
        require(remaining == 0, "incomplete support selection")
        bounds[total] += 1
    return {
        "rank_histogram": dict(sorted(ranks.items())),
        "support_histogram": dict(sorted(bounds.items())),
    }


def frame_orbit(roots):
    index = {r: i for i, r in enumerate(roots)}
    permutations = []
    for simple in SIMPLE:
        moved = []
        for root in roots:
            pairing = inner(root, simple)
            require(pairing % 4 == 0, "nonintegral reflection")
            image = canonical(
                tuple(root[i] - pairing // 4 * simple[i] for i in range(8))
            )
            moved.append(index[image])
        permutations.append(tuple(moved))
    first = tuple(sorted(index[r] for r in frame_lines()))
    queue, seen = [first], {first}
    for cursor in range(2025):
        require(cursor < len(queue), "incomplete frame orbit")
        for permutation in permutations:
            image = tuple(sorted(permutation[i] for i in queue[cursor]))
            if image not in seen:
                seen.add(image)
                queue.append(image)
        require(len(queue) <= 2025, "frame-orbit capacity")
    require(len(seen) == 2025, "frame-orbit cardinality")
    return tuple(sorted(seen))


def direct_root():
    roots = root_lines()
    frames = frame_orbit(roots)
    # Explicit A5 star, independent of the primary stabilizer extension.
    star = tuple(tuple(2 if j in (0, i) else 0 for j in range(8)) for i in range(1, 6))
    costs = []
    for root in roots:
        values = [0] + [inner(root, vertex) for vertex in star]
        costs.append(6 - max(values.count(x) for x in values))
    histogram = Counter()
    for frame in frames:
        counts = [
            sum(costs[i] == k for i in range(120) if i not in frame) for k in range(6)
        ]
        remaining, total = 82, 0
        for k in range(6):
            taken = min(counts[k], remaining)
            total += k * taken
            remaining -= taken
        require(remaining == 0, "incomplete root support selection")
        histogram[total] += 1
    return {
        "support_histogram": dict(sorted(histogram.items())),
        "frame_sha256": hashlib.sha256(json.dumps(frames).encode()).hexdigest(),
    }


def main():
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))
    directions, vertices = gram_vertices()
    require(
        vertices == tuple(map(tuple, expected["graph"]["vertices_doubled"])),
        "independent vertices differ",
    )
    mixed = direct_mixed(directions, vertices)
    root = direct_root()
    for key in mixed:
        require(
            {str(k): v for k, v in mixed[key].items()} == expected["mixed"][key],
            f"independent mixed {key} differs",
        )
    require(
        {str(k): v for k, v in root["support_histogram"].items()}
        == expected["root"]["support_histogram"],
        "independent root costs differ",
    )
    require(
        root["frame_sha256"] == expected["frame_sha256"], "frame inventories differ"
    )
    print(
        "PASS_SEPARATE_SUPPORT30 Gram_vertices=58 quadruples=424270 "
        "rank5=3136 reflection_frames=2025 mixed=121 root=122"
    )


if __name__ == "__main__":
    main()
