"""Our own paired-bit side generator (re-implemented from the two-stage notes' description:
paired exclusion circuit on h-1 points + cross-common-point sharing). Roles R = additions + outputs.
Self-checks: disjoint supports for every addition, exact pair-exclusion outputs."""
import sys
from itertools import combinations
sys.setrecursionlimit(10000)

class Excl:
    def __init__(self, n):
        self.n = n; self.inputs = list(combinations(range(n), 2))
        self.support = [0]+[1 << i for i in range(len(self.inputs))]
        self.args = [None]*len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}
        self.var = {p: i+1 for i, p in enumerate(self.inputs)}
        _, _, self.outputs = self.pairblock(list(range(n)))
        self.active = set(); st = list(self.outputs.values())
        while st:
            x = st.pop()
            if not x or x in self.active: continue
            self.active.add(x)
            if self.args[x]: st.extend(self.args[x])
    def add(self, a, b):
        if not a: return b
        if not b: return a
        assert not self.support[a] & self.support[b]
        s = self.support[a] | self.support[b]
        if s in self.lookup: return self.lookup[s]
        k = len(self.support); self.lookup[s] = k; self.support.append(s); self.args.append((a, b)); return k
    def total(self, vals):
        if not vals: return 0
        if len(vals) == 1: return vals[0]
        h = len(vals)//2; return self.add(self.total(vals[:h]), self.total(vals[h:]))
    def loo(self, vals):                        # total and leave-one-out via prefix/suffix
        n = len(vals); pre = [0]
        for x in vals: pre.append(self.add(pre[-1], x))
        suf = [0]*(n+1)
        for i in range(n-1, -1, -1): suf[i] = self.add(vals[i], suf[i+1])
        return pre[-1], [self.add(pre[i], suf[i+1]) for i in range(n)]
    def pairblock(self, pts):
        return self.block(pts, {(a, b): self.var[a, b] for a, b in combinations(pts, 2)}, {a: 0 for a in pts})
    def block(self, pts, edges, wts):
        if len(pts) <= 4:
            tot = lambda om: self.total([x for p, x in edges.items() if not set(p) & set(om)]+[x for p, x in wts.items() if p not in om])
            return tot(()), {a: tot((a,)) for a in pts}, {(a, b): tot((a, b)) for a, b in combinations(pts, 2)}
        gr = [pts[i:i+2] for i in range(0, len(pts), 2)]; ng = len(gr)
        e = lambda a, b: edges[tuple(sorted((a, b)))]
        coarse = {(i, j): self.total([e(a, b) for a in gr[i] for b in gr[j]]) for i, j in combinations(range(ng), 2)}
        wt = {i: self.total([wts[a] for a in g]+[e(a, b) for a, b in combinations(g, 2)]) for i, g in enumerate(gr)}
        total, outside, far = self.block(list(range(ng)), coarse, wt)
        strips = {}; sums = {}
        for i, g in enumerate(gr):
            other = [j for j in range(ng) if j != i]
            for a in g:
                carry = self.total([wts[u] for u in g if u != a])
                vals = [self.total([e(u, w) for u in g if u != a for w in gr[j]]) for j in other]
                st, one = self.loo([carry]+vals)
                strips[a] = dict(zip(other, one[1:])); sums[a] = st
        out = {}
        single = {a: self.add(outside[i], sums[a]) for i, g in enumerate(gr) for a in g}   # omit one vertex
        for i, g in enumerate(gr):
            for a, b in combinations(g, 2): out[a, b] = outside[i]
        for i, j in combinations(range(ng), 2):
            for a in gr[i]:
                left = self.add(far[i, j], strips[a][j])
                for b in gr[j]:
                    cross = self.total([e(u, w) for u in gr[i] if u != a for w in gr[j] if w != b])
                    out[a, b] = self.add(left, self.add(strips[b][i], cross))
        return total, single, out

def roles(h):
    loc = Excl(h-1)
    for (a, b), nd in loc.outputs.items():   # exact pair-exclusion check
        assert loc.support[nd] == sum(1 << i for i, p in enumerate(loc.inputs) if a not in p and b not in p)
    for nd in loc.active:
        if loc.args[nd]:
            x, y = loc.args[nd]; assert not loc.support[x] & loc.support[y]
    inputs = list(combinations(range(h), 3)); var = {t: i+1 for i, t in enumerate(inputs)}
    args = [None]*(len(inputs)+1); core = [0]+[sum(1 << i for i in t) for t in inputs]; union = list(core)
    points = [[j for j in range(h) if j != i] for i in range(h)]
    lookup = {}; outputs = {}
    for c in range(h):
        mp = {}
        for nd in sorted(loc.active):
            if loc.args[nd] is None:
                a, b = loc.inputs[nd-1]; mp[nd] = var[tuple(sorted((c, points[c][a], points[c][b])))]; continue
            a, b = (mp[x] for x in loc.args[nd])
            co = core[a] & core[b]; un = union[a] | union[b]; key = (co, un)
            if bin(co).count("1") >= 2 and key in lookup: mp[nd] = lookup[key]; continue
            k = len(args); mp[nd] = k; args.append((a, b)); core.append(co); union.append(un)
            if bin(co).count("1") >= 2: lookup[key] = k
        for pair, nd in loc.outputs.items():
            outputs[c, tuple(sorted((c, *(points[c][x] for x in pair))))] = mp[nd]
    act = set(); st = list(outputs.values())
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    adds = sum(args[n] is not None for n in act)
    return adds+len(outputs), adds, len(outputs)

if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        print(h, roles(h), flush=True)
