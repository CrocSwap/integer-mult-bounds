"""Rank-1 entrance pool: nondegenerate small-coefficient lines inside first frames of dim <= MAXD, with all helpers whose first frame contains each line. Usage: lines.py HELPERS.pkl OUT.pkl [MAXD]
Chafik Boukhalfa (chafreaky), Anthropic Claude assistance; Apache-2.0."""
import pickle,sys,itertools,collections,math
from math import gcd
import numpy as np
d=pickle.load(open(sys.argv[1],'rb'));ff=d['firstframe'];ft=d['ftab'];MAXD=int(sys.argv[3]) if len(sys.argv)>3 else 5
def prim(v):
    g=0
    for a in v:g=gcd(g,abs(a))
    if g==0:return None
    v=[a//g for a in v]
    for a in v:
        if a:
            if a<0:v=[-x for x in v]
            break
    return tuple(v)
def nondeg(u):return 9*sum(x*x for x in u)-sum(u)**2!=0
pool=set()
for f,F in ft.items():
    B=F['B'];k=F['dim']
    if k>MAXD:continue
    rng=(-1,0,1) if k>2 else (-2,-1,0,1,2)
    for co in itertools.product(rng,repeat=k):
        if not any(co):continue
        u=prim([sum(c*b[i] for c,b in zip(co,B)) for i in range(20)])
        if u and nondeg(u):pool.add(u)
pool=sorted(pool);print('pool lines',len(pool),flush=True)
U=np.array(pool,dtype=np.int64).T  # 20 x L
frames=sorted(ft);mem=collections.defaultdict(list)
byframe=collections.defaultdict(list)
for s in d['helpers']:byframe[ff[s]].append(s)
for f in frames:
    A=np.array(ft[f]['A'],dtype=np.int64)
    if A.size==0:hit=np.ones(len(pool),bool)
    else:hit=~np.any(A@U,axis=0)
    for j in np.nonzero(hit)[0]:mem[pool[j]].extend(byframe[f])
mem={u:L for u,L in mem.items() if len(L)>1}
print('lines with >=2 helpers',len(mem),'max group',max(len(L) for L in mem.values()),flush=True)
pickle.dump(mem,open(sys.argv[2],'wb'))
