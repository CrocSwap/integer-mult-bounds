"""Original exact primal/dual width-120 bank inventory checker.

No geometry or chronological admission is implied by a packing witness.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import source_data as sd
def verify(capacity,demand,patterns):
    assert type(capacity)is int and capacity>0
    assert all(type(r)is int and 0<r<=capacity and type(n)is int and n>0 for r,n in demand.items())
    supplied=Counter();bins=0;waste=0
    for row in patterns:
        count=row['count'];widths=row['widths']
        assert type(count)is int and count>0
        assert all(type(r)is int and 0<r<=capacity for r in widths)
        width=sum(widths);assert width<=capacity
        bins+=count;waste+=count*(capacity-width)
        supplied.update({r:count*n for r,n in Counter(widths).items()})
    assert supplied==Counter(demand)
    volume=sum(r*n for r,n in demand.items())
    lower=(volume+capacity-1)//capacity
    # y_r=r/capacity is a feasible dual price for every allowed pattern because
    # sum of its widths is at most capacity. No pattern enumeration is required.
    dual={r:F(r,capacity)for r in demand}
    value=sum(dual[r]*n for r,n in demand.items())
    assert value==F(volume,capacity)
    assert bins*capacity-volume==waste
    return dict(capacity=capacity,demand=demand,patterns=patterns,total_rank_demand=volume,
      feasible_bins=bins,unused_coordinate_capacity=waste,dual_prices=dual,
      dual_objective=value,integer_lower_bound=lower,optimal=bins==lower)


def calculate():
    pins=sd.read_json('expected/kernel-pins.json')
    ranks={int(k):n for k,n in pins['bank_families'].items()}
    pivots={int(k):n for k,n in pins['pivot_residual_census'].items()}
    patterns=[dict(widths=[7]*12+[4]*9,count=10)]
    used4=used24=0
    for r,n in sorted(pivots.items()):
        patterns.append(dict(widths=[r]*4+[24]+[4]*(24-r),count=15*n))
        used4+=15*n*(24-r);used24+=15*n
    four=4361*30-used4-60*440;three=60*(34+440)
    full=60*(13200-7-sum(pivots.values()))-used24
    assert four%30==three%40==full%5==0
    patterns.extend([dict(widths=[4]*30,count=four//30),dict(widths=[3]*40,count=three//40),
                     dict(widths=[6]*20,count=48),dict(widths=[24]*5,count=full//5)])
    cert=verify(120,{r:60*n for r,n in ranks.items()},patterns)
    assert cert['optimal'] and cert['feasible_bins']==161470
    assert cert['unused_coordinate_capacity']==0
    return {'stage_certificate':cert}
