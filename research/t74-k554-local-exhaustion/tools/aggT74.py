"""Aggregate T74 owner-packing relaxation.

Bins: every child window of the T74 parent (PR1319 PLAN.json `windows`: per replica 6 rank-8, 4 rank-16, 4 rank-32 and 4 rank-48
windows) times the 112 data streams, i.e. caps = {8: 49728, 16: 33152, 32: 33152, 48: 33152}. Capacity identity: the total equals
74 replicas x 9 calls x 5376 pending coordinates.

Items: the whole-helper widths of every call. The base word has {4:44, 5:44, 7:38, 8:114, 9:240} (W_res 3734) and the extra word
{4:40, 5:48, 7:38, 8:114, 9:240} (W_res 3738).

A bin is either filled exactly or left completely empty; only rank-48 bins may be left empty, as in the admitted exact fill.
Any partially used bin would leave rank-1 holes, which only lose. The model ignores time windows, owner legality and per-call
distinctness, so it is a relaxation: infeasible here means infeasible for the real owner map.

usage: aggT74.py K, where K calls switch from extra to base."""
import sys
import _paths
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
k = int(sys.argv[1])            # number of calls switched extra -> base (k multiple of 12)
nb, ne = 249 + k, 417 - k
base = {4: 44, 5: 44, 7: 38, 8: 114, 9: 240}; extra = {4: 40, 5: 48, 7: 38, 8: 114, 9: 240}
inv = {w: nb * base[w] + ne * extra[w] for w in W}
empty48 = 22748 + (4 * k) // 48
assert sum(w * n for w, n in inv.items()) + empty48 * 48 == sum(c * n for c, n in caps.items()), (sum(w * n for w, n in inv.items()) + empty48 * 48, sum(c * n for c, n in caps.items()))
m = cp_model.CpModel(); X = {}
for cap, n in caps.items():
    ps = pats(cap)
    for p in ps: X[cap, p] = m.NewIntVar(0, n, '')
    m.Add(sum(X[cap, p] for p in ps) + (empty48 if cap == 48 else 0) == n)
for i, w in enumerate(W): m.Add(sum(X[c, p] * p[i] for (c, p) in X) == inv[w])
s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = 60; s.parameters.num_workers = 2
st = s.Solve(m)
print('k', k, 'base', nb, 'extra', ne, 'empty48', empty48, s.StatusName(st))
