# SCHERK sk1 (float SCOUT only, not evidence of impossibility): support-rank realisability of a mask family in normal form NF:
#   sum_r b_r a_r^T = G(A) = Etil diag(A_t+I) - 2I,  b_r,a_r supported on blocks M_r,  A_k = (-1)^(k+1) (A_{k-1}..A_1)^{-1}.
# usage: sk1.py k masks(comma, digits/letters 0-based, '*'=hub) starts [seed]
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import least_squares
signal.alarm(int(os.environ.get('AL','600')))
k=int(sys.argv[1]);D36='0123456789abcdefghijklmnopqrstuvwxyz'
masks=[list(range(k)) if m=='*' else sorted(D36.index(c) for c in m) for m in sys.argv[2].split(',')]
n=len(masks);assert n==2*k-2,(n,2*k-2)
NS=int(sys.argv[3]);rng=np.random.default_rng(int(sys.argv[4]) if len(sys.argv)>4 else 0)
idx=[np.concatenate([[2*t,2*t+1] for t in M]) for M in masks]
nab=sum(2*len(i) for i in idx);nA=4*(k-1)
def G_of(As):
    G=np.zeros((2*k,2*k))
    for s in range(k):
        for t in range(k):G[2*s:2*s+2,2*t:2*t+2]=(1 if s<=t else -1)*(As[t]+np.eye(2))
    return G-2*np.eye(2*k)
def unpack(z):
    As=[z[nab+4*i:nab+4*i+4].reshape(2,2) for i in range(k-1)];P=np.eye(2)
    for a in As:P=a@P
    As=As+[(-1)**(k+1)*np.linalg.inv(P)]
    S=np.zeros((2*k,2*k));i=0
    for ix in idx:
        d=len(ix);b=np.zeros(2*k);a=np.zeros(2*k);b[ix]=z[i:i+d];a[ix]=z[i+d:i+2*d];i+=2*d;S+=np.outer(b,a)
    return As,S
def res(z):
    As,S=unpack(z);r=(S-G_of(As)).ravel()
    # model: det A_t = 1, tr A_t != +-2 (no eigenvalue +-1); margin TM
    pen=[np.linalg.det(a)-1 for a in As[:-1]]+[max(0,TM-abs(np.trace(a)+2)) for a in As]+[max(0,TM-abs(np.trace(a)-2)) for a in As]
    return np.r_[r,pen]
best=1e9;TM=float(os.environ.get('TM','0.3'))
for st in range(NS):
    z=rng.normal(size=nab+nA)
    try:sol=least_squares(res,z,method='trf',max_nfev=3000,xtol=1e-15,ftol=1e-15,gtol=1e-15)
    except Exception as e:continue
    v=np.abs(sol.fun).max();best=min(best,v)
    if v<1e-10:
        As,_=unpack(sol.x);smin=min(np.linalg.svd(a)[1][-1] for a in As);em1=min(abs(np.linalg.eigvals(a)+1).min() for a in As)
        # rebuild V_t from the b,a vectors and check the product directly
        Bm=np.zeros((n,2*k));Am=np.zeros((n,2*k));i=0
        for r,ix in enumerate(idx):
            d=len(ix);Bm[r,ix]=sol.x[i:i+d];Am[r,ix]=sol.x[i+d:i+2*d];i+=2*d
        R=np.eye(n)
        for t in range(k):R=(np.eye(n)+Am[:,2*t:2*t+2]@Bm[:,2*t:2*t+2].T)@R
        print('SOLVED start',st,'res',f'{v:.1e}','min sv(A_t)',f'{smin:.2e}','min|eig+1|',f'{em1:.2e}','|prod+I|',f'{abs(R+np.eye(n)).max():.1e}',flush=True)
        if smin>1e-3 and em1>1e-3:break
print('k',k,'n',n,'sumD',sum(map(len,masks)),'k^2',k*k,'eqs',4*k*k,'unk',nab+nA,'best',f'{best:.2e}',flush=True)
