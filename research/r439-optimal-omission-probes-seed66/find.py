"""Bounded discovery only; the verifier does not rely on this heuristic."""
from pathlib import Path
import gzip,json,random
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
w=json.loads(gzip.decompress((ROOT/'research/r439-helper-stars-seed19/candidate.json.gz').read_bytes()))
g=[(d,s) for _,d,ss in w['D'] for s in ss]
rows=[1<<i for i in range(661)]; masks=[]
for d,s in g:masks.append(rows[s]);rows[d]^=rows[s]
vs=list(dict.fromkeys(masks)); supports=[[i for i in range(661) if v>>i&1] for v in vs]
touch=[[] for _ in range(661)]
for k,ss in enumerate(supports):
    for i in ss:touch[i].append(k)
rng=random.Random(66)
labels=[rng.randrange(4) for _ in range(661)]
vals=[0]*len(vs)
for k,ss in enumerate(supports):
    for i in ss:vals[k]^=labels[i]
weights=[1]*len(vs)
for step in range(10000):
    bad=[k for k,v in enumerate(vals) if not v]
    if not bad:break
    k=rng.choice(bad);best=[];score=None
    for i in supports[k]:
        costs=[0]*4
        for j in touch[i]:costs[vals[j]]+=weights[j]
        for delta in (1,2,3):
            c=costs[delta]-costs[0]
            if score is None or c<score:score=c;best=[(i,delta)]
            elif c==score:best.append((i,delta))
    if score>=0:
        for j in bad:weights[j]+=1
    i,delta=rng.choice(best);labels[i]^=delta
    for j in touch[i]:vals[j]^=delta
else:raise SystemExit('bounded pilot failed')
# A one-probe solution would require v.x=1 for every activation row.
# Track an odd dependency by ordinary augmented Gaussian elimination.
basis={}; relation=None
for k,mask in enumerate(vs):
    row=mask;rhs=1;trace=1<<k
    while row:
        p=row.bit_length()-1
        if p not in basis:basis[p]=(row,rhs,trace);break
        a,b,c=basis[p];row^=a;rhs^=b;trace^=c
    if not row and rhs:relation=[i for i in range(len(vs)) if trace>>i&1];break
assert relation is not None
result={'repair_steps':step,'seed':66,'cap':10000,'probes':[str(sum((1<<i) for i,x in enumerate(labels) if x>>bit&1)) for bit in range(2)],'odd_dependency_unique_indices':relation,'odd_dependency_gate_indices':[masks.index(vs[i]) for i in relation]}
(Path(__file__).parent/'WITNESS.json').write_text(json.dumps(result,indent=2)+'\n')
print('FOUND',step,'steps; odd relation',len(relation),'gates',result['odd_dependency_gate_indices'])
