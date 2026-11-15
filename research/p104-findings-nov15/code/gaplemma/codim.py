"""GAPLEMMA codim.py [N]: at the family-A d=2 local root (loc_A2b2_7), dimension of the set of M = P_3|Z reachable by the left arm
with P_3 = diag(M, -I_Delta) (supports + x.y = 0 only), vs the 40-dim variety {M on R^7 : rank(M-I) = 4}."""
import numpy as np, sys
sys.argv=['x','A2b2','0','0']; exec(open('locgen.py').read().split('rng=')[0])
z=np.load('loc_A2b2_7.npy'); u=z[:nxy]
Zc=[i for i in range(n) if i not in Dl]
def F(u):
    zz=z.copy(); zz[:nxy]=u; X,Y,W,Zm,B=unpack(zz); P=np.eye(n)
    for i in range(NU): P=(np.eye(n)-2*np.outer(X[:,i],Y[:,i]))@P
    con=np.concatenate([np.sum(X*Y,0),(P[np.ix_(Dl,Dl)]+np.eye(2)).ravel(),P[np.ix_(Dl,Zc)].ravel(),P[np.ix_(Zc,Dl)].ravel()])
    return con,P[np.ix_(Zc,Zc)].ravel()
def jac(f,u,h=1e-6):
    c0,m0=f(u); Jc=np.zeros((len(c0),len(u))); Jm=np.zeros((len(m0),len(u)))
    for i in range(len(u)):
        e=np.zeros(len(u)); e[i]=h; c1,m1=f(u+e); c2,m2=f(u-e); Jc[:,i]=(c1-c2)/(2*h); Jm[:,i]=(m1-m2)/(2*h)
    return Jc,Jm
Jc,Jm=jac(F,u); print('constraint residual',np.abs(F(u)[0]).max())
sv=np.linalg.svd(Jc,compute_uv=False); rc=int((sv>1e-7*sv[0]).sum()); print('params',len(u),'constraint rank',rc)
_,_,Vt=np.linalg.svd(Jc); N=Vt[rc:].T
svm=np.linalg.svd(Jm@N,compute_uv=False); print('dim reachable M (tangent) =',int((svm>1e-7*svm[0]).sum()),' sv tail',np.round(svm[-6:],8))
