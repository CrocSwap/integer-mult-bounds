"""Exact rational logarithm/positive-series oracle, separate from Mason's code.

Classical series are credited; this is a checker, never a production tariff.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive independent logarithm")
    k, bound = 0, Q(1)
    if value >= 1:
        while bound < value:
            k, bound = k + 1, bound * 2
        return k
    while bound / 2 >= value:
        k, bound = k - 1, bound / 2
    return k


@lru_cache(None)
def pi_box(bits=100):
    def atan_inverse(d):
        total = Q(0)
        n = 0
        while True:
            total += Q((-1) ** n, (2 * n + 1) * d ** (2 * n + 1))
            n += 1
            tail = Q(1, (2 * n + 1) * d ** (2 * n + 1))
            if tail < Q(1, 1 << (bits + 8)):
                other = total + (-1) ** n * tail
                return min(total, other), max(total, other)
    a, b = atan_inverse(5), atan_inverse(239)
    lo, hi = 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]
    scale = 1 << bits
    return Q((lo * scale).__floor__(), scale), Q((hi * scale).__ceil__(), scale)


@lru_cache(None)
def log_box(integer, bits=100):
    need(type(integer) is int and integer >= 1, "positive exact logarithm input")
    k = integer.bit_length() - 1
    mantissa = Q(integer, 1 << k)
    def local(x):
        y = (x - 1) / (x + 1)
        total, power = Q(0), y
        for n in range(bits + 10):
            total += 2 * power / (2 * n + 1)
            power *= y * y
            tail = 2 * power / ((2 * n + 3) * (1 - y * y))
            if tail < Q(1, 1 << (bits + 8)):
                return total, total + tail
        raise ValueError("bounded independent logarithm series")
    a, b = local(Q(2)), local(mantissa)
    return k * a[0] + b[0], k * a[1] + b[1]


def actual_alpha(p):
    pi_lo, pi_hi = pi_box()
    ln_lo, ln_hi = log_box(16 * p)
    alpha = 1
    while alpha * alpha * pi_lo < 4 * ln_hi:
        alpha += 1
    need((alpha - 1) ** 2 * pi_hi < 4 * ln_lo,
         "finite alpha certificate separates the actual source ceiling")
    return alpha


@lru_cache(None)
def decay_box(factor, bits=90):
    factor = Q(factor)
    need(factor >= 0, "nonnegative independent decay argument")
    # A proved coarse bound avoids huge positive Taylor values when unnecessary.
    if 3 * factor >= bits + 8:
        return Q(0), Q(1, 1 << (3 * factor).__floor__())
    plo, phi = pi_box(bits + 16)
    lo, hi = factor * plo, factor * phi
    termlo = termhi = total_lo = total_hi = Q(1)
    for n in range(1, 8 * (bits + 1) + 500):
        termlo, termhi = termlo * lo / n, termhi * hi / n
        total_lo, total_hi = total_lo + termlo, total_hi + termhi
        if hi < n + 2:
            tail = termhi * hi / (n + 1) / (1 - hi / (n + 2))
            if tail < Q(1, 1 << (bits + 16)):
                return 1 / (total_hi + tail), 1 / total_lo
    raise ValueError("bounded independent direct Taylor series")
