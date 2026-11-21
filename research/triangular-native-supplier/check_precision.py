"""Check the real width controller at exact outer geometries and the public error transfer."""

from fractions import Fraction
from math import gcd, prod
from multiplier import precision
from outer_schedule import Shape, parameters, square_axes
from check_eighth_grid import main as probe_grid


def bounds():
    for exponent, expected in ((16384, 0), (24576, 1), (65536, 2), (131072, 4), (262144, 8)):
        n = (1 << exponent) + 11
        shape = parameters(n)
        assert (shape.count if shape else 0) == expected
        if shape is None:
            continue
        sides = tuple(square_axes(shape.axes()))
        size = prod(sides)
        T = 1 << shape.extent_bits
        b = shape.public // 6
        assert 3 * T <= 4 * size and 2 * ((n + b - 1) // b) - 2 < size <= 1 << b
        assert all(gcd(x, y) == 1 for i, x in enumerate(sides) for y in sides[:i])
        assert precision(shape.public, shape.extent_bits, shape.count) >= 32768 * (
            max(shape.axes()) + 6
        )
    print(
        "verified finite geometry transition and coprime square sides at 1, 2, 4 and 8 axes",
        flush=True,
    )
    for k in (510, 1024, 4096, 9000):
        # n = 2^(2^k). Only the logarithms of its extents are materialized.
        b = 1 << k
        p = 6 * b
        s = (p + 1).bit_length()
        L = b + 2 - k
        cap = L // (64 * s * s)
        d = 1 << (cap.bit_length() - 1)
        old = Shape(p, L, d).precision()
        new = precision(p, L, d)
        assert s >= 512 and old >= 5460 * p and 50 * new < 51 * p
        old_work = 16 * ((2 * old + 47) // 8)
        new_fields = 16 * ((2 * new + 47) // 8 + (p + 11) // 8)
        # For this shape 4n/T=b, including both inputs and output.
        explicit = Fraction(old_work, new_fields + b)
        assert explicit > 3100
        ell = (L + d - 1) // d
        h = max(1, d // (1024 * s))
        E = 4096 * h * (ell + 6)
        J = 20000 * (d + 1) * (ell + 2) ** 6 + 2 * d
        # d times the written per-pack defect is below one eighth of the public step.
        coeff = 6 * J * (d + 1) ** 2 + 2 * (d + 1)
        assert (d * coeff).bit_length() + p + 3 + 4 * E <= new
        assert 32768 * (ell + 6) <= new
        print(
            "log2 b",
            k,
            "old/new P per p",
            float(Fraction(old, p)),
            float(Fraction(new, p)),
            "old work / new fields with binary I/O",
            float(explicit),
            flush=True,
        )


if __name__ == "__main__":
    bounds()
    probe_grid()
