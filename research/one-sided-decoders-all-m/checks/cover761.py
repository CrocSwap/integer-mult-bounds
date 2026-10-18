# (audit addition) weight-14 shape (7,6,1) for the root targets: for EVERY one of the 112 roots r, no 7-dim label flat + 6-dim label flat + 1 line covers Off(r) (53 lines); best leaves 9 lines uncovered.
# Sound pruning: |Y| <= 20 (g(6)) and one line, so the 7-flat part must hold >= 32 target lines; (7-flat, 6-flat) pairs enumerated from all label subspaces.
from base import *
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
Lnp=np.array([[float(c) for c in r] for r in L])
def off(h): return sum(1<<t for t in range(v) if abs(Lnp[t]@h)>1e-9)
res={}
for ri in range(v):
    T=off(Lnp[ri])
    if pc(T)!=53: continue
    X=set(); Y=set()
    for a in range(1,512):
        ma=mask[a]&T
        if pc(ma)<20: continue
        for b in range(a+1,512):
            mab=ma&mask[b]
            if pc(mab)<20: continue
            if (a^b)>b: X.add(mab)            # 7-dim subspace (each once)
            for c in range(b+1,512):
                if c==a^b: continue
                m=mab&mask[c]
                if pc(m)>=20: Y.add(m)
    X=[x for x in X if pc(x)>=32-0]  # need |X|+|Y|>=52 with |Y|<=20
    best=min((pc(T&~(x|y)) for x in X for y in Y), default=99)
    res[ri]=(len(X),len(Y),best)

from collections import Counter; print(Counter(res.values()))
print('cover761: all', len(res), 'roots; minimum uncovered lines over (7,6) pairs:', min(b for _,_,b in res.values()))
