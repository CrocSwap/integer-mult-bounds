#!/usr/bin/env python3
"""Exact new-pencil checks; no predecessor executable is imported."""

import hashlib
import itertools
import json
from pathlib import Path


MONOMIALS = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
ZERO = (0,) * 6
ONE = (1, 0, 0, 0, 0, 0)
X = (0, 1, 0, 0, 0, 0)
Y = (0, 0, 1, 0, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b, p):
    return tuple((a[i] + b[i]) % p for i in range(6))


def scale(a, scalar, p):
    return tuple(scalar * value % p for value in a)


def multiply(a, b, p):
    result = [0] * 6
    for i, (ax, ay) in enumerate(MONOMIALS):
        for j, (bx, by) in enumerate(MONOMIALS):
            power = (ax + bx, ay + by)
            if sum(power) <= 2:
                result[MONOMIALS.index(power)] += a[i] * b[j]
    return tuple(value % p for value in result)


def matmul(a, b, p):
    return tuple(add(multiply(a[2*i], b[j], p),
                     multiply(a[2*i+1], b[2+j], p), p)
                 for i in range(2) for j in range(2))


def target(coefficients, p):
    require(len(coefficients) == 12, "twelve quadratic coefficients required")
    require(p in (2, 3, 5, 7), "unsupported prime field")
    require(all(type(c) is int and 0 <= c < p for c in coefficients),
            "noncanonical field coefficient")
    entries = tuple((0, 0, 0, *coefficients[3*i:3*i+3]) for i in range(4))
    return (add(X, entries[0], p), entries[1], entries[2],
            add(Y, entries[3], p))


def construct(m, p):
    a, b, c, d = m
    gamma, delta = b[5], c[3]
    if gamma == 0:
        s = (0, b[3], b[4], 0, 0, 0)
        return ((a, ZERO, c, ONE), (ONE, s, ZERO, d))
    if delta == 0:
        r = (0, c[4], c[5], 0, 0, 0)
        return ((ONE, b, ZERO, d), (a, ZERO, r, ONE))
    s = (0, b[3], b[4], 0, 0, 0)
    return ((ONE, scale(Y, gamma, p), ZERO, ONE),
            (a, ZERO, c, ONE), (ONE, s, ZERO, d))


def check_word(m, word, p):
    product = (ONE, ZERO, ZERO, ONE)
    for factor in word:
        first = (factor[0] != ONE or factor[2] != ZERO)
        second = (factor[1] != ZERO or factor[3] != ONE)
        require(first != second, "factor must change exactly one scalar column")
        product = matmul(product, factor, p)
    require(product == m, "literal paid word has wrong endpoint")


def binary_tables():
    elements = tuple(tuple((a >> i) & 1 for i in range(6)) for a in range(64))
    table = tuple(tuple(sum(c << i for i, c in enumerate(multiply(a, b, 2)))
                        for b in elements) for a in elements)
    ideals = tuple(frozenset(row) for row in table)
    gl = tuple(m for m in itertools.product(range(2), repeat=4)
               if (m[0]*m[3] - m[1]*m[2]) % 2 == 1)
    require(len(gl) == 6 and len(ideals) == 64, "binary table bounds")
    return table, ideals, gl


def binary_matmul(a, b, table):
    return tuple(table[a[2*i]][b[j]] ^ table[a[2*i+1]][b[2+j]]
                 for i in range(2) for j in range(2))


def binary_two_factor(m, table, ideals, gl):
    # Literal cited criterion: some GMH has N12 in the principal ideal N11 R.
    # This scans every free endpoint; it does not use the new coefficient test.
    for g in gl:
        gm = binary_matmul(g, m, table)
        for h in gl:
            n = binary_matmul(gm, h, table)
            if n[1] in ideals[n[0]]:
                return True
    return False


def binary_action(m, v, table):
    return (table[m[0]][v[0]] ^ table[m[1]][v[1]],
            table[m[2]][v[0]] ^ table[m[3]][v[1]])


def pack(m):
    return tuple(sum(c << i for i, c in enumerate(entry)) for entry in m)


def binary_census():
    table, ideals, gl = binary_tables()
    counts = {2: 0, 3: 0}
    basis = tuple((1 << i, 0) for i in range(6)) + tuple(
        (0, 1 << i) for i in range(6))
    digest = hashlib.sha256()
    actions = 0
    for coefficients in itertools.product(range(2), repeat=12):
        m = target(coefficients, 2)
        word = construct(m, 2)
        encoded = pack(m)
        predicted = coefficients[5] == 0 or coefficients[6] == 0
        require(binary_two_factor(encoded, table, ideals, gl) == predicted,
                "new cost test disagrees with complete free-chart criterion")
        require(len(word) == (2 if predicted else 3), "wrong paid length")
        check_word(m, word, 2)
        packed_word = tuple(pack(factor) for factor in word)
        for v in basis:
            state = v
            for factor in reversed(packed_word):
                state = binary_action(factor, state, table)
            require(state == binary_action(encoded, v, table), "basis action")
            actions += 1
        counts[len(word)] += 1
        digest.update(bytes((*encoded, len(word))))
    require(counts == {2: 3072, 3: 1024}, "binary closed-form count")
    return {"targets": sum(counts.values()), "cost_counts": counts,
            "basis_actions": actions, "records_sha256": digest.hexdigest()}


def odd_samples():
    report = {}
    for p in (3, 5, 7):
        coefficients = {(0,) * 12}
        for i in range(12):
            for value in range(1, p):
                row = [0] * 12
                row[i] = value
                coefficients.add(tuple(row))
        for gamma, delta in itertools.product(range(p), repeat=2):
            row = [(i*i + 3*i + gamma + 2*delta) % p for i in range(12)]
            row[5], row[6] = gamma, delta
            coefficients.add(tuple(row))
        counts = {2: 0, 3: 0}
        for row in sorted(coefficients):
            m = target(row, p)
            word = construct(m, p)
            check_word(m, word, p)
            counts[len(word)] += 1
        require(sum(counts.values()) == len(coefficients), "sample accounting")
        report[str(p)] = {"targets": len(coefficients), "word_lengths": counts}
    return report


def controls():
    row = [0] * 12
    row[5], row[6] = 1, 1
    m = target(row, 3)
    word = construct(m, 3)
    rejected = 0
    mutants = (word[1:], tuple(reversed(word)), word[:1] + word[2:], word[:2])
    for mutant in mutants:
        try:
            check_word(m, mutant, 3)
        except ValueError:
            rejected += 1
    require(rejected == 4, "omission or order mutant survived")
    wrong_sign = ((ONE, scale(Y, -1, 3), ZERO, ONE), *word[1:])
    try:
        check_word(m, wrong_sign, 3)
    except ValueError:
        rejected += 1
    require(rejected == 5, "odd-characteristic sign mutant survived")
    for bad, p in (((0,) * 11, 2), ((0,) * 12, 4), ((3,) * 12, 3)):
        try:
            target(bad, p)
        except ValueError:
            rejected += 1
    require(rejected == 8, "input boundary mutant survived")
    require(multiply(X, Y, 2) != ZERO, "cube-zero differs from square-zero")
    require(multiply(multiply(X, Y, 2), X, 2) == ZERO, "cubic truncation")
    return rejected


def main():
    result = {"binary": binary_census(), "odd_field_samples": odd_samples(),
              "rejecting_controls": controls()}
    package = Path(__file__).resolve().parent
    result["files_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                     "VERIFY.json", "verify.py")
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_DISTINCT_PENCIL_QUADRATIC_LIFTS no_new_kappa")


if __name__ == "__main__":
    main()
