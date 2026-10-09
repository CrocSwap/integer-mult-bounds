"""Evaluator-owned scalar circuit for the BIT side producer (IMMUTABLE; do not edit).

Inputs x_S for every triple S of [h] (nodes 1..v, in itertools.combinations order). The producer may only call
add(a, b) (cancellation-free: the supports of a and b must be disjoint; an existing support is returned instead of a
duplicate node) and total(xs). Supports are bitmasks over the triple list; node 0 is the empty sum.
"""
from itertools import combinations


class BitCircuit:
    def __init__(self, h):
        self.h = h
        self.triples = list(combinations(range(h), 3))
        self.v = len(self.triples)
        self.tindex = {t: j for j, t in enumerate(self.triples)}
        self.args = [(0, 0)]
        self.support = [0]
        self.lookup = {}
        self.inputs = {}
        for j, t in enumerate(self.triples):
            x = len(self.args)
            self.inputs[t] = x
            self.args.append((0, 0))
            self.support.append(1 << j)
            self.lookup[1 << j] = x

    def add(self, a, b):
        """Cancellation-free addition; returns the existing node if this support already exists."""
        if not a:
            return b
        if not b:
            return a
        assert 0 < a < len(self.args) and 0 < b < len(self.args)
        assert not self.support[a] & self.support[b], 'additions must be cancellation-free'
        s = self.support[a] | self.support[b]
        if s in self.lookup:
            return self.lookup[s]
        x = len(self.args)
        self.args.append((a, b))
        self.support.append(s)
        self.lookup[s] = x
        return x

    def total(self, xs):
        """Balanced-tree sum of nonzero nodes (helper; the producer may use its own orders)."""
        xs = [x for x in xs if x]
        while len(xs) > 1:
            xs = [self.add(xs[i], xs[i + 1]) if i + 1 < len(xs) else xs[i] for i in range(0, len(xs), 2)]
        return xs[0] if xs else 0

    def chain(self, xs):
        """Left-to-right chain sum of nonzero nodes."""
        acc = 0
        for x in xs:
            acc = self.add(acc, x)
        return acc
