import itertools, random
from fractions import Fraction as F
import numpy as np
INF=10**6
def v2(x):
    x=F(x)
    if x==0: return None
    n,d=x.numerator,x.denominator; k=0
    while n%2==0: n//=2;k+=1
    while d%2==0: d//=2;k-=1
    return k
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def e8_roots():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in(1,-1):
            for sj in(1,-1):
                r=[F(0)]*8; r[i]=F(si); r[j]=F(sj); R.append(tuple(r))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(F(x,2) for x in s))
    return R
def lines(R):
    seen=set();L=[]
    for r in R:
        n=tuple(-x for x in r)
        if n in seen: continue
        seen.add(r); L.append(r)
    return L
def dn(n):
    R=[]
    for i,j in itertools.combinations(range(n),2):
        for si in(1,-1):
            for sj in(1,-1):
                r=[F(0)]*n; r[i]=F(si); r[j]=F(sj); R.append(tuple(r))
    return R
def solve(A,Rm):
    # coefficients c (len T) with sum c_j A[j] = r ; A: T vectors, via gaussian on Fractions (least: exact)
    T=len(A); n=len(A[0])
    # build augmented system n eq, T unknowns
    M=[[A[j][i] for j in range(T)]+[None] for i in range(n)]
    return M
def inv_coeffs(A):
    # return function r -> coeffs, using Gram: c = G^{-1} (A r)
    T=len(A)
    G=[[dot(A[i],A[j]) for j in range(T)] for i in range(T)]
    # invert G
    M=[row[:]+[F(int(i==j)) for j in range(T)] for i,row in enumerate(G)]
    for c in range(T):
        p=next(r for r in range(c,T) if M[r][c]!=0); M[c],M[p]=M[p],M[c]
        pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for r in range(T):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[x-f*y for x,y in zip(M[r],M[c])]
    Gi=[row[T:] for row in M]
    return Gi
def decoder(roots,A):
    T=len(A); Gi=inv_coeffs(A)
    P=[];Q=[]
    for r in roots:
        q=[dot(r,a) for a in A]
        p=[sum(Gi[j][k]*q[k] for k in range(T)) for j in range(T)]
        # verify
        assert all(sum(p[j]*A[j][i] for j in range(T))==r[i] for i in range(len(r))),"not in span"
        P.append(p);Q.append(q)
    return P,Q
def gram_ok(roots,P,Q):
    for t in range(len(roots)):
        for s in range(len(roots)):
            if sum(P[t][j]*Q[s][j] for j in range(len(P[0])))!=dot(roots[t],roots[s]): return False
    return True
def rank_f2(rows):
    basis={}; r=0
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h in basis: x^=basis[h]
            else: basis[h]=x; r+=1; break
    return r
def Bmat(roots):
    v=len(roots)
    return [sum(1<<s for s in range(v) if s==t or dot(roots[t],roots[s])==0) for t in range(v)]
def subrank(B,R,A):
    mask=sum(1<<s for s in A)
    return rank_f2([B[t]&mask for t in R])
def analyse(roots,A):
    P,Q=decoder(roots,A); T=len(A); v=len(roots)
    ok=gram_ok(roots,P,Q); B=Bmat(roots)
    ranks=[];dr=[]
    for j in range(T):
        Rj=[t for t in range(v) if P[t][j]!=0]; Aj=[t for t in range(v) if Q[t][j]!=0]
        Dj=sorted(set(Rj)&set(Aj))
        ranks.append(subrank(B,Rj,Aj)); dr.append(subrank(B,Dj,Dj))
    return P,Q,ok,sum(ranks),sorted(ranks),sorted(dr)
def valmats(P,Q):
    v=len(P);T=len(P[0])
    VP=np.full((v,T),INF,dtype=np.float64);VQ=VP.copy()
    for t in range(v):
        for j in range(T):
            x=v2(P[t][j]); y=v2(Q[t][j])
            if x is not None: VP[t,j]=x
            if y is not None: VQ[t,j]=y
    return VP,VQ
def surv(VP,VQ,a,diag=1):
    a=np.asarray(a,float)
    m=(VP+a).min(1); n=(VQ-a).min(1)
    return m+n==diag
def search(VP,VQ,diag,rng,half=True,box=3,restarts=60):
    T=VP.shape[1]; step=0.5 if half else 1.0
    best=(-1,None)
    def sc(a): return int(surv(VP,VQ,a,diag).sum())
    for r in range(restarts):
        a=np.array([rng.randint(-box*2,box*2)*step/ (2 if False else 1) for _ in range(T)],float)
        a=np.clip(a,-box,box); cur=sc(a)
        improved=True
        while improved:
            improved=False
            for j in rng.sample(range(T),T):
                for d in (-3*step,-2*step,-step,step,2*step,3*step):
                    b=a.copy(); b[j]=a[j]+d
                    if abs(b[j])>box: continue
                    s=sc(b)
                    if s>cur: a,cur=b,s;improved=True
            # pair moves
            if not improved:
                for i,j in itertools.combinations(range(T),2):
                    for di in (-step,step):
                        for dj in (-step,step):
                            b=a.copy();b[i]+=di;b[j]+=dj
                            if abs(b[i])>box or abs(b[j])>box: continue
                            s=sc(b)
                            if s>cur: a,cur=b,s;improved=True
        if cur>best[0]: best=(cur,a.copy()-a.min())
    return best
