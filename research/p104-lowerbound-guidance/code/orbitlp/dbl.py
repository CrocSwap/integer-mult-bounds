"""ORBITLP dbl.py: check the DOUBLING LEMMA on a mod-4 decoder (W,V as .npy, 104 x m, entries mod 4).
Prints C, rank Y, rank Z, rank [[Y,E],[0,Z]], rank(I+X), |O|, rank (I+X)[O,O]; asserts the proved inequalities."""
import numpy as np, sys
from geo import Q
def rk2(M):
    M=np.array(M)%2; piv={}; r=0
    for row in M:
        x=int(''.join(map(str,row)),2)
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; r+=1; break
    return r
def run(W,V,name=''):
    W=W%4; V=V%4; n,m=W.shape; I=np.eye(n,dtype=int)
    assert not (((W@V.T-2*I)%4)*Q).any(), 'not a mod-4 decoder'
    a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2
    N=(a@b.T)*Q; assert not (N%2).any()
    X=(N//2)%2; Y=((w2@b.T)%2)*Q; Z=((a@v2.T)%2)*Q; E=((w2@v2.T)%2)*Q
    assert not ((Y+Z+I+X)%2).any()
    C=0
    for k in range(m):
        Dk=np.nonzero(W[:,k])[0]; Sk=np.nonzero(V[:,k])[0]
        if len(Dk) and len(Sk): C+=rk2(Q[np.ix_(Dk,Sk)])
    big=np.block([[Y,E],[np.zeros_like(Y),Z]]); rb=rk2(big); ry=rk2(Y); rz=rk2(Z); rix=rk2(I+X)
    O=[t for t in range(n) if a[t].any() and b[t].any()]
    ro=rk2((I+X)[np.ix_(O,O)]) if O else 0
    assert rix==n-len(O)+ro
    assert C>=rb>=ry+rz>=rix, (C,rb,ry,rz,rix)
    print('%-12s C=%d  rk[[Y,E],[0,Z]]=%d  rkY+rkZ=%d+%d  rk(I+X)=%d  |O|=%d  rk(I+X)_OO=%d  OK'%(name,C,rb,ry,rz,rix,len(O),ro))
if __name__=='__main__':
    run(np.load(sys.argv[1]),np.load(sys.argv[2]),sys.argv[3] if len(sys.argv)>3 else '')
def master(W,V,trials=20,seed=0):
    """random lower estimates of rho_B + rho_A (max over y_k ⊆ D_k, z_k ⊆ S_k); must stay <= C"""
    W=W%4; V=V%4; a=W%2; b=V%2; Dm=(W>0).astype(int); Sm=(V>0).astype(int); rng=np.random.default_rng(seed); best=0
    for _ in range(trials):
        y=(rng.random(Dm.shape)<0.5)*Dm; z=(rng.random(Sm.shape)<0.5)*Sm
        best=max(best,rk2(((y@b.T)%2)*Q)+rk2(((a@z.T)%2)*Q))
    return best
