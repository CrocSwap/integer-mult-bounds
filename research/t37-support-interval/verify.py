#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Charles Bethin, with substantial OpenAI Codex assistance.
"""Exact finite certificates for the sharp T37 rank-one support interval.

The continuum argument is in README.md. This program enumerates every bin
count vector and proves its finite premises with integer radical bounds.
No moment engine or producer enumeration is imported.
"""
from fractions import Fraction as Q
from itertools import product
import argparse
import hashlib
import json
from pathlib import Path

WIDTHS=(4,5,7,8,9)
PRICES=(-1,-20,-8,-2,4)
HELPERS=(80,32,54,122,216)
CAPS=(8,16,32,48)
BINS=(672,448,448,448)
BONUSES=(2,4,8,-13)
SCALE=1 << 128
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def nth_root_floor(n,k):
    need(n>=0 and k>=1,'root domain')
    lo,hi=0,1 << ((n.bit_length()+k-1)//k)
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid**k<=n:lo=mid
        else:hi=mid
    return hi if hi**k<=n else lo


def power_bounds(x,b):
    x,b=Q(x),Q(b)
    need(x>0 and b>0,'power domain')
    n=x.numerator**b.numerator*SCALE**b.denominator
    d=x.denominator**b.numerator
    q=nth_root_floor(n//d,b.denominator)
    need(q**b.denominator*d<=n<(q+1)**b.denominator*d,'root enclosure')
    return Q(q,SCALE),Q(q+1,SCALE)


def support_bounds(r,v,b):
    # F_r(b)=925*r*((48/r)^b-1)-v*(48^b-1).
    al,au=power_bounds(Q(48,r),b)
    bl,bu=power_bounds(Q(48),b)
    return (925*r*(al-1)-v*((bu if v>=0 else bl)-1),
            925*r*(au-1)-v*((bl if v>=0 else bu)-1))


def enumerate_bins(prices=PRICES):
    upper={};witness={};count=0
    for cap,bonus in zip(CAPS,BONUSES):
        for vector in product(*(range(cap//w+1) for w in WIDTHS)):
            fill=sum(w*n for w,n in zip(WIDTHS,vector))
            if fill>cap:continue
            count+=1
            r=cap-fill
            score=bonus+sum(p*n for p,n in zip(prices,vector))
            if r not in upper or score>upper[r]:
                upper[r]=score;witness[r]=(cap,vector)
    return upper,witness,count


def relaxed_member(profile,replicas,upper):
    need(type(replicas) is int and replicas>0,'positive replica count')
    need(all(r in upper and type(n) is int and n>=0 for r,n in profile.items()),'relaxed count domain')
    need(sum(profile.values())==2016*replicas,'relaxed bin count')
    need(sum(r*n for r,n in profile.items())==14382*replicas,'relaxed mass')
    need(sum((48*upper[r]+13*r)*n for r,n in profile.items())>=150*replicas,'relaxed credit')
    return True


def certify(upper,count):
    need(count==1163,'complete count-vector inventory')
    mass=sum(c*n for c,n in zip(CAPS,BINS))-9*sum(w*n for w,n in zip(WIDTHS,HELPERS))
    price=sum(n*p for n,p in zip(BINS,BONUSES))+9*sum(n*p for n,p in zip(HELPERS,PRICES))
    need((mass,price)==(14382,-3892),'fixed family totals')
    need((upper[0],upper[1],upper[32],upper[48])==(0,19,8,-13),'support anchors')
    credits={r:48*u+13*r for r,u in upper.items()}
    need(48*price+13*mass==150,'credit demand')
    # At b=2/3 every non-anchor rank except 32 remains strictly above support.
    margins={r:support_bounds(r,credits[r],Q(2,3)) for r in upper if 0<r<48 and r not in (1,32)}
    need(all(lo>0 for lo,hi in margins.values()),'noncritical rank at two thirds')
    left=support_bounds(32,800,Q(16,25))
    right=support_bounds(32,800,Q(13,20))
    need(left[0]>0 and right[1]<0,'sharp root bracket')
    # A relaxed countermodel, not a packing or physical construction.
    alternative={32:3,48:4792}
    need(sum(r*n for r,n in alternative.items())==16*mass,'alternative mass')
    need(sum(upper[r]*n for r,n in alternative.items())==16*price,'alternative signed equality')
    need(sum(credits[r]*n for r,n in alternative.items() if r<48)==16*150,'alternative credit equality')
    need(relaxed_member({**alternative,0:27461},16,upper),'alternative zero-bin completion')
    need(relaxed_member({0:63500,1:6,48:11086},37,upper),'T37 realization of relaxation')
    return dict(status='PASS_SHARP_T37_SUPPORT_INTERVAL',bin_vectors=count,attainable_ranks=sorted(upper),
                upper=upper,credits=credits,mass_per_replica=mass,signed_price_per_replica=price,
                critical_equation='37*(3/2)^b - 48^b - 36 = 0; unique positive root',
                root_bracket=['16/25','13/20'],critical_lower_margin=str(left[0]),critical_upper_margin=str(right[1]),
                noncritical_at_two_thirds={r:str(x[0]) for r,x in sorted(margins.items())},
                normalized_optimum={'1':'6/37','48':'11086/37'},
                strict_equality_replicas='positive multiples of 37 for 0 < b < b_star',
                countermodel=dict(replicas=16,idle=alternative,physical_feasibility='not asserted'),
                scope='Sharp parameter range of the inherited signed-dual relaxation. The continuum proof, hypotheses, and equality cases are in README.md. No new kappa, physical optimum beyond the interval, or multiplication theorem.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    need(not a.out.exists(),'output preservation')
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in pins.items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source drift: '+name)
    u,w,n=enumerate_bins();result=certify(u,n)
    result['source_sha256']=pins
    result['maximizing_patterns']={r:dict(capacity=c,counts=v) for r,(c,v) in sorted(w.items())}
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],'bins=1163','critical_rank=32','16/25 < b_star < 13/20')

if __name__=='__main__':main()
