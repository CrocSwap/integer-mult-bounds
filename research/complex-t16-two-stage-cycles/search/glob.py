"""Global repack (session heuristic, no optimality claim). Stage 1: aggregated CP-SAT over bin classes (cap, allowed-set): pattern counts x[c,p], helper flows y[c,t,w],
per-class per-time capacity sum_w y[c,t,w] <= n_c (R4: family windows are disjoint, so one helper per bin per call).
Stage 2: per class, realise patterns on concrete bins with distinct times (greedy + CP-SAT fallback), then relocate roles.
Bins of one (cap, allowed window) class are interchangeable, and inside a physical family the windows are disjoint,
so R4 reduces to at most one helper per bin per call. Stage 1 keeps the per-(class, call) Hall constraints for every
subset of widths (HALL=small: single widths and all widths only) and, with GR=1, Gale-Ryser-style constraints for
several helpers of one width in a bin (they need distinct calls). Stage 1 is a relaxation of the bin-level problem,
so stage 2 can fail on some classes; glob5.py is the stage 2 that was used.
Writes OUT.stage1.json (x = pattern counts, y = flows) and, unless S1ONLY=1, OUT.OWNERS.json.gz.
env: S1ONLY=1 (stage 1 only), HINT=<stage1.json> (warm start), FIX / FREE = JSON lists of class indices to fix to the
start map or to leave free, FIXTO=1 (fix every class not in FIX/FREE to HINT), HALL=small, GR=1.
argv: LIBDIR START OUT TL1 [NW] [SEED]   Needs CPython 3.12 and ortools."""
import sys, math, json, gzip, random, time
sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter, defaultdict
from ortools.sat.python import cp_model
start, out, TL1 = sys.argv[2], sys.argv[3], float(sys.argv[4])
NW = int(sys.argv[5]) if len(sys.argv) > 5 else 1; SEED = int(sys.argv[6]) if len(sys.argv) > 6 else 0
rng = random.Random(SEED)
import os; STAGE1ONLY = os.environ.get('S1ONLY') == '1'
FIX = set(json.loads(os.environ.get('FIX', '[]')))
HINT = os.environ.get('HINT'); FREE = set(json.loads(os.environ.get('FREE', '[]'))); FIXTO = os.environ.get('FIXTO') == '1'
hx0 = Counter(); hy0 = Counter()
if HINT:
    _d = json.load(open(HINT))
    for ci, p, v in _d['x']: hx0[ci, tuple(p)] = v
    for ci, t, w, v in _d['y']: hy0[ci, t, w] = v
roles = lib.read(start); m = lib.Model(roles)
W = [4, 5, 7, 8, 9]; g = lib.g; SC = 10000; gi = lambda f: round(SC * g(f))
classes = defaultdict(list)
for k in m.cap: classes[m.cap[k], frozenset(m.allowed[k])].append(k)
CL = list(classes)
D = Counter((z['time'], z['width']) for z in m.roles)
def pats(cap):
    o = []
    def rec(i, rem, cur):
        if i == len(W): o.append(tuple(cur)); return
        for c in range(rem // W[i] + 1): rec(i + 1, rem - c * W[i], cur + [c])
    rec(0, cap, []); return o
P = {cap: pats(cap) for cap in (8, 16, 32, 48)}
def pat_of(k): c = Counter(m.roles[i]['width'] for i in m.members[k]); return tuple(c[w] for w in W)
md = cp_model.CpModel(); obj = []; ytw = defaultdict(list); X = {}; Y = {}
for ci, key in enumerate(CL):
    cap, al = key; bins = classes[key]; n = len(bins)
    curp = Counter(pat_of(k) for k in bins); cury = Counter((m.roles[i]['time'], m.roles[i]['width']) for k in bins for i in m.members[k])
    cw = defaultdict(list); xs = []
    for p in P[cap]:
        s = sum(c * w for c, w in zip(p, W))
        if max(p) > n: continue
        if sum(p) > len(al): continue
        x = md.NewIntVar(0, n, ''); xs.append(x); X[ci, p] = x; md.AddHint(x, curp[p])
        if gi(cap - s): obj.append(gi(cap - s) * x)
        for c, w in zip(p, W):
            if c: cw[w].append(c * x)
    md.Add(sum(xs) == n)
    pert = defaultdict(list)
    for w in W:
        ys = []
        for t in al:
            if D[t, w]:
                y = md.NewIntVar(0, min(D[t, w], n), ''); ys.append(y); ytw[t, w].append(y); Y[ci, t, w] = y; pert[t].append(y)
                md.AddHint(y, cury[t, w])
        md.Add(sum(ys) == sum(cw[w]))
    import itertools
    loc = [(p, x) for p in P[cap] if (ci, p) in X for x in [X[ci, p]]]
    hit = {}
    for r in range(1, len(W) + 1):
        for Sset in itertools.combinations(W, r):
            hv = md.NewIntVar(0, n, ''); md.AddHint(hv, sum(curp[p] for p, x in loc if any(p[W.index(w)] for w in Sset))); md.Add(hv == sum(x for p, x in loc if any(p[W.index(w)] for w in Sset))); hit[Sset] = hv
    for t in pert:
        ws = [w for w in W if (ci, t, w) in Y]
        for r in range(1, len(ws) + 1):
            for Sset in itertools.combinations(ws, r):
                if os.environ.get('HALL') == 'small' and 1 < r < len(ws): continue
                md.Add(sum(Y[ci, t, w] for w in Sset) <= hit[Sset])
    if os.environ.get('GR') == '1':
        for wi, w in enumerate(W):
            mx = max(p[wi] for p, x in loc)
            tsw = [t for t in al if (ci, t, w) in Y]
            for j in range(2, mx + 1):
                sel = [(p, x) for p, x in loc if p[wi] >= j]
                h = md.NewIntVar(0, n, ''); md.Add(h == sum(x for p, x in sel))
                mts = []
                for t in tsw:
                    mt = md.NewIntVar(0, n, ''); md.Add(mt <= Y[ci, t, w]); md.Add(mt <= h); mts.append(mt)
                md.Add(sum(p[wi] * x for p, x in sel) <= sum(mts))
    if FIXTO and ci not in FIX and ci not in FREE:
        for p, x in loc: md.Add(x == hx0[ci, p])
        for w in W:
            for t in al:
                if (ci, t, w) in Y: md.Add(Y[ci, t, w] == hy0[ci, t, w])
    if ci in FIX:
        for p, x in loc: md.Add(x == curp[p])
        for w in W:
            for t in al:
                if (ci, t, w) in Y: md.Add(Y[ci, t, w] == cury[t, w])
for tw, d in D.items(): md.Add(sum(ytw[tw]) == d)
cur_obj = sum(gi(m.free(k)) for k in m.cap)
if HINT:
    md.ClearHints(); hx = Counter(); hy = Counter(); dh = json.load(open(HINT))
    for ci, p, v in dh['x']: hx[ci, tuple(p)] = v
    for ci, t, w, v in dh['y']: hy[ci, t, w] = v
    for key, v in X.items(): md.AddHint(v, hx[key])
    for key, v in Y.items(): md.AddHint(v, hy[key])
md.Maximize(sum(obj))
sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = TL1; sv.parameters.num_workers = NW; sv.parameters.random_seed = SEED; sv.parameters.repair_hint = True
t0 = time.time(); st = sv.Solve(md)
print('stage1', sv.StatusName(st), 'obj', sv.ObjectiveValue() / SC, 'bound', sv.BestObjectiveBound() / SC, 'current', cur_obj / SC, f'{time.time()-t0:.0f}s', flush=True)
xv = {key: sv.Value(v) for key, v in X.items() if sv.Value(v)}; yv = {key: sv.Value(v) for key, v in Y.items() if sv.Value(v)}
json.dump(dict(x=[[ci, list(p), v] for (ci, p), v in xv.items()], y=[[ci, t, w, v] for (ci, t, w), v in yv.items()]), open(out + '.stage1.json', 'w'))

# Stage 2: realise per class
byT = defaultdict(list)  # (t, w) -> role indices
for i, z in enumerate(m.roles): byT[z['time'], z['width']].append(i)
for v in byT.values(): rng.shuffle(v)
new = [dict(z) for z in m.roles]; fails = 0
def realise(ci):
    cap, al = CL[ci]; bins = classes[CL[ci]]
    plist = [p for (c, p), v in xv.items() if c == ci for _ in range(v)]
    # keep bins with the same current pattern where possible (fewer relocations)
    pool = defaultdict(list)
    for k in bins: pool[pat_of(k)].append(k)
    assign = {}; rest = []
    for p in plist:
        if pool[p]: assign[pool[p].pop()] = p
        else: rest.append(p)
    left = [k for v in pool.values() for k in v]
    for k, p in zip(left, rest): assign[k] = p
    items = [(t, w) for (c, t, w), v in yv.items() if c == ci for _ in range(v)]
    # CP-SAT feasibility: z[b,t,w]
    need = {k: dict(zip(W, assign[k])) for k in bins}
    cnt = Counter(items)
    mdl = cp_model.CpModel(); z = {}
    bw = defaultdict(list); bt = defaultdict(list); tw = defaultdict(list)
    curset = {(k, m.roles[i]['time'], m.roles[i]['width']) for k in bins for i in m.members[k]}
    for k in bins:
        for (t, w) in cnt:
            if need[k][w]:
                v = mdl.NewBoolVar(''); z[k, t, w] = v; bw[k, w].append(v); bt[k, t].append(v); tw[t, w].append(v)
                mdl.AddHint(v, (k, t, w) in curset)
    for k in bins:
        for w in W:
            if need[k][w]: mdl.Add(sum(bw[k, w]) == need[k][w])
    for vs in bt.values():
        if len(vs) > 1: mdl.AddAtMostOne(vs)
    for key, c in cnt.items(): mdl.Add(sum(tw[key]) == c)
    mdl.Maximize(sum(v for key, v in z.items() if key in curset))
    s2 = cp_model.CpSolver(); s2.parameters.max_time_in_seconds = 60; s2.parameters.num_workers = NW
    r = s2.Solve(mdl); print('class', ci, s2.StatusName(r), flush=True)
    if r not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return None
    return [key for key, v in z.items() if s2.Value(v)]
if STAGE1ONLY: sys.exit(0)
place = defaultdict(list)  # (t,w) -> list of bins
for ci in range(len(CL)):
    res = realise(ci)
    if res is None: print('class', ci, CL[ci][0], len(CL[ci][1]), 'INFEASIBLE', flush=True); fails += 1; continue
    for (k, t, w) in res: place[t, w].append(k)
if fails: print('stage2 fails', fails)
if fails and STAGE1ONLY: sys.exit(1)
# relocate: keep roles already in a chosen bin
for tw, ks in place.items():
    hs = byT[tw]; assert len(hs) == len(ks), tw
    rem = Counter(ks); free_h = []
    for i in hs:
        b = m.bin(i)
        if rem[b] > 0: rem[b] -= 1
        else: free_h.append(i)
    tgt = list(rem.elements()); assert len(tgt) == len(free_h)
    for i, k in zip(free_h, tgt): new[i] = lib.relocate(new[i], *k); new[i]['offset'] = 10**6
new = lib.compact(new)
au = lib.audit(new); pr = lib.price(au['profile'])
print('RESULT kappa', pr['kappa_decimal'], 'idle', au['idle'], 'moved', sum(1 for a, b in zip(roles, new) if (a['owner_replica'], a['child'], a['port']) != (b['owner_replica'], b['child'], b['port'])), flush=True)
open(out + '.OWNERS.json.gz', 'wb').write(gzip.compress(json.dumps(new).encode(), mtime=0))
