#!/usr/bin/env python3
"""Heterogeneous cross-shear rank accounting: finite GL(4,F2) evidence.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
The field-independent proof is in PROOF.md; this checks one finite instance.
"""
import argparse
from collections import Counter
import hashlib
import heapq
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE='2921874911956718fcaaaf9396fe8267b3cfa9f0'
SOURCES={
 'research/experiment-log/campaign-100/architectures-and-stages.md',
 'research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp',
 'research/community-frontier942-audit/ASSEMBLY.json',
 'docs/research/community-batch952-review.md'}
IDENTITY=(1,2,4,8)


def need(ok,message):
    if not ok: raise ValueError(message)


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def rank(rows):
    basis={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p in basis: row^=basis[p]
            else:
                basis[p]=row
                break
    return len(basis)


GENERATORS=[(direction,k,rank((k&3,k>>2))) for direction in (0,1) for k in range(1,16)]


def step(state,generator):
    direction,k,_=generator
    row=list(state)
    d,s=(0,2) if direction==0 else (2,0)
    row[d]^=(state[s] if k&1 else 0)^(state[s+1] if k&2 else 0)
    row[d+1]^=(state[s] if k&4 else 0)^(state[s+1] if k&8 else 0)
    return tuple(row)


def potential(state):
    return rank((state[0]&3,state[1]&3))+rank((state[2]>>2,state[3]>>2))


def exchange(state):
    return state[0]&3==state[1]&3==state[2]>>2==state[3]>>2==0


def pins():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    need(manifest['base_commit']==BASE and set(manifest['files'])==SOURCES,'source inventory/base')
    for name,digest in manifest['files'].items():
        content=(ROOT/name).read_bytes().replace(b'\r\n',b'\n')
        need(hashlib.sha256(content).hexdigest()==digest,'source pin: '+name)
    selected=(HERE/'BASE-SELECTED.json').read_bytes().replace(b'\r\n',b'\n')
    need(hashlib.sha256(selected).hexdigest()==manifest['base_selected_sha256'],'selected snapshot hash')
    data=json.loads(selected)
    need(data['kappa']=='1661960547713947/1000000000000000000','selected context kappa')
    need(data['audited_source_head']=='1960cfa919a0945d0ca4cb14ea96237000037903','selected source context')


def witness(parent,target):
    gates=[]
    while target!=IDENTITY:
        target,g=parent[target]
        gates.append(list(GENERATORS[g]))
    return list(reversed(gates))


def run():
    pins()
    # All 16^4 binary matrices are explicitly filtered, not sampled.
    states=[]
    for code in range(1<<16):
        rows=tuple((code>>(4*i))&15 for i in range(4))
        if rank(rows)==4: states.append(rows)
    need(len(states)==20160,'GL4 group cardinality')
    universe=set(states)
    goals=[s for s in states if exchange(s)]
    need(len(goals)==36,'invertible off-diagonal endpoints')
    edges=hashlib.sha256()
    transitions={}
    first_checks=0
    for state in states:
        phi=potential(state)
        next_states=[]
        for g in GENERATORS:
            nxt=step(state,g)
            need(nxt in universe,'cross shear left GL4')
            need(abs(potential(nxt)-phi)<=g[2],'rank potential step')
            next_states.append(nxt)
            edges.update(encoded([state,g,nxt])+b'\n')
            if state==IDENTITY:
                need(potential(nxt)==4,'first call changes diagonal potential')
                first_checks+=1
        transitions[state]=next_states
    # Full positive-weight Dijkstra proves the finite minimum over arbitrary
    # numbers of calls; no depth cutoff or omitted state is used here.
    distances={IDENTITY:0}
    parent={}
    queue=[(0,IDENTITY)]
    while queue:
        distance,state=heapq.heappop(queue)
        if distance!=distances[state]:continue
        for gi,nxt in enumerate(transitions[state]):
            candidate=distance+GENERATORS[gi][2]
            if candidate<distances.get(nxt,1<<30):
                distances[nxt]=candidate
                parent[nxt]=(state,gi)
                heapq.heappush(queue,(candidate,nxt))
    need(len(distances)==20160,'incomplete weighted reachability')
    # Verify the shortest-path labels against every edge, separately from the
    # priority-queue relaxation. Retained parents provide achievable witnesses.
    for state in states:
        for gi,nxt in enumerate(transitions[state]):
            need(distances[nxt]<=distances[state]+GENERATORS[gi][2],'distance Bellman inequality')
        if state!=IDENTITY:
            before,gi=parent[state]
            need(distances[state]==distances[before]+GENERATORS[gi][2],'distance predecessor equality')
    best=min(goals,key=lambda s:(distances[s],s))
    need(distances[best]==5,'minimum rank volume')
    layers=[]
    layer={IDENTITY:0}
    for calls in range(6):
        costs=[layer[s] for s in goals if s in layer]
        layers.append({'calls':calls,'reachable_states':len(layer),
                       'minimum_exchange_rank':min(costs) if costs else None})
        if calls==5:break
        nxt_layer={}
        for state,cost in layer.items():
            for gi,nxt in enumerate(transitions[state]):
                candidate=cost+GENERATORS[gi][2]
                if candidate<nxt_layer.get(nxt,1<<30):nxt_layer[nxt]=candidate
        layer=nxt_layer
    need([x['minimum_exchange_rank'] for x in layers]==[None,None,None,6,6,5],'call/rank frontier')
    return {'schema':'stage-rank-rigidity/1','base_commit':BASE,'assignment_seed':41,
        'field':'F2','bank_dimension':2,'group_states':len(states),'cross_shears':len(GENERATORS),
        'generator_rank_counts':dict(sorted(Counter(str(g[2]) for g in GENERATORS).items())),
        'transition_checks':len(states)*len(GENERATORS),'transition_sha256':edges.hexdigest(),
        'first_call_checks':first_checks,'off_diagonal_endpoints':len(goals),
        'distance_histogram':dict(sorted(Counter(str(x) for x in distances.values()).items())),
        'distance_labels_sha256':hashlib.sha256(encoded([[s,distances[s]] for s in states])).hexdigest(),
        'minimum_rank_volume':distances[best],'best_endpoint':list(best),'minimum_rank_witness':witness(parent,best),
        'exact_call_layers':layers,'global_call_rank_pareto':[[3,6],[5,5]],
        'scope':'Finite GL4 evidence only; field-independent argument is written separately.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write',type=Path)
    args=p.parse_args()
    receipt=run()
    if args.write:
        with args.write.open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
    else:need(encoded(receipt)==encoded(json.loads((HERE/'EXPECTED.json').read_text())),'receipt mismatch')
    print('PASS_STAGE_RANK_RIGIDITY states=20160 edges=604800 rank_min=5 pareto=3:6,5:5 no_new_kappa')


if __name__=='__main__':main()
