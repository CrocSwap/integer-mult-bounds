"""Exact P112 data and Weyl-chamber direction coverage.

Root/label reconstruction and generator checks descend from Nick Petalas's
PR3161, a1aba8389b87412e6f72ccf4d11f31e0ea232327, Apache-2.0.
The chamber rays and reflection closure are new here.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd, lcm
from pathlib import Path

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


def canonical(row):
    return max(tuple(row), tuple(-x for x in row))


def primitive(row):
    denominator = lcm(*(x.denominator for x in row))
    integers = tuple(int(x * denominator) for x in row)
    divisor = gcd(*integers)
    if not divisor:
        raise ValueError("zero projective direction")
    return canonical(tuple(x // divisor for x in integers))


def chamber_ray(omitted):
    """The rational normal to seven of the eight simple roots."""
    matrix = [
        [Fraction(x) for x in row] for i, row in enumerate(SIMPLE) if i != omitted
    ]
    pivots = []
    for col in range(8):
        rank = len(pivots)
        pivot = next((i for i in range(rank, 7) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(7):
            if i != rank:
                scale = matrix[i][col]
                matrix[i] = [
                    x - scale * y for x, y in zip(matrix[i], matrix[rank], strict=True)
                ]
        pivots.append(col)
    if len(pivots) != 7:
        raise ValueError("simple-root hyperplane rank")
    free = next(col for col in range(8) if col not in pivots)
    result = [Fraction(0)] * 8
    result[free] = Fraction(1)
    for i, col in enumerate(pivots):
        result[col] = -matrix[i][free]
    return primitive(result)


def reflection(direction, root):
    dot = sum(x * y for x, y in zip(direction, root, strict=True))
    return primitive(
        tuple(Fraction(4 * x - dot * y) for x, y in zip(direction, root, strict=True))
    )


def weyl_closure(seeds):
    active = set(seeds)
    pending = sorted(active)
    for index in range(1200):
        if index == len(pending):
            break
        for root in SIMPLE:
            image = reflection(pending[index], root)
            if image not in active:
                if len(active) >= 1200:
                    raise ValueError("Weyl-orbit capacity")
                active.add(image)
                pending.append(image)
    if len(active) != 1200 or any(
        reflection(h, r) not in active for h in active for r in SIMPLE
    ):
        raise ValueError("incomplete Weyl closure")
    return active


def direction_catalogue():
    """All projective directions with at least 42 perpendicular E8 lines."""
    roots = root_lines()
    coefficients = tuple(simple_coefficients(r) for r in roots)
    if any(
        not (all(x >= 0 for x in c) or all(x <= 0 for x in c)) for c in coefficients
    ):
        raise ValueError("roots are not positive or negative in the simple basis")
    six_counts = tuple(
        sum(all(c[i] == 0 for i in omitted) for c in coefficients)
        for omitted in combinations(range(8), 2)
    )
    if max(six_counts) != 36:
        raise ValueError("rank-six parabolic capacity")
    rays = tuple(chamber_ray(i) for i in range(8))
    zero_counts = tuple(
        sum(sum(x * y for x, y in zip(h, r, strict=True)) == 0 for r in roots)
        for h in rays
    )
    active = weyl_closure(
        h for h, count in zip(rays, zero_counts, strict=True) if count >= 42
    )
    counts = {42: 0, 63: 0}
    points = tuple(row for row in roots if row not in frame_lines())
    selected = []
    for h in sorted(active):
        zeros = sum(sum(x * y for x, y in zip(h, r, strict=True)) == 0 for r in roots)
        if zeros not in counts:
            raise ValueError("unexpected perpendicular root system")
        counts[zeros] += 1
        off = sum(bool(sum(x * y for x, y in zip(h, r, strict=True))) for r in points)
        if off <= 70:
            selected.append(h)
    if counts != {42: 1080, 63: 120} or len(selected) != 248:
        raise ValueError("direction inventory")
    return tuple(selected), {
        "rank_six_parabolic_counts": six_counts,
        "chamber_zero_counts": zero_counts,
        "weyl_directions": 1200,
        "e7": 120,
        "d7": 1080,
        "retained": 248,
    }


def root_lines():
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            roots.add(canonical(row))
    for row in product((-1, 1), repeat=8):
        if sum(x == -1 for x in row) % 2 == 0:
            roots.add(canonical(row))
    if len(roots) != 120:
        raise ValueError("E8 root inventory")
    return tuple(sorted(roots))


def frame_lines():
    frame = []
    for i in range(0, 8, 2):
        for sign in (2, -2):
            row = [0] * 8
            row[i], row[i + 1] = 2, sign
            frame.append(canonical(row))
    return tuple(frame)


def simple_coefficients(row):
    matrix = [
        [Fraction(SIMPLE[j][i]) for j in range(8)] + [Fraction(row[i])]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next((i for i in range(col, 8) if matrix[i][col]), None)
        if pivot is None:
            raise ValueError("singular E8 basis")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [x / scale for x in matrix[col]]
        for i in range(8):
            if i != col:
                scale = matrix[i][col]
                matrix[i] = [
                    x - scale * y for x, y in zip(matrix[i], matrix[col], strict=True)
                ]
    coefficients = [matrix[i][8] for i in range(8)]
    if any(x.denominator != 1 for x in coefficients):
        raise ValueError("nonintegral E8 coordinates")
    return tuple(int(x) for x in coefficients)


def exact_label(row):
    return 1 | sum((x % 2) << (i + 1) for i, x in enumerate(simple_coefficients(row)))


def permute(mask, permutation):
    return sum(1 << permutation[i] for i in range(112) if mask >> i & 1)


def signed_gram(points, permutation):
    """Certify that a line permutation lifts to a rational orthogonal map."""
    signs = [0] * 112
    signs[0] = 1
    pending = [0]
    for index in range(112):
        if index == len(pending):
            break
        i = pending[index]
        for j in range(112):
            before = sum(x * y for x, y in zip(points[i], points[j], strict=True))
            after = sum(
                x * y
                for x, y in zip(
                    points[permutation[i]], points[permutation[j]], strict=True
                )
            )
            if abs(before) != abs(after):
                raise ValueError("line permutation changes absolute Gram matrix")
            if before:
                proposed = signs[i] * (before // after)
                if signs[j] and signs[j] != proposed:
                    raise ValueError("inconsistent Gram signs")
                if not signs[j]:
                    signs[j] = proposed
                    pending.append(j)
    if len(pending) != 112:
        raise ValueError("disconnected nonorthogonality graph")
    return signs.count(-1)


def validate_generators(labels, supports, generators):
    support_set = set(supports)
    for permutation in generators:
        if sorted(permutation) != list(range(112)):
            raise ValueError("invalid line permutation")
        basis = [0] * 9
        images = [0] * 9
        for index, label in enumerate(labels):
            value, image = label, labels[permutation[index]]
            for bit in range(8, -1, -1):
                if value >> bit & 1:
                    if basis[bit]:
                        value ^= basis[bit]
                        image ^= images[bit]
                    else:
                        basis[bit], images[bit] = value, image
                        break
            if value == 0 and image != 0:
                raise ValueError("nonlinear label permutation")
        if any(permute(mask, permutation) not in support_set for mask in supports):
            raise ValueError("permutation fails root-support closure")


def fixture(data_path, generators_path):
    roots, frame = root_lines(), frame_lines()
    points = tuple(row for row in roots if row not in frame)
    labels = tuple(exact_label(row) for row in points)
    with Path(data_path).open() as stream:
        source_labels = tuple(map(int, stream.readline().split()))
        source_frame = tuple(map(int, stream.readline().split()))
        source_points = tuple(
            tuple(map(int, stream.readline().split())) for _ in range(112)
        )
    if (
        source_labels != labels
        or source_points != points
        or source_frame != tuple(exact_label(row) for row in frame)
    ):
        raise ValueError("predecessor label/coordinate binding")
    directions, coverage = direction_catalogue()
    supports = tuple(
        sum(
            1 << i
            for i, row in enumerate(points)
            if sum(x * y for x, y in zip(row, direction, strict=True))
        )
        for direction in directions
    )
    if (
        sorted(mask.bit_count() for mask in supports)
        != [53] * 112 + [56] * 8 + [70] * 128
    ):
        raise ValueError("direction-support cardinalities")
    generators = tuple(
        tuple(map(int, line.split()))
        for line in Path(generators_path).read_text().splitlines()
    )
    if len(generators) != 12:
        raise ValueError("generator count")
    validate_generators(labels, supports, generators)
    coverage["orthogonal_generator_negative_signs"] = tuple(
        signed_gram(points, g) for g in generators
    )
    lines = [" ".join(map(str, labels))]
    lines += [" ".join(map(str, row)) for row in directions]
    lines += [f"{mask & ((1 << 64) - 1)} {mask >> 64}" for mask in supports]
    lines += [" ".join(map(str, row)) for row in generators]
    return "\n".join(lines) + "\n", coverage
