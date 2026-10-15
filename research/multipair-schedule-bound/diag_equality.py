"""Diagnostic for the (K=3, s=4) Theorem S equality pattern: (a, d, sigma_P, sigma_Q) after each stage.

Stage 1: one forward and one backward rank-1 word (commuting); later stages: rank E = rank H = 1 with
a and d each rising by 1 (the only pattern equality allows, README Q2). Exhaustive over F2.
usage: python -B diag_equality.py K S
"""
import sys
from itertools import product
from collections import Counter
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from sched_search import rref, rank
K = int(sys.argv[1]); S = int(sys.argv[2]); n = 2 * K; xm = (1 << K) - 1
mats = list(product(range(1 << K), repeat=K)); zero = tuple([0] * K)


def mul(A, B):
    out = []
    for a in A:
        r = 0
        for j in range(K):
            if (a >> j) & 1:
                r ^= B[j]
        out.append(r)
    return tuple(out)


r1 = [M for M in mats if rank(M) == 1]
pairs = [(E, H) for E in r1 for H in r1 if mul(H, E) == zero and mul(E, H) == zero]


def combos(rows):
    c = [0] * (1 << K)
    for m in range(1, 1 << K):
        low = (m & -m).bit_length() - 1
        c[m] = c[m & (m - 1)] ^ rows[low]
    return c


def inv(P, Q):
    a = K - rank([p & xm for p in P]); d = K - rank([q >> K for q in Q])
    b = K - rank([p >> K for p in P]); g = K - rank([q & xm for q in Q])
    return a, d, K - a - b, K - d - g


X = tuple(1 << i for i in range(K)); Y = tuple(1 << (K + i) for i in range(K))
layer = {(rref(X, n), rref(Y, n))}
for s in range(1, S + 1):
    nxt = set()
    for (P, Q) in layer:
        pc, qc = combos(P), combos(Q); a0, d0, _, _ = inv(P, Q)
        for E, H in pairs:
            P2 = rref([P[i] ^ qc[H[i]] for i in range(K)], n); Q2 = rref([Q[i] ^ pc[E[i]] for i in range(K)], n)
            a, d, sp, sq = inv(P2, Q2)
            if s == 1 or (a == a0 + 1 and d == d0 + 1):
                nxt.add((P2, Q2))
    layer = nxt
    print(s, len(layer), dict(Counter(inv(*st) for st in layer)), flush=True)
