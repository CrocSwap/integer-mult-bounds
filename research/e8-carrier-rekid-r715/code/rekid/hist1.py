import sys,time
from collections import Counter
import hx
h,atoms=hx.load(); plans=hx.default_plans(atoms)
for mode in ('cancel','part'):
    S=hx.Search(h,atoms,plans,7,cancel=(mode=='cancel'))
    base=S.R; H=Counter(); n=0; inval=0
    for it in range(3000):
        t=S.rng.choice(S.targets); new=S.propose(t)
        if new is None: inval+=1; continue
        old=S.h.need[t]
        nn=hx.need_of(S.h,new); S.h.need[t]=nn
        x=0
        for u in nn: x^=S.h.content[u]
        if x!=hx.Fm.HYP[t]: S.h.need[t]=old; inval+=1; continue
        R,_=hx.R_of(S.h); H[R-base]+=1; S.h.need[t]=old
    print(mode,'base',base,'invalid',inval,sorted(H.items()))
