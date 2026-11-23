"""Directed reconstruction of the #8072 Gaussian suffix price and fixed-clock allocation."""
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
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
CLOCK_CAP = 318292071
STOP = Q(5, 10**18)
TARGET = Q(39, 10000)
OLD_DEBIT = Q(64939, 524288)
ORD_DEBIT = Q(11239, 8192)
OLD_UPPER = Q(523209464347189355219919950737, 134217728000000000000000000000000)


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


def p(z):
    rem = z % 2
    return rem * rem / 2 - rem


@cache
def periodic_constants(r, k):
    r, k = Q(r), Q(k)
    ratio = k / r
    period = 2 * ratio.denominator
    knots = sorted({Q(i) for i in range(0, period + 1, 2)} |
                   {Q(2*j, ratio) for j in range(ratio.numerator + 1)})
    def H(y):
        return k * p(y) - r / ratio * p(ratio * y)
    hs = [H(y) for y in knots]
    assert hs[0] == hs[-1] == 0
    integral = Q(0)
    maximum = Q(0)
    minimum = None
    for (y, z), (h, j) in zip(zip(knots, knots[1:]), zip(hs, hs[1:])):
        mid = (y+z)/2
        measured = r*(2*(ratio*mid//2)-8) - k*(2*(mid//2)-8)
        assert measured == 9*(k-r) + (j-h)/(z-y)
        assert 0 <= measured < 10*k - 8*r
        assert measured.denominator == 1
        integral += (h+j)*(z-y)/2
        maximum = max(maximum, measured)
        minimum = min(measured, minimum) if minimum is not None else measured
    assert integral/period == -(k - r/ratio)/3
    assert maximum == 10*k-8*r-gcd(int(2*r), int(2*k))
    return max(hs), maximum, minimum, len(knots)-1


def edge_envelopes(r, k, lower):
    ratio = k / r
    hmax, discrete, minimum, num_intervals = periodic_constants(r,k)
    H0 = k * p(Q(lower)) - r/ratio*p(ratio*lower)
    simple = 9*(k-r) + T*r/(2*ratio*lower)
    sharp = 9*(k-r) + T*(hmax-H0)/lower
    assert sharp <= simple and sharp >= 0 and minimum >= 0
    return discrete, min(discrete, simple), min(discrete, sharp), num_intervals


def aggregate(recipe):
    edges = [(Q(r), Q(k), w, recipe.paid.histogram[r]) for (r,k),w in recipe.cells.items()]
    psi = sum(count*w*r*(powers(k/r,C)[0]-1)/C for r,k,w,count in edges)
    price_weights = [(r,k,count*w*powers(r/k,T)[1]) for r,k,w,count in edges]
    return edges, psi, price_weights


def fringe_numerators(recipe, price_weights, lower):
    old = 10 * sum(k*n for k,n in recipe.targets.histogram.items())
    by_grade = {}
    total_discrete = total_simple = total_sharp = 0
    intervals = 0
    for r, k, load in price_weights:
        d, simple, sharp, n = edge_envelopes(r,k,lower)
        by_grade[k] = max(by_grade.get(k, Q(0)), d)
        total_discrete += load*d
        total_simple += load*simple
        total_sharp += load*sharp
        intervals += n
    per_owner = sum(n*by_grade[k] for k,n in recipe.targets.histogram.items())
    assert total_sharp <= total_simple <= total_discrete <= per_owner < old
    return (old, per_owner, total_discrete, total_simple, total_sharp), intervals


def factor(fringe, scale, lower):
    delta = Q(1, 2**128)
    return ((1+delta) * (1+Q(1032, scale)) * powers(scale*lower,C)[1] *
            (1+fringe/lower+delta) / (1-delta)**4)


def booking(upper, denominator=2**24):
    lo, hi = 0, denominator-1
    while hi-lo>1:
        mid = (lo+hi)//2
        if powers(2,Q(mid,denominator))[0] > upper:
            hi = mid
        else:
            lo = mid
    assert powers(2,Q(hi,denominator))[0] > upper
    return Q(hi,denominator)


def ordinary(heights):
    rate = Q(0)
    for i,h in enumerate(heights):
        rate = min(TARGET, (249*(BINARY_C-ORD_DEBIT/h)+rate)/250)
        if i+1 < len(heights):
            rate = Q(int(rate*10**21)-1,10**21)
    return rate


def shape(g):
    total=(CLOCK_CAP-1731-220*g)//320
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
    disclosed=Q(int(value*10**15),10**15)
    assert disclosed+STOP < min(o,c)
    strict,functional,positive=margins(disclosed,Q(1,10**18),disclosed+STOP,c)
    assert len(strict)==54 and len(functional)==4 and min(*strict,*functional,positive)>0
    return {
        "gaussian_height":g,"ordinary_heights":hs,"complete_clock":1731+320*sum(hs)+220*g,
        "supremum":str(value),"lower_bookable":str(disclosed),"lower_decimal":dec(disclosed,15),
        "strict_gain_over_8072_ceiling":str(disclosed-OLD_UPPER),"ordinary_upper":str(o),
        "positive_upper":str(c),"positive_signed_margin":str(positive),
        "smaller_crossing_height":lo,"higher_crossing_height":hi,
        "signed_inequalities_passed":[len(strict),len(functional),1],
    }


def main():
    recipe=numerical_recipe(490950)
    edges,psi,weights=aggregate(recipe)
    assert len(edges)==51 and len(recipe.typed_cells())==88
    raw=word(*load_changed(HERE/'inputs'))
    target,paid=(Counter(p.rank for p in arr) for arr in (raw.targets,raw.paid))
    assert sum(target.values())==52608 and sum(paid.values())==281568
    check_decrease(paid,target)
    deficit_lo,deficit_hi=margin(paid,target,TARGET)
    assert Q('-1.539342547620186178215')<deficit_lo<=deficit_hi<Q('-1.539342547620186178214')
    rawlo=Q('.0038984814465499354937143170325740113')
    rawhi=Q('.0038984814465499354937143170325740114')
    assert margin(paid,target,rawlo)[0]>0>margin(paid,target,rawhi)[1]
    assert C<TARGET and BINARY_C>TARGET
    all_variants={}
    old_upper=optimize(OLD_DEBIT)
    assert Q(old_upper['supremum'])==OLD_UPPER
    scale=1724*306//2
    nums,coverage=fringe_numerators(recipe,weights,BASE_L)
    for name,num in zip(("historical","owner_max","edge_max","mean","phase"),nums):
        fr=num/(T*psi)
        upper=factor(fr,scale,BASE_L)
        debit=booking(upper)
        all_variants[name]={"lower":BASE_L,"fringe_upper":dec(fr),"finite_factor_upper":dec(upper),
                            "debit":str(debit),"debit_decimal":dec(debit),"allocation":optimize(debit)}
    print(json.dumps({"source_head":"75f7e1c44f48c43983016bcf8878c4d9e5e87c62",
        "word_sha256":WORD,"layout_sha256":LAYOUT,"targets":sum(target.values()),"paid":sum(paid.values()),
        "unsplit_target_moment_minus_paid_interval":[str(deficit_lo),str(deficit_hi)],
        "unsplit_root_bracket":[str(rawlo),str(rawhi)],"cG_gap_to_target":str(TARGET-C),
        "ordinary_eta":str(TARGET),"ordinary_raw":str(BINARY_C),"gaussian_raw":str(C),
        "interior_cells":len(edges),"typed_cells":len(recipe.typed_cells()),"phase_intervals":coverage,
        "historical_cap":old_upper,"variants":all_variants},indent=2))


if __name__=='__main__':
    main()
