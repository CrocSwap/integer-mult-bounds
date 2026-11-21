"""INTCALLER ic4: AGGREGATED integer program (relaxation of ic1, exact upper bound; exact when it disaggregates).
Integer variables per degree D=2..k:  N_D (roles of degree D), Z_{D,L} (L-pieces on degree-D roles, L<=min(D,k-2)), U_D (degree-D roles with
no singleton), M_D (mains on degree-D roles).  Linking (necessary conditions of any real type multiset):
  sum_L L Z_{D,L} = D N_D ;  N_D <= sum_L Z_{D,L} ;  U_D <= N_D ;  N_D - U_D <= Z_{D,1} <= D (N_D - U_D) ;  M_D <= Z_{D,1}.
Every ic1 row is piece-additive per D (checked in ic3.coefs), so  row = sum_D C_r(D) N_D + sum Pc_r(D,L) Z_{D,L} + Nn_r(D) U_D + Mn_r sum M_D.
TURAN via N_D (top two degrees, big-M).  Objective = sum (8D+1)^s N_D - (8L)^s Z_{D,L}.
Then: try to disaggregate (exact partition of each D's pieces into N_D roles, U_D of them singleton-free) -> exact design, verified with Fractions.
usage: ic4.py k...  env TUR=0/1."""
import os,sys,time,itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np,highspy
from math import comb
from decimal import Decimal
import ic1,ic3
S=ic1.S
def build(k,tur=True,cuts=()):
    R,C,Pc,Nn,Mn,rhs,sense=ic3.coefs(k);Lm=k-2;n=2*k-2;nr=len(R)
    var={};lo=[];hi=[];cost=[]
    def nv(key,c=0.0,h=np.inf):
        var[key]=len(cost);cost.append(c);lo.append(0.0);hi.append(h)
    for D in range(2,k+1):
        nv(('N',D),-((8*D+1)**S),n);nv(('U',D),0,n);nv(('M',D),0,2*k)
        for L in range(1,min(D,Lm)+1):nv(('Z',D,L),(8*L)**S,n*D)
    Ds=list(range(2,k+1))
    if tur:
        for D in Ds:nv(('a',D),0,1);nv(('b',D),0,1)
        nv(('SC',),0,np.inf)
    rows=[]
    for r in range(nr):
        d={}
        for D in Ds:
            if C[r,D]:d[var[('N',D)]]=C[r,D]
            if Nn[r,D]:d[var[('U',D)]]=Nn[r,D]
            if Mn[r]:d[var[('M',D)]]=Mn[r]
            for L in range(1,min(D,Lm)+1):
                if Pc[r,D,L]:d[var[('Z',D,L)]]=Pc[r,D,L]
        rows.append((d,rhs[r],rhs[r] if sense[r]=='==' else np.inf))
    for D in Ds:
        Ls=range(1,min(D,Lm)+1)
        d={var[('Z',D,L)]:float(L) for L in Ls};d[var[('N',D)]]=-float(D);rows.append((d,0.0,0.0))
        d={var[('Z',D,L)]:1.0 for L in Ls};d[var[('N',D)]]=-1.0;rows.append((d,0.0,np.inf))
        rows.append(({var[('U',D)]:1.0,var[('N',D)]:-1.0},-np.inf,0.0))
        rows.append(({var[('Z',D,1)]:1.0,var[('N',D)]:-1.0,var[('U',D)]:1.0},0.0,np.inf))
        rows.append(({var[('Z',D,1)]:1.0,var[('N',D)]:-float(D),var[('U',D)]:float(D)},-np.inf,0.0))
        rows.append(({var[('M',D)]:1.0,var[('Z',D,1)]:-1.0},-np.inf,0.0))
        if D%2==1:   # PARITY [P]: a role of odd degree has an odd piece
            d={var[('Z',D,L)]:1.0 for L in Ls if L%2==1};d[var[('N',D)]]=-1.0;rows.append((d,0.0,np.inf))
    if tur:
        Tt=ic1.turT(k);BM=float(2*comb(k,2)+Tt+1);sc=var[('SC',)]
        d={var[('N',D)]:float(comb(D,2)) for D in Ds};d[sc]=-1.0;rows.append((d,0.0,0.0))
        for D in Ds:
            rows.append(({var[('N',D)]:1.0,var[('a',D)]:-float(n)},-np.inf,0.0))
            rows.append(({var[('N',D)]:1.0,var[('b',D)]:-float(n)},-np.inf,1.0))
        for D1 in Ds:
            for D2 in Ds:
                if D2>D1:continue
                if D1==D2:rows.append(({sc:1.0,var[('b',D1)]:-BM},Tt+2*comb(D1,2)-BM,np.inf))
                else:rows.append(({sc:1.0,var[('a',D1)]:-BM,var[('a',D2)]:-BM},Tt+comb(D1,2)+comb(D2,2)-2*BM,np.inf))
    for cut in cuts:   # exclude an aggregated N-vector exactly is hard; cut = list of (var,val) -> sum |x-v| >= 1 via N only (not used by default)
        pass
    h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1)
    h.setOptionValue('mip_rel_gap',1e-10);h.setOptionValue('mip_abs_gap',1e-9);h.setOptionValue('time_limit',float(os.environ.get('TL','1100')))
    ncol=len(cost);lp=highspy.HighsLp();lp.num_col_=ncol;lp.num_row_=len(rows)
    lp.col_cost_=np.array(cost);lp.col_lower_=np.array(lo);lp.col_upper_=np.array(hi)
    lp.row_lower_=np.array([r[1] for r in rows]);lp.row_upper_=np.array([r[2] for r in rows])
    cols=[[] for _ in range(ncol)]
    for ri,(d,_,_) in enumerate(rows):
        for c,v in d.items():cols[c].append((ri,v))
    st=[0];idx=[];vv=[]
    for c in range(ncol):
        for ri,v in cols[c]:idx.append(ri);vv.append(v)
        st.append(len(idx))
    lp.a_matrix_.format_=highspy.MatrixFormat.kColwise;lp.a_matrix_.start_=np.array(st,dtype=np.int32);lp.a_matrix_.index_=np.array(idx,dtype=np.int32);lp.a_matrix_.value_=np.array(vv)
    lp.integrality_=[highspy.HighsVarType.kInteger]*ncol
    h.passModel(lp);return h,var
def disagg(D,N,U,Z):
    """split piece multiset Z (dict L->count) into N parts each summing to D, exactly U of them with no 1. Returns list of partitions or None."""
    pieces=sorted([L for L,c in Z.items() for _ in range(c)],reverse=True)
    bins=[[] for _ in range(N)];load=[0]*N
    ones=Z.get(1,0);big=[p for p in pieces if p>1]
    # bins 0..N-U-1 must get >=1 one; bins N-U.. none.  greedy + DFS on big pieces, ones fill the rest.
    hasone=0   # U ignored here: any exact split is re-verified row by row (verify) afterwards
    sys.setrecursionlimit(100000)
    def ok_fill():
        need=[D-load[i] for i in range(N)]
        return min(need)>=0 and sum(need)==ones
    seen=set()
    def dfs(j):
        if j==len(big):return ok_fill()
        key=(j,tuple(sorted(load[:hasone])),tuple(sorted(load[hasone:])))
        if key in seen:return False
        seen.add(key)
        p=big[j];tried=set()
        for i in range(N):
            cap=D-1 if i<hasone else D
            grp=('h' if i<hasone else 'n',load[i])
            if load[i]+p<=cap and grp not in tried:
                tried.add(grp);load[i]+=p;bins[i].append(p)
                if dfs(j+1):return True
                load[i]-=p;bins[i].pop()
        return False
    if not dfs(0):return None
    return [tuple(sorted(bins[i]+[1]*(D-load[i]),reverse=True)) for i in range(N)]
if __name__=='__main__':
    tur=os.environ.get('TUR','1')=='1'
    for k in [int(a) for a in sys.argv[1:]]:
        t0=time.time();h,var=build(k,tur);h.run();st=h.getModelStatus()
        if st!=highspy.HighsModelStatus.kOptimal:print('k',k,'status',st,flush=True);continue
        x=h.getSolution().col_value;info=h.getInfo();g=lambda key:int(round(x[var[key]]))
        obj=-info.objective_function_value;bnd=-info.mip_dual_bound
        design=[];ok=True;T=[];xs={};ys={}
        for D in range(2,k+1):
            N=g(('N',D))
            if N==0:continue
            Z={L:g(('Z',D,L)) for L in range(1,min(D,k-2)+1) if g(('Z',D,L))>0};U=g(('U',D));M=g(('M',D))
            parts=disagg(D,N,U,Z)
            if parts is None:ok=False;design.append(('NODIS',D,N,U,Z,M));continue
            mleft=M
            for P in parts:
                t=(D,P)
                if t not in T:T.append(t)
                i=T.index(t);xs[i]=xs.get(i,0)+1
                o=sum(1 for L in P if L==1);m=min(o,mleft);mleft-=m
                if o:ys[i]=ys.get(i,0)+m
        line='k %d aggIP %.4f MIPbound %.4f (%.0fs)  HP %.4f  bar %.3f %s'%(k,104*obj/k,104*bnd/k,time.time()-t0,ic1.HP(k),ic1.BAR,'ABOVE' if 104*bnd/k>=ic1.BAR else 'BOUND<BAR')
        if ok:
            bad,ms=ic1.verify(k,T,xs,ys,tur);ex=sum(ic1.dval(*T[i])*v for i,v in xs.items())*104/k
            line+='  disaggregated exact %s rows %s'%(str(ex)[:12],'OK' if not bad else bad)
            print(line,flush=True);print('   design:',ic1.fmt(T,xs,ys),flush=True)
        else:print(line,' NOT disaggregated:',design,flush=True)
