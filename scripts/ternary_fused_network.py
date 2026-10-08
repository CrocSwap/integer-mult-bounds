#!/usr/bin/env python3
"""Conditional assembly after exact common-frame fusion of the direct producer."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json

from certify import require
from prepare_layers import serializable
from prime_field_network import bit_counts, parameters as pr7_parameters, witness as pr7_witness
from ternary_target_network import certificate as direct_certificate

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(8567, 10**12)
KAPPA = Q(4281, 10**12)
ROLES = 10356672


def parameters():
    return replace(pr7_parameters(), tau=1-BIT_SAVING,
                   lam=1-Q(8566, 10**12), lamp=1-Q(8565, 10**12), kappa=KAPPA)


def witness():
    return pr7_witness(p=parameters(), bn=bit_counts(ROLES))


def certificate(fusion):
    producer = fusion['producer']
    direct_certificate(producer)
    roles = fusion['global_roles']
    boundary = fusion['source_and_dual_partition']['boundary']
    require(roles['previous'] == 10365877 and roles['current'] == ROLES
            and roles['saved'] == 9205, 'Fused producer width mismatch')
    require(roles['extra_frame_loss'] == 0 and roles['center_loss'] == 9828,
            'Unexpected fused-producer frame loss')
    require(boundary['new_roles'] == ROLES and boundary['inputs'] == 98280,
            'Fused boundary dimensions mismatch')
    require(boundary['inputs']+boundary['boundary_ports']-boundary['boundary_rank_sum'] == ROLES,
            'Boundary rank accounting mismatch')
    require(fusion['exactness']['boundary_field'] == 3,
            'Boundary ranks must use the ternary payload field')
    paths = ['scripts/ternary_fused_network.py', 'docs/research/ternary-span-fusion.md']
    return dict(status='CONDITIONAL 4281/10^12 WITNESS; NOT FORMAL VERIFICATION',
                predecessor=dict(producer='direct intersection-two producer',
                                 roles=10365877, kappa=Q(4277, 10**12)),
                compiler=fusion, witness=witness(),
                proof_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                scope='Exact producer, unchanged rational frames, common-frame boundary ranks '
                      'and assembly arithmetic. The reversible completion lemma, tensor-stage '
                      'transfer and inherited multiplication interfaces rely on the written proofs.')


def write_certificates(fusion):
    producer = fusion['producer']
    records = {
        'ternary-target-network.json': producer,
        'ternary-target-witness.json': direct_certificate(producer),
        'ternary-span-fusion.json': fusion,
        'ternary-fused-witness.json': certificate(fusion),
    }
    for name, result in records.items():
        (ROOT/'certificates'/name).write_text(
            json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Check arithmetic only; do not write certificates')
    args = parser.parse_args()
    if not args.quick:
        from experiments.ternary_span_fusion import certificate as fusion_certificate
        write_certificates(fusion_certificate())
    result = witness()
    print('PASS conditional', KAPPA, '; fused roles', ROLES,
          '; minimum margin', result['minimum_margin'], '; gap', result['absorption_gap'])
