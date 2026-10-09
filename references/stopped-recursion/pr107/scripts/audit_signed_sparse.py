#!/usr/bin/env python3
"""Exact signed-vector factor controls and generative complete raw ledgers."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from certify import require,verify_sources
from experiments.signed_sparse_core import specification,expand_factor,ledger,budget,redundant_factor_control
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[]
    for h,q in ((2,2),(3,2),(4,2),(4,4),(5,4),(6,4)):
        data=expand_factor(h,q)
        controls.append(dict(h=h,q=q,specification=data['specification'],
            labels=data['labels'],U=data['U'],V=data['V'],C=data['C'],
            exact_binary_rank=len(data['reduced_V']),full_core_expanded=True))
    scan=[]
    for q in (2,4,8,16,32):
        for h in range(q,53):
            spec=specification(h,q);row=dict(specification=spec)
            if spec['positive_numerator']:row['target_budget']=budget(h,q)
            scan.append(row)
    best=max((row for row in scan if 'target_budget' in row),
             key=lambda row:row['target_budget']['sufficient_ratio'])
    require((best['specification']['h'],best['specification']['q'])==(31,16),
            'Finite scan maximizer changed')
    s=best['specification'];raw=ledger(31,16)
    require(raw['positive'] and raw['saving_upper']<Q(296,10**11),
            'Raw construction comparison failed')
    require(best['target_budget']['sufficient_ratio']>Q(5555,1000),
            'Target budget lost its advertised margin')
    sources=('scripts/audit_signed_sparse.py','scripts/experiments/signed_sparse_core.py',
             'scripts/experiments/shared_core.py','scripts/experiments/rank_product_core.py',
             'scripts/experiments/cube_core_family.py','docs/research/signed-sparse-core.md')
    return dict(status='POSITIVE GENERATIVE BIT CORE; NO COMPETITIVE SIDE CIRCUIT; NO NEW KAPPA',
        upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),target_kappa=Q(1,2**25),
        controls=controls,redundant_factor_control=redundant_factor_control(),
        finite_scan=scan,best_budget_candidate=best,
        raw_network=raw,storage_floor_benchmark=ledger(31,16,s['n']-s['central_factor_size']),
        complex_companion_supplied=False,large_central_rank_claim='constructive upper bound only',
        source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/signed-sparse-core.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS signed-sparse central factors and raw shared compiler ledger; no new kappa.')
    print('Best scanned sufficient side ratio:',float(result['best_budget_candidate']['target_budget']['sufficient_ratio']))
