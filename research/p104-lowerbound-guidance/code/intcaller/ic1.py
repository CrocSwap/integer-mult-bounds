"""INTCALLER ic1: exact INTEGER program over role-type multiplicities (CC model: Q=0, n=2k-2, D>=2, parts<=k-2, rho=2, lambda!=-1).
Variables: x_{D,P} in Z>=0 (number of roles of type (D, piece multiset P)), y_{D,P} in Z, 0<=y<=#ones(P)*x  (total MAINS on those roles;
mixed main/idle singletons allowed -- a superset of the mf in {0,1} LP model, so sound for C1-like roles).
Rows = every type row of the certified cc2/mp8 LP (cwlp sep,e,ones,wit_l; ms9 coord,shal,pfix; bl5 DYADIC_J masks; cc1 RC_l, RC2_l;
mp8 TRIPLE averaged; mp5 HALL_l) + n, MAINS equalities + new integral row TURAN (env TUR=1):
  for every 2 roles a,b:  sum_{r != a,b} C(D_r,2) >= floor((k-1)^2/4)       [P, from TRIPLE per-triple + Mantel; see IC.md]
Objective = role-piece invoice  c^ = (104/k) sum x (8D+1)^s - sum (8L)^s,  s=.99.
usage: ic1.py k...   env TUR=0/1 (default 1), RELAX=1 (LP relaxation of the same model), TOP=m (m best distinct designs via no-goods),
       RC=gap  (reduced-cost prefilter: only types with LP reduced cost <= gap (raw units) are kept; sound when target opt >= LP-gap)."""
import os,sys,time,itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
from fractions import Fraction as Fr
from math import comb,ceil,log2
from decimal import Decimal,getcontext
import numpy as np
import highspy
S=0.99
BAR=128.891
def RJ(k,J):return sum(2*(len(range(j,k,2**l))//2) for l in range(J+1) for j in range(2**l))
def partitions(D,maxp):
    if D==0:yield ();return
    for p in range(min(D,maxp),0,-1):
        for r in partitions(D-p,p):yield (p,)+r
def types(k):
    Lmax=k-2 if k>=3 else k
    for D in range(2,k+1):
        for P in partitions(D,Lmax):yield D,P
# ---- rows: each returns (coef for type (D,P) with all singletons IDLE, coef per MAIN, sense, rhs); exact Fractions
def rowdefs(k):
    n=2*k-2;Lmax=k-2;R=[]
    one=lambda P:sum(1 for L in P if L==1)
    R.append(('sep',lambda D,P:Fr(D*D-sum(L*L for L in P),2),0,'>=',Fr(k*(k-1))))
    R.append(('e',lambda D,P:Fr(len(P)-1),0,'>=',Fr(2*k-2)))
    R.append(('ones',lambda D,P:Fr(one(P)),0,'>=',Fr(2*k)))
    for l in range(2,Lmax+1):
        R.append(('wit%d'%l,lambda D,P,l=l:Fr(sum(L*(D-L) for L in P if L<l),2)+((l<=D<=k-1)*D*(k-D)),0,'>=',Fr(k*(k-1))))
    for th in range(2,k+1):
        R.append(('coord%d'%th,lambda D,P,th=th:Fr(sum(2*L for L in P if 2<=L<=th)+(D>th)*one(P)-(one(P)==0)),0,'>=',Fr(0)))
    R.append(('shal',lambda D,P:Fr(2*sum(1 for L in P if L==2)+(D>=3)*one(P)),0,'>=',Fr(k)))
    for x in range(1,k):
        ck=comb(k,x);R.append(('pfix%d'%x,lambda D,P,x=x,ck=ck:-Fr(comb(k-D,x),ck)-sum(Fr(comb(L,x),ck) for L in P if L>=2),0,'>=',Fr(-(n-2*x))))
    for J in range(1,ceil(log2(k))+1):
        R.append(('dm%d'%J,lambda D,P,J=J:Fr(min(D,2**(J+1))-1),0,'>=',Fr(RJ(k,J))))
    for l in range(3,k+1):
        R.append(('RC%d'%l,lambda D,P,l=l:Fr(sum(L for L in P if L<l)) if D>=l else Fr(D*(D-1),k-1),0,'>=',Fr(2*k)))
    for l in range(3,k+1):
        R.append(('RC2_%d'%l,lambda D,P,l=l:Fr(sum(L*(k-L) for L in P if L<l),k-1) if D>=l else Fr(D*D-sum(L*L for L in P),k-1),0,'>=',Fr(2*k)))
    R.append(('TRIPLE',lambda D,P:Fr(comb(D,3)+comb(D,2)*(k-D)),0,'>=',Fr(3*comb(k,3))))
    for l in range(2,k+1):   # HALL_l: idle singletons count L(k-L) = k-1 each; a MAIN removes that
        R.append(('HALL%d'%l,lambda D,P,l=l:Fr(sum(L*(k-L) for L in P if L<l)-((D<l)*D*(k-D))),-(k-1)*(1<l),'>=',Fr(0)))
    R.append(('n',lambda D,P:Fr(1),0,'==',Fr(n)))
    R.append(('MAINS',lambda D,P:Fr(0),1,'==',Fr(2*k)))
    return R
def val(D,P):return (8*D+1)**S-sum((8*L)**S for L in P)
def dval(D,P):
    getcontext().prec=60
    pw=lambda x:(Decimal(S).quantize(Decimal('0.01'))*Decimal(x).ln()).exp()
    return pw(8*D+1)-sum(pw(8*L) for L in P)
def turT(k):return (k-1)**2//4
def build(k,T,tur=True,relax=False,nogoods=(),Af=None):
    """T = list of (D,P). Returns highspy model + index maps."""
    R=rowdefs(k);n=2*k-2
    nt=len(T);ones=[sum(1 for L in P if L==1) for D,P in T]
    yidx=[i for i in range(nt) if ones[i]>0]
    Ds=sorted(set(D for D,P in T))
    ncol=nt+len(yidx)+(2*len(Ds)+1 if tur else 0)
    cost=np.zeros(ncol);lo=np.zeros(ncol);hi=np.full(ncol,float(n));integ=[1]*ncol
    for i,(D,P) in enumerate(T):cost[i]=-val(D,P)
    yc={i:nt+j for j,i in enumerate(yidx)}
    for i in yidx:hi[yc[i]]=float(2*k)
    ac={};bc={}
    if tur:
        for j,D in enumerate(Ds):ac[D]=nt+len(yidx)+2*j;bc[D]=ac[D]+1;hi[ac[D]]=1;hi[bc[D]]=1
        SCc=ncol-1;hi[SCc]=np.inf;integ[SCc]=1
    rows=[]  # (dict col->coef, lo, hi)
    for ri,(name,f,mc,sense,rhs) in enumerate(R):
        if Af is not None:
            nz=np.nonzero(np.abs(Af[ri])>1e-12)[0];d=dict(zip(nz.tolist(),Af[ri,nz].tolist()))
        else:
          d={}
          for i,(D,P) in enumerate(T):
            c=f(D,P)
            if c!=0:d[i]=float(c)
        if mc!=0:
            for i in yidx:d[yc[i]]=float(mc)
        r=float(rhs);rows.append((d,r,r if sense=='==' else np.inf))
    for i in yidx:rows.append(({yc[i]:1.0,i:-float(ones[i])},-np.inf,0.0))   # y <= ones*x
    if tur:
        Tt=turT(k);BM=float(comb(k,2)*2+Tt+1)
        d={i:float(comb(D,2)) for i,(D,P) in enumerate(T)};d[SCc]=-1.0;rows.append((d,0.0,0.0))   # SC = sum C(D,2) x
        base={SCc:1.0}
        for D in Ds:   # a_D >= [N_D>=1], b_D >= [N_D>=2]:  N_D <= n a_D ; N_D - 1 <= n b_D
            d={i:1.0 for i,(DD,P) in enumerate(T) if DD==D};d[ac[D]]=-float(n);rows.append((d,-np.inf,0.0))
            d={i:1.0 for i,(DD,P) in enumerate(T) if DD==D};d[bc[D]]=-float(n);rows.append((d,-np.inf,1.0))
        for D1 in Ds:
            for D2 in Ds:
                if D2>D1:continue
                d=dict(base)
                if D1==D2:   # sum C - 2C(D1,2) >= Tt - BM(1-b)
                    d[bc[D1]]=-BM;rhs=Tt+2*comb(D1,2)-BM
                else:
                    d[ac[D1]]=-BM;d[ac[D2]]=-BM;rhs=Tt+comb(D1,2)+comb(D2,2)-2*BM
                rows.append((d,float(rhs),np.inf))
    for ng in nogoods:   # support-class no-good: the next design uses at least one type outside supp(ng)
        rows.append(({i:1.0 for i in ng},-np.inf,float(n-1)))
    h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1)
    h.setOptionValue('mip_rel_gap',1e-10);h.setOptionValue('mip_abs_gap',1e-9);h.setOptionValue('time_limit',float(os.environ.get('TL','1100')))
    lp=highspy.HighsLp();lp.num_col_=ncol;lp.num_row_=len(rows)
    lp.col_cost_=cost;lp.col_lower_=lo;lp.col_upper_=hi
    lp.row_lower_=np.array([r[1] for r in rows]);lp.row_upper_=np.array([r[2] for r in rows])
    cols=[[] for _ in range(ncol)]
    for ri,(d,_,_) in enumerate(rows):
        for c,v in d.items():cols[c].append((ri,v))
    st=[0];idx=[];vv=[]
    for c in range(ncol):
        for ri,v in cols[c]:idx.append(ri);vv.append(v)
        st.append(len(idx))
    lp.a_matrix_.format_=highspy.MatrixFormat.kColwise;lp.a_matrix_.start_=np.array(st,dtype=np.int32);lp.a_matrix_.index_=np.array(idx,dtype=np.int32);lp.a_matrix_.value_=np.array(vv)
    if not relax:lp.integrality_=[highspy.HighsVarType.kInteger]*ncol
    h.passModel(lp)
    return h,R,yc,ac,bc,rows
def verify(k,T,xs,ys,tur=True):
    """exact check: xs dict i->int, ys dict i->int mains. Returns (ok, min slack per row name)."""
    R=rowdefs(k);bad=[];minsl={}
    for name,f,mc,sense,rhs in R:
        lhs=sum(f(*T[i])*v for i,v in xs.items())+mc*sum(ys.values())
        sl=lhs-rhs;minsl[name]=sl
        if (sense=='=='and sl!=0) or (sense=='>=' and sl<0):bad.append((name,sl))
    for i,v in ys.items():
        if not (0<=v<=xs[i]*sum(1 for L in T[i][1] if L==1)):bad.append(('y',i))
    if tur:
        degs=sorted([T[i][0] for i,v in xs.items() for _ in range(v)],reverse=True)
        tsl=sum(comb(D,2) for D in degs[2:])-turT(k);minsl['TURAN']=tsl
        if tsl<0:bad.append(('TURAN',tsl))
    return bad,minsl
def HP(k):
    getcontext().prec=60;pw=lambda x:(Decimal('0.99')*Decimal(x).ln()).exp()
    v2p=pw(17)-pw(16);return Decimal(208)*((k-2)*v2p+pw(8*k+1)-k*pw(8))/k
def solve(k,T,tur=True,relax=False,nogoods=(),Af=None):
    h,R,yc,ac,bc,rows=build(k,T,tur,relax,nogoods,Af);t0=time.time();h.run();st=h.getModelStatus()
    if st!=highspy.HighsModelStatus.kOptimal:return None,str(st),time.time()-t0
    sol=list(h.getSolution().col_value);info=h.getInfo()
    bnd=-info.mip_dual_bound if not relax else -info.objective_function_value
    xs={i:int(round(sol[i])) for i in range(len(T)) if sol[i]>0.5} if not relax else {i:sol[i] for i in range(len(T)) if sol[i]>1e-9}
    ys={i:int(round(sol[yc[i]])) for i in xs if i in yc} if not relax else {}
    return (xs,ys,-info.objective_function_value,bnd),'opt',time.time()-t0
def fmt(T,xs,ys):
    return ' + '.join('%s%d:%s%s'%(('%g'%v+'x ') if v!=1 else '',T[i][0],'|'.join(map(str,T[i][1])),(' m%d'%ys[i]) if ys.get(i) else '') for i,v in sorted(xs.items(),key=lambda t:(-T[t[0]][0],T[t[0]][1])))
if __name__=='__main__':
    tur=os.environ.get('TUR','1')=='1';top=int(os.environ.get('TOP','1'))
    for k in [int(a) for a in sys.argv[1:]]:
        T=list(types(k));t0=time.time()
        r,st,dt=solve(k,T,tur,relax=True)
        lpv=104*r[2]/k if r else None
        r,st,dt=solve(k,T,tur)
        if r is None:print('k',k,'IP',st,flush=True);continue
        xs,ys,obj,bnd=r;bad,ms=verify(k,T,xs,ys,tur)
        ex=sum(dval(*T[i])*v for i,v in xs.items())*104/k
        print('k %d types %d  LP(relax,same rows) %.4f  IP %.4f (exact %s)  MIPbound %.4f  HP %.4f  bar %.3f  %s  exactrows %s  t=%.0fs'%(
            k,len(T),lpv,104*obj/k,str(ex)[:12],104*bnd/k,HP(k),BAR,'ABOVE' if ex>Decimal(str(BAR)) else 'below','OK' if not bad else bad,time.time()-t0),flush=True)
        print('   argmax:',fmt(T,xs,ys),'| tight:',[nm for nm,s in ms.items() if s==0][:12],flush=True)
        ngs=[tuple(xs)]
        for j in range(top-1):
            r,st,dt=solve(k,T,tur,nogoods=ngs)
            if r is None:break
            xs,ys,obj,bnd=r;bad,ms=verify(k,T,xs,ys,tur);ngs.append(tuple(xs))
            print('   #%d %.4f %s %s'%(j+2,104*obj/k,'OK' if not bad else bad,fmt(T,xs,ys)),flush=True)
