#!/usr/bin/env python3
"""Exact scoped obstructions for the unrealized higher-rank label target."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from certify import require
from search_network import log_ratio_bounds

ROOT=Path(__file__).resolve().parents[1]


def incidence_eigenvalues(h,t):
    """Eigenvalues of [C(|S intersect T|,t)] on the four Johnson levels."""
    return [comb(3-j,t-j)*comb(h-t-j,3-t) if j<=t else 0
            for j in range(4)]


def neighbor_spectrum(h):
    b1=incidence_eigenvalues(h,1);b2=incidence_eigenvalues(h,2)
    return [x-2*y+3 for x,y in zip(b1,b2)]


def log_rational_bounds(x):
    require(x>=1,'Positive logarithm required')
    power=0
    while x>=2:x/=2;power+=1
    lo2,hi2=log_ratio_bounds(Q(2))
    lo,hi=log_ratio_bounds(x)
    return power*lo2+lo,power*hi2+hi


def psd_ratio_lower(h):
    spectrum=neighbor_spectrum(h)
    z=spectrum[0];s=-min(spectrum[1:])
    require(s>0,'Need a negative nonconstant eigenvalue')
    return Q(z+s,s)


def psd_saving_bound(h):
    """Optimistic upper enclosure, all label ranks, stated shared-side counts."""
    v=comb(h,3);z=3*comb(h-3,2);x=psd_ratio_lower(h)
    if v<=6*h*x:return None
    W=2*v**3+2*v**3*z+3*v*v*h
    eta=Q(v*v)*(v-6*h*x)/(W*x**3)
    lo_num,hi_num=log_ratio_bounds(1/(1-eta),terms=4)
    lo_den,hi_den=log_rational_bounds(x**3)
    return lo_num/hi_den,hi_num/lo_den


def certificate():
    h=24;v=comb(h,3);k=2
    dims=[1,h-1,comb(h,2)-h,comb(h,3)-comb(h,2)]
    require(min(dims[2:])>2*h,'High harmonic levels would exceed rank 48')
    require(h!=9,'Constant affine eigenspace would vanish at h=9')
    ratio=psd_ratio_lower(h)
    require(ratio==Q(667,37),'Wrong PSD bound')
    intervals={h:b for h in range(6,200) if (b:=psd_saving_bound(h))}
    winner=max(intervals,key=lambda h:intervals[h][0])
    lo,hi=intervals[winner]
    require(winner==35,'Unexpected optimistic PSD winner')
    require(all(upper<lo for h,(lower,upper) in intervals.items() if h!=winner),
            'PSD optimistic intervals do not separate')
    # r/k > h/2, W>2Nz, eta<1/(2z(r/k)^3), log(r^3)>1.
    tail=Q(4,3*comb(197,2)*200**3-4)
    require(tail<lo,'PSD tail not excluded')
    kappa_upper=hi*hi/(20*(1-hi))
    require(kappa_upper<Q(1,2**67),'PSD family may reach 2^-67')
    return {
      'scope':'Scoped restrictions only; unrestricted indefinite rational labels remain unresolved',
      'target':{'h':24,'label_rank':2,'ambient_dimension':24},
      'intersection_only_blocks':{
        'scope':'Gram block depends only on triple intersection size in a common choice of block bases',
        'johnson_multiplicities':dims,'minimum_ambient_rank':48},
      'positive_definite_labels':{
        'scope':'Positive-definite ambient bilinear space; does not apply merely because each individual plane is positive inside an indefinite ambient space',
        'h24_ratio_lower':str(ratio),
        'h24_rank_two_dimension_lower':(k*ratio.numerator+ratio.denominator-1)//ratio.denominator,
        'all_h_all_label_ranks_scope':'Complete triple families, h central roles, three stages and stage-1/stage-3 side sharing, same downstream constraints; even odd h and nonintegral dimensions granted optimistically',
        'optimistic_winner_h':winner,'saving_upper':str(hi),
        'tail_h_start':200,'tail_saving_upper':str(tail),
        'kappa_upper':str(kappa_upper),'excludes_2^-67':True},
      'characteristic_two':{
        'scope':'Block fitting matrix over characteristic two, or rational matrix with regular mod-two reduction and invertible diagonal blocks after reduction',
        'ambient_rank_lower':(v*k+h-1)//h,
        'inequality':'h*r >= C(h,3)*k'},
      'coordinate_supported_planes':{
        'scope':'U_T contained in the three coordinate positions of T, form I-J/9',
        'feasible':False,'reason':'Neighbor pairing forces every plane to be the zero-sum plane, which is not orthogonal at neighbors'},
      'unrestricted_target_status':'OPEN: no construction or general nonexistence proof supplied'}


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/block-label-audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS scoped block-label audit: intersection-only, PSD, coordinate-local and characteristic-two routes excluded')
    print('Unrestricted indefinite rational rank-two target remains OPEN')
