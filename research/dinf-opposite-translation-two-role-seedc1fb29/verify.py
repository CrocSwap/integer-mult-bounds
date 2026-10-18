#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exhaust the radius-three word ball for an opposite-translation D_infinity target."""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter


# D_infinity = Z semidirect C2, with (k,e) acting as x -> (-1)^e*x + k.
# Multiplication is composition: (k,e)(l,f)=(k+(-1)^e*l,e+f mod 2).
GroupElement = tuple[int, int]
Polynomial = dict[GroupElement, int]
Matrix = tuple[tuple[Polynomial, ...], ...]
ZERO: Polynomial = {}
ONE: Polynomial = {(0, 0): 1}
R: GroupElement = (0, 1)
S: GroupElement = (1, 1)
T: GroupElement = (-1, 0)      # r*s
T_INV: GroupElement = (1, 0)   # s*r


def need(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def group_mul(a: GroupElement, b: GroupElement) -> GroupElement:
    k, e = a
    ell, f = b
    return (k + (-1 if e else 1) * ell, (e + f) & 1)


def reduced_word(word: tuple[str, ...]) -> tuple[str, ...]:
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def normal_word(g: GroupElement) -> tuple[str, ...]:
    k, e = g
    if k > 0:
        word = ("s", "r") * k
    elif k < 0:
        word = ("r", "s") * (-k)
    else:
        word = ()
    return reduced_word(word + (("r",) if e else ()))


def poly_xor(a: Polynomial, b: Polynomial) -> Polynomial:
    out = dict(a)
    for word, coefficient in b.items():
        out[word] = out.get(word, 0) ^ coefficient
        if not out[word]:
            del out[word]
    return out


def poly_mul(a: Polynomial, b: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for x, ax in a.items():
        for y, by in b.items():
            z = group_mul(x, y)
            out[z] = out.get(z, 0) ^ (ax & by)
            if not out[z]:
                del out[z]
    return out


def matrix_identity() -> Matrix:
    return ((dict(ONE), dict(ZERO)), (dict(ZERO), dict(ONE)))


def matrix_mul(a: Matrix, b: Matrix) -> Matrix:
    rows = []
    for i in range(2):
        row = []
        for j in range(2):
            value: Polynomial = {}
            for k in range(2):
                value = poly_xor(value, poly_mul(a[i][k], b[k][j]))
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


def rank_one_idempotents() -> tuple[tuple[int, int, int, int], ...]:
    nonzero = [(1, 0), (0, 1), (1, 1)]
    found = set()
    for u in nonzero:
        for v in nonzero:
            if (u[0] * v[0] + u[1] * v[1]) & 1:
                found.add((u[0] * v[0], u[0] * v[1], u[1] * v[0], u[1] * v[1]))
    return tuple(sorted(found))


def factor(n: tuple[int, int, int, int], g: GroupElement) -> Matrix:
    out = []
    for i in range(2):
        row = []
        for j in range(2):
            base = {(0, 0): int(i == j)}
            if n[2 * i + j]:
                base = poly_xor(base, ONE)
                base = poly_xor(base, {g: 1})
            row.append(base)
        out.append(tuple(row))
    return tuple(out)


def target_matrix(first: GroupElement = T, second: GroupElement = T_INV) -> Matrix:
    return (({first: 1}, dict(ZERO)), (dict(ZERO), {second: 1}))


def canonical_matrix(m: Matrix) -> list[list[list[list[int]]]]:
    return [
        [
            [[k, e, coefficient] for (k, e), coefficient in sorted(m[i][j].items())]
            for j in range(2)
        ]
        for i in range(2)
    ]


def apply_word(generators: tuple[Matrix, ...], word: tuple[int, ...]) -> Matrix:
    value = matrix_identity()
    for index in word:
        value = matrix_mul(value, generators[index])
    return value


def direct_word(
    factors: dict[tuple[tuple[int, int, int, int], GroupElement], Matrix],
) -> tuple[tuple[int, int, int, int], ...]:
    e11 = (1, 0, 0, 0)
    e22 = (0, 0, 0, 1)
    labels = [(e11, R), (e11, S), (e22, S), (e22, R)]
    keys = tuple(factors)
    return tuple(keys.index(item) for item in labels)


def main() -> None:
    # Relation and noncommutation controls for the faithful normal form.
    identity = (0, 0)
    need(group_mul(R, R) == identity and group_mul(S, S) == identity, "reflection involutions")
    need(group_mul(R, S) == T and group_mul(S, R) == T_INV, "translation orientation")
    need(T != T_INV and group_mul(T, T_INV) == identity, "torsion-free opposite translations")
    for ka in range(-4, 5):
        for ea in range(2):
            for kb in range(-4, 5):
                for eb in range(2):
                    a, b = (ka, ea), (kb, eb)
                    need(reduced_word(normal_word(a) + normal_word(b)) ==
                         normal_word(group_mul(a, b)), "independent alternating-word product control")

    idempotents = rank_one_idempotents()
    need(len(idempotents) == 6, "complete rank-one idempotent alphabet in M2(F2)")
    brute = set()
    for a, b, c, d in itertools.product((0, 1), repeat=4):
        square = ((a * a + b * c) & 1, (a * b + b * d) & 1,
                  (c * a + d * c) & 1, (c * b + d * d) & 1)
        determinant = (a * d + b * c) & 1
        if square == (a, b, c, d) and determinant == 0 and (a or b or c or d):
            brute.add((a, b, c, d))
    need(brute == set(idempotents), "independent exhaustive idempotent census")
    for a, b, c, d in idempotents:
        # N^2=N and rank(N)=1, checked directly over F2.
        square = ((a * a + b * c) & 1, (a * b + b * d) & 1,
                  (c * a + d * c) & 1, (c * b + d * d) & 1)
        need(square == (a, b, c, d), "idempotent enumeration control")
        need((a * d - b * c) & 1 == 0, "rank-one determinant")

    factor_map = {}
    for g in (R, S):
        for n in idempotents:
            factor_map[(n, g)] = factor(n, g)
    labels = tuple(factor_map)
    generators = tuple(factor_map[label] for label in labels)
    need(len(generators) == 12, "complete 12-factor alphabet")
    need(len({json.dumps(canonical_matrix(g), separators=(",", ":")) for g in generators}) == 12,
         "distinct generator matrices")

    target = target_matrix()
    level = [matrix_identity()]
    counts = []
    hashes = []
    supports = []
    total = 0
    for depth in range(4):
        counts.append(len(level))
        need(counts[-1] == 12 ** depth, f"complete depth-{depth} word count")
        digest = hashlib.sha256()
        support_histogram = Counter()
        hits = 0
        next_level = []
        for prefix_index, matrix in enumerate(level):
            encoded = json.dumps(canonical_matrix(matrix), separators=(",", ":")).encode()
            digest.update(prefix_index.to_bytes(4, "big"))
            digest.update(encoded)
            support_histogram[sum(len(cell) for row in matrix for cell in row)] += 1
            if matrix == target:
                hits += 1
            if depth < 3:
                for generator in generators:
                    next_level.append(matrix_mul(matrix, generator))
        total += len(level)
        hashes.append(digest.hexdigest())
        supports.append({str(k): support_histogram[k] for k in sorted(support_histogram)})
        need(hits == 0, f"target absent at length {depth}")
        level = next_level
    need(total == 1885, "complete radius-three census size")

    direct = direct_word(factor_map)
    need(len(direct) == 4 and apply_word(generators, direct) == target,
         "four-call direct positive control")
    mutated = list(direct)
    mutated[-1] = labels.index(((0, 0, 0, 1), S))
    need(apply_word(generators, tuple(mutated)) != target,
         "wrong-final-reflection negative control")
    need(apply_word(generators, direct[:-1]) != target,
         "dropped-call negative control")

    certificate = {
        "depth_counts": counts,
        "depth_sha256": hashes,
        "support_histograms": supports,
        "target_hits": [0, 0, 0, 0],
        "direct_factor_indices": list(direct),
        "enumerated_total": total,
    }
    print("CERTIFICATE", json.dumps(certificate, sort_keys=True, separators=(",", ":")))
    print("PASS_DINF_OPPOSITE_TRANSLATION_RADIUS3", f"alphabet={len(generators)}",
          f"words={total}", "radius=3", "direct=4", "saving_if_found=25%",
          "target=diag([rs],[sr])", "negative=scoped_to_D_infinity_F2_model")


if __name__ == "__main__":
    main()
