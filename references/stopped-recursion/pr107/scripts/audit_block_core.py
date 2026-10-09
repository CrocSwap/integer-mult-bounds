#!/usr/bin/env python3
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json

from audit_joint_frames import eye
from certify import require,verify_sources
from prepare_layers import serializable
from experiments.block_core import check_block_pair,compile_block,block_counts,block_side_budget
from finite_bit_contract import inspect_candidate

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    core=check_block_pair([3,3],eye(4),2);controls=[]
    for permutation in (None,[1,0]):
        candidate,ledger=compile_block(core,permutation)
        checked=inspect_candidate(candidate,require_deficit=False)
        require(checked['s']==ledger['s'] and checked['deficit']==ledger['deficit'],
                'Expanded higher-rank ledger failed')
        controls.append(dict(permutation=permutation,ledger=ledger,checked=checked))
    old=json.loads((ROOT/'certificates/paired-network.json').read_text())['bit_counts']
    old={k:Q(v) for k,v in old.items()}
    same=block_counts(comb(50,3),50,100,2,int(old['side_roles_per_invocation']),shared=True)
    require(same['W']==old['W'] and same['m']==8*old['m'] and same['s']==8*old['s'],
            'Direct-sum control does not scale the existing finite construction')
    require(same['relative_deficit']==old['eta'],'Direct sum changed the relative deficit')
    budgets=[dict(h=h,**block_side_budget(comb(h,3),h,h,2,Q(16,10**8)))
             for h in (24,26,28,30,32,34,36)]
    sources=('scripts/audit_block_core.py','scripts/experiments/block_core.py',
             'scripts/experiments/rank_product_core.py','scripts/experiments/shared_core.py',
             'docs/research/block-core.md','certificates/paired-network.json')
    return dict(status='HIGHER-RANK BIT COMPILER; NO BETTER BLOCK REPRESENTATION OR KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                expanded_controls=controls,positive_direct_sum_control=same,
                hypothetical_rank_two_budgets=budgets,
                scope='Raw side compiler verified generically; reusing compressed side-role budgets requires new compatible side frames.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/block-core.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS higher-rank bit compiler and direct-sum regression; no stronger kappa.')
