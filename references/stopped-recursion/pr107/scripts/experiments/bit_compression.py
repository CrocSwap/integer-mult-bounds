"""Bounded cancellation-free alternatives for the existing common-point motif.

Exploratory circuits only. No stronger multiplication witness is claimed.
Every sum has disjoint formal supports, so the retained common-point
source-span/complement-frame argument applies without new decreasing edges.
"""
from itertools import combinations
from exclusion_circuit import ExclusionCircuit

class Blocked(ExclusionCircuit):
    """Weighted block recursion, with bounded scheduling choices."""

    def __init__(self, n, k=2, leaf=4, vec='prefix', order=0, assoc=0):
        assert k >= 2 and leaf >= 3
        assert vec in ("prefix", "tree", "paired")
        assert order in (0, 1, 2) and assoc in (0, 1, 2, 3)
        self.k = k
        self.leaf = leaf
        self.vec = vec
        self.order = order
        self.assoc = assoc
        super().__init__(n)

    def vector(self, values, two=True):
        if two or self.vec == 'prefix':
            return super().vector(values, two)
        if self.vec == 'tree':

            def rec(v, carry):
                if len(v) == 1:
                    return [carry]
                m = len(v) // 2
                return rec(v[:m], self.add(carry, self.total(v[m:]))) + rec(v[m:], self.add(carry, self.total(v[:m])))
            return (self.total(values), rec(values, 0), {})
        groups = [values[i:i + 2] for i in range(0, len(values), 2)]
        totals = [self.total(g) for g in groups]
        _, outside, _ = super().vector(totals, False)
        return (self.total(totals), [self.add(outside[i], self.total(g[:j] + g[j + 1:])) for i, g in enumerate(groups) for j in range(len(g))], {})

    def pair(self, points):
        return self.block(points, {p: self.variables[p] for p in combinations(points, 2)}, {a: 0 for a in points})

    def block(self, points, edges, weights):
        if len(points) <= self.leaf:
            total = lambda omit: self.total([x for p, x in edges.items() if not set(p) & set(omit)] + [x for p, x in weights.items() if p not in omit])
            return (total(()), {a: total((a,)) for a in points}, {(a, b): total((a, b)) for a, b in combinations(points, 2)})
        ps = list(points)
        if self.order == 1:
            ps = ps[::2] + ps[1::2]
        if self.order == 2:
            ps = [x for pair in zip(ps[:len(ps) // 2], reversed(ps[len(ps) // 2:])) for x in pair] + ([ps[len(ps) // 2]] if len(ps) % 2 else [])
        groups = [ps[i:i + self.k] for i in range(0, len(ps), self.k)]
        ng = len(groups)
        e = lambda a, b: edges[tuple(sorted((a, b)))]
        coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]]) for i, j in combinations(range(ng), 2)}
        wt = {i: self.total([weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)]) for i, g in enumerate(groups)}
        total, outside, far = self.block(list(range(ng)), coarse, wt)
        strips = {}
        sums = {}
        for i, g in enumerate(groups):
            other = [j for j in range(ng) if j != i]
            vals = {a: [] for a in g}
            for j in other:
                rows = [self.total([e(a, b) for b in groups[j]]) for a in g]
                _, leave, _ = self.vector(rows, False)
                for a, value in zip(g, leave):
                    vals[a].append(value)
            for a in g:
                carry = self.total([weights[u] for u in g if u != a] + [e(u, v) for u, v in combinations(g, 2) if a not in (u, v)])
                st, one, _ = self.vector([carry] + vals[a], False)
                strips[a] = {j: z for j, z in zip(other, one[1:])}
                sums[a] = st
        out = {}
        single = {a: self.add(outside[i], sums[a]) for i, g in enumerate(groups) for a in g}
        for i, g in enumerate(groups):
            for a, b in combinations(g, 2):
                inside = self.total([weights[u] for u in g if u not in (a, b)] + [e(u, v) for u, v in combinations(g, 2) if not {u, v} & {a, b}])
                cross = self.total([e(u, v) for u in g if u not in (a, b) for v in points if v not in g])
                out[tuple(sorted((a, b)))] = self.total([outside[i], inside, cross])
        for i, j in combinations(range(ng), 2):
            matrix = [[e(a, b) for b in groups[j]] for a in groups[i]]
            rows = [self.vector(row, False)[1] for row in matrix]
            crosses = list(zip(*[self.vector(list(col), False)[1] for col in zip(*rows)]))
            for ia, a in enumerate(groups[i]):
                for jb, b in enumerate(groups[j]):
                    A, B, C, D = (far[i, j], strips[a][j], strips[b][i], crosses[ia][jb])
                    if self.assoc == 0:
                        z = self.add(self.add(A, B), self.add(C, D))
                    elif self.assoc == 1:
                        z = self.add(self.add(self.add(A, B), C), D)
                    elif self.assoc == 2:
                        z = self.add(A, self.add(B, self.add(C, D)))
                    elif self.assoc == 3:
                        z = self.add(self.add(A, D), self.add(B, C))
                    out[tuple(sorted((a, b)))] = z
        return (total, single, out)

class FilterTree(ExclusionCircuit):
    """Filter one source-sum tree separately for every excluded pair."""

    def __init__(self, n, kind='vertex', leaf=1):
        assert kind in ("balanced", "vertex")
        self.kind = kind
        self.leaf = leaf
        super().__init__(n)

    def pair(self, points):

        def tree(ids):
            if len(ids) == 1:
                return (self.support[ids[0]], ids[0], None)
            if self.kind == 'balanced':
                m = len(ids) // 2
                left, right = (ids[:m], ids[m:])
            else:
                union = sorted(set((x for i in ids for x in self.inputs[i - 1])))
                mid = len(union) // 2
                cut = set(union[:mid])
                groups = [[], [], []]
                for i in ids:
                    groups[sum((x in cut for x in self.inputs[i - 1]))].append(i)
                groups = [g for g in groups if g]
                if len(groups) == 1:
                    m = len(ids) // 2
                    left, right = (ids[:m], ids[m:])
                else:
                    left = groups[0]
                    right = sum(groups[1:], [])
            l, r = (tree(left), tree(right))
            node = self.add(l[1], r[1])
            return (self.support[node], node, (l, r))
        root = tree(list(range(1, len(self.inputs) + 1)))

        def select(t, allow):
            mask = t[0] & allow
            if not mask:
                return 0
            if mask == t[0]:
                return t[1]
            if mask in self.lookup:
                return self.lookup[mask]
            left, right = t[2]
            return self.add(select(left, allow), select(right, allow))
        outs = {p: select(root, sum((1 << i for i, q in enumerate(self.inputs) if not set(q) & set(p)))) for p in self.inputs}
        return (0, {}, outs)
