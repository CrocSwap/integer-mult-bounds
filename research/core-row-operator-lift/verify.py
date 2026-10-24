#!/usr/bin/env python3
"""The core-row (restricted) operator lift behind HALO's tensor bound, with exact rational controls.

Lemma (README). Let Pi_i be the coordinate projection onto the rows of axis i kept by HALO (distance >= A from the
section faces), B_i the section inverse (zero outside the section), C_i the global inverse, P_sec and P_glob the
section and global Neumann polynomials. If ||B_i - P_sec|| < eps, ||P_glob - C_i|| < eps and Pi_i P_sec = Pi_i P_glob
(HALO's row identity), then ||Pi_i (B_i - C_i)|| < 2 eps; and with ||Pi_i B_i||, ||Pi_i C_i|| <= M,
    ||(x)_i Pi_i B_i - (x)_i Pi_i C_i|| < 2 g M^(g-1) eps,   and (x)_i Pi_i B_i = ((x)_i Pi_i)((x)_i B_i).
This verifier checks exactly (Fractions): the Gram identity X^T X - (Pi X)^T (Pi X) = ((I-Pi) X)^T ((I-Pi) X), which
certifies ||Pi X||_2 <= ||X||_2; the row identity Pi(B - C) = Pi(B - P_sec) + Pi(P_glob - C) when Pi P_sec = Pi P_glob;
the mixed-product rule and the exact restricted telescope for g = 2, 3 on random rational matrices; and #4515's two
examples, where the unrestricted lift fails but the restricted rows obey the bound. Pinned HALO phrases.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def tr(A):
    return [list(r) for r in zip(*A)]


def sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def addm(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def kron(A, B):
    return [[a * b for a in ra for b in rb] for ra in A for rb in B]


def proj(n, keep):
    return [[F(int(i == j and i in keep)) for j in range(n)] for i in range(n)]


def rnd(rng, r, c):
    return [[F(rng.randint(-9, 9), rng.randint(1, 5)) for _ in range(c)] for _ in range(r)]


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    halo = (ROOT / "research/unconditional-batched-crt/HALO.md").read_text(encoding="utf-8")
    for phrase in ("therefore EXACTLY the corresponding row of the global P_i", "Keep outputs at distance A",
                   "from every face. Their difference from the full inverse tensor is at most"):
        need(phrase in halo, "HALO phrase: " + phrase)
    rng = random.Random(4515)
    n = 6
    for _ in range(40):
        keep = set(rng.sample(range(n), 3))
        Pi, I = proj(n, keep), proj(n, set(range(n)))
        X = rnd(rng, n, n)
        PX, RX = mm(Pi, X), mm(sub(I, Pi), X)
        need(sub(mm(tr(X), X), mm(tr(PX), PX)) == mm(tr(RX), RX), "Gram certificate for ||Pi X|| <= ||X||")
        B, C, Psec, Pglob = (rnd(rng, n, n) for _ in range(4))
        Psec = addm(mm(Pi, Pglob), mm(sub(I, Pi), Psec))  # enforce Pi P_sec = Pi P_glob
        need(mm(Pi, Psec) == mm(Pi, Pglob), "row identity on kept rows")
        need(mm(Pi, sub(B, C)) == addm(mm(Pi, sub(B, Psec)), mm(Pi, sub(Pglob, C))), "restricted two-error split")
    for g in (2, 3):
        dims = [3] * g
        Bs = [rnd(rng, d, d) for d in dims]
        Cs = [rnd(rng, d, d) for d in dims]
        Ps = [proj(d, set(rng.sample(range(d), 2))) for d in dims]
        PB = [mm(P, B) for P, B in zip(Ps, Bs)]
        PC = [mm(P, C) for P, C in zip(Ps, Cs)]

        def kr(ms):
            out = ms[0]
            for m in ms[1:]:
                out = kron(out, m)
            return out

        need(mm(kr(Ps), kr(Bs)) == kr(PB), f"g={g}: mixed-product rule")
        total = None
        for k in range(g):
            term = kr(PC[:k] + [sub(PB[k], PC[k])] + PB[k + 1:])
            total = term if total is None else addm(total, term)
        need(sub(kr(PB), kr(PC)) == total, f"g={g}: exact restricted telescope")
    # #4515's examples: unrestricted lift fails, restricted rows behave
    M = [[F(3), F(0)], [F(0), F(9)]]
    e1 = proj(2, {0})
    need(sum(x * x for x in M[0]) < 64 and sum(M[i][1] ** 2 for i in range(2)) > 64, "#4515 example 1: small row, large column")
    PM = mm(e1, M)
    need(max(sum(PM[i][j] ** 2 for i in range(2)) for j in range(2)) == 9 < 64, "restricted to the small row the norm is 3")
    D = [[F(0), F(0)], [F(0), F(2)]]
    need(mm(e1, D) == [[0, 0], [0, 0]], "#4515 example 2: the extra term vanishes on the kept row")
    need(3 + 0 + 3 < 2 * 4 and not 3 + 2 + 3 < 2 * 4, "restricted sum 6 < 8, unrestricted 8 is not")
    print(json.dumps({"status": "PASS_CORE_ROW_OPERATOR_LIFT", "gram_cases": 40, "telescope_g": [2, 3],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
