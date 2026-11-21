# THINQ tq4: reduced type LP for the Q>=1 branch with T = Q + e thins (e = excess thins, each costs 1).
#  F = (2k-2) - e - sum_r x_r (1 - v_r),  v = (8D+1)^s - sum_L (8L)^s,  chat = 104 F / k.
#  rows: count n >= 2k-1 ; MAINS (all singletons, leaves included) >= 2k ;
#        RC2_l, l = 2..k (averaged; l=2 = singletons on DEGREE>=2 roles), rhs = (2-e) k   [P for e = 0 (CallerThin.rc2_pair_thin), e=1 Schur rank]
#  e=0: rhs 2k.  e=1: rhs k.  Types: D = 1..k, parts unrestricted (<= D).
import os, sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
s=.99
def HP(k): return 208/k*((k-2)*(17**s-16**s)+(8*k+1)**s-8**s*k)
def rows(k,D,P,ells):
    P=np.array(P,float); a=[(P==1).sum()]
    for l in ells:
        if D>=l: a.append((P[P<l]*(k-P[P<l])).sum()/(k-1))
        else: a.append((P*(D-P)).sum()/(k-1))
    return np.array(a)
def val(D,P): return (8*D+1)**s-sum((8*L)**s for L in P)
def price(k,wm,wl,ells,lam,mu=0.0,cl=0.0):
    ell=np.array(ells); out=[]
    for D in range(1,k+1):
        g=np.zeros(D)
        for i in range(D):
            L=i+1
            c=-(8*L)**s+wm*(L==1)
            deep=ell<=D
            c+=wl[deep&(ell>L)].sum()*L*(k-L)/(k-1)
            c+=wl[~deep].sum()*L*(D-L)/(k-1)
            g[i]=c
        best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
        for d in range(1,D+1):
            c=best[d-np.arange(1,d+1)]+g[:d];j=int(c.argmax());best[d]=c[j];arg[d]=j+1
        P=[];d=D
        while d>0:P.append(int(arg[d]));d-=arg[d]
        out.append(((8*D+1)**s+best[D]-1+lam+mu*(cl-(1 if D==1 else 0)),D,tuple(sorted(P))))
    return out
def solve(k,e,cl=None,maxit=800):
    # cl: leaf law d1 <= cl*T, T = n-2k+2+e  (cl=k: per-stage LEAF-RANK [P]; cl=1: global [CONJ]; None: off)
    ells=list(range(2,k+1)) if e<2 else []; rhs=np.r_[2*k,[(2-e)*k]*len(ells)]
    cols=list(dict.fromkeys([(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+
          [(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]))
    for it in range(maxit):
        c=-np.array([val(D,P)-1 for D,P in cols]); A=np.array([rows(k,D,P,ells) for D,P in cols]).T
        Aub=np.vstack([-A,-np.ones((1,len(cols)))]); bub=np.r_[-rhs,-(2*k-1)]
        if cl is not None:
            Aub=np.vstack([Aub,-np.array([cl-(1 if D==1 else 0) for D,P in cols])[None,:]]); bub=np.r_[bub,-cl*(2*k-2-e)]
        r=linprog(c,A_ub=Aub,b_ub=bub,method='highs')
        y=-r.ineqlin.marginals   # >= 0 duals of the >= rows
        wm=y[0]; wl=y[1:1+len(ells)]; lam=y[1+len(ells)]; mu=y[2+len(ells)] if cl is not None else 0.0
        pr=price(k,wm,wl,ells,lam,mu,cl or 0.0)
        new=[(sc,D,P) for sc,D,P in pr if sc>1e-9 and (D,P) not in cols]
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:10]]
    F=-r.fun+2*k-2-e
    sup=[(round(x,3),D,P if len(P)<9 else str(P[:8])+'..') for x,(D,P) in zip(r.x,cols) if x>1e-7]
    return F*104/k, sup, it
if __name__=='__main__':
    mode=sys.argv[1]
    for k in map(int,sys.argv[2:]):
        out=[f'k{k} HP {HP(k):.4f}']
        for e in (0,1,2):
            cl={'none':None,'P':k,'C':1}[mode]
            v,sup,it=solve(k,e,cl); out.append(f'e{e} {v:.4f}')
            if e==0: s0=sup
            if e==1: s1=sup
            if e==2: s2=sup
        print(mode,' | '.join(out),flush=True); print('   e0',s0[:6]); print('   e1',s1[:6]); print('   e2',s2[:6],flush=True)
