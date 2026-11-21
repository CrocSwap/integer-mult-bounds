"""mp6b: controls for mp6.numeric, then numeric stage on the 25 GF2 survivors (recomputed)."""
import mp6,itertools,numpy as np,time
F=frozenset;A=F(range(8));X=F({0,1,2,3});Y=F({0,4,5,6})
pcs=[F(p) for p in [{0,1},{2,3},{4,5},{6,7},{0,4},{5,6},{1,2},{3,7}]]
cell={s:(s in X)*2+(s in Y) for s in range(8)}
t=time.time();print('NEG 8cycle gf2',mp6.gf2(cell,set(pcs)),'numeric %.2e'%mp6.numeric([X,A-X,Y,A-Y],set(pcs)),'%.0fs'%(time.time()-t),flush=True)
# POS control: same pairs but signs replaced by a planted solution -> build M from random U,W? use: no masks, keep only pairs between X and Xc where eps rank-1 (X before Xc)
keep=set(F(c) for c in itertools.combinations(range(8),2) if not (min(c)<4<=max(c)))
print('POS cross-only numeric %.2e'%mp6.numeric([F({0}),F({1}),F({2}),F({3})],keep),flush=True)
seen=set();surv=[]
splits=[F(c) for c in itertools.combinations(range(8),4) if 0 in c]
for X in splits:
    for Y in splits:
        if Y==X or Y==A-X:continue
        for P in itertools.product(*[list(mp6.pairings(S)) for S in (X,A-X,Y,A-Y)]):
            p=[q for pp in P for q in pp];key=mp6.canon(X,Y,p)
            if key in seen:continue
            seen.add(key);c={s:(s in X)*2+(s in Y) for s in range(8)}
            if mp6.gf2(c,set(p)):surv.append((X,Y,p))
print('survivors',len(surv),flush=True)
nb=0
for X,Y,p in surv:
    f=mp6.numeric([X,A-X,Y,A-Y],set(p));nb+=f<1e-9
    print('SOLVES' if f<1e-9 else 'stall','%.2e'%f,sorted(X),sorted(Y),[tuple(sorted(q)) for q in p],flush=True)
print('END solves',nb,'of',len(surv),flush=True)
