# E8-level circuit covering (120 lines).  Class I: pieces non-dropping, E8 supports in Lambda_E(F_j).
# Off_E(g) = lines non-orthogonal to g.  Only |Off_E| = 57 (root) is possible when cap < 78.  W(E8) transitive on roots -> ONE rep.
from lib import *
import numpy as np, itertools, sys, time
from cov import can_cover, rref_basis, inspan
labE=lab[:]            # 120 labels
# Off_E for a few directions
def offE(v): return [t for t in range(n) if sum(a*b for a,b in zip(v,lines[t]))!=0]
r0=lines[0]
off_root=offE(r0)
print('root Off_E',len(off_root))
# min |Off_E| over all E8 vectors of norm 4,6 for the record
Z=[0]*512
for a in range(1,512):
    m=0
    for t in range(n):
        if not par(a&lab[t]): m|=1<<t
    Z[a]=m
masks=set()
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)<b: continue
        masks.add(Z[a]&Z[b])
masks=sorted(masks)
print('E8 7-flat masks',len(masks),'max lines',max(bin(m).count('1') for m in masks),flush=True)
lo=np.array([m&((1<<64)-1) for m in masks],dtype=np.uint64); hi=np.array([m>>64 for m in masks],dtype=np.uint64)
def popcnt(a):
    a=a.copy()
    a=a-((a>>np.uint64(1))&np.uint64(0x5555555555555555))
    a=(a&np.uint64(0x3333333333333333))+((a>>np.uint64(2))&np.uint64(0x3333333333333333))
    a=(a+(a>>np.uint64(4)))&np.uint64(0x0f0f0f0f0f0f0f0f)
    return (a*np.uint64(0x0101010101010101))>>np.uint64(56)
def _bits(m):
    while m:
        low=m&-m; yield low.bit_length()-1; m^=low
g={0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36}
om=0
for t in off_root: om|=1<<t
def cover(ds_rest,s,first=7):
    """exists 7-flat (as first big flat) with rest covered by flats ds_rest + s free lines"""
    ol=np.uint64(om&((1<<64)-1)); oh=np.uint64(om>>64)
    rl=ol&~lo; rh=oh&~hi
    cnt=popcnt(rl)+popcnt(rh)
    cap=sum(g[w] for w in ds_rest)+s
    idx=np.nonzero(cnt<=cap)[0]
    idx=idx[np.argsort(cnt[idx],kind='stable')]
    memo={}; tried=0
    for k in idx:
        R=(int(rh[k])<<64)|int(rl[k])
        labs=tuple(sorted(labE[i] for i in _bits(R)))
        tried+=1
        if can_cover(labs,tuple(sorted(ds_rest,reverse=True)),s,memo): return True,tried,len(idx)
    return False,tried,len(idx)
if __name__=='__main__':
    tests=eval(sys.argv[1])
    for name,ds_rest,s in tests:
        t0=time.time(); r=cover(ds_rest,s); print(name,r,round(time.time()-t0,1),flush=True)
