# Enumerate all hyperplane flats of a line set P (subset of E8 lines) via E8 lattice vectors x of norm <= 30
# (every root-spanned hyperplane has normal = multiple of a fundamental-weight image; max norm 30). Exact integers.
import numpy as np, sys, itertools, pickle
from ds_lib import *
def e8_vectors(maxn4=120):
    out=[]
    for par in (0,1):
        vals=[v for v in range(-11,12) if v%2==par]
        # recursive build with norm pruning
        cur=[()]; 
        for d in range(8):
            nxt=[]
            for t in cur:
                s=sum(a*a for a in t)
                for v in vals:
                    if s+v*v<=maxn4: nxt.append(t+(v,))
            cur=nxt
        arr=np.array(cur,dtype=np.int64)
        arr=arr[(arr.sum(1)%4)==0]
        out.append(arr)
    X=np.vstack(out); X=X[np.any(X!=0,axis=1)]
    return X
def flats(P,X):
    # masks of lines orthogonal to x; keep rank-7 ones (hyperplanes), dedupe
    n=len(P); D=(X@P.T)==0
    w=(1<<np.arange(n,dtype=object))
    masks=set()
    for row in D:
        idx=np.nonzero(row)[0]
        if len(idx)<7: continue
        if np.linalg.matrix_rank(P[idx].astype(float))!=7: continue
        masks.add(sum(1<<int(i) for i in idx))
    return masks
if __name__=='__main__':
    L=e8_lines()
    X=e8_vectors(); print('E8 vectors norm<=30:',len(X)); sys.stdout.flush()
    sets={'halfspin':halfspin(L),'E7A1':e7a1(L)}
    out={}
    for nm,P in sets.items():
        # reduce: dedupe orthogonality patterns first quickly via bytes
        D=((X@P.T)==0)
        packed=np.packbits(D,axis=1)
        _,ui=np.unique(packed,axis=0,return_index=True)
        cand=X[ui]
        M=flats(P,cand)
        # maximal only
        Ml=sorted(M,key=lambda m:-bin(m).count('1'))
        print(nm,'distinct orth patterns',len(ui),'hyperplane flats',len(Ml),'sizes',sorted(set(bin(m).count('1') for m in Ml)))
        out[nm]=Ml
    pickle.dump(out,open('flats.pkl','wb'))
