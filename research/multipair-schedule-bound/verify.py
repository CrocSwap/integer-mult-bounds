#!/usr/bin/env python3
"""Bounded verification for research/multipair-schedule-bound (standard library only, about 1 minute).

Checks:
  1. lemma_check.py: the per-stage inequalities of the Theorem S proof on random reachable states over
     GF(2), GF(3), GF(5), with two false-strengthening controls that must fail somewhere.
  2. chains_replay.py: exact rational replay of seven parallel-chain schedules (signed exchange endpoint,
     stage shapes, N = Theorem S bound where claimed, B_4 idle windows {8:6,16:4,32:4,48:4}); its stdout
     must equal CHAINS-REPLAY.jsonl byte for byte.
  3. sched_search.py K = 2, mixed and alternating stages, N_max 8, s <= 6: exhaustive frontier equals
     the Theorem S bound for every s >= 3; outputs equal search/K2_*.json.
  4. price_families.py --check: every family profile, its exact moment bracket and packing ceiling are
     recomputed from inputs/T74-WORDS.json with the retained engine and equal the committed files.
Controls (each must be rejected):
  a. a chain recipe with one call sign flipped fails the exact endpoint check;
  b. a T74 extract with one rank-1 child moved to rank 2 fails the published-profile recomposition;
  c. a claimed schedule with N one below the Theorem S bound (family F12) is recorded as excluded and
     no attained family lies below the bound.
Long searches (K = 3) are not rerun here; their committed outputs are listed in README.md.
"""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(*args):
    out = subprocess.run([PY, '-B', *args], cwd=HERE, capture_output=True, text=True)
    assert out.returncode == 0, (args, out.stderr[-2000:])
    return out.stdout


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bound(K, s):
    return 2 * K + -(-2 * K // (s - 1))


def main():
    assert __debug__, 'run with assertions enabled'
    out = run('lemma_check.py')
    assert out.strip().endswith('PASS_THEOREM_S_LEMMAS checks=10697'), out[-300:]
    print('PASS lemma inequalities (10697 stages, both controls fail as required)')

    out = run('chains_replay.py')
    assert out == (HERE / 'CHAINS-REPLAY.jsonl').read_text(), 'chain replay differs from CHAINS-REPLAY.jsonl'
    rows = [json.loads(line) for line in out.splitlines()[:-1]]
    assert all(r['N'] >= r['theorem_S_bound'] for r in rows)
    assert rows[0]['idle_windows_per_port'] == {'8': 6, '16': 4, '32': 4, '48': 4}
    print('PASS chain replay (7 schedules, exact endpoints, B_4 windows)')

    for flag, ref in (([], 'search/K2_mixed.json'), (['--alternating'], 'search/K2_alternating.json')):
        out = run('sched_search.py', '2', '8', '6', *flag)
        assert out == (HERE / ref).read_text(), ref
        front = json.loads(out.splitlines()[-1])['frontier']
        for row in front:
            if row['s'] >= 3:
                assert row['min_N_at_most_s'] == row['theorem_S_bound'] == bound(2, row['s']), row
    print('PASS exhaustive K=2 frontier = Theorem S bound (mixed and alternating stages)')

    out = run('price_families.py', '--check')
    assert out.strip().endswith('PASS_F1_PRICES families=14'), out[-300:]
    fam = json.loads((HERE / 'FAMILIES.json').read_text())
    by = {f['id']: f for f in fam['families']}
    assert by['F01']['b_lower'] == fam['T74_b_bracket'][0] and by['F05']['b_lower'] == fam['T74_b_bracket'][0]
    assert not any(f.get('beats_T74') for f in fam['families'] if f['status'].startswith('attained'))
    print('PASS family prices recomputed (attained schedules never beat T74; best attained = T74 exactly)')

    # control a: flipped call sign
    cr = load('chains_replay')
    orig = cr.chain_ops

    def broken(k, base, forward):
        ops, length = orig(k, base, forward)
        ops = list(ops)
        op = ops[1]
        assert op[0] == 'call'
        ops[1] = op[:4] + (-op[4],) + op[5:]
        return ops, length
    cr.chain_ops = broken
    try:
        cr.check([(4, True)])
    except AssertionError:
        pass
    else:
        raise AssertionError('control a: flipped sign accepted')
    cr.chain_ops = orig
    print('PASS control a (flipped call sign rejected)')

    # control b: perturbed T74 extract
    pf = load('price_families')
    data = json.loads((HERE / 'inputs/T74-WORDS.json').read_text())
    bad = copy.deepcopy(data)
    p = bad['words']['extra']['actual_paid_profile']
    p['1'] -= 1
    p['2'] = p['2'] + 1
    bad['words']['extra']['helper_width_total'] += 1
    try:
        pf.words(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('control b: perturbed extract accepted')
    print('PASS control b (perturbed T74 extract rejected)')

    # control c: below-bound schedules are only ever excluded
    for f in fam['families']:
        b = bound(f['K'], f['s'])
        if f['N'] < b:
            assert f['status'].startswith('EXCLUDED'), f['id']
        if f['status'].startswith('attained'):
            assert f['N'] >= b, f['id']
    assert by['F12']['N'] == bound(8, 9) - 1 and by['F12']['status'].startswith('EXCLUDED')
    print('PASS control c (F12 at bound - 1 is excluded; no attained family below the bound)')
    print('PASS_MULTIPAIR_SCHEDULE_BOUND')


if __name__ == '__main__':
    main()
