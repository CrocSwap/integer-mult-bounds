#!/usr/bin/env python3
"""Regenerate the ternary side DAG and certify its conditional assembly."""
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as Q
import json

from audit_joint_frames import eye
from certify import require,verify_sources
from experiments.prime_core import compile_prime,inspect_prime
from experiments.ternary_side import build,verify_invocation,verify_invocation_frames
from ternary_assembly import assembly_control,BIT_SAVING,KAPPA,SIDE_ROLES
from prepare_layers import serializable

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    prime=[]
    for p,C in ((3,[[1,2],[2,1]]),(5,[[1,2],[3,1]]),(3,[[1,2],[0,1]])):
        net,expected=compile_prime(C,p,eye(2),eye(2),[1,0])
        result=inspect_prime(net,require_deficit=False)
        require(result['s']==expected['s'],'Prime compiler frame ledger failed')
        prime.append(dict(actual=result,expected=expected))
    controls=[]
    for h in (8,9):
        result=build(h,retain_graph=True)
        scalar=verify_invocation(result);frames=verify_invocation_frames(result)
        result.pop('_graph')
        controls.append(dict(construction=result,scalar=scalar,frames=frames))
        print('Checked full ternary control:',h,flush=True)
    result=build(29,progress=lambda g,n,s:print('Ternary group',g,'allocated nodes',n,flush=True))
    require(result['active_additions']==19593239 and result['output_uses']==1187550
            and result['side_roles']==SIDE_ROLES,'Large shared-side counts changed')
    require(result['edges_sha256']=='343f88d0dd2858b51c70f24c26c7290b1b6519fbd9db40093d758a3c2f3481bd',
            'Large DAG differs from discovery witness')
    c=result['counts']
    require((c['W'],c['s'],c['deficit'])==(589493540769997500,
            14377157287342062574725,678497406452775),'Complete rank counts changed')
    a=assembly_control(c)
    sources=('scripts/audit_ternary_side.py','scripts/ternary_assembly.py',
        'scripts/experiments/ternary_side.py','scripts/experiments/prime_core.py',
        'scripts/experiments/disjoint_tensor.py','scripts/exclusion_circuit.py',
        'scripts/experiments/rank_product_core.py','scripts/experiments/shared_core.py',
        'scripts/certify.py','scripts/search_network.py','scripts/finite_bit_contract.py',
        'scripts/rational_tensor.py',
        'notes/finite-alphabet-transfer.tex','notes/ternary-five-subsets.tex',
        'certificates/complex-compression.json')
    return dict(status='CONDITIONAL TERNARY CONSTRUCTION AND 2^-30 ASSEMBLY',
        upstream_commit=verify_sources(),conditional_kappa=KAPPA,certified_bit_saving=BIT_SAVING,
        construction=result,prime_compiler_controls=prime,complete_invocation_controls=controls,
        assembly_control=a,orthogonal_matching=dict(method='regular bipartite double cover; deterministic augmenting-path algorithm',
            degree=20240,existence_proved=True,large_permutation_expanded=False),
        scope='The large DAG is constructed and counted exactly. Its sharing and frame proof is generative, with complete small coefficient and arbitrary-input controls. Upstream multiplication and identified extensions remain assumptions.',
        source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/ternary-side.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS ternary side construction and conditional 2^-30 assembly.')
