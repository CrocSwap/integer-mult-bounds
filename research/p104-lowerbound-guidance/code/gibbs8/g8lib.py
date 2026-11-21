"""GIBBS8 lib: mod-8 quarter decoders (W,V n x m residues mod 8, (W V^T) o Q = 4 I mod 8), exact Z/8 Gibbs resampling,
cost, rational lift (w = W col, u = V col / 4: sum w u = I mod 2 on Q-cells, 2-integral), MERGEROWS normal-form pipeline."""
import sys, pickle, numpy as np
from fractions import Fraction as Fr
sys.path.insert(0,'../mergerows'); sys.path.insert(0,'../iso3'); sys.path.insert(0,'../den4')
from qlib import std_set, Q_std, normalise, rk2, v2
import m2, nf
from m2 import prices, clean, gauge_max
from nf import normal_form, drop_kernel
import m5

def inv8(x): return pow(int(x),-1,8)
def rank_bits(vecs):
    piv={}; r=0
    for x in vecs:
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; r+=1; break
    return r
class Dec:
    def __init__(s,Q,W,V):
        s.Q=Q; s.n=len(Q); s.W=W%8; s.V=V%8; s.m=W.shape[1]
        s.qrow=[sum(1<<j for j in range(s.n) if Q[i,j]) for i in range(s.n)]
        s.nb=[np.nonzero(Q[i])[0] for i in range(s.n)]
        s.pr=[s.price(k) for k in range(s.m)]
    def price(s,k,wcol=None,vcol=None):
        wc=s.W[:,k] if wcol is None else wcol; vc=s.V[:,k] if vcol is None else vcol
        S=0
        for j in np.nonzero(vc)[0]: S|=1<<int(j)
        D=np.nonzero(wc)[0]
        if len(D)==0 or S==0: return 0
        return rank_bits([s.qrow[int(t)]&S for t in D])
    def C(s): return sum(s.pr)
    def valid(s):
        M=(s.W@s.V.T)%8; I4=4*np.eye(s.n,dtype=np.int64)
        return not (((M-I4)%8)*s.Q).any()
def solve_mod8(A,c,rng):
    """uniform random x in (Z/8)^m with A x = c mod 8, or None."""
    A=(A%8).astype(np.int64).copy(); c=(c%8).astype(np.int64).copy(); r,m=A.shape
    Uc=np.eye(m,dtype=np.int64); rank=0; ds=[]
    for st in range(min(r,m)):
        sub=A[st:,st:]
        if not sub.any(): break
        # min valuation entry
        best=None
        for d in (0,1,2):
            idx=np.argwhere((sub%(2<<d)!=0)&(sub%(1<<d)==0)) if d<3 else None
            if len(idx): best=(d,idx[0]); break
        d,(i,j)=best; i+=st; j+=st
        A[[st,i]]=A[[i,st]]; c[[st,i]]=c[[i,st]]
        A[:,[st,j]]=A[:,[j,st]]; Uc[:,[st,j]]=Uc[:,[j,st]]
        u=inv8(A[st,st]>>d); A[st]=(A[st]*u)%8; c[st]=(c[st]*u)%8
        for i2 in range(st+1,r):
            if A[i2,st]:
                f=A[i2,st]>>d; A[i2]=(A[i2]-f*A[st])%8; c[i2]=(c[i2]-f*c[st])%8
        for j2 in range(st+1,m):
            if A[st,j2]:
                f=A[st,j2]>>d; A[:,j2]=(A[:,j2]-f*A[:,st])%8; Uc[:,j2]=(Uc[:,j2]-f*Uc[:,st])%8
        ds.append(d); rank+=1
    for i in range(rank):
        if c[i]%(1<<ds[i]): return None
    if c[rank:].any(): return None
    y=np.zeros(m,dtype=np.int64)
    for i in range(rank):
        d=ds[i]; y[i]=((c[i]>>d)+(1<<(3-d))*int(rng.integers(0,1<<d)))%8
    y[rank:]=rng.integers(0,8,m-rank)
    return (Uc@y)%8
def step(D,rng,beta=1.0,K=8,jsize=None):
    """one column-restricted Gibbs move on a row t of W or V. returns accepted flag, dC."""
    t=int(rng.integers(D.n)); side=int(rng.integers(2)); m=D.m
    js=jsize if jsize else int(rng.integers(2,m+1))
    J=np.sort(rng.choice(m,js,replace=False)); Jc=np.setdiff1d(np.arange(m),J)
    P=D.nb[t]; cur=(D.W if side==0 else D.V); oth=(D.V if side==0 else D.W)
    A=oth[P][:,J]; c=np.where(P==t,4,0)-oth[P][:,Jc]@cur[t,Jc]
    cands=[];
    for _ in range(K):
        x=solve_mod8(A,c,rng)
        if x is None: return 0,0
        cands.append(x)
    cands.append(cur[t,J].copy())
    base=sum(D.pr[k] for k in J); dels=[];newp=[]
    for x in cands:
        tot=0; pl=[]
        for a,k in enumerate(J):
            if x[a]==cur[t,k]: p=D.pr[k]
            else:
                if side==0: wc=D.W[:,k].copy(); wc[t]=x[a]; p=D.price(k,wcol=wc)
                else: vc=D.V[:,k].copy(); vc[t]=x[a]; p=D.price(k,vcol=vc)
            pl.append(p); tot+=p
        dels.append(tot-base); newp.append(pl)
    d=np.array(dels,float); pw=np.exp(-beta*(d-d.min())); pw/=pw.sum()
    ch=int(rng.choice(len(cands),p=pw)); x=cands[ch]
    cur[t,J]=x
    for a,k in enumerate(J): D.pr[k]=newp[ch][a]
    return 1,dels[ch]
def to_rows(D):
    rows=[]
    for k in range(D.m):
        w=[Fr(int(x)) for x in D.W[:,k]]; u=[Fr(int(x),4) for x in D.V[:,k]]
        if any(w) and any(u): rows.append((w,u))
    return rows
def check2(rows,Q):
    n=len(Q); bad=0
    for i in range(n):
        for j in range(n):
            if Q[i,j]:
                val=sum(w[i]*u[j] for w,u in rows)
                if v2(val-(1 if i==j else 0))<1 and val!=(1 if i==j else 0): bad+=1
    return bad
def pipeline(rows,Q,thr,g0=False,iters=800,seeds=2):
    """MERGEROWS m5 pipeline on the lifted rational object. returns dict."""
    C0=sum(prices(rows,Q)); out=dict(C0=C0)
    if g0: out['S1raw']=gauge_max(rows,Q,300,0)['gmax_sum']
    nfr,ds=m5.nf_all(rows,Q); assert check2(nfr,Q)==0
    C1=sum(prices(nfr,Q)); assert C1<=C0
    g1=max(gauge_max(nfr,Q,iters,sd)['gmax_sum'] for sd in range(seeds))
    out.update(C1=C1,S1=g1,classes=[(len(c),d) for c,d in ds])
    return out
def load_start(f,Q):
    rows=pickle.load(open(f,'rb')); e,W,V,pr,_,_=normalise(rows,Q)
    if e==2: return W%8,V%8
    if e==1: return W%8,(2*V)%8
    return None
def random_gl8(m,rng,steps):
    X=np.eye(m,dtype=np.int64); Y=np.eye(m,dtype=np.int64)   # X Y^T = I
    for _ in range(steps):
        i,j=rng.choice(m,2,replace=False); c=int(rng.integers(1,8))
        E=np.eye(m,dtype=np.int64); E[i,j]=c; Ei=np.eye(m,dtype=np.int64); Ei[i,j]=(-c)%8
        X=(X@E)%8; Y=(Y@Ei.T)%8   # (E)(Ei^T)^T = E Ei = I
    return X,Y
def hs_frame_start(Q):
    from qlib import gram_rows_std
    L=std_set('HS64'); U=[[0]*8 for _ in range(8)]
    for t,i in enumerate(range(0,8,2)):
        for s,sg in enumerate((1,-1)): U[2*t+s][i]=2; U[2*t+s][i+1]=2*sg
    rows=gram_rows_std(L,U); e,W,V,pr,_,_=normalise(rows,Q); assert e==2
    return W%8,V%8
