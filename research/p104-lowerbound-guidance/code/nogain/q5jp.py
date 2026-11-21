"""NOGAIN q5jp.py: DX / YC per-level ranks and |C_l| on the Q5 gain network (R2 run read through ⊥ = NETATTR 2-node net)
and the h=5 ZIGZAG network; min-decoder level profiles (supports from NETATTR exact.min_mass, read-only import)."""
import sys; sys.path.insert(0,'../netattr'); sys.path.insert(0,'../unify')
from fractions import Fraction as Fr
from common import *
from netgen import net_M
from exact import min_mass
from zz_level import rankQ
def walks(m,H):
    out=[]
    def ext(w):
        out.append(w)
        for k in range(m):
            if H[k][w[-1]]: ext(w+[k])
    for v in range(m): ext([v])
    return out
def profile(h,nodes,F,G,H):
    n=len(G); m=len(nodes); dims=[(dimof(a),dimof(b)) for a,b in nodes]; W=walks(m,H); rows=[]
    for l in range(1,h+1):
        Cl=sum(1 for a,b in dims if b<l<=a)
        Myc=[[Fr(0)]*n for _ in range(n)]; Mdx=[[Fr(0)]*n for _ in range(n)]
        for w in W:
            coef=Fr(1)
            for x,y in zip(w,w[1:]): coef*=H[y][x]
            g,d=w[0],w[-1]
            yc= dims[g][0]>=l and dims[d][1]<l
            dx= any(dims[w[i]][0]>=l>dims[w[j]][1] for i in range(len(w)) for j in range(i,len(w)))
            for t in range(n):
                if not G[t][d]: continue
                for p in range(n):
                    if F[g][p]:
                        v=G[t][d]*coef*F[g][p]
                        if yc: Myc[t][p]+=v
                        if dx: Mdx[t][p]+=v
        rows.append((l,Cl,rankQ(Myc),rankQ(Mdx)))
    return rows
def report(name,h,labs,nodes,F,G,H,budget):
    n=len(labs); M,N=net_M(G,H,F); Qm=[[dot(s,t) for t in labs] for s in labs]
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    pr=profile(h,nodes,F,G,H); D=sum(dimof(a)-dimof(b) for a,b in nodes)
    print(f'== {name}: D={D}, rank M={rankQ(M)}, rank odd pattern T={rankQ(T)}')
    print('  network (l,|C_l|,rkYC,rkDX):',pr,' junk=',D-sum(r[3] for r in pr))
    st,c,R,res=min_mass(h,labs,T,Qm,budget,timeout=300,diagfree=True)
    print('  min decoder at budget',budget,':',st)
    if c:
        lv=[0]*(h+1)
        for i in c:
            Dl=[labs[t] for t in R[i][0]]; Sl=[labs[p] for p in R[i][1]]
            a=span(Sl); da=dimof(a); db=da-R[i][2]
            for l in range(db+1,da+1): lv[l]+=1
            print('   row: |D|',len(Dl),'|S|',len(Sl),'dim a',da,'price',R[i][2],'dim b',db)
        print('  decoder level counts |C_l| l=1..h:',lv[1:])
    return pr
# Q5 network (UNIFY r2perp.py data)
h=4; labs=[1,2,7,11,13]
def sp(*v): return span(list(v))
P=lambda S: perp(S,h)
j=(P(sp(13)),P(sp(1,12))); k=(P(sp(12)),P(sp(7,12)))
F=[[0]*5 for _ in range(2)]; G=[[0]*2 for _ in range(5)]
F[0][2]=F[0][3]=1; F[1][0]=F[1][1]=1; G[0][0]=1; G[2][1]=G[3][1]=1; H=[[0,0],[1,0]]
assert j[1]<=k[0]
report('Q5 / NA (R2 through perp)',h,labs,[j,k],F,G,H,3)
# ZIGZAG h=5 (UNIFY zzcx.py data)
h=5; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]
I={'A': [0, 3, 5, 6, 8, 11, 13, 14, 16, 19, 21, 22, 24, 27, 29, 30], 'B': [0, 13, 21, 24], 'A2': [0, 7, 10, 13, 18, 21, 24, 31], 'B2': [0, 18], 'F': [[0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]], 'G': [[0, 1], [0, 0], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 1], [0, 0], [0, 1], [1, 0], [0, 1], [1, 0], [0, 1]]}
nodes=[(frozenset(I['A']),frozenset(I['B'])),(frozenset(I['A2']),frozenset(I['B2']))]
report('ZIGZAG h=5',h,labs,nodes,I['F'],I['G'],[[0,0],[1,0]],6)
