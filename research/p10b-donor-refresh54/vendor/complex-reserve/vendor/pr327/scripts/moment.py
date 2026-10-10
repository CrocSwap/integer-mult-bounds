#!/usr/bin/env python3
"""Exact upper bound of the batched tensor moment  sum_rho n_rho (rho/m)^theta,  theta = 1 - a.

Adapted from scripts/verify_moment.py of eumemic/exact-dft-bounds (eumemic, Claude assistance, Apache-2.0),
commit 6f87d1a0c9ae462cdcb2034a1361c87623221e66, which this package credits for the batched tensor recursion
(Theorem 3.1 there) and these bounds:
    (rho/m)^theta = (rho/m) * exp(a * ln(m/rho)),
    ln(x) <= 2*sum_{j<J} y^(2j+1)/(2j+1) + 2*y^(2J+1)/((2J+1)(1-y^2)),  y = (x-1)/(x+1),
    exp(x) <= 1 + x + x^2/(2(1 - x/3))  for 0 <= x < 3.
All arithmetic is exact rational; the result is an upper bound of the moment, so a positive margin is a proof.
"""
from fractions import Fraction


def ln_upper(x, terms=4000):
    assert x >= 1
    y = (x - 1) / (x + 1)
    y2 = y * y
    grid = 10**60
    s = 0
    p = y
    for j in range(terms):
        k = 2 * j + 1
        t = p / k
        s += -((-t.numerator * grid) // t.denominator)
        p *= y2
        if p < Fraction(1, 10**70):
            break
    k = 2 * (j + 1) + 1
    tail = 2 * p / (k * (1 - y2))
    return Fraction(2 * s, grid) + tail


def exp_upper(x):
    assert 0 <= x < 3
    return 1 + x + x * x / (2 * (1 - x / 3))


def moment_margin(m, W, hist, a):
    """W minus an exact upper bound of sum_rho n_rho (rho/m)^(1-a); positive means the moment is below W."""
    assert all(1 <= r < m for r in hist), 'every child must be strictly narrower than a role'
    total = Fraction(0)
    for r, n in sorted(hist.items()):
        total += n * Fraction(r, m) * exp_upper(a * ln_upper(Fraction(m, r)))
    return W - total, total
