#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate literal matrices, truncated-word relation space and regular action.

No primary mathematical implementation is imported. Shared common.py is I/O.
Gareth Davidson, with substantial OpenAI Codex assistance; no human review.
"""
import argparse
from collections import deque
from itertools import combinations, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import canonical, digest, finish, read, require, HERE

POSITIONS = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))
NAMES = ("", "a", "b", "c", "ab", "ac", "ba", "bc", "cb",
         "aba", "abc", "acb", "bab", "bac", "bcb", "cba", "cbc")
WORDS = ("", "abab", "bcbc", "abacbc", "abcbabcb", "acbabc", "abcbac", "acbacb")
TYPES = (0, 1, 2, 3, 5, 6, 7)


def matmul(a, b):
    return tuple(sum((sum(a[i][k] * b[k][j] for k in range(len(a))) & 1) << j
                     for j in range(len(a))) for i in range(len(a)))


def unpack(rows):
    return tuple(tuple((row >> j) & 1 for j in range(len(rows))) for row in rows)


def literal(code):
    a = [[int(i == j) for j in range(4)] for i in range(4)]
    for k, (i, j) in enumerate(POSITIONS):
        a[i][j] = (code >> k) & 1
    return tuple(tuple(row) for row in a)


MATRICES = tuple(literal(i) for i in range(64))
LOOKUP = {tuple(sum(v << j for j, v in enumerate(row)) for row in m): i
          for i, m in enumerate(MATRICES)}
GROUP = tuple(tuple(LOOKUP[matmul(a, b)] for b in MATRICES) for a in MATRICES)


def xor_rank(rows):
    vectors = list(rows)
    rank = 0
    for column in range(max((v.bit_length() for v in vectors), default=0)):
        pivot = next((i for i in range(rank, len(vectors)) if (vectors[i] >> column) & 1), None)
        if pivot is None:
            continue
        vectors[rank], vectors[pivot] = vectors[pivot], vectors[rank]
        for i in range(len(vectors)):
            if i != rank and ((vectors[i] >> column) & 1):
                vectors[i] ^= vectors[rank]
        rank += 1
    return rank


class Quotient:
    def __init__(self):
        self.words = tuple("".join(w) for n in range(4) for w in product("abc", repeat=n))
        self.index = {w: i for i, w in enumerate(self.words)}
        self.pivots = {}
        for relation in (("aa",), ("bb",), ("cc",), ("ac", "ca")):
            for left in self.words:
                for right in self.words:
                    if len(left) + 2 + len(right) > 3:
                        continue
                    row = 0
                    for term in relation:
                        row ^= 1 << self.index[left + term + right]
                    row = self.reduce(row)
                    if row:
                        self.pivots[row.bit_length() - 1] = row
        self.free = tuple(i for i in range(40) if i not in self.pivots)
        require(tuple(self.words[i] for i in self.free) == NAMES, "independent quotient basis")
        self.table = tuple(tuple(self.reduce(1 << self.index[a + b]) if len(a + b) <= 3 else 0
                                 for b in self.words) for a in self.words)

    def reduce(self, value):
        for pivot in sorted(self.pivots, reverse=True):
            if (value >> pivot) & 1:
                value ^= self.pivots[pivot]
        return value

    def multiply(self, x, y):
        out = 0
        for i in range(40):
            if (x >> i) & 1:
                for j in range(40):
                    if (y >> j) & 1:
                        out ^= self.table[i][j]
        return out

    def compact(self, value):
        value = self.reduce(value)
        return sum(((value >> bit) & 1) << k for k, bit in enumerate(self.free))


def rows_product(a, b, r):
    return tuple(sum((sum(((a[i] >> k) & 1) * ((b[k] >> j) & 1) for k in range(r)) & 1) << j
                     for j in range(r)) for i in range(r))


def subset_coeff(word, quotient):
    out = [[0, 0] for _ in NAMES]
    for size in range(len(word) + 1):
        for chosen in combinations(range(len(word)), size):
            raw = "".join(word[i][0] for i in chosen)
            q = quotient.compact(1 << quotient.index[raw])
            rows = (1, 2)
            for i in chosen:
                _, x, y = word[i]
                rows = rows_product(rows, tuple(y * ((x >> j) & 1) for j in range(2)), 2)
            for k in range(17):
                if (q >> k) & 1:
                    out[k] = [a ^ b for a, b in zip(out[k], rows)]
    return out


def regular_word(word, r):
    rows = [1 << i for i in range(64 * r)]
    # Product D1...Dn acts on a column with Dn first.
    for label, u, v in reversed(word):
        g = 1 << "abc".index(label)
        incoming = [0] * 64
        for j in range(r):
            if (v >> j) & 1:
                incoming = [a ^ b for a, b in zip(incoming, rows[j * 64:(j + 1) * 64])]
        delta = [incoming[h] ^ incoming[GROUP[g][h]] for h in range(64)]
        for i in range(r):
            if (u >> i) & 1:
                for h in range(64):
                    rows[i * 64 + h] ^= delta[h]
    return rows


def witness(targets, r, conjugate=False):
    s = [[int(i == j) for j in range(r)] for i in range(r)]
    if conjugate:
        for j in range(r - 1):
            s[-1][j] = 1
    word = []
    expected = [0] * (r * 64)
    for k in range(r):
        code = targets[k] if k < len(targets) else 0
        u = sum(s[i][k] << i for i in range(r))
        v = sum(s[k][j] << j for j in range(r))
        word.extend((a, u, v) for a in WORDS[code])
        for i in range(r):
            for j in range(r):
                if s[i][k] * s[k][j]:
                    for h in range(64):
                        expected[64 * i + GROUP[code << 3][h]] ^= 1 << (64 * j + h)
    actual = regular_word(word, r)
    require(actual == expected, "faithful regular endpoint")
    formal = []
    for g in range(64):
        coeff = [sum(((actual[64 * i + g] >> (64 * j)) & 1) << j for j in range(r)) for i in range(r)]
        if any(coeff):
            formal.append([g, coeff])
    counts = [sum(letter == a for letter, u, v in word) for a in "abc"]
    return [list(targets), r, conjugate, formal, counts], actual, word


def build():
    q = Quotient()
    paths, images = {0: ""}, {0: 1}
    queue = deque([0])
    while queue:
        old = queue.popleft()
        for j, a in enumerate("abc"):
            new = GROUP[old][1 << j]
            proposal = q.multiply(images[old], 1 | (1 << q.index[a]))
            if new not in paths:
                paths[new] = paths[old] + a
                images[new] = proposal
                queue.append(new)
            else:
                require(images[new] == proposal, "path-independent quotient")
    for a, b in product(range(64), repeat=2):
        require(q.multiply(images[a], images[b]) == images[GROUP[a][b]], "literal quotient homomorphism")
    for i, j, k in product(q.free, repeat=3):
        require(q.multiply(q.multiply(1 << i, 1 << j), 1 << k) == q.multiply(1 << i, q.multiply(1 << j, 1 << k)), "relation quotient associativity")
    transcript = []
    alphabet = tuple(product("abc", range(1, 4), range(1, 4)))
    for n in range(4):
        for word in product(alphabet, repeat=n):
            coeff = subset_coeff(word, q)
            # Independently check the span deductions for all arbitrary short words.
            for label, colnames, rownames in (("a", ("a", "ab", "abc"), ("a", "ba", "cba")),
                    ("b", ("b", "ba", "bc", "bac"), ("b", "ab", "cb", "acb")),
                    ("c", ("c", "cb", "cba"), ("c", "bc", "abc"))):
                cols = [sum(((coeff[NAMES.index(name)][i] >> j) & 1) << i for i in range(2))
                        for name in colnames for j in range(2)]
                rows = [v for name in rownames for v in coeff[NAMES.index(name)]]
                xs = [u for g, u, v in word if g == label]
                ys = [v for g, u, v in word if g == label]
                require(xor_rank(xs + cols) == xor_rank(xs), "independent column implication")
                require(xor_rank(ys + rows) == xor_rank(ys), "independent row implication")
                require(len(xs) >= xor_rank(cols) + xor_rank(rows) - xor_rank(coeff[NAMES.index(label)]), "independent tariff")
            transcript.append(coeff)
    records, column_count = [], 0
    for width in (1, 2, 3):
        for targets in product(TYPES, repeat=width):
            record, _, _ = witness(targets, width + 1)
            records.append(record)
            column_count += 64 * (width + 1)
    for targets, r in [((1, 2, 3, 5, 6, 7), 8), ((5, 6, 7), 6), ((7,), 4)]:
        record, _, _ = witness(targets, r, True)
        records.append(record)
        column_count += 64 * r
    # The nonzero cubic-kernel perturbation affects every input column of one dirty role.
    kernel = [0, 1, 32, 33]
    kernel_columns = [sum(1 << GROUP[g][h] for g in kernel) for h in range(64)]
    require(all(v.bit_count() == 4 for v in kernel_columns), "dirty-kernel visibility")
    require(q.reduce(images[0] ^ images[1] ^ images[32] ^ images[33]) == 0, "kernel quotient invisibility")
    expected = read(HERE / "EXPECTED.json")
    shared = {"group_map_sha256": digest([list(NAMES), [q.compact(images[g]) for g in range(64)], [v for row in GROUP for v in row]]),
              "coefficient_words": len(transcript), "coefficient_sha256": digest(transcript),
              "formal_witnesses": len(records), "witness_sha256": digest(records)}
    require(canonical(shared) == canonical({k: expected[k] for k in shared}), "primary/independent transcript mismatch")
    return {"schema_version": 1, **shared, "relation_generators_rank": len(q.pivots),
            "quotient_dimension": len(q.free), "group_products": 4096,
            "associativity_triples": 4913, "faithful_basis_columns": column_count,
            "dirty_kernel_columns_changed": len(kernel_columns),
            "group_distances": [len(paths[g]) for g in range(64)]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build()
    finish(result, "INDEPENDENT.json", args.write)
    print("PASS_UT4_MIXED_ROOT_INDEPENDENT columns=" + str(result["faithful_basis_columns"]))


if __name__ == "__main__":
    main()
