#!/usr/bin/env python3
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import json

from certify import require,verify_sources
from prepare_layers import serializable
from experiments.rank_product_core import check_core,check_projector_core,_compile
from experiments.shared_core import compile_shared,shared_counts,target_budget
from experiments.subset_core_family import specification
from experiments.cube_core_family import cube_spec
from finite_bit_contract import inspect_candidate

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[]
    cases=[('symmetric',check_core([3,3],[[1,0],[0,1]],[[1,0],[0,1]]),[1,0]),
           ('oblique',check_projector_core([3,2],[[[1,1],[0,0]],[[0,-1],[0,1]]]),[1,0]),
           ('nonautomorphic_cycle',check_core([3,6,4],[[1,0,0],[0,1,0],[0,0,1]],
             [[1,0,0],[0,1,0],[0,0,1]]),[1,2,0])]
    for name,core,pi in cases:
        old,_=_compile(core,1000);before=inspect_candidate(old,require_deficit=False)
        new,ledger=compile_shared(core,pi);after=inspect_candidate(new,require_deficit=False)
        require(after['s']==ledger['s'] and before['deficit']==after['deficit'],'Wrong sharing rank')
        controls.append(dict(name=name,permutation=pi,ledger=ledger,unshared=before,shared=after))
    s=specification(28,4);c=cube_spec(16)
    rows=[]
    for name,n,r,d,degree in [('seven_subset_h28',s['n'],s['central_factor_size'],28,s['degree']),
                             ('cube_q16',c['n'],c['central_factor_size'],c['d'],c['degree'])]:
        rows.append(dict(name=name,raw=shared_counts(n,r,d,n*degree),
            hypothetical_free_side=shared_counts(n,r,d,0),
            hypothetical_target_budget=target_budget(n,r,d,Q(16,10**8)),
            matching_expanded=False,competitive_side_circuit_supplied=False))
    sources=('scripts/audit_shared_core.py','scripts/experiments/shared_core.py',
             'scripts/experiments/rank_product_core.py','docs/research/shared-core.md')
    return dict(status='GENERAL AUXILIARY REUSE; NO NEW MULTIPLICATION BOUND',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                expanded_controls=controls,generative_family_ledgers=rows,
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/shared-core.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS shared two-field compiler; exact all-role controls and hypothetical side budgets.')
