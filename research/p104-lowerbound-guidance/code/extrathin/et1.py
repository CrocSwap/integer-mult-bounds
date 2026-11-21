# EXTRATHIN et1: Q>=1 reduced type LP with e excess thins, rows:
#  count n>=2k-1; MAINS (all singletons) >= 2k; DEEP (singletons on D>=2) >= 2k - e  [P new: DEFICIT law];
#  RC2_l l=3..k averaged, rhs rho*k (rho = pair-rank average lower bound); leaf: d1 <= k*T, T = n-2k+2+e.
#  F = 2k-2-e - sum x (1-v);  chat = 104 F/k.
import os, sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
s=.99
def val(D,P): return (8*D+1)**s-sum((8*L)**s for L in P)
def rows(k,D,P,ells):
    P=np.array(P,float); a=[(P==1).sum(), (P==1).sum() if D>=2 else 0]
    for l in ells:
        if D>=l: a.append((P[P<l]*(k-P[P<l])).sum()/(k-1))
        else: a.append((P*(D-P)).sum()/(k-1))
    return np.array(a)
def price(k,y,ells,lam,mu):
    wm,wd=y[0],y[1]; wl=np.array(y[2:2+len(ells)]); ell=np.array(ells,int); out=[]
    for D in range(1,k+1):
        g=np.zeros(D)
        for i in range(D):
            L=i+1; c=-(8*L)**s+(wm+(wd if D>=2 else 0))*(L==1)
            if len(ell):
                deep=ell<=D
                c+=wl[deep&(ell>L)].sum()*L*(k-L)/(k-1)+wl[~deep].sum()*L*(D-L)/(k-1)
            g[i]=c
        best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
        for d in range(1,D+1):
            c=best[d-np.arange(1,d+1)]+g[:d];j=int(c.argmax());best[d]=c[j];arg[d]=j+1
        P=[];d=D
        while d>0:P.append(int(arg[d]));d-=arg[d]
        out.append(((8*D+1)**s+best[D]-1+lam+mu*(k-(1 if D==1 else 0)),D,tuple(sorted(P))))
    return out
def solve(k,e,rho,leaf=True,maxit=2000):
    ells=list(range(3,k+1)) if rho>0 else []
    rhs=np.r_[2*k,2*k-e,[rho*k]*len(ells)]
    cols=list(dict.fromkeys([(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+
          [(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]))
    for it in range(maxit):
        c=-np.array([val(D,P)-1 for D,P in cols]); A=np.array([rows(k,D,P,ells) for D,P in cols]).T
        Aub=np.vstack([-A,-np.ones((1,len(cols)))]); bub=np.r_[-rhs,-(2*k-1)]
        if leaf:
            Aub=np.vstack([Aub,-np.array([k-(1 if D==1 else 0) for D,P in cols])[None,:]]); bub=np.r_[bub,-k*(2*k-2-e)]
        r=linprog(c,A_ub=Aub,b_ub=bub,method='highs')
        if r.status!=0: return None,None,it
        y=-r.ineqlin.marginals
        lam=y[2+len(ells)]; mu=y[3+len(ells)] if leaf else 0.0
        pr=price(k,y,ells,lam,mu)
        new=[(sc,D,P) for sc,D,P in pr if sc>1e-9 and (D,P) not in cols]
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:10]]
    F=-r.fun+2*k-2-e
    sup=[(round(x,3),D,P if len(P)<7 else str(P[:6])+'..') for x,(D,P) in zip(r.x,cols) if x>1e-7]
    return F*104/k, sup, it
if __name__=='__main__':
    mode=sys.argv[1]; ks=list(map(int,sys.argv[2:]))
    for k in ks:
        out=[f'k{k}']
        for e in range(0,7):
            if k<e+2: break
            rho={'proved':max(2-e,0),'full':2,'conj':(4*k/(2+e)-2)/(k-1)}[mode]
            v,sup,it=solve(k,e,rho); out.append(f'e{e} {v:.3f}')
            if e in (1,2): out.append(str(sup[:4]))
        print(mode,' | '.join(out),flush=True)
