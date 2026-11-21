from e8shard import *
import random, itertools
random.seed(3)
ports=list(range(n))
# subsystems: lines of E8 (indices 0..119) with G-conditions to chosen lines; restrict to ports
def sub_by_orth(S):  # lines orthogonal (G=0) to all lines in S, intersect ports
    return [t for t in ports if all(G[t,s]==0 for s in S)]
def dimlab(Pp):
    # Gram F2-rank of label set (rank of Q matrix)
    return rk2([sum(Q[t][s]<<j for j,s in enumerate(Pp)) for t in Pp])
best={}
for k in (1,2,3,4):
    for trial in range(3000 if k>1 else 120):
        S=random.sample(range(120),k)
        # require S mutually orthogonal?
        Pp=sub_by_orth(S)
        if len(Pp)<4: continue
        pr=prices(Pp); g=len(Pp)-sum(pr); gr=dimlab(Pp)
        if k not in best or g>best[k][0]: best[k]=(g,len(Pp),pr,gr,S)
    print('k',k,'best',best[k],flush=True)
