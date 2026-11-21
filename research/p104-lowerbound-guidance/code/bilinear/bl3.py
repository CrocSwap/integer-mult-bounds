"""BILINEAR bl3: bl1 LP (ms9 coord,pfix,shal + DYADIC_J) + CHAIN_l rows (see BL.md, [P] CLOSURE + CHAIN):
   CHAIN_l :  2 * sum_{roles, D>=l} sum_{pieces L<l} L   -   #{roles whose pieces are ALL of size >= l}   >= 0 ,   l in LS (env, default 3..k-2)
Pricing exact: per (D, mf, j): j singletons + multi fill of D-j; for j=0 the indicator [min piece >= l] is handled by
DP over 'min piece in [l_i, l_{i+1})' bands (2-state flag DP).  Dual certificate as in bl1.  usage: bl3.py k..."""
import os,sys,signal
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bl1
import numpy as np
from scipy.optimize import linprog
class LP(bl1.LP):
    def __init__(s_,k,ls=None,extra=()):
        super().__init__(k,extra)
        s_.ls=sorted(set(l for l in (ls if ls is not None else range(3,k-1)) if 3<=l<=s_.Lmax))
    def crow(s_,D,P):
        return np.array([2.0*sum(L for L in P if L<l)*(D>=l)-1.0*(min(P)>=l) for l in s_.ls],float)
    def price4(s_,w,y,wm,wx,we,wc):
        k,s=s_.k,s_.s;L=np.arange(1,s_.Lmax+1,dtype=float);Li=L.astype(int)
        wsep,we_,w1=w[0],w[1],w[2];wl=w[3:3+len(s_.ells)]
        W=np.zeros(len(L))
        for i,l in enumerate(s_.ells):W[:l-1]+=wl[i]
        cpv=np.array([sum(wx[j]*X[1](l) for j,X in enumerate(s_.X)) for l in Li]);cz=sum(wx[j]*X[3] for j,X in enumerate(s_.X))
        ls=s_.ls;out=[]
        for D in range(s_.Dmin,k+1):
            Lm=min(D,s_.Lmax);Ls=L[:Lm]
            c0=sum(wx[j]*X[0](D) for j,X in enumerate(s_.X));c1=sum(wx[j]*X[2](D) for j,X in enumerate(s_.X))
            const=(8*D+1)**s+wsep*D*D/2-we_+sum(wl[i]*((l<=D<=k-1)*D*(k-D)) for i,l in enumerate(s_.ells))+y+c0
            chainp=np.array([2.0*Lv*sum(wc[i] for i,l in enumerate(ls) if Lv<l<=D) for Lv in Ls])
            g=-(8*Ls)**s-wsep*Ls*Ls/2+we_+W[:Lm]*Ls*(D-Ls)/2+cpv[:Lm]+chainp
            def fill(lo,hi):  # best multi fill of each d with all pieces in [lo,Lm] and at least one piece < hi (hi=None: no flag)
                b0=np.full(D+1,-np.inf);b0[0]=0;a0=np.zeros(D+1,int);b1=np.full(D+1,-np.inf);a1=np.zeros(D+1,int)
                for d in range(1,D+1):
                    for Lv in range(lo,min(d,Lm)+1):
                        v=b0[d-Lv]+g[Lv-1]
                        if v>b0[d]:b0[d]=v;a0[d]=Lv
                        if hi is not None:
                            v1=max(b1[d-Lv]+g[Lv-1], (b0[d-Lv]+g[Lv-1]) if Lv<hi else -np.inf)
                            if v1>b1[d]:b1[d]=v1;a1[d]=Lv
                return b0,a0,b1,a1
            b0,a0,_,_=fill(2,None)
            def path(arr,d):
                P=[]
                while d>0:P.append(int(arr[d]));d-=arr[d]
                return P
            for mf in (0,1):
                if mf==1 and D<s_.dmin:continue
                g1=g[0]+w1+mf*wm+c1
                for j in range(1 if mf else 0,D+1):
                    if j==0:continue
                    rest=b0[D-j]
                    if not np.isfinite(rest):continue
                    tot=j*g1+rest+sum(we[e]*f(D,j) for e,(f,b) in enumerate(s_.E))
                    out.append((tot+const,D,tuple(sorted([1]*j+path(a0,D-j))),mf))
            # j=0 pure-multi types: bands by min piece
            bands=[2]+[l for l in ls if l<=Lm]
            pen=0.0;ej=sum(we[e]*f(D,0) for e,(f,b) in enumerate(s_.E))
            for bi,lo in enumerate(bands):
                if bi>0:pen+=wc[ls.index(lo)]
                hi=bands[bi+1] if bi+1<len(bands) else None
                if hi is None:
                    bb,aa,_,_=fill(lo,None);val=bb[D];
                    if not np.isfinite(val):continue
                    P=path(aa,D)
                else:
                    _,_,bb,aa=fill(lo,hi);val=bb[D]
                    if not np.isfinite(val):continue
                    # reconstruct: greedy recompute via brute DP path (flag path); fallback to a0-style path
                    P=s_._flagpath(g,D,lo,hi,Lm)
                    if P is None:continue
                out.append((val+cz-pen+ej+const,D,tuple(sorted(P)),0))
        out.sort(reverse=True);return out
    def _flagpath(s_,g,D,lo,hi,Lm):
        import functools
        b0=np.full(D+1,-np.inf);b0[0]=0;b1=np.full(D+1,-np.inf);c0={0:None};c1={}
        for d in range(1,D+1):
            for Lv in range(lo,min(d,Lm)+1):
                v=b0[d-Lv]+g[Lv-1]
                if v>b0[d]:b0[d]=v;c0[d]=(0,Lv)
                v1=b1[d-Lv]+g[Lv-1]
                if v1>b1[d]:b1[d]=v1;c1[d]=(1,Lv)
                if Lv<hi:
                    v2=b0[d-Lv]+g[Lv-1]
                    if v2>b1[d]:b1[d]=v2;c1[d]=(0,Lv)
        if not np.isfinite(b1[D]):return None
        P=[];d=D;st=1
        while d>0:
            prev,Lv=(c1 if st else c0)[d];P.append(Lv);d-=Lv;st=prev
        return P
    def solve(s_,maxit=800,tol=1e-9):
        k=s_.k;cols=[]
        seeds=[(D,tuple([1]*D),0) for D in range(2,k+1)]+[(k,tuple([1]*k),1),(k,(k//2,k-k//2),0),(2,(1,1),1),(2,(1,1),0),(2,(2,),0),(3,(1,2),1),(3,(1,1,1),1)]+[(D,(D,),0) for D in range(2,k-1)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
        for t in seeds:
            if s_.ok(t) and t not in cols:cols.append(t)
        bx=np.array([X[4] for X in s_.X]);nx=len(bx);be=np.array([b for f,b in s_.E]);ne=len(be);nc=len(s_.ls)
        for it in range(maxit):
            c=-np.array([s_.val(D,P) for D,P,mf in cols]);A=np.array([s_.rows(D,P) for D,P,mf in cols]).T
            Ax=np.array([s_.xrow(D,P) for D,P,mf in cols]).T if nx else np.zeros((0,len(cols)))
            Ae=np.array([s_.erow(D,P) for D,P,mf in cols]).T if ne else np.zeros((0,len(cols)))
            Ac=np.array([s_.crow(D,P) for D,P,mf in cols]).T if nc else np.zeros((0,len(cols)))
            Am=np.array([[s_.mains(*t) for t in cols]],float)
            r=linprog(c,A_ub=-np.vstack([A,Ax,Ae,Ac]),b_ub=-np.r_[s_.rhs,bx,be,np.zeros(nc)],A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[s_.n,2*k],bounds=(0,None),method='highs')
            if r.status!=0:return None
            mg=-r.ineqlin.marginals;nr=len(s_.rhs);w=mg[:nr];wx=mg[nr:nr+nx];we=mg[nr+nx:nr+nx+ne];wc=mg[nr+nx+ne:];y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
            pr=s_.price4(w,y,wm,wx,we,wc)
            new=[(D,P,mf) for sc,D,P,mf in pr[:12] if sc>tol and (D,P,mf) not in cols and s_.ok((D,P,mf))]
            if not new:break
            cols+=new
        s_.cols,s_.x,s_.duals=cols,r.x,(w,y,wm,wx,we,wc)
        M=pr[0][0];B=s_.n*(M-y)-w@s_.rhs-wm*2*k-wx@bx-we@be
        return B,-r.fun,[(round(float(xx),3),D,tuple(int(a) for a in P),mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
if __name__=='__main__':
    signal.alarm(3000)
    for k in [int(a) for a in sys.argv[1:]]:
        ls=None
        if os.environ.get('LS'):ls=[int(a) for a in os.environ['LS'].split(',')]
        res=LP(k,ls).solve()
        if res is None:print('CHAIN k',k,'INFEASIBLE',flush=True);continue
        B,p,sup=res;print('CHAIN k',k,'cB',round(104*B/k,3),'cP',round(104*p/k,3),sup if os.environ.get('SUP') else '',flush=True)
