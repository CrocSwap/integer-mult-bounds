"""Certified (rational interval) pressure-root tools.
g_q(r) = r*((m/r)^q - 1).  Root of  sum_i z_i g_q(r_i) = D  (increasing in q).
All transcendental values are enclosed by rational intervals (Fraction endpoints, outward rounding)."""
from fractions import Fraction as Fr
import math

DEN = 10**45          # outward rounding grid


def rd(x):            # round down to grid
    return Fr(math.floor(x * DEN), DEN)


def ru(x):
    return Fr(math.ceil(x * DEN), DEN)


def ln_iv(x):
    """enclosure of ln(x), x = Fraction > 0, via ln x = 2 atanh(z), z=(x-1)/(x+1); reduce by powers of 2."""
    x = Fr(x)
    assert x > 0
    if x == 1:
        return (Fr(0), Fr(0))
    # reduce: x = 2^e * y, y in [1/sqrt2, sqrt2]  (use [2/3, 4/3]-ish via loop)
    e = 0
    while x > Fr(4, 3):
        x /= 2; e += 1
    while x < Fr(2, 3):
        x *= 2; e -= 1
    lo2, hi2 = LN2
    lo, hi = _atanh2(x)
    return (rd(lo + e * (lo2 if e >= 0 else hi2)), ru(hi + e * (hi2 if e >= 0 else lo2)))


def _atanh2(x):
    z = (x - 1) / (x + 1)
    az = abs(z)
    s = Fr(0); t = z; k = 0
    N = 40
    for k in range(N):
        s += t / (2 * k + 1)
        t *= z * z
    # tail bound: |sum_{k>=N} z^(2k+1)/(2k+1)| <= |z|^(2N+1)/((2N+1)(1-z^2))
    tail = az ** (2 * N + 1) / ((2 * N + 1) * (1 - z * z))
    s = 2 * s; tail = 2 * tail
    return (rd(s - tail), ru(s + tail))


def _ln2():
    # ln 2 = 2 atanh(1/3)
    z = Fr(1, 3); s = Fr(0); t = z
    N = 60
    for k in range(N):
        s += t / (2 * k + 1); t *= z * z
    tail = z ** (2 * N + 1) / ((2 * N + 1) * (1 - z * z))
    return (rd(2 * s - 2 * tail), ru(2 * s + 2 * tail))


LN2 = _ln2()


def expm1_iv(lo, hi):
    """enclosure of e^y - 1 for y in [lo,hi], 0 <= lo <= hi <= 1."""
    assert 0 <= lo <= hi <= 2
    N = 30

    def ser(y):
        s = Fr(0); t = Fr(1)
        for i in range(1, N + 1):
            t = t * y / i; s += t
        return s
    slo = ser(lo)                         # all terms >= 0 -> lower bound
    shi = ser(hi) + 8 * hi ** (N + 1) / math.factorial(N + 1)   # tail <= y^(N+1)/(N+1)! * e^y, e^y<=8 (y<=2)
    return (rd(slo), ru(shi))


def g_iv(r, m, q):
    """enclosure of r*((m/r)^q - 1), q Fraction >= 0."""
    if r >= m:
        return (Fr(0), Fr(0)) if r == m else None
    l_lo, l_hi = ln_iv(Fr(m) / r)
    lo, hi = expm1_iv(q * l_lo, q * l_hi)
    return (r * lo, r * hi)


def F_iv(prof, m, q):
    """prof: dict rank -> count (Fractions/ints allowed), returns enclosure of sum z g_q(r)."""
    lo = Fr(0); hi = Fr(0)
    for r, z in prof.items():
        if z == 0:
            continue
        a, b = g_iv(Fr(r), Fr(m), Fr(q))
        lo += z * a; hi += z * b
    return (rd(lo), ru(hi))


def root_bracket(prof, m, D, lo=Fr(0), hi=Fr(1, 10), iters=60):
    """returns (qlo, qhi) with F(qlo) < D (certified via upper enclosure) and F(qhi) >= D (via lower enclosure):
       the true root lies in [qlo, qhi]. qhi is a certified UPPER bound of the root."""
    D = Fr(D)
    assert F_iv(prof, m, hi)[0] >= D, 'hi too small'
    for _ in range(iters):
        mid = rd((lo + hi) / 2)
        flo, fhi = F_iv(prof, m, mid)
        if flo >= D:
            hi = mid
        elif fhi < D:
            lo = mid
        else:
            break
    return lo, hi


def cost_iv(prof, m):
    """enclosure of Cost = sum z r ln(m/r)."""
    lo = Fr(0); hi = Fr(0)
    for r, z in prof.items():
        if z == 0 or r >= m:
            continue
        a, b = ln_iv(Fr(m) / r)
        lo += z * r * a; hi += z * r * b
    return lo, hi


if __name__ == '__main__':
    # self-test against floats
    for x in (Fr(64, 7), Fr(73, 8), Fr(100, 3), Fr(3, 2), Fr(1, 5)):
        lo, hi = ln_iv(x)
        assert lo <= Fr(math.log(x)) + Fr(1, 10**12) and hi >= Fr(math.log(x)) - Fr(1, 10**12), x
        assert hi - lo < Fr(1, 10**40), (x, float(hi - lo))
    print('ln ok', float(LN2[1] - LN2[0]))
    lo, hi = expm1_iv(Fr(1, 100), Fr(1, 100))
    print('expm1(0.01)', float(lo), math.expm1(0.01), float(hi - lo))
