"""INTCALLER ic3: large-k IP via LP column generation + reduced-cost fixing (sound filter) + ic1 MILP on the surviving types.
LP = relaxation of the ic1 model without TURAN (any relaxation is valid for reduced-cost fixing); columns (D,P,mode), mode in
{m=0, m=#ones} (m enters linearly, so endpoints suffice). Exact pricing: per D a DP over partitions (parts <= k-2) of the piece weights.
Filter: keep (D,P) whose min-endpoint reduced cost <= z_LP - target_raw (target = BAR*k/104 unless env TGT). Then an IP optimum
>= target uses only kept types; if the restricted IP optimum < target, the full IP optimum < target.  usage: ic3.py k..."""
import os,sys,time
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np,highspy
from decimal import Decimal
import ic1
S=ic1.S
def coefs(k):
    """per row r: const[r][D], piece[r][D][L] (L=1..Lmax), nones[r][D], main[r]; floats. Checked additive on random partitions."""
    R=ic1.rowdefs(k);Lm=k-2;nr=len(R)
    C=np.zeros((nr,k+1));Pc=np.zeros((nr,k+1,Lm+1));N=np.zeros((nr,k+1));Mn=np.array([float(mc) for _,_,mc,_,_ in R])
    for r,(nm,f,mc,se,rhs) in enumerate(R):
        for D in range(2,k+1):
            c0=f(D,());p1=f(D,(1,1))-f(D,(1,));cst=f(D,(1,))-p1
            C[r,D]=cst;N[r,D]=c0-cst;Pc[r,D,1]=p1
            for L in range(2,min(D,Lm)+1):Pc[r,D,L]=f(D,(L,))-c0
    rhs=np.array([float(b) for *_,b in R]);sense=[se for _,_,_,se,_ in R]
    # additivity check
    rng=np.random.default_rng(1)
    for _ in range(200):
        D=int(rng.integers(2,k+1));P=[];d=D
        while d>0:
            L=int(rng.integers(1,min(d,Lm)+1));P.append(L);d-=L
        for r,(nm,f,mc,se,b) in enumerate(R):
            a=C[r,D]+sum(Pc[r,D,L] for L in P)+N[r,D]*(1 not in P)
            assert abs(a-float(f(D,tuple(P))))<1e-9,(nm,D,P)
    return R,C,Pc,N,Mn,rhs,sense
def colvec(C,Pc,N,Mn,D,P,m):
    return C[:,D]+sum(Pc[:,D,L] for L in P)+N[:,D]*(1 not in P)+Mn*m
def lp(k,R,C,Pc,N,Mn,rhs,sense,maxit=3000):
    Lm=k-2;n=2*k-2;e8=np.array([0.0]+[(8*L)**S for L in range(1,Lm+1)])
    cols=[]
    def add(D,P,m):
        t=(D,tuple(sorted(P,reverse=True)),m)
        if t not in cols:cols.append(t)
    for D in range(2,k+1):
        add(D,[1]*D,D);add(D,[1]*D,0)
        if D<=Lm:add(D,[D],0)
    add(k,[k//2,k-k//2],0)
    nr=len(R);BIG=1e4
    for it in range(maxit):
        A=np.array([colvec(C,Pc,N,Mn,D,P,m) for D,P,m in cols]).T
        cost=-np.array([ (8*D+1)**S-sum((8*L)**S for L in P) for D,P,m in cols])
        # artificials: one per row (both directions for ==)
        ncol=len(cols)+nr
        h=highspy.Highs();h.setOptionValue('output_flag',False);h.setOptionValue('threads',1)
        L_=highspy.HighsLp();L_.num_col_=ncol;L_.num_row_=nr
        L_.col_cost_=np.r_[cost,np.full(nr,BIG)];L_.col_lower_=np.zeros(ncol);L_.col_upper_=np.full(ncol,np.inf)
        L_.row_lower_=rhs.copy();L_.row_upper_=np.array([b if s=='==' else np.inf for b,s in zip(rhs,sense)])
        Afull=np.hstack([A,np.diag([1.0 if b>=0 or s=='>=' else -1.0 for b,s in zip(rhs,sense)])])
        st=[0];idx=[];vv=[]
        for c in range(ncol):
            nz=np.nonzero(Afull[:,c])[0];idx+=list(nz);vv+=list(Afull[nz,c]);st.append(len(idx))
        L_.a_matrix_.format_=highspy.MatrixFormat.kColwise;L_.a_matrix_.start_=np.array(st,dtype=np.int32);L_.a_matrix_.index_=np.array(idx,dtype=np.int32);L_.a_matrix_.value_=np.array(vv)
        h.passModel(L_);h.run();sol=h.getSolution();pi=-np.array(sol.row_dual)   # pi>=0 on >= rows for max problem
        z=-h.getInfo().objective_function_value
        new=[];best=0
        for D in range(2,k+1):
            for mode in (0,1):
                rcmin,P=dpmin(k,D,pi,C,Pc,N,Mn,e8,mode)
                if rcmin<-1e-9:new.append((rcmin,D,P,(sum(1 for L in P if L==1) if mode==1 else 0)))
        if not new:break
        new.sort()
        for rc,D,P,m in new[:20]:add(D,P,m)
    art=np.array(sol.col_value[len(cols):]).sum()
    return z,pi,cols,np.array(sol.col_value[:len(cols)]),art
def weights(k,D,pi,C,Pc,N,Mn,e8,mode):
    Lm=min(k-2,D);w=np.array([np.inf]+[pi@Pc[:,D,L]+e8[L] for L in range(1,Lm+1)])
    if mode==1:w[1]+=pi@Mn
    base=pi@C[:,D]-(8*D+1)**S
    return w,base,pi@N[:,D]
def dptab(w,D):
    """best[d][p] = min sum w over partitions of d with parts <= p (p>=1)."""
    Lm=len(w)-1;best=np.full((D+1,Lm+1),np.inf);best[0,:]=0
    for p in range(1,Lm+1):
        for d in range(1,D+1):
            b=best[d,p-1] if p>1 else np.inf
            if d>=p:b=min(b,best[d-p,p]+w[p])
            best[d,p]=b
    return best
def dpmin(k,D,pi,C,Pc,N,Mn,e8,mode):
    w,base,nn=weights(k,D,pi,C,Pc,N,Mn,e8,mode);Lm=len(w)-1
    best=dptab(w,D);wn=w.copy();wn[1]=np.inf;bestn=dptab(wn,D)
    cand=[]
    if D-1>=0 and np.isfinite(best[D-1,Lm]):cand.append((base+w[1]+best[D-1,Lm],'one'))
    if mode==0 and Lm>=2:cand.append((base+nn+bestn[D,Lm],'none'))
    v,kind=min(cand)
    # reconstruct
    P=[];d=D;tab=best;p=Lm
    if kind=='one':P=[1];d=D-1
    else:tab=bestn
    ww=w if kind=='one' else wn
    while d>0:
        while p>1 and tab[d,p]==tab[d,p-1]:p-=1
        P.append(p);d-=p
    return v,P
def enum(k,pi,C,Pc,N,Mn,gap):
    """all (D,P) with min over modes of reduced cost <= gap."""
    Lm=k-2;e8=np.array([0.0]+[(8*L)**S for L in range(1,Lm+1)]);out={}
    for D in range(2,k+1):
        for mode in (0,1):
            w,base,nn=weights(k,D,pi,C,Pc,N,Mn,e8,mode);LL=len(w)-1
            best=dptab(w,D);wn=w.copy();wn[1]=np.inf;bestn=dptab(wn,D)
            # DFS parts non-increasing; track has-one; bound with best tables
            def dfs(d,p,acc,P):
                if d==0:
                    rc=base+acc+(nn if (1 not in P) else 0.0)
                    if (1 in P or mode==0) and rc<=gap+1e-9:
                        t=(D,tuple(P));out[t]=min(out.get(t,np.inf),rc)
                    return
                lb=base+acc+min(best[d,min(p,LL)],bestn[d,min(p,LL)]+min(nn,0.0) if mode==0 else np.inf)
                if lb>gap+1e-9:return
                for q in range(min(p,d,LL),0,-1):dfs(d-q,q,acc+w[q],P+[q])
            sys.setrecursionlimit(10000);dfs(D,LL,0.0,[])
    return out
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:
        t0=time.time();R,C,Pc,N,Mn,rhs,sense=coefs(k)
        z,pi,cols,x,art=lp(k,R,C,Pc,N,Mn,rhs,sense)
        tinv=max(ic1.BAR,104*z/k-float(os.environ.get('DELTA','0.5')));tgt=tinv*k/104;gap=z-tgt
        print('k %d LP %.4f (art %.1e, %d cols, %.0fs)  target %.4f gap_raw %.4f'%(k,104*z/k,art,len(cols),time.time()-t0,tinv,gap),flush=True)
        if gap<0:print('   LP already below target');continue
        keep=enum(k,pi,C,Pc,N,Mn,gap);T=sorted(keep)
        print('   kept types %d (%.0fs)'%(len(T),time.time()-t0),flush=True)
        Af=np.array([C[:,D]+sum(Pc[:,D,L] for L in P)+N[:,D]*(1 not in P) for D,P in T]).T
        for tur in (False,True):
            r,st,dt=ic1.solve(k,T,tur,Af=Af)
            if r is None:print('   IP(TUR=%d) %s -> full IP < target'%(tur,st),flush=True);continue
            xs,ys,obj,bnd=r;bad,ms=ic1.verify(k,T,xs,ys,tur)
            ex=sum(ic1.dval(*T[i])*v for i,v in xs.items())*104/k
            ab=ex>=Decimal(repr(tinv))
            print('   IP(TUR=%d) %.4f exact %s MIPbound %.4f %s exactrows %s  (%s)'%(tur,104*obj/k,str(ex)[:12],104*bnd/k,
                  'ABOVE target -> = full IP optimum' if ab else 'below target -> full IP < target','OK' if not bad else bad,ic1.fmt(T,xs,ys)),flush=True)
