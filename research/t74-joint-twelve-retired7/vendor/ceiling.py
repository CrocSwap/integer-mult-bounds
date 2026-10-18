# SPDX-License-Identifier: Apache-2.0
"""Packing-independent ceiling for a complex local word under the hosted nine-stage coverage law.

Model (all inputs explicit):
  * per replica the template has `families` live data families and `stages` invocations, so
    w = families / stages live families per call; on the selected T37/T16 line all helpers are
    hosted on data families, so w = 2 * pairs * V / stages is fixed by the port count V;
  * coverage identity (PR1012, re-checked here on the selected profile): paid rank mass equals
    (m - 1) * W + centre * N, i.e. every live family keeps exactly one unpaid coordinate and every
    call pays its centre path (`unpaid` > 1 is a what-if for a changed coverage law only);
  * the local word fixes its own paid child profile `local` (per call);
  * every remaining unit of mass is an idle/remainder child of rank at most R, where the outer
    recipe's halving guard m^2 > 2 R^2 bounds R (R = 51 for m = 73).

Lemma. For a >= 0, a child of rank r costs (r/m)^(1-a) = r * c(r), with c(r) = r^(-a) m^(a-1)
non-increasing in r. Hence, with idle mass M fixed and idle ranks <= R, every idle histogram has
moment >= the relaxation that puts all of M into (possibly fractional) rank-R children:

    relax(a) = [ sum_local n_r (r/m)^(1-a) + (M/R) (R/m)^(1-a) ] / w     (per call).

The moment is increasing in a. So relax(a*) > 1 certifies that no hosting, owner packing or
idle-remainder change of the given local word, template and outer recipe certifies a saving
>= a*. Under the retained reduction kappa < a/(1+a) when the complex side binds, so
a*/(1+a*) also bounds kappa. This is a bound for the stated model, not for other local words,
templates, coverage laws or outer recipes.

Exact rational intervals: ln k from atanh chains, exp by Taylor with Lagrange remainder,
outward rounding to 2^-PREC. Standard library only. Douglas Colkitt, with Claude (Anthropic)
assistance.
"""
from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt

PREC = 256


def require(ok, why):
    if not ok:
        raise ValueError(why)


def down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x):
    return -down(-x)


@lru_cache(None)
def atanh(t):
    """Enclosure of atanh(t) for rational 0 < t <= 1/3."""
    require(0 < t <= Q(1, 3), 'atanh range')
    s, p, k = Q(0), t, 0
    while True:
        term = p / (2 * k + 1)
        s += term
        p *= t * t
        k += 1
        tail = p / ((2 * k + 1) * (1 - t * t))
        if tail < Q(1, 1 << (PREC + 8)):
            return down(s), up(s + tail)


@lru_cache(None)
def ln(k):
    """Enclosure of ln k for an integer k >= 1: ln k = ln(k-1) + 2 atanh(1/(2k-1))."""
    require(isinstance(k, int) and k >= 1, 'ln domain')
    if k == 1:
        return Q(0), Q(0)
    lo, hi = ln(k - 1)
    a, b = atanh(Q(1, 2 * k - 1))
    return down(lo + 2 * a), up(hi + 2 * b)


def exp(lo, hi):
    """Enclosure of exp([lo, hi]) for 0 <= lo <= hi <= 1/2."""
    require(0 <= lo <= hi <= Q(1, 2), 'exp range')
    def series(y, upper):
        s, t, k = Q(1), Q(1), 0
        while True:
            k += 1
            t = t * y / k
            s += t
            if t * y < Q(1, 1 << (PREC + 8)):
                return up(s + 2 * t * y / (k + 1)) if upper else down(s)
    return series(lo, False), series(hi, True)


def child_cost(r, m, a):
    """Enclosure of (r/m)^(1-a) = (r/m) exp(a ln(m/r))."""
    lm, um = ln(m)
    lr, ur = ln(r)
    e = exp(max(Q(0), a * (lm - ur)), a * (um - lr))
    return down(Q(r, m) * e[0]), up(Q(r, m) * e[1])


def max_idle_rank(m):
    """Largest R with m^2 > 2 R^2 (outer halving guard)."""
    R = isqrt((m * m - 1) // 2)
    while 2 * (R + 1) ** 2 < m * m:
        R += 1
    while 2 * R * R >= m * m:
        R -= 1
    return R


def model(local, m, families, stages, centre, R=None, unpaid=1):
    """Per-call quantities. local: {rank: count per call (Fraction ok)}."""
    R = max_idle_rank(m) if R is None else R
    require(2 * R * R < m * m, 'idle rank cap violates the halving guard')
    require(all(0 < r < m for r in local) and all(n >= 0 for n in local.values()), 'local profile')
    w = Q(families, stages)
    require(1 <= unpaid < m, 'unpaid coordinates per family')
    total = (m - unpaid) * w + centre
    local_mass = sum(r * Q(n) for r, n in local.items())
    idle = total - local_mass
    require(idle >= 0, 'local word pays more mass than the coverage law allows')
    return dict(R=R, w=w, total_mass=total, local_mass=local_mass, idle_mass=idle, deficit=unpaid * w - centre)


def relax(local, m, families, stages, centre, a, R=None, unpaid=1):
    """Enclosure of the per-call relaxation moment at saving a."""
    q = model(local, m, families, stages, centre, R, unpaid)
    lo = hi = Q(0)
    for r, n in local.items():
        c = child_cost(r, m, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    c = child_cost(q['R'], m, a)
    k = q['idle_mass'] / q['R']
    lo, hi = lo + k * c[0], hi + k * c[1]
    return down(lo / q['w']), up(hi / q['w'])


def ceiling(local, m, families, stages, centre, grid=Q(1, 10 ** 15), R=None, unpaid=1):
    """Grid bracket [a_lo, a_hi]: relax(a_lo) < 1 < relax(a_hi), certified. a_hi is the ceiling."""
    lo, hi = Q(0), Q(1, 20)
    require(relax(local, m, families, stages, centre, hi, R, unpaid)[0] > 1, 'search window too small')
    require(relax(local, m, families, stages, centre, lo, R, unpaid)[1] < 1, 'relaxation has no positive saving')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v = relax(local, m, families, stages, centre, mid, R, unpaid)
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    return lo, hi
