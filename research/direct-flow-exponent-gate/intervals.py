#!/usr/bin/env python3
"""Outward fixed-grid rational intervals; no floating-point decisions.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache

SCALE = 1 << 128


def need(ok, message):
    if not ok:
        raise ValueError(message)


def floorq(x):
    return Q(x.numerator * SCALE // x.denominator, SCALE)


def ceilq(x):
    return -floorq(-x)


class I:
    def __init__(self, lo, hi=None):
        self.lo, self.hi = Q(lo), Q(lo if hi is None else hi)
        need(self.lo <= self.hi, "reversed interval")

    @staticmethod
    def cast(x):
        return x if isinstance(x, I) else I(x)

    def __add__(self, other):
        b = I.cast(other)
        return I(floorq(self.lo + b.lo), ceilq(self.hi + b.hi))

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -I.cast(other)

    def __rsub__(self, other):
        return I.cast(other) + -self

    def __mul__(self, other):
        b = I.cast(other)
        v = [self.lo*b.lo, self.lo*b.hi, self.hi*b.lo, self.hi*b.hi]
        return I(floorq(min(v)), ceilq(max(v)))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = I.cast(other)
        need(b.lo*b.hi > 0, "division interval contains zero")
        return self * I(floorq(1/b.hi), ceilq(1/b.lo))

    def __pow__(self, n):
        need(type(n) is int and 0 <= n <= 10, "bounded integer power")
        answer = I(1)
        for _ in range(n):
            answer = answer*self
        return answer

    def contains(self, x):
        return self.lo <= x <= self.hi

    def decimal(self, places=12):
        unit = 10**places
        low = self.lo.numerator*unit//self.lo.denominator
        high = -((-self.hi.numerator*unit)//self.hi.denominator)
        def fmt(x):
            sign = "-" if x < 0 else ""
            x = abs(x)
            return sign+str(x//unit)+"."+str(x % unit).zfill(places)
        return [fmt(low), fmt(high)]


def log_series(x):
    need(Q(1) <= x <= 2, "log reduced domain")
    y = (x-1)/(x+1)
    total = Q(0)
    for j in range(64):
        total += 2*y**(2*j+1)/(2*j+1)
    remainder = 2*y**129/(129*(1-y*y))
    return I(floorq(total), ceilq(total+remainder))


@lru_cache(None)
def log_integer(n):
    need(type(n) is int and 1 <= n <= 121, "log rank domain")
    k = n.bit_length()-1
    return log_series(Q(n, 1 << k)) + k*log_series(Q(2))


def exp_interval(x):
    x = I.cast(x)
    need(-5 <= x.lo <= x.hi <= 5, "exp bounded domain")
    if x.lo < 0:
        # Monotonicity handles a zero-crossing interval too.
        low = exp_interval(I(-x.lo)).hi if x.lo < 0 else None
        if x.hi <= 0:
            high = exp_interval(I(-x.hi)).lo
            return I(floorq(1/low), ceilq(1/high))
        return I(floorq(1/low), exp_interval(I(x.hi)).hi)
    reduced = x/16
    term, total = I(1), I(1)
    for j in range(1, 41):
        term = term*reduced/j
        total = total+term
    # Every later positive term is <= previous * reduced.hi/42.
    next_term = term*reduced/41
    tail = next_term.hi/(1-reduced.hi/42)
    total = I(total.lo, ceilq(total.hi+tail))
    for _ in range(4):
        total = total*total
    return total


def rank_power(rank, exponent):
    return exp_interval(log_integer(rank)*exponent)
