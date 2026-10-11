"""Scan complex local-channel configurations on one cube (p=3): count addition nodes and source fan-out."""
import json, sys, itertools
from collections import Counter
sys.path.insert(0,'/home/claude/cx/tree/scripts')
from paired_cube.graph import Graph
Aopts={(i,a):['fd']+['e%d'%d for d in range(3) if d!=i] for i in range(3) for a in range(2)}
Gopts={(j,k,m):['e','l','s'] for j,k in itertools.combinations(range(3),2) for m in range(2)}
def build(cfg):
    g=Graph(3,local=cfg); g.local_channels()
    v=len(g.labels); n=len(g.a)
    # fan-out: count consumers per node (args reference)
    cons=Counter()
    for x in range(v,n):
        a,b=g.a[x]; cons[a]+=1; cons[b]+=1
    # outputs: F, A, G nodes are consumed by modules (count +1 each)
    outs=set([g.F[I] for I in g.cubes])|set(g.A.values())|set(g.G.values())
    for o in outs: cons[o]+=1
    src=[cons[s] for s in range(v)]
    excess=sum(max(0,cons[x]-1) for x in range(n))
    return n-v, Counter(src), excess, len(outs)
ref=dict(A={'%d,%d'%k:'fd' for k in Aopts},G={'%d,%d,%d'%k:'s' for k in Gopts},F=2)
print('reference (A fd, G s, F2):',build(ref))
L1=json.load(open('tree/references/paired-cube/sources/local_L1.json')); print('local_L1:',build(L1))
best=[]
keysA=sorted(Aopts); keysG=sorted(Gopts)
import random
rng=random.Random(0)
seen=0
for trial in range(20000):
    cfg=dict(A={'%d,%d'%k:rng.choice(Aopts[k]) for k in keysA},G={'%d,%d,%d'%k:rng.choice(Gopts[k]) for k in keysG},F=rng.randrange(3))
    try: nadd,src,exc,nout=build(cfg)
    except AssertionError: continue
    seen+=1
    best.append((max(src.values() and src.keys()),nadd,exc,json.dumps(cfg,sort_keys=True)))
best.sort()
print('valid configs sampled',seen)
for b in best[:8]: print(b[:3],b[3][:200])
dist=Counter((b[0],b[1]) for b in best); print('max source fan-out x additions distribution (top):',dist.most_common(12))
