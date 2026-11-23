"""Prove exact #8076 capped rates for one through seven ordinary stages."""
from fractions import Fraction as Q
import json

ETA = Q(39, 10000)
BINARY = Q(4391986206293, 2**50)
GAUSSIAN = Q(17145637307, 2**42)
ORDINARY_DEBIT = Q(11178, 8192)
STOP = Q(5, 10**18)
MINIMUM = 8192
MAXIMUM = 524288
GRID = 10**21
BOOKED = Q('.003898226579820971')


def ordinary(heights, exact=True):
    rate = Q(0)
    for i, height in enumerate(heights):
        rate = (249 * (BINARY - ORDINARY_DEBIT / height) + rate) / 250
        if exact:
            rate = min(ETA, rate)
            if i + 1 < len(heights):
                rate = Q((GRID*rate).__floor__() - 1, GRID)
    return rate


def available(clock, g, count):
    return (clock - 1731 - 3*count - 220*g) // 320


def profile3(budget):
    trial = (MINIMUM, budget - MINIMUM - MAXIMUM, MAXIMUM)
    assert MINIMUM <= trial[1] <= MAXIMUM
    a,b,c = [Q(1, 250**(2-i)*height**2) for i,height in enumerate(trial)]
    assert a < b < c
    # The tangent at this corner bounds the relaxed reciprocal objective.
    # Its linear loss is strictly positive for every other integer triple.
    one_unit = Q(249,250)*ORDINARY_DEBIT*min(b-a,c-b,b)
    assert 0 <= ordinary(trial,False)-ordinary(trial) < one_unit
    return trial


def all_lengths(clock, gd, pivot):
    def cell(g):
        p=profile3(available(clock,g,3))
        return p, ordinary(p), GAUSSIAN-gd/g
    p0,o0,g0=cell(pivot)
    p1,o1,g1=cell(pivot+1)
    assert g0<o0 and o1<g1
    ceiling=max(g0,o1)-STOP
    # Positive capacity increases with G; ordinary feasible sets shrink with G.
    # To attain this candidate or do better, the positive margin must reach it.
    min_g = (gd/(GAUSSIAN-ceiling-STOP)).__ceil__()
    assert GAUSSIAN-gd/(min_g-1) < ceiling+STOP <= GAUSSIAN-gd/min_g
    two_size = available(clock,min_g,2)
    p2=(two_size-MAXIMUM,MAXIMUM)
    assert MINIMUM<=p2[0]<=MAXIMUM and Q(1,250*p2[0]**2)<Q(1,MAXIMUM**2)
    # Longer stages lose at least one mandatory preceding height. The carry
    # from all such older stages is at most the source clamp ETA / 250**3.
    last_three=profile3(available(clock,min_g,4)-MINIMUM)
    other=(ordinary((MAXIMUM,),False)-STOP,
           ordinary(p2,False)-STOP,
           ordinary(last_three,False)+ETA/250**3-STOP)
    assert max(other)<ceiling
    return {'clock_cap':clock,'ordinary_heights':p0 if g0>=o1 else p1,
            'gaussian_height':pivot if g0>=o1 else pivot+1,
            'three_stage_slices':[{'G':g,'ordinary':str(o),'gaussian':str(gg)}
                                  for g,o,gg in [(pivot,o0,g0),(pivot+1,o1,g1)]],
            'exact_stopped_upper_one_to_seven_stages':str(ceiling),
            'one_two_and_four_to_seven_relaxed_upper':[str(v) for v in other],
            'required_G_for_equality_or_improvement':min_g}


def verify():
    expected={"public":Q(1667119388378402860472786027,427661302169600000000000000000),
              "composite":Q(1632693363926333812833543539,418829775667200000000000000000)}
    out={}
    for clock in (318291911,318291900):
        for label,gd,pivot in [('public',Q(64939,524288),509812),
                               ('composite',Q(125645,1048576),499284)]:
            result=all_lengths(clock,gd,pivot)
            assert Q(result['exact_stopped_upper_one_to_seven_stages'])==expected[label]
            out[f'{label}_at_{clock}']=result
    cheaper=all_lengths(318291899,Q(125645,1048576),499283)
    assert Q(cheaper['exact_stopped_upper_one_to_seven_stages'])<BOOKED
    out['one_clock_lower_composite']=cheaper
    out['minimum_clock_for_booked_kappa']=318291900
    out['gain_over_public_upper']=str(BOOKED-expected['public'])
    return out


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
