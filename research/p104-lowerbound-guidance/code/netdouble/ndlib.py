# NETDOUBLE ndlib (own code). Legal NetW generator over odd labels in F2^h + exact F2 / GF(2^16) rank tools.
import random
# ---------- GF(2^16) ----------
PR=0x1100B
EXP=[0]*(2*65536); LOG=[0]*65536
x=1
for i in range(65535):
    EXP[i]=x; LOG[x]=i; x<<=1
    if x&0x10000: x^=PR
for i in range(65535,2*65536): EXP[i]=EXP[i-65535]
def gmul(a,b): return 0 if a==0 or b==0 else EXP[LOG[a]+LOG[b]]
def ginv(a): return EXP[65535-LOG[a]]
def grank(A):
    A=[r[:] for r in A]; R=len(A); C=len(A[0]) if R else 0; r=0
    for c in range(C):
        p=next((i for i in range(r,R) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]; iv=ginv(A[r][c]); A[r]=[gmul(iv,v) for v in A[r]]
        for i in range(R):
            if i!=r and A[i][c]:
                f=A[i][c]; A[i]=[A[i][j]^gmul(f,A[r][j]) for j in range(C)]
        r+=1
    return r
# ---------- F2 ----------
def rk2rows(rows):
    piv={}; r=0
    for x in rows:
        while x:
            hb=x.bit_length()-1
            if hb in piv: x^=piv[hb]
            else: piv[hb]=x; r+=1; break
    return r
def rk2(M):  # list of lists of ints (taken mod 2)
    return rk2rows([sum((v&1)<<j for j,v in enumerate(r)) for r in M])
def dot(x,y): return bin(x&y).count('1')&1
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return s
def dimof(S): return len(S).bit_length()-1
def mm(X,Y,mod=None):
    Yt=list(zip(*Y))
    R=[[sum(a*b for a,b in zip(r,c)) for c in Yt] for r in X]
    return [[v%mod for v in r] for r in R] if mod else R
def had(A,B): return [[a*b for a,b in zip(r,s)] for r,s in zip(A,B)]
class Net:
    """nodes: list of (a,b) frozensets (subspaces of F2^h), b<=a; F m x n, G n x m, H m x m (strictly lower), integer entries mod 4."""
    def __init__(s,h,nodes,F,G,H):
        s.h=h; s.labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; s.n=n=len(s.labs); s.m=m=len(nodes)
        s.nodes=nodes; s.F=F; s.G=G; s.H=H
        s.Q=[[dot(a,b) for b in s.labs] for a in s.labs]
        N=[[int(i==j) for j in range(m)] for i in range(m)]; P=[r[:] for r in N]
        for _ in range(m):
            P=mm(P,H); N=[[N[i][j]+P[i][j] for j in range(m)] for i in range(m)]
        s.N=N; s.N4=[[v%4 for v in r] for r in N]; s.Nb=[[v%2 for v in r] for r in N]
        s.M=mm(mm(G,N),F)
        s.D=sum(dimof(a)-dimof(b) for a,b in nodes)
        s.inA=[[int(q in a) for q in s.labs] for a,b in nodes]                    # m x n : q_p in a_k
        s.inBp=[[int(all(dot(q,y)==0 for y in b)) for q in s.labs] for a,b in nodes]  # m x n : q_t in b_k^perp
        s.Fb=[[v%2 for v in r] for r in F]; s.Gb=[[v%2 for v in r] for r in G]
        s.r4=mm(s.N4,F,4); s.rb=[[v%2 for v in r] for r in s.r4]         # content rows mod 4 / mod 2
        s.u4=mm(G,s.N4,4); s.ub=[[v%2 for v in r] for r in s.u4]         # reverse content columns (n x m)
        s.MQb=[[ (s.M[i][j]*s.Q[i][j])%2 for j in range(n)] for i in range(n)]
    def legal(s):
        for k,(a,b) in enumerate(s.nodes):
            if not b<=a: return False
            for p in range(s.n):
                if s.F[k][p]%4 and not s.inA[k][p]: return False
                if s.G[p][k]%4 and not s.inBp[k][p]: return False
            for j in range(s.m):
                if s.H[k][j]%4 and not (j<k and s.nodes[j][1]<=a): return False
        return True
def rand_sub(h,dim,inside=None):
    base=list(range(1<<h)) if inside is None else sorted(inside)
    while True:
        g=[random.choice(base) for _ in range(dim)]
        S=span(g)
        if len(S)==1<<dim: return frozenset(S)
def rand_net(h,mlo=2,mhi=5,ctrl=False,dens=.6):
    labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
    m=random.randint(mlo,mhi); nodes=[]
    for k in range(m):
        da=random.randint(1,h); db=random.randint(0,da-1)
        a=rand_sub(h,da); b=rand_sub(h,db,a) if db>0 else frozenset({0})
        nodes.append((a,b))
    F=[[0]*n for _ in range(m)]; G=[[0]*m for _ in range(n)]; H=[[0]*m for _ in range(m)]
    for k,(a,b) in enumerate(nodes):
        for p,q in enumerate(labs):
            if q in a and random.random()<dens: F[k][p]=random.randint(1,3)
            if all(dot(q,y)==0 for y in b) and random.random()<dens: G[p][k]=random.randint(1,3)
        for j in range(k):
            if (nodes[j][1]<=a or ctrl) and random.random()<dens: H[k][j]=random.randint(1,3)
    return Net(h,nodes,F,G,H)
