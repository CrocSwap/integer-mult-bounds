"""Directed integer bounds for r^(4984891121/5000000000), 1 <= r <= 9.

Produced by Nick Petalas. Only exact integer and rational arithmetic is used.
"""
from fractions import Fraction
from math import factorial

SCALE = 1 << 192
NUMERATOR = 4984891121
DENOMINATOR = 5000000000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def log_series(value):
    require(Fraction(1) <= value <= 2, "Reduced logarithm domain")
    t = (value - 1) / (value + 1)
    term, lower = t, 0
    for index in range(128):
        summand = 2 * term / (2 * index + 1)
        lower += summand.numerator * SCALE // summand.denominator
        term *= t * t
    tail = 2 * term / (257 * (1 - t * t))
    require(0 <= tail < Fraction(1, SCALE), "Logarithm remainder")
    return lower, lower + 129


def price_interval(rank):
    require(type(rank) is int and 1 <= rank <= 9, "Rank domain")
    if rank == 1:
        return SCALE, SCALE
    shift = rank.bit_length() - 1
    lower, upper = log_series(Fraction(rank, 1 << shift))
    low_two, high_two = log_series(Fraction(2))
    lower = (lower + shift * low_two) * NUMERATOR // DENOMINATOR
    upper = ((upper + shift * high_two) * NUMERATOR + DENOMINATOR - 1) // DENOMINATOR
    require(0 <= lower <= upper <= 3 * SCALE, "Exponential domain")
    term_low = term_high = total_low = total_high = SCALE
    for index in range(1, 257):
        divisor = SCALE * index
        term_low = term_low * lower // divisor
        term_high = (term_high * upper + divisor - 1) // divisor
        total_low += term_low
        total_high += term_high
    remainder = Fraction(3**257, factorial(257)) / (1 - Fraction(3, 258))
    require(remainder < Fraction(1, SCALE), "Exponential remainder")
    return total_low, total_high + 1


def polynomial_interval(coefficients, prices):
    lower = upper = 0
    for rank, value in enumerate(coefficients, 1):
        a, b = prices[rank]
        lower += value * (a if value >= 0 else b)
        upper += value * (b if value >= 0 else a)
    return lower, upper
