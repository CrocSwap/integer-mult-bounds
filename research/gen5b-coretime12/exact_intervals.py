"""Original rational log/exp enclosures; upstream programs are never run.

Atanh series uses 64 terms and an explicit positive tail. Exponential series
uses 32 terms with a geometric upper bound for its tail, on arguments <= 1.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
from functools import lru_cache
GRID=10**50
def floor_grid(x):
    return F((x * GRID).numerator // (x * GRID).denominator, GRID)


def ceil_grid(x):
    return -floor_grid(-x)


@lru_cache(None)
def log_interval(x):
    """ln(x), x>=1, binary reduction and 64-term positive atanh series."""
    x = F(x)
    if x < 1:
        raise ValueError('log argument must be at least one')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def short(y):
        z = (y - 1) / (y + 1)
        power, total = z, F(0)
        for j in range(64):
            total += 2 * power / (2*j + 1)
            power *= z*z
        return total, total + 2*power / (129*(1-z*z))
    lo, hi = short(x)
    a, b = short(F(2))
    return floor_grid(lo+k*a), ceil_grid(hi+k*b)


def exp_interval(lo, hi):
    if not 0 <= lo <= hi <= 1:
        raise ValueError('exponential interval is outside certified range')
    def poly(x):
        term = total = F(1)
        for n in range(1, 33):
            term = term*x/n
            total += term
        return total, term
    low, _ = poly(lo)
    high, term = poly(hi)
    tail = (term*hi/33) / (1-hi/34)
    return floor_grid(low), ceil_grid(high+tail)


def moment_interval(m, W, histogram, a):
    W, a = F(W), F(a)
    if not isinstance(m, int) or m <= 1 or W <= 0 or not 0 <= a < 1:
        raise ValueError('invalid moment dimensions or exponent')
    lo = hi = F(0)
    for r, n in histogram.items():
        if not isinstance(r, int) or not 0 < r < m or F(n) <= 0:
            raise ValueError('invalid positive-rank child')
        L, U = log_interval(F(m,r))
        E, G = exp_interval(a*L,a*U)
        weight = F(n)*r/(m*W)
        lo += weight*E
        hi += weight*G
    return lo, hi


def dec(x):
    x = F(x)
    with localcontext() as c:
        c.prec = 45
        return str(Decimal(x.numerator)/Decimal(x.denominator))

