"""CERTKIT numeric engine: exact Fraction mirror of Nov15/CertKitCore.lean (rdn/rup, expLo/expHi, log table,
phiLo/phiHi, ubP/lbP/tailP) + piece search.  Pure stdlib, 1 thread.  Every function here must stay bit-identical
to its Lean twin: the Lean side re-checks the emitted certificate with `decide +kernel`, so a mismatch only makes
the Lean build fail (never unsound), but it wastes a build."""
from fractions import Fraction as Q
from decimal import Decimal, getcontext
import math

PB = 128
NE = 24
S = 1 << PB


def rdn(q):
    return Q(math.floor(q * S), S)


def rup(q):
    return Q(math.ceil(q * S), S)


def expSum(x, n):
    s = Q(0)
    for m in range(n):
        s += x ** m / math.factorial(m)
    return s


def expErr(x, n):
    return abs(x) ** n * (Q(n + 1) / (math.factorial(n) * n))


def eLo0(x):
    return max(Q(0), rdn(expSum(x, NE) - expErr(x, NE)))


def eHi0(x):
    return rup(expSum(x, NE) + expErr(x, NE))


def eLo(j, x):
    if j == 0:
        return eLo0(x)
    a = eLo(j - 1, x / 2)
    return rdn(a * a)


def eHi(j, x):
    if j == 0:
        return eHi0(x)
    a = eHi(j - 1, x / 2)
    return rup(a * a)


def jOf(x):
    j, f = 0, 12
    while f > 0:
        if abs(x) <= Q(2 ** j, 4):
            return j
        j += 1
        f -= 1
    return j


def expLo(x):
    j = jOf(x)
    return eLo(j, x) if abs(x) <= 2 ** j else Q(0)


def expHi(x):
    j = jOf(x)
    return eHi(j, x) if abs(x) <= 2 ** j else Q(1)


def lnSum(x, n):
    s = Q(0)
    for i in range(n):
        s += x ** (i + 1) / (i + 1)
    return s


def lnErr(x, n):
    return x ** (n + 1) / (1 - x)


def log_table(R):
    """entries k = 0..R-1 bound log(k+1): (lo, hi, n) with n = series terms for the step k+1 -> k+2."""
    tb = []
    lo = hi = Q(0)
    for m in range(1, R + 1):
        if m == R:
            tb.append((lo, hi, 0))
            break
        x = Q(1, m + 1)
        n = 1
        while lnErr(x, n) > Q(1, 1 << (PB + 8)):
            n += 1
        tb.append((lo, hi, n))
        s, e = lnSum(x, n), lnErr(x, n)
        lo, hi = rdn(lo + (s - e)), rup(hi + (s + e))
    return tb


class Cert:
    def __init__(self, cs):
        self.cs = cs
        self.R = max(r for _, r in cs)
        self.tb = log_table(self.R)
        self._lo = {}; self._hi = {}

    def phiLo(self, r, t):
        k = (r, t)
        if k not in self._lo:
            self._lo[k] = rdn(r * expLo(rdn(-(t * self.tb[r - 1][1]))))
        return self._lo[k]

    def phiHi(self, r, t):
        k = (r, t)
        if k not in self._hi:
            self._hi[k] = rup(r * expHi(min(Q(0), rup(-(t * self.tb[r - 1][0])))))
        return self._hi[k]

    def ubP(self, a, b):
        return sum((c * self.phiHi(r, a) if c > 0 else c * self.phiLo(r, b)) for c, r in self.cs)

    def lbP(self, a, b):
        return sum((c * self.phiLo(r, b) if c > 0 else c * self.phiHi(r, a)) for c, r in self.cs)

    def tailP(self, a):
        return sum((c * self.phiHi(r, a) if c > 0 else (Q(c) if r == 1 else Q(0))) for c, r in self.cs)


# ---- fast approximate model (Decimal, 60 digits) for the piece search -----------------------------------------
getcontext().prec = 60


def Fd(cs, t):
    t = Decimal(t.numerator) / Decimal(t.denominator) if isinstance(t, Q) else Decimal(t)
    return sum(Decimal(c) * (Decimal(r) ** (1 - t)) for c, r in cs)


def ub_d(cs, a, b):
    a = Decimal(a.numerator) / Decimal(a.denominator); b = Decimal(b.numerator) / Decimal(b.denominator)
    return sum(Decimal(c) * Decimal(r) ** (1 - (a if c > 0 else b)) for c, r in cs)


def lb_d(cs, a, b):
    a = Decimal(a.numerator) / Decimal(a.denominator); b = Decimal(b.numerator) / Decimal(b.denominator)
    return sum(Decimal(c) * Decimal(r) ** (1 - (b if c > 0 else a)) for c, r in cs)


def tail_d(cs, a):
    a = Decimal(a.numerator) / Decimal(a.denominator)
    return sum((Decimal(c) * Decimal(r) ** (1 - a) if c > 0 else (Decimal(c) if r == 1 else 0)) for c, r in cs)


def snap(x, bits=64):
    """a short dyadic just below x (x > 0)."""
    return Q(math.floor(x * (1 << bits)), 1 << bits)


def snap_up(x, bits=64):
    return Q(math.ceil(x * (1 << bits)), 1 << bits)


def up_pieces(C, hi, safety=Q(9, 10), maxp=400):
    """grid hi = g0 < g1 < ... < gm with ubP(g_i, g_i+1) < 0 and tailP(gm) < 0 (exactly checked)."""
    cs = C.cs; g = [hi]; a = hi
    while True:
        if tail_d(cs, a) < 0 and C.tailP(a) < 0:
            return g
        # largest b with ub(a, b) < 0 (ub increasing in b): doubling + bisection on the Decimal model
        h = max(a * Q(1, 10 ** 6), Q(1, 10 ** 30)); lo_h = Q(0)
        while ub_d(cs, a, a + 2 * h) < 0 and h < 4:
            h *= 2
        if ub_d(cs, a, a + h) >= 0:
            hi_h = h; h = h / 2
            while ub_d(cs, a, a + h) >= 0 and h > Q(1, 10 ** 40):
                hi_h = h; h /= 2
        for _ in range(6):
            m = h * Q(3, 2)
            if ub_d(cs, a, a + m) < 0:
                h = m
        b = snap(a + h * safety)
        while not (b > a and C.ubP(a, b) < 0):
            h = h / 2; b = snap(a + h, 96)
            if h < Q(1, 10 ** 45):
                raise RuntimeError('up piece failed at %s' % float(a))
        g.append(b); a = b
        if len(g) > maxp:
            raise RuntimeError('too many up pieces')


def lo_pieces(C, lo, safety=Q(9, 10), maxp=400):
    """grid 0 = g0 < ... < gm = lo with lbP(g_i, g_i+1) > 0 (exactly checked)."""
    cs = C.cs; g = [Q(0)]; a = Q(0)
    while True:
        if lb_d(cs, a, lo) > 0 and C.lbP(a, lo) > 0:
            g.append(lo)
            return g
        h = (lo - a) / 2
        while lb_d(cs, a, a + h) <= 0 and h > Q(1, 10 ** 40):
            h /= 2
        for _ in range(6):
            m = h * Q(3, 2)
            if a + m < lo and lb_d(cs, a, a + m) > 0:
                h = m
        b = snap(a + h * safety, 96)
        while not (a < b < lo and C.lbP(a, b) > 0):
            h = h / 2; b = snap(a + h, 96)
            if h < Q(1, 10 ** 45):
                raise RuntimeError('lo piece failed at %s' % float(a))
        g.append(b); a = b
        if len(g) > maxp:
            raise RuntimeError('too many lo pieces')
