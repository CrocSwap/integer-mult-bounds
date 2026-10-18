"""Class-level window LP/IP for the T16 owner bins with aggregate family-time (R4) cuts (fifth version).
Classes = (capacity, allowed calls); variables x[class, pattern] (bins of the class with that width multiset) and
y[class, call, width] (helpers of that call and width hosted by the class); constraints: class sizes, width balance,
demand per (call, width), and for every group of classes that share physical families (64 groups) and every call,
at most (number of families in the group) helpers of that call. Objective: the surrogate sum g(free), g(f) = f ln f.
It is a relaxation of the bin-level problem (no per-bin call distinctness beyond the R4 aggregate), used here
only as a search guide; the proved ceiling is ceiling_bound.py (PROOF.md).
argv: LIBDIR OWNERS MODE(lp|ip) [TL] [R4=1] [WORKERS] [OUT_JSON]
ip mode (CP-SAT) env: HINT = JSON solution to hint (default: the OWNERS map's own class solution);
  FREE = n and SEED: only n classes, drawn at random, may change (all others are fixed to the OWNERS map);
  FREEFROM = a full-model ip JSON (target): draw the FREE classes only from classes whose (x, y) differ from it;
  PEN = penalty per unit of |x - x_cur| and |y - y_cur| (change penalty); GAIN = required surrogate gain over the
  OWNERS map (in surrogate units). With PEN, the objective is surrogate*1e4 - PEN * (total change).
Needs CPython 3.12, numpy, scipy (lp) or ortools (ip)."""
import sys, math, json; sys.path.insert(0, sys.argv[1]); import lib
import numpy as np, scipy.sparse as sp
from collections import Counter, defaultdict
m = lib.Model(lib.read(sys.argv[2])); MODE = sys.argv[3]; TL = float(sys.argv[4]) if len(sys.argv) > 4 else 600
R4 = (sys.argv[5] if len(sys.argv) > 5 else '1') == '1'
W = [4, 5, 7, 8, 9]; g = lib.g
cls = defaultdict(list)
for k in m.cap: cls[m.cap[k], frozenset(m.allowed[k])].append(k)
CL = list(cls); cid = {}
for i, c in enumerate(CL):
    for k in cls[c]: cid[k] = i
fam = defaultdict(set)
for k in m.cap: fam[m.fam[k]].add(cid[k])
groups = Counter(frozenset(v) for v in fam.values())
D = Counter((z['time'], z['width']) for z in m.roles)
def pats(cap):
    out = []
    def rec(i, rem, cur):
        if i == len(W): out.append(tuple(cur)); return
        for c in range(rem // W[i] + 1): rec(i+1, rem - c*W[i], cur + [c])
    rec(0, cap, []); return out
P = {cap: pats(cap) for cap in (8, 16, 32, 48)}
var = []; obj = []
for ci, (cap, al) in enumerate(CL):
    for p in P[cap]: var.append(('x', ci, p)); obj.append(g(cap - sum(a*w for a, w in zip(p, W))))
for ci, (cap, al) in enumerate(CL):
    for t in al:
        for w in W:
            if D[t, w] and w <= cap: var.append(('y', ci, t, w)); obj.append(0.0)
idx = {v: i for i, v in enumerate(var)}
rows = []; rhs = []; sense = []
def add(coefs, s, b): rows.append(coefs); sense.append(s); rhs.append(b)
xby = defaultdict(list); yby = defaultdict(list)
for v in var:
    if v[0] == 'x': xby[v[1]].append(v)
    else: yby[v[1], v[3]].append(v)
for ci, (cap, al) in enumerate(CL):
    add([(idx[v], 1) for v in xby[ci]], '=', len(cls[CL[ci]]))
    for j, w in enumerate(W):
        co = [(idx[v], -v[2][j]) for v in xby[ci] if v[2][j]] + [(idx[v], 1) for v in yby[ci, w]]
        if co: add(co, '=', 0)
ytw = defaultdict(list)
for v in var:
    if v[0] == 'y': ytw[v[2], v[3]].append(idx[v])
for tw, d in D.items(): add([(i, 1) for i in ytw[tw]], '=', d)
if R4:
    yct = defaultdict(list)
    for v in var:
        if v[0] == 'y': yct[v[1], v[2]].append(idx[v])
    for G, n in groups.items():
        ts = set().union(*(CL[c][1] for c in G))
        for t in ts:
            co = [(i, 1) for c in G for i in yct.get((c, t), [])]
            if co: add(co, '<', n)
print('vars', len(var), 'rows', len(rows), 'groups', len(groups), flush=True)
if MODE == 'lp':
    from scipy.optimize import linprog
    def mat(sel):
        r = []; c = []; d = []
        for ri, j in enumerate(sel):
            for i, a in rows[j]: r.append(ri); c.append(i); d.append(a)
        return sp.csr_matrix((d, (r, c)), shape=(len(sel), len(var)))
    eq = [j for j, s in enumerate(sense) if s == '=']; le = [j for j, s in enumerate(sense) if s == '<']
    res = linprog(-np.array(obj), A_eq=mat(eq), b_eq=[rhs[j] for j in eq], A_ub=mat(le) if le else None, b_ub=[rhs[j] for j in le] if le else None, method='highs')
    print('LP', -res.fun, res.status)
    x = res.x; prof = Counter()
    for v, i in idx.items():
        if v[0] == 'x' and x[i] > 1e-6:
            cap = CL[v[1]][0]; f = cap - sum(a*w for a, w in zip(v[2], W))
            if f: prof[f] += x[i]
    print('profile', {f: round(n, 2) for f, n in sorted(prof.items())})
else:
    from ortools.sat.python import cp_model
    md = cp_model.CpModel(); X = []
    for i, v in enumerate(var):
        ub = len(cls[CL[v[1]]]) if v[0] == 'x' else D[v[2], v[3]]
        X.append(md.NewIntVar(0, ub, ''))
    for co, s, b in zip(rows, sense, rhs):
        e = sum(a*X[i] for i, a in co)
        md.Add(e == b) if s == '=' else md.Add(e <= b)
    # hint from current map
    cur = Counter()
    for k in m.cap:
        c = Counter(m.roles[i]['width'] for i in m.members[k]); cur[cid[k], tuple(c[w] for w in W)] += 1
    ycur = Counter((cid[m.bin(i)], z['time'], z['width']) for i, z in enumerate(m.roles))
    import os
    if os.environ.get('HINT'):
        hd = json.load(open(os.environ['HINT'])); hx = Counter({(ci, tuple(p)): v for ci, p, v in hd['x']}); hy = Counter({(ci, t, w): v for ci, t, w, v in hd['y']})
        for v, i in idx.items(): md.AddHint(X[i], hx[v[1], v[2]] if v[0] == 'x' else hy[v[1], v[2], v[3]])
    else:
        for v, i in idx.items(): md.AddHint(X[i], cur[v[1], v[2]] if v[0] == 'x' else ycur[v[1], v[2], v[3]])
    import os, random
    if os.environ.get('FREE'):
        rr = random.Random(int(os.environ.get('SEED', 0)))
        pool = list(range(len(CL)))
        if os.environ.get('FREEFROM'):
            fd = json.load(open(os.environ['FREEFROM'])); fx = Counter({(ci, tuple(p)): v for ci, p, v in fd['x']}); fy = Counter({(ci, t, w): v for ci, t, w, v in fd['y']})
            ch = {kk[0] for kk in set(fx) | set(cur) if fx[kk] != cur[kk]} | {kk[0] for kk in set(fy) | set(ycur) if fy[kk] != ycur[kk]}
            pool = sorted(ch)
        FREE = set(rr.sample(pool, min(len(pool), int(os.environ['FREE']))))
        print('free classes', sorted(FREE), flush=True)
        for v, i in idx.items():
            if v[1] not in FREE: md.Add(X[i] == (cur[v[1], v[2]] if v[0] == 'x' else ycur[v[1], v[2], v[3]]))
    PEN = int(os.environ.get('PEN', 0)); GAIN = float(os.environ.get('GAIN', 0))
    E = sum(round(1e4*o)*X[i] for i, o in enumerate(obj) if o)
    if PEN:
        Ecur = sum(round(1e4*g(m.free(k))) for k in m.cap); pen = []
        for v, i in idx.items():
            c0 = cur[v[1], v[2]] if v[0] == 'x' else ycur[v[1], v[2], v[3]]
            d = md.NewIntVar(0, 10**6, ''); md.Add(d >= X[i] - c0); md.Add(d >= c0 - X[i]); pen.append(d)
        md.Add(E >= Ecur + round(1e4*GAIN))
        md.Maximize(E - PEN * sum(pen))
    else: md.Maximize(E)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = TL; s.parameters.num_workers = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    st = s.Solve(md); print(s.StatusName(st), 'obj', s.ObjectiveValue()/1e4, 'bound', s.BestObjectiveBound()/1e4)
    prof = Counter(); sol = []
    for v, i in idx.items():
        val = s.Value(X[i])
        if v[0] == 'x' and val:
            cap = CL[v[1]][0]; f = cap - sum(a*w for a, w in zip(v[2], W)); prof[f] += val; sol.append([v[1], list(v[2]), val])
    print('profile', dict(sorted(prof.items())))
    json.dump({'x': sol, 'y': [[v[1], v[2], v[3], s.Value(X[i])] for v, i in idx.items() if v[0] == 'y' and s.Value(X[i])]}, open(sys.argv[7] if len(sys.argv) > 7 else 'winip.json', 'w'))
