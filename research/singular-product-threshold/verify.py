#!/usr/bin/env python3
"""Exact singular-product checks. Produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    def __init__(self, q):
        require(q in (2, 3, 4, 5, 7), "unsupported field order")
        self.q = q
        self.add = tuple(tuple(a ^ b if q == 4 else (a + b) % q
                               for b in range(q)) for a in range(q))
        self.mul = tuple(tuple(self.polynomial(a, b) if q == 4 else a * b % q
                               for b in range(q)) for a in range(q))
        self.neg = tuple(next(b for b in range(q) if self.add[a][b] == 0)
                         for a in range(q))
        self.inv = (0,) + tuple(next(b for b in range(1, q)
                                    if self.mul[a][b] == 1)
                                for a in range(1, q))
        self.lines = ((0, 1),) + tuple((1, a) for a in range(q))
        self.vectors = tuple(product(range(q), repeat=2))

    @staticmethod
    def polynomial(a, b):
        value = 0
        for bit in range(2):
            if b >> bit & 1:
                value ^= a << bit
        if value & 4:
            value ^= 7
        return value

    def sub(self, a, b):
        return self.add[a][self.neg[b]]

    def dot(self, u, v):
        return self.add[self.mul[u[0]][v[0]]][self.mul[u[1]][v[1]]]

    def act(self, a, v):
        return self.dot(a[:2], v), self.dot(a[2:], v)

    def mm(self, a, b):
        return tuple(self.dot(a[2*i:2*i+2], (b[j], b[2+j]))
                     for i in range(2) for j in range(2))

    def det(self, a):
        return self.sub(self.mul[a[0]][a[3]], self.mul[a[1]][a[2]])

    def paid(self, u, y):
        identity = (1, 0, 0, 1)
        return tuple(self.add[identity[2*i+j]][self.mul[u[i]][y[j]]]
                     for i in range(2) for j in range(2))

    def line(self, v):
        require(v != (0, 0), "zero has no projective line")
        return (1, self.mul[v[1]][self.inv[v[0]]]) if v[0] else (0, 1)


def upper_word(f, matrix, wrong_sign=False):
    a, b, c, d = matrix
    if b == 0:
        return (a, 0, c, 1), (1, 0, 0, d), (1, 0, 0, 1)
    lower = f.mul[f.sub(d, 1)][f.inv[b]]
    correction = f.mul[lower][a]
    bottom = f.add[c][correction] if wrong_sign else f.sub(c, correction)
    first = f.sub(a, f.mul[b][bottom])
    return (1, 0, lower, 1), (1, b, 0, 1), (first, 0, bottom, 1)


def full_pivot(f, matrices):
    """Raw product-of-fields ideal test, without kernel/image grouping."""
    for t, phi in product(f.lines, repeat=2):
        valid = True
        for matrix in matrices:
            row = (f.dot(phi, (matrix[0], matrix[2])),
                   f.dot(phi, (matrix[1], matrix[3])))
            if f.dot(row, t) == 0 and row != (0, 0):
                valid = False
                break
        if valid:
            return t, phi
    return None


def grouped_pivot(f, matrices):
    """The new kernel/image criterion, using distinct image lines."""
    for t in f.lines:
        images = set()
        for matrix in matrices:
            if f.act(matrix, t) == (0, 0):
                column = (matrix[0], matrix[2])
                if column == (0, 0):
                    column = (matrix[1], matrix[3])
                images.add(f.line(column))
        if len(images) <= 1:
            return True
    return False


def binary_literal_images(f, rankones):
    matrices = tuple(product(range(2), repeat=4))
    free = tuple(a for a in matrices if f.det(a))
    require(all(a not in free for a in rankones), "zero-paid image excludes singular targets")
    one_masks, two_masks = set(), set()
    for y, scalar in product(f.lines, free):
        image = {f.mm(f.paid(u, y), scalar) for u in f.vectors}
        one_masks.add(sum(1 << i for i, a in enumerate(rankones) if a in image))
        for z in f.lines:
            image = {f.mm(f.mm(f.paid(u, y), f.paid(v, z)), scalar)
                     for u, v in product(f.vectors, repeat=2)}
            two_masks.add(sum(1 << i for i, a in enumerate(rankones) if a in image))
    return one_masks, two_masks


def binary_census():
    f = Field(2)
    rankones = tuple(a for a in product(range(2), repeat=4)
                    if a != (0, 0, 0, 0) and f.det(a) == 0)
    require(len(rankones) == 9, "binary rank-one coverage")
    one_masks, two_masks = binary_literal_images(f, rankones)
    costs = []
    for mask in range(1 << len(rankones)):
        selected = tuple(a for i, a in enumerate(rankones) if mask >> i & 1)
        literal = any(mask & image == mask for image in two_masks)
        require(literal == grouped_pivot(f, selected), "literal/grouped mismatch")
        require(literal == (full_pivot(f, selected) is not None), "raw mismatch")
        one = any(mask & image == mask for image in one_masks)
        costs.append(1 if one else 2 if literal else 3)
    counts = {0: 1}
    rows = []
    for k in range(1, 7):
        next_counts = Counter()
        for mask, multiplicity in counts.items():
            for i in range(len(rankones)):
                next_counts[mask | 1 << i] += multiplicity
        counts = next_counts
        histogram = [0, 0, 0, 0]
        for mask, multiplicity in counts.items():
            histogram[costs[mask]] += multiplicity
        require(sum(histogram) == 9 ** k, "tuple multiplicity coverage")
        require(histogram[3] == (19440 if k == 6 else 0), "threshold census")
        rows.append({"components": k, "targets": 9 ** k, "costs": histogram})
    require(rows[-1]["costs"] == [0, 567, 511434, 19440], "six-component census")
    bad = [mask for mask, cost in enumerate(costs) if cost == 3]
    require(len(bad) == 64 and min(m.bit_count() for m in bad) == 6,
            "obstructed support coverage")
    return rows, {"support_sets": 512, "bad_supports": 64,
                  "one_chart_masks": len(one_masks), "two_chart_masks": len(two_masks)}


def field_check(f):
    for a, b, c in product(range(f.q), repeat=3):
        require(f.add[f.add[a][b]][c] == f.add[a][f.add[b][c]], "add associativity")
        require(f.mul[f.mul[a][b]][c] == f.mul[a][f.mul[b][c]], "mul associativity")
        require(f.mul[a][f.add[b][c]] == f.add[f.mul[a][b]][f.mul[a][c]],
                "distributivity")
    for a in range(1, f.q):
        require(f.mul[a][f.inv[a]] == 1, "field inverse")
    target_count, input_count, reversals, omissions, sign_errors = 0, 0, 0, 0, 0
    for matrix in product(range(f.q), repeat=4):
        word = upper_word(f, matrix)
        require(f.mm(f.mm(word[0], word[1]), word[2]) == matrix, "upper word")
        rights = ((1, 0), (0, 1), (1, 0))
        for factor, right in zip(word, rights, strict=True):
            left = (f.sub(factor[0], 1), factor[2]) if right == (1, 0) else (
                factor[1], f.sub(factor[3], 1))
            require(f.paid(left, right) == factor, "common paid right vector")
        for v in f.vectors:
            actual = v
            for factor in reversed(word):
                actual = f.act(factor, actual)
            require(actual == f.act(matrix, v), "literal arbitrary-input action")
            input_count += 1
        reversals += f.mm(f.mm(word[2], word[1]), word[0]) != matrix
        omissions += f.mm(word[0], word[1]) != matrix
        mutant = upper_word(f, matrix, wrong_sign=True)
        sign_errors += f.mm(f.mm(mutant[0], mutant[1]), mutant[2]) != matrix
        target_count += 1
    require(reversals > 0 and omissions > 0, "word mutation controls")
    if f.q in (3, 5, 7):
        require(sign_errors > 0, "odd-field sign control")
    return {"q": f.q, "matrices": target_count, "inputs": input_count,
            "reversed_rejected": reversals, "omitted_rejected": omissions,
            "wrong_sign_rejected": sign_errors}


def sharp_check(f):
    matrices = []
    for t in f.lines:
        annihilator = (f.neg[t[1]], t[0])
        for image in ((1, 0), (0, 1)):
            matrices.append(tuple(f.mul[image[i]][annihilator[j]]
                                  for i in range(2) for j in range(2)))
    require(len(matrices) == 2 * (f.q + 1), "sharp family size")
    require(not grouped_pivot(f, matrices) and full_pivot(f, matrices) is None,
            "sharp lower bound")
    for i in range(len(matrices)):
        reduced = matrices[:i] + matrices[i+1:]
        require(grouped_pivot(f, reduced) and full_pivot(f, reduced) is not None,
                "deleting any component removes the obstruction")
    repeated = [matrices[2*i] for i in range(f.q + 1) for _ in range(2)]
    require(grouped_pivot(f, repeated) and full_pivot(f, repeated) is not None,
            "multiplicity is not image diversity")
    require(all(full_pivot(f, [a]) is not None for a in matrices),
            "common-chart control")
    return {"q": f.q, "threshold": len(matrices), "deletions": len(matrices)}


def receipt(payload):
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        raw = (root / name).read_bytes()
        require(len(raw) <= 1024 * 1024, "receipt source size bound")
        hashes[name] = sha256(raw).hexdigest()
    print(json.dumps({"schema": "singular-product-threshold/v1",
                      "sources": hashes, "result": payload}, sort_keys=True))


def main():
    rows, supports = binary_census()
    fields, sharp = [], []
    for q in (2, 3, 4, 5, 7):
        f = Field(q)
        fields.append(field_check(f))
        sharp.append(sharp_check(f))
    rejected = False
    try:
        Field(6)
    except ValueError:
        rejected = True
    require(rejected, "composite modulus control")
    print("PASS_SINGULAR_PRODUCT_THRESHOLD binary_cost3=19440 threshold=6 no_new_kappa")
    receipt({"binary": rows, "supports": supports, "fields": fields, "sharp": sharp})


if __name__ == "__main__":
    main()
