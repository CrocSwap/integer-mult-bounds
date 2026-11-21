# QBRANCH qb7: Q>=1 reduced LP {count>=2k-1 (-1 per role), MAINS>=2k, RC2_l l=3..k}, D>=1, L<=k.
# primal = closed-form chart (exact rows, mpmath-60), dual = cutting-plane float w scaled by (1-delta), verified by EXHAUSTIVE partition DP in mpmath-60.
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
from mpmath import mp,mpf
from fractions import Fraction
mp.dps=60
s=mpf('0.99'); sf=.99
def pw(x): return mpf(x)**s
def HP0(k): return mpf(208)/k*((k-2)*(pw(17)-pw(16))+pw(8*k+1)-pw(8)*k)
def chart(k):
    a=k%2; b=k//2   # hub (k, 2^b 1^a)
    rho=Fraction(b*2*(k-2)+a*(k-1),k-1)       # RC2_l coverage of one hub, l>=3
    xh=Fraction(2*k)/rho; x1=2*k-a*xh
    assert x1>=0
    vh=pw(8*k+1)-b*pw(16)-a*pw(8); v1=pw(9)-pw(8)
    F=mpf(x1.numerator)/x1.denominator*(v1-1)+mpf(xh.numerator)/xh.denominator*(vh-1)+2*k-2
    return F*104/k, x1, xh
# ---------- float machinery for dual search
def rows_f(k,D,P,ells):
    P=np.array(P); sq=(P*P).sum(); a=[(P==1).sum()]
    for l in ells:
        a.append((P[P<l]*(k-P[P<l])).sum()/(k-1) if D>=l else (D*D-sq)/(k-1))
    return np.array(a,float)
def val_f(D,P): return (8*D+1)**sf-sum((8*L)**sf for L in P)
def price_f(k,w,ells):
    wm=w[0]; wl=np.array(w[1:]); ell=np.array(ells); out=[]
    for D in range(1,k+1):
        Ls=np.arange(1,D+1,dtype=float); g=np.zeros(D)
        deep=ell<=D
        for i,Li in enumerate(Ls):
            g[i]=-(8*Li)**sf+wm*(Li==1)+(wl[deep&(ell>Li)]).sum()*Li*(k-Li)/(k-1)+(wl[~deep]).sum()*Li*(D-Li)/(k-1)
        best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
        for d in range(1,D+1):
            c=best[d-np.arange(1,d+1)]+g[:d];i=int(c.argmax());best[d]=c[i];arg[d]=i+1
        P=[];d=D
        while d>0:P.append(arg[d]);d-=arg[d]
        out.append((best[D]+(8*D+1)**sf-1,D,tuple(sorted(P))))
    return out
def dual_search(k,sign=-1):
    ells=list(range(3,k+1)); wm=1-(9**sf-8**sf)
    a=k%2;b=k//2; Ph=tuple([2]*b+[1]*a)
    cols=[(D,tuple([1]*D)) for D in range(1,k+1)]+[(D,(D,)) for D in range(1,k+1)]+[(D,tuple([2]*(D//2)+[1]*(D%2))) for D in range(2,k+1)]
    cols=list(dict.fromkeys(cols))
    for it in range(500):
        R=[rows_f(k,D,Pc,ells) for D,Pc in cols]
        A=np.array([r[1:] for r in R]); b_=np.array([1-val_f(D,Pc)-wm*r[0] for (D,Pc),r in zip(cols,R)])
        rh=rows_f(k,k,Ph,ells); 
        r=linprog(np.array(ells,float)*sign,A_ub=A,b_ub=b_,A_eq=rh[1:][None,:],b_eq=[1-val_f(k,Ph)-wm*rh[0]],bounds=(0,None),method='highs')
        if r.status!=0: return None
        w=np.r_[wm,r.x]; pr=price_f(k,w,ells)
        viol=[(sc,D,Pc) for sc,D,Pc in pr if sc>1e-13 and (D,Pc) not in cols]
        if not viol: return r.x,ells
        cols+=[(D,Pc) for _,D,Pc in sorted(viol,reverse=True)[:10]]
    return None
# ---------- exact mp verification of a dual (wm,w) : exhaustive partition DP
def mp_maxPhi(k,wm,w,ells):
    # Phi(D,P)=v-1+wm*m+sum_l w_l rho_l ; per-piece additive given D
    p8={L:pw(8*L) for L in range(1,k+1)}; best_over=mpf('-1e9'); arg=None
    for D in range(1,k+1):
        g=[]
        for L in range(1,D+1):
            c=-p8[L]+(wm if L==1 else 0)
            for l,wl in zip(ells,w):
                if wl==0: continue
                if D>=l:
                    if L<l: c+=wl*L*(k-L)/mpf(k-1)
                else: c+=wl*L*(D-L)/mpf(k-1)
            g.append(c)
        best=[mpf(0)]+[None]*D
        for d in range(1,D+1):
            best[d]=max(best[d-L]+g[L-1] for L in range(1,d+1))
        m=pw(8*D+1)-1+best[D]
        if m>best_over: best_over=m; arg=D
    return best_over,arg
def certify(k,sign=-1):
    out=dual_search(k,sign)
    if out is None: return None
    x,ells=out; wm0=1-(pw(9)-pw(8)); w0=[mpf(float(t)) for t in x]
    for dl in [mpf(10)**-12,mpf(10)**-10,mpf(10)**-9,mpf(10)**-8,mpf(10)**-7,mpf(10)**-6]:
        wm=(1-dl)*wm0; w=[(1-dl)*t for t in w0]
        mx,arg=mp_maxPhi(k,wm,w,ells)
        if mx<=0:
            B=2*k-2-2*k*(wm+sum(w)); return B*104/k,dl,mx
    return None
if __name__=='__main__':
    for k in map(int,sys.argv[1:]):
        c,x1,xh=chart(k); r=certify(k)
        print(k,'chart',mp.nstr(c,12),'x1',float(x1),'xh',float(xh),'dualbound',None if r is None else (mp.nstr(r[0],12),'delta',mp.nstr(r[1],2),'maxPhi',mp.nstr(r[2],3)),'diff',None if r is None else mp.nstr(r[0]-c,3),'HP0',mp.nstr(HP0(k),8),flush=True)
