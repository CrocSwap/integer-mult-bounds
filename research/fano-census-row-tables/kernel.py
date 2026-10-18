# SPDX-License-Identifier: Apache-2.0
"""Exact GF(2) row-action tables for the PR3168 reduced-triple census.

Charan, with substantial OpenAI Codex assistance. No persistent acceptance cache.
"""
from array import array
from collections import Counter


def row_action(row, matrix):
    """XOR the selected rows; the row-vector action is linear over GF(2)."""
    out = 0
    while row:
        bit = row & -row
        out ^= matrix[bit.bit_length() - 1]
        row ^= bit
    return out


def prepare(matrices, dimension=17):
    if not 1 <= dimension <= 32:
        raise ValueError('row tables require dimension 1..32')
    m = [tuple(x) for x in matrices]
    if any(len(x) != dimension or any(type(r) is not int or not 0 <= r < 1 << dimension
                                     for r in x) for x in m):
        raise ValueError('invalid GF(2) row matrix')
    pairs = {(a, b): tuple(row_action(row, m[b]) for row in m[a])
             for a in range(len(m)) for b in range(len(m)) if a != b}
    # Only rows reached by actual reduced pairs are needed; every later lookup
    # is on one of these rows, by construction. No closed-form route assumption.
    domain = sorted({row for ab in pairs.values() for row in ab})
    indices = {row: i for i, row in enumerate(domain)}
    indexed = {pair: tuple(indices[row] for row in reversed(rows))
               for pair, rows in pairs.items()}
    actions = [array('I', (row_action(row, right) for row in domain)) for right in m]
    return indexed, actions, domain


def product_key(indexed_rows, action, dimension=17):
    # Reverse row order makes this Horner encoding exactly sum(row[i] << d*i).
    key = 0
    for i in indexed_rows:
        key = (key << dimension) | action[i]
    return key


def relation_census(matrices):
    """Same full domain and exact dictionary keys as the pinned reference."""
    indexed, actions, _ = prepare(matrices)
    classes = {}
    n = len(matrices)
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            rows = indexed[a, b]
            for c in range(n):
                if c != b:
                    classes.setdefault(product_key(rows, actions[c]), []).append((a, b, c))
    sizes = Counter(map(len, classes.values()))
    relations = set()
    for words in classes.values():
        for left in words:
            for right in words:
                if left != right:
                    a, b, c = left
                    d, e, f = right
                    w = (a, b, c, f, e, d)
                    if all(w[i] != w[(i + 1) % 6] for i in range(6)):
                        relations.add(w)
    return sum(sizes[k] * k for k in sizes), sizes, relations
