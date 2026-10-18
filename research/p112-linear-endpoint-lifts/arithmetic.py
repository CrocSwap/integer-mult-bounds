# SPDX-License-Identifier: Apache-2.0
"""Enclose the complete selected moment with rational series bounds."""
from fractions import Fraction as Q
from functools import lru_cache

EPS = Q(1, 1 << 192)


def atanh_log(value):
    t = (value - 1) / (value + 1)
    if not 0 <= t <= Q(1, 3):
        raise ValueError('log series domain')
    total, power, k = Q(0), t, 0
    while True:
        total += power / (2 * k + 1)
        power *= t * t
        k += 1
        tail = 2 * power / ((2 * k + 1) * (1 - t * t))
        if tail < EPS:
            return 2 * total, 2 * total + tail


@lru_cache(None)
def log_ratio(m, r):
    value, k = Q(m, r), 0
    while value >= 2:
        value /= 2
        k += 1
    lo, hi = atanh_log(value)
    l2, u2 = atanh_log(Q(2))
    return lo + k * l2, hi + k * u2


def exponential(value):
    if not 0 <= value <= Q(1, 2):
        raise ValueError('exp series domain')
    total, term, k = Q(1), Q(1), 0
    while True:
        k += 1
        term *= value / k
        total += term
        next_term = term * value / (k + 1)
        tail = next_term / (1 - value / (k + 2))
        if tail < EPS:
            return total, total + tail


def moment(histogram, m, live, saving):
    low, high = Q(0), Q(0)
    for rank, count in histogram.items():
        lo, hi = log_ratio(m, rank)
        a = exponential(saving * lo)[0]
        b = exponential(saving * hi)[1]
        scale = Q(count * rank, m * live)
        low += scale * a
        high += scale * b
    return low, high
