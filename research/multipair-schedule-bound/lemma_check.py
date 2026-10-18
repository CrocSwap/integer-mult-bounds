#!/usr/bin/env python3
"""Independent exact check of the per-stage inequalities used in the proof of Theorem S.

Works over GF(p) (default p = 5, also p = 2 and p = 3) with random reachable states. A state is
M in GL_2K; P, Q are the row spaces of its top and bottom K rows; X = F^K + 0, Y = 0 + F^K.
A stage is [[I, H], [E, I]] (invertible) applied on the left, so the new top rows are A + H B and
the new bottom rows are E A + B. Bridges diag(S, T) are applied between stages.
For every stage the script checks, with a = dim P&Y, beta = dim P&X, d = dim Q&X, gamma = dim Q&Y,
sigma^P = K - a - beta, sigma^Q = K - d - gamma, h = rank H, e = rank E:
  (i)   a_t <= d_{t-1} + sigma^Q_{t-1}      and   d_t <= a_{t-1} + sigma^P_{t-1}
  (ii)  a_t <= a_{t-1} + h,  beta_t >= beta_{t-1} - h,  d_t <= d_{t-1} + e,  gamma_t >= gamma_{t-1} - e
  (ii') sigma^P_t <= sigma^P_{t-1} + h - (a_t - a_{t-1}),  and the Q analogue
Controls: the strengthened (false) inequality a_t <= a_{t-1} + h - 1 for h >= 1 must fail somewhere,
and so must (i) without its sigma term. Prints one JSON line and PASS_THEOREM_S_LEMMAS.
"""
import json
import random
import sys


def rank(rows, p):
    rows = [list(r) for r in rows]
    rk, col, n = 0, 0, len(rows[0]) if rows else 0
    while rk < len(rows) and col < n:
        piv = next((i for i in range(rk, len(rows)) if rows[i][col] % p), None)
        if piv is None:
            col += 1
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        inv = pow(rows[rk][col], p - 2, p)
        rows[rk] = [x * inv % p for x in rows[rk]]
        for i in range(len(rows)):
            if i != rk and rows[i][col] % p:
                f = rows[i][col]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rk])]
        rk += 1
        col += 1
    return rk


def meet(U, V, p):
    """dim(U & V) = dim U + dim V - dim(U + V) for row lists U, V of full row rank."""
    return rank(U, p) + rank(V, p) - rank(U + V, p)


def matmul(A, B, p):
    return [[sum(a * b for a, b in zip(row, col)) % p for col in zip(*B)] for row in A]


def rand_rank(K, r, rng, p):
    """Random K x K matrix of rank exactly r (product of K x r and r x K full-rank factors)."""
    while True:
        L = [[rng.randrange(p) for _ in range(r)] for _ in range(K)]
        R = [[rng.randrange(p) for _ in range(K)] for _ in range(r)]
        M = matmul(L, R, p) if r else [[0] * K for _ in range(K)]
        if rank(M, p) == r:
            return M


def rand_inv(K, rng, p):
    while True:
        M = [[rng.randrange(p) for _ in range(K)] for _ in range(K)]
        if rank(M, p) == K:
            return M


def invariants(M, K, p):
    top, bot = M[:K], M[K:]
    X = [[int(i == j) for j in range(2 * K)] for i in range(K)]
    Y = [[int(i + K == j) for j in range(2 * K)] for i in range(K)]
    a, beta = meet(top, Y, p), meet(top, X, p)
    d, gamma = meet(bot, X, p), meet(bot, Y, p)
    return a, beta, d, gamma


def run(K, p, walks, steps, seed):
    rng = random.Random(seed)
    stats = dict(stages=0, false_strengthened_failures=0, false_no_sigma_failures=0)
    for _ in range(walks):
        M = [[int(i == j) for j in range(2 * K)] for i in range(2 * K)]
        for _ in range(steps):
            if rng.random() < 0.5:                      # bridge
                S, T = rand_inv(K, rng, p), rand_inv(K, rng, p)
                top, bot = matmul(S, M[:K], p), matmul(T, M[K:], p)
                M2 = top + bot
                assert invariants(M2, K, p) == invariants(M, K, p), 'bridge changed an invariant'
                M = M2
            h, e = rng.randrange(K + 1), rng.randrange(K + 1)
            H, E = rand_rank(K, h, rng, p), rand_rank(K, e, rng, p)
            stage = [[int(i == j) for j in range(K)] + H[i] for i in range(K)] + \
                    [E[i] + [int(i == j) for j in range(K)] for i in range(K)]
            if rank(stage, p) < 2 * K:
                continue
            a0, b0, d0, g0 = invariants(M, K, p)
            M = matmul(stage, M, p)
            assert rank(M, p) == 2 * K
            a1, b1, d1, g1 = invariants(M, K, p)
            sP0, sQ0 = K - a0 - b0, K - d0 - g0
            sP1, sQ1 = K - a1 - b1, K - d1 - g1
            assert sP0 >= 0 and sQ0 >= 0 and sP1 >= 0 and sQ1 >= 0
            assert a1 <= d0 + sQ0 and d1 <= a0 + sP0, '(i)'
            assert a1 <= a0 + h and b1 >= b0 - h and d1 <= d0 + e and g1 >= g0 - e, '(ii)'
            assert sP1 <= sP0 + h - (a1 - a0) and sQ1 <= sQ0 + e - (d1 - d0), "(ii')"
            stats['stages'] += 1
            if h >= 1 and a1 > a0 + h - 1:
                stats['false_strengthened_failures'] += 1
            if a1 > d0 or d1 > a0:
                stats['false_no_sigma_failures'] += 1
    return stats


def main():
    out = []
    for K, p, walks in ((2, 2, 300), (2, 5, 300), (3, 3, 200), (3, 5, 200), (4, 5, 80)):
        st = run(K, p, walks, 12, seed=1000 * K + p)
        assert st['false_strengthened_failures'] > 0, 'control: strengthened (ii) never failed'
        assert st['false_no_sigma_failures'] > 0, 'control: (i) without sigma never failed'
        out.append(dict(K=K, p=p, **st))
    print(json.dumps(out))
    print('PASS_THEOREM_S_LEMMAS checks=%d' % sum(o['stages'] for o in out))


if __name__ == '__main__':
    sys.exit(main())
