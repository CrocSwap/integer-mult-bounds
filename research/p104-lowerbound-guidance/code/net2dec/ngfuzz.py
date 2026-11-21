# NET2DEC fuzz (own code). Random integral NetWs over odd labels in F2^h; checks
#  NG-fwd : mu4(M o Q) <= sum_k [C(d+1,2) + in_k * d*(h - dim a)]
#  NG-mir : mu4(M o Q) <= sum_k [C(d+1,2) + out_k * d*dim b]
#  NG-sum : mu4 <= (h+1)/2 * D
#  N4     : rank_F2( ((M - cover)/2) o Q ) <= 2D
#  RELAXED (decoder-strength, no cross term): mu4 <= sum C(d+1,2)   (expected to FAIL with relays)
# mu4 = number of Smith invariants of (M o Q mod 4) not divisible by 4.
import random, itertools, sys
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 1)
h=int(sys.argv[2]) if len(sys.argv)>2 else 4
TR=int(sys.argv[3]) if len(sys.argv)>3 else 3000
CTRL=len(sys.argv)>4 and sys.argv[4]=='ctrl'
def dot(x,y): return bin(x&y).count('1')&1
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]
n=len(labs)
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return s
def rand_sub(dim,inside=None):
    base=list(range(1<<h)) if inside is None else sorted(inside)
    while True:
        g=[random.choice(base) for _ in range(dim)]
        S=span(g)
        if len(S)==1<<dim: return frozenset(S)
def dimof(S): return len(S).bit_length()-1
def rk2(rows):
    basis=[]
    for x in rows:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
def mu4(A):
    A=[[x%4 for x in r] for r in A]; R=len(A); C=len(A[0]); cnt=0
    rows=list(range(R)); cols=list(range(C))
    while True:
        piv=None
        for i in rows:
            for j in cols:
                if A[i][j]%2: piv=(i,j);break
            if piv:break
        if not piv:break
        i,j=piv; inv=A[i][j]  # 1 or 3, self-inverse mod 4
        for i2 in rows:
            if i2!=i and A[i2][j]:
                f=(A[i2][j]*inv)%4
                A[i2]=[(A[i2][c]-f*A[i][c])%4 for c in range(C)]
        rows.remove(i); cols.remove(j); cnt+=1
    # remaining all even
    rest=[sum(((A[i][j]//2)&1)<<k for k,j in enumerate(cols)) for i in rows]
    return cnt+rk2(rest)
def matmul(X,Y):
    return [[sum(X[i][k]*Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
viol={'fwd':0,'mir':0,'sum':0,'n4':0,'relaxed':0}; tight={'fwd':0,'sum':0}; ex=None; tested=0
for tr in range(TR):
    m=random.randint(2,5)
    nodes=[]
    for k in range(m):
        da=random.randint(1,h); db=random.randint(0,da-1)
        a=rand_sub(da); b=rand_sub(db,a) if db>0 else frozenset({0})
        nodes.append((a,b))
    F=[[0]*n for _ in range(m)]; G=[[0]*m for _ in range(n)]; H=[[0]*m for _ in range(m)]
    for k,(a,b) in enumerate(nodes):
        for p,q in enumerate(labs):
            if q in a and random.random()<.6: F[k][p]=random.randint(1,3)
            if all(dot(q,y)==0 for y in b) and random.random()<.6: G[p][k]=random.randint(1,3)
        for j in range(k):
            ok = nodes[j][1] <= a
            if (ok or CTRL) and random.random()<.6: H[k][j]=random.randint(1,3)
    # N = sum H^i (integers)
    N=[[int(i==j) for j in range(m)] for i in range(m)]; P=[r[:] for r in N]
    for _ in range(m):
        P=matmul(P,H); N=[[N[i][j]+P[i][j] for j in range(m)] for i in range(m)]
    M=matmul(matmul(G,N),F)
    Qm=[[dot(s,t) for t in labs] for s in labs]
    MQ=[[M[i][j]*Qm[i][j] for j in range(n)] for i in range(n)]
    if all(x%4==0 for r in MQ for x in r): continue
    tested+=1
    # cover: hat matrices
    Gh=[[x&1 for x in r] for r in G]; Hh=[[x&1 for x in r] for r in H]; Fh=[[x&1 for x in r] for r in F]
    Nh=[[int(i==j) for j in range(m)] for i in range(m)]; P=[r[:] for r in Nh]
    for _ in range(m):
        P=matmul(P,Hh); Nh=[[Nh[i][j]+P[i][j] for j in range(m)] for i in range(m)]
    cov=matmul(matmul(Gh,Nh),Fh)
    Lrows=[sum((((M[i][j]-cov[i][j])//2)&1)*Qm[i][j]<<j for j in range(n)) for i in range(n)]
    D=sum(dimof(a)-dimof(b) for a,b in nodes)
    inn=[any(H[k][j] for j in range(m)) for k in range(m)]
    out=[any(H[k][j] for k in range(m)) for j in range(m)]
    sf=sum((dimof(a)-dimof(b))*(dimof(a)-dimof(b)+1)//2 + inn[k]*(dimof(a)-dimof(b))*(h-dimof(a)) for k,(a,b) in enumerate(nodes))
    sm=sum((dimof(a)-dimof(b))*(dimof(a)-dimof(b)+1)//2 + out[k]*(dimof(a)-dimof(b))*dimof(b) for k,(a,b) in enumerate(nodes))
    srel=sum((dimof(a)-dimof(b))*(dimof(a)-dimof(b)+1)//2 for a,b in nodes)
    mu=mu4(MQ)
    if mu>sf: viol['fwd']+=1
    if mu>sm: viol['mir']+=1
    if 2*mu>(h+1)*D: viol['sum']+=1
    if rk2(Lrows)>2*D: viol['n4']+=1
    if mu>srel:
        viol['relaxed']+=1
        if ex is None or (D,m)<(ex[0],ex[1]): ex=(D,m,mu,srel,[(sorted(a),sorted(b)) for a,b in nodes],H)
    if mu==sf: tight['fwd']+=1
    if 2*mu==(h+1)*D: tight['sum']+=1
print('h',h,'ctrl',CTRL,'tested',tested,'viol',viol,'tight',tight)
if ex: print('smallest relaxed violation D,m,mu,sumC(d+1,2):',ex[:4]); print(' nodes',ex[4]); print(' H',ex[5])
