# directions h in K^8 with |Off(h)| <= LIM on P112; Off sets (as frozenset of P112 indices)
from lib import *
import itertools, sys, pickle
def vecs(maxn):
    out=[]
    # D8 part: coords 2*a_i, sum a_i even, norm sum a_i^2 <= maxn
    rng=range(-2,3)
    def rec(i,cur,ssq,sm):
        if i==8:
            if sm%2==0 and ssq>0: out.append(tuple(2*x for x in cur))
            return
        for a in rng:
            s2=ssq+a*a
            if s2<=maxn: rec(i+1,cur+[a],s2,sm+a)
    rec(0,[],0,0)
    # half-spin: v_i odd, x_i=v_i/2 half-int, sum x_i even i.e. sum v_i ≡ 0 mod 4 ; norm sum v_i^2/4
    for v in itertools.product((-3,-1,1,3),repeat=8):
        if sum(x*x for x in v)<=4*maxn and sum(v)%4==0: out.append(v)
    return out
V=vecs(6)
print('vectors',len(V))
seen={}
for v in V:
    c=canon(v)
    if c in seen: continue
    off=frozenset(t for t in P if sum(a*b for a,b in zip(v,lines[t]))!=0)
    seen[c]=(sum(a*a for a in v)//4,off)
print('directions',len(seen))
from collections import Counter
cnt=Counter((nm,len(o)) for nm,o in seen.values())
print(sorted(cnt.items())[:60])
sets={}
for c,(nm,o) in seen.items():
    if len(o)<=80: sets.setdefault(o,[]).append((nm,c))
print('distinct Off sets <=80:',len(sets), Counter(len(o) for o in sets))
pickle.dump({o:v for o,v in sets.items()},open('offsets80.pkl','wb'))
