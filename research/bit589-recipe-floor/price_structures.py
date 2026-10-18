#!/usr/bin/env python3
"""Price every idle-window structure of a K = 4 recipe search with PR #589's word at nine stages.

For each structure: the stage-compatible hosting programme (recipe_lib.host: every residual hosted, 0 banks, every paid
remainder <= 45) and the exact rational nine-stage c of the pinned moment engine. The best structures and the template
structure are re-solved with the vendored official PR #442 programme (hosting_k.solve, host_all=True, max_remainder=45)
and must give the same objective.
usage: price_structures.py SEARCH.json OUT.json [--jobs N]
Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5, Anthropic, via Claude Code). Apache-2.0."""
import argparse, json, sys, time
from collections import Counter
from fractions import Fraction as Q
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe_lib as RL

L = 9


def solve_one(row):
    w = RL.pr589()
    win = {i: (None, r, frozenset(st)) for i, (r, st) in enumerate(row['windows'])}
    out = RL.host(win, L, 2 * w['v'], w['R'])
    if out is None: return dict(row, hosting='infeasible')
    rem, proxy = out
    return dict(row, hosting='feasible', remainder={str(r): n for r, n in sorted(rem.items())}, proxy=proxy)


def official(row, HK):
    w = RL.pr589()
    win = {i: (None, r, frozenset(st)) for i, (r, st) in enumerate(row['windows']) if st}
    ys, zs, val = HK.solve(win, 2 * w['v'], {(s, 8): w['R'] for s in range(L)}, RL.M9, host_all=True, max_remainder=45)
    rem = Counter()
    for (i, pat), n in ys.items():
        if win[i][1] - sum(pat): rem[win[i][1] - sum(pat)] += n
    for i, (r, st) in enumerate(row['windows']):
        if not st: rem[r] += 2 * w['v']                 # a window with no stage cannot host (dropped by emit_k too)
    return val, rem


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('search', type=Path); ap.add_argument('out', type=Path)
    ap.add_argument('--jobs', type=int, default=1); ap.add_argument('--official-top', type=int, default=5)
    a = ap.parse_args(); t0 = time.time()
    RL.check_pins(); E = RL.moment_engine(); w = RL.pr589()
    S = json.loads(a.search.read_text()); assert S['K'] == 4 and S['stages'] == L
    rows = S['structures']
    with Pool(a.jobs) as pool: res = pool.map(solve_one, rows, chunksize=4)
    feas = sorted((r for r in res if r['hosting'] == 'feasible'), key=lambda r: r['proxy'])
    # template structure
    st, fin = RL.from_template(RL.template_recipe(4), 4)
    tkey = [[r, list(s)] for r, s in RL.structure_key(RL.windows(RL.schedule(st, 4)))]
    for r in feas:
        rem = Counter({int(k): n for k, n in r['remainder'].items()})
        c, up = RL.price(E, RL.global_profile(w['local'], rem, L), 4, L, w['v'], w['cst'])
        r['c'] = str(c); r['c_decimal'] = E.decimal(c)
    feas.sort(key=lambda r: (-Q(r['c']), r['proxy']))
    template = next(r for r in feas if r['windows'] == tkey)
    assert Q(template['c']) == w['c'], 'template structure does not reproduce PR589 c'
    HK = RL.official_hosting(); checks = []
    for r in feas[:a.official_top] + [template]:
        val, rem = official(r, HK)
        own = {int(k): n for k, n in r['remainder'].items()}
        saving_own = sum(RL.f(rr) * 2 * w['v'] for rr, _ in r['windows']) - r['proxy']
        assert abs(val - saving_own) < 1e-6, ('official objective differs', val, saving_own)
        cc, _ = RL.price(E, RL.global_profile(w['local'], rem, L), 4, L, w['v'], w['cst'])
        assert cc == Q(r['c']), ('official selection prices differently', cc, r['c'])
        checks.append(dict(windows=r['windows'], official_saving=val, own_saving=saving_own, same_c=True))
    best = feas[0]; rank = [Q(r['c']) for r in feas]
    need = L * w['R']; reasons = {}
    for r in res:
        cap = sum((rk // 8) * 2 * w['v'] for rk, st in r['windows'] if st)
        r['capacity'] = cap
        if r['hosting'] == 'feasible': why = 'hostable'
        elif cap < need: why = 'total capacity below %d' % need
        elif any(sum((rk // 8) * 2 * w['v'] for rk, st in r['windows'] if s in st) < w['R'] for s in range(L)): why = 'a stage lacks spanning capacity'
        else: why = 'joint stage transport or remainder cap'
        reasons[why] = reasons.get(why, 0) + 1
    segs = {}
    for r in res: segs[len(r['windows'])] = segs.get(len(r['windows']), 0) + 1
    out = dict(status='PASS_RECIPE_STRUCTURES_PRICED', search=dict((k, S[k]) for k in S if k != 'structures'),
               structures=len(rows), hosting_feasible=len(feas), hosting_infeasible=len(rows) - len(feas),
               template=dict(windows=tkey, c=template['c'], position=1 + sum(1 for x in rank if x > Q(template['c']))),
               best=dict(windows=best['windows'], witness=best['witness'], remainder=best['remainder'], c=best['c'], c_decimal=best['c_decimal'],
                         gain_over_pr589=str(Q(best['c']) - w['c']), relative_gain='%.6f%%' % (100 * float(Q(best['c']) / w['c'] - 1))),
               structures_strictly_above_pr589=sum(1 for x in rank if x > w['c']),
               structures_equal_to_pr589=sum(1 for x in rank if x == w['c']),
               distinct_hostable_prices=sorted({str(x) for x in rank}, key=Q, reverse=True),
               max_total_capacity=max(r['capacity'] for r in res), residuals_needed=need,
               outcome=dict(sorted(reasons.items())), idle_segments={str(k): segs[k] for k in sorted(segs)},
               top=[dict(c=r['c'], windows=r['windows'], remainder=r['remainder'], witness=r['witness']) for r in feas[:10]],
               official_crosscheck=checks, all=[dict(c=r.get('c'), hosting=r['hosting'], capacity=r['capacity'], windows=r['windows']) for r in sorted(res, key=lambda r: r['windows'])],
               seconds=round(time.time() - t0, 1))
    a.out.write_text(json.dumps(out, indent=1) + '\n')
    print('   %d structures (idle segments %s): %d hostable with 0 banks; outcome %s; max capacity %d for %d residuals'
          % (len(rows), out['idle_segments'], len(feas), out['outcome'], out['max_total_capacity'], need))
    print('   template c = PR589 c (rank %d); best c = %s (%s); %d equal, %d above PR589; official programme agrees on %d'
          % (out['template']['position'], best['c_decimal'][:28], out['best']['relative_gain'], out['structures_equal_to_pr589'],
             out['structures_strictly_above_pr589'], len(checks)))
