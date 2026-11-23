"""Integer-only outward bounds for rank^(1-c), including rank 1/2.

The exponent is bracketed on a 2^-128 grid. Each square root, product,
and reciprocal is rounded outward on a 2^-224 grid.
"""
from fractions import Fraction as Q
from functools import cache
from math import isqrt

BITS = 224
UNIT = 1 << BITS
EXP_GRID = 1 << 128


def ceildiv(a, b):
    return -(-a // b)


@cache
def dyadic_power(rank, numerator):
    if rank < 1 or numerator < 0:
        raise ValueError('positive integer rank and nonnegative exponent required')
    whole, rem = divmod(numerator, EXP_GRID)
    low = high = (rank ** whole) * UNIT
    root_low = root_high = rank * UNIT
    step = EXP_GRID
    while step > 1:
        step //= 2
        root_low = isqrt(root_low * UNIT)
        root_high = 1 + isqrt(root_high * UNIT - 1)
        if rem & step:
            low = low * root_low // UNIT
            high = ceildiv(high * root_high, UNIT)
    assert low <= high
    return low, high


@cache
def power(rank, c):
    rank, c = Q(rank), Q(c)
    exponent = 1 - c
    if not 0 <= exponent <= 1 or rank <= 0:
        raise ValueError('rate or rank outside the stated proof domain')
    lo = (exponent * EXP_GRID).__floor__()
    hi = (exponent * EXP_GRID).__ceil__()
    if rank == Q(1, 2):
        _, hi2 = dyadic_power(2, hi)
        lo2, _ = dyadic_power(2, lo)
        return UNIT * UNIT // hi2, ceildiv(UNIT * UNIT, lo2)
    if rank.denominator != 1:
        raise ValueError('only integer ranks and 1/2 occur in the source')
    low, _ = dyadic_power(rank.numerator, lo)
    _, high = dyadic_power(rank.numerator, hi)
    return low, high
