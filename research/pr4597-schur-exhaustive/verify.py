#!/usr/bin/env python3
"""Exhaustive check of PR #4597 (petalas) on all commuting pairs: block Schur commutator identity and rank bound.

#4597 (head dfeb8ca7) proves, for commuting P = [[A,R],[C,D]], Q = [[B,L],[E,F]] over a field with invertible d x d
leading blocks A, B (not assumed to commute), S = D - C A^-1 R, Z = F - E B^-1 L:
    [S,Z] = X V - U Y,  U = C A^-1 - E B^-1, V = A^-1 R - B^-1 L, X = W - E B^-1 H, Y = T - H B^-1 L,
    rank [S,Z] <= min(2d, n-d), with equality 2d iff [X U] has column rank 2d and [V; -Y] has row rank 2d,
where PQ = [[H,T],[W,J]]. Its finite corroboration covers the polynomial families (P, P^2) and one GL_4(F_2) orbit.

This verifier covers every commuting pair (P, Q) in M_3(F_2), M_3(F_3) and M_4(F_2), and every split 1 <= d < n
with A and B invertible. It is written independently (nothing imported from #4597):
  * commuting pairs are enumerated as Q in the centralizer of P, a nullspace computed here over F_q;
  * P runs over orbit representatives of simultaneous block-diagonal conjugation by GL_d x GL_{n-d}, which maps
    commuting pairs to commuting pairs, A, B to conjugates, S, Z, X, U, V, Y to conjugates/equivalents, and so
    preserves invertibility of A, B, both ranks and the identity; every result is weighted by the orbit size, so
    the reported counts are exact counts over all pairs (checked against the total number of commuting pairs);
  * for each admitted pair it checks the identity entrywise, the bound, and the equality criterion, and records
    the commutator-rank distribution, the maximum attained rank, and the same restricted to idempotent pairs.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from itertools import product
import json
import sys

COMMUTING_PAIRS = {(3, 2): 7456, (3, 3): 809433, (4, 2): 2526976}   # recomputed below from centralizer dimensions


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def mul(a, b, q):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % q for j in range(len(b[0])))
                 for i in range(len(a)))


def sub(a, b, q):
    return tuple(tuple((x - y) % q for x, y in zip(ra, rb)) for ra, rb in zip(a, b))


def neg(a, q):
    return tuple(tuple(-x % q for x in r) for r in a)


def block(m, r0, r1, c0, c1):
    return tuple(tuple(m[i][c0:c1]) for i in range(r0, r1))


def rank(m, q):
    rows = [list(r) for r in m]
    r = 0
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


def all_matrices(n, q):
    for e in product(range(q), repeat=n * n):
        yield tuple(tuple(e[i * n:(i + 1) * n]) for i in range(n))


def centralizer(p, q):
    """All Q with PQ = QP, from a nullspace basis over F_q."""
    n = len(p)
    eqs = []
    for i, j in product(range(n), repeat=2):
        row = [0] * (n * n)
        for k in range(n):
            row[k * n + j] = (row[k * n + j] + p[i][k]) % q
            row[i * n + k] = (row[i * n + k] - p[k][j]) % q
        eqs.append(row)
    rows, pivots, r = [x[:] for x in eqs], [], 0
    for c in range(n * n):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], q - 2, q)
        rows[r] = [v * inv % q for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [(x - f * y) % q for x, y in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(n * n) if c not in pivots]
    basis = []
    for f in free:
        v = [0] * (n * n)
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = -rows[i][f] % q
        basis.append(v)
    out = []
    for coeffs in product(range(q), repeat=len(basis)):
        v = [sum(c * b[t] for c, b in zip(coeffs, basis)) % q for t in range(n * n)]
        out.append(tuple(tuple(v[i * n:(i + 1) * n]) for i in range(n)))
    return out


def block_group(n, d, q):
    g1 = [g for g in all_matrices(d, q) if inverse(g, q) is not None]
    g2 = [g for g in all_matrices(n - d, q) if inverse(g, q) is not None]
    out = []
    for a, b in product(g1, g2):
        g = tuple(tuple(a[i] + (0,) * (n - d)) for i in range(d)) + tuple(tuple((0,) * d + b[i]) for i in range(n - d))
        out.append((g, inverse(g, q)))
    return out


def orbit_reps(n, d, q):
    group, seen, reps = block_group(n, d, q), set(), []
    for p in all_matrices(n, q):
        if p in seen:
            continue
        orbit = {mul(mul(g, p, q), gi, q) for g, gi in group}
        seen |= orbit
        reps.append((p, len(orbit)))
    need(sum(s for _, s in reps) == q ** (n * n), "orbits partition M_n")
    return reps


def check_pair(p, qm, d, q):
    n = len(p)
    a, r_, c_, dd = block(p, 0, d, 0, d), block(p, 0, d, d, n), block(p, d, n, 0, d), block(p, d, n, d, n)
    b, l_, e_, f_ = block(qm, 0, d, 0, d), block(qm, 0, d, d, n), block(qm, d, n, 0, d), block(qm, d, n, d, n)
    ai, bi = inverse(a, q), inverse(b, q)
    if ai is None or bi is None:
        return None
    pq = mul(p, qm, q)
    h, t, w = block(pq, 0, d, 0, d), block(pq, 0, d, d, n), block(pq, d, n, 0, d)
    s = sub(dd, mul(mul(c_, ai, q), r_, q), q)
    z = sub(f_, mul(mul(e_, bi, q), l_, q), q)
    comm = sub(mul(s, z, q), mul(z, s, q), q)
    u = sub(mul(c_, ai, q), mul(e_, bi, q), q)
    v = sub(mul(ai, r_, q), mul(bi, l_, q), q)
    x = sub(w, mul(mul(e_, bi, q), h, q), q)
    y = sub(t, mul(mul(h, bi, q), l_, q), q)
    need(comm == sub(mul(x, v, q), mul(u, y, q), q), "identity [S,Z] = XV - UY")
    rk = rank(comm, q)
    need(rk <= min(2 * d, n - d), "rank bound")
    left = tuple(xr + ur for xr, ur in zip(x, u))
    right = v + neg(y, q)
    need((rk == 2 * d) == (rank(left, q) == 2 * d and rank(right, q) == 2 * d), "equality criterion")
    idem = mul(p, p, q) == p and mul(qm, qm, q) == qm
    return rk, idem


def survey(n, q):
    total = sum(len(centralizer(p, q)) for p in all_matrices(n, q))
    need(total == COMMUTING_PAIRS[(n, q)], "commuting pairs in M_%d(F_%d)" % (n, q))
    out = {}
    for d in range(1, n):
        dist, idem_dist, pairs = Counter(), Counter(), 0
        for p, size in orbit_reps(n, d, q):
            for qm in centralizer(p, q):
                pairs += size
                res = check_pair(p, qm, d, q)
                if res is not None:
                    dist[res[0]] += size
                    if res[1]:
                        idem_dist[res[0]] += size
        need(pairs == total, "orbit weights recover every commuting pair")
        out[d] = {"bound": min(2 * d, n - d), "admitted": sum(dist.values()),
                  "rank_distribution": {str(k): v for k, v in sorted(dist.items())},
                  "max_rank": max(dist), "idempotent_rank_distribution":
                  {str(k): v for k, v in sorted(idem_dist.items())}}
    return out


def main():
    results = {"M3(F2)": survey(3, 2), "M3(F3)": survey(3, 3), "M4(F2)": survey(4, 2)}
    for name, res in results.items():
        for d, r in res.items():
            need(r["max_rank"] <= r["bound"], "bound")
    # controls: the bound is attained in M3 at d = 1 over F2 and F3, and in M4(F2) at d = 1 and d = 2
    need(results["M3(F2)"][1]["max_rank"] == 2 and results["M3(F3)"][1]["max_rank"] == 2, "M3, d = 1 attains 2")
    need(results["M4(F2)"][1]["max_rank"] == 2 and results["M4(F2)"][2]["max_rank"] == 2, "M4(F2) attains bound")
    need(all(r[n - 1]["max_rank"] == 0 for r, n in ((results["M3(F2)"], 3), (results["M3(F3)"], 3),
                                                     (results["M4(F2)"], 4))), "n - d = 1 forces rank 0")
    # finding: commuting idempotent pairs never reach 2d in these exhaustive domains (maximum 1)
    idem_max = {name: {d: max(map(int, r["idempotent_rank_distribution"])) for d, r in res.items()}
                for name, res in results.items()}
    need(all(m <= 1 for res in idem_max.values() for m in res.values()), "idempotent pairs stay at rank <= 1")
    need(idem_max["M3(F3)"][1] == 1 and idem_max["M4(F2)"][1] == 1 and idem_max["M4(F2)"][2] == 1, "rank 1 attained")
    # positive control: over F5 (the #4597 sharpness field) a commuting idempotent pair in M_3 reaches 2 at d = 1
    p5 = ((3, 2, 2), (1, 2, 1), (1, 1, 2))
    q5 = ((4, 0, 4), (0, 1, 0), (2, 0, 2))
    need(mul(p5, q5, 5) == mul(q5, p5, 5), "F5 control commutes")
    need(check_pair(p5, q5, 1, 5) == (2, True), "F5 control: idempotent pair with commutator rank 2 = 2d")
    print(json.dumps({"status": "PASS_PR4597_EXHAUSTIVE_COMMUTING_PAIRS", "results": results,
                      "idempotent_max_rank": idem_max, "f5_idempotent_control_rank": 2,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
