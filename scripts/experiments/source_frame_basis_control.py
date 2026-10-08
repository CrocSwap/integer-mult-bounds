#!/usr/bin/env python3
"""Independent finite controls for PR #13's auxiliary source-frame basis.

The existing integer controlled-basis tuple handles all 57 old h=3
projectors and all nine coordinate A4 projectors simultaneously. A separate
h=5 control uses the actual five-subset label form I-2J/25. Arithmetic is
exact modulo PRIME. Nonzero modular corner determinants imply rational
nonzero determinants; rational zero identities and general pivot profiles
still use the projector and Schur-complement proofs, not modular zeros.
"""
from fractions import Fraction
from pathlib import Path
from random import Random
import argparse
import json

try:
    from .controlled_basis_control import (
        PRIME, SingularMatrix, certificate as old_certificate, check_projector,
        identity, inverse, lower_pivots, multiply)
except ImportError:
    from controlled_basis_control import (
        PRIME, SingularMatrix, certificate as old_certificate, check_projector,
        identity, inverse, lower_pivots, multiply)

PREDECESSOR = dict(url='https://github.com/CrocSwap/integer-mult-bounds/pull/13',
                   head='3ef246fa4f69c87ebfed78376418afa9ffcad145', author='eumemic')


def add(*matrices, signs=None):
    signs = signs or [1]*len(matrices)
    n = len(matrices[0])
    return [[sum(s*a[i][j] for s,a in zip(signs,matrices)) % PRIME
             for j in range(n)] for i in range(n)]


def tensor(a,b):
    return [[x*y % PRIME for x in row_a for y in row_b]
            for row_a in a for row_b in b]


def controlled_matrix(h,K,G):
    H = h*h
    return [[G[i][a][b]*K[i][j] % PRIME
             for b in range(h) for j in range(H)]
            for a in range(h) for i in range(H)]


def shifted_exit(source, final, sink=None):
    """Require the all-role endpoint contract before forming the exit edge."""
    unit = identity(len(source))
    sink = add(unit,source) if sink is None else sink
    if add(sink,source,signs=[1,-1]) != unit:
        raise ValueError('Auxiliary endpoint difference is not identity')
    return add(sink,final,signs=[1,-1])


def common_coordinate_control(h=3):
    old = old_certificate(h)
    H,m = h*h,h**3
    S = controlled_matrix(h,**old['parameters'])
    Sinv = inverse(S)
    profiles = []
    for t in range(h):
        for p in range(h):
            # Nullspace <e_t> tensor (<e_p> tensor F), in (third, first,
            # second) order. The second factor is the free h-space.
            zeros = {t*H+p*h+q for q in range(h)}
            transformed = multiply(
                [[0 if j in zeros else x for j,x in enumerate(row)] for row in S], Sinv)
            profiles.append(check_projector(transformed,h))
    assert all(profile == profiles[0] for profile in profiles)
    return dict(h=h, m=m, old_projectors_checked=old['projectors_checked'],
                new_projectors_checked=len(profiles),
                total_projectors_checked=old['projectors_checked']+len(profiles),
                old_class_counts=old['class_counts'], new_class='A4',
                new_profile=profiles[0], one_common_integer_parameter_tuple=True,
                parameter_sha256=old['parameter_sha256'], parameters=old['parameters'],
                rational_corner_nonsingularity_certified=True)


def five_subset_control():
    """Actual h=5 label form, full source/exit matrices and pivot profile."""
    h,H,m = 5,25,125
    # Omega has denominator 25. For the unique five-subset t=(1,...,1),
    # t^T Omega t=3, so its line is nondegenerate over Q and modulo PRIME.
    t = [1]*h
    omega_numerator = [[25*int(i==j)-2 for j in range(h)] for i in range(h)]
    dual_numerator = [sum(t[i]*omega_numerator[i][j] for i in range(h))
                      for j in range(h)]
    norm_numerator = sum(x*y for x,y in zip(t,dual_numerator))
    assert Fraction(norm_numerator,25) == 3
    scale = pow(norm_numerator,PRIME-2,PRIME)
    line = [[x*y*scale % PRIME for y in dual_numerator] for x in t]
    source = tensor(line,tensor(add(identity(h),line,signs=[1,-1]),identity(h)))
    final = tensor(line,identity(H))
    exit_matrix = shifted_exit(source,final)
    assert multiply(final,source) == source
    assert multiply(source,final) == source
    assert multiply(exit_matrix,exit_matrix) == exit_matrix
    ranks = dict(source=len(lower_pivots(source)), final=len(lower_pivots(final)),
                 internal=len(lower_pivots(add(final,source,signs=[1,-1]))),
                 old_exit=len(lower_pivots(add(identity(m),final,signs=[1,-1]))),
                 new_exit=len(lower_pivots(exit_matrix)))
    assert ranks == dict(source=H-h,final=H,internal=h,old_exit=m-H,new_exit=m-h)
    assert ranks['source']+ranks['internal']+ranks['old_exit'] == m
    assert ranks['internal']+ranks['new_exit'] == m
    rng = Random(131026)
    for trial in range(100):
        try:
            K = [[rng.randrange(-50,51) for _ in range(H)] for _ in range(H)]
            inverse(K)
            G = [[[rng.randrange(-50,51) for _ in range(h)] for _ in range(h)]
                 for _ in range(H)]
            for block in G:
                inverse(block)
            S = controlled_matrix(h,K,G)
            transformed = multiply(multiply(S,exit_matrix),inverse(S))
            profile = check_projector(transformed,h)
            return dict(h=h, m=m, label_form='I-2J/25', exact_line_norm='3',
                        source_frame_rank=H-h, new_entrance_rank=0,
                        ranks=ranks, old_total_rank=m, new_total_rank=m,
                        endpoint_difference_identity=True, exit_idempotent_mod_prime=True,
                        pivot_profile=profile, accepted_trial=trial)
        except SingularMatrix:
            continue
    raise ValueError('No successful h5 control tuple within the search budget')


def certificate():
    return dict(status='FINITE SOURCE-FRAME BASIS CONTROL; GENERAL PROOF SEPARATE',
                predecessor=PREDECESSOR, prime=PRIME,
                common_basis=common_coordinate_control(), five_subset=five_subset_control(),
                scope='One common h3 basis covers 57 old and nine new projectors; an actual '
                      'h5 five-subset tests the shifted source and exit. Nonzero modular '
                      'corners certify rational nonzero corners. General simultaneous h28/h30 '
                      'basis existence, rational pivot zero patterns, physical endpoint '
                      'assignment and multiplication assembly remain written proof dependencies.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=certificate()
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS same basis for 57+9 projectors; actual h5 source-frame rank and pivots')
