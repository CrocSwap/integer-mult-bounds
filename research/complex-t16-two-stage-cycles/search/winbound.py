"""Window-aware relaxation (heuristic ceiling, not a proof): bins grouped by (cap, allowed window) class; helpers by
(call, width); pattern counts per class, flows of (call, width) helpers into classes. It drops the per-bin
constraints (one helper per bin per call, which also covers R4) and so over-estimates the surrogate
sum f ln f over idle fragments. The surrogate is only approximately linear in kappa, so the printed CP-SAT bound
is an optimistic ceiling for the surrogate, not a certified kappa bound.
argv: LIBDIR OWNERS [TIME_LIMIT] [WORKERS]   Needs CPython 3.12 and ortools."""
import sys, math; sys.path.insert(0, sys.argv[1]); import lib
from collections import Counter, defaultdict
from ortools.sat.python import cp_model
m = lib.Model(lib.read(sys.argv[2])); TL = float(sys.argv[3]) if len(sys.argv) > 3 else 300
W = [4, 5, 7, 8, 9]; g = lib.g
cls = Counter((m.cap[k], frozenset(m.allowed[k])) for k in m.cap)
print('classes', len(cls))
D = Counter((z['time'], z['width']) for z in m.roles)
def pats(cap):
    out = []
    def rec(i, rem, cur):
        if i == len(W): out.append(tuple(cur)); return
        for c in range(rem // W[i] + 1): rec(i+1, rem - c*W[i], cur + [c])
    rec(0, cap, []); return out
P = {cap: pats(cap) for cap in (8, 16, 32, 48)}
md = cp_model.CpModel(); obj = []; ytw = defaultdict(list); X = {}
for ci, ((cap, al), n) in enumerate(cls.items()):
    xs = []; cw = defaultdict(list)
    for p in P[cap]:
        s = sum(c*w for c, w in zip(p, W)); x = md.NewIntVar(0, n, ''); xs.append(x); X[ci, p] = x
        if g(cap - s): obj.append(round(1e4*g(cap - s)) * x)
        for c, w in zip(p, W):
            if c: cw[w].append(c * x)
    md.Add(sum(xs) == n)
    for w in W:
        ys = []
        for t in al:
            if D[t, w]: y = md.NewIntVar(0, D[t, w] * n, ''); ys.append(y); ytw[t, w].append(y)
        md.Add(sum(ys) == sum(cw[w]))
for tw, d in D.items(): md.Add(sum(ytw[tw]) == d)
md.Maximize(sum(obj)); s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = TL; s.parameters.num_workers = int(sys.argv[4]) if len(sys.argv) > 4 else 2
st = s.Solve(md); print(s.StatusName(st), 'obj', s.ObjectiveValue()/1e4, 'bound', s.BestObjectiveBound()/1e4)
prof = Counter()
for (ci, p), x in X.items():
    v = s.Value(x)
    if v:
        cap = list(cls)[ci][0]; f = cap - sum(c*w for c, w in zip(p, W))
        if f: prof[f] += v
print('profile', dict(sorted(prof.items())))
print('current', sum(g(m.free(k)) for k in m.cap))
