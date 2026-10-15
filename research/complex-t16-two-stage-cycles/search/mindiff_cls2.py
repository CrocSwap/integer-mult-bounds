"""Min-diff, class level, stage 2 (per changed class of mindiff_cls1.py): realise the stage-1 class solution on concrete bins, keeping as
many (bin, call, width) placements of A as possible. Unchanged classes keep A. Per class: z[b,t,w] in {0,1} for every
(t, w) the class hosts; at most one helper per bin per call; class flows y[c,t,w] exact; every bin's free value is
one of the class's stage-1 free values, with their counts exact. CP-SAT (hint = A, repair_hint) finds a start, then
HiGHS (warm started) improves it or proves it optimal. Each class result is cached as CACHE/<class>.json.
argv: LIBDIR STAGE1_JSON CACHE_DIR TL_CPSAT TL_HIGHS PART/NPARTS cp|hi   (run cp first, then hi)
      LIBDIR STAGE1_JSON CACHE_DIR OUT_TRIPLES_JSON merge   (union with A's unchanged classes; checks the result)
Needs CPython 3.12; cp: ortools; hi: numpy, scipy, highspy (one thread each)."""
import sys, json, time, os
sys.path.insert(0, sys.argv[1]); import lib
MODE = sys.argv[-1]   # cp: CP-SAT start; hi: HiGHS from the cached start; merge
# ortools and highspy cannot be loaded in one process (clashing HiGHS symbols), hence two passes.
if MODE == 'cp': from ortools.sat.python import cp_model
elif MODE == 'hi':
    import numpy as np, highspy
    from scipy.sparse import coo_matrix
from collections import Counter, defaultdict
A = lib.selroles; s1 = json.load(open(sys.argv[2])); CACHE = sys.argv[3]; os.makedirs(CACHE, exist_ok=True)
if MODE == 'merge':
    m = lib.Model(A); B = lambda z: (z['owner_replica'], z['child'], z['port'])
    cls = {}
    for k in sorted(m.cap): cls.setdefault((m.cap[k], frozenset(m.allowed[k])), []).append(k)
    cid = {k: ci for ci, key in enumerate(cls) for k in cls[key]}
    TA = {(B(z), z['time'], z['width']) for z in A}; ch = set(s1['changed'])
    out = {tr for tr in TA if cid[tr[0]] not in ch}
    for ci in ch: out |= {(tuple(k), t, w) for k, t, w in json.load(open(f'{CACHE}/{ci}.json'))['triples']}
    fill = Counter()
    for k, t, w in out: fill[k] += w
    idle = Counter(m.cap[k] - fill[k] for k in m.cap if m.cap[k] - fill[k])
    prof = Counter()
    for ci, p, v in s1['x']:
        f = list(cls)[ci][0] - sum(c * w for c, w in zip(p, [4, 5, 7, 8, 9]))
        if f: prof[f] += v
    assert len(out) == len(A) and idle == prof and Counter((t, w) for k, t, w in out) == Counter((z['time'], z['width']) for z in A)
    assert max(Counter((m.fam[k], t) for k, t, w in out).values()) == 1 and all(t in m.allowed[k] for k, t, w in out)
    print('merged: idle', dict(sorted(idle.items())), 'kept', len(out & TA), 'relocated', len(A) - len(out & TA))
    json.dump(dict(triples=sorted(out)), open(sys.argv[4], 'w')); sys.exit(0)
TLC = float(sys.argv[4]) if len(sys.argv) > 4 else 60; TLH = float(sys.argv[5]) if len(sys.argv) > 5 else 120
PART, NP = map(int, (sys.argv[6] if len(sys.argv) > 6 else '0/1').split('/'))
m = lib.Model(A); W = [4, 5, 7, 8, 9]
B = lambda z: (z['owner_replica'], z['child'], z['port'])
cls = defaultdict(list)
for k in sorted(m.cap): cls[m.cap[k], frozenset(m.allowed[k])].append(k)
CL = list(cls); cid = {k: ci for ci, key in enumerate(CL) for k in cls[key]}
TA = {(B(z), z['time'], z['width']) for z in A}
fillA = Counter()
for z in A: fillA[B(z)] += z['width']
y = defaultdict(Counter); fv = defaultdict(Counter)
for ci, t, w, v in s1['y']: y[ci][t, w] = v
for ci, p, v in s1['x']: fv[ci][CL[ci][0] - sum(c * w for c, w in zip(p, W))] += v
for ci in s1['changed'][PART::NP]:
    path = f'{CACHE}/{ci}.json'
    if os.path.exists(path): continue
    cap = CL[ci][0]; bins = cls[CL[ci]]; TW = sorted(y[ci]); vals = sorted(fv[ci]); t0 = time.time()
    C = [(b, t, w) for b in bins for (t, w) in TW]
    bytw = defaultdict(list); bybt = defaultdict(list); bybin = defaultdict(list)
    for j, (b, t, w) in enumerate(C): bytw[t, w].append(j); bybt[b, t].append(j); bybin[b].append((j, w))
    nA = sum(1 for tr in TA if cid[tr[0]] == ci)
    if MODE == 'cp':
        md = cp_model.CpModel(); z = [md.NewBoolVar('') for _ in C]; o = {}
        for tw in TW: md.Add(sum(z[j] for j in bytw[tw]) == y[ci][tw])
        for js in bybt.values():
            if len(js) > 1: md.AddAtMostOne(z[j] for j in js)
        for b in bins:
            for v in vals: o[b, v] = md.NewBoolVar(''); md.AddHint(o[b, v], cap - fillA[b] == v)
            md.AddExactlyOne(o[b, v] for v in vals)
            md.Add(sum(w * z[j] for j, w in bybin[b]) + sum(v * o[b, v] for v in vals) == cap)
        for v in vals: md.Add(sum(o[b, v] for b in bins) == fv[ci][v])
        for j, tr in enumerate(C): md.AddHint(z[j], tr in TA)
        md.Maximize(sum(z[j] for j, tr in enumerate(C) if tr in TA))
        sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = TLC; sv.parameters.num_workers = 1; sv.parameters.repair_hint = True
        st = sv.Solve(md); cps = sv.StatusName(st)
        x0 = None
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            x0 = [sv.Value(v) for v in z]; ov = {key: sv.Value(v) for key, v in o.items()}
        cpk = sv.ObjectiveValue() if x0 else None
        sp = path.replace('.json', '.cp.json')
        if st == cp_model.OPTIMAL:
            sol = [C[j] for j in range(len(C)) if x0[j]]
            print('class', ci, 'cap', cap, 'cpsat OPTIMAL A rows', nA, 'kept', int(cpk), f'{time.time()-t0:.0f}s', flush=True)
            json.dump(dict(ci=ci, kept=int(cpk), nA=nA, bound=int(cpk), triples=sol), open(path, 'w'))
        else:
            print('class', ci, 'cap', cap, 'cpsat', cps, cpk, f'{time.time()-t0:.0f}s', flush=True)
            json.dump(dict(x0=x0, ov=[[b, v, x] for (b, v), x in ov.items()] if x0 else None, cpk=cpk), open(sp, 'w'))
        continue
    sp = path.replace('.json', '.cp.json'); d0 = json.load(open(sp)); x0 = d0['x0']; cpk = d0['cpk']; cps = 'cached'
    ov = {(tuple(b), v): x for b, v, x in d0['ov']} if x0 else None
    best = x0; hs = 'skipped'
    if True:
        R, Cc, V, lo, hi = [], [], [], [], []
        def con(e, l, h):
            r = len(lo)
            for j, v in e: R.append(r); Cc.append(j); V.append(v)
            lo.append(l); hi.append(h)
        for tw in TW: con([(j, 1) for j in bytw[tw]], y[ci][tw], y[ci][tw])
        for js in bybt.values():
            if len(js) > 1: con([(j, 1) for j in js], 0, 1)
        nv = len(C); oh = defaultdict(list); oid = {}
        for b in bins:
            ids = list(range(nv, nv + len(vals))); nv += len(vals)
            con(bybin[b] + [(i, v) for i, v in zip(ids, vals)], cap, cap); con([(i, 1) for i in ids], 1, 1)
            for i, v in zip(ids, vals): oh[v].append(i); oid[b, v] = i
        for v in vals: con([(i, 1) for i in oh[v]], fv[ci][v], fv[ci][v])
        c = np.zeros(nv)
        for j, tr in enumerate(C):
            if tr in TA: c[j] = -1
        Mx = coo_matrix((V, (R, Cc)), shape=(len(lo), nv)).tocsc()
        h = highspy.Highs(); h.setOptionValue('output_flag', False); h.setOptionValue('time_limit', TLH); h.setOptionValue('threads', 1)
        lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = len(lo); lp.col_cost_ = c
        lp.col_lower_ = np.zeros(nv); lp.col_upper_ = np.ones(nv)
        lp.row_lower_ = np.array(lo, float); lp.row_upper_ = np.array(hi, float)
        lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        lp.a_matrix_.start_ = Mx.indptr; lp.a_matrix_.index_ = Mx.indices; lp.a_matrix_.value_ = Mx.data.astype(float)
        lp.integrality_ = [highspy.HighsVarType.kInteger] * nv
        h.passModel(lp)
        if x0:
            v0 = np.zeros(nv); v0[:len(C)] = x0
            for key, i in oid.items(): v0[i] = ov[key]
            s0 = highspy.HighsSolution(); s0.col_value = list(v0); s0.value_valid = True; h.setSolution(s0)
        h.run(); hs = h.modelStatusToString(h.getModelStatus()); xs = np.array(h.getSolution().col_value)
        if xs.size == nv and h.getInfo().primal_solution_status == 2 and (x0 is None or -h.getInfo().objective_function_value >= cpk):
            best = [int(v > 0.5) for v in xs[:len(C)]]
        hb = -h.getInfo().mip_dual_bound; hb = round(hb) if abs(hb) < 1e9 else hb
    if best is None:
        print('class', ci, 'cap', cap, 'FAIL', cps, hs, flush=True); continue
    sol = [C[j] for j in range(len(C)) if best[j]]; keep = sum(tr in TA for tr in sol)
    print('class', ci, 'cap', cap, 'cpsat', cps, cpk, 'highs', hs, 'A rows', nA, 'kept', keep, 'bound', hb, f'{time.time()-t0:.0f}s', flush=True)
    json.dump(dict(ci=ci, kept=keep, nA=nA, bound=hb, triples=sol), open(path, 'w'))
