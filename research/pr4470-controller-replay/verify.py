#!/usr/bin/env python3
"""Independent literal Laurent replay of #4470's p16 query-thinned complex controller.

Reads research/joint-helper-lattice/CONTROLLER.json only. Each of the 2p = 32 lines is a linear combination of the
initial lines with Laurent-polynomial coefficients in Q, D_0 .. D_(2p) (monomial = exponent tuple). Events:
  LOCAL / QUERY_SHEAR (stage, pair, backward): with (x, y) = (2 pair, 2 pair + 1), swapped if backward,
      y += s * Q^e * x with (e, s) = (+1, -1) if backward else (-1, +1); LOCAL then multiplies x and y by D_stage;
  IDLE (pair, stages): multiply both lines of the pair by the product of D_s;
  ADD (dst, src[, c]): dst += c src;   SWAP / SIGNED_SWAP (x, y): (x, y) <- (y, +-x).
Checks: LOCAL stages are exactly the thick ones and QUERY_SHEAR stages the thin ones; for every monomial m,
left * W_m * right equals the indicator of the declared diagonal entries equal to m (rational, exact); central Q
exponents are +-1; no output credits a thin stage; main ranks 1 + 8|stages| x 112 ports, whole-idle ranks 8|stages|
x 2 lines x 112 ports and 15 x 112 thin queries reproduce CONTROLLER.json's invoice; flipping one query orientation
changes the operator and promoting one thin query to a full stage is rejected.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def replay(events, p, thick):
    n, S = 2 * p, 2 * p + 1
    one = (0,) * (S + 1)
    lines = [{i: {one: F(1)}} for i in range(n)]

    def mul(a, b):
        return tuple(x + y for x, y in zip(a, b))

    def scale(i, m):
        lines[i] = {j: {mul(k, m): v for k, v in poly.items()} for j, poly in lines[i].items()}

    def add(dst, src, m, c):
        for j, poly in lines[src].items():
            tgt = lines[dst].setdefault(j, {})
            for k, v in poly.items():
                kk = mul(k, m)
                w = tgt.get(kk, 0) + c * v
                if w:
                    tgt[kk] = w
                else:
                    tgt.pop(kk, None)
            if not tgt:
                lines[dst].pop(j)

    for ev in events:
        op = ev[0]
        if op in ("LOCAL", "QUERY_SHEAR"):
            _, stage, pair, back = ev
            need((stage in thick) == (op == "LOCAL"), "LOCAL exactly on thick stages")
            x, y = 2 * pair, 2 * pair + 1
            if back:
                x, y = y, x
            add(y, x, (1 if back else -1,) + (0,) * S, -1 if back else 1)
            if op == "LOCAL":
                d = (0,) + tuple(int(s == stage) for s in range(S))
                scale(x, d)
                scale(y, d)
        elif op == "IDLE":
            _, pair, sel = ev
            need(set(sel) <= thick, "idle only on thick stages")
            d = (0,) + tuple(int(s in sel) for s in range(S))
            scale(2 * pair, d)
            scale(2 * pair + 1, d)
        elif op == "ADD":
            _, dst, src, *c = ev
            add(dst, src, one, c[0] if c else 1)
        elif op in ("SWAP", "SIGNED_SWAP"):
            _, x, y = ev
            sg = -1 if op == "SIGNED_SWAP" else 1
            old = lines[x]
            lines[x] = lines[y]
            lines[y] = {j: {k: sg * v for k, v in poly.items()} for j, poly in old.items()}
        else:
            raise AssertionError("unknown event " + op)
    return lines


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def diagonal_ok(lines, row, n):
    L = [[F(x) for x in r] for r in row["boundaries"]["left"]]
    R = [[F(x) for x in r] for r in row["boundaries"]["right"]]
    diag = [tuple(k) for k in row["diagonal"]]
    monos = {m for ln in lines for poly in ln.values() for m in poly} | set(diag)
    for m in monos:
        W = [[lines[i].get(j, {}).get(m, F(0)) for j in range(n)] for i in range(n)]
        if matmul(matmul(L, W), R) != [[F(int(i == j and diag[i] == m)) for j in range(n)] for i in range(n)]:
            return False, len(monos)
    return True, len(monos)


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_bytes())
    p = row["pairs"]
    need((row["kind"], p, row["prefix_pairs"], row["ambient_rank"]) == ("complex", 16, 7, 145), "controller parameters")
    thick = {0, 2 * p, *range(1, 2 * p, 2)}
    need(sorted(thick) == row["invoice"]["thick_stages"], "thick stages")
    ev = row["physical_events"]
    counts = Counter(e[0] for e in ev)
    need(counts == Counter({"LOCAL": 18, "QUERY_SHEAR": 15, "IDLE": 15, "ADD": 90, "SIGNED_SWAP": 16}), "event counts")
    ok, monos = diagonal_ok(replay(ev, p, thick), row, 2 * p)
    need(ok, "left * W * right equals the declared diagonal for every monomial")
    diag = [tuple(k) for k in row["diagonal"]]
    need(Counter(d[0] for d in diag) == Counter({1: 16, -1: 16}), "central exponents +-1")
    need(all(s in thick for d in diag for s, x in enumerate(d[1:]) if x), "no thin stage credited")
    main_ranks = Counter()
    for d in diag:
        main_ranks[1 + 8 * sum(1 for x in d[1:] if x)] += 112
    need({str(k): v for k, v in main_ranks.items()} == row["invoice"]["main"], "main invoice")
    idle = Counter()
    for e in ev:
        if e[0] == "IDLE":
            idle[8 * len(e[2])] += 2 * 112
    need({str(k): v for k, v in idle.items()} == row["invoice"]["whole_idle"], "whole-idle invoice")
    need(counts["QUERY_SHEAR"] * 112 == row["invoice"]["thin_queries"] == 1680, "thin queries 15 x 112")
    bad = json.loads(json.dumps(ev))
    next(e for e in bad if e[0] == "QUERY_SHEAR")[3] = True
    need(not diagonal_ok(replay(bad, p, thick), row, 2 * p)[0], "flipped query orientation rejected")
    bad = json.loads(json.dumps(ev))
    i = next(k for k, e in enumerate(bad) if e[0] == "QUERY_SHEAR")
    bad[i][0] = "LOCAL"
    rejected = False
    try:
        replay(bad, p, thick)
    except AssertionError as exc:
        rejected = "thick" in str(exc)
    need(rejected, "promoting a thin query to a full stage is rejected")
    print(json.dumps({"status": "PASS_PR4470_CONTROLLER_REPLAY", "events": dict(counts), "monomials": monos,
                      "main_invoice": row["invoice"]["main"], "whole_idle": row["invoice"]["whole_idle"],
                      "thin_queries": 1680, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
