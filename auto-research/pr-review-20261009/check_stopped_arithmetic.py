#!/usr/bin/env python3
"""Independent accounting cross-check for pinned PR104; Apache-2.0.

Maintainer review with OpenAI Codex assistance. Uses the existing maintainer
log/exp enclosure, not the submitted stopped-product implementation.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from collections import Counter
from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from audit_community_candidate import moment


def check(candidate):
    cert = json.loads((candidate/'certificates/stopped-product-network.json').read_text())
    gaps = {}
    for axis, name, saving in (
            ('bit', 'stopped-product-bit-axis.json', Q(4019, 50000000)),
            ('complex', 'stopped-product-complex-input.json', Q(1949, 25000000))):
        row = json.loads((candidate/'certificates'/name).read_text())
        h, R, loss = row['h'], row['R'], row['loss']
        v, m = comb(h, 3), h*h
        N, bank = v*v, v*R
        W = 2*N+2*bank
        H = row['histogram'][:]
        assert H[h] == h
        assert sum(t*n for t, n in enumerate(H)) == h*R+2*loss
        H[h] -= h
        H[1] += h
        assert sum(t*n for t, n in enumerate(H)) == h*R+loss
        children = Counter()
        for width, multiplicity in ((m-h, 2*bank), ((h-1)**2, 2*N),
                                    (h-1, 4*N), (1, N)):
            children[width] += multiplicity
        for t, n in enumerate(H):
            if t and n:
                children[t] += 2*v*n
        counts = cert[axis]['counts']
        assert counts['W'] == W and counts['m'] == m
        assert dict(children) == {int(t): n for t, n in counts['child_multiplicities'].items()}
        mass = sum(t*n for t, n in children.items())
        assert mass == m*W-N+2*v*loss == counts['total_rank']
        lower, upper = moment(m, W, children.items(), saving)
        assert lower <= upper < 1
        gaps[axis] = str(1-upper)
    actual = Q(999, 1000)*Q(4019, 50000000)+Q(1, 1000)*Q(384599, 10**10)
    assert actual == Q(803380799, 10**13) < Q(1, 1000)
    params = {k: Q(v) for k, v in cert['assembly']['parameters'].items()}
    a, b, beta, eta = (params[k] for k in ('a_bit', 'a_complex', 'beta', 'eta'))
    assert a < actual and (1-beta)*b-a == Q(1, 10**10)
    q = a*(1-2*eta)
    c = q*(1+eta)
    eps = (1-eta)/(1+c+q)
    g = eps*q
    r, delta = (g+1-eps)/2, eta/8
    margins = {'original_prefix': 1-eps*(1+c), 'coordinate_movement': a,
               'compact_phase_layer': g, 'bulk_exposure': a,
               'Gaussian_arithmetic': min(1-eps-delta, r-delta),
               'scalar_work': 1-eps-delta, 'dimension': eps}
    assert margins == {k: Q(v) for k, v in cert['assembly']['margins'].items()}
    kappa = Q(cert['kappa'])
    assert min(margins.values()) == g > kappa > Q(1, 2**14)
    assert g < kappa+Q(1, 10**10)
    assert len(cert['assembly']['strict_constraints']) == 47
    assert all(Q(v) > 0 for v in cert['assembly']['strict_constraints'].values())
    assert 4000-Q(51, 25)*(16*28+9*28+17*28) == Q(40024, 25)
    return dict(status='PASS', kappa=str(kappa), moment_gaps_lower=gaps,
                absorption_gap=str(g-kappa), next_1e_minus_10_grid_rejected=True,
                scope='Complete copied-center inventories, independent moments and direct seven-margin identities; physical transfer reviewed separately')


if __name__ == '__main__':
    print(json.dumps(check(Path(sys.argv[1])), indent=2))
