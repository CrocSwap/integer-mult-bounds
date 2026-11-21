# Gram-class danger search over E8 subsets: minimise 13*c(P) - 7*|P| (negative => ratio < 7/13 => LOUD in the rung, any h <= 9).
# Designs: wB biorthogonal root pairs (P104's), orthoframe, random root bases + dual basis. Uses OMEGA48 lib (own lane code).
import sys, random, math
sys.path.insert(0,'<research-tree>/cards/WILD/OMEGA48')
from lib import L, E, A_FR, R16, wb_pairs, dot, rho, par
from fractions import Fraction as Fr
import numpy as np
seed=int(sys.argv[1]) if len(sys.argv)>1 else 0; vmax=int(sys.argv[2]) if len(sys.argv)>2 else 95
random.seed(seed)
n=len(L)
def terms_supp(terms):
    return [([i for i in range(n) if dot(E[L[i]],u)!=0],[i for i in range(n) if dot(E[L[i]],w)!=0]) for u,w in terms]
def dual_basis(Wv):
    M=np.array(Wv,dtype=object)  # 8 vectors in 9-dim sum-zero space; dual within the span
    G=[[Fr(dot(a,b)) for b in Wv] for a in Wv]
    # inverse Gram
    k=len(G); A=[row[:]+[Fr(int(i==j)) for j in range(k)] for i,row in enumerate(G)]
    for c in range(k):
        p=next(i for i in range(c,k) if A[i][c]!=0); A[c],A[p]=A[p],A[c]
        A[c]=[x/A[c][c] for x in A[c]]
        for i in range(k):
            if i!=c and A[i][c]!=0:
                f=A[i][c]; A[i]=[x-f*y for x,y in zip(A[i],A[c])]
    Gi=[r[k:] for r in A]
    U=[]
    for i in range(k):
        v=[sum(Gi[i][j]*Wv[j][t] for j in range(k)) for t in range(9)]
        den=1
        for x in v: den=den*x.denominator//math.gcd(den,x.denominator)
        U.append(tuple(int(x*den) for x in v))
    return U
def random_root_design():
    while True:
        idx=random.sample(range(n),8); Wv=[E[L[i]] for i in idx]
        if np.linalg.matrix_rank(np.array(Wv,dtype=float))==8: break
    U=dual_basis(Wv); return list(zip(U,Wv))
designs={'wB':[(E[y],E[z]) for y,z in wb_pairs()],'frame':[(E[a],E[a]) for a in A_FR]}
for t in range(4): designs[f'rand{t}']=random_root_design()
lab=[L[i] for i in range(n)]
def cost(sup,P):
    c=0
    for A,B in sup:
        SA=[lab[i] for i in A if P[i]]; SB=[lab[i] for i in B if P[i]]
        if SA and SB: c+=rho(SA,SB)
    return c
def run(name,terms,starts,iters=40000):
    sup=terms_supp(terms); best=None
    for sname,P0 in starts:
        P=P0[:]; v=sum(P); c=cost(sup,P); f=13*c-7*v
        T=6.0
        for it in range(iters):
            i=random.randrange(n)
            if not P[i] and v>=vmax: continue
            P[i]^=1; v2=v+(1 if P[i] else -1)
            if v2==0: P[i]^=1; continue
            c2=cost(sup,P); f2=13*c2-7*v2
            if f2<=f or random.random()<math.exp((f-f2)/T): v,c,f=v2,c2,f2
            else: P[i]^=1
            T=max(0.3,T*0.9999)
            if best is None or f<best[0] : best=(f,c,v,sname,[L[j] for j in range(n) if P[j]])
        print(f'  {name} start={sname}: end v={v} c={c} f={f} | best so far f={best[0]} (c={best[1]}, v={best[2]})'); sys.stdout.flush()
    return best
P120=[1]*n; P104=[0 if L[i] in R16 else 1 for i in range(n)]
def rnd(k): s=set(random.sample(range(n),k)); return [1 if i in s else 0 for i in range(n)]
results={}
for name,terms in designs.items():
    starts=[('P104cut',[1 if (P104[i] and random.random()<0.9) else 0 for i in range(n)]),('rand80',rnd(80)),('rand60',rnd(60))]
    b=run(name,terms,starts); results[name]=b
    print(name,'BEST f',b[0],'c',b[1],'v',b[2],'ratio',round(b[1]/b[2],4),'LOUD' if b[0]<0 else ''); sys.stdout.flush()
