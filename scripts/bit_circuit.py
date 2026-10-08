#!/usr/bin/env python3
"""Paired bit side circuit with aligned blocks, shared pair-star sums and totals.

Each common point i gets the weighted paired recursion of the published h=50
circuit on the points [h] minus i, but with blocks {2k,2k+1} fixed globally;
the partner of i is a singleton. At the top level, the leave-one-block-out
sums of a pair-star {i,q} are formed by one prefix/suffix chain over the
blocks avoiding both i and q, shared by groups i and q, plus one
group-specific term. Each group also keeps its total, the sum of all triples
containing i, as the source of its center wire.

Supports are interned canonically: a sum all of whose triples contain two
points is a pair-star (i,j,K); a single triple is an input; any other sum
belongs to one group and is keyed by its pair mask there.
"""
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json

from exclusion_circuit import ExclusionCircuit
from shared_point_circuit import SharedPointCircuit


class AlignedPairedCircuit:
    def __init__(self, h, base=4):
        assert h >= 8 and h % 2 == 0 and h != 9
        self.h = h; self.base = base
        self.pid = {}; self.pts = []
        for a, b in combinations(range(h), 2):
            self.pid[a, b] = self.pid[b, a] = len(self.pts); self.pts.append((a, b))
        self.ptmask = [(1 << a) | (1 << b) for a, b in self.pts]
        self.inputs = list(combinations(range(h), 3))
        self.variables = {t: k+1 for k, t in enumerate(self.inputs)}
        self.args = [None]*(len(self.inputs)+1)
        self.keys = [None]+[('T', t) for t in self.inputs]
        self.home = [None]*(len(self.inputs)+1)
        self.key2node = {('T', t): k+1 for k, t in enumerate(self.inputs)}
        self.outputs = {}
        for i in range(h):
            self.cur = i
            pts = [a for a in range(h) if a != i]
            edges = {(a, b): 1 << self.pid[a, b] for a, b in combinations(pts, 2)}
            total, out = self.top(pts, edges)
            for (c, d), P in out.items():
                self.outputs[i, tuple(sorted((i, c, d)))] = self.node(i, P)
            self.outputs[i, ()] = self.node(i, total)  # center wire source
        self.active = set(); stack = list(self.outputs.values())
        while stack:
            n = stack.pop()
            if n in self.active: continue
            self.active.add(n)
            if self.args[n]: stack.extend(self.args[n])
        self.additions = sum(self.args[n] is not None for n in self.active)

    # ---- canonical supports -------------------------------------------------
    def key(self, i, P):
        core = (1 << self.h)-1; m = P
        while m and core:
            b = m & -m; m ^= b; core &= self.ptmask[b.bit_length()-1]
        if P & (P-1) == 0:
            return ('T', tuple(sorted((i,)+self.pts[P.bit_length()-1])))
        if core:
            j = core.bit_length()-1; K = 0; m = P
            while m:
                b = m & -m; m ^= b; a, c = self.pts[b.bit_length()-1]; K |= 1 << (c if a == j else a)
            return ('S', min(i, j), max(i, j), K)
        return ('G', i, P)

    def node(self, i, P): return self.key2node[self.key(i, P)]

    def add(self, x, y):
        if not x: return y
        if not y: return x
        assert not x & y, 'Cancellation is forbidden'
        i = self.cur; k = self.key(i, x | y)
        if k not in self.key2node:
            self.key2node[k] = len(self.args); self.keys.append(k); self.home.append(i)
            self.args.append((self.node(i, x), self.node(i, y)))
        return x | y

    def total(self, vals):
        vals = [v for v in vals if v]
        if not vals: return 0
        if len(vals) == 1: return vals[0]
        m = len(vals)//2
        return self.add(self.total(vals[:m]), self.total(vals[m:]))

    # ---- the recursion ------------------------------------------------------
    @staticmethod
    def groups(points):
        by = {}
        for p in points: by.setdefault(p//2, []).append(p)
        return [(k, by[k]) for k in sorted(by)]

    def block(self, points, edges, weights):
        """Weighted paired recursion; returns total, singles and pair outputs."""
        E = lambda a, b: edges.get((a, b)) or edges.get((b, a)) or 0
        if len(points) <= self.base:
            tot = lambda omit: self.total([x for q, x in edges.items() if not set(q) & set(omit)] +
                                          [x for q, x in weights.items() if q not in omit])
            return tot(()), {a: tot((a,)) for a in points}, {(a, b): tot((a, b)) for a, b in combinations(points, 2)}
        G = dict(self.groups(points)); lab = list(G)
        coarse = {(I, J): self.total([E(a, b) for a in G[I] for b in G[J]]) for I, J in combinations(lab, 2)}
        wt = {I: self.total([weights.get(a, 0) for a in G[I]]+[E(a, b) for a, b in combinations(G[I], 2)]) for I in lab}
        total, outside, far = self.block(lab, coarse, wt)
        strips = {}; sums = {}
        for I in lab:
            other = [J for J in lab if J != I]
            for a in G[I]:
                carry = self.total([weights.get(u, 0) for u in G[I] if u != a])
                vals = [self.total([E(u, v) for u in G[I] if u != a for v in G[J]]) for J in other]
                st, one = self.loo([carry]+vals)
                strips[a] = dict(zip(other, one[1:])); sums[a] = st
        return total, {a: self.add(outside[I], sums[a]) for I in lab for a in G[I]}, \
            self.combine(G, lab, E, far, outside, strips)

    def loo(self, vals):
        n = len(vals); pre = [0]
        for x in vals: pre.append(self.add(pre[-1], x))
        suf = [0]*(n+1)
        for k in range(n-1, -1, -1): suf[k] = self.add(vals[k], suf[k+1])
        return pre[-1], [self.add(pre[k], suf[k+1]) for k in range(n)]

    def combine(self, G, lab, E, far, outside, strips):
        F = lambda I, J: far.get((I, J)) or far.get((J, I)) or 0
        out = {}
        for I in lab:
            for a, b in combinations(G[I], 2): out[a, b] = outside[I]
        for I, J in combinations(lab, 2):
            for a in G[I]:
                left = self.add(F(I, J), strips[a][J])
                for b in G[J]:
                    cross = self.total([E(u, v) for u in G[I] if u != a for v in G[J] if v != b])
                    out[a, b] = self.add(left, self.add(strips[b][I], cross))
        return out

    def top(self, points, edges):
        """Top level with shared pair-star leave-one-block-out sums."""
        i = self.cur; E = lambda a, b: edges.get((a, b)) or edges.get((b, a)) or 0
        G = dict(self.groups(points)); lab = list(G); own = i//2
        coarse = {(I, J): self.total([E(a, b) for a in G[I] for b in G[J]]) for I, J in combinations(lab, 2)}
        wt = {I: self.total([E(a, b) for a, b in combinations(G[I], 2)]) for I in lab}
        total, outside, far = self.block(lab, coarse, wt)
        strips = {}
        for I in lab:
            for a in G[I]:
                rest = [u for u in G[I] if u != a]
                if not rest: strips[a] = {J: 0 for J in lab if J != I}; continue
                q = rest[0]
                common = [C for C in lab if C not in (I, own)]
                vals = [self.total([E(q, c) for c in G[C]]) for C in common]
                n = len(vals); pre = [0]
                for x in vals: pre.append(self.add(pre[-1], x))
                suf = [0]*(n+1)
                for k in range(n-1, -1, -1): suf[k] = self.add(vals[k], suf[k+1])
                extra = self.total([E(q, c) for c in G[own]]) if own != I else 0
                st = {C: self.add(self.add(pre[k], suf[k+1]), extra) for k, C in enumerate(common)}
                if own != I: st[own] = pre[-1]
                strips[a] = st
        return total, self.combine(G, lab, E, far, outside, strips)

    # ---- supports and checks ------------------------------------------------
    def core(self, n):
        k = self.keys[n]
        if k[0] == 'T': return sum(1 << p for p in k[1])
        if k[0] == 'S': return (1 << k[1]) | (1 << k[2])
        return 1 << k[1]

    @lru_cache(maxsize=None)
    def support_in(self, n, i):
        """Pair mask of node n in group i coordinates (i must be in its core)."""
        k = self.keys[n]
        if k[0] == 'T':
            a, b = (p for p in k[1] if p != i); return 1 << self.pid[a, b]
        if k[0] == 'S':
            j = k[2] if k[1] == i else k[1]; K = k[3]; P = 0
            assert i in (k[1], k[2])
            while K:
                b = K & -K; K ^= b; P |= 1 << self.pid[j, b.bit_length()-1]
            return P
        assert k[1] == i; return k[2]

    def contained(self, a, b):
        common = self.core(a) & self.core(b)
        if not common: return False
        g = (common & -common).bit_length()-1
        return not self.support_in(a, g) & ~self.support_in(b, g)

    def verify(self):
        h = self.h; digest = sha256()
        for n in sorted(self.active):
            if self.args[n]:
                a, b = self.args[n]; g = self.home[n]
                assert a < n and b < n and self.core(n) >> g & 1
                A, B = self.support_in(a, g), self.support_in(b, g)
                assert not A & B and A | B == self.support_in(n, g)
            digest.update(json.dumps((n, self.args[n], list(self.keys[n])),
                                     separators=(',', ':')).encode()+b'\n')
        side = 0
        for (i, t), n in sorted(self.outputs.items()):
            excluded = set(t) if t else {i}
            want = sum(1 << self.pid[a, b] for a, b in combinations([x for x in range(h) if x not in excluded | {i}], 2))
            assert self.support_in(n, i) == want, (i, t)
            side += bool(t)
            digest.update(json.dumps((i, t, n), separators=(',', ':')).encode()+b'\n')
        return dict(h=h, inputs=len(self.inputs), side_outputs=side, centers=len(self.outputs)-side,
                    additions=self.additions, roles=self.additions+len(self.outputs),
                    all_additions_disjoint=True, all_outputs_exact=True, totals_exact=True,
                    every_node_has_common_point=True, circuit_sha256=digest.hexdigest())

    compile = ExclusionCircuit.compile
    verify_frames = SharedPointCircuit.verify_frames


if __name__ == '__main__':
    import sys
    c = AlignedPairedCircuit(int(sys.argv[1]) if len(sys.argv) > 1 else 50)
    print(c.verify()); print(c.verify_frames())
