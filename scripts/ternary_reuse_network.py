#!/usr/bin/env python3
"""Conditional follow-up witness from exact common-pair gate fusion.

Builds on Zhihao Chen's PR7 construction without modifying its certificate.
General compiler and frame arguments are in docs/research/ternary-reuse.md.
"""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import json

from certify import require
from prepare_layers import serializable
from prime_field_network import bit_counts, parameters as pr7_parameters, witness as pr7_witness
from experiments.ternary_reuse_core2 import certificate as compiler_certificate

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(7543, 10**12)
KAPPA = Q(3769, 10**12)
ROLES = 11775168


def parameters():
    return replace(pr7_parameters(), tau=1-BIT_SAVING,
                   lam=1-Q(7542, 10**12), lamp=1-Q(7541, 10**12), kappa=KAPPA)


def witness():
    return pr7_witness(p=parameters(), bn=bit_counts(ROLES))


def certificate():
    local = compiler_certificate()
    require(local['saved_roles_per_common_pair'] == 174, 'Local savings changed')
    require(local['retained_additions'] == 41439 and local['original_local_roles'] == 44040,
            'Predecessor local template changed')
    saved = comb(28, 2)*local['saved_roles_per_common_pair']
    require(11840940-saved == ROLES, 'Global role bound mismatch')
    paths = ['scripts/experiments/ternary_reuse_core2.py',
             'scripts/experiments/ternary_reuse_plateaus.py',
             'scripts/ternary_reuse_network.py',
             'docs/research/ternary-reuse.md']
    return dict(status='CONDITIONAL 3769/10^12 WITNESS; NOT FORMAL VERIFICATION',
                predecessor=dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/7',
                                 head='6725c6a17b17871a35353fd29157f4ed851bc114',
                                 author='Zhihao Chen (jacklightChen)', kappa=Q(373, 10**11)),
                local_compiler=local,
                global_roles=dict(previous=11840940, saved=saved, current=ROLES,
                                  common_pair_contexts=comb(28, 2), center_loss=comb(28, 2)*26),
                witness=witness(),
                proof_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                scope='Exact local supports, deterministic rational span equality and F3 boundary '
                      'ranks; global role substitution and nested frames rely on the written '
                      'compiler proof. PR7 and all retained upstream interfaces remain assumptions.')


if __name__ == '__main__':
    (ROOT/'certificates/ternary-reuse-network.json').write_text(
        json.dumps(serializable(certificate()), indent=2, sort_keys=True)+'\n')
    result = witness()
    print('PASS conditional', KAPPA, '; roles', ROLES,
          '; minimum margin', result['minimum_margin'], '; gap', result['absorption_gap'])
