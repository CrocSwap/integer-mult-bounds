"""Exact replacement for the pinned independent checker exponential enclosure.

Same Taylor polynomial, geometric tail and 200-bit outward rounding. Only
integer arithmetic is used before constructing the two returned Fractions.
Stephan Arrington, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from math import factorial

D = 1 << 200
FACTORIAL_16 = factorial(16)
COEFFICIENTS = tuple(FACTORIAL_16 // factorial(j) for j in range(17))


def _polynomial(x):
    """Return unreduced N, d with N/d = sum(x**j/j! for j in 0..16)."""
    p, q = x.numerator, x.denominator
    numerator = 1
    q_power = 1
    for coefficient in reversed(COEFFICIENTS[:-1]):
        q_power *= q
        numerator = numerator * p + coefficient * q_power
    return numerator, FACTORIAL_16 * q_power


def exp(a, b):
    """Return exactly the reference bounds for exact 0 <= a <= b < 1."""
    if not isinstance(a, Fraction) or not isinstance(b, Fraction):
        raise TypeError('Fraction endpoints required')
    if not 0 <= a <= b < 1:
        raise ValueError('positive small exponent')
    low_n, low_d = _polynomial(a)
    high_n, high_d = _polynomial(b)
    p, q = b.numerator, b.denominator
    tail_factor = 17 * (18 * q - p)
    high_n = high_n * tail_factor + 18 * p ** 17
    high_d *= tail_factor
    low = (D * low_n) // low_d
    high = -((-D * high_n) // high_d)
    return Fraction(low, D), Fraction(high, D)
