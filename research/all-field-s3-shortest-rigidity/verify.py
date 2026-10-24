#!/usr/bin/env python3
"""Exact signed coefficients and a new ternary-domain census. Read-only."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


GROUP = tuple(permutations(range(3)))
IDENTITY = (0, 1, 2)
S = (1, 0, 2)
T = (0, 2, 1)
Z = (2, 1, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def compose(g, h):
    return tuple(g[h[i]] for i in range(3))


def symbolic(labels):
    """Expand with integer coefficients and noncommuting A,B,C."""
    terms = {(IDENTITY, ()): 1}
    for variable, label in enumerate(labels):
        out = {}
        for (group, word), coefficient in terms.items():
            for address, suffix, sign in (
                (IDENTITY, (), 1),
                (IDENTITY, (variable,), -1),
                (label, (variable,), 1),
            ):
                key = (compose(group, address), word + suffix)
                out[key] = out.get(key, 0) + sign * coefficient
        terms = {key: value for key, value in out.items() if value}
    return {g: {w: c for (h, w), c in terms.items() if h == g} for g in GROUP}


def check_symbolic():
    a, b, c = (0,), (1,), (2,)
    ab, ac, bc, abc = (0, 1), (0, 2), (1, 2), (0, 1, 2)
    expected = {
        IDENTITY: {(): 1, a: -1, b: -1, c: -1, ab: 1, bc: 1, ac: 2, abc: -2},
        S: {a: 1, c: 1, ab: -1, bc: -1, ac: -2, abc: 2},
        T: {b: 1, ab: -1, bc: -1, abc: 1},
        compose(S, T): {ab: 1, abc: -1},
        compose(T, S): {bc: 1, abc: -1},
        Z: {abc: 1},
    }
    need(symbolic((S, T, S)) == expected, "signed integer coefficient table")
    swapped = {compose(Z, compose(g, Z)): v for g, v in expected.items()}
    need(symbolic((T, S, T)) == swapped, "opposite alternating coefficient table")
    for labels in product((S, T), repeat=3):
        top = symbolic(labels)[Z]
        need(bool(top) == (labels in ((S, T, S), (T, S, T))), "label support")
    return 8


def identity(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def add(a, b, p):
    return tuple((x + y) % p if p else x + y for x, y in zip(a, b, strict=True))


def scale(a, scalar, p):
    return tuple((scalar * x) % p if p else scalar * x for x in a)


def multiply(a, b, n, p):
    out = tuple(sum(a[i*n+k] * b[k*n+j] for k in range(n))
                for i in range(n) for j in range(n))
    return tuple(x % p for x in out) if p else out


def factor(label, a, n, p):
    return {IDENTITY: add(identity(n), scale(a, -1, p), p), label: a}


def formal_multiply(left, right, n, p):
    out = {}
    zero = (0,) * (n*n)
    for g, a in left.items():
        for h, b in right.items():
            label = compose(g, h)
            out[label] = add(out.get(label, zero), multiply(a, b, n, p), p)
    return {g: a for g, a in out.items() if any(a)}


def word(labels, matrices, n, p):
    out = {IDENTITY: identity(n)}
    for label, matrix in zip(labels, matrices, strict=True):
        out = formal_multiply(out, factor(label, matrix, n, p), n, p)
    return out


def rank_one_ternary():
    vectors = tuple(v for v in product(range(3), repeat=2) if any(v))
    matrices = {tuple(x*y % 3 for x in u for y in v) for u in vectors for v in vectors}
    need(len(matrices) == 32, "ternary rank-one matrix enumeration")
    return tuple(sorted(matrices))


def ternary_census():
    matrices = rank_one_ternary()
    targets = tuple(a for a in matrices if multiply(a, a, 2, 3) == a)
    need(len(targets) == 12, "ternary target enumeration")
    target_lookup = {
        tuple(sorted(factor(Z, a, 2, 3).items())): a for a in targets
    }
    hits = {a: 0 for a in targets}
    words = 0
    for labels in product((S, T), repeat=3):
        factors = tuple(tuple(factor(g, a, 2, 3) for a in matrices) for g in labels)
        for i, a in enumerate(matrices):
            for j, b in enumerate(matrices):
                prefix = formal_multiply(factors[0][i], factors[1][j], 2, 3)
                for k, c in enumerate(matrices):
                    endpoint = formal_multiply(prefix, factors[2][k], 2, 3)
                    target = target_lookup.get(tuple(sorted(endpoint.items())))
                    if target is not None:
                        need(a == b == c == target, "unexpected nonrigid ternary word")
                        need(labels in ((S, T, S), (T, S, T)), "nonalternating hit")
                        hits[target] += 1
                    words += 1
    need(set(hits.values()) == {2}, "two words per ternary target")
    need(words == 8 * 32**3, "complete census coverage")
    return {"words": words, "targets": len(targets), "hits": sum(hits.values())}


def regular_matrix(formal, n):
    """Independent literal left regular action, without formal multiplication."""
    size = 6*n
    rows = [[0] * size for _ in range(size)]
    for g, a in formal.items():
        for column, h in enumerate(GROUP):
            row = GROUP.index(compose(g, h))
            for i in range(n):
                for j in range(n):
                    rows[6*i+row][6*j+column] += a[n*i+j]
    return tuple(x for row in rows for x in row)


def rational_and_controls():
    e = (Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2))
    need(multiply(e, e, 2, 0) == e, "rational oblique target")
    factors = tuple(regular_matrix(factor(g, e, 2, 0), 2) for g in (S, T, S))
    actual = multiply(multiply(factors[0], factors[1], 12, 0), factors[2], 12, 0)
    need(actual == regular_matrix(factor(Z, e, 2, 0), 2), "rational regular endpoint")
    zero, coord = (0, 0, 0, 0), (1, 0, 0, 0)
    nilpotent, singular = (0, 1, 0, 0), (2, 0, 0, 0)
    controls = (
        ((S, T, S), (coord, nilpotent, coord)),
        ((S, T, S), (coord, singular, coord)),
        ((S, S, T), (coord, coord, coord)),
        ((S, T, S), (coord, coord, zero)),
    )
    for labels, couplings in controls:
        need(word(labels, couplings, 2, 3) != factor(Z, coord, 2, 3), "invalid word accepted")
    # Rank two invalidates rigidity: scratch actions cancel.
    full = identity(2)
    need(word((S, T, S), (full, coord, full), 2, 3) == factor(Z, coord, 2, 3),
         "higher-rank counterexample")
    # Correct first output alone does not restore the dirty spectator.
    leaking = (1, 0, 1, 0)
    endpoint = word((S, T, S), (leaking, leaking, leaking), 2, 3)
    target = factor(Z, coord, 2, 3)
    need(all(endpoint.get(g, zero)[:2] == target.get(g, zero)[:2] for g in GROUP),
         "data-only false-positive fixture")
    need(endpoint != target, "dirty spectator leak missed")
    # Arbitrary nilpotents are involutions only in characteristic two.
    twice = word((S, S), (nilpotent, nilpotent), 2, 3)
    need(twice != {IDENTITY: identity(2)}, "binary involution premise leaked")
    return 7


def main():
    labels = check_symbolic()
    census = ternary_census()
    controls = rational_and_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"status": "PASS_ALL_FIELD_S3_RIGIDITY", "symbolic_label_words": labels,
               "ternary": census, "control_groups": controls, "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
