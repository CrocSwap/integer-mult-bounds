# ZPIN3 lemex.py: combinatorial conditions of Lemma EX (robust exactness) on the 14 tetrads of a frame, all Sigma-pairs {a,b}, all I, |I|<=2.
import sys, itertools
from blib import *
F=frames()[0]; TT=tetrads(F)
idx={f:i for i,f in enumerate(F)}
tets=sorted({tuple(sorted(idx[f] for f in T)) for T in TT}); print('tetrads',len(tets),'lines per tetrad',sorted({len(v) for v in TT.values()}))
tets=[frozenset(t) for t in tets]
bad=0; cases=0; fl=[]
for a,b in itertools.combinations(range(8),2):
    for r in range(0,3):
        for I in itertools.combinations(range(8),r):
            I=set(I)
            for T in tets:
                if len(T&I)>2: bad+=1; continue
                for k in T:
                    cases+=1
                    ok=False
                    for c in T-{k}:
                        if c in I or {k,c}=={a,b}: continue
                        Ts=[T2 for T2 in tets if k in T2 and c in T2 and T2!=T]
                        if any(not({a,b}<=T2) for T2 in Ts): ok=True;break
                    if not ok: bad+=1; fl.append((a,b,tuple(sorted(I)),tuple(sorted(T)),k))
print('cases',cases,'failures',bad)
# check every triple lies in exactly one tetrad and every pair in exactly 3
print(all(sum(1 for T in tets if set(t)<=T)==1 for t in itertools.combinations(range(8),3)), all(sum(1 for T in tets if set(p)<=T)==3 for p in itertools.combinations(range(8),2)))

print(fl[:6]); print(sorted({len(x[2]) for x in fl}), len({x[0:2] for x in fl}))
