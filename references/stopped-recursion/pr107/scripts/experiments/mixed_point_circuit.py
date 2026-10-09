"""Structured mixed-point scalar circuits; no full-size frame certificate.

Plans use direct sums, vector kernels, transposed kernels, paired exclusion,
and optionally common-point decomposition. Counts select between block splits
and tensor evaluation orders; exact support interning supplies further sharing.
"""
from collections import defaultdict
from functools import cache
import heapq
from itertools import combinations
from math import comb
from exclusion_circuit import ExclusionCircuit
from paired_exclusion_circuit import PairedExclusionCircuit

class Circuit:
    add = ExclusionCircuit.add
    total = ExclusionCircuit.total

    def __init__(self, n, k, l, r):
        self.n = n
        self.k = k
        self.l = l
        self.r = r
        self.inputs = list(combinations(range(n), k))
        self.targets = list(combinations(range(n), l))
        self.variables = {p: i + 1 for i, p in enumerate(self.inputs)}
        self.support = [0] + [1 << i for i in range(len(self.inputs))]
        self.args = [None] * len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}

    def finish(self, outputs):
        self.outputs = outputs
        active = set()
        stack = list(outputs)
        while stack:
            x = stack.pop()
            if not x or x in active:
                continue
            active.add(x)
            if self.args[x]:
                stack.extend(self.args[x])
        self.active = sorted(active)
        self.additions = sum((self.args[x] is not None for x in active))
        return self

    def apply(self, t, inputs):
        nodes = [0] * len(t.args)
        nodes[1:len(inputs) + 1] = inputs
        for node in t.active:
            if t.args[node]:
                a, b = t.args[node]
                nodes[node] = self.add(nodes[a], nodes[b])
        return [nodes[node] for node in t.outputs]

    def verify(self):
        for target, node in zip(self.targets, self.outputs):
            mask = sum((1 << i for i, source in enumerate(self.inputs) if len(set(source) & set(target)) == self.r))
            assert self.support[node] == mask
        return True

@cache
def vector(n, l, r):
    c = Circuit(n, 1, l, r)
    if r:

        def output(target):
            if len(target) < 3:
                return c.total([c.variables[a,] for a in target])
            side = [a for a in target if a < n // 2]
            if len(side) < 2:
                side = [a for a in target if a >= n // 2]
            pair = side[:2]
            last = next((a for a in target if a not in pair))
            return c.add(c.add(c.variables[pair[0],], c.variables[pair[1],]), c.variables[last,])
        return c.finish([output(t) for t in c.targets])

    def avoid(points, excluded):
        if not points:
            return 0
        if not excluded:
            return c.total([c.variables[a,] for a in points])
        if len(points) == 1:
            return 0
        mid = len(points) // 2
        left, right = (points[:mid], points[mid:])
        return c.add(avoid(left, excluded.intersection(left)), avoid(right, excluded.intersection(right)))
    return c.finish([avoid(list(range(n)), set(t)) for t in c.targets])

def transpose(t):
    c = Circuit(t.n, t.l, t.k, t.r)
    users = {node: [] for node in t.active}
    for node in t.active:
        if t.args[node]:
            for child in t.args[node]:
                users[child].append(('node', node))
    for i, node in enumerate(t.outputs):
        users[node].append(('input', i + 1))
    image = {}
    for node in reversed(t.active):
        image[node] = c.total([value if typ == 'input' else image[value] for typ, value in users[node]])
    return c.finish([image[i] for i in range(1, len(t.inputs) + 1)])

@cache
def kernel(n, k, l, r):
    if k == 1:
        return vector(n, l, r)
    if l == 1:
        return transpose(vector(n, k, r))
    if k == l == 2 and r == 0:
        t = PairedExclusionCircuit(n)
        c = Circuit(n, k, l, r)
        c.support = t.support
        c.args = t.args
        c.lookup = t.lookup
        return c.finish([t.outputs[targ] for targ in c.targets])
    return None

def feasible(n, k, l, r):
    return 0 <= k <= n and 0 <= l <= n and (0 <= r <= min(k, l)) and (k + l - r <= n)

@cache
def plan(n, k, l, r, common=True):
    p, q = (comb(n, k), comb(n, l))
    degree = comb(l, r) * comb(n - l, k - r)
    if degree == 1:
        return (0, 'single', 0)
    if not l or not k:
        return (q * (p - 1), 'direct', 0)
    winner = (q * (degree - 1), 'direct', 0)
    t = kernel(n, k, l, r)
    if t and t.additions < winner[0]:
        winner = (t.additions, 'kernel', 0)
    if r == 1 and common:
        common_cost = n * plan(n - 1, k - 1, l - 1, 0, common)[0] + (l - 1) * q
        if common_cost < winner[0]:
            winner = (common_cost, 'common', 0)
    for nl in range(1, n):
        nr = n - nl
        cost = 0
        for b in range(max(0, l - nr), min(l, nl) + 1):
            cases = 0
            for a in range(max(0, k - nr), min(k, nl) + 1):
                for u in range(r + 1):
                    if not feasible(nl, a, b, u) or not feasible(nr, k - a, l - b, r - u):
                        continue
                    cases += 1
                    lc = plan(nl, a, b, u, common)[0]
                    rc = plan(nr, k - a, l - b, r - u, common)[0]
                    cost += min(comb(nr, k - a) * lc + comb(nl, b) * rc, comb(nr, l - b) * lc + comb(nl, a) * rc)
            cost += comb(nl, b) * comb(nr, l - b) * (cases - 1)
        if cost < winner[0]:
            winner = (cost, 'split', nl)
    return winner

@cache
def build(n, k, l, r, common=True):
    cost, kind, nl = plan(n, k, l, r, common)
    if kind == 'kernel':
        return kernel(n, k, l, r)
    c = Circuit(n, k, l, r)
    if kind in ('direct', 'single'):
        return c.finish([c.total([i + 1 for i, s in enumerate(c.inputs) if len(set(s) & set(t)) == r]) for t in c.targets])
    if kind == 'common':
        child = build(n - 1, k - 1, l - 1, 0, common)
        pieces = {t: [] for t in c.targets}
        for point in range(n):
            pts = [a for a in range(n) if a != point]
            ins = [c.variables[tuple(sorted((point, *(pts[a] for a in source))))] for source in child.inputs]
            outs = c.apply(child, ins)
            for target, node in zip(child.targets, outs):
                pieces[tuple(sorted((point, *(pts[a] for a in target))))].append(node)
        return c.finish([c.total(pieces[t]) for t in c.targets])
    nr = n - nl
    pieces = {t: [] for t in c.targets}
    for b in range(max(0, l - nr), min(l, nl) + 1):
        TL = list(combinations(range(nl), b))
        TR = list(combinations(range(nr), l - b))
        for a in range(max(0, k - nr), min(k, nl) + 1):
            IL = list(combinations(range(nl), a))
            IR = list(combinations(range(nr), k - a))
            for u in range(r + 1):
                if not feasible(nl, a, b, u) or not feasible(nr, k - a, l - b, r - u):
                    continue
                left = build(nl, a, b, u, common)
                right = build(nr, k - a, l - b, r - u, common)
                mat = [[c.variables[s + tuple((nl + x for x in t))] for t in IR] for s in IL]
                lc = len(IR) * left.additions + len(TL) * right.additions
                rc = len(TR) * left.additions + len(IL) * right.additions
                if lc <= rc:
                    temp = list(zip(*[c.apply(left, list(col)) for col in zip(*mat)]))
                    out = [c.apply(right, list(row)) for row in temp]
                else:
                    temp = [c.apply(right, row) for row in mat]
                    out = list(zip(*[c.apply(left, list(col)) for col in zip(*temp)]))
                for i, s in enumerate(TL):
                    for j, t in enumerate(TR):
                        pieces[s + tuple((nl + x for x in t))].append(out[i][j])
    c.finish([c.total(pieces[t]) for t in c.targets])
    assert c.additions <= cost, (n, k, l, r, c.additions, cost)
    return c


def factored_transpose(t):
    users = {node: [] for node in t.active}
    for node in t.active:
        if t.args[node]:
            for child in t.args[node]:
                users[child].append(node)
    for i, node in enumerate(t.outputs):
        users[node].append(-i - 1)
    expr = {}
    alias = {}
    for node in reversed(t.active):
        terms = [alias.get(x, x) if x > 0 else x for x in users[node]]
        assert len(set(terms)) == len(terms)
        if len(terms) == 1:
            alias[node] = terms[0]
        else:
            expr[node] = set(terms)
            alias[node] = node
    need = [alias[i] for i in range(1, len(t.inputs) + 1)]
    occurrence = defaultdict(set)
    for key, terms in expr.items():
        for pair in combinations(sorted(terms), 2):
            occurrence[pair].add(key)
    heap = [(-len(uses), pair) for pair, uses in occurrence.items() if len(uses) >= 2]
    heapq.heapify(heap)
    helpers = {}
    nexttag = len(t.args)
    steps = 0
    while heap:
        neg, pair = heapq.heappop(heap)
        uses = occurrence.get(pair, set())
        count = len(uses)
        if count < 2:
            continue
        if count != -neg:
            heapq.heappush(heap, (-count, pair))
            continue
        a, b = pair
        tag = nexttag
        nexttag += 1
        helpers[tag] = pair
        touched = set()
        for key in sorted(uses):
            terms = expr[key]
            assert a in terms and b in terms
            others = terms - {a, b}
            for x in others:
                for v in (a, b):
                    old = tuple(sorted((x, v)))
                    occurrence[old].remove(key)
                    if not occurrence[old]:
                        del occurrence[old]
                new = tuple(sorted((x, tag)))
                occurrence[new].add(key)
                touched.add(new)
            terms.difference_update((a, b))
            terms.add(tag)
        del occurrence[pair]
        for new in sorted(touched):
            if len(occurrence[new]) >= 2:
                heapq.heappush(heap, (-len(occurrence[new]), new))
        steps += 1
    c = Circuit(t.n, t.l, t.k, t.r)
    image = {}
    for target in need:
        stack = [(target, False)]
        while stack:
            tag, ready = stack.pop()
            if tag in image:
                continue
            if tag < 0:
                image[tag] = -tag
                continue
            if ready:
                children = helpers[tag] if tag in helpers else sorted(expr[tag])
                image[tag] = c.total([image[child] for child in children])
                continue
            stack.append((tag, True))
            children = helpers[tag] if tag in helpers else sorted(expr[tag])
            stack.extend(((child, False) for child in children if child not in image))
    c.finish([image[tag] for tag in need])
    return (c, dict(factors=steps, expressions=len(expr)))
