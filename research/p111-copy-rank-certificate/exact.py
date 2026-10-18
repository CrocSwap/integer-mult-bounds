"""Independent, standard-library arithmetic for P111 label decoders.

E8 root numbering follows the extended-Hamming construction used by the
repository. No repository implementation is imported.
"""
from itertools import product
from math import gcd
import json
from pathlib import Path

PUNCTURES = {
    "pr545": [39, 52, 57, 71, 76, 78, 103, 109, 114],
    "pr555": [10, 15, 51, 53, 56, 66, 72, 89, 111],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(x):
    return bin(x).count("1") % 2


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def generated_root_set():
    generators = [
        (1, 1, 1, 1, 0, 0, 0, 0),
        (0, 0, 1, 1, 1, 1, 0, 0),
        (0, 0, 0, 0, 1, 1, 1, 1),
        (0, 1, 0, 1, 0, 1, 0, 1),
    ]
    code = {tuple(sum(c[i] * generators[i][j] for i in range(4)) % 2
                  for j in range(8)) for c in product((0, 1), repeat=4)}
    weight4 = sorted(c for c in code if sum(c) == 4)
    out = [tuple(2 * (a == b) for b in range(8)) for a in range(8)]
    for word in weight4:
        support = [i for i, x in enumerate(word) if x]
        for signs in product((1, -1), repeat=3):
            r = [0] * 8
            for i, sign in zip(support, (1,) + signs):
                r[i] = sign
            out.append(tuple(r))
    require(len(out) == 120 and len(set(out)) == 120, "bad root census")
    require(all(dot(r, r) == 4 for r in out), "bad root norm")
    return out


def roots():
    """Pinned supplier ordering, checked against an independently generated set.

    Sorting Hamming words generates the right set in a different order; numeric
    puncture IDs must instead follow the actual supplier's root table.
    """
    data = json.loads((Path(__file__).resolve().parent / "roots.json").read_text())
    out = [tuple(row) for row in data["lines"]]
    require(len(out) == 120 and set(out) == set(generated_root_set()), "bad indexed root table")
    return out


def row_basis_q(rows):
    """Fraction-free integer elimination; output spans the same Q-space."""
    basis = []
    for row in rows:
        v = list(row)
        for p, b in basis:
            if v[p]:
                g, f = b[p], v[p]
                v = [g * x - f * y for x, y in zip(v, b)]
                content = 0
                for x in v:
                    content = gcd(content, x)
                if content > 1:
                    v = [x // content for x in v]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            if v[pivot] < 0:
                v = [-x for x in v]
            basis.append((pivot, v))
    return [v for _, v in basis]


def rank_f2(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def inverse_f2(rows, n):
    augmented = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (augmented[i] >> j) & 1), None)
        require(pivot is not None, "singular binary matrix")
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        for i in range(n):
            if i != j and (augmented[i] >> j) & 1:
                augmented[i] ^= augmented[j]
    require([r & ((1 << n) - 1) for r in augmented] == [1 << i for i in range(n)],
            "bad inverse")
    return [r >> n for r in augmented]


def pairing_rows(lines):
    out = []
    for r in lines:
        require(all(dot(r, s) % 2 == 0 for s in lines), "nonintegral Gram")
        out.append(sum(((1 + dot(r, s) // 2) % 2) << j for j, s in enumerate(lines)))
    return out


class Instance:
    def __init__(self, name):
        require(name in PUNCTURES, "unknown fixture")
        self.name = name
        self.lines = roots()
        self.punctures = PUNCTURES[name]
        self.live = [i for i in range(120) if i not in self.punctures]
        full_pairing = pairing_rows(self.lines)
        self.B = [sum(((full_pairing[i] >> j) & 1) << a
                      for a, j in enumerate(self.punctures)) for i in self.punctures]
        self.target = inverse_f2(self.B, 9)
        self.labels = [sum(((full_pairing[i] >> j) & 1) << a
                           for a, j in enumerate(self.punctures)) for i in self.live]
        require(rank_f2(self.labels) == 9, "live labels do not span")
        self.readers = {}
        self.bases = {}
        for x in range(1, 512):
            indices = [i for i, r in zip(self.live, self.labels) if parity(r & x)]
            self.readers[x] = indices
            self.bases[x] = row_basis_q(self.lines[i] for i in indices)
        deficient = [x for x, basis in self.bases.items() if len(basis) < 8]
        require(deficient == [1 << i for i in range(9)], "unexpected deficient functionals")
        for i, p in enumerate(self.punctures):
            require(len(self.bases[1 << i]) == 7, "bad hyperplane dimension")
            require(all(dot(r, self.lines[p]) == 0 for r in self.bases[1 << i]),
                    "bad hyperplane normal")

    def cost(self, x, y):
        require(type(x) is int and type(y) is int and 0 < x < 512 and 0 < y < 512,
                "terms must contain two nonzero 9-bit integers")
        ux, uy = x & (x - 1) == 0, y & (y - 1) == 0
        if not ux and not uy:
            return 8
        if not (ux and uy):
            return 7
        i, j = x.bit_length() - 1, y.bit_length() - 1
        return 6 if dot(self.lines[self.punctures[i]], self.lines[self.punctures[j]]) == 0 else 7

    def direct_cost(self, x, y):
        a, b = self.bases[x], self.bases[y]
        return len(row_basis_q([[dot(r, s) for s in b] for r in a]))

    def baseline(self):
        return [[1 << i, row] for i, row in enumerate(self.target)]

    def evaluate(self, terms):
        require(isinstance(terms, list) and 1 <= len(terms) <= 20, "bad term count")
        rows = [0] * 9
        costs = []
        for term in terms:
            require(isinstance(term, list) and len(term) == 2, "bad term")
            x, y = term
            costs.append(self.cost(x, y))
            for i in range(9):
                if (x >> i) & 1:
                    rows[i] ^= y
        require(rows == self.target, "rank-one sum fails target identity")
        return {"instance": self.name, "cost": sum(costs), "term_costs": costs,
                "terms": len(terms), "valid": True}
