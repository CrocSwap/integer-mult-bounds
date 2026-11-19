"""Independent class-displacement audit of four interior/exterior inverse weights."""
from fractions import Fraction
import json

import flag_weights as F
from compile_row import apply, inverse, pairing


def cross_weights():
    data = json.loads((F.P.HERE / 'predecessor/source/CLASS-ALGEBRA.json').read_bytes())
    reciprocals = F.P.class_inverse(data)
    bases, spaces, _ = F.P.quotient()
    accum = [Fraction(0), Fraction(0)]
    # A common scaling makes all distance weights integral.
    factors = [(-1)**j * 32**(4-j) for j in range(5)]
    for cls, reciprocal in zip(data['classes'], reciprocals, strict=True):
        previous = None
        for g in cls['representatives']:
            rev = inverse(tuple(g))
            back = [apply(rev, v) for v in range(256)]
            paired = sum(1 << v for v in range(256) if pairing(v, apply(g, v)))
            sums = [0, 0]
            for basis, L in zip(bases, spaces, strict=True):
                preimage = F.P.point_set(tuple(back[x] for x in basis))
                shared = (L & preimage).bit_count()
                j = 5 - shared.bit_length()
                exterior = preimage & ~L
                paired_count = (exterior & paired).bit_count()
                sums[0] += factors[j] * (exterior.bit_count() - paired_count)
                sums[1] += factors[j] * paired_count
            if previous is not None and sums != previous:
                raise ValueError("Rational packet has unequal cross displacement sums")
            previous = sums
        for bit, val in enumerate(previous):
            accum[bit] += cls['size'] * reciprocal * val
    # For one nonzero interior vector, exactly 112 exterior vectors are
    # perpendicular and 128 have nonzero pairing. There are 15 choices of u.
    return tuple(val / (2295 * 15 * choices * 32**4 * 4**13)
                 for choices, val in zip((112, 128), accum, strict=True))


def check():
    expected = cross_weights()
    if not all(expected) or expected[0] == expected[1]:
        raise ValueError("Cross-displacement probes should be distinct and nonzero")
    for bit, inside, outside in ((0, 1, 32), (1, 1, 16)):
        if pairing(inside, outside) != bit:
            raise ValueError("Invalid representative")
        for u, w in ((inside, outside), (outside, inside)):
            got = F.weight(F.BASE, u, F.BASE, w)
            if got != expected[bit]:
                raise ValueError((bit, u, w, got, expected[bit]))
    print("PASS direct reciprocal class sums for interior/exterior and reversed mark pairs",
          *map(str, expected))


if __name__ == '__main__':
    check()
