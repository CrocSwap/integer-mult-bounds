#!/usr/bin/env python3
"""Arithmetic design targets only: the requisite block labels are NOT known."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from certify import A, Parameters, certify_parameters, require
from search_network import log_integer_bounds

ROOT=Path(__file__).resolve().parents[1]


def hypothetical_counts(h,r,k):
    """Assume nondegenerate k-subspaces in dimension r, orthogonal at neighbors.

    Retain the scalar incidence network and share stage-1/stage-3 side roles.
    This function neither constructs nor certifies the assumed subspaces.
    """
    require(h>=6 and h%2==0 and 0<k<=r,'Invalid hypothetical dimensions')
    v=comb(h,3);z=3*comb(h-3,2);N=v**3;m=r**3
    W=2*N+2*N*z+3*v*v*h
    L=3*v*v*h*r*k*k
    D=N*k**3-2*L
    return dict(h=h,r=r,k=k,v=v,z=z,N=N,m=m,W=W,L=L,D=D,
                eta=Q(D,W*m))


def target():
    n=hypothetical_counts(24,24,2)
    a=Q(7,10**9)
    _,log_hi=log_integer_bounds(n['m'])
    require(n['eta']>a*log_hi,'Hypothetical target is too weak')
    p=Parameters(1-a,1-A,Q(1,21),9*a/10,1-19*a*a/20,
                 1-9*a*a/10,Q(1,2**59),beta=Q(9,10))
    arithmetic=certify_parameters(p,generalized_beta=True,strict_margin=True,
                                  layout_model='nonadjacent')
    require(Q(arithmetic['minimum_margin'])==Q(21,10**19),'Wrong target margin')
    # An 11-clique of triples through one common point is an immediate test.
    clique=(24-1)//2
    require(clique*2<=24,'Sunflower clique already excludes target')
    return {
      'status':'UNREALIZED DESIGN TARGET: no block-label construction is supplied',
      'missing_hypothesis':'2024 nondegenerate rational two-dimensional subspaces in a 24-dimensional nondegenerate symmetric bilinear space; orthogonal whenever the indexing triples intersect in one point',
      'hypothetical_counts':{k:str(v) for k,v in n.items()},
      'hypothetical_bit_saving':str(a),'log_m_upper':str(log_hi),
      'deficit_slack':str(n['eta']-a*log_hi),
      'hypothetical_parameter_check':arithmetic,
      'clique_dimension_lower_bound':clique*2,
      'scope':'Arithmetic implication of a missing representation and the written higher-rank transfer argument; not a multiplication result or feasibility certificate'}


if __name__=='__main__':
    result=target()
    (ROOT/'certificates/block-label-target.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('ARITHMETIC TARGET ONLY: hypothetical rank-two labels would support 2^-59; construction missing')
