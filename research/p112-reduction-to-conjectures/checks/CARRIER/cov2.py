# vectorised Circuit-kill covering: Off (<= 80 lines) covered by a 7-flat + flats ds_rest + s free lines.
from lib import *
import numpy as np, pickle, itertools, sys, time
from cov import can_cover, rref_basis, inspan
labP=[lab[t] for t in P]; Pidx={t:i for i,t in enumerate(P)}
sets=pickle.load(open('offsets80.pkl','rb'))
Z=[0]*512
for a in range(1,512):
    m=0
    for i,t in enumerate(P):
        if not par(a&lab[t]): m|=1<<i
    Z[a]=m
masks=set()
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)<b: continue
        masks.add(Z[a]&Z[b])
masks=sorted(masks)
lo=np.array([m&((1<<64)-1) for m in masks],dtype=np.uint64)
hi=np.array([m>>64 for m in masks],dtype=np.uint64)
def popcnt(a):
    a=a.copy()
    a=a-((a>>np.uint64(1))&np.uint64(0x5555555555555555))
    a=(a&np.uint64(0x3333333333333333))+((a>>np.uint64(2))&np.uint64(0x3333333333333333))
    a=(a+(a>>np.uint64(4)))&np.uint64(0x0f0f0f0f0f0f0f0f)
    return (a*np.uint64(0x0101010101010101))>>np.uint64(56)
def _bits(m):
    i=0
    while m:
        low=m&-m; yield low.bit_length()-1; m^=low
g={0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36}
def cover7(off, ds_rest, s, want=1):
    """True/witness if exists 7-flat V (any 7-flat incl. those with few lines) s.t. rest covered by ds_rest flats + s lines."""
    om=0
    for t in off: om|=1<<Pidx[t]
    ol=np.uint64(om&((1<<64)-1)); oh=np.uint64(om>>64)
    rl=ol&~lo; rh=oh&~hi
    cnt=popcnt(rl)+popcnt(rh)
    cap=sum(g[w] for w in ds_rest)+s
    idx=np.nonzero(cnt<=cap)[0]
    # sort by remaining size ascending (most coverage first)
    idx=idx[np.argsort(cnt[idx],kind='stable')]
    memo={}
    for k in idx:
        R=(int(rh[k])<<64)|int(rl[k])
        labs=tuple(sorted(labP[i] for i in _bits(R)))
        if can_cover(labs,tuple(sorted(ds_rest,reverse=True)),s,memo): return True,masks[k]
    return False,None
if __name__=='__main__':
    tests=eval(sys.argv[1])   # list of (name, ds_rest, s, lim)
    for name,ds_rest,s,lim in tests:
        t0=time.time(); out={}
        for off,v in sets.items():
            if len(off)>lim: continue
            ok,_=cover7(off,ds_rest,s)
            key=(len(off),v[0][0],ok); out[key]=out.get(key,0)+1
        print(name,sorted(out.items()),round(time.time()-t0),flush=True)
