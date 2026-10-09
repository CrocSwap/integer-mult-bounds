#!/usr/bin/env python3
"""Complete positive-definite side compiler and bounded sharing experiments."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from audit_joint_frames import eye
from certify import require,verify_sources
from experiments.positive_side_core import PositiveSide,compile_positive_side
from experiments.signed_sparse_core import vectors
from finite_bit_contract import inspect_candidate
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[]
    cases=[([3,3],eye(2),[1,0]),([7,7,7],eye(3),[1,2,0]),
           ([3,6,5],eye(3),[1,2,0]),
           ([13,14,7,11],[[1,0],[1,0],[0,1],[0,1]],[2,3,0,1])]
    for rows,labels,matching in cases:
        c=PositiveSide(rows,labels,'frequent-pairs')
        local=dict(side=c.verify(),frames=c.verify_frames(),scalar=c.verify_invocation())
        nets=[]
        for pi in (None,matching):
            candidate,expected=compile_positive_side(c,pi)
            actual=inspect_candidate(candidate,require_deficit=False)
            require(actual['s']==expected['s'] and actual['deficit']==expected['deficit'],
                    'Complete compressed-side ledger failed')
            nets.append(dict(shared=pi is not None,actual=actual,expected=expected))
        controls.append(dict(local=local,full_networks=nets))
    experiments=[]
    for h,q in ((4,2),(5,2),(4,4),(5,4),(6,4),(8,8)):
        labels=list(vectors(h,q));n=len(labels)
        rows=[sum(1<<j for j,y in enumerate(labels)
                  if i==j or sum(a*b for a,b in zip(x,y))==0)
              for i,x in enumerate(labels)]
        scores=[]
        for strategy in ('balanced','frequent-pairs'):
            c=PositiveSide(rows,labels,strategy)
            record=c.verify()
            record.update(scalar=c.verify_invocation(),r=c.core['r'],
                          density=Q(n,c.core['r']*h))
            if strategy=='frequent-pairs':record['physical_frames']=c.verify_frames()
            record['dag_sha256']=sha256(json.dumps(dict(args=c.args,outputs=c.outputs),
                                        sort_keys=True,separators=(',',':')).encode()).hexdigest()
            scores.append(record)
        experiments.append(dict(h=h,q=q,scores=scores))
        print('Checked signed side:',h,q,[x['side_roles'] for x in scores],flush=True)
    require(all(x['density']<=6 for row in experiments for x in row['scores']),
            'A small tested core unexpectedly has positive deficit')
    sources=('scripts/audit_positive_side.py','scripts/experiments/positive_side_core.py',
             'scripts/exclusion_circuit.py','scripts/finite_bit_contract.py',
             'scripts/experiments/rank_product_core.py','scripts/experiments/shared_core.py',
             'scripts/experiments/signed_sparse_core.py','docs/research/positive-side-core.md')
    return dict(status='VERIFIED COMPRESSED-SIDE COMPILER; BOUNDED SMALL HEURISTICS; NO NEW KAPPA',
        upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
        expanded_complete_controls=controls,small_signed_experiments=experiments,
        large_target_side_circuit_supplied=False,
        scope='The compiler proof applies to positive-definite rational labels and exact cancellation-free side DAGs. The strategy scores are finite heuristic constructions, not lower bounds or extrapolations to q=16,h=31.',
        source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/positive-side-core.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS positive-definite compressed side compiler and bounded controls; no new kappa.')
