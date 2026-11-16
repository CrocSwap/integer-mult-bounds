# exact (6,6,6)+s covering of Off_E(root) (57 lines) by three 6-flats + s free lines, E8 level; also P112-restricted variant not needed.
from e8cov import *
from e8cov import _bits
import numpy as np
M=np.array([[m&((1<<64)-1), m>>64] for m in masks],dtype=np.uint64)
ol=np.uint64(om&((1<<64)-1)); oh=np.uint64(om>>64)
cands=[]
for c in range(1,512):
    zl=np.uint64(Z[c]&((1<<64)-1)); zh=np.uint64(Z[c]>>64)
    lo6=M[:,0]&zl; hi6=M[:,1]&zh
    cov=popcnt(lo6&ol)+popcnt(hi6&oh)
    sel=np.nonzero(cov>=15)[0]
    for k in sel: cands.append((int(hi6[k])<<64)|int(lo6[k]))
cands=sorted(set(cands))
print('6-flat masks covering >=15 Off lines:',len(cands),flush=True)
offm=om
pc=lambda x: bin(x).count('1')
def rank_ok(R,w,s):
    labs=tuple(sorted(labE[i] for i in _bits(R)))
    return remove_cover(labs,w,s)
from cov import remove_cover
C=np.array([[c&((1<<64)-1), c>>64] for c in cands],dtype=np.uint64)
def run(s):
    cl=[(c&offm) for c in cands]
    cnt1=np.array([pc(x) for x in cl])
    order=np.argsort(-cnt1,kind='stable')
    for i in order:
        if cnt1[i]<(57-s+2)//3: break
        R1=offm&~cands[i]
        r1l=np.uint64(R1&((1<<64)-1)); r1h=np.uint64(R1>>64)
        c2=popcnt(C[:,0]&r1l)+popcnt(C[:,1]&r1h)
        sel=np.nonzero(pc(R1)-c2<=20+s)[0]
        for j in sel:
            R2=R1&~cands[j]
            if rank_ok(R2,6,s): return True,(int(i),int(j))
    return False,None
for s in (0,1):
    t0=time.time(); print('(6,6,6)+%d'%s, run(s),round(time.time()-t0),flush=True)
