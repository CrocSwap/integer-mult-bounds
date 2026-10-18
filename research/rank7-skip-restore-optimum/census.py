#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Empirical controls (not part of the proof): the single-gate deletion census of the restore, recomputed completely, and
the tail-exchange census of lane K, whose candidate list is re-derived here and whose stored records are re-checked on a
deterministic sample with this package's exactness test and exact frame solver.

Deletion census: delete one restore gate at a time; keep it if the Lemma 1 end conditions still hold (relaxed semantics:
other final rows free) and price it. Tail-exchange census: for a register r with a restore-phase visit and any other
non-restored, non-target register s with dim(L_r + L_s) <= 8, insert the exact exchange [s += r; r -= s; s += r] at r's
first restore touch or at R0 and relabel the rest of the restore (r <-> s with signs), so that s carries r's restore role;
price every exact candidate. Marius-Paul Dumitrean, with substantial AI assistance (Claude Code).
"""
import argparse
import collections
import copy
import gzip
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frames_exact as FX   # noqa: E402
import restore_bound as RB  # noqa: E402
import verify as VF         # noqa: E402

SAMPLE_EVERY = 25
TAIL_SHA = {'base': '7bfa6fee793b7c7732a21f9d24d6f67029d726b9e4bd646fd6e626ab58e5176d',
            'extra': '7bfa6fee793b7c7732a21f9d24d6f67029d726b9e4bd646fd6e626ab58e5176d'}
TAIL_PINS = {'base': 'evidence/tail-exchange/TAIL-EXCHANGE-3042-base.jsonl.gz',
             'extra': 'evidence/tail-exchange/TAIL-EXCHANGE-3042-extra.jsonl.gz'}


def deletion_census(w, rows, base):
    exact = []
    n = 0
    for i in range(len(w['restore'])):
        x = copy.deepcopy(w)
        g = x['restore'].pop(i)
        fin = RB.run_restore(x['restore'], rows)
        dirty, leaks, targets = RB.end_conditions(x, fin, rows)
        n += 1
        if dirty or leaks or targets:
            continue
        try:
            d = FX.frame_optimum(x)['cost'] - base
        except FX.Infeasible:
            d = None
        exact.append(dict(deleted=i, gate=g[:5], delta=d))
    return dict(deletions=n, exact=len(exact), exact_deletions=exact,
                min_delta=min((e['delta'] for e in exact if e['delta'] is not None), default=None))


def relabel(g, r, s):
    """gate on old registers rewritten after the exchange (new s = old r, new r = -old s); lane K's swapcensus.py"""
    g = list(g)
    if g[0] == 'add':
        t, u, num = g[1], g[2], g[3]
        sgn = 1
        nt = {r: s, s: r}.get(t, t)
        nu = {r: s, s: r}.get(u, u)
        if u == s:
            sgn = -sgn
        if t == s:
            sgn = -sgn
        g[1], g[2], g[3] = nt, nu, num * sgn
    else:
        g[1] = {r: s, s: r}.get(g[1], g[1])
    return g


def exchange(w, r, s, p):
    x = copy.deepcopy(w)
    R0 = w['restore']
    sw = [['add', s, r, 1, 1, list(FX.FULL9)], ['add', r, s, -1, 1, list(FX.FULL9)], ['add', s, r, 1, 1, list(FX.FULL9)]]
    x['restore'] = [list(g) for g in R0[:p]] + sw + [relabel(g, r, s) for g in R0[p:]]
    return x


def tail_jobs(w, lit, LU):
    R = RB.restored(w)
    regs = [q for q, x in sorted(lit.items()) if x['overhead']]
    jobs = []
    for r in regs:
        first = min(i for i, g in enumerate(w['restore']) if r in FX.regs_of(g))
        for s in sorted(LU):
            if s == r or s in R or RB.is_target(s):
                continue
            if len(FX.join(LU[r][0], LU[s][0])) > 8:
                continue
            for p in sorted({first, 0}):
                jobs.append((r, s, p))
    return jobs


def tail_check(prov, w, rows, base, LU, lit):
    raw = (HERE / TAIL_PINS[prov]).read_bytes()
    recs = [json.loads(l) for l in gzip.decompress(raw).decode().splitlines()]
    jobs = tail_jobs(w, lit, LU)
    VF.require(sorted((x['r'], x['s'], x['p']) for x in recs) == sorted(jobs), 'stored census covers exactly the re-derived candidates')
    hist = collections.Counter(x['delta'] for x in recs if x.get('status') == 'ok')
    summary = dict(candidates=len(recs), exact=sum(1 for x in recs if x['clean']), frame_feasible=sum(1 for x in recs if x.get('status') == 'ok'),
                   infeasible=sum(1 for x in recs if x.get('status') == 'infeasible'), not_exact=sum(1 for x in recs if not x['clean']),
                   min_delta=min(hist), negative=sum(v for k, v in hist.items() if k < 0),
                   delta_histogram={str(k): v for k, v in sorted(hist.items())})
    checked = 0
    for i, x in enumerate(sorted(recs, key=lambda y: (y['r'], y['s'], y['p']))):
        if i % SAMPLE_EVERY:
            continue
        y = exchange(w, x['r'], x['s'], x['p'])
        fin = RB.run_restore(y['restore'], rows)
        dirty, leaks, targets = RB.end_conditions(y, fin, rows)
        clean = not dirty and not leaks and not targets
        VF.require(clean == x['clean'], 'exactness of stored candidate %s' % ((x['r'], x['s'], x['p']),))
        if clean:
            try:
                d = FX.frame_optimum(y)['cost'] - base
                status = 'ok'
            except FX.Infeasible:
                d, status = None, 'infeasible'
            VF.require(status == x.get('status') and (d == x.get('delta') or status != 'ok'), 'price of stored candidate %s' % ((x['r'], x['s'], x['p']),))
        checked += 1
    summary['sample_every'] = SAMPLE_EVERY
    summary['sample_rechecked'] = checked
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--work', type=Path)
    a = ap.parse_args()
    t0 = time.monotonic()
    VF.authenticate()
    VF.authenticate(pins={TAIL_PINS['base']: TAIL_SHA['base'], TAIL_PINS['extra']: TAIL_SHA['extra']})
    out = {}
    for prov in ('base', 'extra'):
        w = VF.load_word('3042-' + prov)
        rows = RB.entry_rows(w)
        sol = FX.frame_optimum(w)
        base = sol['cost']
        lit = RB.literal_restore_chains(w)
        Mc, rk = RB.coordinates(rows, {x: {(x, ()): VF.Q(1)} for x in RB.restored(w)})
        caps, _ = RB.forced_caps({x: dict(v) for x, v in Mc.items()}, RB.end_frames(w), RB.restored(w))
        LU = RB.entry_bounds(w, RB.lb_forced(w, caps))
        dele = deletion_census(w, rows, base)
        VF.require(dele['deletions'] == 212 and dele['exact'] == 10 and all(e['delta'] == 0 for e in dele['exact_deletions']), 'deletion census')
        tail = tail_check(prov, w, rows, base, LU, lit)
        VF.require(tail['candidates'] == 8098 and tail['negative'] == 0 and tail['min_delta'] == 0, 'tail-exchange census')
        out[prov] = dict(deletion=dele, tail_exchange=tail)
        print('PASS census', prov, 'deletions', dele['deletions'], 'exact', dele['exact'], 'min delta', dele['min_delta'],
              '| tail exchanges', tail['candidates'], 'exact', tail['exact'], 'feasible', tail['frame_feasible'], 'min delta',
              tail['min_delta'], 'rechecked', tail['sample_rechecked'], flush=True)
    VF.require(out['base'] == out['extra'], 'providers agree')
    text = VF.canonical(out)
    if a.work:
        a.work.mkdir(parents=True, exist_ok=True)
        (a.work / 'CENSUS.json').write_text(text)
    else:
        VF.require((HERE / 'certificates/CENSUS.json').read_text() == text, 'regenerated census differs from certificates/CENSUS.json')
    print('PASS_RANK7_SKIP_RESTORE_CENSUS deletions=212x2 exact=10 tail_exchanges=8098x2 negative=0 (%.1f s)' % (time.monotonic() - t0))


if __name__ == '__main__':
    main()
