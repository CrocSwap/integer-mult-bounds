#!/usr/bin/env python3
"""Fixed-period discovery replay. Prepared for @CubeJerry with OpenAI assistance.
Apache-2.0. Search assertions are diagnostic; verify.py separately certifies
all proof-relevant predicates in normal and optimization modes. This search
stops at the first greedy matching for seeds 0..99, not at exhaustive coverage
of matchings or lattices. Integer set order can select a different valid
matching on a different Python implementation; validate any new output.
"""
from itertools import product
from collections import Counter, deque
from pathlib import Path
import json, random, time

import argparse
import kernel as model

parser=argparse.ArgumentParser(description="Bounded fixed-period correction search; verifier remains authoritative.")
parser.add_argument('--output',type=Path,required=True,help='new or disposable candidate certificate path')
args=parser.parse_args()
basis=model.BASIS
ROWS=model.ROWS
HI=[s for s in range(16) if s.bit_count()>=2]
SIGN=[(-1)**s.bit_count() for s in range(16)]
RE=[(1,0,-1,0)[s.bit_count()%4] for s in range(16)]
IM=[(0,-1,0,1)[s.bit_count()%4] for s in range(16)]
W=[[(-1)**((r&s).bit_count()) for s in range(16)] for r in range(16)]

def walsh(v):return tuple(sum(a*b for a,b in zip(row,v)) for row in W)
def b(v):
    q=walsh(v)
    assert all(x%4==0 for x in q)
    return tuple(s*x//4 for s,x in zip(SIGN,q))
def k(v):return tuple(SIGN[s]*v[s^15] for s in range(16))
def neg(v):return tuple(-x for x in v)
def coords(v):
    total=sum(v);bits=[sum(v[s] for s in range(16) if s>>j&1) for j in range(4)]
    assert total%4==0 and all(x%2==0 for x in bits)
    return [total//4]+[x//2 for x in bits]+[v[s] for s in HI]
def g(v):
    mask=sum((x&1)<<i for i,x in enumerate(v))
    return sum(((r&mask).bit_count()%2)<<i for i,r in enumerate(ROWS))
def base_rep(q):
    a=q&3;bm=q>>2
    z=[0]*16;z[0]=a-bm.bit_count()
    for j in range(4):z[1<<j]=(bm>>j)&1
    return tuple(z)
BASE=[base_rep(q) for q in range(64)]
def key(z):
    q=(sum(z)%4)+4*sum((sum(z[s] for s in range(16) if s>>j&1)%2)<<j for j in range(4))
    r=BASE[q]
    return 64*q+g(coords([a-c for a,c in zip(z,r)]))

# A six-pivot section of the exact L/period quotient.
sections={0:0}
for j in range(16):
    col=sum(((r>>j)&1)<<i for i,r in enumerate(ROWS))
    if col not in sections:
        sections.update({q^col:mask^(1<<j) for q,mask in list(sections.items())})
assert len(sections)==64
LREP=[tuple(sum(basis[j][i] for j in range(16) if sections[q]>>j&1) for i in range(16)) for q in range(64)]
REPS=[tuple(a+b for a,b in zip(BASE[q],LREP[v])) for q in range(64) for v in range(64)]
assert all(key(z)==i for i,z in enumerate(REPS))
BK=[g(coords(b(v))) for v in LREP]
NK=[key(neg(z)) for z in REPS]
KK=[key(k(z)) for z in REPS]
assert all(KK[KK[i]]==i and NK[NK[i]]==i and KK[NK[i]]==NK[KK[i]] for i in range(4096))

orbits=[];oi={}
for i in range(4096):
    if i in oi:continue
    orb=sorted({i,NK[i],KK[i],NK[KK[i]]})
    for v in orb:oi[v]=len(orbits)
    orbits.append(orb)
print('orbits',len(orbits),dict(Counter(map(len,orbits))),flush=True)

def corrections(q,bound=3):
    residue=[x%4 for x in walsh(BASE[q])]
    groups=[]
    for weights in [RE,IM]:
        positions=[i for i,w in enumerate(weights) if w]
        candidates=[]
        options=[[e for e in range(-bound,bound+1) if (e+residue[i])%4==0] for i in positions]
        for vals in product(*options):
            energy=sum(x*x for x in vals)
            if energy<=64 and sum(weights[i]*v for i,v in zip(positions,vals))==0:
                candidates.append((positions,vals,energy))
        groups.append(candidates)
    result=[]
    for ps,vs,en in groups[0]:
        for pt,vt,em in groups[1]:
            if en+em>64:continue
            e=[0]*16
            for i,v in zip(ps,vs):e[i]=v
            for i,v in zip(pt,vt):e[i]=v
            c=tuple(s*v for s,v in zip(SIGN,e))
            ct=neg(b(c))
            y=tuple((s*a+d)//4 for s,a,d in zip(SIGN,walsh(BASE[q]),c))
            assert all((s*a+d)%4==0 for s,a,d in zip(SIGN,walsh(BASE[q]),c))
            result.append((c,ct,key(y)))
    return result

def orbit_values(s,c):return ((s,c),(NK[s],neg(c)),(KK[s],k(c)),(NK[KK[s]],neg(k(c))))
def compatible(s,t,c,ct):
    vals={}
    for u,v in orbit_values(s,c)+orbit_values(t,ct):
        if u in vals and vals[u]!=v:return False
        vals[u]=v
    return True

start=time.monotonic()
CANDS=[corrections(q) for q in range(64)]
print('candidates',dict(Counter(map(len,CANDS))), 'elapsed',time.monotonic()-start,flush=True)
adj=[set() for _ in orbits];edges={}
for a,orb in enumerate(orbits):
    s=orb[0];q=s//64;v=s%64
    for j,(c,ct,tb) in enumerate(CANDS[q]):
        t=tb^BK[v];bb=oi[t]
        if bb in adj[a] or len(orbits[bb])!=len(orb):continue
        if compatible(s,t,c,ct):
            adj[a].add(bb);adj[bb].add(a);edges[tuple(sorted((a,bb)))]=(s,j,t)
    if a%100==0:print('graph',a,len(edges),time.monotonic()-start,flush=True)
print('graph_done',len(edges),'degrees',dict(Counter(map(len,adj))),flush=True)
zeros=[orbits[i] for i,a in enumerate(adj) if not a]
print('zeros',len(zeros),zeros[:10],flush=True)


forced_source=64
forced_target=849
forced_c=tuple(4*int(i==3)-SIGN[i] for i in range(16))
forced_j=next(j for j,(c,ct,tb) in enumerate(CANDS[forced_source//64]) if c==forced_c)
model.require((CANDS[1][forced_j][2]^BK[0])==forced_target,'wrong forced target')
forced_a,forced_b=oi[forced_source],oi[forced_target]
model.require(compatible(forced_source,forced_target,forced_c,neg(b(forced_c))),
              'incompatible forced edge')
edges[tuple(sorted((forced_a,forced_b)))]=(forced_source,forced_j,forced_target)
adj[forced_a].add(forced_b);adj[forced_b].add(forced_a)
print('FORCED_EDGE',forced_a,forced_b,'source',forced_source,'target',forced_target,flush=True)

def greedy_match(seed):
    rng=random.Random(seed);match={forced_a:forced_b,forced_b:forced_a}
    pool=set(range(len(orbits)))-{forced_a,forced_b}
    while pool:
        a=min(pool,key=lambda a:(len(adj[a]&pool),rng.random()))
        opts=adj[a]&pool
        if not opts:return match,pool
        b=min(opts,key=lambda b:(len(adj[b]&pool),rng.random()))
        match[a]=b;match[b]=a;pool.discard(a);pool.discard(b)
    return match,pool

for seed in range(100):
    matching,unmatched=greedy_match(seed)
    print('matching',seed,len(unmatched),flush=True)
    if not unmatched:
        output={}
        for a,bb in matching.items():
            if a>bb:continue
            s,j,t=edges[tuple(sorted((a,bb)))];c,ct,_=CANDS[s//64][j]
            for u,cu in orbit_values(s,c)+orbit_values(t,ct):
                if u in output:assert output[u]==cu
                output[u]=cu
        assert len(output)==4096
        seen=set();cycles=[]
        for s,z0 in enumerate(REPS):
            if s in seen:continue
            c0=output[s];cycles.append([s,list(c0)]);z=z0;c=c0
            for _ in range(4):
                for u,cu in ((key(z),c),(key(neg(z)),neg(c))):
                    model.require(output[u]==cu,'cycle does not match table');seen.add(u)
                z=model.quarter(tuple(a*w+v for a,w,v in zip(SIGN,walsh(z),c)))
                c=neg(b(c))
        certificate={'schema_version':1,'period_rows':list(ROWS),'cycles':cycles}
        model.require(model.expand_certificate(certificate)==tuple(output[i] for i in range(4096)),
                      'compressed certificate mismatch')
        body='{"schema_version":1,"period_rows":'+json.dumps(list(ROWS),separators=(',',':'))+',"cycles":[\n'
        body+=',\n'.join(json.dumps(row,separators=(',',':')) for row in cycles)+'\n]}\n'
        args.output.write_text(body,encoding='utf-8')
        print('FOUND_CERTIFICATE',len(cycles),'cycle generators; successful seed',seed,flush=True);break
    if zeros:break
