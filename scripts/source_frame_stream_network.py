#!/usr/bin/env python3
"""PR #13 source frames + smaller h30 producer + all complex residuals.

The source-frame move is eumemic's PR #13 contribution. PR #10 supplies the
batching transfer and PR #12 the dimension-parametric bank matching.
"""
from dataclasses import asdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'references/pr10/scripts'))
from controlled_bit_rank_moment import counts as old_counts
from certify import Parameters, require
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from prepare_layers import serializable
from experiments.ternary_dimension_sweep import log_upper
from experiments.ternary_target_certify import file_hash
from experiments.complex_all_residuals import certificate as complex_certificate

H,ROLES=30,13056812
BIT_SAVING=Q(2153359,10**12)
COMPLEX_SAVING=Q(4191487,10**12)
KAPPA=Q(1076678,10**12)


def bit_counts(h=H,roles=ROLES):
    n=old_counts(h=h,roles=roles)
    m,v=n['m'],n['v']; copies=v*v*roles
    blocks=[dict(name='stage_one_three_join',copies=copies,width=m-4*h),
            dict(name='stage_three_data_entrance',copies=2*v**3,width=m-2*h*h-2*h+2),
            dict(name='stage_two_source_frame_exit',copies=copies,width=m-2*h)]
    singletons=n['original_rank_sum']-sum(row['copies']*row['width'] for row in blocks)
    require(singletons==n['singleton_calls']-copies*(h*h-2*h),'Source-frame rank relocation failed')
    require(singletons>0 and all(0<row['width']<m for row in blocks),'Invalid recursive widths')
    return dict(h=h,m=m,v=v,W=n['W'],roles=roles,eta=n['eta'],
                rank_sum=n['original_rank_sum'],deficit=n['deficit'],
                singleton_calls=singletons,recursive_blocks=blocks,
                removed_entrance_rank=h*h-h,new_exit_rank=m-h,exit_corner_pivots=h)


def bit_certificate(a=BIT_SAVING,h=H,roles=ROLES):
    n=bit_counts(h,roles);m,W=n['m'],n['W']
    widths=[1]+[row['width'] for row in n['recursive_blocks']]
    masses=[n['singleton_calls']]+[row['copies']*row['width'] for row in n['recursive_blocks']]
    weights=[Q(mass,W*m) for mass in masses]
    logs=[log_upper(Q(m,width)) for width in widths]
    require(sum(weights)==1-n['eta'],'Bit rank mass changed')
    require(all(0<=a*ell<1 for ell in logs),'Invalid exponential comparison')
    upper=sum((w/(1-a*ell) for w,ell in zip(weights,logs)),Q(0))
    require(upper<1,'Unsupported source-frame bit saving')
    return dict(bit_saving=a,counts=n,rank_mass_weights=weights,
                normalized_widths=[Q(width,m) for width in widths],
                logarithm_upper_bounds=logs,moment_upper=upper,strict_gap=1-upper)


def parameters():
    tau=1-BIT_SAVING
    epsilon=Q(((1-Q(1,10**10))/(2+BIT_SAVING)*10**12).__floor__(),10**12)
    return Parameters(tau=tau,sigma=1-COMPLEX_SAVING,epsilon=epsilon,c=Q(1),
                      beta=Q(1,1000),delta=Q(1,10**10),lam=tau+Q(1,10**16),
                      lamp=tau+Q(2,10**16),C1=Q(3749,2500),kappa=KAPPA)


def assembly(complex_result,p=None,roles=ROLES):
    p=parameters() if p is None else p
    bit_certificate(1-p.tau,roles=roles)
    require(complex_result['complex_saving']==1-p.sigma,'Complex saving mismatch')
    require(complex_result['moment_upper']<1,'Complex moment failed')
    g=complex_result['guard']
    require(p.C1==g['C1'],'All-residual guard mismatch')
    require(p.sigma<p.tau,'Complex saving no longer exceeds bit saving')
    exponents=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    constraints=fast_constraints(p)
    constraints['packed_overhead']=p.lam-exponents['internal']
    constraints['reserved_axes']=p.lamp-exponents['preprocessing']
    for name,slack in constraints.items():require(slack>0,'Assembly constraint failed: '+name)
    margins=fast_margins(p);minimum=min(margins.values())
    require(minimum>p.kappa,'No strict final absorption gap')
    return dict(parameters=asdict(p),guard=g,recurrence=exponents,constraints=constraints,
                margins=margins,minimum_margin=minimum,absorption_gap=minimum-p.kappa,
                factor_over_aligned=p.kappa/Q(1624,10**12),
                factor_over_PR13=p.kappa/Q(7699,10**10),dyadic_gap=p.kappa-Q(1,2**20))


def validate_hashes(record):
    for name,digest in record.get('proof_sha256',{}).items():
        require(file_hash(ROOT/name)==digest,'Changed proof dependency: '+name)


def certificate(producer):
    require(producer['h']==H,'Wrong producer dimension')
    require(producer['global_roles']==dict(current=ROLES,center_loss=12180,extra_frame_loss=0),
            'Producer boundary contract changed')
    validate_hashes(producer)
    require(producer['matching']['every_intersection_two']
            and producer['matching']['distinct_images']==142506,'Missing h30 matching audit')
    references={}
    for pr in ('pr10','pr12','pr13'):
        reference=ROOT/'references'/pr
        manifest=json.loads((reference/'SOURCE.json').read_text())
        for name,digest in manifest['sha256'].items():
            require(file_hash(reference/name)==digest,'Changed '+pr+' reference: '+name)
        references[pr]=manifest
    from experiments.source_frame_basis_control import certificate as basis_certificate
    complex_result=complex_certificate()
    require(complex_result['complex_saving']==COMPLEX_SAVING,'Unexpected complex saving')
    paths=('scripts/source_frame_stream_network.py','scripts/experiments/ternary_dimension_sweep.py',
           'scripts/fast_gaussian.py','scripts/compact_control_layer.py',
           'docs/research/source-frame-stream.md','tests/test_source_frame_stream_network.py',
           'scripts/experiments/source_frame_basis_control.py','tests/test_source_frame_basis_control.py',
           'scripts/experiments/controlled_basis_control.py','tests/test_controlled_basis_control.py')
    return dict(status='CONDITIONAL SOURCE-FRAME STREAM WITNESS; NOT FORMAL VERIFICATION',
                producer=producer,bit=bit_certificate(),complex=complex_result,
                assembly=assembly(complex_result),source_frame_basis_control=basis_certificate(),
                references=references,proof_sha256={name:file_hash(ROOT/name) for name in paths},
                scope='Exact h30 producer, matching, frames, bilateral allocation, rank moments '
                      'and assembly arithmetic. General source-frame, simultaneous-basis, '
                      'nested-wire, all-complex batching, precision, and inherited multiplication '
                      'arguments remain mathematical dependencies.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer',type=Path,help='Use a source-hash-validated producer certificate')
    parser.add_argument('--workdir',type=Path)
    parser.add_argument('--quick',action='store_true',help='Arithmetic and complex histogram only')
    args=parser.parse_args()
    if args.quick:
        result=assembly(complex_certificate())
    else:
        if args.producer:
            producer=json.loads(args.producer.read_text())
        else:
            from experiments.ternary_dimension_certify import certificate as producer_certificate
            producer=producer_certificate(args.workdir)
        combined=certificate(producer)
        (ROOT/'certificates/source-frame-stream-witness.json').write_text(
            json.dumps(serializable(combined),indent=2,sort_keys=True)+'\n')
        result=combined['assembly']
    print('PASS conditional',KAPPA,'; factor over aligned',result['factor_over_aligned'],
          '; margin',result['minimum_margin'],'; gap',result['absorption_gap'])
