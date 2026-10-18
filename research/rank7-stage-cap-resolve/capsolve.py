#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent re-solve of the fixed-capacity packing relaxation caps of PR #2979.

Nothing from the audited package is imported.  The model is re-implemented from
its written description (research/rank7-joint-endframes/tools/relax.py docstring):

  per replica: bins {8: 672, 16: 448, 32: 448, 48: 448}; 9 calls; live width 896;
  a pattern is a multiset of helper widths of total <= capacity, paying one idle
  child of rank capacity - used (rank 0 pays nothing);
  LP(b) = min sum_p x_p H(r_p, b) subject to: per capacity, sum x_p = bins[c];
          per width w, sum n_w(p) x_p = 9 * inventory[w]; x >= 0;
  H(r, b) = r * (73 / r) ** b;  M(b) = (9 * sum_r local_r H(r, b) + LP(b)) / (73 * 896);
  cap = the root of M(b) = 1 (M is increasing because every H(r, .) is).

Method, all different from the source's:
  * patterns by recursive multiset enumeration (not a product of count ranges);
  * the optimal basis is located by this file's own dense two-phase simplex
    (numpy float64, Bland's rule) inside a bisection on b; no scipy, no stored basis;
  * certification: the basis is inverted exactly with Fractions by this file's own
    Gauss-Jordan elimination; the root of the basic profile and all reduced costs
    are enclosed with mpmath interval arithmetic (mpmath.iv), not with the source's
    atanh/Taylor series.
The cap bracket is (lo, hi) on the 10^-25 grid: the basic solution is feasible, so
M(lo) <= M_xB(lo) < 1 gives cap > lo; all reduced costs >= 0 at hi make xB optimal
there, so M(hi) = M_xB(hi) > 1 gives cap < hi.
"""
from fractions import Fraction as Q
import mpmath
import numpy as np

BINS = {8: 672, 16: 448, 32: 448, 48: 448}
CALLS = 9
LIVE = 896
BASE = 73
GRID = 10 ** 25
iv = mpmath.iv
iv.dps = 70


def need(cond, msg):
    if not cond:
        raise ValueError(msg)


def multisets(widths, room):
    """All multisets (as count tuples aligned with widths) of total width <= room."""
    if not widths:
        yield ()
        return
    w, rest = widths[0], widths[1:]
    for n in range(room // w + 1):
        for tail in multisets(rest, room - n * w):
            yield (n,) + tail


def catalogue(widths):
    pats = []
    for cap in sorted(BINS):
        for counts in multisets(widths, cap):
            used = sum(w * n for w, n in zip(widths, counts))
            pats.append((cap, counts, cap - used))
    return pats


def column(p, caps, widths):
    cap, counts, _ = p
    return [1 if c == cap else 0 for c in caps] + list(counts)


def rhs_of(inventory, caps, widths):
    return [BINS[c] for c in caps] + [CALLS * Q(inventory[w]) for w in widths]


def hfloat(r, b):
    return 0.0 if r == 0 else r * (BASE / r) ** b


def simplex(A, rhs, cost, eps=1e-9, max_iter=20000):
    """Two-phase dense simplex for min c.x, A x = rhs >= 0, x >= 0.  Returns basis indices."""
    m, n = A.shape
    T = np.zeros((m + 1, n + m + 1))
    T[:m, :n] = A
    T[:m, n:n + m] = np.eye(m)
    T[:m, -1] = rhs
    basis = list(range(n, n + m))

    def run(obj, allowed):
        T[m, :] = 0.0
        T[m, :len(obj)] = obj
        for i, j in enumerate(basis):
            if T[m, j] != 0.0:
                T[m, :] -= T[m, j] * T[i, :]
        for _ in range(max_iter):
            red = T[m, :allowed]
            cand = np.nonzero(red < -eps)[0]
            if cand.size == 0:
                return
            j = int(cand[0])  # Bland: smallest entering index
            col = T[:m, j]
            pos = col > eps
            need(pos.any(), 'unbounded LP')
            ratios = np.full(m, np.inf)
            ratios[pos] = T[:m, -1][pos] / col[pos]
            best = ratios.min()
            ties = [i for i in range(m) if ratios[i] <= best + 1e-12 * max(1.0, best)]
            i = min(ties, key=lambda k: basis[k])  # Bland: smallest leaving index
            T[i, :] /= T[i, j]
            for k in range(m + 1):
                if k != i and T[k, j] != 0.0:
                    T[k, :] -= T[k, j] * T[i, :]
            basis[i] = j
        raise ValueError('simplex iteration limit')

    run(np.concatenate([np.zeros(n), np.ones(m)]), n + m)
    need(-T[m, -1] < 1e-7 * max(1.0, float(np.abs(rhs).sum())), 'LP infeasible')
    for i, j in enumerate(basis):  # drive out remaining (degenerate) artificials
        if j >= n:
            nz = [k for k in range(n) if abs(T[i, k]) > 1e-9 and k not in basis]
            if nz:
                k = nz[0]
                T[i, :] /= T[i, k]
                for r in range(m + 1):
                    if r != i:
                        T[r, :] -= T[r, k] * T[i, :]
                basis[i] = k
    need(all(j < n for j in basis), 'redundant constraint row (artificial left in basis)')
    run(np.asarray(cost, dtype=float), n)
    return sorted(basis)


def float_lp(pats, A, rhs, b):
    cost = [hfloat(r, b) for _, _, r in pats]
    basis = simplex(A, rhs, cost)
    xB = np.linalg.solve(A[:, basis], rhs)
    return sum(cost[j] * x for j, x in zip(basis, xB)), basis


def moment_float(local, val, b):
    return (CALLS * sum(n * hfloat(r, b) for r, n in local.items()) + val) / (BASE * LIVE)


def exact_inverse(M):
    n = len(M)
    aug = [[Q(v) for v in row] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        piv = next((r for r in range(c, n) if aug[r][c] != 0), None)
        need(piv is not None, 'singular basis')
        aug[c], aug[piv] = aug[piv], aug[c]
        p = aug[c][c]
        aug[c] = [v / p for v in aug[c]]
        for r in range(n):
            if r != c and aug[r][c] != 0:
                f = aug[r][c]
                aug[r] = [a - f * bv for a, bv in zip(aug[r], aug[c])]
    return [row[n:] for row in aug]


def h_iv(r, b):
    if r == 0:
        return iv.mpf(0)
    return iv.mpf(r) * iv.exp(frac_iv(Q(b)) * iv.log(iv.mpf(BASE) / r))


def frac_iv(q):
    return iv.mpf(q.numerator) / q.denominator


def moment_iv(profile, b):
    s = iv.mpf(0)
    for r, n in profile.items():
        if n:
            s += frac_iv(Q(n)) * h_iv(r, b)
    return s / (BASE * LIVE)


def grid_root(profile, start):
    """Consecutive grid points (lo, hi) with M(lo) < 1 < M(hi), certified by intervals."""
    def side(k):
        v = moment_iv(profile, Q(k, GRID))
        if v.b < 1:
            return -1
        if v.a > 1:
            return 1
        raise ValueError('interval precision exhausted')
    lo, hi = 0, GRID // 100  # the root lies in (0, 1/100]; the float estimate is not trusted
    need(side(lo) < 0 < side(hi), 'root outside (0, 1/100]')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if side(mid) < 0:
            lo = mid
        else:
            hi = mid
    return Q(lo, GRID), Q(hi, GRID)


def solve_cap(local, inventory):
    local = {int(r): int(n) for r, n in local.items() if int(n)}
    inventory = {int(w): int(n) for w, n in inventory.items() if int(n)}
    widths = sorted(inventory)
    caps = sorted(BINS)
    pats = catalogue(widths)
    rhs = rhs_of(inventory, caps, widths)
    A = np.array([column(p, caps, widths) for p in pats], dtype=float).T
    rhs_f = np.array([float(v) for v in rhs])
    lo, hi = 0.0015, 0.0020
    need(moment_float(local, float_lp(pats, A, rhs_f, lo)[0], lo) < 1, 'lower start')
    need(moment_float(local, float_lp(pats, A, rhs_f, hi)[0], hi) > 1, 'upper start')
    for _ in range(55):
        mid = (lo + hi) / 2
        if moment_float(local, float_lp(pats, A, rhs_f, mid)[0], mid) < 1:
            lo = mid
        else:
            hi = mid
    bstar = (lo + hi) / 2
    basis = float_lp(pats, A, rhs_f, bstar)[1]
    return certify(local, inventory, pats, caps, widths, rhs, basis, bstar)


def certify(local, inventory, pats, caps, widths, rhs, basis, bstar):
    m = len(rhs)
    need(len(basis) == m and len(set(basis)) == m, 'basis size')
    cols = [column(pats[j], caps, widths) for j in basis]
    B = [[cols[k][i] for k in range(m)] for i in range(m)]
    Binv = exact_inverse(B)
    xB = [sum(Binv[k][i] * rhs[i] for i in range(m)) for k in range(m)]
    need(all(v >= 0 for v in xB), 'basic solution infeasible')
    profile = {r: Q(CALLS * n) for r, n in local.items()}
    idle = {}
    for j, x in zip(basis, xB):
        r = pats[j][2]
        if r and x:
            idle[r] = idle.get(r, 0) + x
            profile[r] = profile.get(r, 0) + x
    total = sum(r * n for r, n in profile.items())
    need(total == 65088, 'rank-mass identity 72*896 + 64*9 per replica')
    lo, hi = grid_root(profile, bstar)
    # dual y^T = c_B^T B^-1, kept symbolic: y_i = sum_k Binv[k][i] * H(r_k)
    Y = [{} for _ in range(m)]
    for k, j in enumerate(basis):
        r = pats[j][2]
        if r:
            for i in range(m):
                if Binv[k][i]:
                    Y[i][r] = Y[i].get(r, 0) + Binv[k][i]
    Hhi = {}
    tight = strict = 0
    min_red = None
    for p in pats:
        a = column(p, caps, widths)
        coeff = {p[2]: Q(1)} if p[2] else {}
        for i, ai in enumerate(a):
            if ai:
                for r, v in Y[i].items():
                    coeff[r] = coeff.get(r, 0) - ai * v
        coeff = {r: v for r, v in coeff.items() if v}
        if not coeff:
            tight += 1
            continue
        red = iv.mpf(0)
        for r, v in coeff.items():
            if r not in Hhi:
                Hhi[r] = h_iv(r, hi)
            red += frac_iv(v) * Hhi[r]
        need(red.a > 0, 'reduced cost not positive at hi for pattern %r' % (p,))
        strict += 1
        min_red = red.a if min_red is None else min(min_red, red.a)
    basis_out = []
    for j, x in zip(basis, xB):
        cap, counts, r = pats[j]
        ws = [w for w, n in zip(widths, counts) for _ in range(n)]
        basis_out.append({'capacity': cap, 'widths': sorted(ws, reverse=True), 'count_per_replica': str(x)})
    return {
        'cap_lower': str(lo), 'cap_upper': str(hi), 'patterns': len(pats), 'tight_patterns': tight,
        'strict_patterns': strict, 'min_reduced_cost_lower': mpmath.nstr(mpmath.mpf(min_red), 12),
        'idle_per_replica': {str(r): str(n) for r, n in sorted(idle.items())},
        'rank_mass_per_replica': str(total), 'basis': sorted(basis_out, key=lambda e: (e['capacity'], e['widths'])),
        'float_root': repr(bstar),
    }
