#!/usr/bin/env python3
"""Exact certificate for the descent-improved climbed orders.

Same composition as research/climbed-48 (PR #48 geometry, data corners, copied
centers, complex layer and balanced assembly; orders searched by a full
single-bit descent rather than a greedy climb).  The new bit saving and kappa
are derived here from the searched rows and their certified profiles instead of
being pinned constants:
  * the bit saving is the largest 1e-14 grid point whose moment still contracts,
  * kappa is the largest 1e-14 grid point the assembly accepts,
  * every earlier pinned network is re-excluded at the new saving, which is what
    makes the improvement strict.
"""
from collections import Counter
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR43 = ROOT / 'research' / 'copied-fixed'
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(PR43))
_spec = importlib.util.spec_from_file_location('pr43_verify', PR43 / 'verify.py')
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
from balanced_assembly import assembly, cutoffs  # noqa: E402

require, read, moment, js = base.require, base.read, base.moment, base.js
AC = base.AC
GRID = Q(1, 10**14)
BOUND = 10**11                       # 1e-3 in grid units, above any plausible root
PR49_KAPPA = Q(4123863984, 10**14)
PR49_W = 177284805
PR49_BIT = Q(4124034054, 10**14)


def profile():
    a, b = 23, 25
    m = a * b
    rows = [read(HERE / ('original-%d.json' % h)) for h in (a, b)]
    N = comb(a, 3) * comb(b, 3)
    W = 2 * N + sum(N // r['v'] * r['R'] for r in rows)
    L = sum(N // r['v'] * r['loss'] for r in rows)
    data = base.data_corners()
    good, bad = data['good'], data['fallback']
    parts = {'data': Counter({1: 2 * (9 * good + 47 * bad), 21: 2 * good,
                             17: 2 * good, 481: 2 * N}),
             'paid_endpoint_copy': Counter({1: N})}
    for row in rows:
        h = row['h']
        require(row['v'] == comb(h, 3) and row['R'] == row['c'] + row['q'] - row['matched'],
                'Role allocation')
        require(row['loss'] == h * (h - 1), 'Retained center loss')
        require(sum(r * n for r, n in enumerate(row['histogram'])) == h * row['R'] + 2 * row['loss'],
                'Rank mass')
        f = read(HERE / ('profiles-%d.json' % h))
        for key in ('h', 'v', 'R', 'loss', 'rank_sum'):
            require(f[key] == row[key], 'Fixed/original mismatch: ' + key)
        require(f['crt_disagreements'] == 0 and f['field_prime'] == 2**61 - 1,
                'Invalid CRT profile')
        blocks = f['blocks'][:]
        require(len(blocks) == h + 1 and blocks[h] == h,
                'Exactly h full center cleanup calls expected')
        blocks[h] -= h
        blocks[1] += h
        require(sum(t * n for t, n in enumerate(blocks)) == h * row['R'] + row['loss'],
                'Copied profile mass')
        rep = N // row['v']
        bank = rep * row['R']
        parts['internal_%d' % h] = Counter({t: n * rep for t, n in enumerate(blocks) if t and n})
        parts['exterior_%d' % h] = Counter({h: bank, m - 2 * h: bank})
        parts['data_growth_%d' % h] = Counter({1: 2 * N, h - 2: 2 * N})
    hist = sum(parts.values(), Counter())
    s = sum(t * n for t, n in hist.items())
    require(s == W * m - N + L, 'Complete rank mass')
    require((m, N, L) == (575, 4073300, 2226400), 'Physical constants')
    require(W < PR49_W, 'Role volume must undercut PR #49')
    require(max(hist) == 529 and all(0 < t < m and n > 0 for t, n in hist.items()),
            'Proper children')
    return dict(m=m, N=N, W=W, L=L, total_rank=s, deficit=W * m - s, maxchild=max(hist),
                child_multiplicities=dict(sorted(hist.items())), parts=parts)


def grid_max(predicate):
    """Largest k/1e14 with predicate(k/1e14) true (predicate monotone)."""
    lo, hi = 1, BOUND
    require(predicate(Q(lo, 10**14)), 'predicate fails at the first grid point')
    require(not predicate(Q(hi, 10**14)), 'search bound must fail')
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if predicate(Q(mid, 10**14)):
            lo = mid
        else:
            hi = mid
    require(predicate(Q(lo, 10**14)) and not predicate(Q(hi, 10**14)), 'grid bracket')
    return Q(lo, 10**14)


def excluded(name, ab):
    c = read(HERE / name)
    if 'child_multiplicities' not in c:
        c = c['bit']['counts']
    rows = {int(t): n for t, n in c['child_multiplicities'].items()}
    lower = moment(c['m'], c['W'], rows, ab)['lower']
    require(lower > 1, name + ' network not excluded at the new saving')
    return lower


def run():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    p = profile()
    ab = grid_max(lambda x: moment(p['m'], p['W'], p['child_multiplicities'], x)['upper'] < 1)
    exact = moment(p['m'], p['W'], p['child_multiplicities'], ab)
    require(exact['upper'] < 1, 'Bit characteristic failed')
    require(moment(p['m'], p['W'], p['child_multiplicities'], ab + GRID)['lower'] > 1,
            'Next bit grid point unexpectedly certified')
    prior = base.baseline.certificate()
    phase = prior['complex']['counts']
    phase_row = read(ROOT / 'certificates' / 'copied-centers-complex-input.json')
    bridge = base.baseline.finite_bridge(p, phase, [phase_row, phase_row])

    def accepts(k):
        try:
            assembly(bridge, ab, k, a_complex=AC)
        except (AssertionError, ValueError):
            return False
        return True

    kappa = grid_max(accepts)
    final = assembly(bridge, ab, kappa, a_complex=AC)
    eventual = cutoffs(bridge, final)
    require(not accepts(kappa + GRID), 'Next kappa grid point unexpectedly accepted')
    require(kappa > PR49_KAPPA, 'Must strictly improve on PR #49')
    require(ab > PR49_BIT, 'Bit saving must strictly improve on PR #49')
    require(kappa < Q(1, 2**14), 'Unexpected power-of-two bracket')
    controls = {'comparison-climbed48.json': excluded('comparison-climbed48.json', ab),
                'comparison-pr48.json': excluded('comparison-pr48.json', ab)}
    for name in ('comparison-pr40.json', 'comparison-pr41.json', 'comparison-pr42.json',
                 'comparison-pr43.json', 'comparison-pr44.json', 'comparison-pr46.json',
                 'comparison-pr47.json'):
        if (HERE / name).exists():
            controls[name] = excluded(name, ab)
    return dict(status='Conditional exact arithmetic witness for a searched-order variant',
                kappa=kappa, bit=dict(counts=p, grid_point=str(ab), **exact),
                complex=prior['complex'], finite_bridge=bridge, assembly=final,
                eventual_bounds=eventual,
                comparison=dict(PR49=PR49_KAPPA, ratio_PR49=kappa / PR49_KAPPA,
                                PR49_bit=PR49_BIT, bit_ratio=ab / PR49_BIT,
                                dyadic_corollary='2^-15', next_dyadic_not_reached='2^-14'),
                exclusion_lower_moments={k: js(v) for k, v in controls.items()},
                scope='Searched orders on PR #48 graphs; fixed I+J profiles; everything else '
                      'PR #48. Matching legality, the physical timeline and the profile replay '
                      'are producer.py checks. No global optimality claim.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    text = js(result)
    if args.output:
        args.output.write_text(json.dumps(text, indent=2, sort_keys=True) + '\n')
    print('PASS searched-order kappa=%s bit saving=%s'
          % (result['kappa'], result['bit']['grid_point']))
