"""Aggregate ceiling (heuristic, not a proof): ignores calls, windows and R4 and packs the helper width counts
into bins by capacity, maximising sum g(free) with g(f) = f ln f (scaled to integers). Coarser than winbound.py.
The surrogate is only approximately linear in kappa, so this is not a certified kappa bound.
Standalone: needs CPython 3.12 and ortools only."""
import math, itertools
from ortools.sat.python import cp_model
W = [4, 5, 7, 8, 9]; N = {9: 240*144, 8: 122*144, 4: 56*144, 5: 32*144, 7: 30*144}
B = {8: 10752, 16: 7168, 32: 7168, 48: 7168}
g = lambda f: f*math.log(f) if f > 1 else 0.0
def pats(cap):
    out = []
    def rec(i, rem, cur):
        if i == len(W): out.append(tuple(cur)); return
        for c in range(rem // W[i] + 1): rec(i+1, rem - c*W[i], cur + [c])
    rec(0, cap, []); return out
m = cp_model.CpModel(); obj = []; use = {w: [] for w in W}
cur_obj = 0
for cap, nb in B.items():
    xs = []
    for p in pats(cap):
        s = sum(c*w for c, w in zip(p, W)); x = m.NewIntVar(0, nb, ''); xs.append(x)
        obj.append(round(1e4*g(cap - s)) * x)
        for c, w in zip(p, W):
            if c: use[w].append(c * x)
    m.Add(sum(xs) == nb)
for w in W: m.Add(sum(use[w]) == N[w])
m.Maximize(sum(obj)); s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 120; s.parameters.num_workers = 1
st = s.Solve(m); print(s.StatusName(st), s.ObjectiveValue()/1e4, s.BestObjectiveBound()/1e4)
cur = {1: 2346, 2: 3, 3: 154, 5: 9, 7: 36, 8: 2, 16: 7, 28: 1, 39: 1, 40: 1, 41: 2, 44: 41, 48: 4829}; print('current', sum(n*g(f) for f, n in cur.items()))
