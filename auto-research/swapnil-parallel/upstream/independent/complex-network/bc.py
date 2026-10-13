"""Certified bounds on exp and ln, in exact rationals."""
from fractions import Fraction as Q
from math import comb
from decimal import Decimal as D, getcontext
getcontext().prec = 80

def exp_lower(U, k=10, terms=30):
    # positive Taylor partial sum of exp(U/2^k), squared k times, rounded down: rigorous lower bound
    x = U / 2**k; s = Q(0); t = Q(1)
    for j in range(1, terms): s += t; t = t * x / j
    for _ in range(k):
        s = s * s; s = Q(s.numerator * 10**40 // s.denominator, 10**40)
    return s

def ln_upper(x, rel=Q(1, 10**9)):
    # rational U with exp(U) > x  (so U > ln x), within ~rel of ln x
    lx = D(x.numerator).ln() - D(x.denominator).ln()
    den = 10**12
    U = Q(int(lx * den) + 1, den) * (1 + rel)
    assert exp_lower(U) > x
    return U
