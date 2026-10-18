"""Whole-owner hosting model (linear-programming relaxation) and the pressure root b, for pricing complex helpers.

Setting (PR #523's 112-port unit, reused by PR #531, #568 and #569): the global word has 72 calls.  In every call a
number of helper registers of widths 4..9 must be hosted inside idle frame changes of the 144 owner groups (g = (orp, i),
idle rank r_g, a list of busy times) of PR #523's ASYNC112 plan; each group has P = 112 identical port copies.
Variables: y[g, pattern] = number of ports of group g that host the width multiset `pattern` (total width <= r_g; the
rest of the idle rank is paid as a child of rank r_g - width), x[g, t, w] = helpers of width w hosted by group g at
call t.  Constraints: sum_pattern y = P per group; sum_t x[g, t, w] = sum_pattern y n_w(pattern); sum_g x[g, t, w] =
demand[t][w]; sum_w x[g, t, w] <= P (one helper per port family and call).  Objective: sum y * f(r_g - width), with
f(rho) = rho ((m / rho)^q - 1), m = 73, evaluated at q = the current pressure root.  This is the same model as the
integer program of the earlier hosting solver, with y and x continuous (solved by HiGHS).

b_float(profile, W) is the root q of  sum_r z_r (r / (m W)) (m / r)^q + 32 m (sum z) m^q / (1e16 W) = 1  for a paid
profile {rank r: count z}, found by bisection (the second term is the 1e-16 envelope term; W enters only there and in
the first term's normalisation); mass(profile) = sum r z.
"""
import time
from collections import defaultdict

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

from report import load_json, main_file

M = 73                       # rank modulus m
PORTS = 112                  # port copies per owner group (v)
W_DATA = 7168                # W of the 112-port unit
PLAN_REL = 'research/punctured112-global/inputs/ASYNC112-PLAN.json'
CALLS = 72


def groups():
    """the 144 owner groups (orp, i, idle rank r, busy call times) of PR #523's ASYNC112 plan, sorted by (orp, i)"""
    plan = load_json(main_file(PLAN_REL))
    out = []
    for key, (r, ts) in plan['windows'].items():
        orp, i = map(int, key.split(','))
        out.append((orp, i, r, ts))
    return sorted(out)


def patterns(r, widths, maxk):
    """all multisets of the given widths (counts per width, in sorted width order) with total width <= r and at most
    maxk helpers"""
    ws = sorted(widths)
    out = []

    def rec(idx, rem, cur):
        if idx == len(ws):
            out.append(tuple(cur))
            return
        w = ws[idx]
        c = 0
        while c * w <= rem and sum(cur) + c <= maxk:
            rec(idx + 1, rem - c * w, cur + [c])
            c += 1
    rec(0, r, [])
    return ws, out


def f_cost(rho, q):
    return 0.0 if rho == 0 else rho * ((M / rho) ** q - 1)


def solve_lp(dem_t, q, time_limit=900):
    """LP relaxation of the hosting model for the per-call demands dem_t (72 dicts {width: count}) at pressure q.
    Returns dict(status, obj, rem = {idle remainder rank: number of paid remainders}, secs)."""
    G = groups()
    widths = sorted({w for d in dem_t for w in d if any(dd.get(w, 0) for dd in dem_t)})
    widx = {w: i for i, w in enumerate(widths)}
    xvars = {}                                   # (g, t, w) -> column
    nvar = 0
    ylist = []                                   # (g, pattern, total width, cost, column)
    for gi, (orp, i, r, ts) in enumerate(G):
        ws, pats = patterns(r, widths, len(ts))
        for p in pats:
            size = sum(c * w for c, w in zip(p, ws))
            ylist.append((gi, p, size, f_cost(r - size, q), nvar))
            nvar += 1
    for gi, (orp, i, r, ts) in enumerate(G):
        for t in ts:
            for w in widths:
                xvars[gi, t, w] = nvar
                nvar += 1
    c = np.zeros(nvar)
    for gi, p, size, co, col in ylist:
        c[col] = co
    rows, cs, vs, beq = [], [], [], []
    nr = 0
    ybyg = defaultdict(list)
    for gi, p, size, co, col in ylist:
        ybyg[gi].append((p, col))
    for gi in range(len(G)):                     # sum_pattern y = P
        for p, col in ybyg[gi]:
            rows.append(nr); cs.append(col); vs.append(1.0)
        beq.append(float(PORTS)); nr += 1
    for gi, (orp, i, r, ts) in enumerate(G):     # hosted helpers of width w = helpers the patterns provide
        for w in widths:
            for t in ts:
                rows.append(nr); cs.append(xvars[gi, t, w]); vs.append(1.0)
            for p, col in ybyg[gi]:
                n = p[widx[w]]
                if n:
                    rows.append(nr); cs.append(col); vs.append(-float(n))
            beq.append(0.0); nr += 1
    gt = defaultdict(list)
    for gi, (orp, i, r, ts) in enumerate(G):
        for t in ts:
            gt[t].append(gi)
    for t in range(CALLS):                       # demand
        for w in widths:
            for gi in gt[t]:
                rows.append(nr); cs.append(xvars[gi, t, w]); vs.append(1.0)
            beq.append(float(dem_t[t].get(w, 0))); nr += 1
    Aeq = sp.csr_matrix((vs, (rows, cs)), shape=(nr, nvar))
    rows, cs, vs, bub = [], [], [], []
    nu = 0
    for gi, (orp, i, r, ts) in enumerate(G):     # one helper per port family and call
        for t in ts:
            for w in widths:
                rows.append(nu); cs.append(xvars[gi, t, w]); vs.append(1.0)
            bub.append(float(PORTS)); nu += 1
    Aub = sp.csr_matrix((vs, (rows, cs)), shape=(nu, nvar))
    t0 = time.time()
    res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=(0, None), method='highs',
                  options=dict(time_limit=time_limit))
    out = dict(status=int(res.status), obj=res.fun, secs=time.time() - t0)
    if res.status == 0:
        rem = defaultdict(float)
        for gi, p, size, co, col in ylist:
            v = res.x[col]
            if v > 1e-9 and G[gi][2] - size > 0:
                rem[G[gi][2] - size] += v
        out['rem'] = dict(sorted(rem.items()))
    return out


def mass(p):
    return sum(r * z for r, z in p.items())


def b_float(p, W):
    lo, hi = 0., .01
    for _ in range(100):
        q = (lo + hi) / 2
        mom = (sum(r * z / (M * W) * (M / r) ** q for r, z in p.items())
               + 32 * M * sum(p.values()) / (10 ** 16 * W) * M ** q)
        if mom < 1:
            lo = q
        else:
            hi = q
    return (lo + hi) / 2


def profile_with_remainder(local_profiles, rem):
    """paid profile = sum of the per-call local profiles + the LP's idle remainders (rank -> count)"""
    p = defaultdict(float)
    for l in local_profiles:
        for r, z in l.items():
            p[r] += z
    for r, z in rem.items():
        p[int(r)] += float(z)
    return {r: z for r, z in p.items() if z > 1e-12}


def run_job(job):
    """worker for a process pool: job = (name, local profiles per call, demands per call, q); solves the hosting LP,
    builds the paid profile and its b"""
    name, out_l, out_d, q = job
    o = solve_lp(out_d, q)
    if o['status'] != 0:
        return dict(name=name, status=o['status'], secs=o['secs'])
    p = profile_with_remainder(out_l, o['rem'])
    return dict(name=name, status=0, obj=o['obj'], rem={int(k): float(v) for k, v in o['rem'].items()},
                b=b_float(p, W_DATA), mass=mass(p), secs=o['secs'])
