# NET2DEC targeted 2-node test of the relaxed (no cross term) graded bound. Own code; imports helpers by exec of ngfuzz defs.
import random, sys
src=open('ngfuzz.py').read().split('viol={')[0]
sys.argv=['x','11',sys.argv[1] if len(sys.argv)>1 else '6','0']
exec(src)
random.seed(11)
best=None; cnt=0
for tr in range(4000):
    dj=random.randint(1,3); bj=rand_sub(h-dj) if h-dj>0 else frozenset({0})
    aj=frozenset(range(1<<h))
    # a_k = b_j + extra
    ex=random.randint(0,2)
    ak=span(list(bj)+[random.randrange(1<<h) for _ in range(ex)]); ak=frozenset(ak)
    dk=random.randint(1,dimof(ak)); bk=rand_sub(dimof(ak)-dk,ak) if dimof(ak)-dk>0 else frozenset({0})
    nodes=[(aj,bj),(ak,bk)]; m=2
    F=[[0]*n for _ in range(m)]; G=[[0]*m for _ in range(n)]; H=[[0,0],[random.randint(1,3),0]]
    depj=random.random()<.5
    for k,(a,b) in enumerate(nodes):
        for p,q in enumerate(labs):
            if q in a and random.random()<.7: F[k][p]=random.randint(1,3)
            if (k==1 or depj) and all(dot(q,y)==0 for y in b) and random.random()<.7: G[p][k]=random.randint(1,3)
    N=[[1,0],[H[1][0],1]]
    M=matmul(matmul(G,N),F)
    Qm=[[dot(s,t) for t in labs] for s in labs]
    MQ=[[M[i][j]*Qm[i][j] for j in range(n)] for i in range(n)]
    mu=mu4(MQ); D=sum(dimof(a)-dimof(b) for a,b in nodes)
    srel=sum((dimof(a)-dimof(b))*(dimof(a)-dimof(b)+1)//2 for a,b in nodes)
    cross=dj*(dimof(bj)-dimof(bj&bk))
    if mu>srel:
        cnt+=1
        if best is None or mu-srel>best[0]: best=(mu-srel,mu,srel,cross,dj,dimof(ak),dk,dimof(bj&bk),depj)
print('h',h,'relaxed violations',cnt,'worst (excess,mu,srel,cross,dj,dim ak,dk,dim bj&bk,depj)',best)
