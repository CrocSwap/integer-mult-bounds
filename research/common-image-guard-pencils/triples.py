"""Finite exception certificates for the all-field independent-triple proof."""
from fractions import Fraction
from math import comb

from laws import independent_triple, marginal


def box_triple(q, m):
    """Subtract actual collinear triples in each coordinate product box."""
    d = m - 1
    ambient = q**d
    total = 0
    for free in range(d + 1):
        restricted = d - free
        n = q**free*(q - 1)**restricted
        along_line = q**(2*free)*((q - 1)*(q - 2))**restricted
        frames = n*(n - 1)*(n - 2) - (q - 2)*(along_line - n)
        total += (q - 1)*comb(d, free)*(q - 1)**restricted*frames
    return Fraction(total, (q**m - 1)*ambient*(ambient - 1)*(ambient - q))


def certificates():
    result = []
    for q in (3, 4, 5, 7, 8, 9, 11, 13, 16, 17):
        x = Fraction(1, q)
        t = 1 - x + x*x
        base = q*t**3
        if base <= 1:
            raise ValueError("triple tail growth")
        lower = 2*x*(1 - x)**3 * base**2
        d = 2
        exceptions = []
        while lower <= q + 1:
            counted = box_triple(q, d + 1)
            if counted != independent_triple(q, d + 1):
                raise ValueError("triple affine box count")
            ratio = counted/marginal(q, d + 1)**3
            if ratio <= 1:
                raise ValueError("independent triple finite exception")
            exceptions.append(dict(m=d + 1, ratio=str(ratio), floor_1e6=10**6*ratio.numerator//ratio.denominator))
            lower *= base
            d += 1
        result.append(dict(q=q, first_d_with_tail=d, tail_lower=str(lower), exceptions=exceptions))
    return result
