"""ISO3 ilib (own code): e-uniform isotropic-pair quantities.
alpha = rank_F2 [D(a_k) Q[:,S_k]]_k (digit-0 left factor), beta = rank_F2 [Q[D_k,:] D(b_k)]_k.
Lemma: A0 B0 = G00 = 0 => C >= alpha + beta; on leftker A0 x rightker B0 the form W = (sum_k D(w mod 2^e) Q D(v mod 2^e))/2^e mod 2 equals x^T y."""
import sys, numpy as np
sys.path.insert(0,'<local-clone>/cards/WILD/NOVEL/den4')
from qlib import *
def f2_basis_rows(M):
    """row-reduce over F2, return (rank, pivot-reduced rows as ints)"""
    M=np.asarray(M)%2; piv={}
    for row in M:
        x=int(''.join(str(int(v)) for v in row),2) if len(row) else 0
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; break
    return piv
def nullspace_left(M):
    """basis of {x : x^T M = 0} over F2, as rows of an array"""
    M=np.asarray(M)%2; n=M.shape[0]
    aug=np.concatenate([M,np.eye(n,dtype=np.int64)],axis=1)
    # gaussian elimination on rows
    A=aug.copy(); r=0; m=M.shape[1]
    for c in range(m):
        p=None
        for i in range(r,n):
            if A[i,c]: p=i; break
        if p is None: continue
        A[[r,p]]=A[[p,r]]
        for i in range(n):
            if i!=r and A[i,c]: A[i]^=A[r]
        r+=1
    return A[r:,m:]
def digits(e,W,V):
    M=2**(e+1); Wr=W%M; Vr=V%M
    return [(Wr>>i)&1 for i in range(e+1)],[(Vr>>j)&1 for j in range(e+1)]
def A0B0(e,W,V,Q,D,S):
    A,B=digits(e,W,V); a,b=A[0],B[0]; n=len(Q)
    Al=np.concatenate([a[:,[k]]*Q[:,S[k]] for k in range(W.shape[1]) if S[k]],axis=1)%2
    Br=np.concatenate([Q[D[k],:]*b[:,k][None,:] for k in range(W.shape[1]) if D[k]],axis=0)%2
    return Al,Br
def iso(e,W,V,pr,Q,D,S,check=True):
    n=len(Q); I=np.eye(n,dtype=np.int64)
    Al,Br=A0B0(e,W,V,Q,D,S); al=rk2(Al); be=rk2(Br.T)
    C=sum(pr); assert C>=al+be,(C,al,be)
    res=dict(C=C,alpha=al,beta=be,ab=al+be)
    if check:
        Lx=nullspace_left(Al); Ry=nullspace_left(Br.T)   # y with Br y = 0
        Me=2**e; Wh=W%Me; Vh=V%Me
        Sm=(Wh@Vh.T)*Q
        assert (Sm%Me==0).all()
        Wf=(Sm//Me)%2
        F=(Lx@Wf@Ry.T)%2; F0=(Lx@Ry.T)%2
        assert (F==F0).all(), 'W != identity form on kernels'
        res['dimL']=len(Lx); res['dimR']=len(Ry); res['rankW|']=rk2(F)
        assert res['rankW|']>=n-al-be
    return res
