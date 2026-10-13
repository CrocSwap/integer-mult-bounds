"""E8 geometry for S2: lines, Gram, F2 labels, W(E8) line permutations, exact ranks."""
import numpy as np, itertools
from functools import lru_cache
from e8units import hamming_e8, e8_labels, f2_rank, rank_q
L, G = hamming_e8()
U9 = e8_labels(G).astype(np.int64)        # 120x9, U U^T = (J+G) mod 2
B0 = ((1 + G) % 2).astype(np.int64)
NL = 120
uint = [int(''.join(map(str, r)), 2) for r in U9]   # label as int (bit 8-j = coord j)
def lab_dot(a, b): return bin(a & b).count('1') & 1
ALLP = list(range(1, 512))
# R(p) as python int bitmask over 120 lines
Rmask = {p: sum(1 << T for T in range(NL) if lab_dot(uint[T], p)) for p in range(512)}
def members(mask): 
    out=[];i=0
    while mask:
        if mask & 1: out.append(i)
        mask >>= 1; i += 1
    return out
def rankQ_lines(idx):
    if not idx: return 0
    return int(np.linalg.matrix_rank(L[idx].astype(float)))
def rankG(R, A):
    """exact-enough rank over Q of G[R,A] = L_R L_A^T/2 (entries small ints; rank <= 8; verified exactly elsewhere)"""
    if not R or not A: return 0
    return int(np.linalg.matrix_rank((L[R] @ L[A].T).astype(float)))
def rankG_exact(R, A):
    if not R or not A: return 0
    return rank_q((L[R] @ L[A].T).tolist())
# W(E8) generators: reflections in the 120 roots acting on lines
def line_index():
    d = {}
    for i, r in enumerate(L):
        d[tuple(r)] = i; d[tuple(-r)] = i
    return d
LIDX = line_index()
def reflection_perm(r):
    r = L[r]; nr = r @ r
    perm = []
    for x in L:
        y = x - (2 * (x @ r) // nr) * r if (2 * (x @ r)) % nr == 0 else None
        perm.append(LIDX[tuple(y)])
    return perm
REFL = [reflection_perm(i) for i in range(NL)]
