# g_T(w): max # lines of target T whose labels lie in a w-dim subspace of F2^9 (all subspaces, via codim-c functional spaces, RREF enum)
import json, numpy as np, itertools, pickle, sys
from targ import H, off, LAB
v=112
par=lambda x: bin(x).count('1')&1
def rref_spaces(c,n=9):
    # all c-dim subspaces of F2^n as list of c basis ints (RREF, pivots = leading bits)
    out=[]
    for piv in itertools.combinations(range(n),c):
        free=[[j for j in range(p) if j not in piv] for p in piv]  # bits below pivot not pivots... use: pivot = highest bit
        # row i: bit piv[i] set, other pivot bits clear, bits > piv[i] clear; free bits = non-pivot positions < piv[i]
        for vals in itertools.product(*[range(1<<len(f)) for f in free]):
            rows=[]
            for p,f,x in zip(piv,free,vals):
                r=1<<p
                for k,j in enumerate(f):
                    if x>>k&1: r|=1<<j
                rows.append(r)
            out.append(rows)
    return out
Zm=np.zeros((512,2),dtype=np.uint64)
for phi in range(512):
    m=0
    for t in range(v):
        if par(phi&LAB[t])==0: m|=1<<t
    Zm[phi,0]=m&((1<<64)-1); Zm[phi,1]=m>>64
def kern_masks(c):
    S=rref_spaces(c); A=np.array(S)
    K=Zm[A[:,0]].copy()
    for i in range(1,c): K&=Zm[A[:,i]]
    return K
def tm(T):
    m=sum(1<<t for t in T); return np.array([m&((1<<64)-1), m>>64],dtype=np.uint64)
if __name__=='__main__':
    res={}
    KM={c:kern_masks(c) for c in (1,2,3,4)}
    for c in KM: print('codim',c,len(KM[c]),'global g',int((np.bitwise_count(KM[c][:,0])+np.bitwise_count(KM[c][:,1])).max()),flush=True)
    Ts=sorted(set(off(h) for h in H),key=len)
    for T in Ts:
        m=tm(T); row=[]
        for c in (1,2,3,4):
            K=KM[c]; row.append(int((np.bitwise_count(K[:,0]&m[0])+np.bitwise_count(K[:,1]&m[1])).max()))
        res[T]=row
    pickle.dump(res,open('gT.pkl','wb'))
    from collections import Counter
    print(Counter((len(T),tuple(r)) for T,r in res.items()))
