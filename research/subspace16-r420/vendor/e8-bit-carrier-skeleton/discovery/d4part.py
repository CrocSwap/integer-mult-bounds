"""Enumerate the D4 sub-root systems of E8 (12-line masks) and find, by CP-SAT exact cover, a partition of the 120 root
lines into 10 of them that consists of 5 orthogonally complementary pairs (B, B-perp).  Writes the 10 masks (hex) as
JSON, in the format of data/skeleton/d4part-pairs.json.  Needs ortools.  Not run by verify.sh.
usage: d4part.py OUT.json [seconds]
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import json
import os
import sys

from ortools.sat.python import cp_model

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code", "skeleton"))
import e8  # noqa: E402

V = e8.V
D4 = set()
O = [set(e8.ORTH[a]) for a in range(V)]
for a in range(V):
    for b in e8.ORTH[a]:
        if b < a:
            continue
        for c in O[a] & O[b]:
            if c < b:
                continue
            for d in O[a] & O[b] & O[c]:
                if d < c:
                    continue
                m, k = e8.closure((1 << a) | (1 << b) | (1 << c) | (1 << d))
                if e8.popcount(m) == 12:
                    D4.add(m)
D4 = sorted(D4)
comp = {m: e8.perp(m) for m in D4}
assert all(e8.popcount(c) == 12 and c in comp for c in comp.values())
idx = {m: i for i, m in enumerate(D4)}
model = cp_model.CpModel()
x = [model.NewBoolVar("x%d" % i) for i in range(len(D4))]
for s in range(V):
    model.Add(sum(x[i] for i, m in enumerate(D4) if m >> s & 1) == 1)
for i, m in enumerate(D4):
    model.Add(x[i] == x[idx[comp[m]]])
sol = cp_model.CpSolver()
sol.parameters.max_time_in_seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 120
sol.parameters.num_workers = 4
r = sol.Solve(model)
print("D4 sub-root systems:", len(D4), "status", sol.StatusName(r))
assert r in (cp_model.OPTIMAL, cp_model.FEASIBLE)
chosen = [D4[i] for i in range(len(D4)) if sol.Value(x[i])]
json.dump([hex(m) for m in chosen], open(sys.argv[1], "w"))
print("partition written:", sys.argv[1])
