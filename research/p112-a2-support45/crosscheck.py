"""Independent five-label-basis check of every tight A2 fiber closure."""

import json
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
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


def check(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(a, b):
    return sum(a[i] * b[i] for i in range(8))


def coordinates(root):
    rows = [
        [Fraction(SIMPLE[j][i]) for j in range(8)] + [Fraction(root[i])]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        rows[col] = [x / rows[col][col] for x in rows[col]]
        for i in range(8):
            if i != col:
                factor = rows[i][col]
                rows[i] = [rows[i][j] - factor * rows[col][j] for j in range(9)]
    answer = tuple(row[8] for row in rows)
    check(all(x.denominator == 1 for x in answer), "nonintegral root coordinate")
    return tuple(int(x) for x in answer)


def independent_geometry():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(row)
    for signs in product((-1, 1), repeat=7):
        row = (1, *signs)
        if row.count(-1) % 2 == 0:
            roots.add(row)
    roots = tuple(sorted(roots))
    check(len(roots) == 120 and all(scalar(r, r) == 8 for r in roots), "E8 roots")
    labels = tuple(
        1 + sum((x % 2) * (2 ** (i + 1)) for i, x in enumerate(coordinates(root)))
        for root in roots
    )
    check(len(set(labels)) == 120, "root labels collide")
    return roots, labels


def reduced_basis(values):
    rows = [0] * 9
    for original in values:
        value = original
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if rows[bit]:
                    value ^= rows[bit]
                else:
                    rows[bit] = value
                    break
    for bit in range(9):
        for upper in range(bit + 1, 9):
            if rows[upper] & (1 << bit):
                rows[upper] ^= rows[bit]
    return tuple(row for row in rows if row)


def enumerate_tight(fiber, labels):
    check(len(fiber) == 27, "fiber size")
    spaces = set()
    bases = 0
    for selected in combinations(fiber, 5):
        bases += 1
        basis = reduced_basis(selected)
        if len(basis) == 5:
            spaces.add(basis)
    check(bases == 80730 and len(spaces) <= 2667, "five-label basis census")
    tight = []
    for basis in sorted(spaces):
        span = {0}
        for row in basis:
            span = span | {x ^ row for x in span}
        inside = tuple(label for label in fiber if label in span)
        check(len(inside) <= 10, "fiber capacity exceeds ten")
        if len(inside) == 10:
            check(
                sum(label in span for label in labels) == 10,
                "closure has an extra root",
            )
            tight.append(tuple(sorted(span)))
    check(len(tight) == 216, "tight-flat census")
    return sha256(repr(sorted(tight)).encode()).hexdigest()


def main():
    roots, labels = independent_geometry()
    a = roots[0]
    b = next(root for root in roots if scalar(a, root) in (-4, 4))
    fibers = defaultdict(list)
    for root, label in zip(roots, labels, strict=True):
        pair = (scalar(a, root), scalar(b, root))
        divisor = gcd(*pair)
        if divisor:
            pair = tuple(x // divisor for x in pair)
            if next(x for x in pair if x) < 0:
                pair = tuple(-x for x in pair)
            fibers[pair].append(label)
    check(sorted(map(len, fibers.values())) == [1, 1, 1, 27, 27, 27], "A2 fibers")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    for key, fiber in sorted(fibers.items()):
        if len(fiber) == 27:
            digest = enumerate_tight(fiber, labels)
            check(
                digest == receipt["fibers"][str(key)]["tight_flats_sha256"],
                "flat sets disagree",
            )
    print("PASS_INDEPENDENT_A2_CLOSURES bases=242190 tight=648 root_labels=120")


if __name__ == "__main__":
    main()
