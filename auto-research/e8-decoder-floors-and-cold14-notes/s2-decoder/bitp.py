"""Bit-side punctured units with label decoders (M = B0 on the live lines): star cost = min-weight basis of F2^9 under
s(q) = dim span L[R(q) \\ P] (matroid greedy, exact); ThmC cost needs reader spans."""
import numpy as np
from geo import *
RLIST = {p: np.array(members(Rmask[p])) for p in range(1, 512)}
def f2_indep_add(basis, x):
    for b in basis:
        x = min(x, x ^ b)
    return x
def s_all(Pset):
    live = np.ones(NL, bool); live[list(Pset)] = False
    s = {}
    for q in range(1, 512):
        idx = RLIST[q][live[RLIST[q]]]
        s[q] = rankQ_lines(list(idx))
    return s
def greedy_basis(w):
    order = sorted(range(1, 512), key=lambda q: (w[q], q))
    basis, chosen = [], []
    for q in order:
        x = q
        for b in sorted(basis, reverse=True):
            x = min(x, x ^ b)
        if x:
            basis.append(x); chosen.append(q)
            if len(chosen) == 9: break
    return chosen, sum(w[q] for q in chosen)
def star_cost(Pset):
    s = s_all(Pset)
    return greedy_basis(s)
if __name__ == '__main__':
    print(star_cost(set()))
    P111 = [39, 52, 57, 71, 76, 78, 103, 109, 114]
    print(star_cost(set(P111)))
    print(star_cost(set(range(8))))
