#!/usr/bin/env python3
"""diag_lp.py -- chronological flow LP diagnostics (HiGHS) for a target pattern mix:
 mode elastic : global pattern targets become soft (slack +/-), minimize total slack -> which pattern counts the chronology forces to move
 mode free    : no global targets, catalogue = given patterns, minimize the linearized moment sum_bins H_idle(b*) -> fractional chronological optimum
Usage: python diag_lp.py --chronology pr2833-t37 --providers P.json --mix PATTERNS.json --mode elastic
       python diag_lp.py --chronology pr2833-t37 --providers P.json --mode free --catalogue tight+6 [--out mix.json]"""
import os, sys
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
import argparse, collections, json, pathlib, time, types
import numpy as np
from scipy.sparse import coo_matrix
from scipy.optimize import linprog
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fill17 as F, relax as X

ap = argparse.ArgumentParser()
ap.add_argument('--chronology', default='pr2833-t37'); ap.add_argument('--providers', required=True)
ap.add_argument('--mix'); ap.add_argument('--mode', choices=['elastic', 'free', 'calls'], default='elastic')
ap.add_argument('--catalogue', default='tight', help="free mode: 'tight' (relaxation tight + single residues + empty) | 'rc:<x>' (all patterns with reduced cost <= x in H units)")
ap.add_argument('--out')
a = ap.parse_args()
owner = types.ModuleType('o'); exec(compile(F.ENGINE.read_bytes(), 'o', 'exec'), owner.__dict__)
template, plan, order, dispatch, T = F.load_chronology(a.chronology)
providers = F.load_providers(pathlib.Path(a.providers))
disp = {(s, r): p for s, r, p in dispatch}
inv_by_call = [collections.Counter(providers[disp[tuple(sr)]]['widths']) for sr in order]
loc = next(iter(providers.values()))['actual_paid_profile']
WID = sorted({w for inv in inv_by_call for w in inv})
avg = collections.Counter()
for inv in inv_by_call:
    for w, n in inv.items():
        avg[w] += Q(n, len(order))
rel = X.relax(loc, avg)
b = float((Q(rel['cap_lower']) + Q(rel['cap_upper'])) / 2)
if a.mode in ('elastic', 'calls'):
    mf = json.load(open(a.mix))
    assert [int(w) for w in mf['widths']] == WID
    target = {(int(c), tuple(q)): int(n) for c, q, n in mf['target']}
    cat = collections.defaultdict(set)
    for (c, q) in target:
        cat[c].add(q)
elif a.mix:
    mf = json.load(open(a.mix))
    assert [int(w) for w in mf['widths']] == WID
    cat = collections.defaultdict(set)
    for c, q, n in mf['target']:
        cat[int(c)].add(tuple(q))
    target = None
else:
    pats = X.patterns(X.BINS, WID)
    if a.catalogue == 'tight':
        keep = {(t['capacity'], tuple(t['widths'].count(w) for w in WID)) for t in rel['tight_pattern_list']}
        for cap in X.BINS:
            for i, w in enumerate(WID):
                if w <= cap:
                    keep.add((cap, tuple(int(j == i) for j in range(len(WID)))))
            keep.add((cap, tuple(0 for _ in WID)))
    else:
        thr = float(a.catalogue.split(':')[1])
        # reduced cost at b from the exact dual rows Y (H-basis): rc = H_idle - y_cap - sum n_w y_w
        Y = rel['dual_Y']
        def yv(row):
            return sum(float(Q(v)) * X.Hfloat(int(k), b) for k, v in Y[row].items())
        keep = set()
        for cap, counts, r in pats:
            rc = X.Hfloat(r, b) - yv('cap%d' % cap) - sum(n * yv('w%d' % w) for w, n in zip(WID, counts))
            if rc <= thr:
                keep.add((cap, counts))
    cat = collections.defaultdict(set)
    for cap, counts, r in pats:
        if (cap, counts) in keep:
            cat[cap].add(counts)
    target = None
print('catalogue sizes', {c: len(v) for c, v in sorted(cat.items())}, 'b*', b, flush=True)
win = owner.windows(template, order, T)
need = {t: collections.Counter(inv_by_call[t]) for t in range(len(order))}
groups = collections.defaultdict(list)
for (o, c), (cap, lo, hi) in win.items():
    for port in range(112):
        groups[cap, tuple(range(max(0, lo + 1), min(len(order), hi + 1)))].append((o, c, port))
G = sorted(groups)
rows_eq, rows_ub = [], []
edge, ncol = [], [0]
cost = []
def var(c=0.0):
    j = ncol[0]; ncol[0] += 1; cost.append(c); return j
eq_rhs, ub_rhs = [], []
def eq(r):
    i = len(eq_rhs); eq_rhs.append(r); return ('e', i)
def ub(r):
    i = len(ub_rhs); ub_rhs.append(r); return ('u', i)
E = []
def put(row, v, n):
    E.append((row[0], row[1], v, n))
Xv, Zv = {}, {}
callrow = {(t, w): eq(n) for t, cnt in need.items() for w, n in cnt.items() if n}
short = {}
if a.mode == 'calls':
    for key, r in callrow.items():
        sv = var(1.0); put(r, sv, 1); short[key] = sv
globalrow = {}
if target is not None and a.mode == 'elastic':
    for key, n in target.items():
        r = eq(n); globalrow[key] = r
        sp, sm = var(1.0), var(1.0)
        put(r, sp, 1); put(r, sm, -1)
for gi, (cap, ts) in enumerate(G):
    nb = len(groups[G[gi]])
    br = eq(nb)
    for q in sorted(cat[cap]):
        idle = cap - sum(w * k for w, k in zip(WID, q))
        if idle < 0:
            continue
        xv = var(X.Hfloat(idle, b) if (target is None and idle) else 0.0)
        Xv[gi, q] = xv
        put(br, xv, 1)
        if (cap, q) in globalrow:
            put(globalrow[cap, q], xv, 1)
        residual = {w: q[j] for j, w in enumerate(WID) if q[j]}
        wr = {w: eq(0) for w in residual}
        for w, n in residual.items():
            put(wr[w], xv, -n)
        for t in ts:
            tr = ub(0)
            put(tr, xv, -1)
            for w in residual:
                if (t, w) not in callrow:
                    continue
                zv = var(0.0)
                Zv[gi, q, t, w] = zv
                put(tr, zv, 1); put(wr[w], zv, 1); put(callrow[t, w], zv, 1)
n = ncol[0]
Ae = coo_matrix(([e[3] for e in E if e[0] == 'e'], ([e[1] for e in E if e[0] == 'e'], [e[2] for e in E if e[0] == 'e'])), shape=(len(eq_rhs), n)).tocsr()
Au = coo_matrix(([e[3] for e in E if e[0] == 'u'], ([e[1] for e in E if e[0] == 'u'], [e[2] for e in E if e[0] == 'u'])), shape=(len(ub_rhs), n)).tocsr()
print('LP vars', n, 'eq', len(eq_rhs), 'ub', len(ub_rhs), flush=True)
t0 = time.time()
res = linprog(np.array(cost), A_ub=Au, b_ub=np.array(ub_rhs, dtype=float), A_eq=Ae, b_eq=np.array(eq_rhs, dtype=float), bounds=(0, None), method='highs', options={'time_limit': 1200})
print('LP status', res.status, res.message, '%.1f s' % (time.time() - t0), 'objective', res.fun, flush=True)
if res.x is not None:
    usage = collections.Counter()
    for (gi, q), v in Xv.items():
        if res.x[v] > 1e-7:
            usage[G[gi][0], q] += res.x[v]
    out = {}
    for (cap, q), x in sorted(usage.items()):
        name = '%d:%s' % (cap, '+'.join(str(w) for w, k in zip(WID, q) for _ in range(k)) or 'empty')
        tgt = target.get((cap, q), 0) if target is not None else None
        out[name] = (round(x, 3), tgt)
    for k, v in out.items():
        if target is None or abs(v[0] - v[1]) > 1e-6:
            print('  ', k, v)
    if short:
        sh = collections.Counter()
        for (t, w), sv in short.items():
            if res.x[sv] > 1e-7:
                sh[t, w] += res.x[sv]
        print('call shortfalls (t, w): amount', sorted(((k, round(v, 3)) for k, v in sh.items()))[:80], 'total', round(sum(sh.values()), 3))
        print('calls with shortfall', sorted({t for t, w in sh}))
    if target is not None and a.mode == 'elastic':
        missing = {('%d:%s' % (c, q)): n for (c, q), n in target.items() if usage.get((c, q), 0) < n - 1e-6}
        print('targets under-supplied:', missing)
    if a.out:
        json.dump(dict(widths=WID, usage={k: v[0] for k, v in out.items()}, objective=res.fun, b=b), open(a.out, 'w'), indent=1)
