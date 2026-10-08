#!/usr/bin/env python3
"""Exact role budgets for the controlled batched recurrence, not a circuit.

Upper moments give sufficient arithmetic budgets; lower moments give necessary
budgets. Neither provides a producer, matching, or a multiplication witness.
"""
from fractions import Fraction as Q
from math import ceil
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'references/pr10/scripts'))
from controlled_bit_rank_moment import counts
from search_network import log_integer_bounds
from prepare_layers import serializable

START=Q(1624,10**12)


def unnormalized_gap(h,roles,a,bound,source_frames=False):
    n=counts(h=h,roles=roles);m=n['m']
    blocks=n['recursive_blocks']
    widths=[1]+[row['chunk_digits'] for row in blocks]
    masses=[n['singleton_calls']]+[row['chunk_digits']*row['copies'] for row in blocks]
    if source_frames:
        from source_frame_stream_network import bit_counts
        relocated=bit_counts(h,roles)
        widths=[1]+[row['width'] for row in relocated['recursive_blocks']]
        masses=[relocated['singleton_calls']]+[
            row['width']*row['copies'] for row in relocated['recursive_blocks']]
    value=Q(0)
    ml,mh=log_integer_bounds(m)
    for width,mass in zip(widths,masses):
        low,high=log_integer_bounds(width)
        if bound=='upper':
            ell=Q(ceil((mh-low)*10**9),10**9)
            assert 0<=a*ell<1
            term=1/(1-a*ell)
        elif bound=='lower':
            ell=Q(((ml-high)*10**9).__floor__(),10**9)
            assert ell>=0
            term=1+a*ell  # exp(t)>=1+t; positive t makes this strict.
        else:
            raise ValueError('Expected upper or lower')
        value+=mass*term
    return value-n['W']*m


def budget(h,kappa,source_frames=False):
    # The assembly needs a_b>2*kappa, so this is deliberately favorable.
    a=2*kappa
    thresholds={}
    for bound in ('upper','lower'):
        intercept=unnormalized_gap(h,0,a,bound,source_frames)
        slope=unnormalized_gap(h,1,a,bound,source_frames)-intercept
        assert slope>0
        root=-intercept/slope
        if bound=='upper':
            thresholds['certified_role_budget']=max(-1,ceil(root)-1)
        else:
            thresholds['first_excluded_roles']=max(0,ceil(root))
        thresholds[bound+'_zero_role_gap']=intercept
    sufficient=thresholds['certified_role_budget']
    excluded=thresholds['first_excluded_roles']
    assert sufficient<excluded
    if sufficient>=0:
        assert unnormalized_gap(h,sufficient,a,'upper',source_frames)<0
        assert unnormalized_gap(h,sufficient+1,a,'upper',source_frames)>=0
    assert unnormalized_gap(h,excluded,a,'lower',source_frames)>=0
    if excluded:
        assert unnormalized_gap(h,excluded-1,a,'lower',source_frames)<0
    n=counts(h=h,roles=0)
    return dict(h=h,target_kappa=kappa,favorable_bit_saving=a,source_frames=source_frames,
                output_floor=n['v']+h*(h-1)//2,
                **thresholds)


def certificate():
    # Positive deficit starts at h=23. At R=0, the singleton rank mass is
    # >=(2h^2+2h-5/2)/h^3 and eta<=1/(2h^3). Thus kappa<a_b/2 forces
    # kappa<1/[2(4h^2+4h-5) log(h^3)]. This decreases with h.
    target=10000*START
    excluded=[]
    for h in range(23,100):
        gap=unnormalized_gap(h,0,2*target,'lower')
        assert gap>0
        excluded.append(h)
    assert log_integer_bounds(100**3)[0]>13
    tail=Q(1,2*(4*100**2+4*100-5)*13)
    assert tail<target
    return dict(status='BATCHED ROLE BUDGET SCREEN; NO NEW WITNESS',
                cases={str(h):{str(f):budget(h,f*START) for f in (100,1000,10000)}
                       for h in (26,28,30,32)},
                source_frame_cases={str(h):{str(f):budget(h,f*START,True) for f in (100,1000,10000)}
                       for h in (26,28,30,32)},
                ten_thousand_factor_exclusion=dict(target_kappa=target,
                    nonpositive_deficit_through_h=22,exactly_excluded_h=excluded,
                    tail_from_h=100,tail_kappa_upper=tail,auxiliary_roles_made_free=True),
                scope='Fixed three-stage geometry, unchanged center losses, four controlled '
                      'recursive block classes (or PR #13 source relocation), and kappa<a_b/2. All roles and all internal '
                      'frame costs still require a construction. An upper-bound failure is '
                      'not an impossibility; the separate lower moment proves exclusions.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path)
    args=p.parse_args();result=certificate()
    if args.output:args.output.write_text(json.dumps(serializable(result),sort_keys=True,indent=2)+'\n')
    for h,rows in result['cases'].items():
        print(h,{f:(r['certified_role_budget'],r['first_excluded_roles']) for f,r in rows.items()})
    for h,rows in result['source_frame_cases'].items():
        print('source frames',h,{f:(r['certified_role_budget'],r['first_excluded_roles']) for f,r in rows.items()})
