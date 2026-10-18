#!/usr/bin/env python3
"""Replay of research/bit589-recipe-floor (see README.md).

usage: python3 -B research/bit589-recipe-floor/verify.py [OUTDIR] [--jobs N] [--reuse]
  OUTDIR   fresh output directory (default: a new temporary directory)
  --reuse  re-price the committed K = 4 search (data/search-K4.json, hash-checked) instead of re-running the search
           (the full search takes about 25 minutes with 12 jobs; this is the registered generic replay).
Needs numpy and scipy (hosting programme), as research/e8-bit-p111/requirements.txt.
Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0."""
import argparse, hashlib, json, subprocess, sys, tempfile, time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import recipe_lib as RL
import recipe_search as RS


def step(msg): print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out', type=Path, nargs='?')
    ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--reuse', action='store_true')
    ap.add_argument('--record', action='store_true', help='maintainer use: write EXPECTED.json from this run instead of comparing')
    a = ap.parse_args(); t0 = time.time()
    a.out = a.out or Path(tempfile.mkdtemp(prefix='bit589-recipe-floor-')); a.out.mkdir(parents=True, exist_ok=True)
    exp = {} if a.record else json.loads((HERE / 'EXPECTED.json').read_text()); got = {}

    step('0. pinned inputs (moment engine and PR589 EXPECTED.json = the selected assembly pins; global_k, hosting code, frozen selection)')
    got['pins'] = RL.check_pins(); E = RL.moment_engine(); w = RL.pr589()

    step('1. positive control: the template recipe(4) reproduces PR589 nine-stage hosting and c from the recipe alone')
    st, fin = RL.from_template(RL.template_recipe(4), 4)
    assert RL.exchange(RL.product(st, 4, fin), 4) == RL.ident(4)
    assert RL.antidiagonal(RL.product(st, 4), 4)                # its final bridges are a free Levi
    win = RL.windows(RL.schedule(st, 4))
    sel = json.loads((RL.ROOT / 'research/e8-bit-p111-tuned/data/selection9-p111.json').read_text())['bit']
    assert all(s in win[i][2] and wd == 8 for i, wd, s, n in sel['stages'])
    frozen = Counter()
    for i, pat, n in sel['patterns']:
        if win[i][1] - sum(pat): frozen[win[i][1] - sum(pat)] += n
    rem, proxy = RL.host(win, 9, 2 * w['v'], w['R'])
    assert rem == frozen, (rem, frozen)
    P = RL.global_profile(w['local'], rem, 9); assert P == w['profile']
    c, _ = RL.price(E, P, 4, 9, w['v'], w['cst']); assert c == w['c']
    HK = RL.official_hosting()
    ys, zs, val = HK.solve({i: x for i, x in win.items() if x[2]}, 2 * w['v'], {(s, 8): w['R'] for s in range(9)}, RL.M9,
                           host_all=True, max_remainder=45)
    assert abs(val - sel['proxy_saving']) < 1e-6
    got['positive_control'] = dict(windows={str(i): [p, r, sorted(s)] for i, (p, r, s) in win.items()}, remainder={str(k): v for k, v in sorted(rem.items())},
                                   c=str(c), frozen_selection_remainder_equal=True, official_saving=val)
    step('   template windows = frozen PR589 selection windows; remainder %s; c = %s (PR589 exactly); official programme saving %.4f'
         % (dict(sorted(rem.items())), c, val))

    step('2. negative controls')
    ctl = {}
    for j in range(len(st)):                                   # drop each internal bridge
        if st[j][0] is None: continue
        bad = list(st); bad[j] = (None,) + tuple(st[j][1:])
        assert RL.exchange(RL.product(bad, 4, fin), 4) != RL.ident(4) and not RL.antidiagonal(RL.product(bad, 4), 4)
        ctl['drop_bridge_before_stage_%d' % j] = 'rejected'
    for j in range(len(st)):                                   # drop each local (2K locals): no recipe with 8 stages exists
        bad = st[:j] + st[j + 1:]
        assert not RL.antidiagonal(RL.product([(None if (k == 0) else g, p, ty) for k, (g, p, ty) in enumerate(bad)], 4), 4)
        ctl['drop_local_%d' % j] = 'rejected'
    nowin = {i: (p, r, s - {0}) for i, (p, r, s) in win.items()}
    assert RL.host(nowin, 9, 2 * w['v'], w['R']) is None; ctl['stage0_removed_from_all_windows'] = 'hosting infeasible'
    flip = list(st); flip[4] = (flip[4][0], flip[4][1], 'R')
    assert not RL.antidiagonal(RL.product(flip, 4), 4); ctl['flip_local_type_stage4'] = 'rejected'
    assert RL.invariants(RL.ident(4), 4) == (4, 0, 0, 4); ctl['invariants_at_identity'] = [4, 0, 0, 4]
    assert RL.invariants(RL.product(st, 4), 4) == (0, 4, 4, 0); ctl['invariants_at_template_product'] = [0, 4, 4, 0]
    got['negative_controls'] = ctl; step('   %d controls rejected as expected' % len(ctl))

    step('3. local-count floor, finite confirmation (K = 1, 2; PROOF.md has the general proof)')
    r = subprocess.run([sys.executable, '-B', str(HERE / 'floor_check.py'), str(a.out / 'floor.json')], check=True, capture_output=True, text=True)
    print(r.stdout, end=''); got['floor'] = json.loads((a.out / 'floor.json').read_text())

    step('4. exhaustive recipe search, K = 3 (28,464 recipes expected)')
    k3 = RS.run(3, a.jobs, 8, 2, log=False)
    got['search_K3'] = dict(valid_recipes=k3['valid_recipes'], distinct_window_structures=k3['distinct_window_structures'])
    step('   K=3: %d valid recipes, %d window structures' % (k3['valid_recipes'], k3['distinct_window_structures']))

    step('5. exhaustive recipe search, K = 4 (nine stages)')
    committed = HERE / 'data/search-K4.json'
    if a.reuse:
        h = hashlib.sha256(committed.read_bytes()).hexdigest(); assert a.record or h == exp['search_K4_sha256'], h
        search = committed; step('   reusing committed search, sha256 %s' % h)
    else:
        k4 = RS.run(4, a.jobs, 8, 3); search = a.out / 'search-K4.json'
        search.write_text(json.dumps(k4, separators=(',', ':')) + '\n')
        if a.record:
            committed.parent.mkdir(exist_ok=True); committed.write_text(json.dumps(dict(k4, seconds=None), separators=(',', ':')) + '\n')
        same = json.loads(committed.read_text())
        assert {k: v for k, v in k4.items() if k != 'seconds'} == {k: v for k, v in same.items() if k != 'seconds'}, 'fresh search differs from the committed one'
        step('   fresh K=4 search equals the committed data/search-K4.json')
    got['search_K4_sha256'] = hashlib.sha256(committed.read_bytes()).hexdigest()
    s4 = json.loads(search.read_text())
    got['search_K4'] = dict(valid_recipes=s4['valid_recipes'], distinct_window_structures=s4['distinct_window_structures'])

    step('6. price every K = 4 structure (stage-compatible hosting, 0 banks, remainder <= 45, exact rational c)')
    subprocess.run([sys.executable, '-B', str(HERE / 'price_structures.py'), str(search), str(a.out / 'PRICED-K4.json'), '--jobs', str(a.jobs)], check=True)
    pr = json.loads((a.out / 'PRICED-K4.json').read_text())
    got['priced_K4'] = {k: pr[k] for k in ('structures', 'hosting_feasible', 'hosting_infeasible', 'template', 'best', 'structures_strictly_above_pr589',
                                           'structures_equal_to_pr589', 'distinct_hostable_prices', 'max_total_capacity', 'residuals_needed', 'outcome', 'idle_segments')}

    step('7. compare with EXPECTED.json')
    keys = ('pins', 'positive_control', 'negative_controls', 'search_K3', 'search_K4', 'search_K4_sha256', 'priced_K4')
    if a.record:
        (HERE / 'EXPECTED.json').write_text(json.dumps({k: got[k] for k in keys}, indent=1) + '\n'); exp = json.loads((HERE / 'EXPECTED.json').read_text())
    for k in keys:
        assert got[k] == exp[k], (k, got[k], exp[k])
    assert [x['floor_holds'] and x['attained_at_2K_plus_1'] for x in got['floor']] == [True, True]
    (a.out / 'RESULT.json').write_text(json.dumps(got, indent=1) + '\n')
    b = pr['best']
    print('PASS_BIT589_RECIPE_FLOOR floor=2K+1 K3_recipes=%d K4_recipes=%d K4_structures=%d max_capacity=%d hostable=%d best_c=%s equal=%d above_pr589=%d no_new_kappa (%.0fs)'
          % (got['search_K3']['valid_recipes'], s4['valid_recipes'], s4['distinct_window_structures'], pr['max_total_capacity'], pr['hosting_feasible'],
             b['c'], pr['structures_equal_to_pr589'], pr['structures_strictly_above_pr589'], time.time() - t0))


if __name__ == '__main__':
    main()
