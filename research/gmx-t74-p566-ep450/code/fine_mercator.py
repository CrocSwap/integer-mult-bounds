"""Finer-constant copy of the retained Mercator moment engine (engines/moment.py): retained log algorithm, outward-rounded integer Taylor recurrence,
DYAD 2^1800 outward rounding, 1800 Mercator terms (tail bounded by the next term), 150 exponential terms."""
from fractions import Fraction as F
from functools import lru_cache
DYAD = 1 << 1800
LOGN = 1801
EXPN = 150
def floor(x): return F(x.numerator*DYAD//x.denominator, DYAD)
def ceil(x): return -floor(-x)

def mercator(y):
    """Enclosure [s, s + next term] of log(y) for 1 <= y <= 3/2 by the alternating Mercator series in z = y-1."""
    z = y - 1
    assert 0 <= z <= F(1, 2)
    assert (LOGN - 1) % 2 == 0, 'an even number of terms is required: an odd partial sum lies above the log'
    t = z; s = F(0)
    for n in range(1, LOGN):
        s += (t if n & 1 else -t) / n
        t *= z
    return s, s + t / LOGN

@lru_cache(None)
def logarithm(x):
    assert x >= 1
    k = 0
    while x >= 2: x /= 2; k += 1
    j = int(x >= F(3, 2))
    if j: x /= F(3, 2)
    a, b = mercator(x); c, d = mercator(F(3, 2)); e, f = mercator(F(4, 3))
    return floor(a + (k + j) * c + k * e), ceil(b + (k + j) * d + k * f)

def exponential(l, u):
    """Outward-rounded Taylor recurrence; every integer is in units 1/DYAD."""
    assert 0 <= l <= u < F(1, 10)
    a = l.numerator * DYAD // l.denominator
    b = -(-u.numerator * DYAD // u.denominator)
    tl = tu = sl = su = DYAD
    for j in range(1, EXPN):
        tl = tl * a // (j * DYAD)
        tu = -(-tu * b // (j * DYAD))
        sl += tl; su += tu
    den = EXPN * (DYAD * (EXPN + 1) - b)
    assert den > 0
    tail = -(-tu * b * (EXPN + 1) // den)
    return F(sl, DYAD), F(su + tail, DYAD)

def moment(H, m, W, a, bad=False):
    lo = hi = F(0)
    for r, n in H.items():
        assert 0 < r < m and n > 0
        l, u = logarithm(F(m, r)); e, f = exponential(a * l, a * u)
        p = F(r * n, m * W); lo += p * e; hi += p * f
    if bad:
        l, u = logarithm(F(m)); e, f = exponential(a * l, a * u)
        p = F(32 * m * sum(H.values()), 10**16 * W)
        lo += p * e; hi += p * f
    return floor(lo), ceil(hi)
