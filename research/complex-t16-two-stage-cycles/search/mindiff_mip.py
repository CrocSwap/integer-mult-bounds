"""Min-diff re-assignment MIP (HiGHS): an owner map with the same idle profile (hence the same kappa) as a target
map F that keeps as many placements of the selected PR1094 map A as possible.

Helpers of one (call, width) class are interchangeable for the owner rules R3-R6 (they read only the call and
the width), so the model works on class placements x[bin, call, width] in {0, 1}, with candidates = placements
used by A or by F (or by START). Constraints: every class keeps its count; at most one helper per physical
family per call (R4); windows/active pair (R3/R5) hold because every candidate is a placement of a legal map.
  fill: every bin keeps F's fill exactly.
  two:  every bin's fill is A's or F's (one 0/1 choice per bin where they differ); the number of bins per idle
        value is linear in those choices and is fixed to F's idle profile.
Objective: maximise placements shared with A. realize.py turns the class solution into owner rows.
argv: LIBDIR F_OWNERS OUT_JSON MODE(fill|two) TIME_LIMIT START_JSON(triples, or -)
Needs CPython 3.12, numpy, scipy, highspy. Single thread."""
import sys, json, time
sys.path.insert(0, sys.argv[1]); import lib
import numpy as np
import highspy
from scipy.sparse import coo_matrix
from collections import Counter, defaultdict
Fp, OUT, MODE, TL, START = sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), sys.argv[6]
assert MODE in ('fill', 'two')
A = lib.selroles; F = lib.read(Fp)
B = lambda z: (z['owner_replica'], z['child'], z['port'])
m = lib.Model(A)
TA = {(B(z), z['time'], z['width']) for z in A}; TF = {(B(z), z['time'], z['width']) for z in F}
st = None if START == '-' else {(tuple(k), t, w) for k, t, w in json.load(open(START))['triples']}
C = sorted(TA | TF | (st or set())); n = len(C)
D = Counter((z['time'], z['width']) for z in A)
fillA, fillF = Counter(), Counter()
for z in A: fillA[B(z)] += z['width']
for z in F: fillF[B(z)] += z['width']
idleA, idleF = lib.idle_of(A), lib.idle_of(F)
rows_, cols, vals, lo, hi = [], [], [], [], []


def con(entries, l, h):
    r = len(lo)
    for j, v in entries: rows_.append(r); cols.append(j); vals.append(v)
    lo.append(l); hi.append(h)


bycls = defaultdict(list); bybin = defaultdict(list); byft = defaultdict(list)
for j, (k, t, w) in enumerate(C):
    assert t in m.allowed[k] and w <= m.cap[k]
    bycls[t, w].append(j); bybin[k].append((j, w)); byft[m.fam[k], t].append(j)
for tw, d in D.items(): con([(j, 1) for j in bycls[tw]], d, d)
for js in byft.values():
    if len(js) > 1: con([(j, 1) for j in js], 0, 1)
nv = n; bin_ids = {}
for k, e in bybin.items():
    if MODE == 'fill' or fillA[k] == fillF[k]:
        con([(j, w) for j, w in e], fillF[k], fillF[k]); continue
    i = nv; nv += 1; bin_ids[k] = i          # 1 = F's fill, 0 = A's fill
    con([(j, w) for j, w in e] + [(i, -(fillF[k] - fillA[k]))], fillA[k], fillA[k])
if MODE == 'two':
    for v in sorted(set(idleF) | set(idleA)):
        ent = [(i, co) for k, i in bin_ids.items()
               if (co := int(m.cap[k] - fillF[k] == v) - int(m.cap[k] - fillA[k] == v))]
        con(ent, idleF[v] - idleA[v], idleF[v] - idleA[v])
c = np.zeros(nv)
for j, t in enumerate(C):
    if t in TA: c[j] = -1
M = coo_matrix((vals, (rows_, cols)), shape=(len(lo), nv)).tocsc()
print('vars', nv, 'cons', len(lo), flush=True)
t0 = time.time()
h = highspy.Highs(); h.setOptionValue('time_limit', TL); h.setOptionValue('mip_rel_gap', 0.0); h.setOptionValue('threads', 1)
lp = highspy.HighsLp(); lp.num_col_ = nv; lp.num_row_ = len(lo)
lp.col_cost_ = c; lp.col_lower_ = np.zeros(nv); lp.col_upper_ = np.ones(nv)
lp.row_lower_ = np.array(lo, float); lp.row_upper_ = np.array(hi, float)
lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
lp.a_matrix_.start_ = M.indptr; lp.a_matrix_.index_ = M.indices; lp.a_matrix_.value_ = M.data.astype(float)
lp.integrality_ = [highspy.HighsVarType.kInteger] * nv
h.passModel(lp)
if st is not None:
    x0 = np.zeros(nv)
    for j, tr in enumerate(C): x0[j] = tr in st
    fill0 = Counter()
    for (k, t, w) in st: fill0[k] += w
    for k, i in bin_ids.items(): x0[i] = fill0[k] == fillF[k]
    s0 = highspy.HighsSolution(); s0.col_value = list(x0); s0.value_valid = True
    print('setSolution', h.setSolution(s0), 'start obj', -float(c @ x0), flush=True)
h.run()
info = h.getInfo(); xs = np.array(h.getSolution().col_value)
print('status', h.modelStatusToString(h.getModelStatus()), 'obj', info.objective_function_value,
      'bound', info.mip_dual_bound, f'{time.time()-t0:.0f}s', flush=True)
sol = [C[j] for j in range(n) if xs[j] > 0.5]
json.dump(dict(mode=MODE, obj=-info.objective_function_value, bound=-info.mip_dual_bound, triples=sol), open(OUT, 'w'))
