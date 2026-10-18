# SPDX-License-Identifier: Apache-2.0
"""Replay the T37 restoration-deferral note and its negative controls.

Usage: python3 -B research/t37-restoration-deferral/verify.py --work NEW_EMPTY_DIR

Runs census.py and price.py into the new work directory, requires their
outputs to equal the committed CENSUS.json and PRICES.json, and checks that
every negative control is rejected for its stated reason.
Expected last line: PASS_T37_RESTORATION_DEFERRAL_REPLAY
"""
import argparse
import copy
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from common import (HERE, ROOT, SOURCES, coverage_census, gate_registers, load_construction, rank_mass,
                    read_member, require, restoration_census, window_deferral)


def run(script, *args):
    proc = subprocess.run([sys.executable, '-B', str(HERE / script), *map(str, args)],
                          cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    require(proc.returncode == 0, f'{script} failed:\n{proc.stderr}')


def same_json(a, b):
    return json.loads(Path(a).read_text()) == json.loads(Path(b).read_text())


def rejects(name, fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(reason in str(exc), f'control {name} rejected for another reason: {exc}')
        return name
    raise SystemExit(f'FAIL control {name} was accepted')


def consumed_by_cleanup(local):
    """The note's claim: every positive restoration climb is consumed by full-frame cleanup."""
    for r in local['registers']:
        if r['restoration'] > 0:
            require(r['full_cleanup_gates'] > 0, f"unconsumed restoration climb at register {r['register']}")
    return True


def controls():
    template, word = load_construction('T37')
    local = restoration_census(word)
    local_mass = rank_mass(local['paid'])
    W = template['live']
    passed = []

    def coverage_with(mutate):
        t = copy.copy(template)
        t['idle_children'] = copy.deepcopy(template['idle_children'])
        mutate(t)
        cov = coverage_census(t, local_mass, 8)
        require(cov['coverage_values'] == {'73': W}, 'coverage identity fails')

    big = next(i for i, c in enumerate(template['idle_children']) if c['rank'] == 48)
    passed.append(rejects('C1_idle_child_dropped',
                          lambda: coverage_with(lambda t: t['idle_children'].pop(big)), 'coverage identity fails'))
    passed.append(rejects('C2_idle_child_rank_47',
                          lambda: coverage_with(lambda t: t['idle_children'][big].update(rank=47)),
                          'coverage identity fails'))
    passed.append(rejects('C3_idle_child_duplicated',
                          lambda: coverage_with(lambda t: t['idle_children'].append(dict(t['idle_children'][big]))),
                          'coverage identity fails'))
    # C4: delete every full-frame cleanup gate touching one restoration helper.
    victim = next(r['register'] for r in local['registers'] if r['role'] == 'helper' and r['restoration'] > 0)
    early = {i for i, _ in word['early_cleanup']}
    w2 = dict(word)
    keep, remap = [], {}
    for i, g in enumerate(word['cleanup']):
        if i in early or victim not in gate_registers(g):
            remap[i] = len(keep)
            keep.append(g)
    w2['cleanup'] = keep
    w2['early_cleanup'] = [[remap[i], U] for i, U in word['early_cleanup']]
    passed.append(rejects('C4_cleanup_removed_for_one_helper',
                          lambda: consumed_by_cleanup(restoration_census(w2)), 'unconsumed restoration climb'))
    # C5: a 'deferral' that drops the returned coordinates is not coverage preserving.
    restoration = {r['register'] - 2 * local['v']: r['restoration'] for r in local['registers'] if r['role'] == 'helper'}
    H, removed, _ = window_deferral(template, local['paid'], restoration, {9})
    base = Counter()
    for _ in template['calls']:
        base.update(local['paid'])
    for c in template['idle_children']:
        base[c['rank']] += 1
    zero_cost = base - removed

    def mass_neutral(P):
        require(rank_mass(P) == rank_mass(base), 'deferral changes rank mass')
    mass_neutral(H)
    passed.append(rejects('C5_zero_cost_deletion', lambda: mass_neutral(zero_cost), 'deferral changes rank mass'))
    # C6: a corrupted payload pin is rejected before parsing.
    src = SOURCES['constructions']['T37']
    passed.append(rejects('C6_payload_pin', lambda: read_member(ROOT / src['archive'], src['word_member'], '0' * 64),
                          'payload digest mismatch'))
    # C7: a child above the halving cap is rejected by the scenario guard.
    def halving(P):
        require(73 * 73 > 2 * max(P) ** 2, 'halving guard')
    halving(Counter({48: 1}))
    passed.append(rejects('C7_halving_cap', lambda: halving(Counter({52: 1})), 'halving guard'))
    return passed


def price_controls():
    sys.path.insert(0, str(HERE))
    import price
    from fractions import Fraction as Q
    census = json.loads((HERE / 'CENSUS.json').read_text())
    W = census['T37']['coverage']['live']
    H0 = {int(r): n for r, n in census['scenarios']['baseline']['profile'].items()}
    passed = []
    b0 = price.endpoint(H0, W)
    # C8: at the next complex grid point both engines put the moment above one.
    z = b0 + Q(1, 10 ** 24)
    lo, hi = price.MOMENT.moment(H0, 73, W, z, False)
    blo, bhi = price.BASE_TWO.moment(73, W, list(H0.items()), z)
    require(lo > 1 and blo > 1, 'both engines must exceed one at the next endpoint')

    def accept_next():
        require(hi < 1 or bhi < 1, 'next complex endpoint rejected by both engines')
    passed.append(rejects('C8_next_complex_endpoint', accept_next, 'next complex endpoint rejected by both engines'))
    # C9: one extra rank-one child changes the baseline kappa, so the selected pin would fail.
    H1 = dict(H0)
    H1[1] += 1
    k1, _ = price.kappa(price.endpoint(H1, W))
    def pin():
        require(str(k1) == SOURCES['selected_record']['kappa'], 'baseline kappa differs')
    passed.append(rejects('C9_perturbed_baseline', pin, 'baseline kappa differs'))
    return passed


def float_crosscheck(census_path, prices_path):
    """Double-precision bisection that shares no code with the pinned engines."""
    import math
    census = json.loads(Path(census_path).read_text())
    prices = json.loads(Path(prices_path).read_text())
    W, m = census['T37']['coverage']['live'], 73
    bit = float(prices['bit_lower'].split('/')[0]) / float(prices['bit_lower'].split('/')[1])
    for key, row in census['scenarios'].items():
        H = {int(r): n for r, n in row['profile'].items()}
        f = lambda a: sum(r * n / (m * W) * math.exp(a * math.log(m / r)) for r, n in H.items()) - 1
        lo, hi = 0.0, 0.01
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
        exact = prices['scenarios'][key]
        s = min(bit, lo)
        require(abs(lo - float(exact['complex_decimal'])) < 1e-13, f'{key}: float endpoint disagrees')
        require(abs(s / (1 + s) - float(exact['kappa_decimal'])) < 1e-13, f'{key}: float kappa disagrees')
    best = prices['single_helper_deferral']
    H = {int(r): n for r, n in census['single_helper_profiles'][str(best['best_helper'])].items()}
    f = lambda a: sum(r * n / (m * W) * math.exp(a * math.log(m / r)) for r, n in H.items()) - 1
    lo, hi = 0.0, 0.01
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    b = best['best_complex_lower'].split('/')
    require(abs(lo - int(b[0]) / int(b[1])) < 1e-13, 'best single helper: float endpoint disagrees')
    return len(census['scenarios']) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    work = Path(ap.parse_args().work).resolve()
    require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    run('census.py', work / 'CENSUS.json')
    require(same_json(work / 'CENSUS.json', HERE / 'CENSUS.json'), 'CENSUS.json differs from the committed result')
    run('price.py', work / 'CENSUS.json', work / 'PRICES.json')
    require(same_json(work / 'PRICES.json', HERE / 'PRICES.json'), 'PRICES.json differs from the committed result')
    print('float cross-check agrees for', float_crosscheck(work / 'CENSUS.json', work / 'PRICES.json'), 'priced rows')
    template, word = load_construction('T37')
    consumed_by_cleanup(restoration_census(word))
    passed = controls() + price_controls()
    print('controls rejected as expected:', ', '.join(passed))
    print('PASS_T37_RESTORATION_DEFERRAL_REPLAY')


if __name__ == '__main__':
    main()
