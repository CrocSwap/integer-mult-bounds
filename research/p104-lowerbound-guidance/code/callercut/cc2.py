"""CALLERCUT cc2: high-precision dual certificate for cc1 (base sk2 rows + RC_l + RC2_l).
Duals from the HiGHS master -> Fractions (>= rows clipped to >= 0; equality multipliers y, wm free).  For ANY such duals
  B = n(M - y) - sum_rows w_i b_i - 2k wm,   M = max over ALL allowed types (D, P, mf) of  val + sum_i w_i a_i(D,P) + wm*mains + y
is an upper bound on the LP optimum (weak duality).  Every row is piece-additive for fixed D, so M is an exhaustive DP over
partitions of D (parts <= k-2), rational parts exact (Fractions), only (8L)^.99 terms in mpmath dps 50.  Row coefficients are
re-derived here from the definitions (not read from the float code).  usage: cc2.py k..   prints float and certified c^ = 104 B/k."""
import os,sys,signal
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from math import comb,ceil,log2
import numpy as np, mpmath as mp
from scipy.optimize import linprog
import cc1
mp.mp.dps=50
def solve_store(s_,maxit=1500,tol=1e-9):
    k=s_.k;cols=[]
    seeds=[(D,tuple([1]*D),0) for D in range(2,k+1)]+[(k,tuple([1]*k),1),(k,(k//2,k-k//2),0),(2,(1,1),1),(2,(1,1),0),(2,(2,),0),(3,(1,2),1),(3,(1,1,1),1)]+[(D,(D,),0) for D in range(2,k-1)]+[(D,tuple([1]*D),1) for D in range(2,k+1)]
    for t in seeds:
        if s_.ok(t) and t not in cols:cols.append(t)
    bx=np.array([X[4] for X in s_.X]);nx=len(bx);be=np.array([b for kd,a,b in s_.rowsE])
    for it in range(maxit):
        c=-np.array([s_.val(D,P) for D,P,mf in cols]);A=np.array([s_.rows(D,P) for D,P,mf in cols]).T
        Ax=np.array([s_.xrow(D,P) for D,P,mf in cols]).T;Ae=np.array([s_.erow(D,P) for D,P,mf in cols]).T
        Am=np.array([[s_.mains(*t) for t in cols]],float)
        r=linprog(c,A_ub=-np.vstack([A,Ax,Ae]),b_ub=-np.r_[s_.rhs,bx,be],A_eq=np.vstack([np.ones((1,len(cols))),Am]),b_eq=[s_.n,2*k],bounds=(0,None),method='highs')
        mg=-r.ineqlin.marginals;nr=len(s_.rhs);w=mg[:nr];wx=mg[nr:nr+nx];we=mg[nr+nx:];y=r.eqlin.marginals[0];wm=r.eqlin.marginals[1]
        pr=s_.price6(w,y,wm,wx,we)
        new=[(D,P,mf) for sc,D,P,mf in pr[:15] if sc>tol and (D,P,mf) not in cols and s_.ok((D,P,mf))]
        if not new:break
        cols+=new
    s_.cols=cols;s_.x=r.x;s_.du=(w,wx,we,y,wm);s_.prim=-r.fun
    return [(round(float(xx),3),D,tuple(int(a) for a in P),mf) for xx,(D,P,mf) in zip(r.x,cols) if xx>1e-7]
def rowdefs(L):
    """list of (b, c0(D), f(D,L), z(D)) exact, in the order cwlp rows, ms9 X rows, cc1 rowsE; a(D,P)=c0+sum f + z*[no ones]"""
    k=L.k;out=[];n=L.n;Lmax=L.Lmax
    out.append((Fr(k*(k-1)),lambda D:Fr(D*D,2),lambda D,l:Fr(-l*l,2),lambda D:Fr(0)))          # sep
    out.append((Fr(2*k-2),lambda D:Fr(-1),lambda D,l:Fr(1),lambda D:Fr(0)))                     # e
    out.append((Fr(2*k),lambda D:Fr(0),lambda D,l:Fr(int(l==1)),lambda D:Fr(0)))               # ones
    for ll in L.ells:out.append((Fr(k*(k-1)),lambda D,ll=ll:Fr((ll<=D<=k-1)*D*(k-D)),lambda D,l,ll=ll:Fr(l*(D-l)*(l<ll),2),lambda D:Fr(0)))
    fam=[f for f in os.environ.get('FAM','coord,pfix,shal').split(',') if f]
    assert fam==['coord','pfix','shal'],fam
    # ms9 X order: coord (th=2..k), shal, pfix (x=1..k-1)
    for th in range(2,k+1):out.append((Fr(0),lambda D:Fr(0),lambda D,l,th=th:Fr(2*l*(2<=l<=th)+(1 if (l==1 and D>th) else 0)),lambda D:Fr(-1)))
    out.append((Fr(k),lambda D:Fr(0),lambda D,l:Fr(2*(l==2)+(1 if (l==1 and D>=3) else 0)),lambda D:Fr(0)))
    for x in range(1,k):
        ck=comb(k,x);out.append((Fr(-(n-2*x)),lambda D,x=x,ck=ck:Fr(-comb(k-D,x),ck),lambda D,l,x=x,ck=ck:(Fr(-comb(l,x),ck) if l>=2 else Fr(0)),lambda D:Fr(0)))
    for kind,a,b in L.rowsE:
        if kind=='dm':out.append((Fr(sk2RJ(k,a)),lambda D,a=a:Fr(min(D,2**(a+1))-1),lambda D,l:Fr(0),lambda D:Fr(0)))
        elif kind=='R':out.append((Fr(2*k),lambda D,a=a:(Fr(0) if D>=a else Fr(D*(D-1),k-1)),lambda D,l,a=a:(Fr(l*(l<a)) if D>=a else Fr(0)),lambda D:Fr(0)))
        elif kind=='R2':out.append((Fr(2*k),lambda D,a=a:(Fr(0) if D>=a else Fr(D*D,k-1)),lambda D,l,a=a:(Fr(l*(k-l)*(l<a),k-1) if D>=a else Fr(-l*l,k-1)),lambda D:Fr(0)))
        else:raise ValueError(kind)
    return out
def sk2RJ(k,J):return sum(2*(len(range(j,k,2**l))//2) for l in range(J+1) for j in range(2**l))
def mpf(q):return mp.mpf(q.numerator)/q.denominator
def certify(k,rls):
    L=cc1.LP(k,rls);sup=solve_store(L);w,wx,we,y,wm=L.du
    R=lambda v:Fr(float(v)).limit_denominator(10**12)
    du=[max(Fr(0),R(v)) for v in list(w)+list(wx)+list(we)];y=R(y);wm=R(wm)
    rd=rowdefs(L);assert len(rd)==len(du),(len(rd),len(du))
    # cross-check exact row definitions against float code on the support columns
    for D,P,mf in L.cols[:60]:
        fl=list(L.rows(D,P))+list(L.xrow(D,P))+list(L.erow(D,P))
        ex=[c0(D)+sum(f(D,l) for l in P)+z(D)*(1 not in P) for b,c0,f,z in rd]
        assert max(abs(float(e)-a) for e,a in zip(ex,fl))<1e-6,(D,P)
    s=mp.mpf(99)/100;M=None;arg=None
    for D in range(L.Dmin,k+1):
        Lm=min(D,L.Lmax)
        C0=sum((wi*c0(D) for wi,(b,c0,f,z) in zip(du,rd)),Fr(0))+y
        Z=sum((wi*z(D) for wi,(b,c0,f,z) in zip(du,rd)),Fr(0))
        fr=[None]+[sum((wi*f(D,l) for wi,(b,c0,f,z) in zip(du,rd)),Fr(0)) for l in range(1,Lm+1)]
        gl=[None]+[mpf(fr[l])-(8*l)**s for l in range(1,Lm+1)]
        for mf in (0,1):
            for hasone in (0,1):
                if mf==1 and not hasone:continue
                g=list(gl)
                if mf:g[1]=g[1]+mpf(wm)
                # DP over partitions; hasone=1 forces >=1 part of size 1, hasone=0 forbids
                best=[mp.mpf(0)]+[None]*D
                for d in range(1,D+1):
                    c=[best[d-l]+g[l] for l in range(1 if hasone else 2,min(d,Lm)+1) if best[d-l] is not None]
                    best[d]=max(c) if c else None
                if hasone:
                    if D-1<0 or best[D-1] is None:continue
                    tot=g[1]+best[D-1]
                else:
                    if best[D] is None:continue
                    tot=best[D]+mpf(Z)
                sc=tot+(8*D+1)**s+mpf(C0)
                if M is None or sc>M:M=sc;arg=(D,mf,hasone)
    bsum=sum((wi*b for wi,(b,c0,f,z) in zip(du,rd)),Fr(0))
    B=L.n*(M-mpf(y))-mpf(bsum)-mpf(wm*2*k)
    print('CERT k',k,'rows',len(rd),'primal c^ %.4f'%(104*L.prim/k),'certified c^ <=',mp.nstr(104*B/k,10),'argmax',arg,flush=True)
    if os.environ.get('SUP'):print('  support',sup,flush=True)
    return 104*B/k
if __name__=='__main__':
    signal.alarm(int(os.environ.get('AL','3000')))
    for k in [int(a) for a in sys.argv[1:]]:
        rls=list(range(3,k+1)) if os.environ.get('RC','1')=='1' else []
        certify(k,rls)
