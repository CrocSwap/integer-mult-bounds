# SPDX-License-Identifier: Apache-2.0
"""Exact row controls for pair-first canonical C numerators and both phases."""

from fractions import Fraction as Q

from format import add, depth, norm, require


def coefficient(rank, x, y, sign):
    real, imag = Q(1), Q(0)
    for axis in range(rank):
        s = sign if not ((x ^ y) >> axis & 1) else -sign
        real, imag = (real - s * imag) / 2, (imag + s * real) / 2
    return real, imag


def component(rank, x, dimension, sign, imaginary=False):
    row = {}
    for y in range(dimension):
        if x >> rank != y >> rank:
            continue
        real, imag = coefficient(rank, x, y, sign)
        if real:
            row[2 * y + int(imaginary)] = real
        if imag:
            row[2 * y + int(not imaginary)] = imag if imaginary else -imag
    return row


def partials(rank, inverse, orientation):
    completed = rank if inverse else rank - 1
    sign = -orientation if inverse else orientation
    a, b, c, d = [
        component(completed, x, 1 << rank, orientation, im)
        for x, im in (
            (0, False),
            (0, True),
            (1 << (rank - 1), False),
            (1 << (rank - 1), True),
        )
    ]
    left, right = add(a, b, -sign), add(c, d, sign)
    ileft, iright = add(b, a, sign), add(d, c, -sign)
    return [
        a,
        b,
        c,
        d,
        left,
        right,
        add(left, right, Q(1)),
        ileft,
        iright,
        add(ileft, iright, Q(1)),
    ]


def controls():
    result = []
    for rank in range(1, 10):
        for inverse in (False, True):
            expected_norm = 2 ** (1 + (rank // 2 if inverse else (rank + 1) // 2))
            expected_depth = (rank + 1) // 2 if inverse else rank // 2
            for orientation in (-1, 1):
                rows = partials(rank, inverse, orientation)
                require(
                    max(map(norm, rows)) == expected_norm, "pair-first numerator norm"
                )
                require(
                    max(map(depth, rows)) == expected_depth, "pair-first numerator grid"
                )
                result.append(
                    {
                        "rank": rank,
                        "inverse": inverse,
                        "orientation": orientation,
                        "partial_norm": expected_norm,
                        "partial_grid": expected_depth,
                    }
                )
    return result
