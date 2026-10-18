"""Fraction-free Taylor loop with the retained exact stopping/rounding rule.

ywz65 with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def require(ok, why):
    if not ok:
        raise ValueError(why)


def series(y, precision, upper):
    """Return the original dyadic endpoint and its exact stopping index."""
    require(isinstance(y, (int, Q)), 'rational endpoint')
    require(type(precision) is int and precision >= 0, 'precision')
    y = Q(y)
    require(0 <= y <= Q(1, 2), 'exp range')
    p, q = y.numerator, y.denominator
    power, denominator, total, k = 1, 1, 1, 0
    while True:
        k += 1
        power *= p
        denominator *= q * k
        total = total * q * k + power
        # t_k*y < 2^(-precision-8), exactly as in retained series().
        if (power * p << (precision + 8)) < denominator * q:
            if upper:
                numerator = total * q * (k + 1) + 2 * power * p
                divisor = denominator * q * (k + 1)
                rounded = -((-numerator << precision) // divisor)
            else:
                rounded = (total << precision) // denominator
            return Q(rounded, 1 << precision), k


def exp(lo, hi, precision=256):
    require(0 <= lo <= hi <= Q(1, 2), 'exp range')
    return series(lo, precision, False)[0], series(hi, precision, True)[0]
