#!/usr/bin/env python3
"""Conditional direct intersection-two producer and full assembly witness.

The exact full producer/frame checker is separate from the arithmetic below.
Zhihao Chen's PR7 motif and retained complex construction are the foundation.
"""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json

from certify import require
from prepare_layers import serializable
from prime_field_network import bit_counts, parameters as pr7_parameters, witness as pr7_witness

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(8559, 10**12)
KAPPA = Q(4277, 10**12)
ROLES = 10365877


def parameters():
    return replace(pr7_parameters(), tau=1-BIT_SAVING,
                   lam=1-Q(8558, 10**12), lamp=1-Q(8557, 10**12), kappa=KAPPA)


def witness():
    return pr7_witness(p=parameters(), bn=bit_counts(ROLES))


def certificate(producer):
    require(producer['global_roles']['current'] == ROLES, 'Direct producer width mismatch')
    require(producer['global_roles']['extra_frame_loss'] == 0,
            'Unexpected direct-producer frame loss')
    require(producer['frames']['every_final_frame_nondegenerate'], 'Unresolved rational frame')
    paths = ['scripts/ternary_target_network.py', 'docs/research/ternary-targets.md']
    return dict(status='CONDITIONAL 4277/10^12 WITNESS; NOT FORMAL VERIFICATION',
                predecessor=dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/7',
                                 head='6725c6a17b17871a35353fd29157f4ed851bc114',
                                 author='Zhihao Chen (jacklightChen)', kappa=Q(373, 10**11)),
                producer=producer, witness=witness(),
                proof_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                scope='Exact full-size source supports, all output families, nondegenerate frame '
                      'audit and assembly arithmetic; tensor-stage transfer and all inherited '
                      'multiplication interfaces rely on the written conditional proofs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Check arithmetic only; do not write certificates')
    args = parser.parse_args()
    if not args.quick:
        from experiments.ternary_target_certify import certificate as producer_certificate
        producer = producer_certificate()
        (ROOT/'certificates/ternary-target-network.json').write_text(
            json.dumps(serializable(producer), indent=2, sort_keys=True)+'\n')
        (ROOT/'certificates/ternary-target-witness.json').write_text(
            json.dumps(serializable(certificate(producer)), indent=2, sort_keys=True)+'\n')
    result = witness()
    print('PASS conditional', KAPPA, '; roles', ROLES,
          '; minimum margin', result['minimum_margin'], '; gap', result['absorption_gap'])
