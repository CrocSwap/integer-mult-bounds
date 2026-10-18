# row-side dimension jumps: for killed sets K (classes and 2-subspaces) with |S|>=2, d>=1, find theta where the
# constraint rank drops below generic (off B-locus).
import pickle, itertools, sympy as sp, collections
from a2lib import *
al2,be2,al3,be3=sp.symbols('al2 be2 al3 be3')
g=[[0]*8,[al2*x+be2*y for x,y in zip(r1,r2)],[al3*x+be3*y for x,y in zip(r1,r2)]]
h=[[sp.Rational(R[X[i]][k])+g[i][k] for k in range(8)] for i in range(3)]
cl=sorted(cls.items()); sets=[((c,),w) for c,w in cl]; seen=set()
for a in range(len(cl)):
    for b in range(a+1,len(cl)):
        key=tuple(sorted((cl[a][0],cl[b][0],cl[a][0]^cl[b][0])))
        if key in seen: continue
        seen.add(key); sets.append((key,cl[a][1]|cl[b][1]))
Xs=set(X); cnt=collections.Counter(); hits=[]
cache={}
for key,w in sets:
    Kl=bits(w); S=[i for i in range(3) if X[i] in Kl]
    if len(S)<2: continue
    N=nullspace([R[t] for t in Kl if t not in Xs],8)
    if not N: continue
    # phi(N): projections onto (r1.x, r2.x)
    ph=tuple(sorted(set(tuple(x) for x in [[dot(r1,n),dot(r2,n)] for n in N])))
    sig=(tuple(S),tuple(tuple(n) for n in N))
    C=sp.Matrix([[sum((h[i][k]-h[S[0]][k])*n[k] for k in range(8)) for n in N] for i in S[1:]])
    rg=C.subs({al2:3,be2:-7,al3:5,be3:2}).rank()
    cnt[(len(S),len(N),rg)]+=1
    if rg==0: continue
    minors=[C.extract(list(r),list(c)).det() for r in itertools.combinations(range(C.rows),rg) for c in itertools.combinations(range(C.cols),rg)]
    minors=[sp.factor(mm) for mm in minors if mm!=0]
    sols=sp.solve(minors,[al2,be2,al3,be3],dict=True)
    good=[s_ for s_ in sols if sp.simplify((al2-al3-be3).subs(s_))!=0]
    if good: hits.append((key,len(Kl),S,len(N),rg,good[:3]))
print(cnt); print('row jump loci off B-locus:',len(hits))
for x in hits[:30]: print(x)
pickle.dump(hits,open('rowjump.pkl','wb'))
