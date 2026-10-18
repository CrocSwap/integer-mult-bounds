"""Deterministic, standard-library encoding of PR620's archived fitting pattern.

The Tseitin schema follows Joel Pulikkan / PR620's minrank_sat.py; geometry
follows the preserved DreamingOfClouds utility. See NOTICE.md. Apache-2.0.
"""
from itertools import product
import hashlib

PUNCTURES = (39, 52, 57, 71, 76, 78, 103, 109, 114)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def geometry():
    generators = (0b00001111, 0b00111100, 0b11110000, 0b10101010)
    code = {0}
    for generator in generators:
        code |= {word ^ generator for word in tuple(code)}
    # The archival utility sorts coordinate tuples, not their packed integers.
    supports = sorted(tuple((word >> i) & 1 for i in range(8))
                      for word in code if word.bit_count() == 4)
    rows = [[2*int(i == j) for i in range(8)] for j in range(8)]
    for support in supports:
        indices = [i for i, bit in enumerate(support) if bit]
        for signs in product((1, -1), repeat=3):
            row = [0]*8
            for i, sign in zip(indices, (1,)+signs):
                row[i] = sign
            rows.append(row)
    need(len(rows) == 120 and len({tuple(r) for r in rows}) == 120, "root enumeration")
    gram = [[sum(x*y for x, y in zip(a, b))//2 for b in rows] for a in rows]
    for i in range(120):
        for j in range(120):
            dot = sum(x*y for x, y in zip(rows[i], rows[j]))
            need(dot % 2 == 0, "nonintegral Gram entry")
            need(gram[i][j] in ((2,) if i == j else (-1, 0, 1)), "Gram domain")
    live = [i for i in range(120) if i not in PUNCTURES]
    baseline = [[(1+gram[i][j]) % 2 for j in live] for i in live]
    pattern = {(i, j) for i in range(111) for j in range(111)
               if i != j and gram[live[i]][live[j]] != 0}
    clique = first_clique(111, pattern, 8)
    need(clique is not None, "eight-port anchor missing")
    # Independent explicit anchored nine-bit Gram factor; no symmetric
    # factorization or NumPy is needed for the positive calibration.
    labels = [sum(baseline[t][k] << i for i, k in enumerate(clique))
              | ((1+sum(baseline[t][k] for k in clique)) % 2) << 8
              for t in range(111)]
    need(all(((a & b).bit_count() % 2) == baseline[i][j]
             for i, a in enumerate(labels) for j, b in enumerate(labels)),
         "positive nine-bit Gram factor")
    need(all(labels[k] == 1 << i for i, k in enumerate(clique)), "positive gauge")
    return rows, gram, live, baseline, pattern, clique, labels


def first_clique(v, pattern, size):
    neighbors = [sum(1 << j for j in range(v) if (i, j) in pattern) for i in range(v)]

    def search(chosen, candidates):
        if len(chosen) == size:
            return chosen
        if len(chosen)+candidates.bit_count() < size:
            return None
        while candidates:
            bit = candidates & -candidates
            i = bit.bit_length()-1
            candidates ^= bit
            answer = search(chosen+[i], candidates & neighbors[i])
            if answer is not None:
                return answer
        return None
    return search([], (1 << v)-1)


class CNF:
    def __init__(self, sink=None, calibration=False):
        self.variables = 0
        self.clauses = 0
        self.sink = sink
        self.payload_hash = hashlib.sha256()
        self.values = [False] if calibration else None
        self.unsatisfied = []

    def new(self, value=False):
        self.variables += 1
        if self.values is not None:
            self.values.append(bool(value))
        return self.variables

    def add(self, clause):
        clause = tuple(clause)
        need(all(type(lit) is int and 0 < abs(lit) <= self.variables for lit in clause), "invalid encoded literal")
        self.clauses += 1
        self.payload_hash.update((" ".join(map(str, clause))+" 0\n").encode("ascii"))
        if self.sink:
            self.sink(self.clauses, clause)
        if self.values is not None and not any(self.values[abs(lit)] == (lit > 0) for lit in clause):
            self.unsatisfied.append(self.clauses)

    def AND(self, a, b):
        z = self.new(self.values[a] and self.values[b] if self.values is not None else False)
        for row in ((-z, a), (-z, b), (z, -a, -b)):
            self.add(row)
        return z

    def XOR(self, a, b):
        z = self.new(self.values[a] != self.values[b] if self.values is not None else False)
        for row in ((-z, a, b), (-z, -a, -b), (z, -a, b), (z, a, -b)):
            self.add(row)
        return z

    def parity(self, inputs):
        result = inputs[0]
        for lit in inputs[1:]:
            result = self.XOR(result, lit)
        return result


def build(v, pattern, baseline, dimension, clique, mode, sink=None, inputs=None):
    need(type(dimension) is int and dimension >= 1, "positive dimension required")
    need(mode in ("none", "neB0"), "unknown fitting mode")
    need(len(clique) <= dimension and len(set(clique)) == len(clique), "invalid gauge size")
    need(all((a, b) in pattern for a in clique for b in clique if a != b), "gauge is not a clique")
    f = CNF(sink=sink, calibration=inputs is not None)
    source = [[f.new((inputs[0][t] >> j) & 1 if inputs else False)
               for j in range(dimension)] for t in range(v)]
    sink_labels = [[f.new((inputs[1][t] >> j) & 1 if inputs else False)
                   for j in range(dimension)] for t in range(v)]
    entries = {}

    def entry(t, s):
        if (t, s) not in entries:
            entries[t, s] = f.parity([f.AND(sink_labels[t][j], source[s][j])
                                     for j in range(dimension)])
        return entries[t, s]

    for t in range(v):
        f.add((entry(t, t),))
    for t, s in sorted(pattern):
        f.add((-entry(t, s),))
    for i, t in enumerate(clique):
        for j in range(dimension):
            f.add((source[t][j] if j == i else -source[t][j],))
            f.add((sink_labels[t][j] if j == i else -sink_labels[t][j],))
    if mode == "neB0":
        f.add([entry(t, s) if baseline[t][s] == 0 else -entry(t, s)
               for t in range(v) for s in range(v) if t != s and (t, s) not in pattern])
    return f


def archived(dimension, sink=None):
    rows, gram, live, baseline, pattern, clique, labels = geometry()
    return build(111, pattern, baseline, dimension, clique,
                 "none" if dimension == 8 else "neB0", sink,
                 (labels, labels) if dimension == 9 else None)
