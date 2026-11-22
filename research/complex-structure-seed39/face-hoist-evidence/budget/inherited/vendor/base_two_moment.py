#!/usr/bin/env python3
"""Maintainer arithmetic cross-check of the pinned PR39 certificate.

Uses no producer/checker imports. Counts are inputs, not proved by this script.
80-term rational logarithms and 12-term exponentials independently enclose
the two moments. The accompanying written review addresses their realization.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRID = 10**30


def require(condition, message):
    if not condition:
        raise ValueError(message)


def log_unit(x):
    require(1 <= x <= 2, "logarithm range")
    z = (x-1)/(x+1)
    lo = 2*sum((z**(2*j+1)/(2*j+1) for j in range(80)), Q(0))
    return lo, lo+2*z**161/(161*(1-z*z))


def log_bounds(x):
    k = 0
    while x > 2:
        x /= 2
        k += 1
    lo, hi = log_unit(x)
    l2, u2 = log_unit(Q(2))
    lo, hi = lo+k*l2, hi+k*u2
    # Outward rational rounding keeps later certificates compact.
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)


def exp_bounds(x):
    require(0 <= x < 1, "exponential range")
    term = total = Q(1)
    for j in range(1, 13):
        term *= x/j
        total += term
    tail = term*x/13/(1-x/14)
    return total, total+tail


def moment(m, W, entries, saving):
    lo = hi = Q(0)
    for t, count in entries:
        t, count = int(t), int(count)
        require(0 < t < m and count > 0, "improper child")
        l, u = log_bounds(Q(m, t))
        lower = exp_bounds(saving*l)[0]
        upper = exp_bounds(saving*u)[1]
        lo += Q(t*count, m*W)*lower
        hi += Q(t*count, m*W)*upper
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)

