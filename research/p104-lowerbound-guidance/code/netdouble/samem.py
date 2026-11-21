# NETDOUBLE samem (own code): SAME-M family of the E8-56 decoder (W=W0 X, V=V0 Y, X Y^T = I_8 mod 4, all give the same M mod 4).
# Prints rho_B, rho_A (Rado transversal ranks, random GF(2^16) lower bounds; E8 values must be 28/28), C, rank(I+X).
import sys, random, numpy as np
sys.path.insert(0,'../orbitlp')
from geo import Q
from ndlib import grank, rk2
Q=Q.astype(int); n=104
W0=np.load('../orbitlp/e8W.npy').astype(int)%4; V0=np.load('../orbitlp/e8V.npy').astype(int)%4
random.seed(1); rng=np.random.default_rng(1)
def rado(gens):  # gens[t] = list of 0/1 np vectors
    A=[]
    for gl in gens:
        row=[0]*n
        for g in gl:
            c=random.randrange(1,65536); row=[x^(c if v else 0) for x,v in zip(row,g)]
        A.append(row)
    return grank(A)
def rhos(W,V):
    a=W%2; b=V%2; m=W.shape[1]
    rB=rado([[b[:,k]*Q[t] for k in range(m) if W[t,k]] for t in range(n)])
    rA=rado([[a[:,k]*Q[:,p] for k in range(m) if V[p,k]] for p in range(n)])
    return rB,rA
def cost(W,V):
    return sum(rk2(Q[np.ix_(np.nonzero(W[:,k])[0],np.nonzero(V[:,k])[0])].tolist()) for k in range(W.shape[1]) if W[:,k].any() and V[:,k].any())
def inv4(P):
    m=P.shape[0]; A=np.concatenate([P%4,np.eye(m,dtype=int)],1)
    for c in range(m):
        p=next((i for i in range(c,m) if A[i,c]%2),None)
        if p is None: return None
        A[[c,p]]=A[[p,c]]; A[c]=(A[c]*(1 if A[c,c]%4==1 else 3))%4
        for i in range(m):
            if i!=c: A[i]=(A[i]-A[i,c]*A[c])%4
    return A[:,m:]
M0=(W0@V0.T)%4
if __name__=="__main__": print("E8 rho",rhos(W0,V0),"C",cost(W0,V0),flush=True)
if __name__=='__main__':
    for tr in range(int(sys.argv[2])):
        m=8+int(rng.integers(0,4))
        while True:
            X=rng.integers(0,4,(8,m)); Pi=inv4(X[:,:8])
            if Pi is not None: break
        Y=np.zeros((8,m),dtype=int); Y[:,:8]=Pi.T
        # kernel directions: Y += K with X K^T = 0 : K^T columns = kernel of X; use K = (cols 8.. free) 
        if m>8:
            Kf=rng.integers(0,4,(8,m-8))          # choose free part of K^T rows? build K (8 x m): K[:,8:]=Kf, K[:,:8] = -Kf X[:,8:]^T Pi^T ... solve X K^T=0
            KT=np.zeros((m,8),dtype=int); KT[8:,:]=Kf.T; KT[:8,:]=(-(Pi@(X[:,8:]@Kf.T)))%4
            assert not ((X@KT)%4).any()
            Y=(Y+KT.T)%4
        W=(W0@X)%4; V=(V0@Y)%4
        assert ((W@V.T)%4==M0).all()
        print(tr,'m',m,'C',cost(W,V),'rhoB,rhoA',rhos(W,V),flush=True)
    