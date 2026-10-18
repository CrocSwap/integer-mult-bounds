"""Min-diff toward the selected map A at a target idle profile, class level, stage 1 (HiGHS MIP). Bins of one (cap, allowed-window) class are interchangeable, and at
most one helper per bin per call. Variables: pattern counts x[c,p] (width multiplicities per bin), flows y[c,t,w]
(helpers of call t, width w hosted by class c). Constraints: class sizes, width balance, demand per (t, w),
Hall per (c, t) for single widths and for all widths, idle profile = target. Objective: maximise
sum min(y, yA) (an upper bound on placements of A that can be kept), tie-break: fewer pattern changes.
If solved to optimality without FIX/KEEP, 69,120 minus the kept flow bounds the relocations from below within this
relaxation (up to the small tie-break weight EPS). Stage 1 is a relaxation of the bin-level problem, so
mindiff_cls2.py can find a class unrealisable; such classes are then fixed to A (FIX) and stage 1 is re-solved.
argv: LIBDIR TARGET_OWNERS OUT_JSON TIME_LIMIT [START_OWNERS (warm start; must have the target profile)]
env: FIX = JSON list of class indices kept exactly as in A (used when stage 2 cannot realise a class);
     KEEP = a previous stage-1 JSON whose (x, y) every class outside FIX and FREE (JSON list) keeps exactly
     (FREE classes pay a small cost for moving away from KEEP's flows);
     BAN = JSON list of [class, pattern] pairs forbidden in that class (fourth version: class 9 cannot host
     eleven bins of four width-4 helpers, which need four distinct calls each; Hall alone does not see this).
Needs CPython 3.12, numpy, scipy, highspy. Single thread."""
import sys, json, time, itertools
sys.path.insert(0, sys.argv[1]); import lib
import numpy as np, highspy
from scipy.sparse import coo_matrix
from collections import Counter, defaultdict
A = lib.selroles; F = lib.read(sys.argv[2]); OUT = sys.argv[3]; TL = float(sys.argv[4])
m = lib.Model(A); W = [4, 5, 7, 8, 9]
B = lambda z: (z['owner_replica'], z['child'], z['port'])
cls = defaultdict(list)
for k in sorted(m.cap): cls[m.cap[k], frozenset(m.allowed[k])].append(k)
CL = list(cls); cid = {k: ci for ci, key in enumerate(CL) for k in cls[key]}
D = Counter((z['time'], z['width']) for z in A)
T = lib.idle_of(F)
cnt = defaultdict(Counter); yA = Counter()
for z in A: cnt[B(z)][z['width']] += 1; yA[cid[B(z)], z['time'], z['width']] += 1
xA = Counter((cid[k], tuple(cnt[k][w] for w in W)) for k in m.cap)
def pats(cap):
    o = []
    def rec(i, rem, cur):
        if i == len(W): o.append(tuple(cur)); return
        for c in range(rem // W[i] + 1): rec(i + 1, rem - c * W[i], cur + [c])
    rec(0, cap, []); return o
P = {cap: pats(cap) for cap in (8, 16, 32, 48)}
var_lo, var_hi, cost, integ = [], [], [], []
def var(lo, hi, c=0.0, i=True):
    var_lo.append(lo); var_hi.append(hi); cost.append(c); integ.append(i); return len(var_lo) - 1
R, Cc, V, lo, hi = [], [], [], [], []
def con(e, l, h):
    r = len(lo)
    for j, v in e: R.append(r); Cc.append(j); V.append(v)
    lo.append(l); hi.append(h)
X = {}; Y = {}; prof = defaultdict(list); DV = {}; KV = {}; HV = {}
EPS = 1e-3
for ci, (cap, al) in enumerate(CL):
    n = len(cls[CL[ci]]); ws = defaultdict(list)
    for p in P[cap]:
        if sum(p) > len(al) or max(p) > n: continue
        j = var(0, n); X[ci, p] = j
        f = cap - sum(c * w for c, w in zip(p, W))
        if f: prof[f].append(j)
        for c, w in zip(p, W):
            if c: ws[w].append((j, c))
        if xA[ci, p]:   # d >= xA - x, cost EPS per lost pattern bin
            d = var(0, n, EPS, False); con([(d, 1), (j, 1)], xA[ci, p], np.inf); DV[ci, p] = d
    con([(j, 1) for (c2, p), j in X.items() if c2 == ci], n, n)
    pert = defaultdict(dict)
    for w in W:
        ys = []
        for t in sorted(al):
            if D[t, w]:
                j = var(0, min(D[t, w], n)); Y[ci, t, w] = j; ys.append((j, 1)); pert[t][w] = j
                if yA[ci, t, w]:
                    k = var(0, yA[ci, t, w], -1.0, False); con([(k, 1), (j, -1)], -np.inf, 0); KV[ci, t, w] = k
        con(ys + [(j, -c) for j, c in ws[w]], 0, 0)
    # Hall: per t and width w, y <= bins whose pattern holds w; all widths: sum_w y <= nonempty bins
    hv = {}
    for w in W + [0]:   # hv[w] = bins whose pattern holds width w (0: any helper); aggregated once per class
        hv[w] = var(0, n, 0.0, False); HV[ci, w] = hv[w]
        con([(hv[w], 1)] + [(j, -1) for (c2, p), j in X.items() if c2 == ci and (p[W.index(w)] if w else sum(p))], 0, 0)
    for t, d in pert.items():
        for w, j in d.items(): con([(j, 1), (hv[w], -1)], -np.inf, 0)
        if len(d) > 1: con([(j, 1) for j in d.values()] + [(hv[0], -1)], -np.inf, 0)
byTW = defaultdict(list)
for (ci, t, w), j in Y.items(): byTW[t, w].append((j, 1))
for tw, d in D.items(): con(byTW[tw], d, d)
import os
FIX = set(json.loads(os.environ.get('FIX', '[]')))   # classes kept exactly as in A (x = xA, y = yA)
for (ci, p), j in X.items():
    if ci in FIX: con([(j, 1)], xA[ci, p], xA[ci, p])
for (ci, t, w), j in Y.items():
    if ci in FIX: con([(j, 1)], yA[ci, t, w], yA[ci, t, w])
BAN = json.loads(os.environ.get('BAN', '[]'))   # [[class, pattern], ...] forbidden (x = 0); used when stage 2
for ci, p in BAN:                                 # shows a pattern needs more distinct calls than the class can give
    con([(X[ci, tuple(p)], 1)], 0, 0)
if BAN: print('banned', BAN, flush=True)
KEEP = os.environ.get('KEEP')   # stage-1 JSON: classes not in FREE (and not in FIX) keep its (x, y) exactly
if KEEP:
    FREE = set(json.loads(os.environ.get('FREE', '[]'))); kd = json.load(open(KEEP))
    kx = Counter({(ci, tuple(p)): v for ci, p, v in kd['x']}); ky = Counter({(ci, t, w): v for ci, t, w, v in kd['y']})
    for (ci, p), j in X.items():
        if ci not in FIX and ci not in FREE: con([(j, 1)], kx[ci, p], kx[ci, p])
    for (ci, t, w), j in Y.items():
        if ci not in FIX and ci not in FREE: con([(j, 1)], ky[ci, t, w], ky[ci, t, w])
    for (ci, t, w), j in Y.items():   # free classes: small cost for moving away from KEEP's flows
        if ci in FREE and ci not in FIX:
            e = var(0, np.inf, 1e-4, False); con([(e, 1), (j, -1)], -ky[ci, t, w], np.inf); con([(e, 1), (j, 1)], ky[ci, t, w], np.inf)
    print('kept from', KEEP, 'free classes', sorted(FREE), flush=True)
print('fixed classes', sorted(FIX), flush=True)
for v in sorted(set(prof) | set(T)): con([(j, 1) for j in prof[v]], T[v], T[v])
nv = len(var_lo); Mx = coo_matrix((V, (R, Cc)), shape=(len(lo), nv)).tocsc()
print('vars', nv, 'cons', len(lo), 'A flows', sum(yA.values()), flush=True)
h = highspy.Highs(); h.setOptionValue('time_limit', TL); h.setOptionValue('threads', 1); h.setOptionValue('mip_rel_gap', 1e-6)
lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = len(lo); lp.col_cost_ = np.array(cost)
lp.col_lower_ = np.array(var_lo, float); lp.col_upper_ = np.array(var_hi, float)
lp.row_lower_ = np.array(lo, float); lp.row_upper_ = np.array(hi, float)
lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
lp.a_matrix_.start_ = Mx.indptr; lp.a_matrix_.index_ = Mx.indices; lp.a_matrix_.value_ = Mx.data.astype(float)
lp.integrality_ = [highspy.HighsVarType.kInteger if i else highspy.HighsVarType.kContinuous for i in integ]
h.passModel(lp)
if len(sys.argv) > 5:
    S0 = lib.read(sys.argv[5]); assert lib.idle_of(S0) == T
    c0 = defaultdict(Counter); y0 = Counter()
    for z in S0: c0[B(z)][z['width']] += 1; y0[cid[B(z)], z['time'], z['width']] += 1
    x0 = Counter((cid[k], tuple(c0[k][w] for w in W)) for k in m.cap)
    v0 = np.zeros(nv)
    for key, j in X.items(): v0[j] = x0[key]
    for key, j in Y.items(): v0[j] = y0[key]
    for key, j in DV.items(): v0[j] = max(0, xA[key] - x0[key])
    for key, j in KV.items(): v0[j] = min(yA[key], y0[key])
    for (ci, w), j in HV.items(): v0[j] = sum(v for (c2, p), v in x0.items() if c2 == ci and (p[W.index(w)] if w else sum(p)))
    s0 = highspy.HighsSolution(); s0.col_value = list(v0); s0.value_valid = True
    print('setSolution', h.setSolution(s0), 'start kept', sum(v0[j] for j in KV.values()), flush=True)
t0 = time.time(); h.run()
info = h.getInfo(); xs = np.array(h.getSolution().col_value)
print('status', h.modelStatusToString(h.getModelStatus()), 'obj', info.objective_function_value, 'bound', info.mip_dual_bound, f'{time.time()-t0:.0f}s', flush=True)
xv = [[ci, list(p), int(round(xs[j]))] for (ci, p), j in X.items() if round(xs[j])]
yv = [[ci, t, w, int(round(xs[j]))] for (ci, t, w), j in Y.items() if round(xs[j])]
kept = sum(min(v, yA[ci, t, w]) for ci, t, w, v in yv)
chg = [ci for ci in range(len(CL)) if Counter({tuple(p): v for c2, p, v in xv if c2 == ci}) != Counter({p: v for (c2, p), v in xA.items() if c2 == ci})
       or {(t, w): v for c2, t, w, v in yv if c2 == ci} != {(t, w): v for (c2, t, w), v in yA.items() if c2 == ci}]
print('kept flow', kept, 'relocated >=', len(A) - kept, 'changed classes', len(chg), 'dual bound kept', -info.mip_dual_bound, flush=True)
json.dump(dict(x=xv, y=yv, changed=chg, bound=-info.mip_dual_bound), open(OUT, 'w'))
