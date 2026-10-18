"""Exact P112 boundary data, independent of the predecessor direction list."""

from fractions import Fraction
from itertools import combinations, product
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


def exact_label(row):
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
    return 1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(coefficients))


def permute(mask, permutation):
    return sum(1 << permutation[i] for i in range(112) if mask >> i & 1)


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
    supports = tuple(
        sum(
            1 << i
            for i, row in enumerate(points)
            if sum(x * y for x, y in zip(row, direction, strict=True))
        )
        for direction in roots
    )
    if sorted(mask.bit_count() for mask in supports) != [53] * 112 + [56] * 8:
        raise ValueError("root-support cardinalities")
    generators = tuple(
        tuple(map(int, line.split()))
        for line in Path(generators_path).read_text().splitlines()
    )
    if len(generators) != 12:
        raise ValueError("generator count")
    validate_generators(labels, supports, generators)
    lines = [" ".join(map(str, labels))]
    lines += [f"{mask & ((1 << 64) - 1)} {mask >> 64}" for mask in supports]
    lines += [" ".join(map(str, row)) for row in generators]
    return "\n".join(lines) + "\n"
