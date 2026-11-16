#!/usr/bin/env python3
"""Schur rank of one nullity-32 paired-star class, plus one capped outsider.

The proof is PROOF.md. This file checks the two sharp points in an independent
implementation, then compiles class_witness.c. Failures are raised, so
python -O still fails closed.
"""

import os
import random
import subprocess
import sys

MUL = (
    (0, 0, 0, 0),
    (0, 1, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
)
INV = (0, 1, 3, 2)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def add(a, b):
    return a ^ b


def mul(a, b):
    return MUL[a][b]


def mat(a, b, c, d):
    return ((a, b), (c, d))


ZERO = mat(0, 0, 0, 0)
EYE = mat(1, 0, 0, 1)
E11 = mat(1, 0, 0, 0)


def mm(left, right):
    return tuple(
        tuple(add(mul(left[i][0], right[0][j]), mul(left[i][1], right[1][j])) for j in range(2))
        for i in range(2)
    )


def ma(left, right):
    return tuple(tuple(add(left[i][j], right[i][j]) for j in range(2)) for i in range(2))


def put(grid, stride, brow, bcol, block):
    for i in range(2):
        for j in range(2):
            grid[2 * brow + i][2 * bcol + j] = block[i][j]


def rank(rows):
    a = [list(row) for row in rows]
    n = len(a)
    m = len(a[0])
    r = 0
    for col in range(m):
        pivot = next((i for i in range(r, n) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = INV[a[r][col]]
        a[r] = [mul(inv, value) for value in a[r]]
        for i in range(n):
            if i != r and a[i][col]:
                factor = a[i][col]
                a[i] = [add(a[i][j], mul(factor, a[r][j])) for j in range(m)]
        r += 1
    return r


def schur(blocks):
    p, q, r, s, t, u, v, w = blocks
    eye, zero = EYE, ZERO
    iq, it = ma(eye, q), ma(eye, t)
    rp, rix = mm(r, p), mm(r, iq)
    vp, vx = mm(v, p), mm(v, iq)
    sp, sq = mm(s, p), mm(s, q)
    wp, wq = mm(w, p), mm(w, q)
    z = [[0] * 8 for _ in range(8)]
    put(z, 8, 0, 0, p)
    put(z, 8, 0, 1, eye)
    put(z, 8, 0, 2, iq)
    put(z, 8, 1, 0, eye)
    put(z, 8, 1, 1, r)
    put(z, 8, 1, 3, s)
    put(z, 8, 2, 0, it)
    put(z, 8, 2, 2, u)
    put(z, 8, 3, 1, v)
    put(z, 8, 3, 3, w)
    zd = [[0] * 8 for _ in range(8)]
    put(zd, 8, 0, 1, eye)
    put(zd, 8, 0, 2, eye)
    put(zd, 8, 0, 3, eye)
    put(zd, 8, 1, 0, eye)
    put(zd, 8, 2, 0, eye)
    put(zd, 8, 3, 0, eye)
    for i in range(8):
        for j in range(8):
            zd[i][j] ^= z[i][j]
    ez = [[0] * 6 for _ in range(6)]
    ed = [[0] * 6 for _ in range(6)]
    put(ez, 6, 0, 0, ma(eye, rp))
    put(ez, 6, 0, 1, rix)
    put(ez, 6, 0, 2, s)
    put(ez, 6, 1, 0, it)
    put(ez, 6, 1, 1, u)
    put(ez, 6, 2, 0, vp)
    put(ez, 6, 2, 1, vx)
    put(ez, 6, 2, 2, w)
    put(ed, 6, 0, 0, sp)
    put(ed, 6, 0, 1, r)
    put(ed, 6, 0, 2, sq)
    put(ed, 6, 1, 0, t)
    put(ed, 6, 1, 2, u)
    put(ed, 6, 2, 0, ma(eye, wp))
    put(ed, 6, 2, 1, v)
    put(ed, 6, 2, 2, wq)
    rz, rzd = rank(z), rank(zd)
    sez, sed = rank(ez), rank(ed)
    require(rz == 2 + sez and rzd == 2 + sed, "Schur identity failed")
    require(sez + sed >= 4, "Schur sum below 4")
    return sez, sed, rz, rzd


def algebraic_control():
    require(schur((ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO)) == (2, 2, 4, 4), "zero point")
    require(schur((EYE, EYE, EYE, ZERO, EYE, ZERO, ZERO, ZERO)) == (0, 4, 2, 6), "split point")
    require(schur((ZERO, ZERO, ZERO, ZERO, E11, ZERO, ZERO, ZERO)) == (2, 2, 4, 4), "rank-1 point")
    rng = random.Random(157)
    for _ in range(200):
        blocks = tuple(mat(rng.randrange(4), rng.randrange(4), rng.randrange(4), rng.randrange(4)) for _ in range(8))
        schur(blocks)


def run_witness():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    source = os.path.join(root, "research", "paired-star-nullity32-schur", "class_witness.c")
    binary = os.path.join("/tmp", "nullity32-schur-witness")
    compile_run = subprocess.run(
        ["gcc", "-O2", "-std=c11", "-fopenmp", "-o", binary, source],
        cwd=root,
        capture_output=True,
        text=True,
    )
    require(compile_run.returncode == 0, "gcc failed: " + compile_run.stderr[-500:])
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = env.get("OMP_NUM_THREADS") or "4"
    witness = subprocess.run([binary, "witness"], cwd=root, capture_output=True, text=True, env=env)
    sys.stderr.write(witness.stderr)
    require(witness.returncode == 0, "witness exit %s\n%s" % (witness.returncode, witness.stdout[-1000:]))
    text = witness.stdout
    require("named c=0,0,0 perm=0 gaps=2,4 nullity=32 block=1 private=1 dp=-3 " in text, "named class")
    require("foreign c=0,0,0 perm=4 gaps=2,4 nullity=24 block=0 dp=-3 " in text, "foreign class")
    require("min_schur=4 identity_bad=0" in text, "C smoke test")
    require("PASS_NULLITY32_SCHUR" in text, "witness token")
    shapes = subprocess.run([binary, "shapes"], cwd=root, capture_output=True, text=True, env=env)
    sys.stderr.write(shapes.stderr)
    require(shapes.returncode == 0, "shapes exit %s\n%s" % (shapes.returncode, shapes.stdout[-1000:]))
    require("signatures=1746" in shapes.stdout, "signature count")
    require("nullity32=24 eight4=24 named_mask=1 named_private=1 mask_patterns=24" in shapes.stdout, "mask profile")
    require("PASS_SHAPES" in shapes.stdout, "shapes token")
    require("class_cap=0" in shapes.stdout, "shape pass must not claim rank caps")


def main():
    algebraic_control()
    run_witness()
    print("PASS_NULLITY32_SCHUR")


if __name__ == "__main__":
    main()
