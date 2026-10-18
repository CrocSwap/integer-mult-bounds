# Exact rank-9 realisations of the E8 iff pattern: the A2 family (CONJB 1.2) and B-form (D1 G D2 + c beta^T), with checks.
#   A2: rows a_u=(r_u,0) off X, a_{u_i}=(r_i+g_i,1); cols b_s=(r_s,z_s), z_s=-g_i.r_s on O_{u_i}, z free on X (g_1=0, g_2,g_3 in span(r_1,r_2)).
#   B : a_u=(d1_u r_u, c_u), b_s=(d2_s r_s, beta_s) with c_u beta_s = 0 on orthogonal pairs.
# usage: python a2e8.py   (prints PASS lines).  Also imported by soundtest.py (build_a2, build_b).
import random, itertools
from fractions import Fraction as Fr
from e8lib import E,N,G,O,dot
from modrank import rkp
R=[[Fr(x) for x in r] for r in E]
idx={tuple(r):i for i,r in enumerate(R)}
def line_of(w):
    t=tuple(w); n=tuple(-x for x in w)
    return idx.get(t, idx.get(n))
def a2_triangles():
    out=set()
    for i in range(N):
        for j in range(i+1,N):
            if G[i][j]==0: continue
            s=1 if G[i][j]>0 else -1
            k=line_of([a-s*b for a,b in zip(R[i],R[j])])
            if k is not None and k not in (i,j): out.add(tuple(sorted((i,j,k))))
    return sorted(out)
TRI=a2_triangles()
def build_a2(seed,tri=None):
    rnd=random.Random(seed); u=TRI[0] if tri is None else TRI[tri % len(TRI)]
    g=[[Fr(0)]*8]
    for _ in range(2):
        al,be=rnd.randint(-9,9),rnd.randint(-9,9)
        g.append([al*a+be*b for a,b in zip(R[u[0]],R[u[1]])])
    z=[None]*N
    for s in range(N):
        vals={-dot(g[i],R[s]) for i in range(3) if G[u[i]][s]==0}
        assert len(vals)<=1,'inconsistent z'
        z[s]=vals.pop() if vals else Fr(rnd.randint(-50,50),rnd.randint(1,7))
    A=[R[s]+[Fr(0)] for s in range(N)]
    for i in range(3): A[u[i]]=[a+b for a,b in zip(R[u[i]],g[i])]+[Fr(1)]
    B=[R[s]+[z[s]] for s in range(N)]
    return u,A,B
def build_b(seed,kind='single'):
    # redraw the free scalars until no accidental extra zero occurs (a cancellation d1 d2 G + c beta = 0 on a non-orthogonal pair)
    for t in range(1000):
        S,Sb,A,B=_build_b(seed*1000+t,kind)
        M=[[dot(A[i],B[j]) for j in range(N)] for i in range(N)]
        if not any((M[i][j]==0)!=(i!=j and G[i][j]==0) for i in range(N) for j in range(N)): return S,Sb,A,B
    raise RuntimeError
def _build_b(seed,kind):
    rnd=random.Random(seed)
    if kind=='single':
        u0=rnd.randrange(N); S=[u0]; Sb=[s for s in range(N) if G[u0][s]!=0]     # supp c = {u0}, supp beta = Nbar[u0]
    else:                                                                         # clique supp c, common non-neighbours
        S=[]; c=list(range(N)); rnd.shuffle(c)
        for u in c:
            if all(G[u][w]!=0 for w in S): S.append(u)
        Sb=[s for s in range(N) if all(G[s][w]!=0 for w in S)]
    d1=[Fr(rnd.randint(1,5)) for _ in range(N)]; d2=[Fr(rnd.randint(1,5)) for _ in range(N)]
    A=[[d1[u]*x for x in R[u]]+[Fr(rnd.randint(1,9)) if u in S else Fr(0)] for u in range(N)]
    B=[[d2[s]*x for x in R[s]]+[Fr(rnd.randint(1,9)) if s in Sb else Fr(0)] for s in range(N)]
    return S,Sb,A,B
def check(A,B,label):
    M=[[dot(A[i],B[j]) for j in range(N)] for i in range(N)]
    bad=[(i,j) for i in range(N) for j in range(N) if (M[i][j]==0)!=(i!=j and G[i][j]==0)]
    return M,bad,(rkp(A)==9 and rkp(B)==9)     # A,B of full column rank 9 (mod-p rank <= Q rank <= 9)  =>  rank M = 9
if __name__=='__main__':
    print('A2 triangles in E8:',len(TRI)); assert len(TRI)==1120
    for seed,tri in [(1,0),(2,0),(3,17),(4,400),(5,1119)]:
        u,A,B=build_a2(seed,tri); M,bad,full=check(A,B,'a2')
        assert not bad and full
        off=[w for w in range(N) if w not in u]; assert all(M[w][s]==dot(R[w],R[s]) for w in off for s in range(N))
        print('PASS A2 member seed %d triangle %s: iff pattern exact, rank 9, rows off X equal Gram rows'%(seed,list(u)))
    for seed,kind in [(1,'single'),(2,'single'),(3,'clique'),(4,'clique')]:
        S,Sb,A,B=build_b(seed,kind); M,bad,full=check(A,B,'b')
        assert not bad and full and all(G[u][s]!=0 for u in S for s in Sb)
        print('PASS B-form member seed %d (%s, |supp c|=%d, |supp beta|=%d): iff pattern exact, rank 9'%(seed,kind,len(S),len(Sb)))
    print('PASS a2e8')
