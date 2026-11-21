"""ORBITLP carry2.py: carry pieces under random GL8(Z4) transforms of E8-56: test rank Y, rank Z vs C/2."""
import numpy as np, random
from geo import *
from carry import rk2
W0=np.load('e8W.npy'); V0=np.load('e8V.npy')
def price(W,V):
    return [rk2(Q[np.ix_(np.nonzero(W[:,k]%4)[0],np.nonzero(V[:,k]%4)[0])]) for k in range(W.shape[1])]
def pieces(W,V):
    a=W%2; w2=(W//2)%2; b=V%2; v2=(V//2)%2; m=W.shape[1]
    cnt=sum(np.outer(a[:,k],b[:,k])*Q for k in range(m)); X=((cnt//2)%2)*Q
    Y=sum(np.outer(w2[:,k],b[:,k])*Q for k in range(m))%2
    Z=sum(np.outer(a[:,k],v2[:,k])*Q for k in range(m))%2
    return rk2(X),rk2(Y),rk2(Z),rk2(np.eye(104,dtype=int)+X)
rng=np.random.default_rng(1)
def rand_gl():
    while True:
        g=rng.integers(0,4,(8,8))
        if round(abs(np.linalg.det(g)))%2==1: break
    # inverse mod 4 via adjugate
    from sympy import Matrix
    gi=np.array(Matrix(g).inv_mod(4)).astype(int)
    return g,gi
for trial in range(6):
    g,gi=rand_gl()
    W=(W0@g)%4; V=(V0@gi.T)%4
    Mm=(W@V.T)%4; assert ((Mm-(W0@V0.T))%4==0).all()
    p=price(W,V); C=sum(p)
    print('C',C,'X,Y,Z,I+X ranks',pieces(W,V))
# sparse transforms: elementary
for trial in range(6):
    g=np.eye(8,dtype=int); i,j=rng.choice(8,2,replace=False); g[i,j]=rng.integers(1,4)
    from sympy import Matrix
    gi=np.array(Matrix(g).inv_mod(4)).astype(int)
    W=(W0@g)%4; V=(V0@gi.T)%4
    p=price(W,V); print('elem C',sum(p),p,'ranks',pieces(W,V))
