# NET2DEC: smallest-D legal 2-node relay network violating the per-node Smith law mu4 <= sum C(d+1,2). Own code.
import random, sys
src=open('ngfuzz.py').read().split('viol={')[0]
sys.argv=['x','13',sys.argv[1],'0']
exec(src)
random.seed(13)
best=None
for tr in range(20000):
    dj=random.randint(1,h-1); bj=rand_sub(h-dj)
    aj=frozenset(range(1<<h))
    ak=frozenset(span(list(bj)+[random.randrange(1<<h) for _ in range(random.randint(0,1))]))
    dk=random.randint(1,dimof(ak)); bk=rand_sub(dimof(ak)-dk,ak) if dimof(ak)-dk>0 else frozenset({0})
    nodes=[(aj,bj),(ak,bk)]
    F=[[0]*n for _ in range(2)]; G=[[0]*2 for _ in range(n)]
    for k,(a,b) in enumerate(nodes):
        for p,q in enumerate(labs):
            if q in a and random.random()<.7: F[k][p]=random.randint(1,3)
            if all(dot(q,y)==0 for y in b) and random.random()<.7: G[p][k]=random.randint(1,3)
    H=[[0,0],[random.randint(1,3),0]]
    M=matmul(matmul(G,[[1,0],[H[1][0],1]]),F)
    Qm=[[dot(s,t) for t in labs] for s in labs]
    MQ=[[M[i][j]*Qm[i][j] for j in range(n)] for i in range(n)]
    mu=mu4(MQ); D=dj+dk; srel=dj*(dj+1)//2+dk*(dk+1)//2
    if mu>srel and (best is None or (D,-(mu-srel))<(best[0],-(best[1]-best[2]))):
        best=(D,mu,srel,dj,dk,sorted(bj),sorted(ak),sorted(bk),H[1][0],F,G)
if best:
    D,mu,srel,dj,dk,bj,ak,bk,hh,F,G=best
    print('h',h,'n',n,'D',D,'mu4',mu,'sumC(d+1,2)',srel,'dj',dj,'dk',dk)
    print('a_j = F2^h, b_j =',bj); print('a_k =',ak,' b_k =',bk,' H_kj =',hh)
    print('F_j =',F[0]); print('F_k =',F[1]); print('G_:j =',[r[0] for r in G]); print('G_:k =',[r[1] for r in G])
    print('labels',labs)
else: print('h',h,'none')
