#!/usr/bin/env python3
"""Exact bit, complex and assembly certificate for batched recursive widths.

The PR #7 finite producers are consumed unchanged. New proofs give
large-projector bit batching, whole-residual complex batching, arbitrary
integer widths, and the dependency-path coefficient guard. This module
certifies their rational exponent comparisons and final assembly margins.
"""
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import json

from controlled_bit_rank_moment import (
    BIT_SAVING, certificate as bit_certificate,
    rational_log_bounds, log_integer_upper,
)
from bulk_complex_guard import bulk_complex_guard
from certify import Parameters, require
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from prepare_layers import serializable


ROOT = Path(__file__).resolve().parents[1]
COMPLEX_SAVING = Q(7, 10**7)
KAPPA = Q(6149999, 5*10**13)
ZETA = Q(1, 10000)


def complex_counts():
    h = 28
    v = comb(h, 3)
    m = h**3
    side_roles = 93838
    auxiliary_roles = side_roles+h+1
    N = v**3
    W = 2*v*v*(v+auxiliary_roles)
    L = 3*v*v*h*(h+1)
    deficit = 2*N-2*L
    s = W*m-deficit
    copies = v*v*auxiliary_roles
    bulk = [
        dict(name='first_third_stage_auxiliary_joins',
             copies=copies, rank=m-2*h),
        dict(name='second_stage_auxiliary_sink_edges',
             copies=copies, rank=m-h*h),
    ]
    singletons = s-sum(row['copies']*row['rank'] for row in bulk)
    require(deficit > 0 and singletons > 0, 'Invalid complex rank masses')
    return dict(h=h, v=v, m=m, N=N, side_roles=side_roles,
                auxiliary_roles=auxiliary_roles, W=W, L=L, s=s,
                deficit=deficit, eta=Q(deficit, W*m),
                bulk_classes=bulk, singleton_calls=singletons)


def complex_certificate(a=COMPLEX_SAVING):
    n = complex_counts()
    m, W = n['m'], n['W']
    ratios = [Q(1, m)]+[Q(row['rank'], m) for row in n['bulk_classes']]
    weights = [Q(n['singleton_calls'], W*m)]+[
        Q(row['copies']*row['rank'], W*m) for row in n['bulk_classes']]
    logarithms = [Q(9997, 1000), Q(2555, 10**6), Q(36368, 10**6)]
    enclosures = [log_integer_upper(m)]+[
        rational_log_bounds(1/r)[1] for r in ratios[1:]]
    require(sum(weights) == 1-n['eta'], 'Complex rank-mass identity failed')
    for rigorous, simple in zip(enclosures, logarithms):
        require(rigorous < simple, 'Complex rational logarithm bound failed')
        require(0 < a*simple < 1, 'Exponential upper-bound range failed')
    upper = sum((w/(1-a*ell) for w, ell in zip(weights, logarithms)), Q(0))
    require(upper < 1, 'Unsupported complex exponent')
    return dict(complex_saving=a, sigma=1-a, counts=n,
                normalized_widths=ratios, rank_mass_weights=weights,
                logarithm_upper_bounds=logarithms, logarithm_enclosures=enclosures,
                moment_upper=upper, strict_gap=1-upper,
                formula='sum_i weight_i * ratio_i^(-complex_saving) < 1',
                bound='exp(x) <= 1/(1-x), for 0 <= x < 1')


def parameters():
    return Parameters(
        tau=1-BIT_SAVING, sigma=1-COMPLEX_SAVING,
        epsilon=Q(7999999, 16000000), c=Q(1),
        beta=Q(1, 1000), delta=Q(1, 10**10),
        lam=1-BIT_SAVING+Q(1, 10**16),
        lamp=1-BIT_SAVING+Q(2, 10**16),
        C1=Q(11999, 10000), kappa=KAPPA,
    )


def assembly(p=None, cn=None):
    p = parameters() if p is None else p
    cn = complex_counts() if cn is None else cn
    require(1-p.tau == BIT_SAVING and 1-p.sigma == COMPLEX_SAVING,
            'Assembly and motif exponents differ')
    require(p.sigma < p.tau, 'The stated mixed-width internal-cost case changed')
    g = bulk_complex_guard(cn, p.beta, ZETA)
    require(p.C1 == g['C1'], 'Bulk guard exponent mismatch')
    exponents = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    constraints = fast_constraints(p)
    constraints['packed_overhead'] = p.lam-exponents['internal']
    constraints['reserved_axes'] = p.lamp-exponents['preprocessing']
    for name, slack in constraints.items():
        require(slack > 0, 'Assembly constraint failed: '+name)
    margins = fast_margins(p)
    minimum = min(margins.values())
    require(minimum > p.kappa, 'No strict final absorption gap')
    require(p.kappa > Q(1, 2**23), 'Dyadic improvement comparison failed')
    return dict(parameters=asdict(p), guard=g, recurrence=exponents,
                constraints=constraints, margins=margins,
                minimum_margin=minimum, absorption_gap=minimum-p.kappa,
                dyadic_corollary='2^-23',
                dyadic_gap=p.kappa-Q(1, 2**23))


def certificate():
    b = bit_certificate()
    c = complex_certificate()
    w = assembly(cn=c['counts'])
    source_paths = [
        'notes/batched-23-note.tex',
        'notes/batched-algorithms.tex',
        'notes/batched-bit-rows.tex',
        'notes/batched-complex-rows.tex',
        'notes/batched-path-budget.tex',
        'notes/projector-batching.tex',
        'notes/batched-bit-rank-accounting.tex',
        'notes/controlled-projector-basis.tex',
        'notes/chirp-scaling-correction.tex',
        'notes/fast-gaussian-resampling.tex',
        'notes/bulk-complex-guard.tex',
        'notes/batched-assembly.tex',
        'scripts/batched_bit_rank_moment.py',
        'scripts/controlled_bit_rank_moment.py',
        'scripts/bulk_complex_guard.py',
        'scripts/batched_network.py',
        'scripts/make_batched_patch.py',
    ]
    return dict(
        status='CONDITIONAL 6149999/(5*10^13) > 2^-23 INTEGER-MULTIPLICATION WITNESS',
        upstream_commit='adc7f1241b42e322a6451854ab7e4b4c146bf78a',
        retained_PR7_commit='6725c6a17b17871a35353fd29157f4ed851bc114',
        bit=b, complex=c, assembly=w,
        new_source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths},
        scope='Exact exponent and assembly arithmetic for the new batching and '
              'dependency-path proofs, consuming the retained PR #7 finite '
              'producers and the stated upstream analytic and tape interfaces.',
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()
    result = certificate()
    if args.output:
        args.output.write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    if args.summary:
        w = result['assembly']
        print('PASS kappa='+str(KAPPA)+' > 2^-23')
        print('bit saving='+str(BIT_SAVING)+'; complex saving='+str(COMPLEX_SAVING))
        print('minimum margin='+str(w['minimum_margin']))
        print('strict absorption gap='+str(w['absorption_gap']))
        print(str(len(w['constraints']))+' strict constraints; '+str(len(w['margins']))+' strict margins')
    else:
        print(json.dumps(serializable(result), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
