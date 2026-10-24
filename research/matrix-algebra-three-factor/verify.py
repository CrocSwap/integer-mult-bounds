#!/usr/bin/env python3
"""Bounded constructive corroboration of the all-target three-factor theorem."""

import hashlib
import itertools
import json
from pathlib import Path
import random


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def add(a, b, q):
    return tuple((x + y) % q for x, y in zip(a, b, strict=True))


def scale(c, a, q):
    return tuple(c * x % q for x in a)


def basis(vectors, q):
    """Reduced row basis, also used for column spaces represented as vectors."""
    rows = []
    pivots = []
    for vector in vectors:
        v = vector
        for p, row in zip(pivots, rows, strict=True):
            v = add(v, scale(-v[p], row, q), q)
        p = next((i for i, x in enumerate(v) if x), None)
        if p is None:
            continue
        v = scale(pow(v[p], -1, q), v, q)
        for i, row in enumerate(rows):
            rows[i] = add(row, scale(-row[p], v, q), q)
        at = sum(old < p for old in pivots)
        pivots.insert(at, p)
        rows.insert(at, v)
    return rows


def inside(v, space, q):
    return len(basis([*space, v], q)) == len(space)


def columns(a):
    return list(zip(*a, strict=True))


def transpose(a):
    return tuple(columns(a))


def matmul(a, b, q):
    return tuple(tuple(sum(x * y for x, y in zip(row, col, strict=True)) % q
                       for col in columns(b)) for row in a)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def solve(a, rhs, q):
    """Return one solution with free coordinates zero, or None."""
    n = len(a[0])
    rows = basis([(*row, y) for row, y in zip(a, rhs, strict=True)], q)
    if any(not any(row[:n]) and row[n] for row in rows):
        return None
    answer = [0] * n
    for row in rows:
        p = next((i for i in range(n) if row[i]), None)
        if p is not None:
            answer[p] = row[n]
    check(matmul(a, transpose([answer]), q) == tuple((x,) for x in rhs),
          "linear solver returned a false solution")
    return tuple(answer)


def kernel(a, q):
    n = len(a[0])
    rows = basis(a, q)
    pivots = [next(i for i, x in enumerate(row) if x) for row in rows]
    result = []
    for free in range(n):
        if free in pivots:
            continue
        v = [int(i == free) for i in range(n)]
        for p, row in zip(pivots, rows, strict=True):
            v[p] = -row[free] % q
        result.append(tuple(v))
    return result


def common_complement(w, v, k, q):
    """Complement v inside w while avoiding k, where dim(k)<=dim(v)."""
    check(len(k) <= len(v) <= len(w), "bad complement dimensions")
    u = []
    for _ in range(len(w) - len(v)):
        av, ak = basis([*v, *u], q), basis([*k, *u], q)
        x = next(z for z in w if not inside(z, av, q))
        if inside(x, ak, q):
            y = next(z for z in w if not inside(z, ak, q))
            x = add(x, y, q) if inside(y, av, q) else y
        check(not inside(x, av, q) and not inside(x, ak, q),
              "common-complement step failed")
        u.append(x)
    check(len(basis([*v, *u], q)) == len(w), "not a complement")
    check(len(basis([*k, *u], q)) == len(k) + len(u), "kernel intersection")
    return u


def chart(a, row_swap, col_swap):
    m = len(a) // 2
    rows = list(range(m, 2*m)) + list(range(m)) if row_swap else list(range(2*m))
    cols = list(range(m, 2*m)) + list(range(m)) if col_swap else list(range(2*m))
    return tuple(tuple(a[i][j] for j in cols) for i in rows)


def join(x, y):
    return tuple((*r, *s) for r, s in zip(x, y, strict=True))


def construct(a, q):
    """Choose ranks, construct the graph, then return three legal factors."""
    m = len(a) // 2
    check(q in (2, 3, 5, 7) and 1 <= m <= 4 and len(a) == 2*m,
          "verifier domain exceeded")
    check(all(len(row) == 2*m and all(0 <= x < q for x in row) for row in a),
          "invalid field matrix")
    row_ranks = [len(basis(a[i*m:(i+1)*m], q)) for i in range(2)]
    col_ranks = [len(basis([v[i*m:(i+1)*m] for v in a], q)) for i in range(2)]
    rs, cs = row_ranks[1] > row_ranks[0], col_ranks[0] > col_ranks[1]
    n = chart(a, rs, cs)
    w = basis(columns(n), q)
    v = basis(columns(n)[m:], q)
    if not w:
        f = tuple((0,) * m for _ in range(m))
    else:
        wm = transpose(w)
        k = [tuple(z[0] for z in matmul(wm, transpose([c]), q))
             for c in kernel(wm[:m], q)]
        u = common_complement(w, v, k, q)
        system = transpose([*columns(n)[m:], *u])
        solutions = [solve(system, c, q) for c in columns(n)[:m]]
        check(all(s is not None for s in solutions), "graph lift unsolvable")
        f = transpose([s[:m] for s in solutions])
    first, second = transpose(columns(n)[:m]), transpose(columns(n)[m:])
    graph_image = tuple(add(x, scale(-1, y, q), q)
                        for x, y in zip(first, matmul(second, f, q), strict=True))
    e, lower = graph_image[:m], graph_image[m:]
    b = [solve(transpose(e), row, q) for row in lower]
    check(all(row is not None for row in b), "row projection not injective")
    b = tuple(b)
    upper_right, bottom_right = second[:m], second[m:]
    d = tuple(add(x, scale(-1, y, q), q)
              for x, y in zip(bottom_right, matmul(b, upper_right, q), strict=True))
    one, zero = identity(m), tuple((0,) * m for _ in range(m))
    p = (*join(one, zero), *join(b, one))
    r = (*join(one, upper_right), *join(zero, d))
    s = (*join(e, zero), *join(f, one))
    return (p, r, s), (rs, cs)


def verify_target(a, q, data=False):
    factors, (rs, cs) = construct(a, q)
    m = len(a) // 2
    product = identity(2*m)
    for i, factor in enumerate(factors):
        fixed = range(m, 2*m) if i % 2 == 0 else range(m)
        check(all(columns(factor)[j] == columns(identity(2*m))[j] for j in fixed),
              "factor violates its base-field right-vector alphabet")
        product = matmul(product, factor, q)
    check(chart(product, rs, cs) == a, "three-factor product differs from target")
    if data:
        for x in itertools.product(range(q), repeat=2*m):
            state = transpose([x])
            for factor in reversed(factors):
                state = matmul(factor, state, q)
            check(state == matmul(chart(a, rs, cs), transpose([x]), q),
                  "chronological data action differs")
    return factors, (rs, cs)


def exhaustive_binary():
    digest = hashlib.sha256()
    ranks = [0] * 5
    for entries in itertools.product(range(2), repeat=16):
        a = tuple(tuple(entries[i:i+4]) for i in range(0, 16, 4))
        factors, charts = verify_target(a, 2)
        ranks[len(basis(a, 2))] += 1
        digest.update(bytes(x for f in factors for row in f for x in row))
        digest.update(bytes(charts))
    check(ranks == [1, 225, 7350, 37800, 20160], "binary rank coverage changed")
    return {"targets": 65536, "rank_histogram": ranks, "word_sha256": digest.hexdigest()}


def sharp_target(m):
    a = [list(row) for row in identity(2*m)]
    a[0], a[m+1] = a[m+1], a[0]
    return tuple(tuple(row) for row in a)


def two_factor(a, q):
    m = len(a) // 2
    lines = [(1, x) for x in range(q)] + [(0, 1)]
    for s, t in lines:
        row = tuple(add(scale(s, x, q), scale(t, y, q), q)
                    for x, y in zip(a[:m], a[m:], strict=True))
        full_rank = len(basis(row, q))
        for x, y in lines:
            block = [add(scale(x, r[:m], q), scale(y, r[m:], q), q) for r in row]
            if len(basis(block, q)) == full_rank:
                return True
    return False


def examples_and_controls():
    rng = random.Random(831049)
    count = 0
    sharp = 0
    order_controls = 0
    for q in (2, 3, 5, 7):
        for m in (1, 2, 3, 4):
            for _ in range(24):
                a = tuple(tuple(rng.randrange(q) for _ in range(2*m)) for _ in range(2*m))
                factors, charts = verify_target(a, q)
                rev = matmul(matmul(factors[2], factors[1], q), factors[0], q)
                order_controls += chart(rev, *charts) != a
                count += 1
            if m >= 2:
                a = sharp_target(m)
                verify_target(a, q, data=(q == 2 and m == 2))
                check(not two_factor(a, q), "sharp witness admits two factors")
                sharp += 1
    check(solve(((0,),), (1,), 2) is None, "inconsistent solver control")
    check(common_complement([(1, 0), (0, 1)], [(1, 0)], [(0, 1)], 2)
          == [(1, 1)], "binary union-of-two-subspaces control")
    check(two_factor(identity(4), 2), "free target control")
    check(order_controls > 0, "reversal control failed to discriminate")
    a = sharp_target(2)
    factors, charts = verify_target(a, 2)
    check(all(chart(matmul(factors[i], factors[j], 2), *charts) != a
              for i, j in ((0, 1), (0, 2), (1, 2))), "omission control")
    for q in (2, 3, 5, 7):
        for entries in itertools.product(range(q), repeat=4):
            verify_target((entries[:2], entries[2:]), q)
            count += 1
    return {"additional_targets": count, "sharp_witnesses": sharp, "controls": 5,
            "reversed_words_differing": order_controls}


def receipt(results):
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"):
        path = package / name
        check(path.stat().st_size <= 1024*1024, "oversize package file")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((package / "SOURCES.json").read_text())
    check(len(manifest["files"]) <= 8, "source manifest exceeds replay bound")
    for row in manifest["files"]:
        if row["usage"] == "input":
            payload = (root / row["path"]).read_bytes()
            check(hashlib.sha256(payload).hexdigest() == row["sha256"], "source pin drift")
            hashes[row["path"]] = row["sha256"]
    return {"files": hashes, "results": results}


def main():
    results = {"binary": exhaustive_binary(), "other": examples_and_controls()}
    print(json.dumps(receipt(results), sort_keys=True))
    print("PASS_MATRIX_ALGEBRA_THREE_FACTOR binary_targets=65536 "
          f"additional_targets={results['other']['additional_targets']} "
          "sharp_witnesses=12 controls=5 no_new_kappa")


if __name__ == "__main__":
    main()
