"""Exact fixed Taylor polynomial and the retained geometric remainder."""

from fractions import Fraction as Q

TERMS = 48
MAX_INPUT_BITS = 16384


def exp_interval(x):
    """Return exactly the retained rational pair after 48 Taylor steps."""
    if type(x) not in (int, Q):
        raise ValueError("exact rational exponential argument required")
    x = Q(x)
    if not 0 <= x < 1:
        raise ValueError("exponential enclosure range")
    a, b = x.numerator, x.denominator
    if max(a.bit_length(), b.bit_length()) > MAX_INPUT_BITS:
        raise ValueError("exponential input bit capacity")
    numerator = denominator_power = factorial = 1
    for j in range(TERMS, 0, -1):
        denominator_power *= b
        factorial *= j
        numerator = a * numerator + factorial * denominator_power
    denominator = factorial * denominator_power
    tail_factor = (TERMS + 1) * ((TERMS + 2) * b - a)
    upper_numerator = numerator * tail_factor + (TERMS + 2) * a ** (TERMS + 1)
    return Q(numerator, denominator), Q(upper_numerator, denominator * tail_factor)
