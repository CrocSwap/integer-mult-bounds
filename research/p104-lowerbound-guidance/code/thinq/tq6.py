# THINQ tq6: exact dual certificate (mpmath-50, exhaustive DP over ALL partitions of every D<=k) for the e=0 LP with the
# per-stage leaf row (cl=k) or none / global (cl=1).  Rows re-derived here from definitions; float duals from tq4 only as a guess.
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
from mpmath import mp,mpf
mp.dps=50
import numpy as np
from scipy.optimize import linprog
import tq4
S=mpf('0.99')
def pw(x): return mpf(x)**S
def dual_float(k,e,cl):
    # re-solve and return float duals (wm, wl[l=2..k], lam, mu)
    ells=list(range(2,k+1)); rhs=np.r_[2*k,[(2-e)*k]*len(ells)]
    v,sup,_=tq4.solve(k,e,cl)
    # rebuild final LP on the support's full colgen columns is internal; re-run a fresh colgen and capture duals
    cols=list(dict.fromkeys([(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+
          [(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]))
    for it in range(800):
        c=-np.array([tq4.val(D,P)-1 for D,P in cols]); A=np.array([tq4.rows(k,D,P,ells) for D,P in cols]).T
        Aub=np.vstack([-A,-np.ones((1,len(cols)))]); bub=np.r_[-rhs,-(2*k-1)]
        if cl is not None:
            Aub=np.vstack([Aub,-np.array([cl-(1 if D==1 else 0) for D,P in cols])[None,:]]); bub=np.r_[bub,-cl*(2*k-2-e)]
        r=linprog(c,A_ub=Aub,b_ub=bub,method='highs'); y=-r.ineqlin.marginals
        wm=y[0]; wl=y[1:1+len(ells)]; lam=y[1+len(ells)]; mu=y[2+len(ells)] if cl is not None else 0.0
        pr=tq4.price(k,wm,wl,ells,lam,mu,cl or 0.0)
        new=[(sc,D,P) for sc,D,P in pr if sc>1e-10 and (D,P) not in cols]
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:10]]
    return v,wm,wl,lam,mu
def certify(k,e,cl):
    v,wm,wl,lam,mu=dual_float(k,e,cl)
    wm=mpf(max(wm,0)); wl=[mpf(max(x,0)) for x in wl]; lam=mpf(max(lam,0)); mu=mpf(max(mu,0)); ells=list(range(2,k+1))
    c=mpf(cl) if cl is not None else mpf(0)
    # suffix sums for deep weights: Wdeep(L) = sum_{l>L, l<=D} w_l ; shallow: sum_{l>D} w_l
    def maxprofit():
        best_all=mpf(-10**9)
        W=[sum(wl[l-2] for l in ells if l>x) for x in range(k+1)]
        for D in range(1,k+1):
            g=[]
            for L in range(1,D+1):
                t=-pw(8*L)+(wm if L==1 else 0)
                t+=(W[L]-W[D])*L*(k-L)/mpf(k-1)
                t+=W[D]*L*(D-L)/mpf(k-1)
                g.append(t)
            b=[mpf(0)]+[None]*D
            for d in range(1,D+1): b[d]=max(b[d-L]+g[L-1] for L in range(1,d+1))
            prof=pw(8*D+1)+b[D]-1+lam+mu*(c-(1 if D==1 else 0))
            best_all=max(best_all,prof)
        return best_all
    eps=maxprofit()
    # make dual feasible: lower lam by eps (if eps>0); bound F <= 2k-2-e - y.b
    # any solution with F>=0 has sum of deficits <= 2k-2, each role deficit >= 1-v1 (v1 = 9^s-8^s is the max role value),
    # so n <= (2k-2)/(1-v1); infeasibility eps costs at most eps*n.
    nmax=(2*k-2)/(1-(pw(9)-pw(8)))
    yb=wm*2*k+sum(wl)*(2-e)*k+lam*(2*k-1)+mu*c*(2*k-2-e)
    F=2*k-2-e-yb+max(eps,0)*nmax
    return mpf(104)*F/k, v, eps
if __name__=='__main__':
    mode=sys.argv[1]; e=0
    for k in map(int,sys.argv[2:]):
        cl={'none':None,'P':k,'C':1}[mode]
        bound,v,eps=certify(k,e,cl)
        print(f'{mode} e{e} k{k}: float LP {v:.6f}  CERTIFIED chat <= {mp.nstr(bound,12)}  (pricing slack {mp.nstr(eps,3)})',flush=True)
