#!/usr/bin/env python3
"""Exact rational positive and negative ledgers; never a frontier certificate."""
from fractions import Fraction as Q
import json
from pathlib import Path

selected=Q('0.001672660197076918')
bit=Q('0.001733427039589844234749')
complex_=Q('0.001675462676808103522925')
a=Q('0.00173');q=Q(67,40000);eps=Q(99999,100000)
r=Q(1,200000);beta=Q(1,100000);k=Q(83749,50000000)
# An exact elementary upper bound sufficient for the ledger.
assert 7**16 < 2**45
omega_upper=Q(45,16)
margins=dict(coordinate_routing=a,synthetic=eps*q,
             hypothetical_tensor_local=1-eps*(1-q),
             batched_boundary=1-(omega_upper-1)*(1-r)/2,
             polynomial_products=eps)
slacks=dict(bit_endpoint=bit-a,complex_endpoint=complex_-q,
            leaf_saving=(1-beta)*complex_-q,gamma=1-eps-r,
            epsilon_positive=eps,epsilon_below_one=1-eps,
            rank_exponent=q,beta_positive=beta,beta_below_one=1-beta)
slacks.update({name+'_above_kappa':v-k for name,v in margins.items()})
assert all(v>0 for v in slacks.values())
paid=dict(margins,unfused_gaussian=1-eps)
assert min(paid.values()) < k
assert 1-eps < selected
assert k>selected
# Require the missing map to be declared; calculations do not discharge it.
result=dict(status='PASS_OPTIMISTIC_LEDGER_AND_PAID_REJECTION',
            selected_kappa=str(selected), target_kappa=str(k),
            absolute_gain=str(k-selected),
            proposed_parameters={name:str(v) for name,v in
                                 dict(a=a,q=q,epsilon=eps,r=r,beta=beta).items()},
            omega_upper=str(omega_upper),omega_control='7^16 < 2^45',
            optimistic_margins={name:str(v) for name,v in margins.items()},
            optimistic_slacks={name:str(v) for name,v in slacks.items()},
            fully_paid_margins={name:str(v) for name,v in paid.items()},
            fully_paid_accepts_target=False,
            missing_lemma='Stable complete tensor Gaussian resampling including variable-core movement in stated cost and O(p) record width.',
            scope='Arithmetic conditional target and explicit rejected existing-interface row; not a new multiplication certificate.')
Path(__file__).with_name('LEDGER.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
