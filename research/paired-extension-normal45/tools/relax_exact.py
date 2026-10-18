#!/usr/bin/env python3
"""relax_exact.py -- Fractions-only verification of a stored optimal basis of the changed-inventory
fixed-capacity fractional relaxation (relax.py), without scipy.

relax.py locates the optimal basis with a float LP (scipy/HiGHS) and then certifies it exactly. This module
performs only the exact part, from a stored list of basis patterns:
  1. x_B = B^-1 rhs (exact rationals), x_B >= 0: the basic solution is feasible, so the cap is at least the
     root of its complete profile (root.py bracket at 10^-digits);
  2. the dual y(b) = B^-T c_B(b) is an exact rational combination of the H_k(b); every one of the capacity-
     feasible patterns has reduced cost > 0 (or identically 0) at b = hi, so by weak duality every feasible x
     has moment >= 1 at hi: the cap is at most hi.
The bins, pattern catalogue, moment model and interval arithmetic are relax.py's / root.py's (imported).

Marius-Paul Dumitrean, prepared with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
"""
from fractions import Fraction as Q
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root as R
import relax as X


def need(c, m):
    if not c:
        raise ValueError(m)


def pattern_of(entry, widths, bins):
    cap = int(entry['capacity'])
    need(cap in bins, 'basis pattern capacity %r is not a bin capacity' % cap)
    counts = tuple(list(entry['widths']).count(w) for w in widths)
    need(sum(counts) == len(entry['widths']), 'basis pattern uses a width outside the inventory: %r' % (entry,))
    used = sum(w * n for w, n in zip(widths, counts))
    need(used <= cap, 'basis pattern exceeds its capacity')
    return (cap, counts, cap - used)


def verify_basis(local, inventory, basis_patterns, bins=X.BINS, digits=25):
    local = {int(r): Q(n) for r, n in local.items() if Q(n) != 0}
    inventory = {int(w): Q(n) for w, n in inventory.items() if Q(n) != 0}
    need(all(n > 0 for n in local.values()) and all(n > 0 for n in inventory.values()), 'positive local/inventory')
    widths = sorted(inventory)
    caps = sorted(bins)
    pats = X.patterns(bins, widths)
    patset = set(pats)
    rhs = [Q(bins[c]) for c in caps] + [X.CALLS * inventory[w] for w in widths]
    local_rep = {r: X.CALLS * n for r, n in local.items()}
    total_cap = sum(c * bins[c] for c in caps)
    inv_mass = sum(w * inventory[w] for w in widths) * X.CALLS
    local_mass = sum(r * n for r, n in local_rep.items())
    idle_mass = total_cap - inv_mass
    need(idle_mass >= 0, 'inventory exceeds bin capacity')
    mass_ok = (local_mass + idle_mass == R.MASS_PER_REPLICA)
    basis = [pattern_of(e, widths, bins) for e in basis_patterns]
    need(len(basis) == len(rhs), 'basis must have exactly %d patterns' % len(rhs))
    need(all(p in patset for p in basis), 'basis pattern outside the catalogue')
    need(len(set(basis)) == len(basis), 'repeated basis pattern')
    cols = [X.column(p, caps, widths) for p in basis]
    need(X.rat_rank(cols) == len(rhs), 'basis columns are linearly dependent')
    Bm = [[cols[k][i] for k in range(len(basis))] for i in range(len(rhs))]
    Binv = X.rat_inverse(Bm)
    xB = [sum(Binv[k][i] * rhs[i] for i in range(len(rhs))) for k in range(len(basis))]
    need(all(v >= 0 for v in xB), 'basis not primal feasible (negative basic variable)')
    for e, v in zip(basis_patterns, xB):
        if 'count_per_replica' in e:
            need(Q(e['count_per_replica']) == v, 'stored basic count differs from B^-1 rhs: %r' % (e,))
    idle = {}
    for p, n in zip(basis, xB):
        if p[2] and n:
            idle[p[2]] = idle.get(p[2], 0) + n
    full = dict(local_rep)
    for r, n in idle.items():
        full[r] = full.get(r, 0) + n
    cap_lo, cap_hi = R.root_bracket(full, X.LIVE, digits, check_mass_T=1 if mass_ok else None)
    ranks = sorted({r for cap, counts, r in pats if r})
    Y = {j: {} for j in range(len(rhs))}
    for j in range(len(rhs)):
        for k, p in enumerate(basis):
            r = p[2]
            if r == 0 or Binv[k][j] == 0:
                continue
            Y[j][r] = Y[j].get(r, 0) + Binv[k][j]
    Hhi = {r: R.H(r, cap_hi) for r in ranks}
    tight = strict = 0
    min_slack = None
    for p in pats:
        a = X.column(p, caps, widths)
        coeff = {}
        if p[2]:
            coeff[p[2]] = Q(1)
        for j in range(len(rhs)):
            if a[j] == 0:
                continue
            for k, v in Y[j].items():
                coeff[k] = coeff.get(k, 0) - a[j] * v
        coeff = {k: v for k, v in coeff.items() if v != 0}
        if not coeff:
            tight += 1
            continue
        lower = sum(v * (Hhi[k][0] if v > 0 else Hhi[k][1]) for k, v in coeff.items())
        need(lower > 0, 'dual sign failure for pattern %s (reduced-cost lower bound %s)' % (str(p), str(lower)))
        strict += 1
        min_slack = lower if min_slack is None else min(min_slack, lower)
    return dict(status='PASS_EXACT_RELAXATION_CAP' if mass_ok else 'PASS_EXACT_RELAXATION_CAP_MASS_NOT_65088',
                cap_lower=str(cap_lo), cap_upper=str(cap_hi), patterns=len(pats), tight_patterns=tight,
                strict_patterns=strict, minimum_slack_lower=str(min_slack), rank_mass_identity=mass_ok,
                idle_per_replica={str(r): str(n) for r, n in sorted(idle.items())},
                basic_counts=[str(v) for v in xB])
