# common setup: P112 / P104 lines, frames, nbar, label classes (dense B), Omega form via labels
import sys, pickle
from cert2 import *
def load(unit):
    F0, F1 = load_frames()
    if unit=='P112': L=[E8[i] for i in range(120) if i not in set(F0)]
    else: L=[E8[i] for i in range(120) if i not in set(F0)|set(F1)]
    v,G,frames,nbar=setup(L,8)
    basis=colspace_vectors(B0rows(L),v); h=len(basis)
    cls={}
    for co in range(1,1<<h):
        w=0
        for i in range(h):
            if co>>i&1: w^=basis[i]
        cls[co]=w
    return L,v,G,frames,nbar,h,basis,cls
pc=lambda x: bin(x).count('1')
