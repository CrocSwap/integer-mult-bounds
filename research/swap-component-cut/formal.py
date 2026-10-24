"""Formal algebra M_R(F2[GL_n(F2)]) and an exact meet-in-the-middle word search.

Group elements are tuples of row bitmasks. Algebra elements are frozensets
of group elements (F2 coefficients). A paid call is I_R + ([g] + [I]) N with
g a coordinate CNOT and N a rank-one binary idempotent. Free scalar maps are
normalized away first (#4939 step 1), so words consist of paid calls only.
"""

from __future__ import annotations

from collections import deque
from functools import reduce


def mul(a, b, n):
    return tuple(reduce(lambda acc, k: acc ^ (b[k] if a[i] >> k & 1 else 0), range(n), 0)
                 for i in range(n))


def identity(n):
    return tuple(1 << i for i in range(n))


def cnots(n):
    out = []
    for i in range(n):
        for j in range(n):
            if i != j:
                g = list(identity(n))
                g[i] ^= 1 << j
                out.append(tuple(g))
    return out


def row_permutation(n, sigma):
    """Row a of the result is row sigma[a] of the identity."""
    base = identity(n)
    return tuple(base[sigma[a]] for a in range(n))


def word_lengths(n):
    dist = {identity(n): 0}
    queue = deque([identity(n)])
    while queue:
        x = queue.popleft()
        for g in cnots(n):
            y = mul(g, x, n)
            if y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def algebra_product(x, y, n):
    acc = set()
    for g in x:
        for h in y:
            acc ^= {mul(g, h, n)}
    return frozenset(acc)


def matrix_product(a, b, registers, n):
    rows = []
    for i in range(registers):
        row = []
        for j in range(registers):
            entry = set()
            for k in range(registers):
                if a[i][k] and b[k][j]:
                    entry ^= algebra_product(a[i][k], b[k][j], n)
            row.append(frozenset(entry))
        rows.append(tuple(row))
    return tuple(rows)


class Model:
    def __init__(self, n, registers):
        self.n, self.registers = n, registers
        self.one = frozenset([identity(n)])
        self.zero = frozenset()
        projectors = []
        for u in range(1, 1 << registers):
            for v in range(1, 1 << registers):
                if bin(u & v).count("1") % 2:
                    projectors.append((u, v))
        self.generators = []
        for g in cnots(n):
            label = frozenset([g, identity(n)])
            for u, v in projectors:
                self.generators.append(tuple(
                    tuple((self.one if a == b else self.zero) ^ (label if (u >> a & 1) and (v >> b & 1) else self.zero)
                          for b in range(registers)) for a in range(registers)))

    def diagonal(self, elements):
        entries = [frozenset([e]) for e in elements] + [self.one] * (self.registers - len(elements))
        return tuple(tuple(entries[a] if a == b else self.zero for b in range(self.registers))
                     for a in range(self.registers))

    def layers(self, start, depth):
        seen = {start: 0}
        frontier = [start]
        for d in range(1, depth + 1):
            nxt = []
            for x in frontier:
                for g in self.generators:
                    y = matrix_product(x, g, self.registers, self.n)
                    if y not in seen:
                        seen[y] = d
                        nxt.append(y)
            frontier = nxt
        return seen

    def shortest(self, target, forward, backward_depth):
        """Least length <= max(forward) + backward_depth reaching target, or None.

        Generators are involutions, so the backward ball from the target is
        the set of target * W for words W of length <= backward_depth.
        """
        backward = self.layers(target, backward_depth)
        common = forward.keys() & backward.keys()
        return min((forward[x] + backward[x] for x in common), default=None)
