#!/usr/bin/env python3
"""Bounded and exact screens of alternative bit-network counting families."""
from fractions import Fraction as Q
from functools import lru_cache
from math import comb, log, log1p
from pathlib import Path
import json

from certify import A, require
from research_networks import full_bit_search
from search_network import log_integer_bounds,log_ratio_bounds

ROOT=Path(__file__).resolve().parents[1]


def unequal_counts(hs):
    vs=[comb(h,3) for h in hs]
    zs=[3*comb(h-3,2) for h in hs]
    N=vs[0]*vs[1]*vs[2]
    m=hs[0]*hs[1]*hs[2]
    W=N*(2+sum(zs))+sum((N//v)*h for h,v in zip(hs,vs))
    L=sum((N//v)*h*h for h,v in zip(hs,vs))
    return N,m,W,N-2*L


@lru_cache(maxsize=None)
def log_bounds(m):return log_integer_bounds(m)


def unequal_search():
    intervals,baseline=full_bit_search()
    best_lo,best_hi=intervals[46]
    require(log_integer_bounds(36**3)[0]>10,'Need global logarithm lower bound')
    visited=positive=coarse_rejected=0
    survivors=[]
    runner_hi=Q(0);runner=None
    items=[(h,comb(h,3),3*comb(h-3,2)) for h in range(15,300)]
    for i,(h,v,z) in enumerate(items):
        for j in range(i,len(items)):
            H,V,Z=items[j]
            for hh,vv,zz in items[j:]:
                visited+=1
                N=v*V*vv
                D=N-2*(V*vv*h*h+v*vv*H*H+v*V*hh*hh)
                if D<=0:continue
                positive+=1
                W=N*(2+z+Z+zz)+V*vv*h+v*vv*H+v*V*hh
                m=h*H*hh
                # a < eta/(10*(1-eta)); exact integer rejection against A.
                if A.denominator*D < 10*A.numerator*(m*W-D):
                    coarse_rejected+=1;continue
                eta=Q(D,m*W)
                lo_num,hi_num=log_ratio_bounds(1/(1-eta),terms=3)
                lo_den,hi_den=log_bounds(m)
                upper=hi_num/lo_den
                hs=(h,H,hh)
                if hs!=(46,46,46):
                    require(upper<best_lo,f'Unequal candidate survives: {hs}')
                    if upper>runner_hi:runner_hi,runner=upper,hs
                survivors.append(hs)
    # Positive deficit forces h_i>=15 and m>36^3. If H=max h_i>=300,
    # eta<1/(225 H z(H)); this decreasing upper bound excludes the tail.
    tail=Q(1,10*(225*300*3*comb(297,2)-1))
    require(tail<best_lo,'Unresolved unequal tail')
    return {'scope':'Original per-edge side wires and three tensor stages; unequal complete-triple ground-set sizes',
            'winner':[46,46,46],'saving_lower':str(best_lo),'saving_upper':str(best_hi),
            'finite_ground_sizes':[15,299],'unordered_triples_examined':visited,
            'positive_deficit_cases':positive,'coarse_exact_rejections':coarse_rejected,
            'log_enclosure_cases':len(survivors),
            'runner_up':runner,'runner_up_saving_upper':str(runner_hi),
            'tail_max_ground_size_start':300,'tail_saving_upper':str(tail)}


def odd_subset_screen():
    """Optimistic scores, not construction certificates or infinite-family bounds.

    Hypothesize rational label dimension r at least C(h,t)-C(h,t-1),
    the top harmonic multiplicity for a degree-t Johnson kernel. We use that
    favorable dimension, retain h central wires and three stages, and count all
    odd-intersection neighbors. A survivor would still need its frame proof.
    """
    rows=[]
    for k in range(5,16,2):
        t=(k-1)//2
        best=None
        for h in range(k+1,500):
            v=comb(h,k);r=comb(h,t)-comb(h,t-1)
            z=sum(comb(k,j)*comb(h-k,k-j) for j in range(1,k,2) if h-k>=k-j)
            D=v-6*h*r
            if D<=0 or not z:continue
            eta=Q(D,r**3*(2*v+3*v*z+3*h))
            # Floating-point scores only locate the finite range's winner.
            score=-log1p(-float(eta))/log(r**3)
            if best is None or score>best[0]:best=(score,h,r,v,z,eta)
        if best is None:continue
        score,h,r,v,z,eta=best
        num_lo,num_hi=log_ratio_bounds(1/(1-eta),terms=3)
        den_lo,den_hi=log_integer_bounds(r**3)
        rows.append({'subset_size':k,'ground_sizes_checked':[k+1,499],
                     'selected_ground_size':h,
                     'optimistic_label_dimension':r,'vertices':v,'neighbors':z,
                     'selected_score_lower':str(num_lo/den_hi),
                     'selected_score_upper':str(num_hi/den_lo)})
    return {'scope':'Exploratory bounded scores with a favorable assumed label dimension; no new network or all-h impossibility claim',
            'cases':rows}


if __name__=='__main__':
    result={'unequal_factors':unequal_search(),'higher_odd_subsets':odd_subset_screen()}
    (ROOT/'certificates/network-variants.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS exact unequal-factor search:',result['unequal_factors']['winner'])
    for row in result['higher_odd_subsets']['cases']:
        print('Exploratory subset size',row['subset_size'],
              'selected ground size',row['selected_ground_size'])
