"""Separate dense-coordinate and dual-two-space check of the analytic lemma."""

import json
from fractions import Fraction
from itertools import combinations, product

from common import PACKAGE, geometry, require


def dot(x, y):
    return sum(u * v for u, v in zip(x, y, strict=True))


def rebuild(g):
    roots = set()
    for positions in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            row = tuple(
                signs[positions.index(i)] if i in positions else 0 for i in range(8)
            )
            roots.add(max(row, tuple(-x for x in row)))
    for row in product((-1, 1), repeat=8):
        if sum(row) % 4 == 0:
            roots.add(max(row, tuple(-x for x in row)))
    roots = tuple(sorted(roots))
    matrix = [
        [Fraction(g.SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if matrix[i][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [x / scale for x in matrix[col]]
        for i in range(8):
            if i != col:
                scale = matrix[i][col]
                matrix[i] = [
                    x - scale * y for x, y in zip(matrix[i], matrix[col], strict=True)
                ]
    labels = []
    for root in roots:
        coords = [sum(matrix[i][j + 8] * root[j] for j in range(8)) for i in range(8)]
        require(
            all(c.denominator == 1 for c in coords), "independent integral coordinates"
        )
        labels.append(
            1 + sum((int(c) & 1) * 2 ** (i + 1) for i, c in enumerate(coords))
        )
    require(roots == g.root_lines(), "independent root inventory")
    return roots, tuple(labels)


def independent_codes(values):
    codes = {0: 0}
    dimension = 0
    for value in values:
        if value not in codes:
            codes.update({x ^ value: y + 2**dimension for x, y in tuple(codes.items())})
            dimension += 1
    require(dimension == 8, "full axis span dimension")
    return codes


def main():
    g = geometry()
    roots, labels = rebuild(g)
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    a, b = (roots[i] for i in expected["pair"])
    axis = tuple(i for i, r in enumerate(roots) if dot(a, r) and not dot(b, r))
    codes = independent_codes(tuple(labels[i] for i in axis))
    quads = tuple(
        z
        for z in combinations(range(33), 4)
        if all(not dot(roots[axis[i]], roots[axis[j]]) for i, j in combinations(z, 2))
    )
    removed = tuple(sum(1 << j for j in z) for z in quads)
    kernels = tuple(
        sum(
            1 << j
            for j, i in enumerate(axis)
            if (codes[labels[i]] & normal).bit_count() % 2 == 0
        )
        for normal in range(256)
    )
    maxima = [0] * len(removed)
    count = 0
    for f, h in combinations(range(1, 256), 2):
        if h < (f ^ h):
            mask = kernels[f] & kernels[h]
            count += 1
            for j, puncture in enumerate(removed):
                maxima[j] = max(maxima[j], (mask & ~puncture).bit_count())
    require(
        count == 10795 and len(removed) == 120 and set(maxima) == {18},
        "independent arbitrary-six-space puncture maxima",
    )
    witness = expected["fixed_p112_witness"]
    require(len(witness["support"]) == 18, "fixed witness support size")
    all_values = {0}
    for i in witness["support"]:
        all_values.update(x ^ labels[i] for x in tuple(all_values))
    require(len(all_values) == 64, "fixed witness rank six")
    x, y = (roots[i] for i in witness["pair"])
    frame = set(g.frame_lines())
    require(
        all(
            dot(x, roots[i]) and not dot(y, roots[i]) and roots[i] not in frame
            for i in witness["support"]
        ),
        "literal fixed P112 witness",
    )
    require(
        set(witness["puncture"])
        == {
            i for i, r in enumerate(roots) if dot(x, r) and not dot(y, r) and r in frame
        },
        "actual frame puncture",
    )
    print("PASS_D6_INDEPENDENT six_spaces=10795 punctures=120 fixed_P112_witness=18")


if __name__ == "__main__":
    main()
