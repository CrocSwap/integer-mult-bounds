"""Aggregate T74 owner-packing relaxation with a free provider mix.

Variants d = 0..4 demote d of the four E5 entrances 627/629/630/631 to E4 (d=0 is the base word, d=4 the extra word, and W_res = 3734 + d).
The model maximises the number of completely empty rank-48 bins over all mixes of 666 calls, with the same bins as aggT74.py."""
from ortools.sat.python import cp_model
W = [4, 5, 7, 8, 9]
caps = {8: 2 * 24864, 16: 2 * 16576, 32: 2 * 16576, 48: 2 * 16576}
def pats(cap):
    out = []
    def rec(i, rem, cur):
        if i == len(W):
            if rem == 0: out.append(tuple(cur))
            return
        w = W[i]
        for k in range(rem // w + 1):
            cur.append(k); rec(i + 1, rem - k * w, cur); cur.pop()
    rec(0, cap, []); return out
provs = {d: {4: 44 - d, 5: 44 + d, 7: 38, 8: 114, 9: 240} for d in range(0, 5)}   # d demoted helpers (E5->E4), W_res = 3734 + d
m = cp_model.CpModel(); X = {}
n = {d: m.NewIntVar(0, 666, 'n%d' % d) for d in provs}
m.Add(sum(n.values()) == 666)
E = m.NewIntVar(0, 2 * 16576, 'empty48')
for cap, cnt in caps.items():
    ps = pats(cap)
    for p in ps: X[cap, p] = m.NewIntVar(0, cnt, '')
    m.Add(sum(X[cap, p] for p in ps) + (E if cap == 48 else 0) == cnt)
for i, w in enumerate(W):
    m.Add(sum(X[c, p] * p[i] for (c, p) in X) == sum(n[d] * provs[d][w] for d in provs))
m.Maximize(E)
s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 120; s.parameters.num_workers = 2
st = s.Solve(m)
print(s.StatusName(st), 'empty48', s.Value(E), {d: s.Value(n[d]) for d in provs}, 'bound', s.BestObjectiveBound())
