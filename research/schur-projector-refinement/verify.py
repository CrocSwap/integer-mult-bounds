#!/usr/bin/env python3
"""Projector refinement of PR #4597's block Schur commutator bound (its open question 2).

#4597 (petalas, head dfeb8ca7): for commuting P, Q with invertible leading d x d blocks, the Schur complements S, Z
satisfy rank [S,Z] <= min(2d, n-d); for idempotent P, Q the complements are idempotent; the bound is sharp over F5.

Here, for commuting idempotent P, Q:
  (1) parity theorem (PROOF in README): two idempotents never have an invertible commutator in odd dimension, over
      any field, so rank [S,Z] <= min(2d, 2 floor((n-d)/2)). Checked here on every pair of idempotents (commuting or
      not) in M_3(F_2) and M_3(F_3), on random idempotent pairs in M_5(F_2), M_5(F_3), M_5(F_5), and on the
      algebra identities used in the proof;
  (2) minimal-dimension sharpness at small fields, by exhaustive negatives over all commuting idempotent pairs
      (enumerated here from the full idempotent lists) and explicit witnesses:
        d = 1, rank 2: F5 at n = 3; F3 first at n = 4 (n = 3 exhaustively max 1); F2 first at n = 5 (n = 3, 4 max 1);
        d = 2 over F2: rank 2 first at n = 5 (n = 4 exhaustively max 1), which is the refined bound there;
                       rank 4 = 2d at n = 6;
        d = 2 over F5 at n = 5: rank 2, again the refined bound (the unrefined bound would be 3).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from itertools import product
import json
import random
import sys

WITNESSES = [  # (q, n, d, P, Q, rank)
    (5, 3, 1, ((3, 2, 2), (1, 2, 1), (1, 1, 2)), ((4, 0, 4), (0, 1, 0), (2, 0, 2)), 2),
    (3, 4, 1, ((2, 2, 2, 0), (0, 1, 0, 0), (2, 1, 2, 0), (2, 1, 1, 1)),
     ((1, 0, 2, 1), (2, 2, 1, 1), (1, 2, 2, 0), (1, 2, 2, 0)), 2),
    (2, 5, 1, ((1, 1, 0, 0, 0), (0, 0, 0, 0, 0), (1, 0, 1, 1, 1), (0, 0, 0, 1, 0), (1, 1, 0, 1, 0)),
     ((1, 1, 1, 0, 0), (1, 0, 0, 1, 1), (1, 0, 0, 1, 1), (1, 0, 1, 0, 1), (1, 1, 0, 1, 0)), 2),
    (2, 5, 2, ((1, 0, 0, 0, 0), (1, 1, 1, 1, 0), (1, 0, 0, 1, 0), (0, 0, 0, 1, 0), (1, 0, 1, 1, 1)),
     ((1, 1, 0, 1, 1), (0, 1, 0, 0, 0), (0, 0, 1, 0, 0), (0, 1, 0, 0, 1), (0, 0, 0, 0, 1)), 2),
    (2, 6, 2, ((0, 1, 1, 1, 0, 1), (1, 1, 1, 1, 1, 0), (0, 1, 1, 0, 1, 1), (1, 0, 1, 0, 1, 0), (1, 0, 1, 1, 0, 0),
               (0, 1, 0, 0, 1, 0)),
     ((0, 1, 0, 1, 1, 1), (1, 1, 1, 1, 0, 0), (0, 1, 0, 0, 1, 1), (0, 0, 0, 1, 0, 0), (1, 0, 1, 1, 1, 0),
      (0, 0, 0, 0, 0, 1)), 4),
    (5, 5, 2, ((0, 4, 4, 0, 0), (3, 3, 2, 2, 4), (2, 3, 4, 3, 1), (0, 1, 1, 4, 1), (0, 1, 1, 3, 2)),
     ((4, 3, 1, 2, 1), (2, 0, 0, 0, 4), (2, 4, 1, 0, 4), (2, 3, 2, 0, 4), (1, 1, 2, 4, 3)), 2),
]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mul(a, b, q):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % q for j in range(len(b[0])))
                 for i in range(len(a)))


def sub(a, b, q):
    return tuple(tuple((x - y) % q for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def block(m, r0, r1, c0, c1):
    return tuple(tuple(m[i][c0:c1]) for i in range(r0, r1))


def rank(m, q):
    rows, r = [list(x) for x in m], 0
    for c in range(len(rows[0]) if rows else 0):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        inv = pow(rows[r][c], q - 2, q)
        rows[r] = [v * inv % q for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % q for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def inverse(m, q):
    n = len(m)
    rows = [list(r) + [int(i == j) for j in range(n)] for i, r in enumerate(m)]
    for c in range(n):
        p = next((i for i in range(c, n) if rows[i][c]), None)
        if p is None:
            return None
        rows[c], rows[p] = rows[p], rows[c]
        inv = pow(rows[c][c], q - 2, q)
        rows[c] = [v * inv % q for v in rows[c]]
        for i in range(n):
            if i != c and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % q for x, y in zip(rows[i], rows[c])]
    return tuple(tuple(r[n:]) for r in rows)


def schur_commutator(p, qm, d, q):
    """(S, Z, rank [S,Z]) or None when a leading block is singular."""
    n = len(p)
    ai, bi = inverse(block(p, 0, d, 0, d), q), inverse(block(qm, 0, d, 0, d), q)
    if ai is None or bi is None:
        return None
    s = sub(block(p, d, n, d, n), mul(mul(block(p, d, n, 0, d), ai, q), block(p, 0, d, d, n), q), q)
    z = sub(block(qm, d, n, d, n), mul(mul(block(qm, d, n, 0, d), bi, q), block(qm, 0, d, d, n), q), q)
    return s, z, rank(sub(mul(s, z, q), mul(z, s, q), q), q)


def idempotents(n, q):
    out = []
    for e in product(range(q), repeat=n * n):
        m = tuple(tuple(e[i * n:(i + 1) * n]) for i in range(n))
        if mul(m, m, q) == m:
            out.append(m)
    return out


def random_idempotent(n, q, rng):
    while True:
        m = tuple(tuple(rng.randrange(q) for _ in range(n)) for _ in range(n))
        mi = inverse(m, q)
        if mi is not None:
            diag = tuple(tuple(rng.randrange(2) if i == j else 0 for j in range(n)) for i in range(n))
            return mul(mul(m, diag, q), mi, q)


def gaussian_binomial_count(n, q):
    """Number of idempotents in M_n(F_q): sum_k [n choose k]_q q^(k(n-k))."""
    total = 0
    for k in range(n + 1):
        num = den = 1
        for i in range(k):
            num *= q ** (n - i) - 1
            den *= q ** (i + 1) - 1
        total += num // den * q ** (k * (n - k))
    return total


def main():
    # (1) parity theorem checks
    for n, q in ((3, 2), (3, 3)):
        ids = idempotents(n, q)
        need(len(ids) == gaussian_binomial_count(n, q), "idempotent count M_%d(F_%d)" % (n, q))
        need(all(rank(sub(mul(s, z, q), mul(z, s, q), q), q) < n for s in ids for z in ids),
             "odd dimension: every idempotent pair in M_%d(F_%d) has a singular commutator" % (n, q))
        for s in ids:
            for z in ids:
                u = mul(sub(s, z, q), sub(s, z, q), q)
                need(mul(s, u, q) == mul(u, s, q) and mul(z, u, q) == mul(u, z, q), "(S-Z)^2 is central")
    rng = random.Random(4597)
    for n, q in ((5, 2), (5, 3), (5, 5)):
        for _ in range(3000):
            s, z = random_idempotent(n, q, rng), random_idempotent(n, q, rng)
            need(rank(sub(mul(s, z, q), mul(z, s, q), q), q) < n, "random odd-dimension pair singular")
    # (2a) exhaustive negatives over all commuting idempotent pairs
    maxima = {}
    for n, q in ((3, 2), (4, 2), (3, 3)):
        ids = idempotents(n, q)
        for d in range(1, n):
            best = 0
            for p in ids:
                for qm in ids:
                    if mul(p, qm, q) == mul(qm, p, q):
                        res = schur_commutator(p, qm, d, q)
                        if res is not None:
                            need(mul(res[0], res[0], q) == res[0] and mul(res[1], res[1], q) == res[1],
                                 "Schur complements of idempotents are idempotent")
                            need(res[2] <= min(2 * d, 2 * ((n - d) // 2)), "refined bound")
                            best = max(best, res[2])
            maxima["M%d(F%d) d=%d" % (n, q, d)] = best
    need(maxima == {"M3(F2) d=1": 1, "M3(F2) d=2": 0, "M4(F2) d=1": 1, "M4(F2) d=2": 1, "M4(F2) d=3": 0,
                    "M3(F3) d=1": 1, "M3(F3) d=2": 0}, "exhaustive maxima")
    # (2b) witnesses
    rows = []
    for q, n, d, p, qm, r in WITNESSES:
        need(mul(p, p, q) == p and mul(qm, qm, q) == qm and mul(p, qm, q) == mul(qm, p, q), "witness inputs")
        s, z, rk = schur_commutator(p, qm, d, q)
        need(mul(s, s, q) == s and mul(z, z, q) == z, "witness complements idempotent")
        need(rk == r == min(2 * d, 2 * ((n - d) // 2)), "witness attains the refined bound")
        rows.append({"field": "F%d" % q, "n": n, "d": d, "rank": rk, "unrefined_bound": min(2 * d, n - d)})
    # failure control: without idempotence the refinement is false (general commuting pair, F2, n = 5, d = 2, rank 3)
    gp = ((1, 0, 1, 0, 1), (1, 1, 1, 1, 0), (0, 0, 1, 1, 0), (1, 1, 0, 0, 1), (0, 1, 0, 0, 0))
    gq = ((1, 0, 0, 0, 1), (0, 1, 1, 1, 1), (0, 0, 1, 1, 1), (1, 0, 0, 0, 0), (0, 1, 0, 1, 1))
    need(mul(gp, gq, 2) == mul(gq, gp, 2) and mul(gp, gp, 2) != gp, "control: commuting, not idempotent")
    need(schur_commutator(gp, gq, 2, 2)[2] == 3, "control: general commuting pair reaches the unrefined bound 3")
    print(json.dumps({"status": "PASS_PR4597_PROJECTOR_REFINEMENT",
                      "general_pair_control_F2_n5_d2_rank": 3,
                      "parity_checks": "all idempotent pairs M3(F2), M3(F3); 3000 random pairs each M5(F2/F3/F5)",
                      "exhaustive_commuting_idempotent_maxima": maxima, "witnesses": rows,
                      "minimal_n_for_rank_2_at_d1": {"F5": 3, "F3": 4, "F2": 5},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
