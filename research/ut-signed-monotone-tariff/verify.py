#!/usr/bin/env python3
"""Exact finite corroboration of the written signed monotone UT tariff."""
from __future__ import annotations

import argparse
import hashlib
import itertools as it
import json
from pathlib import Path
import random

Poly = frozenset[int]
Group = tuple[tuple[int, ...], ...]
Formal = dict[Group, int]
ZERO: Poly = frozenset()
ONE: Poly = frozenset({0})


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(d: int) -> Group:
    need(type(d) is int and 2 <= d <= 6, "dimension outside replay bound")
    return tuple(tuple(int(i == j) for j in range(d)) for i in range(d))


def group_mul(a: Group, b: Group) -> Group:
    d = len(a)
    need(len(b) == d, "group dimensions differ")
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(d))
                       for j in range(d)) for i in range(d))


def root(d: int, label: int, sign: int) -> Group:
    a = [list(row) for row in identity(d)]
    need(0 <= label < d - 1 and sign in (-1, 1), "invalid root letter")
    a[label][label + 1] = sign
    return tuple(tuple(row) for row in a)


def binary_identity(r: int) -> int:
    need(type(r) is int and 1 <= r <= 4, "roles outside replay bound")
    return sum(1 << (i * r + i) for i in range(r))


def binary_mul(a: int, b: int, r: int) -> int:
    out = 0
    for i, j in it.product(range(r), repeat=2):
        value = sum(((a >> (i * r + k)) & 1) *
                    ((b >> (k * r + j)) & 1) for k in range(r)) & 1
        out |= value << (i * r + j)
    return out


def projectors(r: int) -> tuple[tuple[int, int, int], ...]:
    binary_identity(r)
    out = []
    for x, y in it.product(range(1, 1 << r), repeat=2):
        if (x & y).bit_count() % 2:
            n = sum(1 << (i * r + j) for i, j in it.product(range(r), repeat=2)
                    if (x >> i) & (y >> j) & 1)
            need(binary_mul(n, n, r) == n, "projector is not idempotent")
            out.append((x, y, n))
    return tuple(out)


def formal_gate(g: Group, n: int, r: int) -> Formal:
    e = identity(len(g))
    need(g != e, "identity is not a paid root")
    return {g: n, e: binary_identity(r) ^ n}


def formal_mul(a: Formal, b: Formal, r: int) -> Formal:
    need(len(a) <= 4096 and len(b) <= 4096, "formal support limit")
    out: Formal = {}
    for ga, ma in a.items():
        for gb, mb in b.items():
            coefficient = binary_mul(ma, mb, r)
            if coefficient:
                g = group_mul(ga, gb)
                out[g] = out.get(g, 0) ^ coefficient
    return {g: m for g, m in out.items() if m}


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: set[int] = set()
    for x, y in it.product(a, b):
        out.symmetric_difference_update({x + y})
    return frozenset(out)


def projection(a: Formal, r: int, label: int, sign: int = 1):
    out = [[set() for _ in range(r)] for _ in range(r)]
    for g, matrix in a.items():
        exponent = sign * g[label][label + 1]
        for i, j in it.product(range(r), repeat=2):
            if (matrix >> (i * r + j)) & 1:
                out[i][j].symmetric_difference_update({exponent})
    return tuple(tuple(frozenset(p) for p in row) for row in out)


def delta(a) -> int:
    """Leibniz determinants of every square minor, including the empty one."""
    r = len(a)
    need(1 <= r <= 4, "minor dimension outside replay bound")
    answer = 0
    for k in range(1, r + 1):
        for rows, columns in it.product(it.combinations(range(r), k), repeat=2):
            determinant = ZERO
            for order in it.permutations(columns):
                term = ONE
                for i, j in zip(rows, order):
                    term = poly_mul(term, a[i][j])
                determinant = determinant.symmetric_difference(term)
            if determinant:
                answer = max(answer, max(determinant))
    return answer


def gate_checks() -> dict[str, int]:
    count = total = 0
    for r in range(1, 5):
        for _, _, n in projectors(r):
            total += 1
            for sign in (-1, 1):
                a = formal_gate(root(2, 0, sign), n, r)
                need(delta(projection(a, r, 0)) == int(sign == 1), "positive gate degree")
                need(delta(projection(a, r, 0, -1)) == int(sign == -1), "negative gate degree")
                count += 1
    need(total == 155, "projector inventory")
    return {"projectors": total, "signed_gate_checks": count}


def mixed_checks() -> dict[str, int]:
    alphabet = [(label, sign, formal_gate(root(3, label, sign), n, 2))
                for label, sign in it.product(range(2), (-1, 1))
                for _, _, n in projectors(2)]
    words = degree_checks = 0
    for letters in it.product(alphabet, repeat=3):
        a = {identity(3): binary_identity(2)}
        for _, _, gate in letters:
            a = formal_mul(a, gate, 2)
        for label, sign in it.product(range(2), (-1, 1)):
            bill = sum(q == label and s == sign for q, s, _ in letters)
            need(delta(projection(a, 2, label, sign)) <= bill, "mixed word exceeds bill")
            degree_checks += 1
        words += 1
    need(words == 24 ** 3, "incomplete three-letter domain")
    return {"mixed_three_call_words": words, "mixed_degree_checks": degree_checks}


def free_mixing_checks() -> dict[str, int]:
    e = identity(2)
    gl2 = (1 | 8, 2 | 4, 1 | 2 | 8, 1 | 4 | 8, 1 | 2 | 4, 2 | 4 | 8)
    checks = 0
    for _, _, n in projectors(2):
        gate = formal_gate(root(2, 0, 1), n, 2)
        for left, right in it.product(gl2, repeat=2):
            a = formal_mul(formal_mul({e: left}, gate, 2), {e: right}, 2)
            for sign in (-1, 1):
                need(delta(projection(a, 2, 0, sign)) == int(sign == 1), "free mixing changes degree")
                checks += 1
    return {"free_mixing_checks": checks}


def endpoint(words, d: int, r: int) -> Formal:
    out: Formal = {}
    for role in range(r):
        g = identity(d)
        if role < len(words):
            for label, sign in words[role]:
                g = group_mul(g, root(d, label, sign))
        out[g] = out.get(g, 0) ^ (1 << (role * r + role))
    return out


def witness(words, d: int, r: int, omit: int = -1) -> Formal:
    a = {identity(d): binary_identity(r)}
    index = 0
    for role, word in enumerate(words):
        for label, sign in word:
            if index != omit:
                gate = formal_gate(root(d, label, sign), 1 << (role * r + role), r)
                a = formal_mul(a, gate, r)
            index += 1
    return a


def monotone_checks() -> dict[str, int]:
    rng = random.Random(21163316)
    targets = omissions = 0
    for d, m, n, spectators in it.product(range(3, 6), range(1, 4), range(1, 4), range(3)):
        a = [(0, 1)] * m + [(1, -1)] * n
        b = [(1, 1)] * n + [(0, -1)] * m
        words, r = [a, b], 2 + spectators
        target = endpoint(words, d, r)
        need(witness(words, d, r) == target, "inverse-pair formal endpoint")
        ga = next(iter(endpoint([a], d, 1)))
        gb = next(iter(endpoint([b], d, 1)))
        need(all(ga[label][label + 1] + gb[label][label + 1] == 0 for label in range(2)),
             "aggregate character should cancel")
        for index in range(2 * (m + n)):
            need(witness(words, d, r, index) != target, "omitted paid factor accepted")
            omissions += 1
        targets += 1
    for d, r, _ in it.product(range(2, 7), range(1, 5), range(10)):
        words = []
        for _role in range(r):
            word = [(label, rng.choice((-1, 1)), rng.randrange(3)) for label in range(d - 1)]
            letters = [(label, sign) for label, sign, count in word for _ in range(count)]
            rng.shuffle(letters)
            words.append(letters)
        target = endpoint(words, d, r)
        need(witness(words, d, r) == target, "monotone formal endpoint")
        for label, sign in it.product(range(d - 1), (-1, 1)):
            bill = sum(q == label and s == sign for word in words for q, s in word)
            need(delta(projection(target, r, label, sign)) == bill, "endpoint tariff not sharp")
        targets += 1
    return {"monotone_target_fixtures": targets, "single_omission_controls": omissions}


def permute_bits(value: int, g: Group, q: int) -> int:
    d = len(g)
    size = q ** d
    need(d == 3 and q == 3 and 0 <= value < (1 << size), "literal action outside bound")
    out = 0
    for index, v in enumerate(it.product(range(q), repeat=d)):
        if (value >> index) & 1:
            w = tuple(sum(g[i][j] * v[j] for j in range(d)) % q for i in range(d))
            target = sum(w[i] * q ** (d - i - 1) for i in range(d))
            out ^= 1 << target
    return out


def literal_gate(state, g: Group, x: int, y: int):
    total = 0
    for i, value in enumerate(state):
        if (y >> i) & 1:
            total ^= value
    change = permute_bits(total, g, 3) ^ total
    return tuple(value ^ (change if (x >> i) & 1 else 0) for i, value in enumerate(state))


def formal_action(a: Formal, state):
    r = len(state)
    out = [0] * r
    for g, matrix in a.items():
        for i, j in it.product(range(r), repeat=2):
            if (matrix >> (i * r + j)) & 1:
                out[i] ^= permute_bits(state[j], g, 3)
    return tuple(out)


def literal_checks() -> dict[str, int]:
    rng = random.Random(19112716)
    ps = projectors(3)
    basis = samples = 0
    for _case in range(16):
        letters = [(rng.randrange(2), rng.choice((-1, 1)), rng.choice(ps)) for _ in range(5)]
        a = {identity(3): binary_identity(3)}
        for label, sign, (_, _, n) in letters:
            a = formal_mul(a, formal_gate(root(3, label, sign), n, 3), 3)
        states = [tuple((1 << (j % 27)) if i == j // 27 else 0 for i in range(3))
                  for j in range(81)]
        states += [tuple(rng.getrandbits(27) for _ in range(3)) for _ in range(20)]
        for state in states:
            out = state
            for label, sign, (x, y, _) in reversed(letters):
                out = literal_gate(out, root(3, label, sign), x, y)
            need(out == formal_action(a, state), "literal arbitrary-dirty action mismatch")
        basis += 81
        samples += 20
    return {"literal_basis_inputs": basis, "literal_dirty_samples": samples}


def controls() -> dict[str, int]:
    central = [(0, 1), (1, 1), (0, -1), (1, -1)]
    a = endpoint([central], 3, 1)
    need(a != {identity(3): 1}, "commutator control collapsed")
    need(all(delta(projection(a, 1, label, sign)) == 0
             for label, sign in it.product(range(2), (-1, 1))), "central control should be invisible")
    pair = [[(0, 1), (1, -1)], [(1, 1), (0, -1)]]
    wrong = [[(0, 1), (1, -1)], [(0, -1), (1, 1)]]
    need(endpoint(pair, 3, 2) != endpoint(wrong, 3, 2), "noncommuting order control")
    need(delta(((frozenset({2}), ZERO), (ZERO, frozenset({-2})))) == 2,
         "full determinant degree substituted for all-minor degree")
    invalid = 0
    for d, label, sign in ((1, 0, 1), (7, 0, 1), (3, 2, 1), (3, -1, 1), (3, 0, 0)):
        try:
            root(d, label, sign)
        except ValueError:
            invalid += 1
    need(invalid == 5, "invalid root accepted")
    return {"scope_and_order_controls": 3, "invalid_input_controls": invalid}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new source-bound receipt outside the checkout")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt:
        destination = args.receipt.resolve()
        need(package.parent.parent not in destination.parents, "receipt must be outside checkout")
        need(not destination.exists(), "receipt destination already exists")
    result = {}
    for part in (gate_checks(), mixed_checks(), free_mixing_checks(), monotone_checks(),
                 literal_checks(), controls()):
        result.update(part)
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report = {"claim_type": "scoped written proof with finite corroboration", "checks": result,
              "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                                for name in files}}
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            need(stream.write(encoded) == len(encoded), "incomplete receipt write")
    print(encoded, end="")
    print("PASS_UT_SIGNED_MONOTONE_TARIFF no_new_kappa")


if __name__ == "__main__":
    main()
