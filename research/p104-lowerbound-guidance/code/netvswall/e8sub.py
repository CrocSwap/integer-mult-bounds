from e8shard import *
import random
random.seed(1)
res={}
# subspaces W of F2^9 by random basis, dim k; P' = ports with label in W
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return s
for k in range(4,9):
    best=None
    for trial in range(4000 if k>=6 else 1500):
        W=span([random.randrange(1,512) for _ in range(k)])
        if len(W)!=1<<k: continue
        Pp=[t for t in range(n) if U[t] in W]
        if len(Pp)<3: continue
        pr=prices(Pp); g=len(Pp)-sum(pr)
        key=(g,len(Pp))
        if best is None or key>best[0]: best=(key,pr,dimspan(Pp))
    print('dim',k,'best (gain,n)',best,flush=True)
