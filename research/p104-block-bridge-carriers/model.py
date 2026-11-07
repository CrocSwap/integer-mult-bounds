"""Exact fixed-root bridge and ordinary carrier model.

Jerry Chen / @CubeJerry, substantial OpenAI GPT-6 Astra Pro assistance.
Apache-2.0. Source root: DreamingOfClouds, CrocSwap/integer-mult-bounds#6833.
No numerical library is needed by the verification path.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[0] * n for _ in range(n)]


def add(a, b, scale=1):
    return [[u + scale*v for u, v in zip(x, y)] for x, y in zip(a, b)]


def outer(x, y):
    return [[u*v for v in y] for u in x]


def dot(x, y):
    return sum(u*v for u, v in zip(x, y))


def transpose(a):
    return list(map(list, zip(*a)))


def mm(a, b):
    bt = transpose(b)
    return [[sum(u*v for u, v in zip(ar, bc) if u and v) for bc in bt] for ar in a]


def basis(rows):
    out, pivots = [], []
    for raw in rows:
        row = list(map(Q, raw))
        for p, earlier in zip(pivots, out):
            factor = row[p]
            if factor:
                row = [u-factor*v for u, v in zip(row, earlier)]
        p = next((i for i, value in enumerate(row) if value), None)
        if p is not None:
            factor = row[p]
            out.append([v/factor for v in row])
            pivots.append(p)
    return out


def rank(rows):
    return len(basis(rows))


def build(a=9, b=9):
    """Independent closed formulas for the odd/odd unit-child family."""
    need(a > 0 and b > 0 and a % 2 == b % 2 == 1, 'positive odd arm lengths')
    m, n = a+b, a+b+2
    A, E = 0, n-1
    fi, hi = list(range(1, a+1)), list(range(a+1, m+1))
    def vector(values):
        ans = [0]*n
        for i, value in values:
            ans[i] += value
        return ans
    left, right = [], []
    for j, f in enumerate(fi):
        x = vector([(A, 1), (f, 1)] + [(k, 2) for k in fi[:j]])
        y = vector([(A, 1), (f, -1)])
        left.append((x, y, {A, *fi[:j+1]}))
    for j, h in enumerate(hi):
        x = vector([(A, -1), (h, 1)] + [(k, 2) for k in hi[j+1:]])
        y = vector([(A, 1), (h, 1)])
        right.append((x, y, {A, *hi[j:]}))
    F, H = vector([(i, 1) for i in fi]), vector([(i, 1) for i in hi])
    ee = vector([(E, 1)])
    v = vector([(A, 1)]+[(i, 1) for i in fi]+[(i, -1) for i in hi])
    z = vector([(A, -1)]+[(i, (-1)**j) for j, i in enumerate(fi)]
               +[(i, -(-1)**j) for j, i in enumerate(hi)])
    u = [f+h for f, h in zip(F, H)]
    w = vector([(A, 2)]+[(i, -(-1)**j) for j, i in enumerate(fi)]
               +[(i, (-1)**j) for j, i in enumerate(hi)])
    q0 = ([f+h+e for f, h, e in zip(F, H, ee)], vector([(A, 1)]), None)
    q1 = (vector([(A, -1)]+[(i, 2) for i in hi]),
          vector([(A, 2), (E, 1)]+[(i, -(-1)**j) for j, i in enumerate(fi)]
                 +[(i, (-1)**j) for j, i in enumerate(hi)]), None)
    q2 = (vector([(A, -1), (E, -1)]+[(i, 2) for i in hi]),
          vector([(A, 3), (E, 1)]+[(i, -2*(-1)**j) for j, i in enumerate(fi)]
                 +[(i, 2*(-1)**j) for j, i in enumerate(hi)]), None)
    thin = [q0, q1, q2]
    B = eye(n)
    for x, y, _ in thin:
        B = mm(add(eye(n), outer(x, y), -2), B)
    return {'a':a, 'b':b, 'n':n, 'm':m, 'left':left, 'right':right,
            'full':left+right, 'thin':thin, 'sites':left+thin+right,
            'E':ee, 'v':v, 'z':z, 'u':u, 'w':w, 'B':B}


def source_outer(a=9, b=9):
    m = a+b
    targets = Counter({1:1, 8*m+1:1})
    paid = Counter({1:3})
    for g in (a, b):
        targets.update(8*j+1 for j in range(1, g+1))
        paid.update(8*j for j in range(1, g))
    return targets, paid


INTERVALS = [(a, b) for a in range(18) for b in range(a, 18)]


class CapacityModel:
    def __init__(self):
        self.root = build()
        self.full = self.root['full']
        self.powers = [eye(20), self.root['B'], mm(self.root['B'], self.root['B'])]
        self.cache = {}

    def capacity(self, a, b, mask, closure=True):
        key = (a, b, tuple(sorted(mask)), closure)
        if key in self.cache:
            return self.cache[key]
        xs = [self.full[j][0] for j in range(a, b+1)]
        ys = [self.full[j][1] for j in range(a, b+1)]
        for p in range(20):
            if p not in mask:
                e = [int(i == p) for i in range(20)]
                xs.append(e); ys.append(e)
        if a < 9 <= b and closure:
            # Columns and rows close under B because B has polynomial degree three.
            xs = [col for power in self.powers for col in transpose(mm(power, transpose(xs)))]
            ys = [row for power in self.powers for row in mm(ys, power)]
        xb, yb = basis(xs), basis(ys)
        pair = [[dot(y, x) for x in xb] for y in yb]
        result = 20-len(xb)-len(yb)+rank(pair)
        need(0 <= result <= len(mask), 'pairing capacity bounds')
        self.cache[key] = result
        return result

    def case(self, a, b):
        need(0 <= a <= 8 and 9 <= b <= 17, 'central dense-mask domain')
        masks = [set(s[2]) for s in self.full]
        for j in range(a, b+1):
            masks[j] = set(range(19))
        caps = [self.capacity(c, d, set.intersection(*masks[c:d+1])) for c, d in INTERVALS]
        demands = [len(m)-2 for m in masks]
        targets = Counter(1+8*sum(f in mask for mask in masks) for f in range(20))
        return caps, demands, targets


@lru_cache(None)
def log_bounds(integer, terms=32):
    need(integer >= 1, 'positive logarithm input')
    if integer == 1:
        return Q(0), Q(0)
    power = integer.bit_length()-1
    a = Q(integer, 2**power)
    def series(value):
        z = (value-1)/(value+1)
        total = 2*sum(z**(2*j+1)/Q(2*j+1) for j in range(terms))
        tail = 2*z**(2*terms+1)/Q(2*terms+1)/(1-z*z)
        return total, total+tail
    lo, hi = series(a)
    l2, h2 = series(Q(2))
    return lo+power*l2, hi+power*h2


def floor_q(value):
    return value.numerator//value.denominator


def ceil_q(value):
    return -floor_q(-value)


@lru_cache(None)
def power_bounds(integer, kappa):
    """Outward rational bounds for integer**(1-kappa); no floating arithmetic."""
    kappa = Q(kappa)
    need(0 <= kappa <= Q(1, 10), 'tariff exponent range')
    lo, hi = log_bounds(integer)
    xl, xh = kappa*lo, kappa*hi
    need(0 <= xl <= xh <= 1, 'alternating exponential range')
    def exponential(x, last):
        term, total = Q(1), Q(1)
        for j in range(1, last+1):
            term *= -x/Q(j)
            total += term
        return total
    low = integer*exponential(xh, 13)
    high = integer*exponential(xl, 14)
    scale = 10**18
    return Q(floor_q(low*scale), scale), Q(ceil_q(high*scale), scale)


def moment(hist, kappa):
    lo = hi = Q(0)
    for r, count in hist.items():
        a, b = power_bounds(int(r), str(kappa))
        lo += count*a; hi += count*b
    return lo, hi


def source_complete(kappa, helpers, paid):
    targets, outer_paid = source_outer()
    target_hist = Counter({int(r):18*n for r, n in helpers.items()})
    paid_hist = Counter({int(r):18*n for r, n in paid.items()})
    target_hist.update({r:104*n for r, n in targets.items()})
    paid_hist.update({r:104*n for r, n in outer_paid.items()})
    need(sum(r*n for r, n in target_hist.items())-sum(r*n for r, n in paid_hist.items()) == 760,
         'complete signed rank surplus is 760')
    t, p = moment(target_hist, kappa), moment(paid_hist, kappa)
    return t[0]-p[1], t[1]-p[0]
