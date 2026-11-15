"""GAPLEMMA refac.py [N]: REDUCTION test. Target T = diag(M', -I_Delta), M' = S'_1 S'_0 a generic 2-stage prefix on the 7 Z-coords
{H0,1 E0 2,3 e1 6 E2 7,8} with masks Z'_0, Z'_1 (arg). Find family-A d=2 left arm (stages on {0..4},{0..6},{0..8}; s=4, D=5) with
product T exactly (x.y=0). If solvable for generic M', the rest of the caller only sees M' and family A d=2 exists iff the
non-dying layout L' (first two stages replaced by S'_0,S'_1) has a root."""
import numpy as np, sys
from scipy.optimize import least_squares
n=9; Zc=[0,1,2,3,6,7,8]; Dl=[4,5]
masks=[list(range(5)),list(range(7)),list(range(9))]; sup=[masks[i//2] for i in range(6)]
offs=[];o=0
for s_ in sup: offs.append(o); o+=2*len(s_)
dim=o
def tv(x,y): return np.eye(len(x))-2*np.outer(x,y)
def iso_pair(rng,m):
    while True:
        x=np.zeros(n);y=np.zeros(n);x[m]=rng.normal(size=len(m));y[m]=rng.normal(size=len(m)); y-= (x@y)/(x@x)*x; return x,y
def target(rng,mk0,mk1):
    M=np.eye(n)
    for mk in (mk0,mk0,mk1,mk1):
        x,y=iso_pair(rng,mk); M=tv(x,y)@M
    T=M.copy(); T[np.ix_(Dl,Dl)]=-np.eye(2); return T
def unpack(z):
    X=np.zeros((n,6));Y=np.zeros((n,6))
    for i,s_ in enumerate(sup):
        k=len(s_);X[s_,i]=z[offs[i]:offs[i]+k];Y[s_,i]=z[offs[i]+k:offs[i]+2*k]
    return X,Y
def prod(z):
    X,Y=unpack(z);P=np.eye(n)
    for i in range(6): P=tv(X[:,i],Y[:,i])@P
    return P,X,Y
mode=sys.argv[1]; rng=np.random.default_rng(int(sys.argv[2]))
mk0={'A':[0,1,2,3],'B':[0,1,2,3,6],'C':Zc}[mode]; mk1=Zc
for tgt in range(int(sys.argv[3])):
    T=target(rng,mk0,mk1); best=9
    def res(z):
        P,X,Y=prod(z); return np.concatenate([(P-T).ravel(),np.sum(X*Y,0)])
    for st in range(int(sys.argv[4])):
        sol=least_squares(res,rng.normal(size=dim),method='trf',max_nfev=4000,xtol=1e-15,ftol=1e-15,gtol=1e-15)
        m=np.abs(res(sol.x)).max(); best=min(best,m)
        if m<1e-10:
            P,X,Y=prod(sol.x); G=Y.T@X; t=[G[2*s,2*s+1]*G[2*s+1,2*s] for s in range(3)]
            print('target',tgt,'start',st,'SOLVED %.1e'%m,'t',np.round(t,3),flush=True); np.save('refac_%s_%d.npy'%(mode,tgt),np.concatenate([sol.x,T.ravel()])); break
    else: print('target',tgt,'unsolved best %.1e'%best,flush=True)
