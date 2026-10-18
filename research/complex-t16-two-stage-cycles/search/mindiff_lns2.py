"""Second-phase min-diff LNS toward the selected map A. Inside the neighbourhood every legal placement (bin, call, width) of the rows it holds is
a candidate (not only A's or F's), each bin's free capacity is any value already present among the neighbourhood's
bins, and the number of bins per free value is preserved (so the global idle profile and kappa are unchanged).
Maximises placements shared with A (HiGHS, warm start = current state).
Each iteration frees a random subset (30/60/90/all) of the differing bins plus up to EXTRA sampled bins (sharing a
physical family with a differing bin, or partly filled). Unlike mindiff_lns.py, fills are not restricted to A's or F's.
argv: LIBDIR START_TRIPLES_JSON OUT_JSON ITERS SEED [EXTRA] [TL]
Needs CPython 3.12, numpy, scipy, highspy. Single thread."""
import sys, json, random, time
sys.path.insert(0, sys.argv[1]); import lib
import numpy as np, highspy
from scipy.sparse import coo_matrix
from collections import Counter, defaultdict
A = lib.selroles
cur = {(tuple(k), t, w) for k, t, w in json.load(open(sys.argv[2]))['triples']}
OUT, ITERS, rng = sys.argv[3], int(sys.argv[4]), random.Random(int(sys.argv[5]))
EXTRA = int(sys.argv[6]) if len(sys.argv) > 6 else 200
TL = float(sys.argv[7]) if len(sys.argv) > 7 else 120
B = lambda z: (z['owner_replica'], z['child'], z['port'])
m = lib.Model(A)
TA = {(B(z), z['time'], z['width']) for z in A}
DA = Counter((z['time'], z['width']) for z in A)


def idle(trs):
    fill = Counter()
    for k, t, w in trs: fill[k] += w
    return Counter(m.cap[k] - fill[k] for k in m.cap if m.cap[k] - fill[k])


target = idle(cur)


def check(trs):
    assert len(trs) == len(A) and idle(trs) == target
    assert Counter((t, w) for k, t, w in trs) == DA
    assert max(Counter((m.fam[k], t) for k, t, w in trs).values()) == 1
    assert all(t in m.allowed[k] for k, t, w in trs)


def solve(trs, N):
    N = set(N)
    inN = {tr for tr in trs if tr[0] in N}
    D = Counter((t, w) for k, t, w in inN)
    wt = defaultdict(set)
    for t, w in D: wt[t].add(w)
    occ_out = {(m.fam[k], t) for k, t, w in trs if k not in N}
    C = sorted((k, t, w) for k in N for t in m.allowed[k] if t in wt and (m.fam[k], t) not in occ_out
               for w in wt[t] if w <= m.cap[k])
    C = sorted(set(C) | inN)
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
    cnt0 = Counter(m.cap[k] - fillc[k] for k in N)
    vs = sorted(v for v in cnt0 if v)
    nv = n; ohs = defaultdict(list); x0x = {}
    for k in N:
        opts = [v for v in vs if v <= m.cap[k]]
        ids = list(range(nv, nv + len(opts))); nv += len(opts)
        con([(j, w) for j, w in bybin[k]] + [(i, v) for i, v in zip(ids, opts)], m.cap[k], m.cap[k])
        if len(ids) > 1: con([(i, 1) for i in ids], 0, 1)
        for i, v in zip(ids, opts): ohs[v].append(i); x0x[i] = (m.cap[k] - fillc[k] == v)
    for v in vs: con([(i, 1) for i in ohs[v]], cnt0[v], cnt0[v])
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
    for i, v in x0x.items(): x0[i] = v
    s0 = highspy.HighsSolution(); s0.col_value = list(x0); s0.value_valid = True
    h.setSolution(s0); h.run()
    xs = np.array(h.getSolution().col_value)
    info = h.getInfo()
    stat = (h.modelStatusToString(h.getModelStatus()), len(N), n, round(-info.mip_dual_bound))
    if xs.size != nv: return None, 0, stat
    new = {C[j] for j in range(n) if xs[j] > 0.5}
    gain = sum(tr in TA for tr in new) - sum(tr in TA for tr in inN)
    return (trs - inN) | new, gain, stat


best = len(TA & cur)
print('start relocated', len(A) - best, 'profile', dict(sorted(target.items())), flush=True)
allbins = sorted(m.cap)
for it in range(ITERS):
    t0 = time.time()
    diffb = {tr[0] for tr in (TA - cur) | (cur - TA)}
    # extras: bins sharing a family with a diff bin, bins with free capacity, random others
    fams = {m.fam[k] for k in diffb}
    fillc = Counter()
    for k, t, w in cur: fillc[k] += w
    pool1 = [k for k in allbins if k not in diffb and m.fam[k] in fams]
    pool2 = [k for k in allbins if k not in diffb and 0 < m.cap[k] - fillc[k] < m.cap[k]]
    ex = set(rng.sample(pool1, min(len(pool1), EXTRA // 2))) | set(rng.sample(pool2, min(len(pool2), EXTRA // 2)))
    sub = set(rng.sample(sorted(diffb), min(len(diffb), rng.choice([30, 60, 90, 400]))))
    new, gain, stat = solve(cur, sub | ex)
    if new is not None and gain > 0:
        check(new); cur = new; best += gain
        json.dump(dict(triples=sorted(cur)), open(OUT, 'w'))
    print(f'it {it} {stat} gain {gain} relocated {len(A)-best} {time.time()-t0:.1f}s', flush=True)
json.dump(dict(triples=sorted(cur)), open(OUT, 'w'))
print('final relocated', len(A) - best)
