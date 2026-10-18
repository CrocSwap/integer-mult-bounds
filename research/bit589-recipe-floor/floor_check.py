#!/usr/bin/env python3
"""Finite confirmation of the local-count floor (PROOF.md) for K = 1, 2.

Breadth-first over products of rank-1 shears: lower u uᵀ (forward local conjugated by any bridge sequence) and upper
-w wᵀ (reverse local), u, w primitive integer vectors with entries in [-B, B], matrix entries bounded by E. A product
that maps L0 -> L1 and L1 -> L0 (block anti-diagonal) is what a recipe with a free final Levi and the exchange needs.
Expected: none at length 2K, some at 2K + 1. Standard library only. This is a bounded finite check, not the proof.
Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0."""
import itertools, json, math, sys


def primitive_vectors(K, B):
    out = []
    for v in itertools.product(range(-B, B + 1), repeat=K):
        if any(v) and next(x for x in v if x) > 0 and math.gcd(*map(abs, v)) == 1:
            out.append(v)
    return out


def generators(K, B):
    gens = []
    for u in primitive_vectors(K, B):
        S = [[u[i] * u[j] for j in range(K)] for i in range(K)]
        low = [[int(i == j) for j in range(2 * K)] for i in range(2 * K)]
        up = [[int(i == j) for j in range(2 * K)] for i in range(2 * K)]
        for i in range(K):
            for j in range(K):
                low[K + i][j] = S[i][j]
                up[i][K + j] = -S[i][j]
        gens += [tuple(map(tuple, low)), tuple(map(tuple, up))]
    return gens


def mul(A, B):
    n = len(A)
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(n) if A[i][k]) for j in range(n)) for i in range(n))


def anti(P, K):
    return all(P[i][j] == 0 for i in range(K) for j in range(K)) and \
        all(P[i][j] == 0 for i in range(K, 2 * K) for j in range(K, 2 * K))


def run(K, B, E):
    gens = generators(K, B)
    ident = tuple(tuple(int(i == j) for j in range(2 * K)) for i in range(2 * K))
    layer = {ident}; rows = []
    for length in range(1, 2 * K + 2):
        new = set()
        for M in layer:
            for g in gens:
                P = mul(g, M)
                if max(abs(x) for r in P for x in r) <= E:
                    new.add(P)
        layer = new
        hits = sum(1 for P in layer if anti(P, K))
        rows.append(dict(length=length, states=len(layer), block_antidiagonal=hits))
    return dict(K=K, vector_bound=B, entry_bound=E, generators=len(gens), layers=rows,
                floor_holds=all(r['block_antidiagonal'] == 0 for r in rows if r['length'] <= 2 * K),
                attained_at_2K_plus_1=rows[2 * K]['block_antidiagonal'] > 0)


if __name__ == '__main__':
    res = [run(1, 3, 50), run(2, 2, 50)]
    for r in res:
        print('   K=%d: %s' % (r['K'], ', '.join('L%d:%d/%d' % (x['length'], x['block_antidiagonal'], x['states']) for x in r['layers'])))
        assert r['floor_holds'] and r['attained_at_2K_plus_1'], r
    json.dump(res, sys.stdout if len(sys.argv) < 2 else open(sys.argv[1], 'w'), indent=1)
    if len(sys.argv) < 2: print()
