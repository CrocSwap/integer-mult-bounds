#!/usr/bin/env python3
"""Integer-only ordinary-stage height thresholds for fixed 65/66-bit prices."""
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
GRID=10**21
ETA_NUM=39
ETA_DEN=10000
ETA_TICKS=ETA_NUM*GRID//ETA_DEN
BOOKED=3890115286594461005 # (kappa+5g)*10^21
ORIGINAL_H=2*10**12
CASES=(
 (65,143519922218066619,1920864718790),
 (66,287039844436133239,1479259210417),
)


def trunc_zero(num,den):
    """Match Python int(Fraction), including the negative small-height range."""
    assert den>0
    return num//den if num>=0 else -((-num)//den)


def ordinary(depth,cnum,h):
    """Evaluate the literal e264 recurrence entirely with integer numerators."""
    assert h>0
    cden=1<<depth
    previous=0
    rows=[]
    for i in range(7):
        H=h*16**i
        denominator=250*cden*8*H
        # 10^21*((249*(c-11/(8H))+previous/10^21)/250).
        unbounded=249*(8*H*cnum-11*cden)*GRID+previous*cden*8*H
        numerator=min(unbounded,ETA_TICKS*denominator)
        tick=BOOKED if i==6 else trunc_zero(numerator,denominator)-1
        margin=Fraction(numerator-tick*denominator,denominator*GRID)
        rows.append({'stage':i+1,'height':H,'previous_tick':previous,'rate_tick':tick,
                     'eta_capped':unbounded>=ETA_TICKS*denominator,
                     'strict':previous<tick and numerator>tick*denominator,
                     'margin':str(margin)})
        previous=tick
    return rows


def frac_decimal(frac):
    with localcontext() as ctx:
        ctx.prec=70
        return str(Decimal(frac.numerator)/Decimal(frac.denominator))


def last_margin(rows):
    return Fraction(rows[-1]['margin'])


def main():
    assert ETA_NUM*GRID%ETA_DEN==0
    expected={
      (65,1920864718789):Fraction(-105317725745311877,8448052374772727525933056000000000000000000000000),
      (65,1920864718790):Fraction(8158050008405753,844805237477712557244416000000000000000000000000),
      (66,1479259210416):Fraction(-9126686979662669,271077117057856109019136000000000000000000000000),
      (66,1479259210417):Fraction(47305501493475931,13011701618785889325940736000000000000000000000000),
    }
    out={}
    for depth,C,claimed in CASES:
        # Search on the final cap alone, which is monotone even when earlier
        # candidates fail their own stage conditions. The adjacent full
        # success below establishes that the found cap threshold is feasible.
        lo,hi=1,ORIGINAL_H
        assert last_margin(ordinary(depth,C,lo))<0
        assert last_margin(ordinary(depth,C,hi))>0
        visits=0
        while lo<hi:
            mid=(lo+hi)//2
            if last_margin(ordinary(depth,C,mid))>0:
                hi=mid
            else:
                lo=mid+1
            visits+=1
        assert lo==claimed
        before=ordinary(depth,C,claimed-1)
        after=ordinary(depth,C,claimed)
        assert last_margin(before)==expected[depth,claimed-1]<0
        assert last_margin(after)==expected[depth,claimed]>0
        assert all(x['strict'] for x in before[:-1])
        assert all(x['strict'] for x in after)
        assert not before[-1]['eta_capped'] and not after[-1]['eta_capped']
        assert [x['rate_tick'] for x in before[:-1]]==[x['rate_tick'] for x in after[:-1]]
        sixth=after[-2]['rate_tick']
        D=1<<depth
        # On this shared rounding plateau, L7(h)-booked = A - B/h.
        # B/A below is the exact real boundary for the common sixth tick.
        A_num=249*C*GRID+sixth*D-250*BOOKED*D
        assert A_num>0
        threshold=Fraction(249*11*D*GRID,8*16**6*A_num)
        assert threshold.numerator//threshold.denominator==claimed-1
        reduction=Fraction(ORIGINAL_H-claimed,ORIGINAL_H)*100
        out[str(depth)]={
          'trial':str(Fraction(C,D)), 'least_first_height':claimed,
          'neighbor_margins':[{'height':z,'margin':str(v),'decimal':frac_decimal(v)}
             for z,v in ((claimed-1,last_margin(before)),(claimed,last_margin(after)))],
          'sixth_tick_on_both_neighbors':sixth,
          'first_six_ticks':[r['rate_tick'] for r in after[:-1]],
          'shared_plateau_exact_threshold':str(threshold),
          'reduction_percent_exact':str(reduction),'reduction_percent_decimal':frac_decimal(reduction),
          'binary_search_iterations':visits,'first_six_strict':True,'seventh_strict_at_success':True,
        }
    doc={
      'scope':'Ordinary seven-stage invoice only; eta cap, exact input heights and actual truncation/one-tick policy are included. No other physical or all-size machine obligation is implied.',
      'kappa':'0.003890115286594461','gap':'1/1000000000000000000000',
      'ordinary_tick_e21':BOOKED,'debit':'11/8','height_ratio':16,
      'monotonicity':'For positive integer h, each c-(11/8)/(16^i*h) increases with h. The capped stage limit is nondecreasing in h and in its prior tick. Truncation toward zero and subtracting one are nondecreasing on the real line, so induction makes the seventh cap nondecreasing. Adjacent failure rules out all smaller h; strict success checks all stages at the next integer.',
      'cases':out,
    }
    (HERE/'HEIGHT-EXACT.json').write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
    print('PASS_ORDINARY_HEIGHT_THRESHOLDS_65_66')

if __name__=='__main__':main()
