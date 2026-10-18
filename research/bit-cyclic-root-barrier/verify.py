#!/usr/bin/env python3
"""Finite checks for the written chain-ring proof; ywz65/Codex, Apache-2.0."""
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mul(a, b, q):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out & ((1 << q) - 1)


def val(a, q):
    return (a & -a).bit_length() - 1 if a else q


def inverse(a, q):
    need(a & 1, "nonunit inverse")
    b = 1
    for i in range(1, q):
        if (mul(a, b, q) >> i) & 1:
            b ^= 1 << i
    need(mul(a, b, q) == 1, "unit inverse failed")
    return b


def smith(a, q):
    """Only invertible elementary operations; no division by nonunits."""
    a = [row[:] for row in a]
    n, cols, valuations = len(a), len(a[0]), []
    for k in range(min(n, cols)):
        v, i, j = min((val(a[i][j], q), i, j)
                      for i in range(k, n) for j in range(k, cols))
        if v == q:
            break
        a[k], a[i] = a[i], a[k]
        for row in a:
            row[k], row[j] = row[j], row[k]
        inv = inverse(a[k][k] >> v, q)
        a[k] = [mul(x, inv, q) for x in a[k]]
        need(a[k][k] == 1 << v, "pivot normalization")
        for i in range(k + 1, n):
            need(val(a[i][k], q) >= v, "column divisibility")
            r = a[i][k] >> v
            a[i] = [x ^ mul(r, y, q) for x, y in zip(a[i], a[k])]
        for j in range(k + 1, cols):
            need(val(a[k][j], q) >= v, "row divisibility")
            r = a[k][j] >> v
            for i in range(n):
                a[i][j] ^= mul(r, a[i][k], q)
        valuations.append(v)
    need(all(a[i][j] == (1 << valuations[i] if i == j and i < len(valuations) else 0)
             for i in range(n) for j in range(cols)), "not diagonal")
    return valuations


def rank(columns):
    basis = {}
    for v in columns:
        while v:
            lead = v.bit_length() - 1
            if lead in basis:
                v ^= basis[lead]
            else:
                basis[lead] = v
                break
    return len(basis)


def image(a, q, shift=0):
    """Independent regular representation using shifts, not ring multiply."""
    return [sum(((a[i][j] << (b + shift)) & ((1 << q) - 1)) << (q * i)
                for i in range(len(a))) for j in range(len(a[0])) for b in range(q)]


def check(a, q):
    pivots = smith(a, q)
    r, rz = rank(image(a, q)), rank(image(a, q, 1))
    need(r - rz == len(pivots), "socle engines disagree")
    need(r == sum(q - v for v in pivots), "image dimensions disagree")
    need(len(pivots) <= len(a[0]), "column bound")
    return len(pivots)


def mm(a, b, q):
    out = [[0] * len(b[0]) for _ in a]
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                out[i][j] ^= mul(a[i][k], b[k][j], q)
    return out


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def gp(s, q):
    out = 1
    for _ in range(s):
        out = mul(out, 3, q)
    return out


def telescoping(q, n, length):
    p, uc, vr = identity(n), [], []
    for j in range(length):
        u = [[((j + 3) * (i + 5) * 13) & ((1 << q) - 1)] for i in range(n)]
        v = [[((j + 7) * (i + 2) * 19) & ((1 << q) - 1) for i in range(n)]]
        uc.append([r[0] for r in mm(p, u, q)])
        vr.append(v[0])
        f = mm(u, v, q)
        for i in range(n):
            f[i][i] ^= 1
        p = mm(p, f, q)
    u = [list(r) for r in zip(*uc)]
    for i in range(n):
        p[i][i] ^= 1
    need(mm(u, vr, q) == p, "telescoping factorization")
    need(check(p, q) <= length, "product bound")


def nonchain():
    # F2[x,y]/(x^2,y^2), basis 1,x,y,xy; U=(x,y)^T.
    def product(a, b):
        out = 0
        for i in range(4):
            for j in range(4):
                if (a >> i) & (b >> j) & 1 and not (i & j):
                    out ^= 1 << (i | j)
        return out
    values = {0}
    for i in range(4):
        v = product(2, 1 << i) | (product(4, 1 << i) << 4)
        values |= {x ^ v for x in list(values)}
    socle = [v for v in values if all(product(v & 15, a) == product(v >> 4, a) == 0
                                     for a in (2, 4))]
    need(len(values) == 8 and len(socle) == 4 and rank(socle) == 2, "nonchain witness")
    return {"columns": 1, "image_dimension": 3, "socle_dimension": 2}


def pins():
    rows = [(ROOT / r["path"], r) for r in json.loads((HERE / "SOURCES.json").read_text())["files"]]
    r = json.loads((HERE / "PREDECESSOR.json").read_text())
    rows.append((HERE / r["local_path"], r))
    for path, row in rows:
        b = path.read_bytes()
        need(hashlib.sha256(b).hexdigest() == row["sha256"], "source SHA: " + str(path))
        need(hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
             == row["git_blob"], "source blob: " + str(path))


def run():
    pins()
    totals = []
    for q, n, cols in [(2, 2, 3), (4, 2, 2)]:
        count = 0
        for entries in itertools.product(range(1 << q), repeat=n * cols):
            check([list(entries[i * cols:(i + 1) * cols]) for i in range(n)], q)
            count += 1
        totals.append({"q": q, "rows": n, "columns": cols, "matrices": count})
    state, sampled = 19015, 0
    for q in (3, 8, 16):
        for n, cols in ((1, 5), (5, 1), (4, 3), (3, 4)):
            for _ in range(64):
                a = []
                for i in range(n):
                    row = []
                    for j in range(cols):
                        state = (1664525 * state + 1013904223) & 0xffffffff
                        row.append((state >> 12) & ((1 << q) - 1))
                    a.append(row)
                check(a, q)
                sampled += 1
    targets = []
    for q in (2, 4, 8, 16):
        n, powers = 7, [1, q // 2, q - 1, 1]
        target, word = identity(n), identity(n)
        for i, s in enumerate(powers):
            target[i][i] = gp(s, q)
            f = identity(n)
            f[i][i] = target[i][i]
            word = mm(word, f, q)
        difference = [row[:] for row in target]
        for i in range(n):
            difference[i][i] ^= 1
        need(word == target and check(difference, q) == 4, "mixed target minimum")
        for s in range(1, q):
            need(val(gp(s, q) ^ 1, q) == 1 << val(s, q), "monomial valuation")
        for length in range(1, 7):
            telescoping(q, 4, length)
        targets.append({"q": q, "powers": powers, "restored_helpers": 3, "exact_minimum": 4})
    need(rank(image([[2]], 4)) == 3, "ordinary binary rank differs from socle")
    need(check([[0, 0], [0, 2]], 4) == 1, "exclude identity roles")
    need(check([[2, 0], [0, 2]], 4) == 2, "rank-two increment cannot cost one")
    need((4 * (8 - 4) + 6) // 7 == 3, "C8 ordinary rank screen")
    counterexample = nonchain()
    return {"status": "PASS_CYCLIC_ROOT_BARRIER_FINITE_PREMISES", "exhaustive": totals,
            "sampled_rectangular": sampled, "targets": targets, "telescoping_cases": 24,
            "semantic_controls": 5, "nonchain_control": counterexample,
            "scope": "Finite independent algebra checks; universal theorem is the written proof."}


if __name__ == "__main__":
    result = run()
    receipt = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write-receipt"]:
        need(not receipt.exists(), "will not overwrite receipt")
        receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        need(not sys.argv[1:], "unknown arguments")
        need(result == json.loads(receipt.read_text()), "receipt mismatch")
    print(json.dumps(result, indent=2))
