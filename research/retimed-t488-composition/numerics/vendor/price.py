# SPDX-License-Identifier: Apache-2.0
"""Rational enclosures for the finite paid-profile comparison.

For 1<=x<2, log(x)=2*sum(z^(2j+1)/(2j+1)), z=(x-1)/(x+1).
The positive remainder is at most 2*z^(2n+1)/((2n+1)*(1-z*z)).
Range reduction gives z<=1/3. Alternating exponential partial sums then
bound exp(-a*log(r)); no floating arithmetic or root solver is used.
"""
from fractions import Fraction as Q
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


def log_series(x, n=100):
    z = (x - 1) / (x + 1)
    total = Q(0)
    power = z
    for j in range(n):
        total += 2 * power / (2*j + 1)
        power *= z*z
    tail = 2 * power / ((2*n + 1) * (1-z*z))
    return total, total + tail


@lru_cache(None)
def log_bounds(rank):
    need(type(rank) is int and 1 <= rank <= 73, 'priced rank domain')
    exponent = rank.bit_length() - 1
    a, b = log_series(Q(rank, 1 << exponent))
    c, d = log_series(Q(2))
    lo, hi = a + exponent*c, b + exponent*d
    # Outward rational quantization keeps subsequent denominators bounded.
    scale = 10**90
    low = (lo.numerator * scale) // lo.denominator
    high = -((-hi.numerator * scale) // hi.denominator)
    return Q(low, scale), Q(high, scale)


def exp_negative(x, degree):
    need(0 <= x < 1, 'alternating exponential range')
    term = Q(1)
    total = term
    for j in range(1, degree + 1):
        term *= -x / j
        total += term
    return total


@lru_cache(None)
def h_bounds(rank, a):
    need(Q(0) < a < Q(1, 100), 'exponent domain')
    lo, hi = log_bounds(rank)
    return rank * exp_negative(a*hi, 31), rank * exp_negative(a*lo, 30)


def interval(profile, a):
    a = Q(a)
    lower = upper = Q(0)
    for r, count in profile.items():
        need(type(r) is int and type(count) is int, 'integer signed profile')
        lo, hi = h_bounds(r, a)
        lower += count * (lo if count >= 0 else hi)
        upper += count * (hi if count >= 0 else lo)
    return lower, upper


def compact(bounds):
    # Report outward intervals at 60 decimal places, retaining rational signs.
    lo, hi = bounds
    scale = 10**60
    low = (lo.numerator*scale)//lo.denominator
    high = -((-hi.numerator*scale)//hi.denominator)
    return {'lower': str(Q(low, scale)), 'upper': str(Q(high, scale))}
