#!/usr/bin/env python3
"""Independent arithmetic cross-check of the pinned PR49 follow-up.

Uses the maintainer's rational enclosures, without importing contributor code.
Finite counts remain inputs, justified by the separate full producer replay.
Run with --candidate-root pointing at PR49 f95d2910, then --check the receipt.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from audit_community_candidate import moment, require


def run(root):
    path = root / 'research/climbed-48/certificate.json'
    data = json.loads(path.read_text())
    moments = {}
    for name in ('bit', 'complex'):
        item = data[name]
        counts = item['counts']
        entries = (counts['child_multiplicities'].items() if name == 'bit'
                   else item['child_width_multiplicities'])
        lo, hi = moment(counts['m'], counts['W'], entries, Q(item['saving']))
        require(hi < 1, name + ' moment does not contract')
        moments[name] = dict(lower=str(lo), upper=str(hi), gap_lower=str(1-hi))
    counts = data['bit']['counts']
    a = Q(data['bit']['saving'])
    require(tuple(counts[k] for k in ('m', 'W', 'N', 'L', 'deficit')) ==
            (575, 177284805, 4073300, 2226400, 1846900), 'finite constants')
    require(sum(int(t)*n for t, n in counts['child_multiplicities'].items()) ==
            counts['total_rank'] == counts['W']*575-1846900, 'rank mass')
    next_lo, _ = moment(counts['m'], counts['W'],
                        counts['child_multiplicities'].items(), a+Q(1, 10**14))
    require(next_lo > 1, 'next bit-saving grid negative control')
    p = {k: Q(v) for k, v in data['assembly']['parameters'].items()}
    h = p['h']
    q = a*(1-2*h)
    eps, c = (1-h)/(1+q), q+h/4
    G = eps*q
    r, delta = (G+1-eps)/2, h/8
    require(0 < q < a < (1-p['beta'])*p['a_complex'] < p['a_complex'] < 1,
            'layer/stopping ordering')
    require(c > q and 1-eps*(1+c) > 0 and eps+r < 1 and eps > (1-r)/2 and eps > a,
            'geometric, analytic and router conditions')
    require(tuple(p[k] for k in ('epsilon', 'c', 'q', 'alpha_squared_power', 'delta')) ==
            (eps, c, q, r, delta), 'parameter transcription')
    margins = [1-eps, a, G, a, min(1-eps-delta, r-delta), 1-eps-delta, eps]
    require(margins == [Q(data['assembly']['margins']['g'+str(i)]) for i in range(1, 8)],
            'margin transcription')
    kappa = Q(data['kappa'])
    require(min(margins) == G > kappa > Q(1, 2**15) and kappa < Q(1, 2**14),
            'headline comparison')
    require(G-kappa == Q(data['assembly']['absorption_gap']), 'absorption gap')
    slacks = data['assembly']['constraints']
    require(len(slacks) == 47 and all(Q(v) > 0 for v in slacks.values()), '47 strict slacks')
    return dict(candidate_commit='f95d2910e027495983b53cae1693cf535abf2569',
                certificate_sha256=sha256(path.read_bytes()).hexdigest(),
                independent_arithmetic_source_sha256=sha256(
                    Path(__file__).with_name('audit_community_candidate.py').read_bytes()).hexdigest(),
                moments=moments, next_bit_grid_moment_lower=str(next_lo),
                kappa=str(kappa), ratio_to_published_pr39=str(kappa/Q(971668963, 25000000000000)),
                margins=list(map(str, margins)), absorption_gap=str(G-kappa),
                scope='Independent rational log/exp bounds and direct assembly arithmetic; '
                      'finite counts supplied by the separately replayed certificate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    receipt = run(args.candidate_root)
    if args.check:
        require(receipt == json.loads(args.check.read_text()), 'receipt mismatch')
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print('PASS independent PR49 moments, rank mass, seven margins and strict arithmetic')
