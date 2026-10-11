"""Rational bounds used by the rate lemmas (library; used by foldlib.py).

log_upper(m, r, D): a rational upper bound L of log(m/r) with D decimals and the number N of terms of the
exponential series with  m/r <= sum_{i<N} L^i / i!  (checked exactly here; Lean re-checks it with `norm_num`).
frac_lean(q): a rational as Lean text.
Nothing is trusted from this file: Lean re-checks every inequality.
"""
from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_CEILING
getcontext().prec = 80


def log_upper(m, r, D):
    x = (Decimal(m).ln() - Decimal(r).ln()) * Decimal(10) ** D
    L = Fraction(int(x.to_integral_value(rounding=ROUND_CEILING)) + 1, 10 ** D)
    # number of series terms
    target = Fraction(m, r)
    s, term, N = Fraction(0), Fraction(1), 0
    while s < target:
        s += term
        N += 1
        term = term * L / N
        assert N < 400
    return L, N


def frac_lean(q, typ="ℝ"):
    if q.denominator == 1:
        return "(%d:%s)" % (q.numerator, typ)
    return "((%d:%s)/%d)" % (q.numerator, typ, q.denominator)
