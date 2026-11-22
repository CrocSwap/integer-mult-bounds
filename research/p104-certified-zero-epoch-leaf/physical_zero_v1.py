#!/usr/bin/env python3
"""Run genuine #8035 physical 36-call source on a finite v=1 stand-in.

Power 1 is a feasible diagnostic, NOT the installed v=268. Real native
projector matrices, ADD/SWAP/INIT/CLEAR, fresh ownership and synchronization
are used. Seed several nonconstant sparse ternary address fields in retained
root jobs. Verify every selected single-source cut is physically empty, skip
its paid call, and run twice; compare the first pass with an independent
coordinate-exchange oracle and the second with the exact initial fields.
"""
import json,sys
from pathlib import Path
from dataclasses import replace
from random import Random
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from upstream import install
install()
from strong_binary import graph,caller,StrongBinarySource
from tagged_sources import binary_ports
from periodic import Job
from check_raw_delta import Sparse

selected=json.loads((HERE/'zero_raw_labels.json').read_text())
safe={tuple(r[0]) for r in selected}
assert len(safe)==13824
raw=binary_ports(graph(),caller())
word=replace(raw,power=1,floor=15,low_cut=12,high_cut=12)
assert word.paid[0].tag==('move',4,2,630) and word.paid[0].rank==1
n=134;modulus=3
ident=tuple(bytes(int(i==j) for i in range(n)) for j in range(n))
banks=Sparse(ident,modulus)
source=StrongBinarySource(banks)
seeds={('root',0,0),('root',1,0),('root',19,5)}
rng=Random(5329)
prod=[];expected={};initial={}
for port,keep in word.target_paths():
    if not keep:continue
    owner=banks.zero(); job=Job(owner,tuple(range(port.rank)))
    prod.append(job)
    if port.tag[0] in seeds:
        h=bytes(rng.randrange(modulus) for _ in range(n))
        t=bytes(rng.randrange(modulus) for _ in range(n))
        label=port.tag[0]
        banks.values[owner].add((label,ident,h,t)); initial[owner]=banks.values[owner].copy()
        eh=bytes(t[i] if i<port.rank else h[i] for i in range(n))
        et=bytes(h[i] if i<port.rank else t[i] for i in range(n))
        expected[owner]={(label,ident,eh,et)}
assert len(initial)==3 and len(prod)==3774
logs=[]
for cycle in range(2):
    skipped=paid=0
    for block,job in zip(word.paid_paths(),word.native(prod,1,source),strict=True):
        (tag,)=block.tags
        if tag in safe:
            assert block.rank in (1,2,4) and block.first==0
            assert not banks.values[job.owner],('selected cut not zero',tag)
            skipped+=1
        else:
            banks.pay(job)
        paid+=1
    assert skipped==13824
    expected_now=expected if cycle==0 else initial
    bad=[job.owner for job in prod if banks.values[job.owner]!=expected_now.get(job.owner,set())]
    assert not bad,bad[:10]
    assert len(banks.values)==len(prod)
    logs.append({'cycle':cycle+1,'actual_emitted_blocks':paid,'zero_cut_blocks_skipped':skipped,
                 'active_paid_so_far':banks.active_paid,'nonempty_routes_so_far':banks.active_routes,
                 'independent_coordinate_oracle':True if cycle==0 else None,
                 'exact_inverse_return':True if cycle==1 else None})
    print('finished cycle',cycle+1,flush=True,file=sys.stderr)
print(json.dumps({'modulus':modulus,'columns':1,'power':1,'floor':15,
                  'seeds':[list(s) for s in sorted(seeds)],'physical_passes':logs,
                  'scope':'finite actual native projector data and ownership; general 268-factor proof separate'},indent=2))
print('PASS_PHYSICAL_V1_ZERO_SKIP_AND_INVOLUTION')
