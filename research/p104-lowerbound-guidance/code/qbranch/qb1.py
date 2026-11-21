# QBRANCH qb1: reduced LP {count, MAINS, RC2_l l=3..k} for Q=0 (control, = HP) and Q>=1 (D>=1, L<=k, n>=2k-1, -1 per role). float, column generation.
import os
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import sys, numpy as np
from scipy.optimize import linprog
s=.99
def HP(k): return 208/k*((k-2)*(17**s-16**s)+(8*k+1)**s-8**s*k)
def rows(k,D,P,ells):
    P=np.array(P); sq=(P*P).sum()
    a=[(P==1).sum()]
    for l in ells:
        if D>=l: a.append((P[P<l]*(k-P[P<l])).sum()/(k-1))
        else: a.append((D*D-sq)/(k-1))
    return np.array(a,float)
def val(D,P): return (8*D+1)**s-sum((8*L)**s for L in P)
def price(k,w,y,ells,Dmin,Lmax,cq):
    # score = v - cq_sub + w.rows + y ; maximize over types; returns best per D
    L=np.arange(1,Lmax+1,dtype=float); wm=w[0]; wl=np.array(w[1:]); out=[]
    ell=np.array(ells)
    for D in range(Dmin,k+1):
        Lm=min(D,Lmax); Ls=L[:Lm]
        g=np.zeros(Lm)
        for i,Li in enumerate(Ls):
            c=-(8*Li)**s+wm*(Li==1)
            deep=ell<=D
            c+=(wl[deep&(ell>Li)]).sum()*Li*(k-Li)/(k-1)
            c+=(wl[~deep]).sum()*Li*(D-Li)/(k-1)
            g[i]=c
        best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
        for d in range(1,D+1):
            m=min(d,Lm);c=best[d-np.arange(1,m+1)]+g[:m];i=int(c.argmax());best[d]=c[i];arg[d]=i+1
        P=[];d=D
        while d>0:P.append(arg[d]);d-=arg[d]
        out.append((best[D]+(8*D+1)**s+y,D,tuple(sorted(P))))
    return out
def solve(k,Q0,maxit=600):
    ells=list(range(3,k+1)); Dmin=2 if Q0 else 1; Lmax=k-2 if (Q0 and k>=3) else k
    n=2*k-2 if Q0 else 2*k-1; sub=0 if Q0 else 1
    rhs=np.array([2*k]*(1+len(ells)),float)
    cols=[(D,tuple([1]*D)) for D in range(Dmin,k+1)]+[(2,(2,)) ,(2,(1,1))]
    cols=list(dict.fromkeys(cols))
    for it in range(maxit):
        c=-np.array([val(D,P)-sub for D,P in cols]);A=np.array([rows(k,D,P,ells) for D,P in cols]).T
        if Q0: r=linprog(c,A_ub=-A,b_ub=-rhs,A_eq=np.ones((1,len(cols))),b_eq=[n],method='highs')
        else:  r=linprog(c,A_ub=np.vstack([-A,-np.ones((1,len(cols)))]),b_ub=np.r_[-rhs,-n],method='highs')
        w=-r.ineqlin.marginals[:len(rhs)]
        y=r.eqlin.marginals[0] if Q0 else -r.ineqlin.marginals[-1]
        # reduced score of type: v-sub + w.a + y ?  (Q0: y is multiplier of count eq: score=v+w.a - (-y)?) -> use sign check below
        pr=price(k,w,0,ells,Dmin,Lmax,0)
        yy=-r.eqlin.marginals[0] if Q0 else -r.ineqlin.marginals[-1]*(-1)
        # dual of max problem: reduced cost of col j = -(c_j) - ... ; simply test improvement via recomputed score
        # score_j = (v_j - sub) + w.a_j - lam, lam = count multiplier (>=0 for >=, free for =)
        lam = -r.eqlin.marginals[0] if Q0 else -r.ineqlin.marginals[-1]
        # scipy marginals are d(obj)/d(rhs) for min of -F: for eq, marginal m => lam_F = -m ... derive empirically below
        new=[(sc-sub-lam_,D,P) for sc,D,P in pr for lam_ in [None] if False]
        new=[]
        for sc,D,P in pr:
            sc2=sc-sub-(lam)  # sc includes (8D+1)^s - pieces + w.rows
            if sc2>1e-9 and (D,P) not in cols: new.append((sc2,D,P))
        new.sort(reverse=True)
        if not new: break
        cols+= [(D,P) for _,D,P in new[:12]]
    F=-r.fun+(0 if Q0 else 2*k-2)
    return F*104/k, [(round(x,3),D,P) for x,(D,P) in zip(r.x,cols) if x>1e-7]
if __name__=='__main__':
    for k in map(int,sys.argv[1:]):
        c0,s0=solve(k,True); c1,s1=solve(k,False)
        print(k,'HP',round(HP(k),4),'Q0 LP',round(c0,4),'Qge1 LP',round(c1,4)); print('  Q0 sup',s0[:8]); print('  Q1 sup',s1[:10],flush=True)
