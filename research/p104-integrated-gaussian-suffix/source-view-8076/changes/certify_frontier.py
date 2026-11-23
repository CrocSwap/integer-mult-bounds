"""Directed reconstruction of the #8076 composite price and fixed-clock allocation."""
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from functools import cache
from math import ceil, gcd, isqrt
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
sys.path.insert(0, str(RUNTIME))
from upstream import HERE, install
install()
sys.path.insert(0, str(ROOT / "peer/research/tiered-native-multiplier/source"))
from grades import numerical_recipe
from installations import BINARY_C, GAUSSIAN_C
from outer_budget import margins
from strong_complex import LAYOUT, WORD, load_changed, word
sys.path.insert(0, str(RUNTIME / "inputs/complex-source"))
from verify_component import check_decrease, margin

getcontext().prec = 52
GRID = 1 << 192
C = GAUSSIAN_C
T = 1 - C
BASE_L = 1874
CLOCK_CAP = 318291900
STOP = Q(5, 10**18)
TARGET = Q(39, 10000)
OLD_DEBIT = Q(64939, 524288)
ORD_DEBIT = Q(11178, 8192)
OLD_UPPER = Q(1667119388378402860472786027,427661302169600000000000000000)


def dec(value, places=32):
    value = Q(value)
    return format(Decimal(value.numerator) / Decimal(value.denominator), f".{places}f")


@cache
def powers(base, exponent):
    """Independent directed interval for a rational base and a positive dyadic exponent."""
    base, exponent = Q(base), Q(exponent)
    assert base > 0 and 0 <= exponent < 1 and exponent.denominator.bit_count() == 1
    low = int(base * GRID)
    high = ceil(base * GRID)
    low_result = high_result = GRID
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        low = isqrt(low * GRID)
        high = 1 + isqrt(high * GRID - 1)
        if exponent.numerator & (1 << bit):
            low_result = (low_result * low) // GRID
            high_result = -(-high_result * high // GRID)
    return Q(low_result, GRID), Q(high_result, GRID)








def aggregate(recipe):
    edges = [(Q(r), Q(k), w, recipe.paid.histogram[r]) for (r,k),w in recipe.cells.items()]
    psi = sum(count*w*r*(powers(k/r,C)[0]-1)/C for r,k,w,count in edges)
    price_weights = [(r,k,count*w*powers(r/k,T)[1]) for r,k,w,count in edges]
    return edges, psi, price_weights




def factor(fringe, scale, lower):
    delta = Q(1, 2**128)
    return ((1+delta) * (1+Q(1032, scale)) * powers(scale*lower,C)[1] *
            (1+fringe/lower+delta) / (1-delta)**4)




def ordinary(heights):
    rate = Q(0)
    for i,h in enumerate(heights):
        rate = min(TARGET, (249*(BINARY_C-ORD_DEBIT/h)+rate)/250)
        if i+1 < len(heights):
            rate = Q(int(rate*10**21)-1,10**21)
    return rate


def shape(g):
    total=(CLOCK_CAP-1740-220*g)//320
    last=524288
    rest=total-last
    weights=(Q(1,62500),Q(1,250),Q(1))
    lo,hi=max(8192,rest-last),min(last,rest-8192)
    first_lo,first_hi=lo,hi
    while lo<hi:
        n=(lo+hi)//2
        middle=rest-n
        first_gain=weights[0]/(n*(n+1))
        middle_cost=weights[1]/((middle-1)*middle)
        if first_gain>middle_cost:lo=n+1
        else:hi=n
    optimum=lo
    h=(optimum,rest-optimum,last)
    def ideal(hs):
        return Q(249,250)*sum(w*(BINARY_C-ORD_DEBIT/b)
                              for w,b in zip(weights,hs))
    # Separable integer reciprocal costs. Every deposit outside this fixed
    # slice originates in a lost unit or in a decrement of the last stage.
    inc=[w/(b*(b+1)) if b<last else Q(0) for w,b in zip(weights,h)]
    dec=[w/((b-1)*b) if b>8192 else None for w,b in zip(weights,h)]
    assert all(d>=inc[j] for i,d in enumerate(dec) if d is not None
               for j in range(3) if i!=j)
    third_gap=dec[2]-max(inc[0],inc[1])
    budget_gap=min(x for x in dec if x is not None)
    near=[(n,rest-n,last) for n in range(max(first_lo,optimum-1),min(first_hi,optimum+1)+1)]
    best=max(near,key=ordinary)
    assert ideal(h)-ordinary(best) < Q(249,250)*ORD_DEBIT*min(third_gap,budget_gap)
    for n in (optimum-2,optimum+2):
        if first_lo<=n<=first_hi:
            assert ideal((n,rest-n,last))<ordinary(best)
    return best


def optimize(debit):
    def at(g):
        hs=shape(g)
        return hs,ordinary(hs),C-debit/g
    lo,hi=400000,524288
    assert at(lo)[1]>at(lo)[2] and at(hi)[1]<at(hi)[2]
    while hi-lo>1:
        m=(lo+hi)//2
        _,o,c=at(m)
        if o>c:lo=m
        else:hi=m
    rows=[(min(o,c)-STOP,g,hs,o,c) for g,(hs,o,c) in ((k,at(k)) for k in (lo,hi))]
    value,g,hs,o,c=max(rows)
    disclosed=Q(int(value*10**18),10**18)
    assert disclosed+STOP < min(o,c)
    strict,functional,positive=margins(disclosed,Q(1,10**18),disclosed+STOP,c)
    assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,positive)>0
    return {
        "gaussian_height":g,"ordinary_heights":hs,"complete_clock":1740+320*sum(hs)+220*g,
        "supremum":str(value),"lower_bookable":str(disclosed),"lower_decimal":dec(disclosed,18),
        "strict_gain_over_8076_ceiling":str(disclosed-OLD_UPPER),"ordinary_upper":str(o),
        "positive_upper":str(c),"positive_signed_margin":str(positive),
        "smaller_crossing_height":lo,"higher_crossing_height":hi,
        "signed_inequalities_passed":[len(strict),len(functional),1],
    }




