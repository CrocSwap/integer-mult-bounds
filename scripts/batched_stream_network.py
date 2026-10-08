#!/usr/bin/env python3
"""Combine the smaller producer with IceKylin's PR #10 batching construction.

PR #10 is pinned at 62691e395a0458ce089a1c7b5d89e74291e95e29. Unmodified
rank-moment/guard code and proof dependencies live in references/pr10, with
their original attribution and hashes. This adds no publication artifacts.
"""
from dataclasses import asdict, replace
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'references/pr10'
sys.path.insert(0,str(REFERENCE/'scripts'))
from controlled_bit_rank_moment import certificate as controlled_certificate
from bulk_complex_guard import bulk_complex_guard
from certify import require
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from prime_field_network import complex_counts, parameters as original_parameters
from prepare_layers import serializable
from search_network import log_integer_bounds, log_ratio_bounds
from experiments.ternary_target_certify import file_hash

ROLES=8771396
BIT_SAVING=Q(329773,10**12)
COMPLEX_SAVING=Q(7,10**7)
KAPPA=Q(164886,10**12)


def bit_certificate(a=BIT_SAVING,roles=ROLES):
    return controlled_certificate(a=a,roles=roles)


def complex_certificate(a=COMPLEX_SAVING):
    """PR #10 whole-residual moment on the unchanged PR #7 complex network."""
    n=complex_counts();h,m,W=n['h'],n['m'],n['W']
    copies=n['v']**2*(n['roles']+h+1)
    ranks=(m-2*h,m-h*h)
    singles=n['s']-copies*sum(ranks)
    require(singles>0,'Invalid singleton count')
    ratios=[Q(1,m),*(Q(r,m) for r in ranks)]
    weights=[Q(singles,W*m),*(Q(copies*r,W*m) for r in ranks)]
    logs=[Q(9997,1000),Q(2555,10**6),Q(36368,10**6)]
    bounds=[log_integer_bounds(m)[1],*(log_ratio_bounds(1/r)[1] for r in ratios[1:])]
    require(sum(weights)==1-n['eta'],'Complex rank-mass identity failed')
    for rigorous,bound in zip(bounds,logs):
        require(rigorous<bound and 0<a*bound<1,'Invalid complex log comparison')
    upper=sum((w/(1-a*ell) for w,ell in zip(weights,logs)),Q(0))
    require(upper<1,'Unsupported complex saving')
    return dict(complex_saving=a,counts=n,normalized_widths=ratios,
                rank_mass_weights=weights,logarithm_upper_bounds=logs,
                logarithm_enclosures=bounds,moment_upper=upper,strict_gap=1-upper)


def parameters():
    return replace(original_parameters(),tau=1-BIT_SAVING,sigma=1-COMPLEX_SAVING,
                   epsilon=Q(499999917,10**9),c=Q(1),beta=Q(1,1000),
                   delta=Q(1,10**10),lam=1-BIT_SAVING+Q(1,10**16),
                   lamp=1-BIT_SAVING+Q(2,10**16),C1=Q(11999,10000),kappa=KAPPA)


def grid_selection():
    """Exact optimality controls for the fixed bit and epsilon grids only."""
    bit=bit_certificate()
    next_a=BIT_SAVING+Q(1,10**12)
    next_moment=sum((w/(1-next_a*ell) for w,ell in zip(
        bit['rank_mass_weights'],bit['logarithm_upper_bounds'])),Q(0))
    require(next_moment>=1,'Selected bit saving is not maximal on its grid')
    p=parameters();scale=10**9
    # g3=epsilon*(1-lamp) increases and g5=1-delta-2*epsilon decreases.
    # Their intersection gives an upper envelope for every seven-margin
    # minimum. On this grid its maximum is at one of the two adjacent points.
    crossing=(1-p.delta)/(2+1-p.lamp)
    lower=(crossing*scale).__floor__()
    candidates=[]
    for numerator in (lower,lower+1):
        epsilon=Q(numerator,scale)
        bound=min(epsilon*(1-p.lamp),1-p.delta-2*epsilon)
        actual=min(fast_margins(replace(p,epsilon=epsilon)).values())
        candidates.append(dict(epsilon=epsilon,margin_upper=bound,actual_minimum=actual))
    optimum=max(row['margin_upper'] for row in candidates)
    minimum=min(fast_margins(p).values())
    require(minimum==optimum,'Epsilon does not attain the global grid upper bound')
    require(any(row['epsilon']==p.epsilon for row in candidates),'Epsilon is not adjacent to the crossing')
    require(KAPPA<minimum<=KAPPA+Q(1,10**12),'Kappa is not the strict grid point below the minimum')
    return dict(bit_grid=Q(1,10**12),next_bit_saving=next_a,next_bit_moment=next_moment,
                epsilon_grid=Q(1,scale),epsilon_crossing=crossing,
                epsilon_candidates=candidates,kappa_grid=Q(1,10**12),
                scope='Maximal bit saving for this rational moment bound and grid; maximal '
                      'seven-margin minimum on the epsilon grid with all other parameters fixed. '
                      'No global parameter or construction optimum is asserted.')


def assembly(p=None,roles=ROLES):
    p=parameters() if p is None else p
    bit_certificate(1-p.tau,roles)
    c=complex_certificate(1-p.sigma)
    require(p.sigma<p.tau,'Mixed-width internal cost case changed')
    g=bulk_complex_guard(c['counts'],p.beta,Q(1,10000))
    require(p.C1==g['C1'],'Bulk guard mismatch')
    exponents=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    slacks=fast_constraints(p)
    slacks['packed_overhead']=p.lam-exponents['internal']
    slacks['reserved_axes']=p.lamp-exponents['preprocessing']
    for name,value in slacks.items():require(value>0,'Assembly constraint failed: '+name)
    margins=fast_margins(p);minimum=min(margins.values())
    require(minimum>p.kappa,'No strict final absorption gap')
    return dict(parameters=asdict(p),guard=g,recurrence=exponents,constraints=slacks,
                margins=margins,minimum_margin=minimum,absorption_gap=minimum-p.kappa,
                factor_over_aligned=Q(p.kappa,Q(1624,10**12)),
                factor_over_PR10=Q(p.kappa,Q(6149999,5*10**13)))


def certificate(producer):
    roles=producer['global_roles']
    require(roles['current']==ROLES,'Producer width changed')
    require(roles['extra_frame_loss']==0 and roles['center_loss']==9828,'Producer loss changed')
    manifest=json.loads((REFERENCE/'SOURCE.json').read_text())
    for name,digest in manifest['sha256'].items():
        require(file_hash(REFERENCE/name)==digest,'Changed PR #10 reference: '+name)
    from experiments.ternary_direction import paired_guard_control
    from experiments.controlled_basis_control import certificate as basis_control
    paths=('scripts/batched_stream_network.py','scripts/prime_field_network.py',
           'scripts/fast_gaussian.py','scripts/compact_control_layer.py',
           'docs/research/batched-stream.md','tests/test_batched_stream_network.py',
           'scripts/experiments/controlled_basis_control.py','tests/test_controlled_basis_control.py')
    return dict(status='CONDITIONAL BATCHED STREAM WITNESS; NOT FORMAL VERIFICATION',
                batching_reference=manifest,producer=producer,
                bit=bit_certificate(),complex=complex_certificate(),assembly=assembly(),
                grid_selection=grid_selection(),
                paired_complex_path_control=paired_guard_control(),
                controlled_basis_small_check=basis_control(),
                proof_sha256={name:file_hash(ROOT/name) for name in paths},
                scope='Exact producer, physical allocation, rank moments and assembly checks. '
                      'Conditional on the nested-wire argument, PR #10 controlled-basis and '
                      'mixed-width transfer/guard proofs, corrected Gaussian precision enclosure, '
                      'and inherited multiplication interfaces.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick',action='store_true',help='Arithmetic only; no certificate writes')
    parser.add_argument('--workdir',type=Path)
    parser.add_argument('--reuse-producer-certificate',type=Path,
                        help='Validate and reuse construction artifacts in --workdir; rerun the complete current register compiler')
    args=parser.parse_args()
    if not args.quick:
        from experiments.ternary_stream_certify import certificate as producer_certificate
        producer=producer_certificate(args.workdir,reuse_certificate=args.reuse_producer_certificate)
        result=certificate(producer)
        from ternary_stream_network import certificate as singleton_certificate
        for name,value in [('ternary-stream-producer.json',producer),
                           ('ternary-stream-witness.json',singleton_certificate(producer)),
                           ('batched-stream-witness.json',result)]:
            (ROOT/'certificates'/name).write_text(json.dumps(serializable(value),indent=2,sort_keys=True)+'\n')
    result=assembly()
    print('PASS conditional',KAPPA,'; factor over aligned',result['factor_over_aligned'],
          '; margin',result['minimum_margin'],'; gap',result['absorption_gap'])
