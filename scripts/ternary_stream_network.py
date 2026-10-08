#!/usr/bin/env python3
"""Conditional assembly for the smaller producer with nested delivery reuse."""
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
from math import ceil
import argparse
import json

from certify import require
from prepare_layers import serializable
from prime_field_network import bit_counts, complex_counts, parameters as original_parameters
from fast_gaussian import fast_margins
from search_network import log_integer_bounds
from experiments.assembly_breakthrough_guard import RHO, ZETA, research_witness
from experiments.ternary_target_certify import file_hash

ROOT=Path(__file__).resolve().parents[1]
ROLES=8771396
GRID=10**12
BIT_LOG=Q(9997,1000)


def strict_grid_below(value):
    return Q(ceil(value*GRID)-1,GRID)


def parameters(roles=ROLES):
    saving=strict_grid_below(bit_counts(roles)['eta']/BIT_LOG)
    beta=Q(1,1000)
    p=replace(original_parameters(),tau=1-saving,lam=1-saving+Q(1,GRID),
              lamp=1-saving+Q(2,GRID),beta=beta,C1=beta+(1-beta)*RHO+ZETA)
    return replace(p,kappa=strict_grid_below(min(fast_margins(p).values())))


def witness(roles=ROLES,p=None):
    p=parameters(roles) if p is None else p
    bn,cn=bit_counts(roles),complex_counts()
    require(log_integer_bounds(bn['m'])[1]<BIT_LOG,'Bit logarithm bound failed')
    require(log_integer_bounds(cn['m'])[1]<10,'Complex logarithm bound failed')
    require(bn['eta']>(1-p.tau)*BIT_LOG,'Unsupported bit saving')
    require(cn['eta']>(1-p.sigma)*10,'Unsupported complex saving')
    result=research_witness(n=cn,parameters=p)
    g=result['guard'];W,s=cn['W'],cn['s']
    require(36*W**3+4*s+4*W+4<g['E'],'Coefficient-depth enclosure failed')
    result.update(status='CONDITIONAL NESTED-WIRE ASSEMBLY; NOT FORMAL VERIFICATION',
                  bit=bn,complex=cn,log_upper=dict(bit=BIT_LOG,complex=Q(10)),
                  deficit_slacks=dict(bit=bn['eta']-(1-p.tau)*BIT_LOG,
                                      complex=cn['eta']-(1-p.sigma)*10),
                  scope='Nested delivery compiler, unchanged ternary tensor stages and complex '
                        'network, dependency-path guard and inherited multiplication interfaces.')
    return result


def certificate(producer):
    require(producer['global_roles']['current']==ROLES,'Unexpected producer role count')
    require(producer['global_roles']['center_loss']==9828,'Unexpected center loss')
    require(producer['global_roles']['extra_frame_loss']==0,'Unaccounted frame loss')
    from experiments.ternary_direction import paired_guard_control
    paths=('scripts/ternary_stream_network.py','scripts/prime_field_network.py',
           'scripts/fast_gaussian.py','scripts/compact_control_layer.py',
           'scripts/experiments/assembly_breakthrough_guard.py',
           'scripts/experiments/ternary_direction.py','docs/research/assembly-breakthrough.md',
           'docs/research/ternary-depth.md')
    return dict(status='CONDITIONAL NESTED-WIRE MULTIPLICATION WITNESS',
                producer=producer,paired_complex_guard=paired_guard_control(),
                witness=witness(),proof_sha256={p:file_hash(ROOT/p) for p in paths})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--quick',action='store_true',help='Arithmetic only; no certificate writes')
    p.add_argument('--workdir',type=Path)
    args=p.parse_args()
    if not args.quick:
        from experiments.ternary_stream_certify import certificate as producer_certificate
        producer=producer_certificate(args.workdir)
        records={'ternary-stream-producer.json':producer,
                 'ternary-stream-witness.json':certificate(producer)}
        for name,value in records.items():
            (ROOT/'certificates'/name).write_text(json.dumps(serializable(value),sort_keys=True,indent=2)+'\n')
    result=witness()
    print('PASS conditional',result['parameters']['kappa'],'; roles',ROLES,
          '; minimum margin',result['minimum_margin'],'; gap',result['absorption_gap'])
