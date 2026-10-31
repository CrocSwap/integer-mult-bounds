#!/usr/bin/env python3
"""Exact conditional witness for sharing across common-point groups."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from certify import A, LOG_BOUND, Parameters, certify_parameters, require, verify_sources
from search_network import log_integer_bounds
from shared_point_circuit import SharedPointCircuit

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(203,10**11)
KAPPA=Q(13,2**66)


def counts(h=46,circuit=None):
    require(h>=6 and h%2==0,'Even ground size required')
    c=circuit or SharedPointCircuit(h)
    require(c.h==h,'Mismatched circuit')
    v=comb(h,3);N=v**3;m=h**3;R=c.additions+len(c.outputs)
    W=2*N+2*v*v*(R+h);L=3*v*v*h*h;D=N-2*L
    return dict(h=h,v=v,N=N,m=m,side_roles_per_invocation=R,
                W=W,L=L,D=D,s=W*m-D,eta=Q(D,W*m))


def parameters():
    a=BIT_SAVING
    return Parameters(1-a,1-A,Q(1,21),9*a/10,1-19*a*a/20,
                      1-9*a*a/10,KAPPA,beta=Q(9,10))


def certificate():
    c=SharedPointCircuit(46);n=counts(circuit=c)
    symbolic=c.verify();frames=c.verify_frames()
    _,log_hi=log_integer_bounds(n['m'])
    require(log_hi<LOG_BOUND and n['eta']>BIT_SAVING*LOG_BOUND,'Insufficient saving')
    witness=certify_parameters(parameters(),generalized_beta=True,strict_margin=True,
                               layout_model='nonadjacent')
    require(Q(witness['minimum_margin'])==3*BIT_SAVING**2/70,'Wrong minimum')
    # Necessary bound for this particular circuit and downstream constraints.
    log_lo,_=log_integer_bounds(n['m'])
    a_upper=n['eta']/((1-n['eta'])*log_lo)
    ceiling=a_upper*a_upper/(20*(1-a_upper))
    require(ceiling<Q(1,2**62),'Unexpected crossing of 2^-62')
    # Sufficient role budget for a future 2^-59 witness with the same recipe.
    target_a=Q(64,10**10)
    require(3*target_a**2/70>Q(1,2**59),'Invalid target saving')
    budget=n['D']/(2*n['v']**2*n['m']*target_a*LOG_BOUND)-n['v']-n['h']
    return dict(status='CONDITIONAL 13*2^-66 WITNESS; frame-transfer proof supplied separately',
                upstream_commit=verify_sources(),bit_counts={k:str(v) for k,v in n.items()},
                circuit=symbolic,frames=frames,bit_saving=str(BIT_SAVING),
                complex_saving_unchanged=str(A),log_m_upper=str(LOG_BOUND),
                deficit_slack=str(n['eta']-BIT_SAVING*LOG_BOUND),witness=witness,
                exact_circuit_kappa_upper=str(ceiling),
                target_59=dict(bit_saving=str(target_a),
                               sufficient_maximum_integer_side_roles=(budget.numerator-1)//budget.denominator),
                scope='Conditional on the written source-span/complement-frame transfer and unchanged upstream interfaces; no general optimality claim.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/shared-point-network.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS conditional shared-point witness 13*2^-66; minimum',result['witness']['minimum_margin'])
    print(result['bit_counts'])
    print('Target 59:',result['target_59'])
