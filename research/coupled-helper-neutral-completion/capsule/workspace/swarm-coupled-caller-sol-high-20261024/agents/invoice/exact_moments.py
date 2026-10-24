#!/usr/bin/env python3
"""Independent directed-rational moment arithmetic for construction-sensitive invoices.

No provider/candidate evaluator is imported. This does not establish reachability,
target autonomy, native phases, precision or any complete compiler admission.
Construction credit remains with the provider/controller/native predecessors.
Chris R/Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRECISION = 10 ** 65


def need(x, text):
    if not x:
        raise ValueError(text)


def floorq(x):
    return F(x.numerator * PRECISION // x.denominator, PRECISION)


def ceilq(x):
    return -floorq(-x)


@lru_cache(None)
def logarithm(n):
    need(type(n) is int and n >= 1, 'positive integer rank')
    a = n.bit_length() - 1

    def local(q):
        z = (q - 1) / (q + 1)
        need(0 <= z <= F(1, 3), 'log range')
        total, term = F(0), z
        for j in range(72):
            total += 2 * term / (2 * j + 1)
            term *= z * z
        remainder = 2 * term / (145 * (1 - z * z))
        return floorq(total), ceilq(total + remainder)

    lo, hi = local(F(n, 2 ** a))
    l2, u2 = local(F(2))
    return lo + a * l2, hi + a * u2


def expbound(q):
    if q < 0:
        lo, hi = expbound(-q)
        return floorq(1 / hi), ceilq(1 / lo)
    squarings = 0
    while q > F(1, 64):
        q /= 2
        squarings += 1
    term = total = F(1)
    for j in range(1, 41):
        term *= q / j
        total += term
    remainder = term * q / 41 / (1 - q / 42)
    lo, hi = floorq(total), ceilq(total + remainder)
    for _ in range(squarings):
        lo, hi = floorq(lo * lo), ceilq(hi * hi)
    return lo, hi


@lru_cache(None)
def power(rank, exponent):
    lo, hi = logarithm(rank)
    a, b = sorted([lo * exponent, hi * exponent])
    return expbound(a)[0], expbound(b)[1]


def moment(profile, exponent):
    lo = hi = F(0)
    for rank, count in profile.items():
        a, b = power(int(rank), exponent)
        lo += count * a
        hi += count * b
    return lo, hi


def minus(a, b):
    return a[0] - b[1], a[1] - b[0]


def homogeneous_limit(budget, rank, exponent):
    """Largest n with certified n*rank^exponent < budget lower bound."""
    lo, hi = power(rank, exponent)
    n = budget[0] // hi
    if n * hi >= budget[0]:
        n -= 1
    need(n >= 0, 'negative strict allowance')
    return {'certified_maximum': n,
            'accepted_upper': n * hi,
            'budget_lower': budget[0],
            'next_cost_lower': (n + 1) * lo,
            'next_rejected': (n + 1) * lo >= budget[1]}


def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x

