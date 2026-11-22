"""Global one-crossing proof certificate for the actual 36-call binary tariff.

Pass a restored e264 P104 machine directory. The two outward dyadic sign tests
use the source's integer square-root enclosures at 112 fractional bits.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import json
import sys


def signed_support(a, p):
    low = {r: count for r, count in sorted(a.items()) if r < p}
    high = sorted(r for r in a if r > p)
    tails = {r: sum(count for j, count in a.items() if j >= r) for r in high}
    if not low or any(count > 0 for count in low.values()) or min(low.values()) >= 0:
        raise ValueError('lower coefficients do not force monotonicity')
    if any(count < 0 for count in tails.values()):
        raise ValueError('negative upper tail')
    return low, tails


def check(directory):
    sys.path.insert(0, str(Path(directory).resolve()))
    from upstream import install
    install()
    from independent_binary_price import raw_moments
    from strong_binary import graph, caller
    from strict_moment import UNIT, power_interval

    targets, paid = raw_moments(graph(), caller())
    pivot = 8
    coefficients = Counter(targets)
    coefficients.subtract(paid)
    negative_low, tails = signed_support(coefficients, pivot)
    totals = [sum(a * r**t for r, a in coefficients.items()) for t in (0, 1)]
    assert totals[0] < 0 < totals[1]
    nonpositive_t_bound = coefficients[1] + sum(a for a in coefficients.values() if a > 0)
    assert nonpositive_t_bound == -30_678
    # For t>=0, x**t log x is nonnegative and strictly increasing for x>1.
    # Summing the upper terms by parts makes the positive derivative explicit.
    denom = 1 << 100
    lower = Fraction('.003890115286594461129996942')
    upper = Fraction('.003890115286594461129996943')
    dy_lo = Fraction(-((-lower * denom) // 1), denom)
    dy_hi = Fraction((upper * denom) // 1, denom)
    assert lower <= dy_lo < dy_hi <= upper

    def signs(c):
        low = 0
        high = 0
        for r, a in coefficients.items():
            lo, hi = power_interval(r, 1-c)
            low += min(a*lo, a*hi)
            high += max(a*lo, a*hi)
        return [low,high]

    pos, neg = signs(dy_lo), signs(dy_hi)
    assert pos[0] > 0 > neg[1]
    grid = 10**18
    last = (lower*grid)//1
    assert last == (upper*grid)//1
    # Alter one high surplus label, and the certificate must refuse the changed
    # structure even though every low coefficient still passes its sign test.
    damaged = coefficients.copy()
    damaged[127] -= tails[127]+1
    try:
        signed_support(damaged, pivot)
    except ValueError as exc:
        assert str(exc) == 'negative upper tail'
    else:
        raise AssertionError('corrupt tail passed the monotonicity certificate')
    return {'pivot':pivot,'negative_low':negative_low,'upper_tail_counts':tails,
            'D_at_t_zero_and_one':totals,'upper_bound_for_t_at_most_zero':nonpositive_t_bound,'price_bracket_decimal':['0.003890115286594461129996942','0.003890115286594461129996943'],
            'price_bracket_fractions':list(map(str,(lower,upper))),
            'inner_dyadic_witnesses':list(map(str,(dy_lo,dy_hi))),
            'sign_numerators_at_witnesses':[pos,neg],'common_power_scale':UNIT,
            'last_raw_report_tick_numerator':last,'report_denominator':grid,
            'damaged_high_tail_rejected':True}

if __name__=='__main__':
    print(json.dumps(check(sys.argv[1]),indent=2))
