"""BILINEAR bl1: SCHERK sk2 LP (ms9 FAM coord,pfix,shal + DYADIC_J; imported unmodified) + extra rows of the form
     sum_types f(D, j) x >= b,   j = #singleton pieces of the type   (f may be NONLINEAR in j).
Pricing: for each (D, mf, j): j singletons + best multi-piece fill of D-j (DP over piece sizes 2..Lmax).  Bound = dual certificate
B = n(M-y) - w.rhs - wm*2k - wx.bx - we.be with M from the exhaustive (D,mf,j) pricing.  usage: bl1.py ROW k...
ROW: none | sq<beta>  (sum_{D>=3} C(j,2) >= beta*C(k,2)) | tot<g> (sum j >= g k) | d3<a> (sum_{D>=3} j >= a k)"""
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
os.environ.setdefault('FAM','coord,pfix,shal')
sys.path.insert(0,'code/scherk')
import sk2
sys.path.insert(0,sk2.BASE+'UNIMODEL/routes/mainscan');import ms9
import numpy as np
from math import ceil,log2,comb
from scipy.optimize import linprog
class LP(ms9.LP):
    def __init__(s_,k,extra=()):
        super().__init__(k)
        for J in range(1,ceil(log2(k))+1):s_.X.append((lambda D:float(min(D,2**(J+1))-1) if False else 0.0,lambda L:0.0,lambda D:0.0,0.0,0.0))
        s_.X=[x for x in s_.X if x[4]!=0.0 or True][:len(s_.X)-ceil(log2(k))]   # drop placeholders (DYADIC handled below as f-rows)
        s_.E=[(lambda D,j,c=2**(J+1):float(min(D,c)-1),float(sk2.RJ(k,J))) for J in range(1,ceil(log2(k))+1)]+list(extra)
    def erow(s_,D,P):
        j=sum(1 for L in P if L==1);return np.array([f(D,j) for f,b in s_.E],float)
    def price3(s_,w,y,wm,wx,we):
        k,s=s_.k,s_.s;L=np.arange(1,s_.Lmax+1,dtype=float);Li=L.astype(int)
        wsep,we_,w1=w[0],w[1],w[2];wl=w[3:3+len(s_.ells)]
        W=np.zeros(len(L))
        for i,l in enumerate(s_.ells):W[:l-1]+=wl[i]
        cpv=np.array([sum(wx[j]*X[1](l) for j,X in enumerate(s_.X)) for l in Li]);cz=sum(wx[j]*X[3] for j,X in enumerate(s_.X))
        out=[]
        for D in range(s_.Dmin,k+1):
            Lm=min(D,s_.Lmax);Ls=L[:Lm]
            c0=sum(wx[j]*X[0](D) for j,X in enumerate(s_.X));c1=sum(wx[j]*X[2](D) for j,X in enumerate(s_.X))
            const=(8*D+1)**s+wsep*D*D/2-we_+sum(wl[i]*((l<=D<=k-1)*D*(k-D)) for i,l in enumerate(s_.ells))+y+c0
            g=-(8*Ls)**s-wsep*Ls*Ls/2+we_+W[:Lm]*Ls*(D-Ls)/2+cpv[:Lm]
            best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
            for d in range(2,D+1):
                m=min(d,Lm)
                if m<2:continue
                c=best[d-np.arange(2,m+1)]+g[1:m];i=int(c.argmax());best[d]=c[i];arg[d]=i+2
            for mf in (0,1):
                if mf==1 and D<s_.dmin:continue
                g1=g[0]+w1+mf*wm+c1
                for j in range(0 if mf==0 else 1,D+1):
                    if j>Lm*0+D:break
                    rest=best[D-j]
                    if not np.isfinite(rest):continue
                    if Lm<1 and j>0:continue
                    tot=j*g1+rest+(cz if j==0 else 0.0)+sum(we[e]*f(D,j) for e,(f,b) in enumerate(s_.E))
                    P=[1]*j;d=D-j
                    while d>0:P.append(arg[d]);d-=arg[d]
                    out.append((tot+const,D,tuple(sorted(P)),mf))
        out.sort(reverse=True);return out
    def solve(s_,maxit=800,tol=1e-9):
        k=s_.k;cols=[]
        seeds=[(D,tuple([1]*D),0) for D in range(2,k+1)]+[(k,tuple([1]*k),1),(k,(k//2,k-k//2),0),(2,(1,1),1),(2,(1,1),0),(2,(2,),0),(3,(1,2),1),(3,(1,1,1),1)]+[(D,(D,),0) for D in range(2,k-1)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
        for t in seeds:
            if s_.ok(t) and t not in cols:cols.append(t)
        bx=np.array([X[4] for X in s_.X]);nx=len(bx);be=np.array([b for f,b in s_.E]);ne=len(be)
        for it in range(maxit):
            c=-np.array([s_.val(D,P) for D,P,mf in cols]);A=np.array([s_.rows(D,P) for D,P,mf in cols]).T
            Ax=np.array([s_.xrow(D,P) for D,P,mf in cols]).T if nx else np.zeros((0,len(cols)))
            Ae=np.array([s_.erow(D,P) for D,P,mf in cols]).T if ne else np.zeros((0,len(cols)))
            Am=np.array([[s_.mains(*t) for t in cols]],float)
            r=linprog(c,A_ub=-np.vstack([A,Ax,Ae]),b_ub=-np.r_[s_.rhs,bx,be],A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[s_.n,2*k],bounds=(0,None),method='highs')
            if r.status!=0:return None
            mg=-r.ineqlin.marginals;nr=len(s_.rhs);w=mg[:nr];wx=mg[nr:nr+nx];we=mg[nr+nx:];y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
            pr=s_.price3(w,y,wm,wx,we)
            new=[(D,P,mf) for sc,D,P,mf in pr[:12] if sc>tol and (D,P,mf) not in cols]
            if not new:break
            cols+=new
        M=pr[0][0];B=s_.n*(M-y)-w@s_.rhs-wm*2*k-wx@bx-we@be
        return B,-r.fun,[(round(float(xx),3),D,tuple(int(a) for a in P),mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
def parse(row,k):
    if row=='none':return ()
    if row.startswith('sq'):b=float(row[2:]);return ((lambda D,j:float(comb(j,2))*(D>=3),b*comb(k,2)),)
    if row.startswith('tot'):g=float(row[3:]);return ((lambda D,j:float(j),g*k),)
    if row.startswith('d3'):a=float(row[2:]);return ((lambda D,j:float(j)*(D>=3),a*k),)
    raise SystemExit('bad row')
if __name__=='__main__':
    signal.alarm(3000)
    row=sys.argv[1]
    for k in [int(a) for a in sys.argv[2:]]:
        res=LP(k,parse(row,k)).solve()
        if res is None:print(row,'k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=res;print(row,'k',k,'cB',round(104*B/k,3),'cP',round(104*p/k,3),sup if os.environ.get('SUP') else '',flush=True)
# ---- WALT rows (piece-aware CROSS averaged over uniform w-subsets W labelled alternately X,Y,X,..; see BL.md) ----
def walt_rows(k,ws):
    out=[]
    for w in ws:
        ck=comb(k,w)
        out.append((lambda D,w=w,ck=ck:1.0-(comb(k-D,w)+D*comb(k-D,w-1))/ck, lambda L,w=w,ck=ck:-(comb(L,w)/ck if L>=2 else 0.0), lambda D:0.0, 0.0, float(2*(w//2))))
    return out
