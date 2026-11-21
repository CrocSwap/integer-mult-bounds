# E7 minus a 7-frame (56 lines): h, M-uniqueness rank, Gram per-term floor via rank-6 flats.
import numpy as np, collections, itertools
from ds_lib import *; from ds_rank import *; from s2_flats import e8_vectors
L=e8_lines(); E7=e7a1(L)[:-1]; a0=L[0]
# 7 mutually orthogonal lines in E7 (greedy w/ backtracking)
G=E7@E7.T
def find(cur,start):
    if len(cur)==7: return cur
    for j in range(start,len(E7)):
        if all(G[j,i]==0 for i in cur):
            r=find(cur+[j],j+1)
            if r: return r
    return None
fr=find([],0); P=E7[[i for i in range(len(E7)) if i not in fr]]
print('E7-frame lines',len(P),'h',hrank(P))
X=e8_vectors(); X=X[(X@a0)==0]
D=(X@P.T)==0; packed=np.packbits(D,axis=1); _,ui=np.unique(packed,axis=0,return_index=True)
n=len(P); Q=Qmat(P); lab=Labels(Q); S=set(); sizes=collections.Counter()
for i in ui:
    idx=np.nonzero(D[i])[0]
    if len(idx)>=6 and np.linalg.matrix_rank(P[idx].astype(float))==6:
        sizes[len(idx)]+=1; A=[j for j in range(n) if j not in set(idx.tolist())]; S.add(lab.span(A))
S=list(S); hist=collections.Counter(lab.pair_rank(a,b) for a in S for b in S)
print('flats by size',sorted(sizes.items()),'spans',len(S),'pair-rank hist',sorted(hist.items()))
# M uniqueness inside R^7: constraints rank (8x8 unknowns; expect 64-15=49 if unique on R^7)
rows=[]
for i in range(n):
    for j in range(n):
        if i==j or P[i]@P[j]==0: rows.append(np.outer(P[i],P[j]).reshape(-1))
print('constraint rank',np.linalg.matrix_rank(np.array(rows,dtype=float)),'(49 = unique on R^7)')
