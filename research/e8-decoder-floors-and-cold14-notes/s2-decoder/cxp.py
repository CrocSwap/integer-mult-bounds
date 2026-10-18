"""Complex-side punctured units with frame decoders.  For a frame K (8 pairwise orthogonal lines) the totals are
A_a = R_a = live lines non-orthogonal to f_a (plus f_a if live); ThmC cost rank_F2 B0[A,A], star cost dim span u_A."""
import numpy as np, itertools
from geo import *
from e8units import f2_rank_rows
def f2rank_ints(vs): return f2_rank_rows(list(vs))
def gram_rank_f2(idx):
    # rank over F2 of B0[idx, idx]
    rows = [sum(int(B0[i, j]) << k for k, j in enumerate(idx)) for i in idx]
    return f2_rank_rows(rows)
# all frames
def frames():
    out = set()
    adj0 = [[G[i, j] == 0 and i != j for j in range(NL)] for i in range(NL)]
    def rec(cl, cand):
        if len(cl) == 8: out.add(tuple(sorted(cl))); return
        for c in cand:
            if c > cl[-1]:
                rec(cl + [c], [d for d in cand if d > c and G[c, d] == 0])
    for i in range(NL):
        rec([i], [d for d in range(NL) if d > i and G[i, d] == 0])
    return sorted(out)
FRAMES = frames()
def cost(Pset, K):
    th = st = 0
    for f in K:
        A = [S for S in range(NL) if S not in Pset and (G[S, f] != 0)]
        th += gram_rank_f2(A); st += f2rank_ints(uint[S] for S in A)
    return th, st
def best(Pset):
    return min((cost(Pset, K), K) for K in FRAMES)
if __name__ == '__main__':
    print('frames', len(FRAMES))
    K0 = tuple(range(8))
    print('P120', cost(set(), K0), 'P112', cost(set(K0), K0))
