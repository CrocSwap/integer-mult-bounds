"""BILINEAR bl5: COVER-law LP (see BL.md [P] CLOSURE -> COVER).  Thresholds LS (env, default 3..Lmax).  A 'profile' gives, per threshold l,
  tau_l^- (used in rows  S_l := sum_r sum_{pieces L<l} L [D_r>=l]  >= tau_l^-)  and  tau_l^+ (|T_l| <= tau_l^+).
Effective size of a type: e = #singletons + sum_{multi pieces L} min(L, U(L)),  U(L) = min_{l in LS, l<=L} tau_l^+   (U = inf if no l<=L).
Rows: base ms9 (coord,pfix,shal) + DYADIC_J on masks + DYADIC_J on effective sizes + S_l rows.  Pricing exact: DP over (d, e, hasone).
Bound = dual certificate.  usage: bl5.py k [profile]   profile 'all' = tau^-=tau^+=k for every l (the everything-effective branch)."""
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
os.environ.setdefault('FAM','coord,pfix,shal')
sys.path.insert(0,'code/scherk')
import sk2
sys.path.insert(0,sk2.BASE+'UNIMODEL/routes/mainscan');import ms9
import numpy as np
from math import ceil,log2
from scipy.optimize import linprog
NEG=-1e300
class LP(ms9.LP):
    def __init__(s_,k,ls,tm,tp,dyeff=True,dymask=True):
        super().__init__(k);s_.ls=list(ls);s_.tm=list(tm);s_.tp=list(tp)
        s_.Js=list(range(1,ceil(log2(k))+1))
        s_.U=[None]+[min([tp[i] for i,l in enumerate(ls) if l<=L],default=10**9) for L in range(1,s_.Lmax+1)]
        s_.rowsE=[]   # (kind, J or l, b)
        if dymask:s_.rowsE+=[('dm',J,float(sk2.RJ(k,J))) for J in s_.Js]
        if dyeff:s_.rowsE+=[('de',J,float(sk2.RJ(k,J))) for J in s_.Js]
        s_.rowsE+=[('S',l,float(t)) for l,t in zip(ls,tm) if t>0]
        if os.environ.get('PC','1')=='1':s_.rowsE+=[('pc',0,float(k*(k-1)))]   # CROSS c=1 on effective masks: sum C(e,2) >= k(k-1)
    def einc(s_,L):return 1 if L==1 else min(L,s_.U[L])
    def erow(s_,D,P):
        e=sum(s_.einc(L) for L in P);out=[]
        for kind,a,b in s_.rowsE:
            if kind=='dm':out.append(min(D,2**(a+1))-1)
            elif kind=='de':out.append(max(0,min(e,2**(a+1))-1))
            elif kind=='pc':out.append(e*(e-1)/2)
            else:out.append(sum(L for L in P if L<a)*(D>=a))
        return np.array(out,float)
    def price6(s_,w,y,wm,wx,we):
        k,s=s_.k,s_.s;L=np.arange(1,s_.Lmax+1,dtype=float);Li=L.astype(int)
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
            for i,(kind,a,b) in enumerate(s_.rowsE):
                if kind=='S' and D>=a:g=g+we[i]*Ls*(Ls<a)
            # per-D, per-e constant from dyadic rows
            ev=np.arange(D+1);eD=np.zeros(D+1)
            for i,(kind,a,b) in enumerate(s_.rowsE):
                if kind=='dm':eD+=we[i]*(min(D,2**(a+1))-1)
                elif kind=='de':eD+=we[i]*np.maximum(0,np.minimum(ev,2**(a+1))-1)
                elif kind=='pc':eD+=we[i]*ev*(ev-1)/2
            inc=[s_.einc(v) for v in range(1,Lm+1)]
            for mf in (0,1):
                if mf==1 and D<s_.dmin:continue
                gg=g.copy();gg[0]+=w1+mf*wm+c1
                # DP[h][d][e]
                dp=np.full((2,D+1,D+1),NEG);dp[0,0,0]=0;ar=np.zeros((2,D+1,D+1,3),int)
                for d in range(1,D+1):
                    for v in range(1,min(d,Lm)+1):
                        ei=inc[v-1]
                        for h in (0,1):
                            src=dp[h,d-v,:D+1-ei]
                            nh=1 if (h or v==1) else 0
                            cand=src+gg[v-1];tgt=dp[nh,d,ei:]
                            m=cand>tgt
                            if m.any():
                                tgt[m]=cand[m];idx=np.nonzero(m)[0]+ei
                                ar[nh,d,idx,0]=v;ar[nh,d,idx,1]=h;ar[nh,d,idx,2]=idx-ei
                for h in ((1,) if mf else (0,1)):
                    tot=dp[h,D]+eD+(cz if h==0 else 0.0)
                    e=int(np.argmax(tot))
                    if tot[e]<=NEG/2:continue
                    P=[];d=D;hh=h;ee=e
                    while d>0:
                        v,ph,pe=ar[hh,d,ee];P.append(int(v));d-=v;hh=ph;ee=pe
                    out.append((tot[e]+const,D,tuple(sorted(P)),mf))
        out.sort(reverse=True);return out
    def solve(s_,maxit=1500,tol=1e-9):
        k=s_.k;cols=[]
        seeds=[(D,tuple([1]*D),0) for D in range(2,k+1)]+[(k,tuple([1]*k),1),(k,(k//2,k-k//2),0),(2,(1,1),1),(2,(1,1),0),(2,(2,),0),(3,(1,2),1),(3,(1,1,1),1)]+[(D,(D,),0) for D in range(2,k-1)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
        for t in seeds:
            if s_.ok(t) and t not in cols:cols.append(t)
        bx=np.array([X[4] for X in s_.X]);nx=len(bx);be=np.array([b for kd,a,b in s_.rowsE]);ne=len(be)
        for it in range(maxit):
            c=-np.array([s_.val(D,P) for D,P,mf in cols]);A=np.array([s_.rows(D,P) for D,P,mf in cols]).T
            Ax=np.array([s_.xrow(D,P) for D,P,mf in cols]).T
            Ae=np.array([s_.erow(D,P) for D,P,mf in cols]).T
            Am=np.array([[s_.mains(*t) for t in cols]],float)
            r=linprog(c,A_ub=-np.vstack([A,Ax,Ae]),b_ub=-np.r_[s_.rhs,bx,be],A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[s_.n,2*k],bounds=(0,None),method='highs')
            if r.status!=0:return None
            mg=-r.ineqlin.marginals;nr=len(s_.rhs);w=mg[:nr];wx=mg[nr:nr+nx];we=mg[nr+nx:];y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
            pr=s_.price6(w,y,wm,wx,we)
            new=[(D,P,mf) for sc,D,P,mf in pr[:15] if sc>tol and (D,P,mf) not in cols and s_.ok((D,P,mf))]
            if not new:break
            cols+=new
        s_.cols,s_.x=cols,r.x
        M=pr[0][0];B=s_.n*(M-y)-w@s_.rhs-wm*2*k-wx@bx-we@be
        return B,-r.fun,[(round(float(xx),3),D,tuple(int(a) for a in P),mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
def run(k,ls,tm,tp,tag=''):
    r=LP(k,ls,tm,tp).solve()
    if r is None:print(tag,'k',k,'INFEASIBLE',flush=True);return None
    B,p,sup=r;print(tag,'k',k,'cB %.3f cP %.3f'%(104*B/k,104*p/k),sup if os.environ.get('SUP') else '',flush=True);return 104*B/k
if __name__=='__main__':
    signal.alarm(3000)
    k=int(sys.argv[1]);prof=sys.argv[2] if len(sys.argv)>2 else 'all'
    Lmax=k-2;ls=[int(a) for a in os.environ['LS'].split(',')] if os.environ.get('LS') else list(range(3,Lmax+1))
    if prof=='all':run(k,ls,[k]*len(ls),[k]*len(ls),'COVER-all')
