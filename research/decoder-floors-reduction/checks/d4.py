import numpy as np, itertools
from res_setup import *
from collections import Counter, defaultdict
Lm=L; E8=np.array(D['E8'])
allr=list(E8)+[-r for r in E8]
off=lambda h: frozenset(t for t in range(v) if abs(Lm[t]@h)>1e-9)
dirs={}
for r in E8: dirs.setdefault(off(r),('r',tuple(r)))
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]
    if round(s@s)==4: dirs.setdefault(off(s),('n4',tuple(s)))
sel={o:dirs[o] for o in dirs if len(o)<=76}
Oset={z:frozenset(O[z]) for z in range(1,512)}
sets12=defaultdict(list)
for o,(kind,h) in sel.items():
    if len(o)!=76: continue
    for z in range(1,512):
        I=Oset[z]&o
        if len(I)==12: sets12[I].append((h,z))
print('12-overlap (h,z) total',sum(len(x) for x in sets12.values()),'distinct sets',len(sets12))
# labels span / 12-line flats
def span_dim(S):
    basis=[]
    for s in S:
        x=LAB[s]
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
cnt=Counter()
for I in sets12: cnt[span_dim(I)]+=1
print('label span dims of 12-sets',cnt)

def closure(S):
    # lines whose label lies in span of labels of S
    basis=[]
    for s_ in S:
        x=LAB[s_]
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    def inspan(x):
        for b in basis: x=min(x,x^b)
        return x==0
    return [t for t in range(v) if inspan(LAB[t])]
res=Counter()
for I,lst in sets12.items():
    cl=closure(I); res[(len(I),span_dim(I),len(cl),len(lst))]+=1
print(res)
