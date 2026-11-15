"""GAPLEMMA locgen.py [N]: generic LOCAL relaxation of the left arm up to stage K-1.
args: spec name, seed, trials.  Constraints: x.y=0; Lemma S (W,Z); P_K block-diag wrt Delta; b vectors beta_i with
X[~Delta]beta_i=0, Z^T beta_i=0, beta^T beta = I; F1 (X and Y) for j=0..K-1 via C_j [X_<=j, e_H] = I; t_s != -1."""
import numpy as np, sys
from scipy.optimize import least_squares
SPECS={
 # coords listed; masks per stage; Delta; b
 'A1': dict(n=7, masks=[[0,1,2,3,4],[0,1,2,3,4,5,6]], Dl=[4,5], b=1),      # c=1 k=1 d=1 slack 0..1: H01 E0 23 s4 D5 e1 6
 'A2': dict(n=9, masks=[[0,1,2,3,4],[0,1,2,3,4,5,6],list(range(9))], Dl=[4,5], b=1),  # c=1 k=1 d=2 slack 0..2 (E2=7,8)
 'A2b2': dict(n=9, masks=[[0,1,2,3,4],[0,1,2,3,4,5,6],list(range(9))], Dl=[4,5], b=2),
 'P2': dict(n=9, masks=[[0,1,2,3,4],[0,1,2,3,4,5,6],list(range(9))], Dl=[4,5,6], b=2), # c=2 k=1 d=2 slack 0..2 (killed: control)
}
sp=SPECS[sys.argv[1]]; n=sp['n']; masks=sp['masks']; Dl=sp['Dl']; b=sp['b']; K=len(masks); NU=2*K
Zr=[i for i in range(n) if i not in Dl]
sup=[masks[i//2] for i in range(NU)]
offs=[];o=0
for s_ in sup: offs.append(o); o+=2*len(s_)
nxy=o; o+=4*NU; ob=o; o+=b*NU; oc=o
csz=[(2*j+4)*(len(masks[j])) for j in range(K)]
o+=2*sum(csz); ot=o; o+=K; dim=o
H=np.zeros((n,2));H[0,0]=H[1,1]=1
def unpack(z):
    X=np.zeros((n,NU));Y=np.zeros((n,NU))
    for i,s_ in enumerate(sup):
        k=len(s_);X[s_,i]=z[offs[i]:offs[i]+k];Y[s_,i]=z[offs[i]+k:offs[i]+2*k]
    W=z[nxy:nxy+2*NU].reshape(NU,2);Zm=z[nxy+2*NU:nxy+4*NU].reshape(NU,2)
    B=z[ob:ob+b*NU].reshape(NU,b)
    return X,Y,W,Zm,B
def res(z):
    X,Y,W,Zm,B=unpack(z); r=[]; G=Y.T@X; Kk=W@Zm.T
    for i in range(NU):
        for j in range(NU):
            if i==j: r+=[G[i,i],Kk[i,i]-1]
            else: r.append(G[i,j]-np.sign(i-j)*Kk[i,j])
    P=np.eye(n)
    for i in range(NU): P=(np.eye(n)-2*np.outer(X[:,i],Y[:,i]))@P
    r+=list(P[np.ix_(Zr,Dl)].ravel())+list(P[np.ix_(Dl,Zr)].ravel())
    r+=list((X[Zr]@B).ravel())+list((Zm.T@B).ravel())+list((B.T@B-np.eye(b)).ravel())
    o=oc
    for M in (X,Y):
        for j in range(K):
            m=masks[j]; A=np.hstack([M[m][:,:2*j+2],H[m]]); C=z[o:o+csz[j]].reshape(2*j+4,len(m)); o+=csz[j]
            r+=list((C@A-np.eye(2*j+4)).ravel())
    for s in range(K): r.append(z[ot+s]*(1+G[2*s,2*s+1]*G[2*s+1,2*s])-1)
    return np.array(r)
rng=np.random.default_rng(int(sys.argv[2])); ok=0; best=[]
for trial in range(int(sys.argv[3])):
    sol=least_squares(res,rng.normal(size=dim),method='trf',max_nfev=3000,xtol=1e-15,ftol=1e-15,gtol=1e-15)
    m=np.abs(res(sol.x)).max(); best.append(m); print(trial,'%.2e'%m,flush=True)
    if m<1e-9: ok+=1; np.save('loc_%s_%d.npy'%(sys.argv[1],trial),sol.x)
print('spec',sys.argv[1],'solved',ok,'of',len(best),'best %.2e'%min(best))
