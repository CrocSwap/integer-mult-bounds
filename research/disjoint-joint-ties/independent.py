#!/usr/bin/env python3
"""Independent finite disjoint-triple contraction reconstruction.

Standard library only; no repository or primary experiment imports.  The
bottom-up arithmetic recurrence is evaluated separately, and tuple-indexed
factor tables are contracted through a support-keyed interner.  The underlying
disjointness identity and balanced binary summation convention come from
Douglas R. Colkitt; Curtis Dransfield's PR863 introduced tied root contractions.
Apache-2.0. Substantial AI assistance: OpenAI Codex.
"""
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from math import comb
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def recurrence(limit):
    """Compute all rank-at-most-three plans bottom-up, keeping first ties."""
    table = {}
    for n in range(limit + 1):
        for a in range(min(3, n) + 1):
            for b in range(min(3, n) + 1):
                if a + b > n:
                    table[n, a, b] = (0, "empty")
                    continue
                if a == 0:
                    table[n, a, b] = (0, "copy")
                    continue
                if b == 0:
                    table[n, a, b] = (comb(n, a) - 1, "sum")
                    continue
                best = (comb(n, b) * (comb(n - b, a) - 1), "rows")
                for left in range(1, n // 2 + 1):
                    right = n - left
                    cost = 0
                    for j in range(max(0, b - right), min(left, b) + 1):
                        terms = 0
                        for i in range(max(0, a - right), min(left, a) + 1):
                            if i + j > left or a - i + b - j > right:
                                continue
                            lc = table[left, i, j][0]
                            rc = table[right, a - i, b - j][0]
                            cost += min(comb(right, a - i) * lc + comb(left, j) * rc,
                                        comb(left, i) * rc + comb(right, b - j) * lc)
                            terms += 1
                        if terms:
                            cost += comb(left, j) * comb(right, b - j) * (terms - 1)
                    if cost < best[0]:
                        best = (cost, left)
                table[n, a, b] = best
    return table


@lru_cache(maxsize=None)
def choose(points, rank):
    return tuple(combinations(points, rank))


class SupportInterner:
    def __init__(self, size):
        self.supports = [0] + [1 << i for i in range(size)]
        self.children = [None] * (size + 1)
        self.by_support = {s: i for i, s in enumerate(self.supports)}

    def join(self, x, y):
        if x == 0:
            return y
        if y == 0:
            return x
        sx, sy = self.supports[x], self.supports[y]
        require(sx & sy == 0, "independent interner: overlapping inputs")
        support = sx | sy
        if support in self.by_support:
            return self.by_support[support]
        node = len(self.supports)
        self.by_support[support] = node
        self.supports.append(support)
        self.children.append((x, y))
        return node

    def reduce(self, nodes):
        if not nodes:
            return 0
        if len(nodes) == 1:
            return nodes[0]
        cut = len(nodes) // 2
        return self.join(self.reduce(nodes[:cut]), self.reduce(nodes[cut:]))


def _reconstruct(order, flips, h, root_split, plans):
    require(type(h) is int and h >= 8 and h % 2 == 0, "even h >= 8 required")
    require(type(root_split) is int and 1 <= root_split <= h // 2,
            "invalid root split")
    order = tuple(order)
    require(len(order) == 4 and all(type(j) is int for j in order)
            and set(order) == set(range(4)), "invalid root channel order")
    flips = tuple(tuple(f) for f in flips)
    require(len(set(flips)) == len(flips), "duplicate tied channel")
    tied = set()
    for i in range(4):
        for j in range(4):
            l, r = root_split, h - root_split
            if i > l or j > l or 3 - i > r or 3 - j > r:
                continue
            if i + j > l or 6 - i - j > r:
                continue
            lc, rc = plans[l, i, j][0], plans[r, 3 - i, 3 - j][0]
            if comb(r, 3 - i) * lc + comb(l, j) * rc == \
                    comb(l, i) * rc + comb(r, 3 - j) * lc:
                tied.add((i, j))
    require(all(f in tied for f in flips), "invalid tied channel")
    flipped = set(flips)
    inputs = choose(tuple(range(h)), 3)
    interner = SupportInterner(len(inputs))

    def apply(points, a, b, values):
        n = len(points)
        method = root_split if n == h else plans[n, a, b][1]
        targets = choose(points, b)
        if method == "empty":
            return {target: 0 for target in targets}
        if method == "copy":
            return {target: values[()] for target in targets}
        if method == "sum":
            return {(): interner.reduce(list(values.values()))}
        if method == "rows":
            return {target: interner.reduce([values[source] for source in choose(points, a)
                                             if set(source).isdisjoint(target)])
                    for target in targets}
        left, right = points[:method], points[method:]
        l, r = len(left), len(right)
        terms = {target: [] for target in targets}
        js = order if n == h else range(max(0, b - r), min(l, b) + 1)
        for j in js:
            if not max(0, b - r) <= j <= min(l, b):
                continue
            for i in range(max(0, a - r), min(l, a) + 1):
                if i + j > l or a - i + b - j > r:
                    continue
                lc = plans[l, i, j][0]
                rc = plans[r, a - i, b - j][0]
                left_first = comb(r, a - i) * lc + comb(l, j) * rc <= \
                    comb(l, i) * rc + comb(r, b - j) * lc
                if n == h and (i, j) in flipped:
                    left_first = not left_first
                # One generic two-factor contraction handles both orientations.
                if left_first:
                    first, second = left, right
                    source_rank, target_rank = i, j
                else:
                    first, second = right, left
                    source_rank, target_rank = a - i, b - j
                other_source, other_target = a - source_rank, b - target_rank
                middle = {}
                for second_source in choose(second, other_source):
                    row = {first_source: values[tuple(sorted(first_source + second_source))]
                           for first_source in choose(first, source_rank)}
                    middle[second_source] = apply(first, source_rank, target_rank, row)
                for first_target in choose(first, target_rank):
                    row = {second_source: middle_row[first_target]
                           for second_source, middle_row in middle.items()}
                    results = apply(second, other_source, other_target, row)
                    for second_target, node in results.items():
                        terms[tuple(sorted(first_target + second_target))].append(node)
        return {target: interner.reduce(nodes) for target, nodes in terms.items()}

    outputs = apply(tuple(range(h)), 3, 3,
                    {source: i + 1 for i, source in enumerate(inputs)})
    require(set(outputs) == set(inputs), "independent output domain mismatch")
    for target, node in outputs.items():
        expected = sum(1 << i for i, source in enumerate(inputs)
                       if set(source).isdisjoint(target))
        require(interner.supports[node] == expected, "independent coefficient mismatch")
    live = set()
    pending = list(outputs.values())
    while pending:
        node = pending.pop()
        if node == 0 or node in live:
            continue
        live.add(node)
        children = interner.children[node]
        if children:
            x, y = children
            require(0 < x < node and 0 < y < node, "independent cyclic node")
            require(interner.supports[x] & interner.supports[y] == 0,
                    "independent overlapping node")
            require(interner.supports[node] == interner.supports[x] | interner.supports[y],
                    "independent wrong node support")
            pending.extend(children)
        else:
            require(node <= len(inputs) and interner.supports[node] == 1 << (node - 1),
                    "independent malformed input")
    nodes = [[node, interner.children[node], str(interner.supports[node])]
             for node in sorted(live)]
    output_hash = sha256()
    width = (len(inputs) + 7) // 8
    for target in inputs:
        output_hash.update(interner.supports[outputs[target]].to_bytes(width, "little"))
    additions = sum(interner.children[node] is not None for node in live)
    return {"h": h, "root_split": root_split, "order": list(order),
            "flips": [list(f) for f in flips], "additions": additions,
            "roles": additions + len(inputs), "live_nodes": len(live),
            "allocated_nodes": len(interner.supports) - 1,
            "nodes_only_sha256": sha256(json.dumps(nodes, separators=(",", ":")).encode()).hexdigest(),
            "output_support_sha256": output_hash.hexdigest(),
            "coefficient_entries": len(inputs) ** 2,
            "all_integer_coefficients_verified": True}


def run_cases(recipes, h=22, root_split=11):
    """Return exact records for (root j permutation, tied-channel flips) recipes."""
    require(type(h) is int and h >= 8 and h % 2 == 0, "even h >= 8 required")
    plans = recurrence(h)
    return [_reconstruct(order, flips, h, root_split, plans) for order, flips in recipes]


if __name__ == "__main__":
    print(json.dumps(run_cases([((0, 1, 2, 3), ()),
                               ((0, 1, 2, 3), ((1, 1),))]), indent=2))
