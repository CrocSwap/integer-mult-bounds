# Classify helpers into face modules (center point), LP modules (anti-diagonal line pair), or mixed; sum chain D.
import json, collections, sys, math
import numpy as np
sys.path.insert(0,'/home/claude/work/eval'); sys.path.insert(0,'/home/claude/work/agentA')
from cost import load_snapshot
from decomp import lab
d=sys.argv[1]
s,fr,dim,rec=load_snapshot(d)
v=s['v'];n=s['n'];R=n+1
g=lambda r: r*math.log(120/r) if r>0 else 0
init={r:dim[s['initial'][str(r)]] for r in range(n)}
P=lambda p:p//2
Wd=(v+63)//64
val=np.zeros((R,Wd),np.uint64)
for i in range(v): val[i,i//64]|=np.uint64(1)<<np.uint64(i%64)
ever=np.zeros((R,Wd),np.uint64)
cur={r:dim[s['initial'][str(r)]] for r in range(n)}
chain=collections.defaultdict(list)
for k in range(len(rec)):
    o,a,b,c,f,z=map(int,rec[k])
    if o==0:
        chain[a].append(dim[c]-cur[a]); cur[a]=dim[c]
    elif o==1:
        if c&1:
            val[a]^=val[b]
            if a<n: ever[a]|=val[a]
    elif o==2: val[n]=val[a]
    elif o==3: val[n]=0
labs=[set(l) for l in lab]
def classify(h):
    b=np.unpackbits(ever[h].view(np.uint8),bitorder='little')[:v]
    its=np.nonzero(b)[0]
    if len(its)==0: return ('empty',)
    common=set(lab[its[0]])
    for i in its[1:]: common&=labs[i]
    if common:
        if len(its)<=4: return ('cube-ish',)
        return ('face',)
    # LP module: items of form {c,d',z} or {c',d,z} for fixed anti-diagonal pair in pairs (Pc,Pd)
    # test: there exist two pairs Pc,Pd such that every item contains a point of Pc and a point of Pd with "anti" pattern
    pairsets=[set(P(p) for p in lab[i]) for i in its]
    cp=set.intersection(*pairsets)
    if len(cp)>=2:
        return ('lp',) if len(its)>4 else ('cube-ish',)
    return ('mixed',)
cat=collections.defaultdict(lambda:[0,0.0])
for h in range(2*v,n):
    if init[h]==24: continue
    k=classify(h)+(('sig0' if init[h]==0 else 'gauged'),)
    cat[k][0]+=1; cat[k][1]+=sum(g(x) for x in chain[h] if x>0)
tot=sum(x[1] for x in cat.values())
for k,(c,dd) in sorted(cat.items(), key=lambda x:-x[1][1]):
    print('%-28s n=%5d D=%8.0f (%4.1f%%) per=%.1f'%(str(k),c,dd,100*dd/tot,dd/c))
