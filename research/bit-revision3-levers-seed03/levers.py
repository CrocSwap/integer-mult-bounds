# SPDX-License-Identifier: Apache-2.0
"""Exact, standard-library tools for bit-side lever budgets (and the complex cross-check).

Model (the coverage-law relaxation of #1240, applied to the PR589 bit supplier):
  per call, the paid children are a local histogram L (rank -> count, fractional allowed) plus idle
  children carrying the remaining rank mass (m - u) w + cst - mass(L) at one rank R (fractional);
  the per-call bill at saving a is  B(a) = (1/w) sum_r n_r (r/m)^(1-a),  increasing in a.
  w = live families per call, u = unpaid coordinates per family (1 today), cst = per-call copy charge.
A configuration reaches saving a iff B(a) < 1. Every number below is an exact rational interval:
ln via atanh prime chains, exp via Taylor series with a remainder bound, outward dyadic rounding.
"""
from fractions import Fraction as Q
from functools import lru_cache

PREC = 200


class Reject(Exception):
    """A check failed; the argument is its label."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def _down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def _up(x):
    return -_down(-x)


@lru_cache(None)
def atanh(t):
    s, p, k = Q(0), t, 0
    while True:
        s += p / (2 * k + 1)
        p *= t * t
        k += 1
        tail = p / ((2 * k + 1) * (1 - t * t))
        if tail < Q(1, 1 << (PREC + 8)):
            return _down(s), _up(s + tail)


@lru_cache(None)
def ln(k):
    """Interval for ln k, k a positive integer: ln k = ln(k-1) + 2 atanh(1/(2k-1))."""
    if k == 1:
        return Q(0), Q(0)
    lo, hi = ln(k - 1)
    a, b = atanh(Q(1, 2 * k - 1))
    return _down(lo + 2 * a), _up(hi + 2 * b)


def exp_iv(lo, hi):
    """Interval for exp on [lo, hi] with 0 <= lo <= hi < 1."""
    def series(y, upper):
        s, t, k = Q(1), Q(1), 0
        while True:
            k += 1
            t = t * y / k
            s += t
            if t * y < Q(1, 1 << (PREC + 8)):
                return _up(s + 2 * t * y / (k + 1)) if upper else _down(s)
    return series(lo, False), series(hi, True)


def child(r, m, a):
    """Interval for (r/m)^(1-a) = (r/m) exp(a ln(m/r)), integer r <= m, 0 <= a < 1."""
    lm, um = ln(m)
    lr, ur = ln(r)
    e = exp_iv(max(Q(0), a * (lm - ur)), a * (um - lr))
    return _down(Q(r, m) * e[0]), _up(Q(r, m) * e[1])


def bill(H, m, w, a, surcharge=False):
    """Interval for (1/w) sum_r n_r (r/m)^(1-a) [+ the inherited bad-residue surcharge 32 m N m^a / 1e16 / w]."""
    lo = hi = Q(0)
    for r, n in H.items():
        if n:
            c = child(r, m, a)
            lo += Q(n) * c[0]
            hi += Q(n) * c[1]
    if surcharge:
        N = sum(Q(n) for n in H.values())
        c = child(1, m, a)                       # (1/m)^(1-a): 32 m^2 N c / 1e16 = 32 m N m^a / 1e16
        lo += Q(32 * m * m) * N * c[0] / 10 ** 16
        hi += Q(32 * m * m) * N * c[1] / 10 ** 16
    return _down(lo / w), _up(hi / w)


def relaxed(local, m, w, cst, R, unpaid=1):
    """Per-call histogram: the local children plus all remaining coverage-law mass at rank R."""
    total = (m - unpaid) * Q(w) + Q(cst)
    mass = sum(Q(r) * Q(n) for r, n in local.items())
    need(mass <= total, 'local mass exceeds the coverage law')
    need(0 < R < m and all(0 < r < m for r in local), 'child ranks must lie in (0, m)')
    H = {r: Q(n) for r, n in local.items() if n}
    if total > mass:
        H[R] = H.get(R, Q(0)) + (total - mass) / R
    return H


def verdict(H, m, w, a, surcharge=False):
    """'pass' (certified B(a) < 1), 'fail' (certified B(a) > 1) or 'undecided'."""
    lo, hi = bill(H, m, w, a, surcharge)
    return 'pass' if hi < 1 else 'fail' if lo > 1 else 'undecided'


def root(H, m, w, surcharge=False, tol=Q(1, 10 ** 13), top=Q(1, 20)):
    """Certified bracket [lo, hi] of the saving where B = 1: B(lo) < 1 < B(hi) certified, hi - lo <= tol."""
    lo, hi = Q(0), top
    need(verdict(H, m, w, lo, surcharge) == 'pass' and verdict(H, m, w, hi, surcharge) == 'fail', 'root not bracketed')
    while hi - lo > tol:
        mid = (lo + hi) / 2
        v = verdict(H, m, w, mid, surcharge)
        if v == 'pass':
            lo = mid
        elif v == 'fail':
            hi = mid
        else:
            raise Reject('interval too wide to bisect')
    return lo, hi


def dec(x, digits=10):
    return format(float(x), '.%dg' % digits)


def max_count(base, extra_rank, m, w, cst, R, a, limit):
    """Largest k (0..limit) such that base + k children of rank extra_rank passes at a; None if k=0 fails.

    Returns (k, verdict_k, verdict_k_plus_1) with both verdicts certified (k+1 must fail or exceed limit).
    """
    def ok(k):
        local = dict(base)
        local[extra_rank] = local.get(extra_rank, 0) + k
        try:
            return verdict(relaxed(local, m, w, cst, R), m, w, a)
        except Reject:
            return 'fail'                         # exceeds the coverage law: no idle room left
    if ok(0) != 'pass':
        return None
    lo, hi = 0, limit
    while lo < hi:
        mid = (lo + hi + 1) // 2
        v = ok(mid)
        need(v != 'undecided', 'undecided boundary')
        if v == 'pass':
            lo = mid
        else:
            hi = mid - 1
    nxt = ok(lo + 1) if lo < limit else 'limit'
    return lo, 'pass', nxt
