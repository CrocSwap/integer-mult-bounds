#!/usr/bin/env python3
"""Outward rational intervals, adapted from my PR4433 arithmetic.

All endpoints are fractions; series tails and every rounding are outward.
zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
GRID = 2**192

def need(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return Q((x*GRID).__floor__(), GRID)


def up(x):
    return Q(-((-x*GRID).__floor__()), GRID)


def rounded(lo, hi):
    return down(lo), up(hi)


def mul(a, b):
    products = [x*y for x in a for y in b]
    return rounded(min(products), max(products))


def scale(a, x):
    return mul(a, (x, x))


def divide(a, b):
    need(b[0] > 0, 'positive interval denominator')
    return mul(a, rounded(1/b[1], 1/b[0]))


@lru_cache(None)
def log_bounds(n):
    """Exact atanh series, binary reduction; round only the final interval."""
    need(isinstance(n, int) and n >= 1, 'positive integer logarithm')

    def series(x):
        u = (x-1)/(x+1)
        term, total = u, Q(0)
        for j in range(80):
            total += 2*term/(2*j+1)
            term *= u*u
        tail = 2*term/(161*(1-u*u))
        return total, total+tail

    k = n.bit_length()-1
    a, b = series(Q(2))
    c, d = series(Q(n, 2**k))
    return rounded(k*a+c, k*b+d)


def exp_point(x):
    """Outward fixed-point Taylor enclosure, with binary scaling/squaring."""
    need(abs(x) < 16, 'bounded exponential argument')
    if x < 0:
        a, b = exp_point(-x)
        return rounded(1/b, 1/a)
    divisions = 0
    while x > Q(1, 2):
        x /= 2
        divisions += 1
    term = total = (Q(1), Q(1))
    for j in range(1, 65):
        term = scale(term, x/j)
        total = rounded(total[0]+term[0], total[1]+term[1])
    following = scale(term, x/65)
    # Every remaining ratio is <= 1/132. Twice the next term is safe.
    result = rounded(total[0], total[1]+2*following[1])
    for _ in range(divisions):
        result = mul(result, result)
    return result


def exp_interval(a):
    return exp_point(a[0])[0], exp_point(a[1])[1]


@lru_cache(None)
def power(n, exponent):
    return exp_interval(scale(log_bounds(n), exponent))


def moment(histogram, exponent):
    low = high = Q(0)
    for n, count in histogram.items():
        a, b = power(n, exponent)
        low += count*a
        high += count*b
    return rounded(low, high)


def display(a):
    unit = 10**30

    def fixed(n):
        sign = '-' if n < 0 else ''
        s = str(abs(n)).rjust(31, '0')
        return sign+s[:-30]+'.'+s[-30:]

    return {'lower': fixed((a[0]*unit).__floor__()),
            'upper': fixed(-((-a[1]*unit).__floor__()))}


def encoded(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encoded(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encoded(v) for v in x]
    return x



def add(a, b):
    return rounded(a[0]+b[0], a[1]+b[1])


def sub(a, b):
    return rounded(a[0]-b[1], a[1]-b[0])


def ipow(a, n):
    """Integer powers of a nonnegative interval, bounded-size endpoints."""
    need(type(n) is int and n >= 0 and a[0] >= 0, 'nonnegative integer power')
    out = (Q(1), Q(1))
    while n:
        if n & 1:
            out = mul(out, a)
        a = mul(a, a)
        n //= 2
    return out


def qpower(x, exponent):
    """Positive rational base, rational exponent, with an enclosed logarithm."""
    x = Q(x)
    need(x > 0, 'positive rational power base')
    return exp_interval(scale(sub(log_bounds(x.numerator),
                                  log_bounds(x.denominator)), exponent))
