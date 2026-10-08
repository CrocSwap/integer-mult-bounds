"""Independent re-implementation of the paired degree-three exclusion producer.

Problem: points P (n of them), inputs x_U for 3-subsets U. For every E subset of
P with |E|<=3 produce D_E = sum of x_U with U disjoint from E, using only
disjoint (cancellation-free) additions. Nodes are interned by exact support.
"""
from itertools import combinations
from collections import defaultdict


class DAG:
    def __init__(self, nleaves):
        self.sup = [0] + [1 << i for i in range(nleaves)]
        self.args = [None] * (nleaves + 1)
        self.idx = {s: i for i, s in enumerate(self.sup)}

    def add(self, a, b):
        if not a: return b
        if not b: return a
        sa, sb = self.sup[a], self.sup[b]
        assert sa & sb == 0
        s = sa | sb
        r = self.idx.get(s)
        if r is None:
            r = len(self.sup); self.idx[s] = r; self.sup.append(s); self.args.append((a, b))
        return r

    def tot(self, xs):
        # balanced tree, first half = floor(len/2)
        xs = list(xs)
        if not xs: return 0
        if len(xs) == 1: return xs[0]
        m = len(xs) // 2
        return self.add(self.tot(xs[:m]), self.tot(xs[m:]))

    def loo(self, xs):
        """total and leave-one-out sums via prefix/suffix chains."""
        n = len(xs); pre = [0]
        for x in xs: pre.append(self.add(pre[-1], x))
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1): suf[i] = self.add(xs[i], suf[i + 1])
        return pre[n], [self.add(pre[i], suf[i + 1]) for i in range(n)]

    def active(self, roots):
        seen = set(); st = list(roots)
        while st:
            x = st.pop()
            if not x or x in seen: continue
            seen.add(x)
            if self.args[x]: st.extend(self.args[x])
        return seen


def pairs_of(pts):
    return [pts[i:i + 2] for i in range(0, len(pts), 2)]


class Producer:
    def __init__(self, n, base=4, order_style='theirs'):
        self.n = n; self.base = base
        self.inputs = list(combinations(range(n), 3))
        self.d = DAG(len(self.inputs))
        w = {t: i + 1 for i, t in enumerate(self.inputs)}
        self.res = self.deg3(list(range(n)), w)
        self.outputs = {E: self.res[E] for E in self.inputs}
        self.total = self.res[()]

    # degree <= 2 weighted exclusion: monomials are vertex weights (1 pt) and
    # edges (2 pts); returns total, exclude-one, exclude-two (pairs).
    def deg2(self, pts, edges, wts):
        d = self.d
        if len(pts) <= 4:
            def f(om):
                om = set(om)
                return d.tot([x for p, x in edges.items() if not (set(p) & om)] +
                             [x for p, x in wts.items() if p not in om])
            return f(()), {a: f((a,)) for a in pts}, {(a, b): f((a, b)) for a, b in combinations(pts, 2)}
        gs = pairs_of(pts); k = len(gs)
        E = lambda a, b: edges[(a, b) if a < b else (b, a)]
        cedge = {(i, j): d.tot([E(a, b) for a in gs[i] for b in gs[j]]) for i, j in combinations(range(k), 2)}
        cw = {i: d.tot([wts[a] for a in g] + [E(a, b) for a, b in combinations(g, 2)]) for i, g in enumerate(gs)}
        T, out1, out2 = self.deg2(list(range(k)), cedge, cw)
        strip = {}; ssum = {}
        for i, g in enumerate(gs):
            oth = [j for j in range(k) if j != i]
            for a in g:
                rest = [u for u in g if u != a]
                carry = d.tot([wts[u] for u in rest])
                vals = [d.tot([E(u, v) for u in rest for v in gs[j]]) for j in oth]
                s, lo = d.loo([carry] + vals)
                ssum[a] = s; strip[a] = dict(zip(oth, lo[1:]))
        single = {a: d.add(out1[i], ssum[a]) for i, g in enumerate(gs) for a in g}
        pair = {}
        for i, g in enumerate(gs):
            for a, b in combinations(g, 2): pair[a, b] = out1[i]
        for i, j in combinations(range(k), 2):
            for a in gs[i]:
                left = d.add(out2[i, j], strip[a][j])
                for b in gs[j]:
                    cross = d.tot([E(u, v) for u in gs[i] if u != a for v in gs[j] if v != b])
                    pair[a, b] = d.add(left, d.add(strip[b][i], cross))
        return T, single, pair

    def deg3(self, pts, w):
        d = self.d
        subs = [s for r in range(4) for s in combinations(pts, r)]
        if len(pts) <= self.base:
            return {s: d.tot([x for t, x in w.items() if not (set(s) & set(t))]) for s in subs}
        gs = pairs_of(pts); k = len(gs)
        gof = {u: i for i, g in enumerate(gs) for u in g}
        cparts = defaultdict(list)
        for t, x in w.items(): cparts[tuple(sorted({gof[u] for u in t}))].append(x)
        cw = {G: d.tot(xs) for G, xs in cparts.items()}
        RC = self.deg3(list(range(k)), cw)
        one = {}
        for u in pts:
            g = gof[u]; oth = [j for j in range(k) if j != g]
            parts = defaultdict(list)
            for t, x in w.items():
                if u not in t: continue
                rest = [a for a in t if a != u]
                if any(gof[a] == g for a in rest): continue
                parts[tuple(sorted({gof[a] for a in rest}))].append(x)
            c = {G: d.tot(xs) for G, xs in parts.items()}
            edges = {G: c.get(G, 0) for G in combinations(oth, 2)}
            wts = {j: c.get((j,), 0) for j in oth}
            T, s1, s2 = self.deg2(oth, edges, wts)
            c0 = c.get((), 0)
            one[u] = {(): d.add(c0, T)}
            one[u].update({(j,): d.add(c0, x) for j, x in s1.items()})
            one[u].update({G: d.add(c0, x) for G, x in s2.items()})
        two = {}
        for u, v in combinations(pts, 2):
            i, j = gof[u], gof[v]
            if i == j: continue
            oth = [q for q in range(k) if q not in (i, j)]
            vals = [d.tot([w.get(tuple(sorted((u, v, a))), 0) for a in gs[q]]) for q in oth]
            T, lo = d.loo([w.get((u, v), 0)] + vals)
            two[u, v] = {(): T}; two[u, v].update({(q,): x for q, x in zip(oth, lo[1:])})
        res = {}
        for Ex in subs:
            Es = set(Ex); G = tuple(sorted({gof[a] for a in Es}))
            surv = [u for i in G for u in gs[i] if u not in Es]
            pc = {(): RC[G]}
            for u in surv:
                pc[(u,)] = one[u][tuple(i for i in G if i != gof[u])]
            for u, v in combinations(surv, 2):
                pc[(u, v)] = two[u, v][tuple(i for i in G if i not in (gof[u], gof[v]))]
            if len(surv) == 3:
                a, b, c = surv
                pc[(a, b, c)] = w.get((a, b, c), 0)
                order = [(), (a,), (b,), (a, b), (c,), (a, c), (b, c), (a, b, c)]
            else:
                order = [s for r in range(len(surv) + 1) for s in combinations(surv, r)]
            res[Ex] = d.tot([pc[s] for s in order])
        return res

    def check(self):
        """Every output support equals the exact disjoint family; all adds disjoint."""
        n = self.n
        for E, node in self.res.items():
            Es = set(E)
            exp = sum(1 << i for i, t in enumerate(self.inputs) if not (Es & set(t)))
            assert self.d.sup[node] == exp, E
        return True


if __name__ == '__main__':
    import sys, time
    for n in map(int, sys.argv[1:]):
        t = time.time(); p = Producer(n); p.check()
        act = p.d.active(p.outputs.values()); a1 = sum(1 for x in act if p.d.args[x])
        act2 = p.d.active(list(p.outputs.values()) + [p.total]); a2 = sum(1 for x in act2 if p.d.args[x])
        print(n, 'outputs-only additions', a1, 'with total', a2, 'time %.1f' % (time.time() - t), flush=True)
