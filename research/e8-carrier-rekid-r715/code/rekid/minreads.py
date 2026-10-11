import os,sys,pickle,itertools
os.environ['E8COORD']='ham'
import frames as Fm, e8lib as E
from collections import Counter
sys.modules['__main__'].SH=None
import ham1
h=pickle.load(open('h865.pkl','rb'))
V=120
res=Counter(); detail={}
for t in range(V):
    tgt=Fm.HYP[t]  # content mask of junk = HYP[t] as lines
    pool=[u for u in range(V,len(h.content)) if Fm.inside(h.frame[u],Fm.HYP[t])]
    vec=[h.content[u] for u in pool]
    # exclude sources (single lines) from pool to see symbol reads; include them as extras later
    d2={}
    # pairs
    one={v:(i,) for i,v in enumerate(vec)}
    best=None
    cur=len(h.need[t])
    # find min k<=4 using meet in middle: sets of size<=2 and <=2
    pairs={}
    for i,a in enumerate(vec):
        pairs.setdefault(a,(i,))
    for i in range(len(vec)):
        for j in range(i+1,len(vec)):
            x=vec[i]^vec[j]
            if x not in pairs: pairs[x]=(i,j)
    found=None
    if tgt in pairs: found=pairs[tgt]
    else:
        for x,idx in pairs.items():
            y=tgt^x
            if y in pairs: found=idx+pairs[y]; break
    res[(cur,len(found) if found else None)]+=1
print(sorted(res.items(),key=str))
