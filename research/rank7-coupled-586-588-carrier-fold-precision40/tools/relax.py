#!/usr/bin/env python3
"""relax.py -- changed-inventory, fixed-capacity fractional relaxation (upper bound on the complex endpoint)
for an ARBITRARY per-call local profile and per-call helper-width inventory, with exact rational verification.

Model (everything per replica; the fractional cap is independent of T):
  * bins: every replica has 112 ports x 18 idle children; the child capacities (ranks) come from the
    T37 template: 6 children of capacity 8, 4 of 16, 4 of 32, 4 of 48  -> bins {8:672, 16:448, 32:448, 48:448}.
  * roles: every call hosts all its helpers; a helper of width w occupies w consecutive units of ONE bin;
    the 9 calls of a replica supply 9*inventory[w] roles of width w per replica (the inventory is per call;
    with two providers of different widths pass the call-weighted average, a Fraction is fine).
  * pattern catalogue: every multiset of widths with sum <= capacity ("bounded count-vector enumeration");
    the bin then pays ONE idle child of rank cap - used (rank 0 = nothing).
  * CHRONOLOGY IS IGNORED: no source windows, no per-call family collisions, no "one role per bin per call",
    no integrality.  A bin pattern count may be fractional.  Hence this is an UPPER bound on what any
    actual fill of the same inventory can reach, and the bound is NOT a chronological witness.
  * local profile is fixed and fully paid: 9 * local[r] children of rank r per replica.
  Moment: M_x(b) = (9*sum_r local_r H_r(b) + sum_p x_p H_{r_p}(b)) / (73*896),  H_r(b) = r*(73/r)^b,
  LP(b): min_x sum_p x_p H_{r_p}(b)  s.t.  sum_{p in cap c} x_p = bins[c],  sum_p n_w(p) x_p = 9*inv[w], x>=0.
  cap = the root b of min_x M_x(b) = 1 (g(b) = min_x M_x(b) is increasing).

Exact verification (same technique as PR2857's audit_relaxation.py, re-implemented):
  1. float bisection with scipy/HiGHS locates b*; the optimal basis B (9 columns) is read off;
  2. x_B = B^-1 rhs exactly (Fractions) -> the primal profile; root bracketed at 10^-25 with the package's
     rational interval arithmetic (root.py): M(lo) < 1 < M(hi) -> cap >= lo (x_B is feasible);
  3. dual y(b) = B^-T c_B(b) is an exact rational combination of the H_k(b): the Y matrix of the receipt;
     every pattern's reduced cost at b = hi is bracketed with the H enclosures and must be > 0 (or identically 0
     for the tight patterns)  -> by weak duality every feasible x has M_x(hi) >= M_{x_B}(hi) > 1  -> cap <= hi.
  Reproduces PR2857: cap in [0.001720100805416885927944, 0.001720100805416885927945], 1163 patterns, 11 tight.

Usage:
  python -B relax.py --calibrate
  python -B relax.py --inventory '{"4":26,"5":2,"7":62,"8":85,"9":233}' --local '{"1":2397,"2":640,"3":266,"4":128,"5":26,"8":8}'
  python -B relax.py --delta-inventory '{"8":1,"9":-1}' --delta-local '{"1":3,"2":-2}'     # relative to PR2857
  python -B relax.py --scenarios                      # the hypothetical table of ROUND.md (one/two 9->8, 8->7, removal)
API: relax(local, inventory, bins=BINS) -> dict (cap_lower, cap_upper, active patterns, idle histogram, dual check, ...)
"""
from fractions import Fraction as Q
from itertools import product
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root as R

BINS = {8: 672, 16: 448, 32: 448, 48: 448}          # bins per replica (112 ports x children per capacity)
LIVE = R.LIVE_PER_REPLICA                            # 896
CALLS = R.CALLS_PER_REPLICA                          # 9
PR2857_LOCAL = {1: 2394, 2: 642, 3: 266, 4: 128, 5: 26, 8: 8}
PR2857_INV = {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}
PR2857_REALIZED_LOWER = Q('17200966286848326009728/10000000000000000000000000')
PR2857_REALIZED_UPPER = Q('17200966286848326009729/10000000000000000000000000')
PR2857_CAP_UPPER = Q('344020161083377185589/200000000000000000000000')      # 0.001720100805416885927945
PR2848_KAPPA = Q('17186585083049300/10000000000000000000')                   # 0.0017186585083049300 (incumbent of PR2857's gain)


def need(c, m):
    if not c:
        raise ValueError(m)


def patterns(bins, widths):
    out = []
    for cap in sorted(bins):
        for counts in product(*(range(cap // w + 1) for w in widths)):
            used = sum(w * n for w, n in zip(widths, counts))
            if used <= cap:
                out.append((cap, counts, cap - used))
    return out


def Hfloat(r, b):
    import math
    return 0.0 if r == 0 else r * (73.0 / r) ** b


def lp_min(pats, caps, widths, rhs, b):
    """float LP at saving b: returns (optimal value, x, duals y)."""
    import numpy as np
    from scipy.optimize import linprog
    c = np.array([Hfloat(r, b) for cap, counts, r in pats])
    A = np.zeros((len(caps) + len(widths), len(pats)))
    for j, (cap, counts, r) in enumerate(pats):
        A[caps.index(cap), j] = 1.0
        for i, n in enumerate(counts):
            if n:
                A[len(caps) + i, j] = n
    res = linprog(c, A_eq=A, b_eq=np.array([float(v) for v in rhs]), bounds=(0, None), method='highs')
    need(res.status == 0, 'LP infeasible or failed: ' + res.message)
    return res.fun, res.x, res.eqlin.marginals, A


def rat_inverse(Bm):
    n = len(Bm)
    M = [row[:] + [Q(int(i == j)) for j in range(n)] for i, row in enumerate(Bm)]
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        need(piv is not None, 'singular basis')
        M[col], M[piv] = M[piv], M[col]
        f = M[col][col]
        M[col] = [v / f for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                g = M[r][col]
                M[r] = [a - g * bb for a, bb in zip(M[r], M[col])]
    return [row[n:] for row in M]


def rat_rank(cols):
    """rank of a list of rational column vectors"""
    rows = [list(c) for c in cols]
    rank = 0
    ncol = len(rows[0]) if rows else 0
    for col in range(ncol):
        piv = next((r for r in range(rank, len(rows)) if rows[r][col] != 0), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(len(rows)):
            if r != rank and rows[r][col] != 0:
                g = rows[r][col] / rows[rank][col]
                rows[r] = [a - g * bb for a, bb in zip(rows[r], rows[rank])]
        rank += 1
    return rank


def column(pat, caps, widths):
    cap, counts, r = pat
    return [Q(int(cap == c)) for c in caps] + [Q(n) for n in counts]


def relax(local, inventory, bins=BINS, digits=25, verbose=False):
    local = {int(r): Q(n) for r, n in local.items() if Q(n) != 0}
    inventory = {int(w): Q(n) for w, n in inventory.items() if Q(n) != 0}
    need(all(n > 0 for n in local.values()) and all(n > 0 for n in inventory.values()), 'positive local/inventory')
    widths = sorted(inventory)
    caps = sorted(bins)
    pats = patterns(bins, widths)
    rhs = [Q(bins[c]) for c in caps] + [CALLS * inventory[w] for w in widths]
    local_rep = {r: CALLS * n for r, n in local.items()}
    total_cap = sum(c * bins[c] for c in caps)
    inv_mass = sum(w * inventory[w] for w in widths) * CALLS
    local_mass = sum(r * n for r, n in local_rep.items())
    idle_mass = total_cap - inv_mass
    need(idle_mass >= 0, 'inventory exceeds bin capacity')
    mass_ok = (local_mass + idle_mass == R.MASS_PER_REPLICA)

    # --- 1. float bisection on b
    import numpy as np
    def gfloat(b):
        val, x, y, A = lp_min(pats, caps, widths, rhs, b)
        loc = sum(float(n) * Hfloat(r, b) for r, n in local_rep.items())
        return (loc + val) / (73 * LIVE) - 1.0, x, y
    lo, hi = 0.0, 0.01
    g_lo, _, _ = gfloat(lo)
    g_hi, _, _ = gfloat(hi)
    need(g_lo < 0 < g_hi, 'root window [0, 0.01] does not bracket the cap')
    for _ in range(64):
        mid = (lo + hi) / 2
        g, x, y = gfloat(mid)
        if g < 0:
            lo = mid
        else:
            hi = mid
    b_star = (lo + hi) / 2
    g, x, y, = gfloat(b_star)
    val, x, y, A = lp_min(pats, caps, widths, rhs, b_star)

    # --- 2. basis: support of x, completed by tight (zero reduced cost) columns to full rank
    c = np.array([Hfloat(r, b_star) for cap, counts, r in pats])
    rc = c - A.T @ y
    order = sorted(range(len(pats)), key=lambda j: (0 if x[j] > 1e-9 else 1, abs(float(rc[j])), -float(x[j])))
    basis = []
    cols = []
    for j in order:
        if len(basis) == len(rhs):
            break
        if x[j] <= 1e-9 and abs(rc[j]) > 1e-7:
            continue
        col = column(pats[j], caps, widths)
        if rat_rank(cols + [col]) > len(cols):
            basis.append(j)
            cols.append(col)
    need(len(basis) == len(rhs), 'could not complete an optimal basis (degenerate LP); %d of %d' % (len(basis), len(rhs)))
    Bm = [[cols[k][i] for k in range(len(basis))] for i in range(len(rhs))]   # rows = constraints
    Binv = rat_inverse(Bm)
    xB = [sum(Binv[k][i] * rhs[i] for i in range(len(rhs))) for k in range(len(basis))]
    need(all(v >= 0 for v in xB), 'basis not primal feasible')
    active = [(pats[j], xB[k]) for k, j in enumerate(basis) if xB[k] > 0]
    idle = {}
    for (cap, counts, r), n in active:
        if r:
            idle[r] = idle.get(r, 0) + n
    full = dict(local_rep)
    for r, n in idle.items():
        full[r] = full.get(r, 0) + n
    cap_lo, cap_hi = R.root_bracket(full, LIVE, digits, check_mass_T=1 if mass_ok else None)

    # --- 3. exact dual in the H basis: y_j(b) = sum_k (B^-T)_{j,k} H_{r_k}(b)
    ranks = sorted({r for cap, counts, r in pats if r})
    # (B^-T)_{j,k} = Binv[k][j]
    Y = {j: {} for j in range(len(rhs))}
    for j in range(len(rhs)):
        for k, pj in enumerate(basis):
            r = pats[pj][2]
            if r == 0 or Binv[k][j] == 0:
                continue
            Y[j][r] = Y[j].get(r, 0) + Binv[k][j]
    Hhi = {r: R.H(r, cap_hi) for r in ranks}
    tight = []
    strict = 0
    min_slack = None
    for p in pats:
        cap, counts, r = p
        a = column(p, caps, widths)
        coeff = {}
        if r:
            coeff[r] = Q(1)
        for j in range(len(rhs)):
            if a[j] == 0:
                continue
            for k, v in Y[j].items():
                coeff[k] = coeff.get(k, 0) - a[j] * v
        coeff = {k: v for k, v in coeff.items() if v != 0}
        if not coeff:
            tight.append(p)
            continue
        lower = sum(v * (Hhi[k][0] if v > 0 else Hhi[k][1]) for k, v in coeff.items())
        need(lower > 0, 'dual sign failure for pattern %s (reduced-cost lower bound %s)' % (str(p), str(lower)))
        strict += 1
        min_slack = lower if min_slack is None else min(min_slack, lower)
    dual_obj = sum(rhs[j] * sum(v * Hhi[k][0] for k, v in Y[j].items()) for j in range(len(rhs)))  # not needed for the proof, informational
    dual_rows = ['cap%d' % c for c in caps] + ['w%d' % w for w in widths]
    return dict(
        status='PASS_EXACT_RELAXATION_CAP' if mass_ok else 'PASS_EXACT_RELAXATION_CAP_MASS_NOT_65088',
        cap_lower=str(cap_lo), cap_upper=str(cap_hi), cap_lower_decimal=R.mpmath_str(cap_lo, digits), cap_upper_decimal=R.mpmath_str(cap_hi, digits),
        patterns=len(pats), tight_patterns=len(tight), strict_patterns=strict, minimum_slack_lower=str(min_slack),
        basis_patterns=[dict(capacity=pats[j][0], widths=[w for w, n in zip(widths, pats[j][1]) for _ in range(n)], count_per_replica=str(xB[k])) for k, j in enumerate(basis)],
        tight_pattern_list=[dict(capacity=p[0], widths=[w for w, n in zip(widths, p[1]) for _ in range(n)]) for p in tight],
        idle_per_replica={str(r): str(n) for r, n in sorted(idle.items())},
        idle_mass_per_replica=str(idle_mass), local_mass_per_replica=str(local_mass), rank_mass_per_replica=str(local_mass + idle_mass), rank_mass_identity=mass_ok,
        dual_Y={dual_rows[j]: {str(k): str(v) for k, v in sorted(Y[j].items())} for j in range(len(rhs))},
        inventory_per_call={str(w): str(inventory[w]) for w in widths}, local_per_call={str(r): str(n) for r, n in sorted(local.items())}, bins_per_replica=bins,
        delta_vs_PR2857_realized=dict(lower=str(cap_lo - PR2857_REALIZED_UPPER), upper=str(cap_hi - PR2857_REALIZED_LOWER), float=float(cap_lo - PR2857_REALIZED_LOWER)),
        delta_vs_PR2857_cap=dict(float=float(cap_lo - PR2857_CAP_UPPER)),
        assumptions='fixed capacities 8/16/32/48 (112 ports x 6/4/4/4 children per replica), all count-vector patterns with sum<=cap, one idle child of rank cap-used per bin, chronology/windows/collisions/integrality ignored, local profile fully paid; upper bound on any actual fill of this inventory, not a witness',
    )


def scenarios():
    base_local, base_inv = PR2857_LOCAL, PR2857_INV
    def mod(dl, di):
        l = {r: base_local.get(r, 0) + dl.get(r, 0) for r in set(base_local) | set(dl)}
        i = {w: base_inv.get(w, 0) + di.get(w, 0) for w in set(base_inv) | set(di)}
        return {r: n for r, n in l.items() if n}, {w: n for w, n in i.items() if n}
    table = [
        ('PR2857 actual (calibration)', {}, {}),
        ('one more 9->8 at PR2857 cost {1:+3,2:-2}', {1: 3, 2: -2}, {8: 1, 9: -1}),
        ('one more 9->8 at PR2853 cost {1:+5,2:-3}', {1: 5, 2: -3}, {8: 1, 9: -1}),
        ('one more 9->8 at minimal cost {1:+1,2:-1}', {1: 1, 2: -1}, {8: 1, 9: -1}),
        ('two more 9->8 at PR2857 cost {1:+6,2:-4}', {1: 6, 2: -4}, {8: 2, 9: -2}),
        ('four more 9->8 at PR2857 cost {1:+12,2:-8}', {1: 12, 2: -8}, {8: 4, 9: -4}),
        ('one 8->7 at PR2857-like cost {1:+3,2:-2}', {1: 3, 2: -2}, {7: 1, 8: -1}),
        ('one 8->7 at minimal cost {1:+1,2:-1}', {1: 1, 2: -1}, {7: 1, 8: -1}),
        ('one 9->7 (two units) at cost {1:+6,2:-4}', {1: 6, 2: -4}, {7: 1, 9: -1}),
        ('remove one width-9 helper, its 9 one-dim climbs vanish {1:-9}', {1: -9}, {9: -1}),
        ('remove one width-9 helper paying {1:-7,2:-1}', {1: -7, 2: -1}, {9: -1}),
        ('remove one width-8 helper {1:-8}', {1: -8}, {8: -1}),
        ('remove one width-4 helper {1:-4}', {1: -4}, {4: -1}),
        ('local only: +1 H1 -1 H2 per call (mass -1, inventory unchanged: NOT a legal word, derivative probe)', {1: 1, 2: -1}, {}),
        ('local only: -1 H1 per call (mass -1, derivative probe)', {1: -1}, {}),
        ('local only: 2 H1 -> 1 H2 per call (mass neutral)', {1: -2, 2: 1}, {}),
        ('local only: 1 H3 -> 1 H1 + 1 H2 per call (mass neutral)', {3: -1, 1: 1, 2: 1}, {}),
    ]
    out = []
    for name, dl, di in table:
        l, i = mod(dl, di)
        try:
            r = relax(l, i)
            row = dict(scenario=name, delta_local=dl, delta_inventory=di, cap_lower=r['cap_lower_decimal'], cap_upper=r['cap_upper_decimal'],
                       gain_vs_PR2857_realized_float=r['delta_vs_PR2857_realized']['float'], gain_vs_PR2857_cap_float=r['delta_vs_PR2857_cap']['float'],
                       tight=r['tight_patterns'], patterns=r['patterns'], idle_per_replica=r['idle_per_replica'], basis=r['basis_patterns'], rank_mass_identity=r['rank_mass_identity'], status=r['status'])
        except Exception as e:  # noqa
            row = dict(scenario=name, delta_local=dl, delta_inventory=di, error=str(e))
        out.append(row)
        print('%-95s cap<= %s  gain vs realized %+.4e  vs cap %+.4e  %s' % (name, row.get('cap_upper', '?'), row.get('gain_vs_PR2857_realized_float', float('nan')), row.get('gain_vs_PR2857_cap_float', float('nan')), row.get('error', '')), file=sys.stderr, flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--scenarios', action='store_true')
    ap.add_argument('--inventory', help='JSON per-call {width: count}')
    ap.add_argument('--local', help='JSON per-call {rank: count}')
    ap.add_argument('--delta-inventory', help='JSON {width: +-count} relative to PR2857')
    ap.add_argument('--delta-local', help='JSON {rank: +-count} relative to PR2857')
    ap.add_argument('--digits', type=int, default=25)
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.calibrate:
        r = relax(PR2857_LOCAL, PR2857_INV, digits=a.digits)
        r['reproduces_PR2857_cap_lower'] = (Q(r['cap_lower']) == Q('215012600677110740993/125000000000000000000000'))
        r['bracket_inside_PR2857_bracket'] = (Q(r['cap_lower']) >= Q('215012600677110740993/125000000000000000000000') and Q(r['cap_upper']) <= PR2857_CAP_UPPER)
        r['reproduces_PR2857_cap_upper_at_24_digits'] = (relax(PR2857_LOCAL, PR2857_INV, digits=24)['cap_upper'] == str(PR2857_CAP_UPPER))
        r['reproduces_PR2857_pattern_count_1163'] = (r['patterns'] == 1163)
        r['reproduces_PR2857_11_tight_1152_strict'] = (r['tight_patterns'] == 11 and r['strict_patterns'] == 1152)
        res = r
    elif a.scenarios:
        res = scenarios()
    else:
        local = dict(PR2857_LOCAL)
        inv = dict(PR2857_INV)
        if a.local:
            local = {int(k): Q(v) for k, v in json.loads(a.local).items()}
        if a.inventory:
            inv = {int(k): Q(v) for k, v in json.loads(a.inventory).items()}
        if a.delta_local:
            for k, v in json.loads(a.delta_local).items():
                local[int(k)] = local.get(int(k), 0) + Q(v)
        if a.delta_inventory:
            for k, v in json.loads(a.delta_inventory).items():
                inv[int(k)] = inv.get(int(k), 0) + Q(v)
        res = relax({k: v for k, v in local.items() if v}, {k: v for k, v in inv.items() if v}, digits=a.digits)
    s = json.dumps(res, indent=1, sort_keys=True, default=str)
    if a.out:
        open(a.out, 'w').write(s)
    print(s)


if __name__ == '__main__':
    main()
