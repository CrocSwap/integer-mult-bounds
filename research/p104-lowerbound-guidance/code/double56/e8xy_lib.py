"""DOUBLE56 e8xy_lib.py: Rado-minimiser spaces Xs, Ys for the isotropic-pair lemma."""
import numpy as np
from rho import *
def nullsp(Mrows,support,n):
    # vectors supported on support, orthogonal to rows of M; return basis as array
    sup=sorted(support); A=(Mrows[:,sup]%2) if len(Mrows) else np.zeros((0,len(sup)),int)
    # nullspace of A over F2
    A=A.copy()%2; r=0; pivs=[]; m=len(sup)
    for c in range(m):
        p=None
        for i in range(r,len(A)):
            if A[i,c]: p=i;break
        if p is None: continue
        A[[r,p]]=A[[p,r]]
        for i in range(len(A)):
            if i!=r and A[i,c]: A[i]^=A[r]
        pivs.append(c); r+=1
    free=[c for c in range(m) if c not in pivs]; out=[]
    for f in free:
        v=np.zeros(m,int); v[f]=1
        for i,c in enumerate(pivs): v[c]=A[i,f]
        full=np.zeros(n,int); full[sup]=v; out.append(full)
    return np.array(out)

def xy_spaces(RB,RA,n):
    vb,J=rado_ub(RB,n); va,Jp=rado_ub(RA,n)
    def bits(x): return np.array([(x>>(n-1-s))&1 for s in range(n)])
    VJ=np.array([bits(x) for t in J for x in RB[t]]).reshape(-1,n); UJ=np.array([bits(x) for t in Jp for x in RA[t]]).reshape(-1,n)
    return nullsp(UJ,J,n),nullsp(VJ,Jp,n),vb,va
