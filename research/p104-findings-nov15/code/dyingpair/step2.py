"""DYINGPAIR step 2 [C chk.check, Block Rank Bound, 4^L]: unbalanced L<=9 analogues of B with c own roles entering left stage k dying after d."""
import sys, time; sys.path.insert(0,'.')
from chk import check
def B(L,nl):
    ms=[set(range(L))]*2
    for k in range(nl): ms+=[set(range(k,nl))]*2
    for k in range(L-1,nl-1,-1): ms+=[set(range(nl,k+1))]*2
    return [set(m) for m in ms]
def dying(L,nl,specs):
    ms=B(L,nl)
    for arm,k,d,c,extra in specs:
        if arm=='L': full=set(range(k,nl)); new=set(range(k,d+1)); ex=set(range(d+1,nl))
        else: full=set(range(nl,L-k)); new=set(range(L-1-d,L-k)); ex=set(range(nl,L-1-d))
        for _ in range(c): ms.remove(full); ms.append(set(new))
        for _ in range(extra): ms.append(set(ex))
    return ms
if __name__=='__main__':
    L=int(sys.argv[1]); nl=int(sys.argv[2])
    print('B control L=%d nl=%d violations'%(L,nl), len(check(B(L,nl),L)), flush=True)
    for c in (1,2):
        for k in range(0,nl-2):
            for d in range(k,nl-2):
                for both in (0,1):
                    sp=[('L',k,d,c,0)]+([('R',k,d,c,0)] if both and d<L-nl-2 else [])
                    if both and len(sp)==1: continue
                    t=time.time(); v=check(dying(L,nl,sp),L)
                    print('c=%d k=%d d=%d arms=%d violations %d %s (%.0fs)'%(c,k,d,len(sp),len(v),v[:2],time.time()-t),flush=True)
