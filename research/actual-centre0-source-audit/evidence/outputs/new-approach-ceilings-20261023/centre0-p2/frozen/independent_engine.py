#!/usr/bin/env python3
"""Independent conditional arithmetic check; no physical/compiled word executes.

Uses r*exp(-C log r), rational logarithm series and alternating exponential
bounds. It does not import the author screen or its positive-exponential engine.
Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTHOR = HERE.parent / 'native-c-inverse-boundary-20261023'

def logsmall(z):
    assert 0 <= z <= Q(1, 3)
    terms = 40
    lower = sum((2*z**(2*j+1)/(2*j+1) for j in range(terms)), Q(0))
    tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return lower, lower+tail

def logint(r):
    k = r.bit_length()-1
    x = Q(r, 2**k)
    a, b = logsmall((x-1)/(x+1))
    c, d = logsmall(Q(1, 3))
    return a+k*c, b+k*d

def alternating(x, n):
    assert 0 <= x < Q(1, 50)
    term, total = Q(1), Q(1)
    for j in range(1, n+1):
        term *= -x/j
        total += term
    return total

def rankpower(r, saving):
    assert r >= 1 and 0 <= saving <= Q(17, 5000)
    a, b = logint(r)
    # For x>=0 and x<1 the alternating exponential terms decrease.
    # Odd truncation is below exp(-x); even truncation is above it.
    return r*alternating(saving*b, 17), r*alternating(saving*a, 18)

def moment(hist, saving):
    pairs = [(n, rankpower(r, saving)) for r, n in hist.items()]
    return tuple(sum((n*v[i] for n, v in pairs), Q(0)) for i in (0, 1))

def interval(a, b):
    scale = 10**24
    lower, upper = (a*scale).__floor__(), (b*scale).__ceil__()
    return {'outward_lower': str(Q(lower, scale)),
            'outward_upper': str(Q(upper, scale)),
            'floor_24_decimal_units': lower,
            'ceil_24_decimal_units': upper}

def main():
    original = json.loads((HERE/'frozen/RESULT.json').read_text())
    source = AUTHOR/'screen-sources/5027-RESULT.json'
    assert source.read_bytes() == (HERE/'frozen/RESULT.json').read_bytes()
    helpers = {4:28, 7:7, 8:47, 9:326}
    native = {1:2201, 2:412, 3:510, 4:127, 5:40}
    targets = Counter({153:224})
    paid = Counter({1:2240})
    for j in range(1, 10):
        targets[1+8*j] += 448
        paid[8*j] += 448
    for r, n in helpers.items(): targets[r] += 19*n
    for r, n in native.items(): paid[r] += 19*n
    assert dict(targets) == {int(k):v for k,v in original['targets'].items()}
    assert dict(paid) == {int(k):v for k,v in original['paid'].items()}
    corrected = paid.copy()
    corrected[1] += 19*(336-112)
    assert corrected[1] == 19*(2201+336)+112 == 48315
    assert sum(targets.values()) == 12008
    assert 19*sum(helpers.values()) == 7752
    assert sum(corrected.values()) == 73038
    assert sum(r*n for r,n in targets.items()) == 265533
    assert sum(r*n for r,n in corrected.items()) == 267773
    author = json.loads((AUTHOR/'SCREEN-RESULT.json').read_text())
    assert dict(corrected) == {int(k):v for k,v in author['hypothetical_corrected_paid'].items()}
    results = {}
    a, b = Q('0.0030217758'), Q('0.00339999')
    for c in (a, b):
        tl, tu = moment(targets, c)
        pl, pu = moment(corrected, c)
        lo, hi = tl-pu, tu-pl
        assert hi < 0
        recorded = author['point_margins'][str(c)]
        # The much narrower author's interval must lie in this independent one.
        assert lo <= Q(recorded['exact_lower']) <= Q(recorded['exact_upper']) <= hi
        results[str(c)] = interval(lo, hi)
    upper = moment(targets, a)[1]-moment(corrected, b)[0]
    assert upper < -2797
    output = {'status':'PASS_INDEPENDENT_CONDITIONAL_ARITHMETIC',
              'hypothetical_substitution_proved':False,
              'helper_credit_once':7752, 'additional_H1':4256,
              'changed_paid_count':73038, 'changed_paid_rank_mass':267773,
              'rank_mass_margin':-2240, 'point_margins':results,
              'uniform_interval':[str(a),str(b)],
              'uniform_margin_upper':interval(upper, upper)['outward_upper'],
              'uniform_method':'T(C)<=T(a), P(C)>=P(b); separate monotonicity only',
              'no_inference_outside_interval':True,
              'hashes':{str(x.relative_to(HERE.parent)):sha256(x.read_bytes()).hexdigest()
                        for x in (Path(__file__), AUTHOR/'screen.py', AUTHOR/'SCREEN-RESULT.json', source)}}
    (HERE/'C-INVERSE-SCREEN-CHECK.json').write_text(json.dumps(output,indent=2)+'\n')
    print(output['status'], 'upper<-2797, conditional invoice only')

if __name__ == '__main__': main()
