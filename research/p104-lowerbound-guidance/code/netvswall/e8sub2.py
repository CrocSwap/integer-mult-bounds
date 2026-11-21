from e8shard import *
import random, sys
random.seed(2)
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return s
# dim 8: all hyperplanes v^perp
best=None
for v in range(1,512):
    W=[x for x in range(512) if dot(x,v)==0]; Ws=set(W)
    Pp=[t for t in range(n) if U[t] in Ws]
    pr=prices(Pp); key=(len(Pp)-sum(pr),len(Pp))
    if best is None or key>best[0]: best=(key,v,pr,dot(v,v))
print('dim8 all hyperplanes best',best,flush=True)
# dim 7: all perp of 2-dim subspaces; compute plain restriction, no greedy
best=None; cnt=0; seenW=set()
for v1 in range(1,512):
    for v2 in range(v1+1,512):
        S=frozenset(span([v1,v2]))
        if len(S)!=4 or S in seenW: continue
        seenW.add(S)
        W=[x for x in range(512) if all(dot(x,s)==0 for s in S)]; Ws=set(W)
        Pp=[t for t in range(n) if U[t] in Ws]
        if len(Pp)<3: continue
        pr=prices(Pp); key=(len(Pp)-sum(pr),len(Pp))
        if best is None or key>best[0]: best=(key,sorted(S),pr)
print('dim7 all best',best,len(seenW),flush=True)
