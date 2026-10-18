# SPDX-License-Identifier: Apache-2.0
"""Code-disjoint exact interval arithmetic for complex-moment endpoints and the kappa reduction.

Imports nothing from the retained engines (moment.py, base_two_moment.py, outer.py).
Extends the arithmetic of research/t37-endpoints-independent (PR1051) to every prime:
    ln 2 = 2 atanh(1/3),  ln p = ln(p-1) + 2 atanh(1/(2p-1))  for odd primes p,
since p/(p-1) = (1+t)/(1-t) with t = 1/(2p-1) <= 1/5. atanh tails use the geometric bound
t^(2K+1) / ((2K+1)(1-t^2)); exp uses a Taylor polynomial with remainder 2 y^(K+1)/(K+1)!;
all intervals are exact rationals rounded outward to multiples of 2^-PREC.
"""
from fractions import Fraction as Q
from functools import lru_cache

PREC = 320
TERMS = 120
TAYLOR = 16


def require(ok, message):
    if not ok:
        raise ValueError(message)


def down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x):
    return -down(-x)


class I:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        hi = lo if hi is None else hi
        require(lo <= hi, 'interval order')
        self.lo, self.hi = down(Q(lo)), up(Q(hi))

    def __add__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = o if isinstance(o, I) else I(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return I(min(p), max(p))

    __radd__ = __add__
    __rmul__ = __mul__


def atanh(t):
    t = Q(t)
    require(0 < t <= Q(1, 3), 'atanh argument')
    s, power = Q(0), t
    for k in range(TERMS):
        s += power / (2 * k + 1)
        power *= t * t
    return I(s, s + power / ((2 * TERMS + 1) * (1 - t * t)))


def is_prime(p):
    return p >= 2 and all(p % d for d in range(2, int(p ** 0.5) + 1))


@lru_cache(None)
def ln_prime(p):
    require(is_prime(p), 'not a prime')
    if p == 2:
        return 2 * atanh(Q(1, 3))
    return ln_int(p - 1) + 2 * atanh(Q(1, 2 * p - 1))


@lru_cache(None)
def ln_int(k):
    require(k >= 1, 'positive integer')
    out, d = I(0), 2
    while k > 1:
        while k % d == 0:
            out = out + ln_prime(d)
            k //= d
        d += 1
    return out


def exp_small(y):
    require(0 <= y.lo and y.hi < Q(1, 100), 'exp range')
    lo = hi = tlo = thi = Q(1)
    for k in range(1, TAYLOR + 1):
        tlo = down(tlo * y.lo / k)
        thi = up(thi * y.hi / k)
        lo += tlo
        hi += thi
    return I(lo, hi + thi * y.hi / (TAYLOR + 1) * 2)


def moment(H, m, W, z, surcharge=False):
    total = I(0)
    lm = ln_int(m)
    for r, n in H.items():
        require(0 < r < m, 'child rank range')
        total = total + I(Q(r * n, m * W)) * exp_small((lm - ln_int(r)) * I(z))
    if surcharge:
        total = total + I(Q(32 * m * sum(H.values()), 10 ** 16 * W)) * exp_small(lm * I(z))
    return total


def certify(H, m, W, b, grid=Q(1, 10 ** 24), surcharge=False):
    at, nxt = moment(H, m, W, b, surcharge), moment(H, m, W, b + grid, surcharge)
    require(at.hi < 1, 'moment not below one at the endpoint')
    require(nxt.lo > 1, 'moment not above one at the next grid point')
    return (float(at.hi - 1), float(nxt.lo - 1))


def kappa_from(b, c, grid=Q(1, 10 ** 18)):
    """Selected T37 reduction: s = min(c, (1-beta) b) - 10^-27, seven bootstrap steps from 384599/10^10,
    q = a7 (1 - 2 eta), kappa = largest grid point strictly below (1 - eta) q / (1 + q); eta = beta = 10^-24."""
    eta = beta = Q(1, 10 ** 24)
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 27)
    a = Q(384599, 10 ** 10)
    for _ in range(7):
        a = (1 - s) * s + s * a
    q = a * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    t = margin / grid
    k = (-((-t.numerator) // t.denominator) - 1) * grid
    require(k < margin <= k + grid, 'grid reduction')
    return k, margin, ('bit' if c <= (1 - beta) * b else 'complex')
