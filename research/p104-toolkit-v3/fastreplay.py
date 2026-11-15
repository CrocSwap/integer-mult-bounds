#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fast randomised-exact replay of a P104 word (our NETCAUX lane; idea from our SHADOWCORE lane: replay mod 2^61-1).  Stdlib only.
Rows are LINEAR in the program, so instead of the full N x N row matrix we replay the N x k PROJECTION  row . R  where R is a fixed random
N x k matrix mod p = 2^61-1 (pure python ints, no numpy).  A nonzero row difference projects to zero with probability p^-k = 2^-244 at k=4.
Any FLAG (a projected mismatch) is re-checked by an EXACT Fraction replay of the backward slice that influences the flagged registers.
API
  FastReplay(W, R=None, k=4, seed=1)       -> .proj (N,2,k), .bad (structural problems, same kinds as pricekit.replay), .ok, .nproblems
  proj_matrix(n, N, k, seed)               -> R for a word with n publics and N-n owned (owned rows start at 0)
  exact_rows(W, regs)                      -> {reg: Fraction row} by exact replay of the backward slice only
  slice_events(W, regs)                    -> sorted event indices that can influence the final rows of `regs`
"""
import random, collections
from fractions import Fraction as Q
P = 2 ** 61 - 1

def proj_matrix(n, k=4, seed=1):
    """R for publics 0..n-1: list of n random k-vectors mod 2^61-1."""
    rng = random.Random(seed)
    return [[rng.randrange(1, P) for _ in range(k)] for _ in range(n)]

class FastReplay:
    def __init__(self, W, R=None, k=4, seed=1):
        n = W['public']; NO = W['owned_fields']; N = n + NO; self.n = n; self.N = N; self.k = k
        if R is None: R = proj_matrix(n, k, seed)
        assert len(R) >= n
        zero = [0] * k
        M = [list(R[r]) for r in range(n)] + [list(zero) for _ in range(NO)]
        cur = list(W['initial']) + [None] * NO; bad = []; owned = set()
        cache = {}
        def qm(s):
            c = cache.get(s)
            if c is None:
                q = Q(s)
                if q.denominator % P == 0: bad.append(('denominator-divisible-by-modulus', s))
                c = cache[s] = q.numerator % P * pow(q.denominator % P, -1, P) % P
            return c
        for i, e in enumerate(W['program']):
            op, r = e[0], e[1]
            if op == 'MOVE':
                if cur[r] != e[2]: bad.append(('move-from', i))
                cur[r] = e[3]
            elif op == 'INIT': owned.add(r); M[r] = list(zero); cur[r] = e[2]
            elif op == 'CLEAR': owned.discard(r); M[r] = list(zero); cur[r] = None
            elif op == 'SCALE':
                if cur[r] != e[3]: bad.append(('scale-frame', i))
                q = qm(e[2]); M[r] = [x * q % P for x in M[r]]
            elif op in ('ADD', 'COPY'):
                s = e[2]; f = e[4]
                if cur[r] != f or cur[s] != f: bad.append(('add-frame', i))
                if op == 'COPY':
                    if any(M[r]): bad.append(('copy-nonzero', i))
                    M[r] = list(zero)
                q = qm(e[3]); M[r] = [(x + q * y) % P for x, y in zip(M[r], M[s])]
            else: bad.append(('op', i, op))
        if owned: bad.append(('owned-alive', len(owned)))
        if cur[:n] != list(W['final']): bad.append(('exit-frames',))
        self.proj = M; self.bad = bad; self.ok = not bad; self.nproblems = len(bad); self.cur = cur
        self.W = W
    def is_zero(self, r): return not any(self.proj[r])

def slice_events(W, regs):
    """Backward slice: indices of events that can influence the final rows of regs."""
    need = set(regs); keep = []
    P = W['program']
    for i in range(len(P) - 1, -1, -1):
        e = P[i]; op = e[0]
        if op == 'MOVE': continue
        r = e[1]
        if r not in need: continue
        keep.append(i)
        if op in ('INIT', 'CLEAR'): need.discard(r)      # content before is dropped
        elif op == 'COPY': need.discard(r); need.add(e[2])
        elif op == 'ADD': need.add(e[2])
    return sorted(keep)

def exact_rows(W, regs):
    n = W['public']; N = n + W['owned_fields']; regs = list(regs)
    ev = slice_events(W, regs); P = W['program']
    rows = {}
    def row(r):
        if r not in rows: rows[r] = {r: Q(1)} if r < n else {}
        return rows[r]
    for i in ev:
        e = P[i]; op = e[0]; r = e[1]
        if op in ('INIT', 'CLEAR'): rows[r] = {}; continue
        if op == 'SCALE':
            q = Q(e[2]); rows[r] = {k: v * q for k, v in row(r).items()}; continue
        s = e[2]; q = Q(e[3]); R = row(r)
        if op == 'COPY': R.clear()
        for k, v in list(row(s).items()):
            nv = R.get(k, 0) + q * v
            if nv: R[k] = nv
            else: R.pop(k, None)
    return {r: row(r) for r in regs}

def replay(W, R=None, k=4, seed=1):
    """returns (rows, cur, bad) where rows[r] is the k-vector PROJECTION of row r
    (list of k ints mod 2^61-1), not a Fraction dict.  Use proj_matrix(...) once and pass R to compare two words' rows
    (equal projections <=> equal rows except with probability 2^-244 per row).  bad entries are structural, same shapes as pricekit.replay."""
    F = FastReplay(W, R, k, seed)
    return F.proj, F.cur, F.bad

def unit_projection(W, R, r):
    """projection of the identity row e_r (what 'helper ends identity' compares against)."""
    return list(R[r])

def rows_equal(rowsA, rowsB, mapA=lambda r: r):
    """indices r (of A) whose projections differ between A and B (B indexed through mapA)."""
    return [r for r in range(len(rowsA)) if rowsA[r] != rowsB[mapA(r)]]
