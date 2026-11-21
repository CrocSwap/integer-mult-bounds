# DANGERSETS lib (own code). E8 lines in standard coords scaled by 2 (integers), Q = J+G mod 2 (1 on orthogonal pairs + diag).
import itertools, numpy as np
def e8_lines():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for a in (2,-2):
            for b in (2,-2):
                v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(s))
    L=[];seen=set()
    for r in R:
        if tuple(-x for x in r) in seen: continue
        seen.add(r); L.append(r)
    return np.array(L,dtype=np.int64)   # 120 x 8, norm 8 (= 4 * root norm 2)
def Qmat(L):
    G=L@L.T   # 4 * Gram; orthogonal <-> 0; self 8; +-1 roots <-> +-4
    return ((G%8)==0).astype(np.uint8)
def rank2(M):
    M=np.array(M,dtype=np.uint8)%2; M=M.copy(); r=0; rows,cols=M.shape
    for c in range(cols):
        p=None
        for i in range(r,rows):
            if M[i,c]: p=i;break
        if p is None: continue
        M[[r,p]]=M[[p,r]]
        nz=np.nonzero(M[:,c])[0]
        for i in nz:
            if i!=r: M[i]^=M[r]
        r+=1
        if r==rows: break
    return r
def hrank(L): return rank2(Qmat(L))
def halfspin(L): return L[np.all(np.abs(L)==1,axis=1)]
def e7a1(L):
    a0=L[0]; E7=L[(L@a0)==0]; return np.vstack([E7,a0[None,:]])
