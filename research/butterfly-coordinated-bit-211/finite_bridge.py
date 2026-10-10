"""Independent exact PR193 loose-bridge arithmetic; Apache-2.0.
Adapted from the reviewed PR193/PR187 composition with substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from math import prod

def validate_loose(f, cp, cm):
    m=cp['m'];h=cp['h'];v=cp['v'];half=m//2
    assert (m,h,v)==(66,22,1320) and max(cm['histogram'])==20 and 2*max(cm['histogram'])<m
    V=2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W=V*cp['W_per_vertex'];s=V*cp['rank_per_vertex'];r=max(cm['histogram'])
    assert V<2**5184 and cp['W_per_vertex']<10**7 and W<2**5208 and s<2**5215
    assert sum(t*n for t,n in cm['histogram'].items())==s//V==m*cp['W_per_vertex']-1320
    # These are193's deliberately loose bounds, not181's word-specific bill.
    sem=f['semantic'];power=lambda k:sem[k]['base']**sem[k]['exponent']
    assert sem['G']==dict(base=2,exponent=30000) and sem['E']==dict(base=2,exponent=100000)
    assert sem['C0']==dict(base=2,exponent=210000) and sem['B_upper']==dict(base=2,exponent=100001)
    G,E,C0=power('G'),power('E'),power('C0');Bnd=s+E
    K_upper=2**9300;route_upper=64*(m+1)**3*(K_upper+1)*(W+1)**2
    literal=2*G*W*W+8*s+4*W+4+32*m
    assert G>route_upper and E>literal and 2*Bnd*(m-r)-s-E>=1
    assert Bnd<power('B_upper') and C0>32*m*Bnd**2 and C0>2*Bnd+18
    assert sem['C1']==1 and sem['strict_literal_gap']==sem['induction_gap_lower']==1
    rows=f['rows'];assert rows['coefficient']==10000+9909+252==20161
    assert W.bit_length()<10000 and rows['degree']==10**6 and rows['suffix_slope']==4*10**6
    assert rows['degree_gap']==rows['degree']-Q(51,25)*rows['coefficient']>0
    return dict(vertices=V,W=W,total_rank=s,maxchild=r,halving_degree=1,wire_bits=W.bit_length(),
        local_groups_upper_power2=4096,logical_groups_upper_power2=9300,router_upper_bits=route_upper.bit_length(),
        literal_charge_bits=literal.bit_length(),actual_B_bits=Bnd.bit_length(),required_C0_bits=(32*m*Bnd**2).bit_length(),
        all_exact_semantic_dominances=True,scalar_denominator_divides=6,fixed_odd_divisor=3)
