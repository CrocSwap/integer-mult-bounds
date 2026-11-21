import sys; sys.set_int_max_str_digits(0)
import re,itertools
src=open('<research-tree>/lean/decoder-duality/Nov15/FrameCert.lean').read()
lp=int(re.search(r'def labelsP : Nat := (\d+)',src).group(1)); fp=int(re.search(r'def framesP : Nat := (\d+)',src).group(1))
lab=[(lp>>(9*t))&511 for t in range(104)]
frames=[(fp>>(104*i))&((1<<104)-1) for i in range(759)]
def par(u): return bin(u).count('1')&1
col=[0]*104
pm={}
def lam(u1,u2):
    m=0
    for t,l in enumerate(lab):
        if par(u1&l)==0 and par(u2&l)==0: m|=1<<t
    return m
def blocking(u1,u2):
    L=lam(u1,u2); return all(f&L for f in frames)
import functools
@functools.lru_cache(None)
def blk(x,y): return blocking(x,y)
# all lines (x<y<x^y)
lines=[(a,b) for a in range(1,512) for b in range(a+1,512) if b<(a^b)]
print(len(lines))
B=[l for l in lines if blk(*l)]
print('blocking lines',len(B))
Bs=set(B)
def canon(x,y):
    z=x^y; t=sorted([x,y,z]); return (t[0],t[1])
bad=0; cnt=0
for (a,b) in B:
    for u in range(1,512):
        if u in (a,b,a^b): continue
        pts=[a,b,a^b,u,u^a,u^b,u^a^b]
        ls=set(canon(p,q) for p in pts for q in pts if p!=q)
        assert len(ls)==7
        cnt+=1
        if all(l in Bs for l in ls): bad+=1
print('planes checked',cnt,'6-dim blocking planes',bad)
