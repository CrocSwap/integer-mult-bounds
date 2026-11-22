# SPDX-License-Identifier: Apache-2.0
"""Exact integer idle-histogram ceiling for a complex local word under the coverage law.

`research/complex-local-word-ceiling` bounds packing with a *fractional* relaxation: it puts
the whole idle mass M of a call into M/R (possibly fractional) rank-R children, which
minimises the per-call moment over all non-negative **real** counts. That is the right
optimistic bound, so its ceiling is a valid but not tight statement: a real packing uses a
non-negative **integer** multiset of children, because each child of rank r is an object.

This module replaces the relaxation by the attained optimum over integer histograms, so its
ceiling is a certified statement about every realizable idle packing rather than about a
fractional ideal:

    min { sum_r n_r (r/m)^(1-a) : n_r in Z_{>=0}, sum_r r n_r = M, 1 <= r <= R }   (per call)

The minimum is computed by dynamic programming over the mass axis, which enumerates the whole
feasible set exactly -- no sampling and no exchange argument. Two certified interval facts
follow, both using the outward-rounded enclosures of `ceiling.py`:

  * DP_lower(a) = min_h sum n_r lo_r(a) is a certified **lower** bound on the true optimum,
    so DP_lower(a)/w > 1 rejects a: no integer histogram of any shape attains moment <= 1.
  * moment_upper(H(a)) = sum n_r hi_r(a) over the DP argmin is a certified **upper** bound
    on that histogram's true moment, so it < 1 accepts a: the histogram is a witness.

Model inputs are unchanged from `ceiling.py` and are re-checked there and in `verify.py`:
one fixed paid local profile per call, parent width m, `families/stages` live families per
call, a per-call centre charge, `unpaid` unpaid coordinates per live family and the outer
halving guard R = max_idle_rank(m). Only the integrality of the idle remainder is added.
Standard library only; exact rational arithmetic with outward rounding to 2^-PREC.
Nick Petalas, with AI assistance. Apache-2.0.
"""
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

__all__ = ['scaled', 'best_idle', 'idle_bounds', 'moment', 'ceiling_int', 'model']


def scaled(x):
    """Exact integer numerator of the dyadic rational x at 2^-PREC."""
    v = Q(x) * (1 << C.PREC)
    C.require(v.denominator == 1, 'value is not a multiple of 2^-PREC')
    return v.numerator


def model(local, m, families, stages, centre, R=None, unpaid=1):
    """Per-call model quantities, re-using the parent's coverage law and halving guard."""
    return C.model(local, m, families, stages, centre, R, unpaid)


def best_idle(mass, R, m, a):
    """Exact minimum over integer idle histograms of total mass `mass`, ranks 1..R.

    Returns (certified_lower_scaled, histogram) where the scaled value is in units of 2^-PREC.
    Dynamic program over the mass axis; the argmin is recovered and is a genuine feasible
    integer histogram. Unbounded use of rank r is expressed by the standard recurrence
        f[j] = min over 1 <= r <= min(R, j) of f[j-r] + cost[r],
    which is the min-cost unbounded change-making value for exact mass j.
    """
    C.require(isinstance(mass, int) and mass >= 0, 'idle mass must be a non-negative integer')
    C.require(1 <= R < m, 'idle rank cap out of range')
    if mass == 0:
        return 0, {}
    cost = [0] + [scaled(C.child_cost(r, m, a)[0]) for r in range(1, R + 1)]
    best = [None] * (mass + 1)
    back = [0] * (mass + 1)
    best[0] = 0
    for j in range(1, mass + 1):
        value, pick = None, 0
        for r in range(1, min(R, j) + 1):
            prev = best[j - r]
            if prev is None:
                continue
            v = prev + cost[r]
            if value is None or v < value:
                value, pick = v, r
        best[j], back[j] = value, pick
    C.require(best[mass] is not None, 'no integer idle histogram exists for this mass and cap')
    hist = {}
    j = mass
    while j:
        r = back[j]
        C.require(1 <= r <= R, 'dynamic program produced an out-of-range rank')
        hist[r] = hist.get(r, 0) + 1
        j -= r
    C.require(sum(r * n for r, n in hist.items()) == mass, 'recovered histogram does not conserve mass')
    return best[mass], hist


def idle_bounds(hist, m, a):
    """Certified (lower, upper) enclosure of sum_r n_r (r/m)^(1-a) for an integer histogram."""
    lo = hi = 0
    for r, n in hist.items():
        c = C.child_cost(r, m, a)
        lo += n * scaled(c[0])
        hi += n * scaled(c[1])
    return lo, hi


def moment(local, m, families, stages, centre, a, R=None, unpaid=1):
    """Per-call moment of the best integer idle packing.

    Returns (lower, upper, idle_histogram, info) where lower/upper are certified enclosures of
    the minimum per-call moment over all feasible integer idle histograms: `lower` bounds every
    feasible moment from below and `upper` bounds the DP argmin's moment from above.
    """
    q = C.model(local, m, families, stages, centre, R, unpaid)
    mass = q['idle_mass']
    C.require(mass.denominator == 1, 'idle mass is not an integer; see README on the two-unpaid lever')
    dp_lo, hist = best_idle(int(mass), q['R'], m, a)
    idle_lo, idle_hi = idle_bounds(hist, m, a)
    local_lo = local_hi = 0
    for r, n in local.items():
        c = C.child_cost(r, m, a)
        local_lo += n * scaled(c[0])
        local_hi += n * scaled(c[1])
    scale = Q(1 << C.PREC)
    w = q['w']
    return (Q(dp_lo + local_lo) / scale / w, Q(idle_hi + local_hi) / scale / w, hist, q)


def ceiling_int(local, m, families, stages, centre, grid=Q(1, 10 ** 15), R=None, unpaid=1):
    """Certified bracket [a_lo, a_hi] for the attained integer idle ceiling.

    a_lo: the DP argmin's certified upper moment is < 1, so some integer packing is a witness.
    a_hi: the certified lower moment of every integer packing is > 1, so none is.
    """
    lo, hi = Q(0), Q(1, 20)
    _, bottom_hi, _, _ = moment(local, m, families, stages, centre, lo, R, unpaid)
    top_lo, _, _, _ = moment(local, m, families, stages, centre, hi, R, unpaid)
    C.require(top_lo > 1, 'search window too small')
    C.require(bottom_hi < 1, 'no integer packing reaches moment below one')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        if mid <= lo:
            mid = lo + grid
        v_lo, v_hi, _, _ = moment(local, m, families, stages, centre, mid, R, unpaid)
        if v_hi < 1:
            lo = mid
        elif v_lo > 1:
            hi = mid
        else:
            raise ValueError('enclosure too wide to separate the grid point')
    return lo, hi