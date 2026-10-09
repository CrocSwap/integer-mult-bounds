#!/usr/bin/env python3
"""Constructive cube-core rank bounds and exact code-subfamily rejections."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from certify import require,verify_sources
from experiments.cube_core_family import cube_spec,cube_ledger,cube_target_budget,expand_factor,quadratic_rank_screen
from experiments.rank_product_core import binary_factor
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[]
    for q in (2,4):
        data=expand_factor(q);_,V=binary_factor(data['C'],data['specification']['n'])
        require(len(V)==data['specification']['central_factor_size'],'Small bound not sharp')
        controls.append(dict(q=q,specification=data['specification'],U=data['U'],V=data['V'],
                             exact_binary_rank=len(V),full_core_factor_expanded=True,
                             full_network_expanded=False))
    rows=[]
    for q in (2,4,8,16,32):
        spec=cube_spec(q);row=dict(specification=spec,raw=cube_ledger(q),
                                 free_side_benchmark=cube_ledger(q,0))
        if spec['positive_numerator']:
            row['working_target_budget']=cube_target_budget(q,Q(16,10**8))
            row['necessary_target_budget']=cube_target_budget(q,Q(5,2**25))
        rows.append(row)
    require(rows[3]['free_side_benchmark']['saving_lower']>Q(16,10**8),
            '32-dimensional benchmark lacks target headroom')
    require(rows[3]['raw']['saving_upper']<Q(296,10**11),'Raw cube unexpectedly beats retained saving')
    screens=[quadratic_rank_screen(t) for t in (3,4,5)]
    require(all(s['specified_core_positive_deficit_excluded'] for s in screens),'Quadratic-code screen did not close')
    sources=('scripts/audit_cube_cores.py','scripts/experiments/cube_core_family.py',
             'scripts/experiments/rank_product_core.py','docs/research/cube-core-family.md')
    return dict(status='NEW GENERATIVE CUBE CORE; NO COMPETITIVE SIDE CIRCUIT; NO NEW KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),target_kappa=Q(1,2**25),
                expanded_core_controls=controls,family_ledger=rows,
                quadratic_code_screens=screens,
                opposite_field_complex_construction_supplied=False,
                scope='The large bit central factor is proved generatively; the raw ledger uses all-role completion. Free-side values are benchmarks only. Code screens reject only their specified full-support binary matrices.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/cube-core-family.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    row=result['family_ledger'][3]
    print('PASS cube factors and exact quadratic-code rank screens; no new kappa.')
    print('q=16 target side roles per label:',float(row['working_target_budget']['sufficient_side_ratio']))
