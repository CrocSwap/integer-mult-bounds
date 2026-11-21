import sys,numpy as np; sys.path.insert(0,'../orbitlp')
from geo import Q, frames
from rho import *
W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4; n=104
a=W%2;b=V%2; N=(a@b.T)*Q; X=(N//2)%2; I=np.eye(n,dtype=int)
RB=spaces_B(W,V,Q); RA=spaces_A(W,V,Q)
vb,J=rado_ub(RB,n); va,Jp=rado_ub(RA,n)
print('B',vb,len(J),'A',va,len(Jp))
def bits(x): return np.array([(x>>(n-1-s))&1 for s in range(n)])
VJ=np.array([bits(x) for t in J for x in RB[t]]); UJ=np.array([bits(x) for t in Jp for x in RA[t]])
def nullsp(Mrows,support):
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
Xs=nullsp(UJ,J); Ys=nullsp(VJ,Jp)
print('dim X',len(Xs),'dim Y',len(Ys))
from rho import f2rank
def rk(M): return f2rank([toint(r) for r in M%2])
print('rank X^T I Y',rk(Xs@Ys.T),'rank X^T X Y',rk(Xs@X@Ys.T),'rank X^T (I+X) Y',rk(Xs@((I+X)%2)@Ys.T))
print('|J|',len(J),'dimVJ',f2rank([x for t in J for x in RB[t]]),'|Jp|',len(Jp))
