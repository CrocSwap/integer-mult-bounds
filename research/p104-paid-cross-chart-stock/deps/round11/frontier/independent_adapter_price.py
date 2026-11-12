"""Independent exact rank-one census and rational price separation on #7161."""
from collections import Counter
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

TARGET = Fraction('0.0040075385047236')
PINS = {
    'peer/research/p104-rank8-exit-funded-split/WORD.json.gz': 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    'peer/research/p104-rank8-exit-funded-split/RESULT.json': '59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089',
    'caller/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}


def read(root, path):
    data = (root / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f'SHA-256 mismatch: {path}')
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)


def chart_span(vectors):
    values = {0}
    for vector in vectors:
        if vector in values:
            raise ValueError('dependent chart basis')
        values.update(vector ^ x for x in tuple(values))
    return values


@cache
def reduced_log(value):
    assert 1 <= value <= 2
    t = (value-1)/(value+1)
    n = 30
    low = 2*sum((t**(2*j+1)/Fraction(2*j+1) for j in range(n)), Fraction(0))
    tail = 2*t**(2*n+1)/(Fraction(2*n+1)*(1-t*t))
    return low, low+tail


def exp_minus_bounds(value):
    assert 0 <= value < 1
    terms = [Fraction(1)]
    for degree in range(1,21):
        terms.append(-terms[-1]*value/degree)
    return sum(terms[:-1]), sum(terms)


@cache
def price(rank):
    exponent = rank.bit_length()-1
    dyadic = Fraction(rank, 1 << exponent)
    low2, high2 = reduced_log(Fraction(2))
    low, high = reduced_log(dyadic)
    lower = exp_minus_bounds(TARGET*(high+exponent*high2))[0]
    upper = exp_minus_bounds(TARGET*(low+exponent*low2))[1]
    return rank*lower, rank*upper


def pair_margin(moment, delta, pairs):
    return tuple(a+pairs*b for a,b in zip(moment,delta,strict=True))


def encode(bounds):
    scale = 10**25
    lower, upper = (entry*scale for entry in bounds)
    endpoints = [lower.numerator//lower.denominator, -((-upper.numerator)//upper.denominator)]
    return [str(Fraction(value, scale)) for value in endpoints]


def run(root):
    word, result, caller = (read(root, name) for name in PINS)
    spaces = [chart_span(frame) for frame in word['frames']]
    main = set(word['live']) | {row+112 for row in word['live']}
    main.update(word['hosted']['X2']+word['hosted']['Y2'])
    native, rank_one = Counter(), Counter()
    for event in word['program']:
        if event[0] != 'MOVE':
            continue
        _, role, source, target, owned = event
        a, b = spaces[source], spaces[target]
        assert owned == (role >= word['public'])
        assert a < b or owned and b < a
        rank = abs(len(word['frames'][source])-len(word['frames'][target]))
        native[rank] += 1
        if rank == 1:
            rank_one['owned' if owned else 'main' if role in main else 'public_helper'] += 1
    paid, stages = Counter(), []
    for event in caller['events']:
        if event[0] == 'J':
            paid.update(native)
            stages.append(event[1])
            continue
        kind, op, _, *params = event
        ports = len(caller['types'][kind]['ports'])
        if op == 'QUERY':
            paid[1] += ports
        elif op in ('IDLE_ONE','IDLE_ODD'):
            paid[8*len(params[0])+(op == 'IDLE_ODD')] += ports
    assert stages == list(range(1,18))
    frozen = result['price']['after']
    assert paid == {int(k):v for k,v in frozen['P'].items()}
    target = {int(k):v for k,v in frozen['T'].items()}
    physical = result['checks']['ODD-PHYSICAL-BINDING.json']['occurrence_and_geometry']
    assert frozen['T'] == physical['targets'] and sum(target.values()) == 22427
    assert sum(paid.values()) == 110519
    moment = [Fraction(0), Fraction(0)]
    for rank in sorted(paid.keys()|target.keys()):
        count = target.get(rank,0)-paid.get(rank,0)
        interval = price(rank)
        if count < 0:
            interval = interval[::-1]
        moment = [a+count*b for a,b in zip(moment,interval,strict=True)]
    two_low, two_high = price(2)
    delta = 2-two_high, 2-two_low
    ideal = sum(count*len(stages)//2 for count in rank_one.values())
    public_ideal = sum(rank_one[key]*len(stages)//2 for key in ('main','public_helper'))
    ratio = -moment[1]/delta[1]
    needed = -(-ratio.numerator//ratio.denominator)
    assert ideal == 33991 and public_ideal == 33821 and needed == 25328
    prev, first = (pair_margin(moment,delta,k) for k in (needed-1,needed))
    assert prev[1] < 0 < first[0]
    return {'target':str(TARGET),'pins':PINS,'native_rank_one_classes':rank_one,
            'stages':len(stages),'paid_total':sum(paid.values()),
            'productive_total':sum(target.values()),'ideal_pairs_all_native':ideal,
            'ideal_pairs_public_only':public_ideal,'minimum_ideal_pairs':needed,
            'interval_rational_scale':10**25,'baseline':encode(moment),'one_pair_credit':encode(delta),
            'before_threshold':encode(prev),'first_positive_threshold':encode(first),
            'all_native_upper':encode(pair_margin(moment,delta,ideal)),
            'public_only_upper':encode(pair_margin(moment,delta,public_ideal))}


if __name__ == '__main__':
    assert __debug__
    print(json.dumps(run(Path(sys.argv[1])),indent=2,sort_keys=True))
