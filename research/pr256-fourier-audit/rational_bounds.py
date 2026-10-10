"""Exact rational bounds used by the Fourier extension verifier.

These helpers enclose logarithms and derived exponent savings with rational
arithmetic. Decimal formatting is for display only. Network counts and proof
obligations are supplied and checked by verify_extension.py.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from fractions import Fraction as F

def series_bounds(y: F, terms: int) -> tuple[F, F]:
    """Rigorous natural-log enclosure for rational 1 <= y <= 2."""
    if not (1 <= y <= 2) or terms < 1:
        raise ValueError('series requires 1 <= y <= 2 and terms >= 1')
    z = (y-1)/(y+1)
    z2 = z*z
    t, s = z, F(0)
    for j in range(terms):
        s += t/(2*j+1)
        t *= z2
    lo = 2*s
    tail = 2*t/((2*terms+1)*(1-z2))
    return lo, lo+tail

def log_bounds(x: F) -> tuple[F, F]:
    """Range reduction plus exact atanh series; x is rational and >= 1."""
    if x < 1:
        raise ValueError('x must be >= 1')
    y, k = x, 0
    while y > 2:
        y /= 2
        k += 1
    t = 6 if y < F(1001,1000) else 40
    lo, hi = series_bounds(y, t)
    l2, u2 = series_bounds(F(2), 40)
    return lo+k*l2, hi+k*u2

def saving_bounds(c: dict) -> tuple[F, F]:
    eta = c['eta']
    if not (0 < eta < 1):
        raise ValueError('positive contraction required')
    nl, nu = log_bounds(1/(1-eta))
    dl, du = log_bounds(F(c['m']))
    return nl/du, nu/dl

def decimal(x: F, precision: int = 36) -> str:
    with localcontext() as ctx:
        ctx.prec = precision
        return str(Decimal(x.numerator)/Decimal(x.denominator))

def frac_json(x: F) -> dict:
    return {'numerator': str(x.numerator), 'denominator': str(x.denominator)}
