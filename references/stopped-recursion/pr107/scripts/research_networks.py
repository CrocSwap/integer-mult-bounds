#!/usr/bin/env python3
"""Exact scoped screens for stronger bit networks; not a new construction."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

from certify import network, require
from search_network import saving_bounds, log_integer_bounds

ROOT = Path(__file__).resolve().parents[1]


def pair_common_neighbors(h, overlap):
    outside = h-6+overlap
    return overlap*comb(outside,2)+(3-overlap)**2*outside


def full_bit_search():
    intervals = {}
    for h in range(7,200):
        if h == 9:
            continue
        n=network(h)
        if n['N'] <= 2*n['Lb']:
            continue
        intervals[h] = saving_bounds(n,bit_only=True)
    winner=max(intervals,key=lambda h:intervals[h][0])
    lo,hi=intervals[winner]
    require(winner==46,'Unexpected full-triple optimum')
    require(all(lo>u for h,(l,u) in intervals.items() if h!=winner),
            'Full-triple intervals overlap')
    n=network(200)
    tail=Q(1,3*n['zb']*n['m']-1)
    require(tail<lo,'Unresolved full-triple tail')
    return intervals, {'winner_h':winner,'saving_lower':str(lo),'saving_upper':str(hi),
                       'finite_h_min':min(intervals),'finite_h_max':max(intervals),
                       'tail_start':200,'tail_upper':str(tail)}


def thinning_derivative_numerator(h,v):
    # eta_bound(v)=(v-B)/(h^3*(A*v^2+C*v+D)).
    A,B,C,D=Q(27,h),6*h*h,47-18*h,3*h
    return -A*v*v+2*A*B*v+C*B+D


def report():
    intervals,full=full_bit_search()
    lo,hi=intervals[46]
    n=network(46)
    v,z=n['v'],n['zb']
    common=max(pair_common_neighbors(46,k) for k in range(3))
    channels=v*z-(v-1)*common
    # For admissible h>=39, max common=(h-4)^2 and z/(z-common)<3.
    # Hence eta_tree<3 eta_full. Since eta_full<1/10,
    # (1-eta_full)^4 < 1-3 eta_full, giving a_tree<4 a_full.
    # eta_full<1/(3*z*m)<1/10 uniformly for h>=39.
    n39=network(39)
    require(Q(1,3*n39['zb']*n39['m'])<Q(1,10),'Need small deficit')
    hierarchy_a_upper=4*hi
    hierarchy_k_upper=hierarchy_a_upper**2/(20*(1-hierarchy_a_upper))
    require(hierarchy_k_upper<Q(1,2**70),'Hierarchy screen misses target')

    # Thinning: positivity requires v>6h^2. For h<=38 even all triples fail.
    require(comb(38,3)<=6*38**2,'Unexpected positivity threshold')
    for h in range(39,60):
        # Derivative decreases for v>B; positive at the upper endpoint is enough.
        require(thinning_derivative_numerator(h,comb(h,3))>0,
                'Need a finer thinning optimizer')
        require(intervals[h][1] <= hi,'Unexpected finite thinning winner')
    # E1/v >= 9v/h -6h+15 > 8v/h for v>6h^2.
    # eta < (v-B)/(24 v^2 h^2) <= 1/(576 h^4).
    # log(h^3)>10 for h>=60, certified at 60.
    require(log_integer_bounds(60**3)[0]>10,'Need tail log bound')
    thinning_tail=Q(1,10*(576*60**4-1))
    require(thinning_tail<lo,'Thinning tail unresolved')

    D=n['N']-2*n['Lb']
    require(D<2*n['Wb'],'Reuse criterion not applicable')
    return {
      'scope':'Scoped upper bounds and rejection criteria; no new network or kappa certificate',
      'full_triples_bit_only':full,
      'hierarchical_aggregation':{
        'scope':'One shared binary source hierarchy, pure-neighbor channels, original counts and no smaller central losses',
        'h46_max_pair_common_neighbors':common,
        'h46_side_channels_lower':channels,
        'h46_side_channel_factor_upper':str(Q(v*z,channels)),
        'all_h_primitive_saving_upper':str(hierarchy_a_upper),
        'all_h_kappa_upper_current_constraints':str(hierarchy_k_upper),
        'excludes_2^-70':True},
      'triple_subfamilies':{
        'scope':'Any subfamily of triples retaining h-dimensional label space, h central wires, three original stages and per-edge side wires',
        'edge_lower_bound':'9*v^2/h - 6*v*h + 15*v',
        'finite_h_range':[39,59], 'finite_max_at_full_family':True,
        'tail_h_start':60,'tail_saving_upper':str(thinning_tail),
        'winner_h':46,'saving_upper':str(hi)},
      'reuse_rejection':{
        'scope':'Remove r wires while adding at least r backward dimensions, with N and m fixed',
        'h46_D_over_W':str(Q(D,n['Wb'])),
        'D_less_than_2W':True,
        'condition':'New relative deficit <= old relative deficit whenever D <= 2W'}}


if __name__=='__main__':
    result=report()
    out=ROOT/'certificates/network-research.json'
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('Certified: shared-hierarchy screen excludes 2^-70; thinning cannot beat full h=46.')
