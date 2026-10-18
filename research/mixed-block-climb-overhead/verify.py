#!/usr/bin/env python3
"""Mixed charged/free block profiles; a cost-alphabet implication audit only.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The interval engine is Douglas Colkitt's retained PR1240 source, unchanged.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
TARGET = Q(21, 20) * Q(1690054109089, 10**15)
WIDTH, STOCK, IDLE, CAP = 73, Q(896, 9), 1646, 51
INPUTS = {
    'research/complex-local-word-ceiling/ceiling.py',
    'research/complex-rank-one-block-budget/README.md',
    'research/complex-rank-one-block-budget/RESULT.json',
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load_engine():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    live = [v for v in pins['files'] if v['usage'] == 'input']
    require(len(live) == len(INPUTS) and {v['path'] for v in live} == INPUTS,
            'incomplete source inventory')
    authenticated = {}
    for v in live:
        data = (ROOT / v['path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == v['sha256'],
                'source drift: ' + v['path'])
        authenticated[v['path']] = data
    prior = json.loads(authenticated['research/complex-rank-one-block-budget/RESULT.json'])
    require(prior['local_profile'] == {str(r): n for r, n in BASE.items()} and
            Q(prior['target']) == TARGET and prior['idle_mass'] == IDLE and
            prior['rank16_complete_max_extra_integer_rank_mass'] == 10,
            'predecessor model binding')
    frozen = pins['frozen_sources'][0]
    data = (HERE / frozen['local_path']).read_bytes()
    require(hashlib.sha256(data).hexdigest() == frozen['sha256'], 'PR3039 source drift')
    # Execute precisely the authenticated source bytes, without consulting pyc.
    path = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    namespace = {'__name__': 'retained_ceiling', '__file__': str(path)}
    exec(compile(authenticated['research/complex-local-word-ceiling/ceiling.py'],
                 str(path), 'exec'), namespace)
    return namespace['child_cost']


def profile(charged_pairs):
    require(type(charged_pairs) is int and 0 <= charged_pairs <= 6, 'pair domain')
    out = Counter(BASE)
    del out[1]
    out[16] += 150
    out[2] += 2 * charged_pairs  # payload plus fully additional transport
    remainder = 12 - 2 * charged_pairs
    if remainder:
        out[remainder] += 1
    return dict(sorted(out.items()))


def moment(histogram, cost, idle=IDLE, target=TARGET):
    require(type(idle) is int and idle >= 0, 'idle domain')
    out = [Q(0), Q(0)]
    for rank, count in list(histogram.items()) + [(CAP, Q(idle, CAP))]:
        require(type(rank) is int and 1 <= rank <= CAP and count >= 0, 'histogram domain')
        lo, hi = cost(rank, WIDTH, target)
        out[0] += count * lo
        out[1] += count * hi
    return out[0] / STOCK, out[1] / STOCK


def decimal_bounds(bounds, digits=15):
    scale = 10**digits
    lo = (bounds[0] * scale).__floor__()
    hi = (bounds[1] * scale).__ceil__()
    return [str(Q(lo, scale)), str(Q(hi, scale))]


def sign(bounds):
    if bounds[1] < 1:
        return 'pass'
    if bounds[0] > 1:
        return 'fail'
    raise ValueError('interval does not decide strict moment sign')


def result(cost):
    rows = []
    for q in range(7):
        h = profile(q)
        require(sum(r * n for r, n in h.items()) == 5586 + 2*q, 'paid mass')
        bounds = moment(h, cost)
        require(sign(bounds) == ('pass' if q <= 5 else 'fail'), 'mixed boundary')
        # Each charged pair loses relative to its two original singleton calls.
        c1, c2 = cost(1, WIDTH, TARGET), cost(2, WIDTH, TARGET)
        require(2*c2[0] > 2*c1[1], 'individual charged pair must lose')
        rows.append({'charged_pairs': q, 'profile': {str(r): n for r, n in h.items()},
                     'rank_mass': 5586 + 2*q, 'moment': decimal_bounds(bounds),
                     'decision': sign(bounds)})
        require(sign(moment(h, cost, target=Q(1, 99))) == 'fail',
                'rank-one-only planning-target control')

    require(sign(moment(BASE, cost)) == 'fail', 'baseline control')
    unpaid = profile(6)
    unpaid[2] -= 6
    require(sign(moment(unpaid, cost)) == 'pass', 'omitted overhead control')
    require(sign(moment(profile(6), cost, idle=IDLE-12)) == 'pass',
            'illicit idle-credit control')
    checks = ['all_seven_complete_profiles', 'mass_includes_transport',
              'charged_pair_individually_loses', 'unchanged_baseline_fails',
              'omitted_transport_false_pass', 'idle_refund_false_pass',
              'one_over_99_still_fails']
    return {'scope': 'cost-alphabet only; no physical decoder or new kappa',
            'target': str(TARGET), 'stock': str(STOCK), 'width': WIDTH,
            'idle_mass': IDLE, 'idle_rank': CAP, 'rows': rows,
            'maximum_charged_pairs_in_this_family': 5, 'checks': checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    expected = result(load_engine())
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(expected, indent=2) + '\n')
    else:
        actual = json.loads((HERE / 'RESULT.json').read_text())
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'result receipt drift')
    print('PASS_MIXED_BLOCK_OVERHEAD charged_pairs=5 next=6_rejected no_new_kappa')


if __name__ == '__main__':
    main()
