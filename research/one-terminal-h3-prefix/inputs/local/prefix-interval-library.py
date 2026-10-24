#!/usr/bin/env python3
"""Paid-node gate and exact CONDITIONAL prefix-split arithmetic; no search."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import gzip
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent


def need(test, why):
    if not test:
        raise ValueError(why)


def atanh_log(x):
    """Exact rational bounds for log(x),1<=x<=2; positive Taylor tail."""
    z = (x-1)/(x+1)
    need(0 <= z <= F(1, 3), 'reduced logarithm domain')
    value = F(0)
    power = z
    count = 64
    for k in range(count):
        value += 2*power/(2*k+1)
        power *= z*z
    tail = 2*power/((2*count+1)*(1-z*z))
    return value, value+tail


def log_interval(n):
    if n == 1:
        return F(0), F(0)
    k = n.bit_length()-1
    l2, u2 = atanh_log(F(2))
    lr, ur = atanh_log(F(n, 1 << k))
    return k*l2+lr, k*u2+ur


def exp_minus(x):
    """Alternating Taylor bounds: odd partial15 <= exp(-x) <= even16."""
    need(0 <= x < F(1, 100), 'small exact exponential argument')
    term, total = F(1), F(1)
    lower = None
    for k in range(1, 17):
        term *= -x/k
        total += term
        if k == 15:
            lower = total
    return lower, total


def power_interval(n, C):
    lo, hi = log_interval(n)
    low = n*exp_minus(C*hi)[0]
    high = n*exp_minus(C*lo)[1]
    return low, high


def add_intervals(terms):
    lo, hi = F(0), F(0)
    for coefficient, (l, u) in terms:
        lo += coefficient*(l if coefficient >= 0 else u)
        hi += coefficient*(u if coefficient >= 0 else l)
    return lo, hi


def decimal_interval(interval):
    scale = 10**24
    l, u = interval
    low = (l*scale).numerator//(l*scale).denominator
    high = -((-u*scale).numerator//(-u*scale).denominator)
    need(F(low, scale) <= l <= u <= F(high, scale), 'outward exact decimal enclosure')
    def display(n):
        sign = '-' if n < 0 else ''
        n = abs(n)
        return sign+str(n//scale)+'.'+str(n % scale).zfill(24)
    return dict(lower=display(low), upper=display(high), method='exact rational Taylor bounds')


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        raw = (HERE/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == row['git_blob'], 'full source Git blob')
    word = json.loads(gzip.decompress((HERE/'source/ACTUAL-WORD.json.gz').read_bytes()))
    profiles = {}
    for direction in ('forward', 'backward'):
        program = word['programs'][direction]
        paid = Counter(e[5] for e in program if e[0] == 'climb')
        paid.update(e[4] for e in program if e[0] == 'center')
        need(dict(paid) == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8},
             'actual paid child profile')
        need(paid.get(9, 0) == 0, 'NO existing paidH9 node to replace')
        profiles[direction] = {str(r): paid[r] for r in sorted(paid)}
    canonical = word['canonical']
    rank8_paid_events = [dict(event=i, instruction=e) for i, e in enumerate(word['programs']['forward'])
                        if (e[0] == 'climb' and e[5] == 8) or (e[0] == 'center' and e[4] == 8)]
    need(len(rank8_paid_events) == 8 and all(r['instruction'][0] == 'center' for r in rank8_paid_events),
         'all paidH8 children are centres, not mainB child observations')
    helper = Counter(len(canonical['frames'][canonical['final'][r]])
                     - len(canonical['frames'][canonical['start'][r]]) for r in range(224, 632))
    need(dict(helper) == {4: 28, 7: 7, 8: 47, 9: 326}, 'productive helper census')
    path = [dict(event=i, input=e[3], output=e[4], rank=e[5])
            for i, e in enumerate(word['programs']['forward']) if e[0] == 'climb' and e[2] == 224]
    need(Counter(e['rank'] for e in path) == {1: 5, 4: 1}, 'helper224 actual5H1+H4 path')
    last = path[-1]['event']
    later = [i for i, e in enumerate(word['programs']['forward']) if i > last
             and e[0] == 'scalar' and e[1][0] == 'add' and e[1][1] == ['L', 224]]
    need(path[-1] == dict(event=17722, input=279, output=1, rank=1) and later,
         'terminalH1 has later writes; no clean-prefix inference')
    endpoints = []
    for C in (F(30217758, 10**10), F(34, 10**4)):
        powers = {r: power_interval(r, C) for r in (1, 2, 3, 4, 5, 7, 8, 9, 17)}
        split = add_intervals([(112, powers[8]), (112, powers[1]), (-112, powers[9])])
        margin_terms = [(224, powers[17])]
        margin_terms += [(2*n, powers[r]) for r, n in helper.items()]
        margin_terms += [(-2*n, powers[int(r)]) for r, n in profiles['forward'].items()]
        margin = add_intervals(margin_terms)
        leftover = (margin[0]-split[1], margin[1]-split[0])
        endpoints.append(dict(C=str(C), conditional112_split_surcharge=decimal_interval(split),
                              original_optimistic_moment=decimal_interval(margin),
                              conditional_moment_after_unrealized_split=decimal_interval(leftover)))
    result = dict(status='PASS_SOURCE_GATE_NO_PAID_H9_SPLIT',
                  source_commit=sources['source_commit'], paid_profiles=profiles,
                  productive_helpers={str(r): n for r, n in sorted(helper.items())},
                  helper224_paid_path=path, later_scalar_writes_to224=later,
                  rank8_paid_events=rank8_paid_events,
                  native_port0_frames=dict(Y_exit=canonical['final'][112],
                                           helper224_exit=canonical['final'][224],
                                           helper224_preterminal=path[-1]['input']),
                  hypothetical_split_endpoints=endpoints,
                  conditional_surcharge_monotone_in_C=True,
                  accepted_profile_change=False, actual_prefix_access_proved=False,
                  clean_prefix_assumed=False, new_kappa=False,
                  missing_physical_premise='A replaceable paid subword with complete incident contacts and a phase-correct exposed prefix; the productive H9 endpoint is not a paidH9 node.')
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'fixed exact receipt')
    print('PASS_SOURCE_GATE_NO_PAID_H9_SPLIT conditional_surcharge_only '
          'helper224=5H1+H4 later_writes_prefix_unproved no_new_kappa')


if __name__ == '__main__':
    main()
