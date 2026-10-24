#!/usr/bin/env python3
"""Directed rational arithmetic for the fixed centre-exchange invoice family.

Independent implementation; classical atanh/Taylor interval formulas. Construction
credit: Cao Yifan #4610, Ali Romman #5377/#5383, and retained native/compiler lineage.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
S = 10**50
SOURCE_SHA = 'b4f720a7ccbb5b46e472eaf85dc8739a40598986f19b37d26c4f9ecfbd31f0de'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def up(a, b):
    return -((-a) // b)


def point(x):
    x = F(x)
    return x.numerator*S//x.denominator, up(x.numerator*S, x.denominator)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def scale(a, x):
    x = F(x)
    values = [F(a[0])*x, F(a[1])*x]
    return min(values).__floor__(), max(values).__ceil__()


def mul(a, b):
    values = [x*y for x in a for y in b]
    return min(values)//S, up(max(values), S)


def reciprocal(a):
    need(a[0] > 0, 'Positive reciprocal denominator')
    return S*S//a[1], up(S*S, a[0])


@lru_cache(None)
def log_reduced(q):
    q = F(q)
    need(1 <= q <= 2, 'Log reduction range')
    z = (q-1)/(q+1)
    term, total = z, F(0)
    for j in range(64):
        total += 2*term/(2*j+1)
        term *= z*z
    # All omitted terms are nonnegative, denominators at least 129.
    tail = 2*term/(129*(1-z*z))
    return point(total)[0], point(total+tail)[1]


@lru_cache(None)
def log_rank(r):
    need(type(r) is int and r > 0, 'Positive integer rank')
    e = r.bit_length()-1
    return add(scale(log_reduced(F(2)), e), log_reduced(F(r, 2**e)))


def exp_positive(a):
    need(0 <= a[0] <= a[1], 'Nonnegative exponential argument')
    if a[1] >= S:
        half = scale(a, F(1, 2))
        value = exp_positive(half)
        return mul(value, value)
    result, term = point(1), point(1)
    for j in range(1, 49):
        term = scale(mul(term, a), F(1, j))
        result = add(result, term)
    first = scale(mul(term, a), F(1, 49))
    ratio = scale(a, F(1, 50))
    tail = mul(first, reciprocal((S-ratio[1], S-ratio[0])))
    return result[0], result[1]+tail[1]


@lru_cache(None)
def power(r, c):
    c = F(c)
    need(0 <= c <= 1, 'Saving in [0,1]')
    return scale(reciprocal(exp_positive(scale(log_rank(r), c))), r)


def margin(targets, paid, c):
    result = point(0)
    for histogram, sign in [(targets, 1), (paid, -1)]:
        for r, n in histogram.items():
            result = add(result, scale(power(r, F(c)), sign*n))
    return result


def derivative(targets, paid, lo, hi):
    # d/dc (T-P) = sum(P-T) log(r) r**(1-c).
    result = point(0)
    for histogram, sign in [(paid, 1), (targets, -1)]:
        for r, n in histogram.items():
            value = (power(r, F(hi))[0], power(r, F(lo))[1])
            result = add(result, scale(mul(log_rank(r), value), sign*n))
    return result


def decimal(a):
    def convert(x):
        prefix = '-' if x < 0 else ''
        x = abs(x)
        return prefix+str(x//S)+'.'+str(x%S).zfill(50)
    return [convert(x) for x in a]


def exchange(targets, paid, count):
    need(type(count) is int and 0 <= count <= 144, 'At most 144 original centre slots')
    t, p = dict(targets), dict(paid)
    p[1] -= count
    p[8] -= count
    t[9] -= count
    need(min([*t.values(), *p.values()]) >= 0, 'No overspent paid or target inventory')
    return t, p


def run():
    raw = (HERE/'source/INVOICE.json').read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'Exact original final-4610 invoice bytes')
    source = json.loads(raw)
    targets = {int(r): n for r, n in source['targets'].items()}
    paid = {int(r): n for r, n in source['paid'].items()}
    need(paid[8] == 144, 'All original centre jobs counted')
    brackets = {0: ('.00302177587077', '.00302177587078'),
                16: ('.00302238736347', '.00302238736348'),
                128: ('.00302667476807', '.00302667476808'),
                144: ('.00302728824993', '.00302728824994')}
    cases = {}
    for count, (lo, hi) in brackets.items():
        t, p = exchange(targets, paid, count)
        lower, upper = margin(t, p, F(lo)), margin(t, p, F(hi))
        need(lower[0] > 0 > upper[1], 'Strict root bracket '+str(count))
        # Monotonicity near the crossing; global nonfunding below handles the
        # later range without incorrectly requiring a globally negative derivative.
        slope = derivative(t, p, F(0), F(1, 100))
        need(slope[1] < 0, 'Strictly decreasing margin on [0,.01] '+str(count))
        cases[str(count)] = {
            'raw_root_bracket': [lo, hi],
            'margin_at_lower': decimal(lower), 'margin_at_upper': decimal(upper),
            'derivative_on_0_to_001': decimal(slope),
            'paid_calls': sum(p.values()), 'target_fields': sum(t.values()),
            'rank_surplus': sum(r*n for r,n in t.items())-sum(r*n for r,n in p.items())}
    t, p = exchange(targets, paid, 144)
    bit_boundary = margin(t, p, F('.0034'))
    need(bit_boundary[1] < 0, 'Even all centre exchanges miss .0034')
    # A directed interval cover proves that no second positive window occurs.
    # For c in [lo,hi], every r**(1-c) lies between its endpoint values.
    # All smaller exchange counts have <= this best-case margin by concavity.
    cells = []
    for j in range(1024):
        lo = F(1,100)+F(99*j,102400)
        hi = F(1,100)+F(99*(j+1),102400)
        bound = point(0)
        for histogram, sign, endpoint in [(t, 1, lo), (p, -1, hi)]:
            for r,n in histogram.items():
                bound = add(bound, scale(power(r, endpoint), sign*n))
        need(bound[1] < 0, 'Global nonfunding interval '+str(j))
        cells.append(bound[1])
    # Independent exact calibrations of logarithm/exponential arithmetic.
    for r in (1, 2, 4, 8, 9, 16, 64, 145):
        for c, value in [(F(0), r), (F(1), 1)]:
            a = power(r, c)
            need(a[0] <= value*S <= a[1], 'Exact integral-power calibration')
    for r, root in [(4,2), (9,3), (16,4), (64,8)]:
        a = power(r, F(1,2))
        need(a[0] <= root*S <= a[1], 'Exact square-root calibration')
    rejected = {}
    try:
        exchange(targets, paid, 145)
    except ValueError:
        rejected['invented_145th_centre'] = True
    bad_t, bad_p = exchange(targets, paid, 128)
    bad_t[9] += 128
    need(margin(bad_t, bad_p, F('.0034'))[0] > 0,
         'Omitted target debits falsely fund the bit boundary')
    rejected['omitted_H9_debits_change_answer'] = True
    need(len(rejected) == 2, 'Both budget controls executed')
    return {'status': 'PASS_FIXED_CENTRE_EXCHANGE_BUDGET',
            'source_invoice_sha256': SOURCE_SHA, 'cases': cases,
            'all_144_margin_at_0034': decimal(bit_boundary),
            'global_nonfunding_cover': {'interval': ['.01','1'], 'cells': 1024,
                'largest_margin_upper': decimal((0,max(cells)))[1]},
            'remaining_raw_headroom_upper': str(F(brackets[144][1])-F(brackets[128][0])),
            'controls': rejected,
            'scope': 'At most one -H1-H8 paid/-H9 target exchange per original centre; all other inventory fixed. Raw moments only.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
