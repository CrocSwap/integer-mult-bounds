#!/usr/bin/env python3
"""Exact certificate for optimal carrier matching on RaD's fixed-basis graphs.

Everything except the carrier matching and the h=25 summand order is PR #43
(Chafik Boukhalfa, research/copied-fixed): geometry and data corners (with its
ten conservatively charged fallbacks), copied centers, paid endpoint
corrections, complex layer, balanced assembly. The bit child list is rebuilt
from this directory's replayed original/profile JSON.
Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR43 = ROOT/'research/copied-fixed'
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(PR43))
_spec = importlib.util.spec_from_file_location('pr43_verify', PR43/'verify.py')
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
from balanced_assembly import assembly, cutoffs  # noqa: E402  (PR #43 / PR #34 audit)

require, read, moment, js = base.require, base.read, base.moment, base.js
AB = Q(4100797413, 10**14)
KAPPA = Q(2050314627, 50000000000000)
AC = base.AC
PR43_KAPPA = Q(409953, 10**10)
PR43_AB = Q(409970, 10**10)


def profile():
    a, b = 23, 25
    m = a*b
    rows = [read(HERE/f'original-{h}.json') for h in (a, b)]
    N = comb(a, 3)*comb(b, 3)
    W = 2*N+sum(N//r['v']*r['R'] for r in rows)
    L = sum(N//r['v']*r['loss'] for r in rows)
    data = base.data_corners()
    good, bad = data['good'], data['fallback']
    parts = {'data': Counter({1: 2*(9*good+47*bad), 21: 2*good, 17: 2*good, 481: 2*N}),
             'paid_endpoint_copy': Counter({1: N})}
    for row in rows:
        h = row['h']
        require(row['v'] == comb(h, 3) and row['R'] == row['c']+row['q']-row['matched'], 'Role allocation')
        require(row['loss'] == h*(h-1), 'Retained center loss')
        require(sum(r*n for r, n in enumerate(row['histogram'])) == h*row['R']+2*row['loss'], 'Rank mass')
        f = read(HERE/f'profiles-{h}.json')
        for key in ('h', 'v', 'R', 'loss', 'rank_sum'):
            require(f[key] == row[key], 'Fixed/original mismatch: '+key)
        require(f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1, 'Invalid CRT profile')
        blocks = f['blocks'][:]
        require(len(blocks) == h+1 and blocks[h] == h, 'Exactly h full center cleanup calls expected')
        blocks[h] -= h
        blocks[1] += h
        require(sum(t*n for t, n in enumerate(blocks)) == h*row['R']+row['loss'], 'Copied profile mass')
        rep = N//row['v']
        bank = rep*row['R']
        parts[f'internal_{h}'] = Counter({t: n*rep for t, n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank})
        parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
    hist = sum(parts.values(), Counter())
    s = sum(t*n for t, n in hist.items())
    require(s == W*m-N+L == 102565738275, 'Complete rank mass')
    require((m, N, W, L) == (575, 4073300, 178378409, 2226400), 'Physical constants (same roles as PR #43)')
    require(max(hist) == 529 and all(0 < t < m and n > 0 for t, n in hist.items()), 'Proper children')
    return dict(m=m, N=N, W=W, L=L, total_rank=s, deficit=W*m-s, maxchild=max(hist),
                child_multiplicities=dict(sorted(hist.items())), parts=parts)


def excluded(name):
    c = read(HERE/name)
    rows = {int(t): n for t, n in c['child_multiplicities'].items()}
    lower = moment(c['m'], c['W'], rows, AB)['lower']
    require(lower > 1, name+' network not excluded at new saving')
    return lower


def run():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    p = profile()
    exact = moment(p['m'], p['W'], p['child_multiplicities'], AB)
    require(exact['upper'] < 1, 'Bit characteristic failed')
    nxt = moment(p['m'], p['W'], p['child_multiplicities'], AB+Q(1, 10**14))
    require(nxt['lower'] > 1, 'Next bit grid point unexpectedly certified')
    prior = base.baseline.certificate()
    phase = prior['complex']['counts']
    phase_row = read(ROOT/'certificates/copied-centers-complex-input.json')
    bridge = base.baseline.finite_bridge(p, phase, [phase_row, phase_row])
    final = assembly(bridge, AB, KAPPA, a_complex=AC)
    eventual = cutoffs(bridge, final)
    try:
        assembly(bridge, AB, KAPPA+Q(1, 10**14), a_complex=AC)
    except (AssertionError, ValueError):
        pass
    else:
        raise ValueError('Next kappa grid point unexpectedly accepted')
    controls = {name: excluded(name) for name in
                ('comparison-pr43.json',)}
    controls.update({name: excluded('../copied-fixed/'+name) for name in
                     ('comparison-pr40.json', 'comparison-pr41.json', 'comparison-pr42.json')})
    require(KAPPA > PR43_KAPPA > base.PR42_KAPPA > base.PR41_KAPPA > Q(1, 2**15), 'Comparison failed')
    require(KAPPA < Q(1, 2**14), 'Unexpected power-of-two bracket')
    own = sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.cpp'))+sorted(HERE.glob('*.uses'))
    own += [HERE/f'{k}-{h}.json' for h in (23, 25) for k in ('original', 'profiles')]
    own += [HERE/'comparison-pr43.json']
    return dict(status='Conditional exact arithmetic witness; general transfer proofs are inherited dependencies',
                kappa=KAPPA, bit=dict(counts=p, **exact), next_bit_grid_lower=nxt['lower'],
                complex=prior['complex'], finite_bridge=bridge, assembly=final, eventual_bounds=eventual,
                comparison=dict(PR43=PR43_KAPPA, PR42=base.PR42_KAPPA, PR41=base.PR41_KAPPA,
                                ratio_PR43=KAPPA/PR43_KAPPA, ratio_PR42=KAPPA/base.PR42_KAPPA,
                                dyadic_corollary='2^-15', next_dyadic_not_reached='2^-14'),
                exclusion_lower_moments=controls,
                local_sha256={str(f.relative_to(ROOT)): sha256(f.read_bytes()).hexdigest() for f in own},
                scope='Pinned max-weight maximum carrier matchings on RaD alternating graphs with descending '
                      'summand order at both dimensions; fixed I+J profiles; everything else PR #43. '
                      'Matching legality and the physical timeline are replayed by producer.py with PR #43 checkers. '
                      'No global optimality claim beyond these finite graphs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(js(result), indent=2, sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB))
    print('47 strict inequalities; seven margins; next grid points rejected; PR40-43 networks excluded')
