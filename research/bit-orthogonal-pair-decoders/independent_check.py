#!/usr/bin/env python3
"""Independent check of the finite facts behind verify.py (standard library only, imports nothing from it).

Different methods: roots and norm-4 vectors are found by an E8 membership filter; functionals are coordinatized
on nine lines S with independent B0 rows, and the witness is checked through the 9 x 9 identity
sum_j B0[S,a_j] B0[b_j,S] = B0[S,S], which is equivalent to sum_j u_{a_j} u_{b_j}^T = I_9; ranks use fraction-free
(Bareiss) integer elimination on full Gram blocks G[R, A]; the simple system comes from a generic linear functional;
D7 normals are the 2160 norm-4 lattice vectors.  Pricing is not repeated here.

Run:  python3 -I -B research/bit-orthogonal-pair-decoders/independent_check.py [--repo ROOT]
"""
import argparse
import gzip
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def report(tag, ok, info):
    print(('PASS ' if ok else 'FAIL ') + tag + ': ' + info, flush=True)
    if not ok:
        FAILS.append(tag)


def in_doubled_e8(x):
    """x = 2v with v in E8 = {v in Z^8 or (Z + 1/2)^8 : sum v even}."""
    parity = {c % 2 for c in x}
    return len(parity) == 1 and sum(x) % 4 == 0


def lattice_vectors(norm2):
    even = range(-4, 5, 2)
    odd = (-3, -1, 1, 3)
    out = []
    for vals in (even, odd):
        for x in itertools.product(vals, repeat=8):
            if sum(c * c for c in x) == norm2 and in_doubled_e8(x):
                out.append(x)
    return out


def positive(x):
    return next(c for c in x if c) > 0


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def bareiss_rank(M):
    A = [list(r) for r in M]
    rows, cols = len(A), len(A[0]) if A else 0
    rank, prev = 0, 1
    for c in range(cols):
        p = next((i for i in range(rank, rows) if A[i][c]), None)
        if p is None:
            continue
        A[rank], A[p] = A[p], A[rank]
        for i in range(rank + 1, rows):
            for j in range(c + 1, cols):
                num = A[i][j] * A[rank][c] - A[i][c] * A[rank][j]
                if num % prev:
                    raise ArithmeticError('inexact Bareiss step')
                A[i][j] = num // prev
            A[i][c] = 0
        prev = A[rank][c]
        rank += 1
        if rank == rows:
            break
    return rank


def popcount(x):
    return bin(x).count('1')


def nullspace(rows):
    m = [[Fraction(c) for c in r] for r in rows]
    piv, rk = [], 0
    for c in range(8):
        p = next((i for i in range(rk, len(m)) if m[i][c]), None)
        if p is None:
            continue
        m[rk], m[p] = m[p], m[rk]
        m[rk] = [x / m[rk][c] for x in m[rk]]
        for i in range(len(m)):
            if i != rk and m[i][c]:
                f = m[i][c]
                m[i] = [x - f * y for x, y in zip(m[i], m[rk])]
        piv.append(c)
        rk += 1
    res = []
    for fr in [c for c in range(8) if c not in piv]:
        v = [Fraction(0)] * 8
        v[fr] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -m[i][fr]
        d = 1
        for x in v:
            d *= x.denominator
        res.append([int(x * d) for x in v])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(HERE.parents[1]))
    repo = Path(ap.parse_args().repo).resolve()

    roots = lattice_vectors(8)
    lines = sorted(r for r in roots if positive(r))
    n = len(lines)
    pos = {r: i for i, r in enumerate(lines)}
    report('X.roots', len(roots) == 240 and n == 120, 'membership filter finds 240 roots, 120 lines')
    G = [[dot(x, y) // 4 for y in lines] for x in lines]
    B0 = [[(1 + G[i][j]) % 2 for j in range(n)] for i in range(n)]

    rowint = [sum(B0[i][t] << t for t in range(n)) for i in range(n)]
    S, echelon = [], {}
    for i in range(n):                      # nine lines whose B0 rows are independent over F2
        v = rowint[i]
        while v and (v.bit_length() - 1) in echelon:
            v ^= echelon[v.bit_length() - 1]
        if v:
            echelon[v.bit_length() - 1] = v
            S.append(i)
    rest_dependent = len(S) == 9
    readers = [0] * 512                     # reader set of the functional with S-coordinates f
    for f in range(512):
        for k in range(9):
            if f >> k & 1:
                readers[f] ^= rowint[S[k]]
    sizes = sorted(popcount(readers[f]) for f in range(1, 512))
    report('X.code', rest_dependent and sizes.count(56) == 255 and sizes.count(64) == 255 and sizes.count(120) == 1,
           'B0 has F2 rank 9; the 511 reader sets have sizes 56 (255), 64 (255), 120 (1)')
    coord = {readers[f]: f for f in range(1, 512)}
    uint = [coord.get(rowint[a]) for a in range(n)]   # S-coordinates of each root functional lambda_a
    report('X.root-functionals', all(u is not None for u in uint) and len(set(uint)) == 120,
           'every root functional lambda_a (row a of B0) is one of the 511 codewords, all distinct')

    def cost(rmask, amask):
        R = [t for t in range(n) if rmask >> t & 1]
        A = [t for t in range(n) if amask >> t & 1]
        return bareiss_rank([[G[r][a] for a in A] for r in R])

    W = json.loads((HERE / 'WITNESS.json').read_text(encoding='utf-8'))['pairs']
    pairs = [(pos[tuple(a)], pos[tuple(b)]) for a, b in W]
    ident = all(sum(B0[s][a] * B0[b][s2] for a, b in pairs) % 2 == B0[s][s2] for s in S for s2 in S)
    report('X.dual-identity', ident and all(G[a][b] == 0 for a, b in pairs),
           'sum_j B0[S,a_j] B0[b_j,S] = B0[S,S] on a 9-line basis S (equivalent to sum_j u_a u_b^T = I_9); pairs orthogonal')
    A_ = [a for a, _ in pairs]
    B_ = [b for _, b in pairs]
    full = (1 << n) - 1

    def chain(p):
        if p <= 9:
            return A_[:p]
        if p <= 18:
            return A_ + B_[:p - 9]
        return A_ + B_ + [t for t in range(n) if t not in A_ + B_][:p - 18]

    ok = True
    for p in range(26):
        live = full & ~sum(1 << t for t in chain(p))
        cs = [cost(readers[uint[a]] & live, readers[uint[b]] & live) for a, b in pairs]
        ok &= sum(cs) == max(72 - p, 54)
    report('X.chain', ok, 'Bareiss Gram-block costs give cst = max(72 - p, 54) for p = 0..25 (P102: 54 on 102 lines)')

    f = (10007, 1009, 101, 13, 7, 5, 3, 2)
    posr = [r for r in roots if dot(r, f) > 0]
    pset = set(posr)
    simple = [r for r in posr if not any(tuple(a - b for a, b in zip(r, s)) in pset for s in posr)]
    report('X.simple', len(posr) == 120 and len(simple) == 8 and all(dot(a, b) in (0, -4) for a in simple for b in simple if a != b),
           'a generic functional gives 8 simple roots with off-diagonal Cartan entries 0 / -1')

    def taus(normal_list):
        inside = sum(1 << t for t in range(n) if all(dot(lines[t], w) == 0 for w in normal_list))
        return popcount(inside), sorted(popcount(readers[fn] & ~inside) for fn in range(1, 512))

    seen = {}
    for i in range(8):
        cnt, ts = taus(nullspace([simple[j] for j in range(8) if j != i]))
        seen[cnt] = (ts[0], ts[1])
    expect = {63: (1, 24), 42: (14, 34), 37: (27, 28), 28: (28, 35), 23: (33, 41), 22: (35, 35), 16: (40, 43), 14: (43, 43)}
    report('X.types', seen == expect, 'eight hyperplane types (lines: min/next): ' +
           ', '.join('%d: %d/%d' % (k, v[0], v[1]) for k, v in sorted(seen.items(), reverse=True)))
    report('X.roots-direct', all(taus([lines[a]])[1][:2] == [1, 24] for a in range(n)), 'every root hyperplane: min 1, next 24')
    d7 = sorted({v if positive(v) else tuple(-c for c in v) for v in lattice_vectors(16)})
    sets, d7ok = [], True
    for w in d7:
        inside = sum(1 << t for t in range(n) if dot(lines[t], w) == 0)
        ranked = sorted((popcount(readers[fn] & ~inside), fn) for fn in range(1, 512))
        d7ok &= popcount(inside) == 42 and ranked[0][0] == 14 and ranked[1][0] >= 34
        sets.append(readers[ranked[0][1]] & ~inside)
    union = min(popcount(x | y) for x, y in itertools.combinations(sets, 2))
    report('X.D7', len(d7) == 1080 and d7ok and union >= 21,
           '1080 norm-4 directions, each a 42-line hyperplane with a 14-puncture minimizer (next >= 34); unions >= %d' % union)
    theta = min(taus(nullspace([simple[j] for j in I]))[1][0] for I in itertools.combinations(range(8), 6))
    report('X.theta6', theta == 26, 'rank-6 standard subspaces need >= %d punctures' % theta)

    word = json.loads(gzip.decompress((repo / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz').read_bytes()))
    hl = {tuple(v) for v in word['lines']}
    pats = {tuple(abs(c) for c in v) for v in hl}
    hroots = [x for x in itertools.product(range(-2, 3), repeat=8) if sum(c * c for c in x) == 4
              and (sum(1 for c in x if c) == 1 or tuple(abs(c) for c in x) in pats)]
    hlines = sorted({v for v in hroots if positive(v)})
    hn = len(hlines)
    hidx = {v: i for i, v in enumerate(hlines)}
    hb = [[(1 + dot(x, y) // 2) % 2 for y in hlines] for x in hlines]
    P = [hidx[v] for v in hlines if v not in hl]
    rows = [sum(hb[p][t] << t for t in range(hn)) for p in P]
    dual = []
    for k in range(9):
        for mask in range(1, 512):
            comb = 0
            for j in range(9):
                if mask >> j & 1:
                    comb ^= rows[j]
            if all((comb >> P[j] & 1) == (j == k) for j in range(9)):
                dual.append(comb)
                break
    roots_among_duals = [k for k in range(9) if any(sum(hb[j][t] << t for t in range(hn)) == dual[k] for j in range(hn))
                         ] if len(dual) == 9 else []
    ext = P + [next(j for j in range(hn) if sum(hb[j][t] << t for t in range(hn)) == dual[roots_among_duals[0]])] \
        if len(roots_among_duals) == 1 else P
    live = [t for t in range(hn) if t not in ext]
    lmask = sum(1 << t for t in live)
    ident = all(sum((rows[k] >> t & 1) * (dual[k] >> s & 1) for k in range(9)) % 2 == hb[t][s] for t in live for s in live)
    cst = sum(bareiss_rank([[dot(hlines[r], hlines[a]) // 2 for a in range(hn) if (dual[k] & lmask) >> a & 1]
                            for r in range(hn) if (rows[k] & lmask) >> r & 1]) for k in range(9))
    report('X.shipped', hn == 120 and len(P) == 9 and len(dual) == 9 and len(roots_among_duals) == 1
           and len(live) == 110 and ident and cst == 62,
           'PR589 word: 9 punctured lines, one dual root; puncturing it leaves 110 lines, identity holds, cst 62')
    if FAILS:
        print('FAILED: ' + ' '.join(FAILS))
        sys.exit(1)
    print('PASS_BIT_PAIR_INDEPENDENT: membership roots, basis-coordinate functionals, Bareiss ranks; chain p=0..25; '
          'thresholds 1/14/26; shipped P110 cst 62')


if __name__ == '__main__':
    main()
