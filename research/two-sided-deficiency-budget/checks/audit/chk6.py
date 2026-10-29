# per-target caps (w=7,6,5) on all 1120 level-2 targets S = P112 \ E6, own masks (validated enumerator for codim 3,4)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import sys, json, numpy as np, time
sys.path.insert(0,os.path.join(HERE,'..','rb'))
from gT import rref_spaces
D=json.load(open(DATA))
LAB=[int(x) for x in D['LAB']]; L=np.rint(np.array(D['L'])*2).astype(int); E=np.rint(np.array(D['E8'])*2).astype(int)
Zi=[sum(1<<t for t in range(112) if bin(p&LAB[t]).count('1')%2==0) for p in range(512)]
Z=np.array([[m&(2**64-1), m>>64] for m in Zi],dtype=np.uint64)
M={}
for c in (2,3,4):
    S=np.array(rref_spaces(c)); A=Z[S[:,0]].copy()
    for i in range(1,c): A&=Z[S[:,i]]
    M[c]=np.unique(A,axis=0); print('codim',c,'unique flats',len(M[c]),flush=True)
R=np.vstack([E,-E]); from collections import Counter
A2=set()
for i in range(240):
    for j in range(240):
        if R[i]@R[j]==-4: A2.add(tuple(sorted([tuple(R[i]),tuple(R[j])])))
tab=Counter(); t0=time.time()
for a in A2:
    a=np.array(a); S=sum(1<<t for t in np.nonzero(~((L@a.T)==0).all(axis=1))[0].tolist())
    s=np.array([S&(2**64-1),S>>64],dtype=np.uint64)
    caps=tuple(int((np.bitwise_count(M[c][:,0]&s[0]).astype(np.int16)+np.bitwise_count(M[c][:,1]&s[1])).max()) for c in (2,3,4))
    tab[(bin(S).count('1'),)+caps]+=1
print('(|S|, cap7, cap6, cap5): count',sorted(tab.items()),time.time()-t0)
