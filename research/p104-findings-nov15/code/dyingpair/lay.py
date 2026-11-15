import sys,time,itertools
import numpy as np
from rs2 import *
from chk import check
# time order: stages 0..L-1 ; left arm = 0..nl-1 ; thin between nl-1 and nl ; right arm nl..L-1
def build(rolesets,L,nl):
    n=len(rolesets); Z=[[r for r,s in enumerate(rolesets) if k in s] for k in range(L)]; th=n+2-2*L
    o=[('S',Z[k]) for k in range(nl)]+[('T',)]*th+[('S',Z[k]) for k in range(nl,L)]
    return n,o,th
def B(L,nl):
    ms=[set(range(L))]*2
    for k in range(nl): ms+=[set(range(k,nl))]*2
    for k in range(L-1,nl-1,-1): ms+=[set(range(nl,k+1))]*2
    return ms
def win(L,nl,w):
    ms=[set(range(L))]*2
    for k in range(nl): ms+=[set(range(k,min(k+w,nl)))]*2
    for k in range(L-1,nl-1,-1): ms+=[set(range(max(k-w+1,nl),k+1))]*2
    return ms
if __name__=='__main__':
    name=sys.argv[1]; starts=int(sys.argv[2]); L=int(sys.argv[3]); nl=L//2
    ms={'B':B(L,nl),'w1':win(L,nl,1),'w2':win(L,nl,2)}[name]
    v=check(ms,L); print(name,'L',L,'counting violations',len(v),flush=True)
    n,o,th=build(ms,L,nl); m=Model(n,o,-0.5,()); t0=time.time()
    h,b,z=run(m,starts,seed=3,nfev=1500)
    print('%s L=%d n=%d N=%d dim=%d solved %d/%d best %.1e (%.0fs)'%(name,L,n,m.N,m.dim,h,starts,b,time.time()-t0),flush=True)
