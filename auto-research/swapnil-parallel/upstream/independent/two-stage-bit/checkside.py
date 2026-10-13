"""Validity check of sidegen.py's lifted side circuit at a given h, with EXACT supports.
Re-runs the lift but tracks for every node the true set of triples it sums (bitmask over the v triples),
and checks: every addition has disjoint supports; a shared node (by sidegen's (core,union) key) has
the same true support as the node it replaces; every node has a common point; every output equals
the exact excluded sum {T : c in T, T cap {a,b} = {}}; outputs cover all 3v (centre, triple) keys.
Returns R = active additions + outputs, with sidegen's own counter for comparison."""
import sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.setrecursionlimit(100000)
from itertools import combinations
import sidegen

def check(h):
    loc = sidegen.Excl(h-1)
    for (a, b), nd in loc.outputs.items():
        assert loc.support[nd] == sum(1 << i for i, p in enumerate(loc.inputs) if a not in p and b not in p)
    trip = list(combinations(range(h), 3)); idx = {t: i for i, t in enumerate(trip)}; v = len(trip)
    pts = lambda t: sum(1 << i for i in t)
    args = [None]*(v+1); sup = [0]+[1 << i for i in range(v)]
    core = [0]+[pts(t) for t in trip]; union = list(core)
    lookup = {}; outputs = {}; shared = 0
    Mp = [sum(1 << i for i, t in enumerate(trip) if p in t) for p in range(h)]
    for c in range(h):
        others = [j for j in range(h) if j != c]; mp = {}
        for nd in sorted(loc.active):
            if loc.args[nd] is None:
                a, b = loc.inputs[nd-1]; mp[nd] = idx[tuple(sorted((c, others[a], others[b])))]+1; continue
            x, y = (mp[z] for z in loc.args[nd])
            assert sup[x] & sup[y] == 0, 'overlapping addition'
            co = core[x] & core[y]; un = union[x] | union[y]; key = (co, un); s = sup[x] | sup[y]
            assert co, 'node without common point'
            if bin(co).count('1') >= 2 and key in lookup:
                assert sup[lookup[key]] == s, 'sharing merged different supports'
                mp[nd] = lookup[key]; shared += 1; continue
            k = len(args); mp[nd] = k; args.append((x, y)); sup.append(s); core.append(co); union.append(un)
            if bin(co).count('1') >= 2: lookup[key] = k
        for (a, b), nd in loc.outputs.items():
            A, B = others[a], others[b]
            want = Mp[c] & ~Mp[A] & ~Mp[B]
            assert sup[mp[nd]] == want, 'wrong output'
            outputs[c, tuple(sorted((c, A, B)))] = mp[nd]
    assert len(outputs) == 3*v
    act = set(); st = list(outputs.values())
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    # every active addition's operands are built before it (topological) and disjoint (checked above)
    assert all(x < n and y < n for n in act if args[n] for x, y in [args[n]])
    adds = sum(args[n] is not None for n in act)
    return adds+len(outputs), adds, len(outputs), shared

if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        mine = check(h); theirs = sidegen.roles(h)
        print(h, mine[0], mine[1], mine[2], 'shared', mine[3], 'sidegen', theirs, 'MATCH' if mine[:3] == theirs else 'DIFF', flush=True)
