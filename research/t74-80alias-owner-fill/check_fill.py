#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Legality recount and certified price of OWNERS-80.json.gz (80-alias T74 owner fill).

This checker does not import build_fill.py.  It runs our own iteration-3 independent checker
(vendor/iter3/fill_check.py, commit 4a2f20ea, verbatim; written for PR #2269's 437-helper fill) on the new
400-helper fill:

  X1   windows are rebuilt from the 30 source events of PR #2269's GLOBAL-TEMPLATE.json.gz expanded in
       ORDER.json (bridge-aware), and must equal PR #2269's new/PLAN.json windows exactly;
  R-a  one role per (call, live helper); helper i = i-th live register of BORROW-WORD-80{base,extra};
       widths re-derived from the words (GF(2) ranks);
  R-e  family = owner*896 + (2*pair+side)*112 + port, copy = 112*owner + port, inside [0, 896*T); never the
       caller's active pair; at most one helper per family per call;
  R-d  every call strictly inside the owner's rebuilt window;
  R-b  slices inside the child rank, disjoint per bin, occupied prefix;
  R-c  idle remainders and global profile = 249*P_gauge44 + 417*P_extra + idle recounted and compared with
       PROFILE-80.json / BUILD-RECEIPT.json; rank mass 73*66304 - 23680; halving guard 73^2 > 2*48^2.

One adaptation: PR #2269's PLAN per_call_widths list the 437-helper widths, so the PLAN width check of
fill_check.check_static is replaced by widths re-derived from the 80-alias words (everything else of
check_static, including X1, is kept).  The 12 negative controls of fill_check.controls are run against the
new fill.  Price: the certified moment-root bracket of vendor/iter3/price_check.py (Evaluator, 800-bit
directed rounding) on the recounted profile (native complex side, no surcharge).

Credits: PR2339 (this author); PR2269 Jeremy Kothe (template, windows, dispatch, owner-row format);
PR2322 Vlado Vojdanovski; PR2312/PR2302 jeremykothe2; PR2226 Cinna Davis; PR1319/PR1297 T74 lineage
(Rohan Arun et al.); rules from PR858 / complex-double-replica-owners PROOF.md and the T16 owner audit.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage: python3 -I -B check_fill.py [--repo PATH] [--out]
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction

if not __debug__:
    sys.exit('refusing to run under python -O')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
HEAD_2339 = 'bf1742aee4d855efb8bbd44a8419eddb33a679e5'
WORDS = {'gauge44': ('research/t74-low-alias-borrowing/words/BORROW-WORD-80base.json.gz',
                     'c5953dfdb0ee9ac0c2c73eb29e320582b4569d2b',
                     '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493'),
         'extra': ('research/t74-low-alias-borrowing/words/BORROW-WORD-80extra.json.gz',
                   '852868543ed36efa799b3ed6dd76a0442b0d6ff1',
                   '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5')}
VENDOR = {'fill_check.py': ('3a5a5ff893ea2fac77e3dec66fbf05b204783ebd',
                            '6b0e5950876da81238096f29c75ff9b52d6ae6f96435203d46a75e28c7ab8cd6'),
          'price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                             '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f')}
CLAIM_2269 = Fraction('0.0016962471390584742207696225394800943861')
CLAIM_2322 = Fraction('0.001697060296258836')
DIGITS = 40


def vendored(name):
    path = os.path.join(HERE, 'vendor', 'iter3', name)
    data = open(path, 'rb').read()
    oid, sha = VENDOR[name]
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == oid, name
    assert hashlib.sha256(data).hexdigest() == sha, name
    spec = importlib.util.spec_from_file_location('iter3_' + name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    F = vendored('fill_check.py')
    P = vendored('price_check.py')
    # ---- PR2269 inputs through the iteration-3 pins (blob id + sha256 at head b479fc55)
    blobs, record = F.load_blobs(args.repo)
    plan = F.parse(blobs, 'new/PLAN.json')
    template = F.parse(blobs, 'GLOBAL-TEMPLATE.json.gz')
    order = [tuple(x) for x in F.parse(blobs, 'ORDER.json')]
    dispatch = F.dispatch_map(F.parse(blobs, 'DISPATCH.json'), 'R-0.dispatch')
    assert order == [tuple(x) for x in plan['order']]
    # ---- the 80-alias words
    widths, local, info = {}, {}, {}
    for pid, (path, oid, sha) in WORDS.items():
        got = F.git(args.repo, 'rev-parse', '--verify', HEAD_2339 + ':' + path).decode().strip()
        F.need(got == oid, 'input.pin', path)
        data = F.git(args.repo, 'cat-file', 'blob', oid)
        F.need(hashlib.sha256(data).hexdigest() == sha, 'input.pin', path)
        word = json.loads(gzip.decompress(data), parse_float=Fraction)
        h = F.word_helpers(word, pid)
        F.need(len(h['live']) == 400 and len(h['removed']) == 80, 'R-a.word', pid + ' 400 live helpers')
        widths[pid] = h['widths']
        local[pid] = F.as_profile(word['report']['local_profile'], 'R-c.local', pid)
        F.need(Counter(h['widths']) == F.as_profile(word['report']['width_inventory'], 'R-a.word', pid),
               'R-a.word', pid + ' width inventory')
        F.need(F.mass(local[pid]) == 1856 + sum(h['widths']), 'R-c.local', pid + ' local mass = 1856 + widths')
        info[pid] = dict(live=h['live'], removed=h['removed'], hyperplane_ended=len(h['hyperplane_ended']))
        record[path] = dict(git_blob=oid, sha256=sha, commit=HEAD_2339)
    F.need(widths['gauge44'] == widths['extra'] and info['gauge44']['live'] == info['extra']['live'],
           'R-a.word', 'provider-independent helper map')
    # ---- the fill and its claims
    raw = open(os.path.join(HERE, 'OWNERS-80.json.gz'), 'rb').read()
    rows = json.loads(gzip.decompress(raw))
    build = json.load(open(os.path.join(HERE, 'BUILD-RECEIPT.json')))
    prof_file = json.load(open(os.path.join(HERE, 'PROFILE-80.json')))
    F.need(hashlib.sha256(raw).hexdigest() == build['owners_sha256'], 'R-0.pins', 'OWNERS-80 sha256')
    F.need(build['helper_map']['live_registers'] == info['gauge44']['live'] and
           build['helper_map']['widths'] == widths['gauge44'], 'R-0.pins', 'receipt helper map')
    claims = dict(idle=[('BUILD-RECEIPT.json idle', F.as_profile(build['idle'], 'R-c.idle', 'receipt'))],
                  profile=[('PROFILE-80.json', F.as_profile(prof_file, 'R-c.profile', 'PROFILE-80')),
                           ('BUILD-RECEIPT.json profile', F.as_profile(build['profile'], 'R-c.profile', 'receipt'))],
                  rank_mass=build['rank_mass'], deficit=build['deficit'], hosted=build['roles'],
                  cross_replica=build['cross_replica_roles'], idle_remainders=build['idle_remainders'])
    ctx = F.build_context('ext80-T74', plan['T'], 400, order, dispatch, widths, local, template, plan, claims)

    original_static = F.check_static

    def check_static_80(ctx_, sched_):
        """fill_check.check_static without the PLAN per_call_widths comparison (437-helper widths)."""
        T, order_, plan_ = ctx_['T'], ctx_['order'], ctx_['plan']
        F.need(len(order_) == F.STAGES * T and set(order_) == {(s, r) for s in range(F.STAGES) for r in range(T)},
               'R-0.order', 'call inventory')
        F.need(plan_['order'] == [list(x) for x in order_], 'R-0.order', 'PLAN order')
        F.need(set(ctx_['dispatch']) == set(order_), 'R-0.dispatch', 'dispatch inventory')
        for t, (s, r) in enumerate(order_):
            pc = plan_['provider_calls'][t]
            F.need((pc['stage'], pc['replica']) == (s, r) and pc['provider'] == ctx_['dispatch'][s, r],
                   'R-0.dispatch', 'PLAN provider call %d' % t)
        pw = plan_['windows']
        F.need(len(pw) == len(sched_['windows']), 'R-d.plan_windows', 'window count')
        for (r, c), times in sched_['window_times'].items():
            key = '%d,%d' % (r, c)
            F.need(key in pw and pw[key] == [sched_['rank'][c], times], 'R-d.plan_windows', 'PLAN window ' + key)

    F.check_static = check_static_80
    try:
        sched = F.derive_schedule(ctx)
        result = F.run_pipeline(ctx, sched, rows)
        controls = F.controls(ctx, sched, rows)
    except F.CheckFailure as exc:
        print('FAIL_T74_80ALIAS_FILL_CHECK ' + str(exc))
        return 1
    finally:
        F.check_static = original_static
    F.need(Counter(dispatch.values()) == Counter({'gauge44': 249, 'extra': 417}), 'R-0.dispatch', 'provider counts')
    # ---- certified price of the recounted profile
    H = {int(k): v for k, v in result['profile'].items()}
    ev = P.Evaluator(H, F.M, ctx['W'], surcharge=False)
    lo, hi, steps, undecided = ev.root_bracket(DIGITS)
    P.need(undecided is None and hi - lo == Fraction(1, 10 ** DIGITS), 'moment.bracket', 'bisection stalled')
    F.need(hi < CLAIM_2269 < CLAIM_2322, 'price', 'ordering versus the open records')
    receipt = dict(
        status='PASS_T74_80ALIAS_FILL_CHECK',
        object=dict(owners='OWNERS-80.json.gz', sha256=build['owners_sha256'], roles=len(rows)),
        inputs=record, vendored=VENDOR,
        windows=dict(rebuilt=len(sched['windows']), equal_to_plan=True, expanded_events=sched['events'],
                     bridges=sched['bridges'], child_ranks={str(c): sched['rank'][c] for c in sorted(sched['rank'])}),
        recount=result, controls_rejected=controls,
        helper_map=dict(rule='helper i = i-th live register (224..703 minus 80 removed), both providers',
                        removed_registers=info['gauge44']['removed'],
                        hyperplane_ended_live=info['gauge44']['hyperplane_ended']),
        price=dict(side='native complex (no surcharge), mu(a) = sum_r n_r (r/73)^(1-a) / 66304',
                   root_bracket=[str(lo), str(hi)], width='1e-%d' % DIGITS, bisection_steps=steps,
                   b_floor_decimal=P.dec(lo, DIGITS), below_pr2269_claim=True, below_pr2322_claim=True,
                   gap_to_pr2269=float(CLAIM_2269 - hi)),
        adaptation='PLAN per_call_widths check replaced by widths re-derived from the 80-alias words',
        not_checked=['native lowering / controller emission / invoice of the 80-alias words',
                     'placement of the 44 private cleanup zero buffers (physical stock)',
                     'outer ledger / kappa (no claim)'],
        credits='PR2339 (this author); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; PR2312/PR2302 '
                'jeremykothe2; PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.). Prepared with '
                'substantial AI assistance (Claude Code, Anthropic); Apache-2.0.')
    if args.out:
        with open(os.path.join(HERE, 'check_fill.receipt.json'), 'w') as h:
            h.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print('fill: roles=%d idle=%s' % (result['roles'], result['idle']))
    print('profile=%s mass=%d deficit=%d cross=%d' % (result['profile'], result['rank_mass'], result['deficit'],
                                                      result['cross_replica_roles']))
    print('controls rejected: %d (%s)' % (len(controls), ', '.join(c['name'] for c in controls)))
    print('b in [%s, %s] (1e-%d bracket)' % (P.dec(lo, DIGITS), P.dec(hi, DIGITS), DIGITS))
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_80ALIAS_FILL_CHECK roles=%d controls=%d' % (result['roles'], len(controls)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
