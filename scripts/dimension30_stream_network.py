#!/usr/bin/env python3
"""Separate h30 batched witness using the verified dimension-parametric motif."""
from dataclasses import asdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json

from batched_stream_network import complex_certificate, bulk_complex_guard, REFERENCE
from certify import Parameters, require
from fast_gaussian import fast_constraints, fast_margins
from compact_control_layer import layer_exponents
from prepare_layers import serializable
from experiments.ternary_dimension_sweep import moment
from experiments.ternary_target_certify import file_hash

ROOT = Path(__file__).resolve().parents[1]
H, ROLES = 30, 13056812
BIT_SAVING = Q(336958, 10**12)
COMPLEX_SAVING = Q(7, 10**7)
KAPPA = Q(168478, 10**12)


def bit_certificate(a=BIT_SAVING, roles=ROLES):
    result = moment(H, roles, a)
    require(result['strict_gap'] > 0, 'Unsupported h30 bit saving')
    return result


def parameters():
    return Parameters(tau=1-BIT_SAVING, sigma=1-COMPLEX_SAVING,
                      epsilon=Q(499999915710, 10**12), c=Q(1), beta=Q(1, 1000),
                      delta=Q(1, 10**10), lam=1-BIT_SAVING+Q(1, 10**16),
                      lamp=1-BIT_SAVING+Q(2, 10**16), C1=Q(11999, 10000), kappa=KAPPA)


def assembly(p=None, roles=ROLES):
    p = parameters() if p is None else p
    bit_certificate(1-p.tau, roles)
    complex_result = complex_certificate(1-p.sigma)
    require(p.sigma < p.tau, 'Mixed-width internal-cost case changed')
    guard = bulk_complex_guard(complex_result['counts'], p.beta, Q(1, 10000))
    require(p.C1 == guard['C1'], 'Bulk guard mismatch')
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    constraints = fast_constraints(p)
    constraints['packed_overhead'] = p.lam-exponents['internal']
    constraints['reserved_axes'] = p.lamp-exponents['preprocessing']
    for name, value in constraints.items():
        require(value > 0, 'Assembly constraint failed: '+name)
    margins = fast_margins(p)
    minimum = min(margins.values())
    require(minimum > p.kappa, 'No strict final absorption gap')
    return dict(parameters=asdict(p), guard=guard, recurrence=exponents,
                constraints=constraints, margins=margins, minimum_margin=minimum,
                absorption_gap=minimum-p.kappa, factor_over_aligned=p.kappa/Q(1624, 10**12))


def certificate(producer):
    require(producer['h'] == H, 'Wrong producer dimension')
    require(producer['global_roles'] == dict(current=ROLES, center_loss=12180, extra_frame_loss=0),
            'H30 producer boundary contract changed')
    require(producer['matching']['every_intersection_two']
            and producer['matching']['distinct_images'] == 142506, 'Missing full matching audit')
    reference = json.loads((REFERENCE/'SOURCE.json').read_text())
    for name, digest in reference['sha256'].items():
        require(file_hash(REFERENCE/name) == digest, 'Changed PR #10 reference: '+name)
    paths = ('scripts/dimension30_stream_network.py', 'scripts/batched_stream_network.py',
             'scripts/experiments/ternary_dimension_sweep.py', 'scripts/prime_field_network.py',
             'scripts/fast_gaussian.py', 'scripts/compact_control_layer.py',
             'docs/research/dimension30-stream.md', 'tests/test_dimension30_stream_network.py')
    return dict(status='CONDITIONAL H30 BATCHED STREAM WITNESS; NOT FORMAL VERIFICATION',
                producer=producer, bit=bit_certificate(), complex=complex_certificate(),
                assembly=assembly(), batching_reference=reference,
                proof_sha256={name: file_hash(ROOT/name) for name in paths},
                scope='Exact finite h30 producer/matching/physical compiler and exact moments. '
                      'Uses PR #12 even-dimension matching and dimension-parametric PR #10 '
                      'controlled-basis/transfer arguments; retains the h28 complex network, '
                      'bulk guard, corrected Gaussian precision and inherited multiplication interfaces.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--workdir', type=Path)
    args = parser.parse_args()
    if not args.quick:
        from experiments.ternary_dimension_certify import certificate as producer_certificate
        producer = producer_certificate(args.workdir)
        result = certificate(producer)
        for name, value in [('dimension30-stream-producer.json', producer),
                            ('dimension30-stream-witness.json', result)]:
            (ROOT/'certificates'/name).write_text(json.dumps(serializable(value), indent=2, sort_keys=True)+'\n')
    result = assembly()
    print('PASS conditional', KAPPA, '; h30 roles', ROLES,
          '; factor over aligned', result['factor_over_aligned'],
          '; margin', result['minimum_margin'], '; gap', result['absorption_gap'])
