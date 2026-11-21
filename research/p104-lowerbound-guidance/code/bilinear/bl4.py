"""BILINEAR bl4: EFFECTIVE-SUPPORT LP (see BL.md [P] CLOSURE, INERT_l).  Fix l>=3 and tau>=0.  Two branches:
  LP1 (|T_l| > tau is possible only if S_l >= tau+1):  base rows + DYADIC_J(masks) + row  S_l := sum_{D>=l} s_l >= tau+1
  LP2 (|T_l| <= tau):  base rows + DYADIC_J on EFFECTIVE sizes e = min(D, s_l + tau)   [replaces mask DYADIC; both valid, keep both]
  s_l(type) = sum of piece sizes < l (singletons included).  Bound = max(LP1, LP2) (disjunction), each a dual certificate.
Base = ms9 coord,pfix,shal (imported unmodified).  Pricing exact over (D, s, hasone, mf): small fill (pieces < l) x big fill (pieces >= l).
usage: bl4.py l tau k...   (tau may be 'f<frac>' meaning tau = floor(frac*k))"""
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
os.environ.setdefault('FAM','coord,pfix,shal')
sys.path.insert(0,'code/scherk')
import sk2
sys.path.insert(0,sk2.BASE+'UNIMODEL/routes/mainscan');import ms9
import numpy as np
from math import ceil,log2
from scipy.optimize import linprog
NEG=-np.inf
class LP(ms9.LP):
    def __init__(s_,k,l,E):
        super().__init__(k);s_.l=l;s_.E=E   # E: list of (f(D,s), b)
    def sl(s_,P):return sum(L for L in P if L<s_.l)
    def erow(s_,D,P):s=s_.sl(P);return np.array([f(D,s) for f,b in s_.E],float)
    def price5(s_,w,y,wm,wx,we):
        k,s=s_.k,s_.s;l=s_.l;L=np.arange(1,s_.Lmax+1,dtype=float);Li=L.astype(int)
        wsep,we_,w1=w[0],w[1],w[2];wl=w[3:3+len(s_.ells)]
        W=np.zeros(len(L))
        for i,ll in enumerate(s_.ells):W[:ll-1]+=wl[i]
        cpv=np.array([sum(wx[j]*X[1](v) for j,X in enumerate(s_.X)) for v in Li]);cz=sum(wx[j]*X[3] for j,X in enumerate(s_.X))
        out=[]
        for D in range(s_.Dmin,k+1):
            Lm=min(D,s_.Lmax);Ls=L[:Lm]
            c0=sum(wx[j]*X[0](D) for j,X in enumerate(s_.X));c1=sum(wx[j]*X[2](D) for j,X in enumerate(s_.X))
            const=(8*D+1)**s+wsep*D*D/2-we_+sum(wl[i]*((ll<=D<=k-1)*D*(k-D)) for i,ll in enumerate(s_.ells))+y+c0
            g=-(8*Ls)**s-wsep*Ls*Ls/2+we_+W[:Lm]*Ls*(D-Ls)/2+cpv[:Lm]
            # big fill: pieces in [l, Lm]
            bb=np.full(D+1,NEG);bb[0]=0;ba=np.zeros(D+1,int)
            for d in range(1,D+1):
                for v in range(l,min(d,Lm)+1):
                    t=bb[d-v]+g[v-1]
                    if t>bb[d]:bb[d]=t;ba[d]=v
            for mf in (0,1):
                if mf==1 and D<s_.dmin:continue
                gs=g.copy();gs[0]=g[0]+w1+mf*wm+c1
                # small fill with flag hasone: pieces in [1, min(l-1,Lm)]
                sm=np.full((2,D+1),NEG);sm[0,0]=0;sa=np.zeros((2,D+1,2),int)
                for d in range(1,D+1):
                    for v in range(1,min(l-1,Lm,d)+1):
                        for h in (0,1):
                            if not np.isfinite(sm[h,d-v]):continue
                            nh=1 if (h or v==1) else 0;t=sm[h,d-v]+gs[v-1]
                            if t>sm[nh,d]:sm[nh,d]=t;sa[nh,d]=(v,h)
                for sv in range(0,D+1):
                    rest=bb[D-sv]
                    if not np.isfinite(rest):continue
                    for h in (0,1):
                        if mf==1 and h==0:continue
                        if not np.isfinite(sm[h,sv]):continue
                        tot=sm[h,sv]+rest+(cz if h==0 else 0.0)+sum(we[e]*f(D,sv) for e,(f,b) in enumerate(s_.E))
                        P=[];d=sv;hh=h
                        while d>0:v,ph=sa[hh,d];P.append(int(v));d-=v;hh=ph
                        d=D-sv
                        while d>0:P.append(int(ba[d]));d-=ba[d]
                        out.append((tot+const,D,tuple(sorted(P)),mf))
        out.sort(reverse=True);return out
    def solve(s_,maxit=1000,tol=1e-9):
        k=s_.k;cols=[]
        seeds=[(D,tuple([1]*D),0) for D in range(2,k+1)]+[(k,tuple([1]*k),1),(k,(k//2,k-k//2),0),(2,(1,1),1),(2,(1,1),0),(2,(2,),0),(3,(1,2),1),(3,(1,1,1),1)]+[(D,(D,),0) for D in range(2,k-1)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
        for t in seeds:
            if s_.ok(t) and t not in cols:cols.append(t)
        bx=np.array([X[4] for X in s_.X]);nx=len(bx);be=np.array([b for f,b in s_.E]);ne=len(be)
        for it in range(maxit):
            c=-np.array([s_.val(D,P) for D,P,mf in cols]);A=np.array([s_.rows(D,P) for D,P,mf in cols]).T
            Ax=np.array([s_.xrow(D,P) for D,P,mf in cols]).T
            Ae=np.array([s_.erow(D,P) for D,P,mf in cols]).T
            Am=np.array([[s_.mains(*t) for t in cols]],float)
            r=linprog(c,A_ub=-np.vstack([A,Ax,Ae]),b_ub=-np.r_[s_.rhs,bx,be],A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[s_.n,2*k],bounds=(0,None),method='highs')
            if r.status!=0:return None
            mg=-r.ineqlin.marginals;nr=len(s_.rhs);w=mg[:nr];wx=mg[nr:nr+nx];we=mg[nr+nx:];y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
            pr=s_.price5(w,y,wm,wx,we)
            new=[(D,P,mf) for sc,D,P,mf in pr[:12] if sc>tol and (D,P,mf) not in cols and s_.ok((D,P,mf))]
            if not new:break
            cols+=new
        s_.cols,s_.x,s_.duals=cols,r.x,(w,y,wm,wx,we)
        M=pr[0][0];B=s_.n*(M-y)-w@s_.rhs-wm*2*k-wx@bx-we@be
        return B,-r.fun,[(round(float(xx),3),D,tuple(int(a) for a in P),mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
def dy(k):return [(lambda D,s,c=2**(J+1):float(min(D,c)-1),float(sk2.RJ(k,J))) for J in range(1,ceil(log2(k))+1)]
def dyeff(k,tau):return [(lambda D,s,c=2**(J+1),tau=tau:float(max(0,min(D,s+tau,c)-1)),float(sk2.RJ(k,J))) for J in range(1,ceil(log2(k))+1)]
def branches(k,l,tau):
    lp1=LP(k,l,dy(k)+[(lambda D,s,l=l:float(s*(D>=l)),float(tau+1))])
    lp2=LP(k,l,dy(k)+dyeff(k,tau))
    return lp1,lp2
if __name__=='__main__':
    signal.alarm(3000)
    l=int(sys.argv[1]);ta=sys.argv[2]
    for k in [int(a) for a in sys.argv[3:]]:
        tau=int(float(ta[1:])*k) if ta.startswith('f') else int(ta)
        res=[]
        for nm,L in zip(('LP1','LP2'),branches(k,l,tau)):
            r=L.solve();res.append((nm,None if r is None else r))
        out=[];bmax=-1e9
        for nm,r in res:
            if r is None:out.append(nm+' INFEAS');continue
            B,p,sup=r;bmax=max(bmax,104*B/k);out.append('%s cB %.3f'%(nm,104*B/k)+(' '+str(sup) if os.environ.get('SUP') else ''))
        print('EFF l',l,'tau',tau,'k',k,'BOUND %.3f'%bmax,' | '.join(out),flush=True)
