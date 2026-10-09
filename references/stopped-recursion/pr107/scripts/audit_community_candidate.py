#!/usr/bin/env python3
"""Maintainer arithmetic cross-check of the pinned PR39 certificate.

Uses no producer/checker imports. Counts are inputs, not proved by this script.
80-term rational logarithms and 12-term exponentials independently enclose
the two moments. The accompanying written review addresses their realization.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRID = 10**30


def require(condition, message):
    if not condition:
        raise ValueError(message)


def log_unit(x):
    require(1 <= x <= 2, "logarithm range")
    z = (x-1)/(x+1)
    lo = 2*sum((z**(2*j+1)/(2*j+1) for j in range(80)), Q(0))
    return lo, lo+2*z**161/(161*(1-z*z))


def log_bounds(x):
    k = 0
    while x > 2:
        x /= 2
        k += 1
    lo, hi = log_unit(x)
    l2, u2 = log_unit(Q(2))
    lo, hi = lo+k*l2, hi+k*u2
    # Outward rational rounding keeps later certificates compact.
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)


def exp_bounds(x):
    require(0 <= x < 1, "exponential range")
    term = total = Q(1)
    for j in range(1, 13):
        term *= x/j
        total += term
    tail = term*x/13/(1-x/14)
    return total, total+tail


def moment(m, W, entries, saving):
    lo = hi = Q(0)
    for t, count in entries:
        t, count = int(t), int(count)
        require(0 < t < m and count > 0, "improper child")
        l, u = log_bounds(Q(m, t))
        lower = exp_bounds(saving*l)[0]
        upper = exp_bounds(saving*u)[1]
        lo += Q(t*count, m*W)*lower
        hi += Q(t*count, m*W)*upper
    return Q((lo*GRID).__floor__(), GRID), Q((hi*GRID).__ceil__(), GRID)


def run():
    path = ROOT/'research/copied-fixed-reversed/certificate.json'
    raw = path.read_bytes()
    data = json.loads(raw)
    moments = {}
    for name in ('bit', 'complex'):
        item = data[name]
        counts = item['counts']
        entries = (counts['child_multiplicities'].items() if name == 'bit'
                   else item['child_width_multiplicities'])
        lo, hi = moment(counts['m'], counts['W'], entries, Q(item['saving']))
        require(hi < 1, name+' moment does not contract')
        moments[name] = dict(lower=str(lo), upper=str(hi), gap_lower=str(1-hi))
    bit = data['bit']
    counts = bit['counts']
    next_lower, _ = moment(counts['m'], counts['W'],
                           counts['child_multiplicities'].items(),
                           Q(bit['saving'])+Q(1, 10**14))
    require(next_lower > 1, 'next bit-saving grid negative control')
    p = {k: Q(v) for k, v in data['assembly']['parameters'].items()}
    a, b, h, beta = (p[k] for k in ('a_bit', 'a_complex', 'h', 'beta'))
    q = a*(1-2*h)
    eps, c = (1-h)/(1+q), q+h/4
    G = eps*q
    r, delta = (G+1-eps)/2, h/8
    require(0 < q < a < (1-beta)*b < b < 1, 'layer/stopping ordering')
    require(c > q and 1-eps*(1+c) > 0, 'reservation/geometry')
    require(eps+r < 1 and eps > (1-r)/2 and eps > a, 'analytic/router ranges')
    require(p['epsilon'] == eps and p['c'] == c and p['q'] == q
            and p['alpha_squared_power'] == r and p['delta'] == delta,
            'parameter transcription')
    margins = [1-eps, a, G, a, min(1-eps-delta, r-delta), 1-eps-delta, eps]
    require(margins == [Q(data['assembly']['margins']['g'+str(j)])
                        for j in range(1, 8)], 'margin transcription')
    require(min(margins) == G > p['kappa'] > Q(1, 2**15), 'headline comparison')
    require(G-p['kappa'] == Q(data['assembly']['absorption_gap']), 'absorption')
    ref = ROOT/'references/semantic-bulk/rad20'
    manifest = json.loads((ref/'SOURCE.json').read_text())['source_sha256']
    for name, digest in manifest.items():
        require(sha256((ref/name).read_bytes()).hexdigest() == digest, 'source: '+name)
    return dict(candidate_commit='70ae24129649f6d6d4ec6360962a80c3c42a38f1',
                certificate_sha256=sha256(raw).hexdigest(), moments=moments,
                next_bit_grid_moment_lower=str(next_lower),
                kappa=str(p['kappa']), ratio_to_dyadic_15=str(p['kappa']*2**15),
                margins=list(map(str, margins)), absorption_gap=str(G-p['kappa']),
                complete_rad_manifest_files=len(manifest),
                scope='Independent arithmetic/source cross-check; finite counts and '
                      'general proof obligations are addressed in the written review.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path, help='Compare with an existing audit receipt')
    args = parser.parse_args()
    receipt = run()
    if args.check:
        require(receipt == json.loads(args.check.read_text()), 'audit receipt differs')
    result = json.dumps(receipt, indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(result)
    elif args.check:
        print('PASS independent moments, seven margins and all 32 RaD source hashes')
    else:
        print(result, end='')
