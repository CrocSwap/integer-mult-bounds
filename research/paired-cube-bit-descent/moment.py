#!/usr/bin/env python3
"""Retained PR161 bit word, exact paid moment and positive atom toll.

Checks supplied graph/frame inputs and all formal columns without executing
the foreign producer. The analytic weighted-compiler contracts are retained.
"""
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.dont_write_bytecode=True
from word import Candidate,need
from interval_moment import moment,log_interval,exp_interval


def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x


def paid_moment(p,a,details=False):
    raw=moment(p,a,details);m,w=p['m'],p['W']
    count=sum(p['child_multiplicities'].values());bad=Q(1,10**16);fallback=32*m*m
    ll,lu=log_interval(Q(m));el,eu=exp_interval(a*ll,a*lu)
    weight=bad*Q(fallback*count,w*m)
    return dict(saving=a,lower=raw['lower']+weight*el,upper=raw['upper']+weight*eu,
        strict_gap_lower=1-raw['upper']-weight*eu,raw=raw,fallback_lower=weight*el,
        fallback_upper=weight*eu,edge_count=count,fallback_children_per_edge=fallback,
        bad_fraction=bad)


def certify(row):
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    grid=10**18;lo=0;hi=grid//100
    need(paid_moment(p,Q(lo,grid))['upper']<1,'zero-saving rank contraction')
    need(paid_moment(p,Q(hi,grid))['lower']>1,'upper bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;r=paid_moment(p,Q(mid,grid))
        if r['upper']<1:lo=mid
        elif r['lower']>1:hi=mid
        else:raise ValueError('increase moment precision')
    coarse=Q(lo,grid);accepted=paid_moment(p,coarse,True);rejected=paid_moment(p,Q(hi,grid),True)
    need(accepted['upper']<1<rejected['lower'],'adjacent grid paid-moment proof')
    old=Q(384599,10**10);threshold=coarse/(1+coarse-old);atomgrid=10**24
    floor=(threshold*atomgrid).numerator//(threshold*atomgrid).denominator
    atom=Q(floor+1,atomgrid);actual=(1-atom)*coarse+atom*old
    need(actual<atom<1-actual,'paid atom and row adapter toll')
    need(Q(2*p['m']**3,2**80)<Q(1,10**16),'fixed prime rare-class bound')
    need(Q(p['total_rank'])+accepted['bad_fraction']*accepted['fallback_children_per_edge']*accepted['edge_count']<p['W']*p['m'],'contaminated mass contracts')
    previous=atom-Q(1,atomgrid)
    need(previous<=(1-previous)*coarse+previous*old,'previous atom grid does not pay strict toll')
    return dict(coarse_saving=coarse,accepted=accepted,rejected=rejected,coarse_grid=grid,
        atom_beta=atom,old_atom_saving=old,ordinary_saving=actual,atom_threshold=threshold,
        atom_grid=atomgrid,atom_lower_gap=atom-actual,atom_upper_gap=1-actual-atom,
        controls=dict(next_coarse_grid_rejected=True,previous_atom_grid_rejected=True),
        scope='Adjacent coarse exclusion for this fixed worst-case bad-class envelope and least atom on the stated grid; no true bad-fraction or global optimality claim.')
