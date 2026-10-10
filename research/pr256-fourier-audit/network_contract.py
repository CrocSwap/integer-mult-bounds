"""Reusable exact arithmetic for finite tensor-network certificates.

The histogram is an input, not a proof of a realizable network. The written
network contract must separately establish its physical and algorithmic meaning.
"""
from fractions import Fraction as Q
from math import factorial
from rational_bounds import log_bounds


def moment_bounds(hist, m, roles, saving):
    """Enclose sum n_r (r/m)^(1-saving) / roles using rational arithmetic."""
    if not 0 < saving < 1 or roles <= 0 or m < 2 or not hist:
        raise ValueError('invalid network parameters')
    lower = upper = Q(0)
    grid = 10**60
    for width, count in hist.items():
        if not 0 < width < m or count <= 0:
            raise ValueError('children must have positive counts and smaller widths')
        lo, hi = log_bounds(Q(m, width))
        lo = Q(lo.numerator * grid // lo.denominator, grid)
        hi = Q((hi.numerator * grid + hi.denominator - 1) // hi.denominator, grid)
        x, y = saving * lo, saving * hi
        if not 0 <= y < 3:
            raise ValueError('exponential bound outside its domain')
        # Positive Taylor terms give a lower bound; the successive tail ratios
        # from the quadratic term onward are at most y/3.
        el = sum(x**j / factorial(j) for j in range(7))
        eu = 1 + y + y*y / (2 * (1 - y/3))
        weight = Q(count) * Q(width, m) / roles
        lower += weight * el
        upper += weight * eu
    return lower, upper
