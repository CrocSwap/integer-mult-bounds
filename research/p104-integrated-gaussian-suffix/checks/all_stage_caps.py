"""Bound every allowed 1..7-stage terminal word under the fixed resource clock."""
from fractions import Fraction as Q
from decimal import Decimal,getcontext
from pathlib import Path
import json
# The trial values are the literal dyadics in both pinned installations.
GAUSSIAN_C=Q(17145637307,2**42)
BINARY_C=Q(4391986206293,2**50)
ETA=Q(39,10000)
def dec(x,places):
    getcontext().prec=60
    return format(Decimal(x.numerator)/Decimal(x.denominator),f".{places}f")

M=524288
m=8192
A=Q(249,250)
raw=BINARY_C
moment=lambda b,d:raw-d/b
stop=Q(5,10**18)

def relax(heights,d):
    return A*sum(moment(b,d)*Q(1,250)**(len(heights)-i-1) for i,b in enumerate(heights))

def cubic_bound(S,d):
    h=(m,S-m-M,M)
    assert m<=h[1]<=M
    w=(Q(1,62500),Q(1,250),Q(1))
    a,b,c=[x/y**2 for x,y in zip(w,h)]
    assert a<b<c
    # Concavity and feasible signs: sum displacements <=0, first nonnegative,
    # last nonpositive, hence sum slope_i*displacement_i<=0.
    return h,relax(h,d)

def compute(resource,ord_debit,g_debit,ceiling):
    # A strict global gain requires a positive cap strictly above ceiling+stop.
    ig=(g_debit/(GAUSSIAN_C-ceiling-stop)).__floor__()+1
    assert GAUSSIAN_C-g_debit/(ig-1)-stop<=ceiling<GAUSSIAN_C-g_debit/ig-stop
    S=(resource-1731-220*ig)//320
    h2=(S-M,M)
    assert m<=h2[0]<=M and Q(1,250*h2[0]**2)<Q(1,M*M)
    one=relax((M,),ord_debit)-stop
    two=relax(h2,ord_debit)-stop
    hs,three=cubic_bound(S-m,ord_debit)
    # All n>=4 cost at least one discarded height m. The rate supplied to the
    # final three stages by all older stages is clamped at eta independently
    # of n. Removing their grid floors, clamps and the other lost heights is
    # a monotone relaxation of the permitted recurrence.
    more=three+ETA/250**3-stop
    assert max(one,two,more)<ceiling
    return {'clock_cap':resource,'minimum_G_to_beat_3_stage':ig,'ordinary_budget_above_this_G':S,
        'three_stage_exact_stopped_supremum':str(ceiling),'two_stage_relaxed_opt_heights':h2,
        'last_three_relaxed_opt_for_4_plus':hs,
        'upper_for_1':str(one),'upper_for_2':str(two),'upper_for_4_to_7':str(more),
        'deficits_from_three_stage_for_1_2_4plus':[dec(ceiling-q,25) for q in (one,two,more)]}

def prove_three_cross(resource,od,gd,cross,claimed):
    budget=(resource-1731-220*cross)//320
    heights,ideal=cubic_bound(budget,od)
    rate=Q(0)
    for i,h in enumerate(heights):
        cap=min(ETA,(249*(BINARY_C-od/h)+rate)/250)
        rate=Q(int(cap*10**21)-1,10**21) if i<2 else cap
    alpha,beta,gamma=[w/h**2 for w,h in zip((Q(1,62500),Q(1,250),Q(1)),heights)]
    assert alpha<beta<gamma
    tangent_loss=A*od*min(beta-alpha,gamma-beta,beta)
    assert 0<ideal-rate<tangent_loss
    assert GAUSSIAN_C-gd/(cross-1)<rate<=GAUSSIAN_C-gd/cross
    assert rate-stop==claimed
    return {'crossing_G':cross,'ordinary_heights':heights,
            'before_grid_relaxed_upper':str(ideal),'installed_native_upper':str(rate),
            'minimum_relaxed_loss_of_another_integer_allocation':str(tangent_loss)}

new=Q(523210571423785163651433485201,134217728000000000000000000000000)
old=Q(523210198560303585338978849681,134217728000000000000000000000000)
eight=Q(523210399077391326763724428177,134217728000000000000000000000000)
families={'six_column_composite':(318291911,Q(125645,1048576),491002,new),
          'eight_column_composite':(318291911,Q(130699669,1073741824),496173,eight),
          'published_8073_family':(318292011,Q(64939,524288),501831,old)}
out={}
for key,(budget,debit,cross,ceiling) in families.items():
    three=prove_three_cross(budget,Q(11204,8192),debit,cross,ceiling)
    others=compute(budget,Q(11204,8192),debit,ceiling)
    out[key]=dict(others,three_stage_crossing=three)
if __name__=='__main__':print(json.dumps(out,indent=2))
