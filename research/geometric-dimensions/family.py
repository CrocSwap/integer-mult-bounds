"""Exact obstructions within the retained-center, c+Q compiler architecture.

These are NOT lower bounds for arbitrary multiplication algorithms or motifs.
"""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from search_network import log_integer_bounds

TARGET=F(761,10**11)


def saving_upper(eta,m):
    assert 0 <= eta < 1
    return eta/((1-eta)*log_integer_bounds(m)[0])


def cap(q,h,output_factor=1,retain_loss=True):
    r,t=2*q-1,q-1
    v=comb(h,r)
    outputs=comb(h,t)*(comb(h-t,q)+1)
    deficit=v-6*comb(h,t)*(h-t) if retain_loss else v
    if deficit<=0:return F(0)
    eta=F(deficit,2*h**3*(v+output_factor*outputs))
    return saving_upper(eta,h**3)


def tail_cap(q,h,output_factor=1):
    # Drop positive retained losses and total outputs. This decreases the
    # denominator and increases the numerator, hence gives an upper bound.
    eta=F(1,2*h**3*(1+output_factor*comb(2*q-1,q-1)))
    return saving_upper(eta,h**3)


def checks():
    identities=[]
    for p,a in [(2,1),(3,1),(2,2),(5,1),(7,1),(2,3),(3,2),(2,4)]:
        q=p**a
        values=[(comb(j,q-1)-int(j==q-1))%p for j in range(2*q)]
        assert values==[int(j==2*q-1) for j in range(2*q)]
        identities.append(dict(p=p,a=a,q=q,all_intersection_coefficients_exact=True))
    # For q=5, h=14 has negative deficit; from h=15 every boundary output
    # is distinct and nontrivial, so additions >= outputs and R >= 2 outputs.
    assert cap(5,14)==0
    stop=15
    while tail_cap(5,stop,2)>=TARGET:stop+=1
    rows=[dict(h=h,upper=cap(5,h,2)) for h in range(15,stop)]
    best=max(rows,key=lambda row:row['upper'])
    assert best['upper']<TARGET and tail_cap(5,stop,2)<TARGET
    # For q>=7, h>=3q-1>=20 and C(2q-1,q-1)>=C(13,6).
    # Both monotone quantities only improve this upper bound.
    all_large=tail_cap(7,20)
    assert all_large<TARGET
    assert cap(4,27,2)>TARGET, 'These bounds must not exclude the q=4 case.'
    return dict(target_bit_saving=TARGET,identities=identities,
                q5=dict(finite_dimensions=rows,largest_finite_upper=best,
                        tail_starts_at=stop,tail_upper=tail_cap(5,stop,2)),
                every_prime_power_at_least_seven_upper=all_large,
                status='ARCHITECTURE-SPECIFIC OBSTRUCTION; NOT A GENERAL LOWER BOUND')


if __name__=='__main__':
    print(json.dumps(checks(),indent=2,default=str))
