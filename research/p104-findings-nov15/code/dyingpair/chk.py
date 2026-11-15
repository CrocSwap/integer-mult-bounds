"""ARMTREE chk.py: check the Block Rank Bound (ilp2) on a mask layout; layouts for L=8: B form, toy 'two bounded headers'."""
import sys, itertools, numpy as np
from ilp2 import samples, minrank
def masks_B(L,nl,hubs=2,grow=2):
    ms=[set(range(L))]*hubs
    for k in range(nl): ms+= [set(range(k,nl))]*grow
    for k in range(L-1,nl-1,-1): ms+=[set(range(nl,k+1))]*grow
    return ms
def piece(lo,hi,nl,grow=2):   # time-contiguous mountain piece stages lo..hi-1, centre between lo+nl-1 | lo+nl
    ms=[]
    for k in range(lo,lo+nl): ms+=[set(range(k,lo+nl))]*grow
    for k in range(hi-1,lo+nl-1,-1): ms+=[set(range(lo+nl,k+1))]*grow
    return ms
def toy(L=8,hubs=2,npieces=2):
    ms=[set(range(L))]*hubs; w=L//npieces
    for p in range(npieces): ms+=piece(p*w,(p+1)*w,w//2)
    return ms
def check(ms,L,verbose=True):
    Gs=samples(L); viol=[]
    for lab in itertools.product(range(4),repeat=L):
        ma=sum(1<<i for i in range(L) if lab[i] in(1,3)); mb=sum(1<<i for i in range(L) if lab[i] in(2,3))
        if not ma or not mb or ma>mb and False: continue
        A=[i for i in range(L) if ma>>i&1];B=[i for i in range(L) if mb>>i&1]
        need=minrank(Gs,A,B); have=sum(1 for m in ms if (m&set(A)) and (m&set(B)))
        if have<need: viol.append((A,B,need,have))
    return viol
if __name__=='__main__':
    L=int(sys.argv[1]); 
    for name,ms in (('B form',masks_B(L,L//2)),('toy 2 pieces hubs2',toy(L,2,2)),('toy 2 pieces hubs4',toy(L,4,2)),('toy 2 pieces hubs2 own+1',toy(L,2,2))):
        v=check(ms,L); print(name,'n',len(ms),'Z',[sum(1 for m in ms if k in m) for k in range(L)],'violations',len(v),v[:3],flush=True)
