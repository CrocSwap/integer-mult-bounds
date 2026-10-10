"""Combinatorial module model: donor x=y+z hands operand y to a later op t=y+w iff sup(z) subset sup(w) (strict, or equal
support with id(t) > id(x)); order = (|sup| ascending, id). Outputs have no later targets. Returns adds, arcs, debt."""
from collections import defaultdict
def evaluate(circ, want=False):
    nin = circ['input_count']; args = circ['args']; roots = circ['roots']; N = len(args)
    sup = [1 << i for i in range(nin)]
    for x in range(nin, N):
        a, b = args[x]; assert not sup[a] & sup[b]; sup.append(sup[a] | sup[b])
    ops = list(range(nin, N))
    used = set(roots)
    for x in ops:
        for y in args[x]: used.add(y)
    for x in ops: assert x in used, 'unused node %d' % x
    size = [bin(s).count('1') for s in sup]
    order = sorted(ops, key=lambda x: (size[x], x)); pos = {x: i for i, x in enumerate(order)}
    byval = defaultdict(list)
    for x in ops:
        for y in args[x]: byval[y].append(x)
    adj = {}
    for x in ops:
        lst = []
        for y in args[x]:
            for t in byval[y]:
                if t == x or pos[t] <= pos[x]: continue
                if sup[x] & ~sup[t] == 0: lst.append((y, t))
        adj[x] = lst
    mR = {}; mL = {}
    def try_(x, seen):
        for u in adj[x]:
            if u in seen: continue
            seen.add(u)
            if u not in mR or try_(mR[u], seen):
                mR[u] = x; mL[x] = u; return True
        return False
    for x in ops: try_(x, set())
    if want: return len(ops), len(mL), len(ops) - len(mL), dict(adj=adj, match=mL, sup=sup)
    return len(ops), len(mL), len(ops) - len(mL)
