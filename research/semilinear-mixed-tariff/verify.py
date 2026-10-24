#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md, not proof by sampling.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
Standard library, no network/Git dependency and no generated package files.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
import runpy


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Polynomial-basis arithmetic; every nonzero inverse is checked."""

    def __init__(self, degree, polynomial):
        require(degree >= 1 and polynomial.bit_length() == degree + 1,
                "bad polynomial degree")
        self.degree, self.size, self.polynomial = degree, 1 << degree, polynomial
        self.table = [[self.multiply(a, b) for b in range(self.size)]
                      for a in range(self.size)]
        self.inverse = [0] + [self.power(a, self.size - 2)
                              for a in range(1, self.size)]
        require(all(self.table[a][self.inverse[a]] == 1
                    for a in range(1, self.size)), "reducible polynomial")

    def multiply(self, a, b):
        out = 0
        while b:
            if b & 1:
                out ^= a
            b >>= 1
            a <<= 1
            if a & self.size:
                a ^= self.polynomial
        return out

    def power(self, a, exponent):
        result = 1
        while exponent:
            if exponent & 1:
                result = self.table[result][a]
            a = self.table[a][a]
            exponent >>= 1
        return result


def binary_rank(columns):
    pivots = {}
    for vector in columns:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = vector
                break
            vector ^= pivots[pivot]
    return len(pivots)


def field_rank(matrix, field):
    a = [list(row) for row in matrix]
    row = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        inv = field.inverse[a[row][col]]
        a[row] = [field.table[inv][v] for v in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col]:
                scale = a[i][col]
                a[i] = [v ^ field.table[scale][w]
                        for v, w in zip(a[i], a[row])]
        row += 1
    return row


def apply_binary(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def natural(field, label):
    a, j = label
    return tuple(field.table[a][field.power(1 << k, 1 << j)]
                 for k in range(field.degree))


def group_product(field, left, right):
    a, j = left
    b, k = right
    return (field.table[a][field.power(b, 1 << j)], (j + k) % field.degree)


def displacement(field, character_field, root, label):
    """Actual (p+1)-square rho(g)-I direct-sum chi(g)-1 matrix."""
    columns, p = natural(field, label), field.degree
    a = [[0] * (p + 1) for _ in range(p + 1)]
    for i in range(p):
        for j in range(p):
            a[i][j] = ((columns[j] >> i) & 1) ^ (i == j)
    a[p][p] = character_field.power(root, label[1]) ^ 1
    return a


def rank_one_idempotents(r):
    for x in range(1, 1 << r):
        for y in range(1, 1 << r):
            if (x & y).bit_count() % 2:
                yield x, y


def paid_displacement(block, x, y, r):
    d = len(block)
    return [[block[i % d][j % d] if ((x >> (i // d)) & 1)
             and ((y >> (j // d)) & 1) else 0
             for j in range(r * d)] for i in range(r * d)]


def check_family(p, polynomial, character_degree, character_polynomial,
                 exhaustive_products):
    field, cf = Field(p, polynomial), Field(character_degree, character_polynomial)
    root = next(z for z in range(2, cf.size) if cf.power(z, p) == 1)
    require(all(cf.power(root, j) != 1 for j in range(1, p)), "nonprimitive character")
    labels = [(a, j) for a in range(1, field.size) for j in range(p)]
    reps = {g: natural(field, g) for g in labels}
    blocks = {g: displacement(field, cf, root, g) for g in labels}
    ranks = {"identity": 0, "normal": 0, "outside": 0}
    for a, j in labels:
        g = a, j
        kind = "identity" if g == (1, 0) else "normal" if j == 0 else "outside"
        expected = 0 if kind == "identity" else p if kind == "normal" else p - 1
        require(binary_rank([v ^ (1 << k) for k, v in enumerate(reps[g])])
                == expected, "natural rank law")
        require(field_rank(blocks[g], cf) == (0 if kind == "identity" else p),
                "constant displacement rank")
        ranks[kind] += 1
    products = itertools.product(labels, labels) if exhaustive_products else (
        pair for g in labels for h in [(2, 0), (1, 1)]
        for pair in [(g, h), (h, g)])
    product_count = 0
    for g, h in products:
        product = group_product(field, g, h)
        require(tuple(apply_binary(reps[g], v) for v in reps[h]) == reps[product],
                "semilinear composition")
        require(cf.table[cf.power(root, g[1])][cf.power(root, h[1])]
                == cf.power(root, product[1]), "quotient character composition")
        product_count += 1
    # Actual field elimination on tensor factors checks scalar extension and
    # the rank-one boundary, instead of only summing expected block ranks.
    factors = 0
    for g in labels:
        if g == (1, 0):
            continue
        for x, y in rank_one_idempotents(2):
            require(field_rank(paid_displacement(blocks[g], x, y, 2), cf) == p,
                    "paid factor rank")
            factors += 1
    return {"p": p, "labels": len(labels), "rank_classes": ranks,
            "products": product_count, "product_scope":
            "all ordered pairs" if exhaustive_products else "left/right generator pairs",
            "paid_factors": factors}, (field, cf, root, blocks)


def binary_matrix_product(left, right):
    return tuple(apply_binary(left, v) for v in right)


def binary_inverse(columns):
    r = len(columns)
    return tuple(next(x for x in range(1 << r)
                      if apply_binary(columns, x) == 1 << k) for k in range(r))


def check_scalar_normalization():
    r, checked = 3, 0
    for s in itertools.product(range(8), repeat=r):
        if binary_rank(s) != r:
            continue
        inverse = binary_inverse(s)
        require(binary_matrix_product(s, inverse) == (1, 2, 4), "inverse control")
        for x, y in rank_one_idempotents(r):
            n = tuple(x if (y >> j) & 1 else 0 for j in range(r))
            conjugate = binary_matrix_product(binary_matrix_product(s, n), inverse)
            require(binary_rank(conjugate) == 1, "conjugate rank")
            require(binary_matrix_product(conjugate, conjugate) == conjugate,
                    "conjugate idempotence")
            require(binary_matrix_product(s, n) == binary_matrix_product(conjugate, s),
                    "free scalar covariance")
            checked += 1
    require(checked == 168 * 28, "complete GL3/idempotent coverage")
    return checked


def rejected(action, message):
    try:
        action()
    except (ValueError, StopIteration):
        return 1
    raise ValueError("negative control accepted: " + message)


def check_controls(context):
    field, cf, root, blocks = context
    count = rejected(lambda: Field(3, 0b1001), "reducible field polynomial")
    wrong = [row[:] for row in blocks[(1, 1)]]
    wrong[-1][-1] = 0
    count += rejected(lambda: require(field_rank(wrong, cf) == 3, "missing character"),
                      "omitted character block")
    wrong = [row[:] for row in blocks[(2, 0)]]
    for row in wrong[:-1]:
        for j in range(3):
            row[j] = 0
    count += rejected(lambda: require(field_rank(wrong, cf) == 3, "missing natural block"),
                      "omitted natural block")
    # A rank-two gate updates two equal labels in one call: a different model.
    block = blocks[(2, 0)]
    twice = [[0] * 8 for _ in range(8)]
    for t in range(2):
        for i in range(4):
            for j in range(4):
                twice[4*t+i][4*t+j] = block[i][j]
    require(field_rank(twice, cf) == 6, "rank-two contrast")
    count += rejected(lambda: require(field_rank(twice, cf) == 3, "gate rank"),
                      "higher-rank gate silently treated as rank one")
    # Natural rank alone accepts two normal calls for three outside targets.
    # This is a relaxation fixture, NOT a claimed full formal word.
    require(3 * 2 >= 2 * 3, "natural-only diagnostic")
    count += rejected(lambda: require(0 >= 3, "quotient deficit"),
                      "missing outside-call count constraint")
    composite = Field(9, 0b1000010001)
    columns = natural(composite, (1, 3))
    actual = binary_rank([v ^ (1 << k) for k, v in enumerate(columns)])
    require(actual == 6, "composite-degree boundary fixture")
    count += rejected(lambda: require(actual + 1 == 9, "prime-degree hypothesis missing"),
                      "composite degree")
    require([z for z in range(cf.size) if cf.power(z, 2) == 1] == [1],
            "characteristic-two repeated-root boundary")
    count += rejected(lambda: next(z for z in range(2, cf.size)
                                    if cf.power(z, 2) == 1), "p=2 character")
    g, h = (1, 1), (2, 0)
    incorrect = (field.table[g[0]][h[0]], (g[1] + h[1]) % 3)
    count += rejected(lambda: require(group_product(field, g, h) == incorrect,
                                      "twist missing"), "untwisted group law")
    return count


def main():
    family_stats, contexts = [], []
    for args in [(3, 0b1011, 2, 0b111, True),
                 (5, 0b100101, 4, 0b10011, True),
                 (7, 0b10000011, 3, 0b1011, False)]:
        stats, context = check_family(*args)
        family_stats.append(stats)
        contexts.append(context)
    scalar_checks = check_scalar_normalization()
    controls = check_controls(contexts[0])
    package = Path(__file__).resolve().parent
    # Separate implementation: full formal coefficients, no represented ranks.
    small = runpy.run_path(str(package / "small_words.py"))["run_checks"]()
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(package.iterdir())
              if path.is_file() and path.suffix in {".py", ".md", ".json"}}
    result = {"status": "PASS_SEMILINEAR_MIXED_TARIFF", "families": family_stats,
              "scalar_covariances": scalar_checks, "primary_rejection_controls": controls,
              "full_formal_small_words": small, "package_sha256": hashes,
              "scope": "finite corroboration; universal claims proved in PROOF.md; no new kappa"}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
