#!/usr/bin/env python3
"""Binary projectors attain the Schur-commutator bound 2d for every d (follow-up to #4597 OQ2 and #4609).

#4597 (petalas) proves rank [S,Z] <= min(2d, n-d) for the Schur complements of commuting P, Q with invertible leading
d x d blocks, with sharpness over F5; #4609 refines this for idempotents to min(2d, 2 floor((n-d)/2)) and shows that
over F2 the value 2d is first reached at n = 5 for d = 1 and at n = 6 for d = 2.

Corollary (proved below, checked for d = 1..4): over F2, for every d >= 1 there are commuting idempotents in M_{5d}
with invertible leading d x d blocks whose Schur commutator has rank exactly 2d.
Proof: take the #4609 witness (P, Q) in M_5(F2) at d = 1 (p_00 = q_00 = 1, rank [S,Z] = 2) and put P' = P (x) I_d,
Q' = Q (x) I_d with coordinate (i, k) at index i*d + k, so the first d coordinates are (0, k), k < d. Then P', Q'
are commuting idempotents,
the leading d x d blocks are p_00 I_d = I_d, the Schur complements are S (x) I_d and Z (x) I_d, and
[S (x) I_d, Z (x) I_d] = [S,Z] (x) I_d has rank 2d. The bound 2d is attained since min(2d, 2 floor(4d/2)) = 2d.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
import sys

P5 = ((1, 1, 0, 0, 0), (0, 0, 0, 0, 0), (1, 0, 1, 1, 1), (0, 0, 0, 1, 0), (1, 1, 0, 1, 0))
Q5 = ((1, 1, 1, 0, 0), (1, 0, 0, 1, 1), (1, 0, 0, 1, 1), (1, 0, 1, 0, 1), (1, 1, 0, 1, 0))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mul(a, b):
    return tuple(tuple(sum(a[i][k] & b[k][j] for k in range(len(b))) & 1 for j in range(len(b[0])))
                 for i in range(len(a)))


def sub(a, b):
    return tuple(tuple(x ^ y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def block(m, r0, r1, c0, c1):
    return tuple(tuple(m[i][c0:c1]) for i in range(r0, r1))


def rank(m):
    rows, r = [list(x) for x in m], 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def inverse(m):
    n = len(m)
    rows = [list(r) + [int(i == j) for j in range(n)] for i, r in enumerate(m)]
    for c in range(n):
        p = next((i for i in range(c, n) if rows[i][c]), None)
        if p is None:
            return None
        rows[c], rows[p] = rows[p], rows[c]
        for i in range(n):
            if i != c and rows[i][c]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[c])]
    return tuple(tuple(r[n:]) for r in rows)


def kron_identity(m, d):
    n = len(m)
    return tuple(tuple(m[i // d][j // d] if i % d == j % d else 0 for j in range(n * d)) for i in range(n * d))


def schur_rank(p, q, d):
    n = len(p)
    ai, bi = inverse(block(p, 0, d, 0, d)), inverse(block(q, 0, d, 0, d))
    need(ai is not None and bi is not None, "invertible leading blocks")
    s = sub(block(p, d, n, d, n), mul(mul(block(p, d, n, 0, d), ai), block(p, 0, d, d, n)))
    z = sub(block(q, d, n, d, n), mul(mul(block(q, d, n, 0, d), bi), block(q, 0, d, d, n)))
    need(mul(s, s) == s and mul(z, z) == z, "idempotent Schur complements")
    return rank(sub(mul(s, z), mul(z, s)))


def main():
    need(mul(P5, P5) == P5 and mul(Q5, Q5) == Q5 and mul(P5, Q5) == mul(Q5, P5), "base witness")
    need(schur_rank(P5, Q5, 1) == 2, "base rank 2 at n = 5, d = 1")
    ranks = {}
    for d in range(1, 5):
        p, q = kron_identity(P5, d), kron_identity(Q5, d)
        need(mul(p, p) == p and mul(q, q) == q and mul(p, q) == mul(q, p), "tensored commuting idempotents")
        r = schur_rank(p, q, d)
        need(r == 2 * d == min(2 * d, 2 * ((5 * d - d) // 2)), "rank 2d attained at n = 5d")
        ranks[str(d)] = {"n": 5 * d, "rank": r}
    print(json.dumps({"status": "PASS_BINARY_PROJECTOR_SHARPNESS_ALL_D", "ranks": ranks,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
