"""LNS toward the selected map A under an exact idle-profile constraint (min-diff search).

State: class-level placements (bin, call, width). Helpers of one (call, width) class are interchangeable for the
owner rules R3-R6, so a state fixes the owner map up to that relabelling (realize.py picks the labels).
Each bin's fill is either A's or F's (F = the equivalent-profile target map, e.g. the LNS/CP-SAT best). A step frees
a neighbourhood of bins grown by BFS over the current diff graph; the rows of each class currently in those bins may
move among the candidate placements (A's, F's, current) of those bins. The per-free-value bin counts inside the
neighbourhood are preserved, so the global idle profile (hence kappa) is unchanged. Each sub-MIP (HiGHS, warm
started at the current state) maximises the placements shared with A.
argv: LIBDIR F_OWNERS START_TRIPLES_JSON OUT_JSON ITERS SEED [NBINS] [TL]
Needs CPython 3.12, numpy, scipy, highspy. Single thread."""
import sys, json, random, time
sys.path.insert(0, sys.argv[1]); import lib
import numpy as np, highspy
from scipy.sparse import coo_matrix
from collections import Counter, defaultdict, deque
A = lib.selroles; F = lib.read(sys.argv[2])
cur = {(tuple(k), t, w) for k, t, w in json.load(open(sys.argv[3]))['triples']}
OUT, ITERS, rng = sys.argv[4], int(sys.argv[5]), random.Random(int(sys.argv[6]))
NB = int(sys.argv[7]) if len(sys.argv) > 7 else 300
TL = float(sys.argv[8]) if len(sys.argv) > 8 else 60
B = lambda z: (z['owner_replica'], z['child'], z['port'])
m = lib.Model(A)
TA = {(B(z), z['time'], z['width']) for z in A}
TF = {(B(z), z['time'], z['width']) for z in F}
fillA, fillF = Counter(), Counter()
for z in A: fillA[B(z)] += z['width']
for z in F: fillF[B(z)] += z['width']
candbin = defaultdict(set)
for tr in TA | TF: candbin[tr[0]].add(tr)
DA = Counter((z['time'], z['width']) for z in A)


def idle(trs):
    fill = Counter()
    for k, t, w in trs: fill[k] += w
    out = Counter()
    for k in m.cap:
        f = m.cap[k] - fill[k]
        if f: out[f] += 1
    return out


target = idle(TF)
assert idle(cur) == target, 'start profile differs from F'


def check(trs):
    assert len(trs) == len(A) and idle(trs) == target
    assert Counter((t, w) for k, t, w in trs) == DA
    assert max(Counter((m.fam[k], t) for k, t, w in trs).values()) == 1
    assert all(t in m.allowed[k] for k, t, w in trs)


def graph(trs):
    adj = defaultdict(set); diff = (TA - trs) | (trs - TA)
    bycls = defaultdict(list); byft = defaultdict(set)
    for k, t, w in diff: bycls[t, w].append(k)
    for tr in TA | trs: byft[m.fam[tr[0]], tr[1]].add(tr[0])
    for ks in bycls.values():
        for a in ks:
            adj[a].update(b for b in ks if b != a)
    for k, t, w in diff:
        for k2 in byft[m.fam[k], t]:
            if k2 != k: adj[k].add(k2); adj[k2].add(k)
    return adj, sorted({tr[0] for tr in diff})


def solve(trs, N):
    N = set(N)
    inN = {tr for tr in trs if tr[0] in N}
    D = Counter((t, w) for k, t, w in inN)
    occ_out = {(m.fam[k], t) for k, t, w in trs if k not in N}
    C = set(inN)
    for k in N: C |= candbin[k]
    C = sorted(tr for tr in C if (tr[1], tr[2]) in D and (m.fam[tr[0]], tr[1]) not in occ_out)
    n = len(C); rows, cols, vals, lo, hi = [], [], [], [], []

    def con(e, l, h):
        r = len(lo)
        for j, v in e: rows.append(r); cols.append(j); vals.append(v)
        lo.append(l); hi.append(h)
    bycls = defaultdict(list); bybin = defaultdict(list); byft = defaultdict(list)
    for j, (k, t, w) in enumerate(C):
        bycls[t, w].append(j); bybin[k].append((j, w)); byft[m.fam[k], t].append(j)
    for tw, d in D.items(): con([(j, 1) for j in bycls[tw]], d, d)
    for js in byft.values():
        if len(js) > 1: con([(j, 1) for j in js], 0, 1)
    fillc = Counter()
    for k, t, w in inN: fillc[k] += w
    nv = n; bid = {}
    for k in N:
        if fillA[k] == fillF[k] or fillc[k] not in (fillA[k], fillF[k]):
            con([(j, w) for j, w in bybin[k]], fillc[k], fillc[k]); continue
        i = nv; nv += 1; bid[k] = i
        con([(j, w) for j, w in bybin[k]] + [(i, -(fillF[k] - fillA[k]))], fillA[k], fillA[k])
    vs = set()
    for k in bid: vs |= {m.cap[k] - fillF[k], m.cap[k] - fillA[k]}
    for v in vs - {0}:
        e, rhs = [], 0
        for k, i in bid.items():
            co = int(m.cap[k] - fillF[k] == v) - int(m.cap[k] - fillA[k] == v)
            if co: e.append((i, co)); rhs += co * int(fillc[k] == fillF[k])
        con(e, rhs, rhs)
    c = np.zeros(nv)
    for j, tr in enumerate(C):
        if tr in TA: c[j] = -1
    M = coo_matrix((vals, (rows, cols)), shape=(len(lo), nv)).tocsc()
    h = highspy.Highs(); h.setOptionValue('output_flag', False)
    h.setOptionValue('time_limit', TL); h.setOptionValue('threads', 1)
    lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = len(lo); lp.col_cost_ = c
    lp.col_lower_ = np.zeros(nv); lp.col_upper_ = np.ones(nv)
    lp.row_lower_ = np.array(lo, float); lp.row_upper_ = np.array(hi, float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = M.indptr; lp.a_matrix_.index_ = M.indices; lp.a_matrix_.value_ = M.data.astype(float)
    lp.integrality_ = [highspy.HighsVarType.kInteger] * nv
    h.passModel(lp)
    x0 = np.zeros(nv)
    for j, tr in enumerate(C): x0[j] = tr in inN
    for k, i in bid.items(): x0[i] = fillc[k] == fillF[k]
    s0 = highspy.HighsSolution(); s0.col_value = list(x0); s0.value_valid = True
    h.setSolution(s0); h.run()
    xs = np.array(h.getSolution().col_value)
    if xs.size != nv: return None, 0
    new = {C[j] for j in range(n) if xs[j] > 0.5}
    gain = sum(tr in TA for tr in new) - sum(tr in TA for tr in inN)
    return (trs - inN) | new, gain


best = len(TA & cur)
print('start kept', best, 'relocated', len(A) - best, flush=True)
for it in range(ITERS):
    t0 = time.time()
    adj, dbins = graph(cur)
    if not dbins: break
    seed = rng.choice(dbins); N = [seed]; seen = {seed}; q = deque([seed])
    size = rng.choice([NB // 2, NB, NB * 2])
    while q and len(N) < size:
        a = q.popleft(); nb = sorted(adj[a]); rng.shuffle(nb)
        for b in nb:
            if b not in seen: seen.add(b); N.append(b); q.append(b)
    new, gain = solve(cur, N)
    if new is not None and gain > 0:
        check(new); cur = new; best += gain
        json.dump(dict(triples=sorted(cur)), open(OUT, 'w'))
    print(f'it {it} N {len(N)} gain {gain} kept {best} relocated {len(A)-best} {time.time()-t0:.1f}s', flush=True)
json.dump(dict(triples=sorted(cur)), open(OUT, 'w'))
print('final relocated', len(A) - best)
