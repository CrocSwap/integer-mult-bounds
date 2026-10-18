#!/usr/bin/env python3
"""Separate faithful-regular witness implementation; imports no local code.

Address multiplication uses literal binary 3x3 matrices. Register actions use
8r-dimensional row-bit matrices, not formal group-algebra coefficients.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""

import hashlib
from itertools import product
import json


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def address_product(a, b):
    return tuple(sum(a[3 * i + k] * b[3 * k + j] for k in range(3)) % 2 for i in range(3) for j in range(3))


ELEMENTS = tuple((1, n & 1, n >> 2, 0, 1, (n >> 1) & 1, 0, 0, 1) for n in range(8))
INDEX = {value: i for i, value in enumerate(ELEMENTS)}
PERM = tuple(tuple(INDEX[address_product(g, h)] for h in ELEMENTS) for g in ELEMENTS)
DIRECT = ((), (1,), (2,), (2, 1), (1, 2, 1, 2), (2, 1, 2), (1, 2, 1), (1, 2))


def identity(n):
    return [1 << i for i in range(n)]


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            low = row & -row
            value ^= b[low.bit_length() - 1]
            row ^= low
        out.append(value)
    return out


def paid(r, label, u, v):
    rows = identity(8 * r)
    for i in range(r):
        for j in range(r):
            if u >> i & 1 and v >> j & 1:
                for h in range(8):
                    rows[8 * i + h] ^= 1 << (8 * j + h)
                    rows[8 * i + PERM[label][h]] ^= 1 << (8 * j + h)
    return rows


def endpoint(labels, r):
    rows = [0] * (8 * r)
    for i in range(r):
        label = labels[i] if i < len(labels) else 0
        for h in range(8):
            rows[8 * i + PERM[label][h]] = 1 << (8 * i + h)
    return rows


def lift(scalar):
    r = len(scalar)
    rows = [0] * (8 * r)
    for i, row in enumerate(scalar):
        for j in range(r):
            if row >> j & 1:
                for h in range(8):
                    rows[8 * i + h] |= 1 << (8 * j + h)
    return rows


def basis(r):
    changes = []
    for i in range(r - 1):
        change = identity(r)
        change[i] |= 1 << (i + 1)
        changes.append(change)
    forward = identity(r)
    backward = identity(r)
    for change in changes:
        forward = multiply(forward, change)
    for change in reversed(changes):
        backward = multiply(backward, change)
    demand(multiply(forward, backward) == identity(r), "independent basis inversion")
    return lift(forward), lift(backward)


def digest_rows(digest, rows):
    digest.update(json.dumps(rows, separators=(",", ":")).encode() + b"\n")


def run():
    for label, word in enumerate(DIRECT):
        g = ELEMENTS[0]
        for letter in word:
            g = address_product(g, ELEMENTS[letter])
        demand(g == ELEMENTS[label], "direct literal address word")
    witness_digest = hashlib.sha256()
    fixtures = columns = 0
    for size in range(1, 4):
        for labels in product(range(8), repeat=size):
            for extra in (0, 1):
                r = size + extra
                gates = [paid(r, letter, 1 << i, 1 << i) for i, label in enumerate(labels) for letter in DIRECT[label]]
                for conjugated in (False, True):
                    f, inv = basis(r)
                    out = identity(8 * r)
                    for gate in gates:
                        op = multiply(multiply(f, gate), inv) if conjugated else gate
                        out = multiply(out, op)
                    expected = endpoint(labels, r)
                    if conjugated:
                        expected = multiply(multiply(f, expected), inv)
                    demand(out == expected, "faithful full arbitrary-input boundary")
                    digest_rows(witness_digest, out)
                    fixtures += 1
                    columns += 8 * r
    pair_digest = hashlib.sha256()
    alphabet = [paid(2, label, u, v) for label in (1, 2) for u in range(1, 4) for v in range(1, 4)]
    for left, right in product(alphabet, repeat=2):
        digest_rows(pair_digest, multiply(left, right))
    involutions = nilpotents = 0
    for r in (2, 3, 4):
        for u, v in product(range(1, 1 << r), repeat=2):
            for label in (1, 2):
                gate = paid(r, label, u, v)
                demand(multiply(gate, gate) == identity(8 * r), "full expanded factor involution")
                involutions += 1
                nilpotents += (u & v).bit_count() % 2 == 0
    # A four-term off-diagonal algebra element invisible to both small images
    # must still change the faithful action on a restored dirty role.
    good = endpoint((4,), 2)
    bad = list(good)
    for label in (0, 1, 4, 5):
        for h in range(8):
            bad[PERM[label][h]] ^= 1 << (8 + h)
    differences = [a ^ b for a, b in zip(good, bad)]
    demand(any(differences), "faithful kernel mutation must reject")
    demand(all(d & 255 == 0 for d in differences), "clean-input-only blind spot")
    dirty_changed = sum(any(d >> j & 1 for d in differences) for j in range(8, 16))
    demand(dirty_changed == 8, "all eight dirty basis inputs detect kernel mutation")
    # Reversing the noncommuting direct word distinguishes ab from ba.
    demand(multiply(paid(1, 1, 1, 1), paid(1, 2, 1, 1)) != endpoint((3,), 1), "noncommuting order control")
    return {"witness_fixtures": fixtures, "faithful_columns": columns,
            "witness_digest": witness_digest.hexdigest(), "two_factor_digest": pair_digest.hexdigest(),
            "two_factor_products": 324, "expanded_involutions": involutions,
            "nilpotent_involutions": nilpotents, "kernel_dirty_columns_detected": dirty_changed}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
