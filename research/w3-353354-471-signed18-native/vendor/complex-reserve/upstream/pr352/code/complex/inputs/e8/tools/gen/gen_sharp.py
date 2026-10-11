"""Rational LOWER bounds of logarithms used by the sharpness lemmas (library; used by foldlib.py, foldgen.py).

log_lower(m, r, D): a rational lower bound L of log(m/r) (D decimals), certified by
   (sum_{i<n} y^i/i! + y^n (n+1)/(n! n))^(2^s) <= m/r,  y = L/2^s <= 1/2     (checked exactly here, re-checked by Lean).
"""
from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_FLOOR
getcontext().prec = 80


def log_lower(m, r, D):
    x = (Decimal(m).ln() - Decimal(r).ln()) * Decimal(10) ** D
    L = Fraction(int(x.to_integral_value(rounding=ROUND_FLOOR)) - 1, 10 ** D)
    assert L > 0
    s = 0
    while L / 2 ** s > Fraction(1, 2):
        s += 1
    y = L / 2 ** s
    target = Fraction(m, r)
    n = 2
    while True:
        S, term = Fraction(0), Fraction(1)
        for i in range(n):
            S += term
            term = term * y / (i + 1)
        fact = 1
        for i in range(2, n + 1):
            fact *= i
        U = S + y ** n * (n + 1) / (fact * n)
        if U ** (2 ** s) <= target:
            return L, s, n
        n += 1
        assert n < 60
