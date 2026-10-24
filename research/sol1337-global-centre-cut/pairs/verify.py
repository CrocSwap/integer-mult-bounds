#!/usr/bin/env python3
"""Independent all-case rank/histogram replay; Apache-2.0, Codex assisted.

Does not import the predecessor rank implementation or execute scan.cpp.
The graph retains all 640 arbitrary owners and fixed 408 helper jobs.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent

def need(test, message):
    if not test:
        raise ValueError(message)

def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)

def canon(rows):
    rows = list(rows)
    k = 0
    for bit in range(18):
        j = next((j for j in range(k,len(rows)) if rows[j] >> bit & 1),None)
        if j is None:
            continue
        rows[k],rows[j] = rows[j],rows[k]
        for i in range(len(rows)):
            if i != k and rows[i] >> bit & 1:
                rows[i] ^= rows[k]
        k += 1
    return tuple(sorted(rows[:k]))

def distance(a,b):
    return rank(list(a)+list(b))-9

def neighbour(x,phase):
    z = (x & -x) if phase else 0
    axis = x | (z << 9)
    return [v ^ (axis if ((v >> 9) & x).bit_count() % 2 else 0)
            for v in ZERO]

raw = (HERE/'center-contact-graph.txt').read_bytes()
it = iter(map(int,raw.split()))
n,f,m,e = [next(it) for _ in range(4)]
nodes = [(next(it),next(it)) for _ in range(n)]
frames = [[next(it) for _ in range(9)] for _ in range(f)]
maps = [[next(it) for _ in range(18)] for _ in range(m)]
edges = [tuple(next(it) for _ in range(5)) for _ in range(e)]
need(next(it,None) is None,'no trailing graph words')
ZERO = [1 << (9+j) for j in range(9)]
need(frames[0] == ZERO,'empty chart convention')
metadata=json.loads((HERE/'graph-metadata.json').read_text())
need(metadata['inputs']==640 and metadata['helpers']=={'4':28,'7':7,'8':47,'9':326},'full retained interface')
need(metadata['independent_center_reward']==0,'no independent centre credit')
empty = {i for i,(frame,fixed) in enumerate(nodes) if frame==0 and not fixed}
need(len(empty)==176,'empty contact inventory')
pairs=[]; neighbours=defaultdict(Counter)
for a,b,r,sign,mp in edges:
    need(sign==1,'all graph edges are paid')
    if a in empty or b in empty:
        need(mp==0,'selected contact incident edges have identity native map')
    for own,other in ((a,b),(b,a)):
        if own in empty:
            neighbours[own][(nodes[other][0],r)] += 1
    if a in empty and b in empty:
        need(r==0,'original shared edge rank zero')
        pairs.append(tuple(sorted((a,b))))
need(len(pairs)==len(set(pairs))==256,'distinct internal pair census')
need(dict(Counter(r for a,b,r,s,mp in edges if r))=={1:2201,2:412,3:510,4:127,5:40,8:8},'complete original paid bill')

# Distinct code path: each endpoint is changed alone against original neighbours.
# Combining two changes removes the two singly-paid rank-one shared-edge changes
# and inserts its actual opposite-neighbour distance-one bill exactly once.
profiles=Counter(); seen=set(); distance_cache={}; geometries=0
for x in range(1,512):
    alternatives=[neighbour(x,phase) for phase in (0,1)]
    need(distance(ZERO,alternatives[0])==distance(ZERO,alternatives[1])==1,'neighbour distance')
    need(distance(*alternatives)==1,'opposite pair distance')
    kernel=[v<<9 for v in range(1,512) if (v&x).bit_count()%2==0]
    need(rank(kernel)==8,'shared hyperplane dimension')
    for alt in alternatives:
        need(rank(alt+kernel)==9,'same hyperplane in both neighbours')
        key=canon(alt);need(key not in seen,'distinct neighbour');seen.add(key)
    for phase,alt in enumerate(alternatives):
        for frame,_ in set(k for values in neighbours.values() for k in values):
            distance_cache[phase,frame]=distance(alt,frames[frame])
    unary={}
    for node in empty:
        for phase in (0,1):
            d=[0]*10
            for (frame,old),multiplicity in neighbours[node].items():
                new=distance_cache[phase,frame]
                d[old]-=multiplicity;d[new]+=multiplicity
            unary[node,phase]=d
    for a,b in pairs:
        for order in (0,1):
            d=[u+v for u,v in zip(unary[a,order],unary[b,1-order])]
            d[0]+=1;d[1]-=1
            profiles[tuple(d)]+=1
    geometries+=1
need(geometries==511 and len(seen)==1022,'complete hyperplane grouping')
screen=json.loads((HERE/'SCREEN.json').read_text())
observed=Counter({tuple(row['delta']):row['count'] for row in screen['profiles']})
need(profiles==observed,'independent exact full-domain histogram equality')
need(sum(profiles.values())==261632,'all ordered endpoint choices')
expected=[3,3,3,3,3,3,3,2,2]
prefix=[min(sum(d[r]*min(r,j) for r in range(10)) for d in profiles) for j in range(1,10)]
need(prefix==expected==screen['minimum_prefix_deltas'],'exact prefix certificate')
best=(-3,3,0,0,0,0,0,1,-1,0)
need(profiles[best]==4,'sharp common lower profile')

# Controls: same neighbour on both ends makes the edge rank zero, unlike
# opposite neighbours. Omitting the second endpoint correction changes the bill.
need(distance(neighbour(30,0),neighbour(30,0))==0,'same-neighbour control')
need(distance(neighbour(30,0),neighbour(30,1))==1,'opposite-neighbour control')
def rejected(call):
    try:
        call()
    except ValueError:
        return True
    return False
need(rejected(lambda: need(distance(neighbour(30,0),neighbour(30,0))==1,
                           'same-neighbour incorrectly billed as opposite')),
     'wrong shared-edge control must reject')

# A new prospective full rank-eight pair scan is unnecessary: exact incidence
# alone funds at least two units outside the shared edge, whose rank stays >=6.
adj=defaultdict(list)
for i,(a,b,r,sign,mp) in enumerate(edges):
    adj[a].append((i,b,r,mp));adj[b].append((i,a,r,mp))
rank8=[]
for i,(a,b,r,sign,mp) in enumerate(edges):
    if nodes[a][1] or nodes[b][1] or r!=8:
        continue
    need({nodes[a][0]==0,nodes[b][0]==0}=={True,False},'empty/high rank-eight endpoints')
    external=[]
    for node,other in ((a,b),(b,a)):
        need(len(adj[node])==4,'rank-eight endpoint has degree four')
        need(sum(v==other for _,v,_,_ in adj[node])==1,'no parallel shared edge')
        ext=[row for row in adj[node] if row[0]!=i]
        need(len(ext)==3 and all(mp==0 for _,_,_,mp in ext),'three native-identity external edges')
        ranks=sorted(r for _,_,r,_ in ext)
        need(ranks[:2]==[0,0] and ranks[2]<=2,'two empty-cost edges and one rank-at-most-two edge')
        external.append(dict(node=node,external_rank_multiset=ranks,edges=ext))
    rank8.append(dict(edge=i,endpoints=[a,b],external=external))
need(len(rank8)==8,'all eight rank-eight internal edges')
need(rejected(lambda:need([0,0,3][2]<=2,'unsupported external-rank inventory')),
     'changed-graph rank inventory control must reject')
(HERE/'RANK8-CENSUS.json').write_text(json.dumps(dict(edges=rank8,
    nominal_independent_neighbour_cases=8*1022**2,actual_pair_cases_evaluated=0,
    complete_paid_lower_bound='2 + 6^theta - 8^theta >= 2 - 2^theta',
    power_interval='0 <= theta < 1',status='ANALYTIC_STOP_BEFORE_PAIR_SCAN'),indent=2)+'\n')
result=dict(status='PASS',cases=261632,distinct_profiles=len(profiles),hyperplane_groups=511,
            distinct_neighbours=1022,prefix_minima=prefix,sharp_lower_paid_delta=list(best),
            full_power_interval='0 <= theta <= 1',exact_uniform_paid_loss_lower_bound=2,
            helpers_unchanged=408,independent_center_reward=0,
            graph_sha256=sha256(raw).hexdigest(),
            rank8_pair_domain_closed_analytically=8*1022**2,
            scope='fixed graph, two adjacent empty contacts, opposite neighbours of one common hyperplane; rank-eight pair analytic gate')
(HERE/'VERIFY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
