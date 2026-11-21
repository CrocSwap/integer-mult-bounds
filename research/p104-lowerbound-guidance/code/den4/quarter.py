"""DEN4 quarter.py (own code): exact check of the quarter-level carry identity and the quarter master bound."""
import numpy as np, sys
from qlib import *
def G(x,y,Q): return ((x@y.T)*Q)%2
def Gh(x,y,Q): return (x@y.T)*Q
def quarter(e,W,V,pr,Q,name='',verbose=True):
    assert e==2
    n=len(Q); I=np.eye(n,dtype=np.int64)
    Mm=((W@V.T)*Q)%8; assert ((Mm-4*I*Q)%8==0).all(), 'not a mod-8 quarter decoder'
    r8W=W%8; r8V=V%8
    a=r8W%2; a1=(r8W>>1)&1; c=np.isin(r8W,[4,5]).astype(np.int64); eW=np.where(np.isin(r8W,[6,7]),-1,1)
    b=r8V%2; b1=(r8V>>1)&1; d=np.isin(r8V,[4,5]).astype(np.int64); eV=np.where(np.isin(r8V,[6,7]),-1,1)
    N=Gh(a,b,Q); assert (N%2==0).all()                      # level 0
    X0=(N//2)%2; Y=G(a1,b,Q); Z=G(a,b1,Q)
    assert ((Y+Z+X0)%2==0).all()                             # level 1
    P=N+2*Gh(eW*a1,b,Q)+2*Gh(a,eV*b1,Q); assert (P%4==0).all()
    K=(P//4+N//2)%2; D4=(G(c,b,Q)+G(a,d,Q))%2
    T=(I+K+D4)%2
    assert (T==G((a+a1)%2,(b+b1)%2,Q)).all()                 # level 2 (quarter carry identity)
    E=G(a1,b1,Q)
    Cst=sum(pr); ry=rk2(Y); rz=rk2(Z); rT=rk2(T); rIK=rk2((I+K)%2)
    big=np.block([[Y,E],[np.zeros_like(Y),Z]]); rb=rk2(big)
    big2=np.block([[Y,T],[np.zeros_like(Y),Z]]); assert rk2(big2)==rb
    assert Cst>=rb>=max(ry+rz,rT), (Cst,rb,ry,rz,rT)
    res=dict(name=name,n=n,C=Cst,rows=len(pr),rkY=ry,rkZ=rz,rkX0=rk2(X0),rkT=rT,rkIK=rIK,rkD4=rk2(D4),master=rb)
    if verbose: print(res)
    return res
if __name__=='__main__':
    L=std_set('HS64'); Q=Q_std(L); n=len(L)
    U=[[0]*8 for _ in range(8)]
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)):
            U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
    rows=gram_rows_std(L,U); print('HS64 n',n,'decoder violations',check_decoder(rows,Q))
    e,W,V,pr,D,S=normalise(rows,Q); print('e',e,'prices',pr)
    quarter(e,W,V,pr,Q,'HS64-D8frame')
