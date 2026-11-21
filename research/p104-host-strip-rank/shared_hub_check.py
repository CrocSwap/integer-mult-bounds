#!/usr/bin/env python3
"""Independent bounded controls for host-strip and shared-hub rank claims.

These finite checks are not a proof of the general algebraic statement and do
not assert that a signed frame is a verifier-legal caller.
"""
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import json
import random
import subprocess
import sympy as S

HERE = Path(__file__).resolve().parent
PINS = {
    'CallerSGram.lean': '6c03a7f3b3c50fe4340cd105378409ca39abc474',
    'CallerExtraThin.lean': '6cb7618e691f52b647e168494d3218d80dda9915',
    'CallerRC2.lean': '321ec331931fecddd844f3b12fe0caf27178269c',
}
for name, expected in PINS.items():
    got = subprocess.check_output(['git', 'hash-object', str(HERE / "source" / name)], text=True).strip()
    assert got == expected, (name, got, expected)


def sign(i, j):
    assert i != j
    return 1 if i < j else -1


def stage_and_k(A, B, blocks):
    n, m = A.shape
    assert B.shape == (n, m)
    assert sorted(sum((list(b) for b in blocks), [])) == list(range(m))
    time = {col: s for s, block in enumerate(blocks) for col in block}
    G = B.T * A
    K = S.Matrix(m, m, lambda i, j: (2 if i == j else 0) +
                 (G[i, j] if time[i] <= time[j] else -G[i, j]))
    P = S.eye(n)
    for block in blocks:
        P = (S.eye(n) + A[:, block] * B[:, block].T) * P
    return P, G, K


def sub(M, rows, cols):
    return M.extract(list(rows), list(cols))


def two_stage_control():
    # Fixed host gauge supplied by /root/extra_thins; complete signed frame.
    J = S.Matrix([[1, -1], [1, 1]])
    C = J - 2 * S.eye(2)
    A = C.row_join(C)
    B = S.eye(2).row_join(S.eye(2))
    P, G, K = stage_and_k(A, B, [[0, 1], [2, 3]])
    assert P == -S.eye(2) and K.rank() == 2
    assert sub(K, [0, 1], [0, 1]) == J == sub(K, [2, 3], [2, 3])
    assert all(any(A[r, i] or B[r, i] for i in block)
               for r in range(2) for block in ([0, 1], [2, 3]))
    return {'hosts': 2, 'roles': 2, 'K_rank': 2, 'product_minus_I': True,
            'common_roles': 2, 'host_blocks': 'fixed J', 'verifier_legal': False}


def rank_one(M):
    assert M.rank() == 1
    j = next(j for j in range(M.cols) if M[:, j] != S.zeros(M.rows, 1))
    a = M[:, j]
    i = next(i for i in range(M.rows) if a[i] != 0)
    b = (M[i, :] / a[i]).T
    assert a * b.T == M
    return a, b


def three_stage_control():
    # Independently replay /root/extra_thins' frame and thin-factor construction.
    J = S.Matrix([[1, -1], [1, 1]])
    D = [S.Matrix([[-1, 0], [-2, 1]]), S.diag(1, -1), S.Matrix([[-1, 2], [0, 1]])]
    V = [x.inv() * J for x in D]
    A, B = S.zeros(7, 6), S.zeros(7, 6)
    row = 2
    for t in range(3):
        cols = slice(2*t, 2*t+2)
        A[0:2, cols], B[0:2, cols] = V[t], S.eye(2)
        residual = J - 2*S.eye(2) - V[t]
        C, E = residual.rank_decomposition()
        r = residual.rank()
        A[row:row+r, cols], B[row:row+r, cols] = E, C.T
        row += r
    assert row == 7
    eye = S.eye(7)
    P = eye
    for t in range(3):
        C = [2*t, 2*t+1]
        P = (eye + A[:, C] * B[:, C].T) * P
    target = -P.inv()
    u = [S.Matrix([3, 7, -2, 1, 1, 0, -1]),
         S.Matrix([-4, -10, 3, -1, -1, 1, 1]),
         S.Matrix([-S.Rational(2, 5), 2, -S.Rational(6, 5), S.Rational(2, 5),
                   S.Rational(2, 5), -S.Rational(2, 5), -S.Rational(2, 5)])]
    f = [S.Matrix([1, 3, 8, -8, 0, 0, 0]),
         S.Matrix([0, 1, S.Rational(12, 5), -2, -S.Rational(2, 5), S.Rational(2, 5), 0]),
         S.Matrix([0, 0, 1, 5, -6, 1, -5])]
    Ts = [eye + u[i] * f[i].T for i in range(3)]
    H = Ts[2].inv() * Ts[1].inv() * Ts[0].inv() * target
    assert H*H == eye and (H-eye).rank() == 1
    for T in [H, Ts[2], Ts[1], Ts[0]]:
        a, b = rank_one(T - eye)
        A, B = A.row_join(a), B.row_join(b)
    blocks = [[0,1], [2,3], [4,5], [6], [7], [8], [9]]
    P, G, K = stage_and_k(A, B, blocks)
    Kh = sub(K, range(6), range(6))
    assert P == -eye and G.rank() == 7 and K.rank() == Kh.rank() == 3
    assert all(sub(K, blocks[i], blocks[i]) == J for i in range(3))
    masks = [{i for i in range(3) if any(A[r,j] or B[r,j] for j in blocks[i])}
             for r in range(7)]
    assert masks[:2] == [set(range(3))] * 2
    assert all(len(M) == 1 for M in masks[2:])
    assert all(sub(G, blocks[i], blocks[j]).rank() == 2
               for i, j in combinations(range(3), 2))
    altered = A.copy()
    altered[0, 6] += 1
    changed_product, _, _ = stage_and_k(altered, B, blocks)
    assert changed_product != -eye
    return {'hosts': 3, 'roles': 7, 'thin_columns': 4, 'excess': 1,
            'K_rank': 3, 'host_K_rank': 3, 'G_rank': 7, 'product_minus_I': True,
            'common_roles': 2, 'host_blocks': 'fixed J', 'mutation_rejected': True,
            'verifier_legal': False}


def alternating_controls():
    # Actual sign pivots and the two odd-stage Schur scalars.
    receipts = []
    for m in range(2, 18):
        if m % 2 == 0:
            rows, cols = list(range(0, m, 2)), list(range(1, m, 2))
            F = S.Matrix([[sign(i, j) for j in cols] for i in rows])
            assert abs(F.det()) == 2**(m//2-1)
            receipts.append({'m': m, 'pivot_det': abs(int(F.det()))})
        else:
            rest = list(range(1, m))
            cs = []
            for o in (0, 1):
                rows, cols = rest[o::2], rest[1-o::2]
                F = S.Matrix([[sign(i, j) for j in cols] for i in rows])
                v = S.Matrix([[sign(0, j) for j in cols]])
                w = S.Matrix([[sign(i, 0)] for i in rows])
                assert F.det() != 0
                cs.append((v*F.inv()*w)[0])
            assert cs == [-1, 1]
            receipts.append({'m': m, 'odd_schur_scalars': [int(c) for c in cs]})
    return receipts


def rankp(M, p):
    M = [list(row) for row in M]
    if not M:
        return 0
    r, width = 0, len(M[0])
    for j in range(width):
        pivot = next((i for i in range(r, len(M)) if M[i][j] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        v = pow(M[r][j] % p, -1, p)
        M[r] = [(x*v) % p for x in M[r]]
        for i in range(r+1, len(M)):
            z = M[i][j] % p
            if z:
                M[i] = [(a-z*b) % p for a, b in zip(M[i], M[r])]
        r += 1
    return r


def random_controls():
    rng = random.Random(1047852)
    checks, minimum = 0, {}
    for p in (3, 5):
        for m in range(2, 9):
            smallest = 2*m
            for _ in range(350):
                Bs = [[[rng.randrange(p) for _ in range(2)] for _ in range(2)] for _ in range(m)]
                As = [[[rng.randrange(p) for _ in range(2)] for _ in range(2)] for _ in range(m)]
                Ds = []
                while len(Ds) < m:
                    D = [[rng.randrange(p) for _ in range(2)] for _ in range(2)]
                    if rankp(D, p) == 2:
                        Ds.append(D)
                K = [[0]*(2*m) for _ in range(2*m)]
                for i in range(m):
                    for j in range(m):
                        for a in range(2):
                            for b in range(2):
                                K[2*i+a][2*j+b] = (Ds[i][a][b] if i == j else
                                    sign(i, j)*sum(Bs[i][a][x]*As[j][x][b] for x in range(2))) % p
                rk = rankp(K, p)
                assert rk >= m, (p, m, K, rk)
                smallest = min(smallest, rk)
                checks += 1
            minimum[f'p{p}_m{m}'] = smallest
    # Characteristic 2 destroys the sign distinction: the 3-block all-I host
    # matrix has rank 2, despite each diagonal block being invertible.
    K2 = [[int(i % 2 == j % 2) for j in range(6)] for i in range(6)]
    assert rankp(K2, 2) == 2
    return {'cases_checked': checks, 'minima': minimum,
            'characteristic_2_counterexample_hosts': 3, 'characteristic_2_rank': 2}


def strip_controls():
    # Exact host-only construction: one local strip is deficient and its
    # complement has rank 2. This K need not arise from a full signed frame.
    U = S.Matrix([[1,0,0], [0,1,0], [0,1,0], [0,0,1], [0,1,0], [0,0,1]])
    K = U*U.T
    assert K.rank() == 3
    ds=[]
    for i in range(3):
        rows = [2*i, 2*i+1]
        other = [v for j in range(3) if j != i for v in (2*j,2*j+1)]
        assert sub(K, rows, rows).det() != 0
        ds.append(2 - sub(K, rows, other).rank())
    assert ds == [1,0,0]
    for size in range(4):
        for J in combinations(range(3), size):
            inside = [v for j in J for v in (2*j, 2*j+1)]
            assert sub(K, inside, inside).rank() + sum(ds[j] for j in range(3) if j not in J) <= K.rank()
    assert sub(K, [2,3,4,5], [2,3,4,5]).rank() == 2
    return {'host_matrix_rank': 3, 'deficiencies': ds, 'rank2_complement': True,
            'all_subsets_checked': 8, 'full_frame_claimed': False}


def graph_controls():
    # Exhaustive small-graph comparison with the Turan complement formula.
    results = {}
    for n in range(2, 7):
        edges = list(combinations(range(n), 2))
        best = [len(edges)+1]*(n+1)
        for mask in range(1 << len(edges)):
            graph = {edges[i] for i in range(len(edges)) if mask & (1 << i)}
            alpha = max(len(V) for size in range(n+1) for V in combinations(range(n), size)
                        if all(e not in graph for e in combinations(V, 2)))
            for r in range(alpha, n+1):
                best[r] = min(best[r], len(graph))
        for r in range(1, n+1):
            q, t = divmod(n, r)
            assert best[r] == t*comb(q+1, 2) + (r-t)*comb(q, 2)
        results[str(n)] = best[1:]
    def minimum(n, r):
        q, t = divmod(n, r)
        return t*comb(q+1, 2) + (r-t)*comb(q, 2)
    assert minimum(76, 2) == 1406 and minimum(76, 3) == 925
    assert 2*minimum(38, 2) == 684
    return {'exhaustive_minimum_by_n_and_r': results, 'k76_r2': 1406,
            'k76_r3': 925, 'two_clusters_38_r2': 684}


result = {'pins': PINS, 'two_stage_frame': two_stage_control(),
          'three_stage_frame': three_stage_control(), 'alternating_minors': alternating_controls(),
          'finite_field_controls': random_controls(), 'projected_strip': strip_controls(),
          'graph_controls': graph_controls(),
          'scope': 'Paper proofs and finite controls only; no legal caller or price improvement inferred.'}
print(json.dumps(result, indent=2, sort_keys=True))
