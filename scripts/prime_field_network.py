#!/usr/bin/env python3
"""Conditional 373/10^11 > 2^-28 certificate: new F3 interchange and paired complex circuits.

Substantial new construction by Zhihao Chen (jacklightChen), with GPT-6 Astra
assistance. The attribution and retained dependencies are in NOTICE and the note.
"""
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse,json
from certify import Parameters,require,verify_sources
from prepare_layers import serializable
from search_network import log_integer_bounds
from complex_circuit import Checks,verify_role_frames
from complex_network import guard
from fast_gaussian import fast_constraints,fast_margins
from compact_control_layer import layer_exponents
from paired_complex import PairedComplex
from prime_field_circuit import check_global_producer
from prime_field_checks import matching,SmallProducer,scalar_control,frame_control

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(3,400000000)
COMPLEX_SAVING=Q(39,10**9)
KAPPA=Q(373,10**11)
H=28
BIT_ROLES=11840940
COMPLEX_ROLES=93838


def bit_counts(roles=BIT_ROLES,center_dimension=H-2):
    h=H;v=comb(h,5);m=h**3;N=v**3;c=comb(h,2);W=2*v*v*(v+roles)
    L=3*v*v*c*center_dimension;D=N-2*L
    require(D>0,'No bit rank deficit')
    return dict(h=h,v=v,m=m,N=N,roles=roles,retained_totals=c,W=W,L=L,D=D,s=W*m-D,eta=Q(D,W*m))


def complex_counts(c=None):
    h=H;v=comb(h,3);m=h**3;N=v**3;I=3*v*v;R=COMPLEX_ROLES if c is None else c.roles
    W=2*v*v*(v+R+h+1);L=I*h*(h+1);D=2*N-2*L
    n=dict(h=h,v=v,m=m,N=N,I=I,roles=R,W=W,L=L,D=D,s=W*m-D,eta=Q(D,W*m))
    additions=61022 if c is None else c.additions
    gates=I*(4*(additions+v)+4*v+4)
    require(gates<=12*W,'Complex scalar gate enclosure failed')
    n['scalar_gates']=gates
    return n


def parameters():
    return Parameters(tau=1-BIT_SAVING,sigma=1-COMPLEX_SAVING,
        epsilon=Q(4999,10000),c=Q(9999,10000),lam=1-Q(749,10**11),
        lamp=1-Q(748,10**11),kappa=KAPPA,beta=Q(19,25),delta=Q(1,10**6),C1=Q(19601,10000))


def witness(p=None,bn=None,cn=None):
    p=parameters() if p is None else p;bn=bit_counts() if bn is None else bn;cn=complex_counts() if cn is None else cn
    bit_log=Q(9997,1000);complex_log=Q(10)
    require(log_integer_bounds(bn['m'])[1]<bit_log,'Bit log upper bound failed')
    require(log_integer_bounds(cn['m'])[1]<complex_log,'Complex log upper bound failed')
    require(bn['eta']>(1-p.tau)*bit_log,'Unsupported bit exponent')
    require(cn['eta']>(1-p.sigma)*complex_log,'Unsupported complex exponent')
    g=guard(cn,p.beta,Q(1,10000));E=g['E'];W=cn['W'];s=cn['s']
    require(36*W**3+4*s+4*W+4<E,'Coefficient-depth enclosure failed')
    require(p.C1==g['C1'],'Guard exponent mismatch')
    exponents=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    constraints=fast_constraints(p)
    constraints['packed_overhead']=p.lam-exponents['internal']
    constraints['reserved_axes']=p.lamp-exponents['preprocessing']
    for name,slack in constraints.items():require(slack>0,'Constraint failed: '+name)
    margins=fast_margins(p)
    require(min(margins.values())>p.kappa,'No strict final absorption gap')
    return dict(parameters=asdict(p),bit=bn,complex=cn,guard=g,
        log_upper=dict(bit=bit_log,complex=complex_log),
        deficit_slacks=dict(bit=bn['eta']-(1-p.tau)*bit_log,complex=cn['eta']-(1-p.sigma)*complex_log),
        recurrence=exponents,constraints=constraints,margins=margins,
        minimum_margin=min(margins.values()),absorption_gap=min(margins.values())-p.kappa)


def certificate():
    producer=check_global_producer()
    require(producer['independent_template_check']['role_upper_bound']==BIT_ROLES,'Bit width mismatch')
    small=SmallProducer(8);small_map=small.verify_map();scalar=scalar_control(small);frames=frame_control(small)
    c=PairedComplex(H);checks=Checks(c)
    complex_check=dict(stats=c.stats(),map=checks.verify_map(),labels=checks.verify_labels(),roles=verify_role_frames(c,checks))
    require(c.roles==COMPLEX_ROLES,'Complex width mismatch')
    files=['scripts/paired_triple_circuit.py','scripts/prime_field_circuit.py','scripts/prime_field_supports.cpp',
        'scripts/prime_field_checks.py','scripts/paired_complex.py','scripts/prime_field_network.py',
        'notes/prime-field28-construction.tex']
    return dict(status='CONDITIONAL 373/10^11 > 2^-28 WITNESS; NOT FULL FORMAL VERIFICATION',
        upstream_commit=verify_sources(),producer=producer,matching=matching(),
        small_controls=dict(coefficients=small_map,all_dirty_basis=scalar,physical_frames=frames),
        complex_checks=complex_check,witness=witness(cn=complex_counts(c)),
        proof_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
        scope='Full h28 formal support counts and replacement boundary sums; full complex h28 '
              'coefficients, binary labels and compiled role frames; all scalar basis inputs and '
              'rational physical frames at h8. General tensor-stage, finite-alphabet and '
              'multiplication transfer rely on the written proof and retained upstream interfaces.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');a=p.parse_args()
    result=witness() if a.quick else certificate()
    if not a.quick:
        (ROOT/'certificates/prime-field28.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional 373/10^11 > 2^-28; margin',witness()['minimum_margin'],'gap',witness()['absorption_gap'])
