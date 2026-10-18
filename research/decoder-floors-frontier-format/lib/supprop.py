"""Lemma 1.1 (support propagation) machinery shared by c2 and c4; standard library only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from units import *

def setup(L, T):
    v = len(L); G = gram(L); adj = orth_graph(L)
    frames = [c for c in maximal_cliques(adj) if popcount(c) == T]
    nbar = [sum(1 << s for s in range(v) if G[t][s] != 0) for t in range(v)]
    return v, frames, nbar

def propagate(O, frames, nbar):
    S = [E & ~O for E in frames]
    while True:
        Wg = -1
        for s in S:
            w = 0; x = s
            while x:
                b = x & -x; w |= nbar[b.bit_length() - 1]; x ^= b
            Wg &= w
        S2 = [s & Wg for s in S]
        if S2 == S: return S
        S = S2

def census(L, T):
    v, frames, nbar = setup(L, T); Br = b0rows(L); basis = colspace_basis(Br); h = len(basis)
    classes = span_vectors(basis); unc = []
    for co, w in classes:
        S = propagate(w, frames, nbar)
        if min(popcount(s) for s in S) > 0: unc.append((co, w))
    return dict(v=v, h=h, T=T, nframes=len(frames), nclasses=len(classes), unc=unc, Br=Br)

