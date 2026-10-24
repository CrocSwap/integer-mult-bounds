#!/usr/bin/env python3
"""Check the new conjugation compiler, not the inherited fixed-price theorem."""

import hashlib
import itertools
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(r):
    return tuple(1 << i for i in range(r))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    return tuple(xor_rows(row, b) for row in a)


def xor_rows(mask, rows):
    result = 0
    for i, row in enumerate(rows):
        if mask >> i & 1:
            result ^= row
    return result


def inverse(a):
    r = len(a)
    rows = [a[i] | (1 << (r + i)) for i in range(r)]
    for j in range(r):
        pivots = [i for i in range(j, r) if rows[i] >> j & 1]
        need(bool(pivots), "singular conjugator")
        k = pivots[0]
        rows[j], rows[k] = rows[k], rows[j]
        for i in range(r):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    result = tuple(row >> r for row in rows)
    need(multiply(a, result) == identity(r), "inverse identity")
    return result


def outer(u, v, r):
    return tuple(v if u >> i & 1 else 0 for i in range(r))


def projectors(r):
    return tuple(outer(u, v, r)
                 for u in range(1, 1 << r)
                 for v in range(1, 1 << r)
                 if (u & v).bit_count() % 2)


def adapted_basis(p):
    """Columns are an image generator followed by a basis of the kernel."""
    r = len(p)
    columns = [sum(((p[i] >> j) & 1) << i for i in range(r))
               for j in range(r)]
    u = next(column for column in columns if column)
    j = next(i for i in range(r) if u >> i & 1)
    v = p[j]
    k = next(i for i in range(r) if v >> i & 1)
    need((u & v).bit_count() % 2 == 1, "image/kernel complement")
    basis = [u] + [(1 << i) ^ (((v >> i) & 1) << k)
                   for i in range(r) if i != k]
    return tuple(sum(((column >> i) & 1) << j
                     for j, column in enumerate(basis)) for i in range(r))


def conjugator(p, n):
    c = multiply(adapted_basis(n), inverse(adapted_basis(p)))
    need(multiply(c, p) == multiply(n, c), "conjugation equation")
    return c


GROUP = tuple(itertools.permutations(range(3)))
E = GROUP.index((0, 1, 2))
A = GROUP.index((1, 0, 2))
B = GROUP.index((0, 2, 1))
Z = GROUP.index((2, 1, 0))
TABLE = tuple(tuple(GROUP.index(tuple(g[h[i]] for i in range(3)))
                    for h in GROUP) for g in GROUP)


def scalar(c):
    zero = (0,) * len(c)
    return tuple(c if g == E else zero for g in range(6))


def paid(g, p):
    result = list(scalar(identity(len(p))))
    result[E] = add(result[E], p)
    result[g] = add(result[g], p)
    return tuple(result)


def formal_multiply(x, y):
    result = [(0,) * len(x[0]) for _ in range(6)]
    for g in range(6):
        for h in range(6):
            k = TABLE[g][h]
            result[k] = add(result[k], multiply(x[g], y[h]))
    return tuple(result)


def compiled(g, n, cheapest):
    c = conjugator(cheapest, n)
    ci = inverse(c)
    result = formal_multiply(scalar(c), paid(g, cheapest))
    result = formal_multiply(result, scalar(ci))
    need(result == paid(g, n), "full formal conjugation")
    return result


def check_conjugations():
    pairs = 0
    for r in range(1, 4):
        ps = projectors(r)
        need(len(ps) == ((1 << r) - 1) * (1 << (r - 1)),
             "rank-one projector population")
        need(len(set(ps)) == len(ps), "duplicate projector")
        for p in ps:
            need(multiply(p, p) == p, "projector idempotence")
            for n in ps:
                for g in (A, B):
                    compiled(g, n, p)
                    pairs += 1
    for r in range(4, 9):
        p = outer((1 << r) - 1, 1, r)
        for i in range(r):
            n = outer(1 << i, 1 << i, r)
            for g in (A, B):
                compiled(g, n, p)
                pairs += 1
    return pairs


def price_table(ps, case):
    """Fixed displayed-projector costs; gauges are separately free."""
    return {g: {p: (0 if case == 0 else 1 + (i + case * g) % 9)
                for i, p in enumerate(ps)} for g in (A, B)}


def swap_target(r, t):
    p = tuple(1 << i if i < t else 0 for i in range(r))
    return paid(Z, p)


def check_tariff_compilations():
    endpoints = 0
    for r in range(1, 4):
        ps = projectors(r)
        for case in range(4):
            prices = price_table(ps, case)
            cheapest = {g: min(ps, key=prices[g].__getitem__) for g in (A, B)}
            minimum = {g: prices[g][cheapest[g]] for g in (A, B)}
            first, second = sorted((A, B), key=minimum.__getitem__)
            for t in range(r + 1):
                result, cost = scalar(identity(r)), 0
                for i in range(t):
                    n = outer(1 << i, 1 << i, r)
                    for g in (first, second, first):
                        result = formal_multiply(result, compiled(g, n, cheapest[g]))
                        cost += prices[g][cheapest[g]]
                need(result == swap_target(r, t), "whole dirty endpoint")
                expected = t * (minimum[A] + minimum[B] + min(minimum.values()))
                need(cost == expected, "collapsed tariff attainment")
                endpoints += 1
    return endpoints


def check_boundaries():
    r = 2
    p = outer(3, 1, r)
    n = outer(1, 1, r)
    target = swap_target(r, 1)
    need(p != n, "noncoordinate cheap projector")
    result = scalar(identity(r))
    for g in (A, B, A):
        result = formal_multiply(result, compiled(g, n, p))
    need(result == target, "zero-price compiled target")
    # Without gauges, every zero-price word is in this six-state subgroup.
    zero_states = {paid(g, p) for g in range(6)}
    for state in zero_states:
        for g in (A, B):
            need(formal_multiply(state, paid(g, p)) in zero_states,
                 "zero-price state closure without gauges")
    need(target not in zero_states, "restricted-gauge counterexample")
    c = conjugator(p, n)
    broken = formal_multiply(scalar(c), paid(A, p))
    need(broken != paid(A, n), "missing inverse-gauge rejection")
    return {"no_gauge_zero_states": len(zero_states), "controls": 2}


def main():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    manifest = json.loads((package / "SOURCES.json").read_text())
    pins = [row for row in manifest["files"] if row["usage"] == "input"]
    need(len(pins) == 1, "one inherited theorem input")
    source = pins[0]
    source_bytes = (root / source["path"]).read_bytes()
    need(hashlib.sha256(source_bytes).hexdigest() == source["sha256"],
         "inherited theorem source hash")
    receipt = {"conjugation_checks": check_conjugations(),
               "tariff_endpoints": check_tariff_compilations(),
               **check_boundaries(), "claim_type": "scoped proof"}
    receipt["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                         for name in ("verify.py", "README.md", "SOURCES.json")}
    receipt["source_sha256"] = source["sha256"]
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_PROJECTOR_PRICE_ORBIT_COLLAPSE")


if __name__ == "__main__":
    main()
