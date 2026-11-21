"""KASYM ka2: REDUCED witness LP (relaxation of cc1: keeps only  sum x=n, mains=2k, SEP, RC2_l (l=3..k)), env DM=1 adds DYADIC_J.
type (D,P,mf), D in 2..k, parts <= k-2, val=(8D+1)^s - sum (8L)^s.  column generation + per-D partition DP pricing. usage ka2.py k.."""
import os,sys,time
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
from math import ceil,log2
s=.99
def RJ(k,J):return sum(2*(len(range(j,k,2**l))//2) for l in range(J+1) for j in range(2**l))
class R:
    def __init__(S,k,dm=False,sep=True):
        S.k=k;S.n=2*k-2;S.Lmax=k-2;S.ls=list(range(3,k+1));S.sep=sep
        S.Js=list(range(1,ceil(log2(k))+1)) if dm else []
        S.b=np.array(([k*(k-1)] if sep else [])+[2*k]*len(S.ls)+[RJ(k,J) for J in S.Js],float)
    def val(S,D,P):return (8*D+1)**s-sum((8*L)**s for L in P)
    def a(S,D,P):
        k=S.k;P=np.array(P);out=[(D*D-(P*P).sum())/2] if S.sep else []
        for l in S.ls:out.append((P[P<l]*(k-P[P<l])).sum()/(k-1) if D>=l else (D*D-(P*P).sum())/(k-1))
        for J in S.Js:out.append(min(D,2**(J+1))-1)
        return np.array(out,float)
    def mains(S,D,P,mf):return mf*sum(1 for L in P if L==1)
    def price(S,w,y,wm):
        k=S.k;ws=w[0] if S.sep else 0.;wl=w[1:1+len(S.ls)] if S.sep else w[:len(S.ls)];wd=w[len(w)-len(S.Js):] if S.Js else []
        L=np.arange(1,S.Lmax+1,dtype=float)
        # cum: Wle[D] = sum_{l<=D} w_l ; Wgt[D]=sum_{l>D} w_l
        wfull=np.zeros(k+2);wfull[3:k+1]=wl
        out=[]
        for D in range(2,k+1):
            Lm=min(D,S.Lmax);Ls=L[:Lm]
            # deep part: for l<=D: piece L contributes L(k-L)/(k-1) if L<l : sum_{L<l<=D} w_l
            Wdeep=np.array([wfull[int(x)+1:D+1].sum() for x in Ls]);Wsh=wfull[D+1:k+1].sum()
            g=-(8*Ls)**s-ws*Ls*Ls/2+Wdeep*Ls*(k-Ls)/(k-1)-Wsh*Ls*Ls/(k-1)
            const=(8*D+1)**s+ws*D*D/2+Wsh*D*D/(k-1)+y+sum(wd[i]*(min(D,2**(J+1))-1) for i,J in enumerate(S.Js))
            for mf in (0,1):
                gg=g.copy();gg[0]+=mf*wm
                best=np.full(D+1,-np.inf);best[0]=0;arg=np.zeros(D+1,int)
                for d in range(1,D+1):
                    m=min(d,Lm);c=best[d-np.arange(1,m+1)]+gg[:m];i=int(c.argmax());best[d]=c[i];arg[d]=i+1
                P=[];d=D
                while d>0:P.append(int(arg[d]));d-=arg[d]
                if mf==1 and 1 not in P:continue
                out.append((best[D]+const,D,tuple(sorted(P)),mf))
        out.sort(reverse=True);return out
    def solve(S,maxit=3000,tol=1e-9):
        k=S.k;cols=[(2,(2,),0),(2,(1,1),1),(k,tuple([1]*k),1),(k,(k//2,k-k//2),0)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
        for it in range(maxit):
            c=-np.array([S.val(D,P) for D,P,mf in cols]);A=np.array([S.a(D,P) for D,P,mf in cols]).T
            Am=np.array([[S.mains(*t) for t in cols]],float)
            r=linprog(c,A_ub=-A,b_ub=-S.b,A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[S.n,2*k],bounds=(0,None),method='highs')
            if r.status!=0:return None
            w=-r.ineqlin.marginals;y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
            pr=S.price(w,y,wm)
            new=[(D,P,mf) for sc,D,P,mf in pr[:15] if sc>tol and (D,P,mf) not in cols]
            if not new:break
            cols+=new
        M=pr[0][0];B=S.n*(M-y)-w@S.b-wm*2*k
        S.w,S.y,S.wm,S.cols,S.x=w,y,wm,cols,r.x
        return 104*B/k,104*(-r.fun)/k,[(round(float(xx),3),D,P,mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        t0=time.time();S=R(k,dm=os.environ.get('DM')=='1',sep=os.environ.get('SEP','1')=='1');cb,cp,sup=S.solve()
        print('k',k,'cB %.4f cP %.4f  %.0fs'%(cb,cp,time.time()-t0),flush=True)
        if os.environ.get('V'):
            print('  wm %.5f y %.5f sep*k %.4f'%(S.wm,S.y,S.w[0]*k if S.sep else 0));o=1 if S.sep else 0
            print('  (l-1)w_l:',' '.join('%d:%.4f'%(l,(l-1)*S.w[o+i]) for i,l in enumerate(S.ls) if l in (3,4,5,6,8,12,16,24,32,48,64,96,128,k-1,k)))
            print('  sup',sup,flush=True)
