#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Registered failure controls for research/rank7-r1-t740-cap (standard library only, about four to five minutes).

Each control changes one thing and must be rejected (or, for the ablation, must lose the gain):
  no_relocations          ten lockstep copies of PR2979's T74 fill alone (PR3015's allocation): a valid allocation whose root is PR3015's,
                          strictly below the cap (the relocations are what attains it);
  dropped_chain_link      one relocation of an exchange chain omitted: the owner engine rejects the allocation;
  window_violation        one relocated role sent to a same-capacity bin whose window excludes its call;
  family_collision        one relocated role sent to a bin of a family its call already uses;
  stale_profile           the claimed complete profile with one extra rank-1 child;
  tampered_relocations    two relocated roles of different widths exchange destinations: payload pin fails;
  wrong_moment_baseline   the moment auditor fed PR2969's claim instead of PR3015's: authenticated-baseline rejection.
Rohan Arun, with substantial AI assistance (Anthropic Claude). Apache-2.0.
"""
import collections
import json
import shutil
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))
import lift as L  # noqa: E402
import verify as V  # noqa: E402


def main():
    if not __debug__:
        raise SystemExit('refusing python -O: this checker relies on assertions')
    start = time.monotonic()
    V.check_pins()
    providers = V.derive_providers()
    engine = V.load('owners2979_r1_controls', V.SRC / 'allocation/vendor/independent_owners.py')
    plan, template = L.read(V.SRC / 'allocation/vendor/PLAN.json.gz'), L.read(V.SRC / 'allocation/vendor/TEMPLATE.json.gz')
    relocations = L.read(PKG / 'allocation/RELOCATIONS.json')
    expected = L.read(PKG / 'allocation/EXPECTED.json')
    claimed = {int(k): v for k, v in L.read(PKG / 'allocation/PROFILE.json').items()}
    sys.path.insert(0, str(V.SRC / 'tools'))
    import root as R
    cap_lo = Q(L.read(PKG / 'certificates/R1-RELAX-CAP.json')['cap_lower'])
    results = {}

    def build(rel):
        T, order, dispatch, fill, touched = L.build(V.SRC / 'allocation', rel, providers)
        return T, order, {(s, r): p for s, r, p in dispatch}, fill

    def rejected(name, rel, claim=claimed):
        T, order, d, fill = build(rel)
        try:
            engine.check(T, order, fill, d, claim, plan, template, providers)
        except ValueError as error:
            results[name] = 'rejected: ' + str(error)
            return
        raise AssertionError('accepted corrupted allocation: ' + name)

    # ablation: no relocations
    T, order, d, fill = build([])
    result, win, _ = engine.check(T, order, fill, d, None, plan, template, providers)
    prof = {int(k): v for k, v in result['profile'].items()}
    base = {int(k): v for k, v in L.read(PKG / 'comparators/PR3015-PROFILE.json').items()}
    V.need(prof == {r: 10 * n for r, n in base.items()} and prof != claimed, 'lift alone = ten times the PR3015 profile')
    lo, hi = R.kappa_from_profile(prof, T)
    V.need(hi < cap_lo and (lo, hi) == R.kappa_from_profile(base, 74), 'lift alone keeps the PR3015 root below the cap')
    results['no_relocations'] = 'valid allocation, root bracket [%s, %s] below the cap by %.4e' % (lo, hi, float(cap_lo - hi))
    # one omitted chain link: the first relocation whose destination bin also loses a role
    sources = {}
    base_rows = {(r[0], r[1]): (r[2], r[3], r[4]) for r in L.lift_rows(L.read(V.SRC / 'allocation/FILL.json.gz'))}
    for e in relocations:
        sources.setdefault(base_rows[e[0], e[1]], []).append(e)
    link = next(e for e in relocations if tuple(e[2:]) in sources)
    rejected('dropped_chain_link', [e for e in relocations if e is not link])
    # window violation: same capacity, window excludes the call
    e = relocations[0]
    cap = win[e[2], e[3]][0]
    (o, c), _ = next(((k, v) for k, v in win.items() if v[0] == cap and not v[1] < e[0] <= v[2]))
    bad = [list(x) for x in relocations]
    bad[0] = [e[0], e[1], o, c, e[4]]
    rejected('window_violation', bad)
    # family collision: a bin (same window class) of a family already used by the call
    t0 = e[0]
    T_, order_, d_, fill_ = build(relocations)
    used = {(r[2], r[3], r[4]) for r in fill_['rows'] if r[0] == t0 and r[1] != e[1]}
    target = next(b for b in sorted(used) if win[b[0], b[1]][1] < t0 <= win[b[0], b[1]][2])
    bad = [list(x) for x in relocations]
    bad[0] = [e[0], e[1]] + list(target)
    rejected('family_collision', bad)
    # stale profile
    wrong = dict(claimed)
    wrong[1] += 1
    rejected('stale_profile', relocations, wrong)
    # tampered relocations: swap destinations of two roles of different widths
    width = lambda x: providers[d_[tuple(order_[x[0]])]]['widths'][x[1]]
    a = relocations[0]
    b = next(x for x in relocations if width(x) != width(a))
    bad = [list(x) for x in relocations]
    ia, ib = relocations.index(a), relocations.index(b)
    bad[ia] = a[:2] + b[2:]
    bad[ib] = b[:2] + a[2:]
    T2, order2, dispatch2, fill2, touched2 = L.build(V.SRC / 'allocation', bad, providers)
    V.need(L.digest(fill2) != expected['payload_sha256']['FILL.json.gz'], 'tampered relocations change the pinned payload')
    results['tampered_relocations'] = 'rejected: canonical FILL payload differs from allocation/EXPECTED.json'
    # moment auditor with a wrong baseline
    moment = V.load('moment_controls', PKG / 'tools/audit_allocation_moment.py')
    repo = V.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        cand, wrongbase = Path(tmp) / 'candidate', Path(tmp) / 'baseline'
        cand.mkdir()
        wrongbase.mkdir()
        (cand / 'ORDER.json').write_bytes(L.canonical(order_))
        (cand / 'PROFILE.json').write_bytes(L.canonical({str(r): n for r, n in sorted(claimed.items())}))
        shutil.copyfile(V.SRC / 'allocation/baseline/CLAIM.json', wrongbase / 'CLAIM.json')
        shutil.copyfile(V.SRC / 'allocation/baseline/ORDER.json', wrongbase / 'ORDER.json')
        shutil.copyfile(V.SRC / 'allocation/baseline/PROFILE.json', wrongbase / 'PROFILE.json')
        try:
            moment.run(cand, wrongbase)
        except ValueError as error:
            results['wrong_moment_baseline'] = 'rejected: ' + str(error)
        else:
            raise AssertionError('moment auditor accepted an unauthenticated baseline')
    V.need(set(results) == {'no_relocations', 'dropped_chain_link', 'window_violation', 'family_collision', 'stale_profile',
                            'tampered_relocations', 'wrong_moment_baseline'}, 'all controls ran')
    print(json.dumps(results, indent=1, sort_keys=True))
    print('PASS_RANK7_R1_T740_CAP_CONTROLS %d controls %.1f s' % (len(results), time.monotonic() - start))


if __name__ == '__main__':
    main()
