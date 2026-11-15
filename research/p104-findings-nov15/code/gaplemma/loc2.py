"""GAPLEMMA loc2.py [N]: LOCAL relaxation of pair k=1 d=2 + slack 0..2 (K=3).
coords: H=0,1  E0=2,3  s=4  D=5,6  E2=7,8.  stages 0,1,2 masks Z0={0..4}, Z1={0..6}, Z2={0..8}; units 2 per stage.
Constraints: x_i.y_i=0; Lemma S: y_i.x_j = sgn(i-j) w_i.z_j (i!=j), w_i.z_i=1; P3=T5..T0 block-diag wrt Delta={4,5,6};
B = V3 cap R^Delta of dim 2 with sum-zero coefficients (Z^T beta=0): X beta1 = e_s, X beta2 = e_5 + u e_6."""
import numpy as np, sys
from scipy.optimize import least_squares
n=9; Dl=[4,5,6]; Zr=[0,1,2,3,7,8]
masks=[list(range(5)),list(range(7)),list(range(9))]
sup=[masks[i//2] for i in range(6)]
offs=[];o=0
for s_ in sup: offs.append(o); o+=2*len(s_)
nxy=o; dim=nxy+24+12+1
def unpack(z):
    X=np.zeros((n,6));Y=np.zeros((n,6))
    for i,s_ in enumerate(sup):
        k=len(s_);X[s_,i]=z[offs[i]:offs[i]+k];Y[s_,i]=z[offs[i]+k:offs[i]+2*k]
    W=z[nxy:nxy+12].reshape(6,2);Zm=z[nxy+12:nxy+24].reshape(6,2)
    b1=z[nxy+24:nxy+30];b2=z[nxy+30:nxy+36];u=z[-1]
    return X,Y,W,Zm,b1,b2,u
def res(z):
    X,Y,W,Zm,b1,b2,u=unpack(z); r=[]
    G=Y.T@X; K=W@Zm.T
    for i in range(6):
        for j in range(6):
            if i==j: r.append(G[i,i]); r.append(K[i,i]-1)
            else: r.append(G[i,j]-np.sign(i-j)*K[i,j])
    P=np.eye(n)
    for i in range(6): P=(np.eye(n)-2*np.outer(X[:,i],Y[:,i]))@P
    r+=list(P[np.ix_(Zr,Dl)].ravel())+list(P[np.ix_(Dl,Zr)].ravel())
    e=np.zeros(n);e[4]=1; r+=list(X@b1-e)
    e=np.zeros(n);e[5]=1;e[6]=u; r+=list(X@b2-e)
    r+=list(Zm.T@b1)+list(Zm.T@b2)
    return np.array(r)
def diag(z):
    X,Y,W,Zm,b1,b2,u=unpack(z); G=Y.T@X
    t=[G[2*s,2*s+1]*G[2*s+1,2*s] for s in range(3)]
    P=np.eye(n)
    for i in range(6): P=(np.eye(n)-2*np.outer(X[:,i],Y[:,i]))@P
    sv=np.linalg.svd(X,compute_uv=False)
    return t,np.round(np.linalg.eigvals(P[np.ix_(Dl,Dl)]),6),sv[-1],np.linalg.matrix_rank(X[Zr],1e-8)
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
ok=0
for trial in range(40):
    z0=rng.normal(size=dim)
    sol=least_squares(res,z0,method='trf',max_nfev=3000,xtol=1e-15,ftol=1e-15)
    m=np.abs(res(sol.x)).max()
    if m<1e-9:
        ok+=1; t,ev,smin,rk=diag(sol.x)
        print(trial,'res %.1e'%m,'t',np.round(t,3),'eigDelta',ev,'smin X %.2e'%smin,'rankXZ',rk)
        np.save('loc2_sol%d.npy'%trial,sol.x)
    else: print(trial,'fail %.1e'%m)
print('solved',ok)
