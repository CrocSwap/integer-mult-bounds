# E7 Gram floor: per-term rank >= min over pairs of rank-6 flats (hyperplanes of span R^7) of rank Q[P\F1,P\F2].
import numpy as np, collections
from ds_lib import *; from ds_rank import *; from s2_flats import e8_vectors
L=e8_lines(); E7=e7a1(L)[:-1]; a0=L[0]
X=e8_vectors()
X=X[(X@a0)==0]   # normals inside a0^perp = R^7 (E7 lattice vectors; coweights of E7 have norm <= 30? check max below)
D=(X@E7.T)==0; packed=np.packbits(D,axis=1); _,ui=np.unique(packed,axis=0,return_index=True)
masks=set()
for i in ui:
    idx=np.nonzero(D[i])[0]
    if len(idx)>=6 and np.linalg.matrix_rank(E7[idx].astype(float))==6: masks.add(tuple(idx))
print('E7 hyperplane flats (rank 6):',len(masks),'sizes',sorted(collections.Counter(len(m) for m in masks).items()))
Q=Qmat(E7); lab=Labels(Q); n=len(E7)
S=set()
for m in masks:
    A=[i for i in range(n) if i not in set(m)]; S.add(lab.span(A))
S=list(S); hist=collections.Counter()
for a in S:
    for b in S: hist[lab.pair_rank(a,b)]+=1
print('h',lab.h,'distinct spans',len(S),'pair rank hist',sorted(hist.items()))
