#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""An owner map for PR2435's T74 words that attains the certified pattern optimum (+5.80e-10 over PR2435's map).

PR2442 certified the bin-pattern integer optimum for PR2435's words (jeremykothe2, head 324d7d35):
  - idle multiset {1:20822, 3:6694, 5:2, 48:25302};
  - root 0.0016985119240027768;
  - every legal whole-helper fill has b <= that root + 1e-15.
PR2435's own map has idle {1:20824, 3:6695, 5:1, 48:25302}. This package realizes the optimum with four role moves
(MOVES.json) on PR2435's pinned OWNERS.json.gz. They re-pattern four bins:
  A  48: [8,8,9,9,9]+5 -> [4,8,9,9,9,9]      B  48: [9,9,9,9,9]+3 -> [4,8,9,9,9,9]
  C  32: [4,9,9,9]+1   -> [9,9,9]+5          D  32: [4,9,9,9]+1   -> [9,9,9]+5
Family and copy are updated from the new bin, and offsets are prefix-repacked in the touched bins.

The script rebuilds the new map and re-checks it with this author's independent PR2387 fill_check80, vendored and
pinned:
  - R-a..R-e (roles, widths, families, active pair, windows rebuilt from GLOBAL-TEMPLATE, capacity, prefix);
  - the R-c recount;
  - R-f namespace;
  - R-g X2 pending axes and 73-column charts.
It then certifies the root of the new global profile to within +-1e-15 of the optimum root, using 800-bit
enclosures, so it lies 5.80e-10 above PR2435's root.

Controls:
  - the unmodified PR2435 map reproduces PR2435's idle multiset and root;
  - each single move alone is rejected or leaves a non-optimal idle multiset;
  - a move into a bin outside the role's window is rejected (R-d);
  - a move onto a bin of the same family already used in that call is rejected (R-e).

No kappa claim. PR2435's admission (invoice with the new chart count, outer ledger) is not re-run. kappa = C - 1/F - B
would follow its certified endpoint.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B optimal_map.py [--repo PATH] [--fetch] [--remote URL] [--out] [--write-map]
"""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_2435_OPTIMAL_MAP refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
VENDOR = {
    'vendor/pr2387/fill_check80.py': ('557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    'vendor/pr2387/ceiling_lp.py': ('48362358660f74e0e235865df3e172494c191212',
                                    '63e2d35b07342508680e20f4b60c4da888acf4c771cd9b10400c21490f1491be'),
    'vendor/pr2387/vendor/iter3/price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                                                  '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f'),
}
HEAD_2435 = '324d7d3590dc21003940a44cb0cbdc32b3620f25'
PKG_2435 = 'research/gmx-t74-borrow43-handoff'
PINS_2435 = {
    'new/PLAN.json': ('d1e02eca782c3669b6d8c89dc88643687912a2f3', 'b2420a0ef9e145c6552b4cbeca11d56e8447ccce7b67193677a2b1a2871243ad'),
    'new/SPEC.json': ('5263146bfdfb3c92bdae12bc59dd375362a6b971', 'dd0bdfc8c7b871d627eac981af185dee061ab1bd564ce7c3ebfdccec4aa965d3'),
    'GLOBAL-TEMPLATE.json.gz': ('5327fc2f4e8ea82ed356c94ff040d23fc73c731f', '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    'ORDER.json': ('46808f1afdd5f93f6fd49289a9a8ddd276ed228f', '7d8d5e9ce5f9466dcee081ca164675ccfa3a4a020435fd23b7ea4ecd7031ff29'),
    'DISPATCH.json': ('dfa7fe3205fbd0b9499339fc8c489c7bd08b4665', 'd6d96a047b54ecf9b3a708463af79c18e6d0a9ac9f717f10538cb47b33750f56'),
    'CONSTRUCTION.json': ('ed5e7e453af5db4ac26b99f374bd880e84113eb2', '23cebad9767aa3b7dd52b0bb526dbc5919e076c8d980b15c49dcf24a173e6883'),
    'OWNERS.json.gz': ('4b0eb1cabf6e90d3a9d66782621291bb50b8ac6a', '3243366353e3e3e6ccd5d4a013b10675a5cb8dc826f7fa5ba472df15242b1c83'),
    'new/PROFILE.json': ('0d6ec10cc91d7f1cfeee47cb8ff5a13ac212d741', 'ef0fbaa24a2998e202b5effa9078cce4e6e8398683b7b15bf6bc9b193e4bcbb5'),
    'new/borrow/words/BORROW-WORD-43base.json.gz': ('7e382c2d03ab32a62c3b0aa3d799612a126068af', '46924868825e07168c2e8149dada6b1157afa444b316eb00c16555ec8a4004db'),
    'new/borrow/words/BORROW-WORD-43extra.json.gz': ('29fa1b3a8b4618632116252bcbd6e2beac395d58', 'b678b0bad0275b6870681b40bbcaefc7e815ed36713f0318a1b236cdf7d9e0b6'),
    'new/borrow/receipts/AUDIT-43base.json': ('f362e0600a7f609b0b66838dfd8ab0e7334ca417', '0cc5dd843fea9296a25541287c4cef14978f47d418ed75b1e392d7cc9cce0de3'),
    'new/borrow/receipts/AUDIT-43extra.json': ('9ddcf6fcae4f4989cf84e3cf5ad99104a1c0e70e', '346558ae4cb1f80a08f80eba551705353066a2beaaf6f4f3c84b379b22cd52c7'),
}
HEAD_2447 = '805bbaddf664459c1eb92aa461645cd69764c86e'     # PR2447 (jeremykothe2): optimal owner fill, concurrent
PINS_2447 = {k: v for k, v in PINS_2435.items() if 'receipts/AUDIT' not in k}   # words identical; receipts regenerated
PINS_2447.update({
    'new/PLAN.json': ('23bf2e23c7890eb37ed213bc96d614502888f021', '1fcfb74bdcab0330b7ed8a9d6d2a01b3fa7c66bccf64af7e9f5ce0b727c32761'),
    'new/SPEC.json': ('c225f3908929ba1e1f4168ada904986b193d0ce9', '7c0046abf81f353b1b563284e458e8c9c82726d349abd131e6b484bd43308f16'),
    'CONSTRUCTION.json': ('c9deb2d1c9d6a40d0780a9b610dbab77215d1415', '01053f0053b2d9ade94f3151b584926cf6c58a8c63112ad84400251cc7d70c85'),
    'OWNERS.json.gz': ('9c385c954b7bf565139ac1c162107ae6d98d29d2', '0b22cfebc06f22bbfd6070587d0ae0ef0e912cd2f9e98ba16a6f5cac2f9e3354'),
    'new/PROFILE.json': ('ea36809b6da2a8a6b81c8b9c57fcdbe1bd56ca17', 'e37ef93ec2b1d9ef8029f5ca971779a74302e8cde53c9f3a024e4ed4e344319f'),
    'outer/OUTER-CLAIM.json': ('e7d5e39f02930f8c2317e7e86b9ad4db1fe972f0', '04dd59d21af4c182e8763933f3f5c7a7fc064c83cb7c4ce616d988d4c9cb43ab'),
})
KAPPA_2447_DEC = '0.001698511924002761437757966262255027756475230301463200108591'
KAPPA_2435 = Fraction('0.001698511343697629329051733814187744630805511096704593311278')
OPT_ROOT = Fraction('0.0016985119240027768')          # PR2442 pattern optimum (float root, certified +-1e-15 below)
OPT_IDLE = {'1': 20822, '3': 6694, '5': 2, '48': 25302}
OLD_IDLE = {'1': 20824, '3': 6695, '5': 1, '48': 25302}
EPS = Fraction(1, 10 ** 15)


def load(rel, name):
    path = os.path.join(HERE, rel)
    data = open(path, 'rb').read()
    blob, sha = VENDOR[rel]
    if hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != blob or hashlib.sha256(data).hexdigest() != sha:
        raise SystemExit('FAIL_T74_2435_OPTIMAL_MAP vendored pin ' + rel)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    ap.add_argument('--write-map', action='store_true', help='also write OWNERS-OPT.json.gz next to this script')
    args = ap.parse_args()
    t0 = time.time()
    FC = load('vendor/pr2387/fill_check80.py', 'fc80')
    LP = load('vendor/pr2387/ceiling_lp.py', 'ceiling_lp')
    need = FC.need
    try:
        for head, ref in ((HEAD_2435, 'refs/pull/2435/head'), (FC.HEAD_2269, 'refs/pull/2269/head')):
            if not FC.commit_present(args.repo, head) and args.fetch:
                subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, ref], check=True)
            need(FC.commit_present(args.repo, head), 'R-0.pins', '%s absent (rerun with --fetch)' % head[:8])
        b, rec_in = FC.read_pinned(args.repo, HEAD_2435, PKG_2435, PINS_2435, 'PR2435')
        tpl = FC.template_2269(b)
        words = {}
        for pid, tag in (('gauge44', 'base'), ('extra', 'extra')):
            words[pid] = FC.load_word(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % tag,
                                      'new/borrow/receipts/AUDIT-43%s.json' % tag, tag, 46)
        ctx = FC.context('pr2435-opt', tpl, 434, {p: words[p]['widths'] for p in words},
                         {p: words[p]['local'] for p in words}, dict(idle=[], profile=[], scalars=[]), plan_widths=True)
        rows = FC.parse(b, 'OWNERS.json.gz')
        sched = FC.derive_schedule(ctx['T'], tpl['template'], ctx['order'])
        rank, pair, side, V, FPR = sched['rank'], sched['child_pair'], sched['child_side'], FC.V, FC.FAMILIES_PER_REPLICA
        moves = json.load(open(os.path.join(HERE, 'MOVES.json')))

        def apply(base, mvlist):
            new = copy.deepcopy(base)
            touched = set()
            for m in mvlist:
                z = new[m['row_index']]
                need((z['time'], z['helper'], z['width'], [z['owner_replica'], z['child'], z['port']]) ==
                     (m['time'], m['helper'], m['width'], m['from_bin']), 'R-0.moves', 'move does not match the row')
                o, c, p = m['to_bin']
                z['owner_replica'], z['child'], z['port'] = o, c, p
                z['family'] = o * FPR + (2 * pair[c] + side[c]) * V + p
                z['copy'] = V * o + p
                touched.add(tuple(m['from_bin']))
                touched.add(tuple(m['to_bin']))
            for bb in touched:
                idx = [i for i, z in enumerate(new) if (z['owner_replica'], z['child'], z['port']) == bb]
                off = 0
                for i in sorted(idx, key=lambda i: (-new[i]['width'], new[i]['time'], new[i]['helper'])):
                    new[i]['offset'] = off
                    off += new[i]['width']
            return new

        def wmu(profile, a, upper):
            P = LP.P
            tot = Fraction(0)
            for r, n in profile.items():
                r = int(r)
                ll, lu = P.log_enclosure(73, r)
                el, eu = P.exp_enclosure((a.numerator * ll) // a.denominator, P.cdiv(a.numerator * lu, a.denominator))
                tot += n * Fraction(r * (eu if upper else el), 73 * P.ONE)
            return tot

        # control: the unmodified PR2435 map
        rec0 = FC.run_pipeline(ctx, sched, rows)
        need(rec0['idle'] == OLD_IDLE, 'R-c.idle', 'PR2435 map recount')
        need(wmu(rec0['profile'], KAPPA_2435 + EPS, False) > ctx['W'] and
             wmu(rec0['profile'], KAPPA_2435 - EPS, True) < ctx['W'], 'R-c.root', 'PR2435 root control')
        print('control: PR2435 map passes R-a..R-e, idle %s, root within 1e-15 of its kappa' % rec0['idle'], flush=True)
        # the optimal map
        new = apply(rows, moves['moves'])
        rec = FC.run_pipeline(ctx, sched, new)
        need(rec['idle'] == OPT_IDLE, 'R-c.idle', 'new idle %s is not the certified optimum' % rec['idle'])
        print('optimal map: R-a..R-e PASS (%d roles, %d cross-replica); idle %s = PR2442 optimum'
              % (rec['roles'], rec['cross_replica_roles'], rec['idle']), flush=True)
        geo = FC.private_namespace(ctx['W'], ctx['R'], words['gauge44']['buffers'], rec['max_hosted_family'])
        need(geo['physical'] + geo['zero_buffers'] == tpl['spec']['expected']['physical'], 'R-f.namespace', 'physical stock')
        ports = [FC.parse(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % t)['ports'] for t in ('base', 'extra')]
        phases, pports, recph = FC.load_phases(args.repo, tpl['template'], ports)
        bases = FC.owner_bases(pports)
        xg = FC.pending_axes_and_charts(sched, phases, bases, new)
        print('R-f physical %d + %d buffers = %d; R-g: %d pending-axis checks disjoint, %d distinct 73-column charts '
              '(PR2435 map: %d)' % (geo['physical'], geo['zero_buffers'], geo['physical'] + geo['zero_buffers'],
                                    xg['pending_axis_checks'], xg['actual_73column_charts'],
                                    tpl['spec']['expected']['actual_73column_sigmas']), flush=True)
        need(wmu(rec['profile'], OPT_ROOT + EPS, False) > ctx['W'] and wmu(rec['profile'], OPT_ROOT - EPS, True) < ctx['W'],
             'R-c.root', 'new root not within 1e-15 of the optimum root')
        gain = OPT_ROOT - KAPPA_2435
        print('root of the new global profile certified within +-1e-15 of %s: +%.4e over PR2435' % (float(OPT_ROOT),
                                                                                                    float(gain)), flush=True)
        # negative controls
        rejected = []
        for k in range(4):                         # each single move alone must not give the optimum
            try:
                r1 = FC.run_pipeline(ctx, sched, apply(rows, [moves['moves'][k]]))
            except FC.CheckFailure as e:
                rejected.append('single_move_%d_rejected_%s' % (k, str(e).split(':')[0]))
            else:
                need(r1['idle'] != OPT_IDLE, 'control', 'single move %d reached the optimum' % k)
                rejected.append('single_move_%d_not_optimal' % k)
        bad = copy.deepcopy(moves['moves'])
        # window violation: send the width-9 role into a bin whose window excludes its call
        z9 = bad[1]
        windows, callpos = sched['windows'], sched['callpos']
        t9 = z9['time']
        out_bin = next([o, c, 0] for (o, c), (lo, hi) in sorted(windows.items())
                       if rank[c] == 32 and not (lo < callpos[t9] < hi))
        bad[1] = dict(z9, to_bin=out_bin)
        try:
            FC.run_pipeline(ctx, sched, apply(rows, bad))
        except FC.CheckFailure as e:
            need(e.check == 'R-d.window', 'control', 'window mutant rejected for the wrong reason')
            rejected.append('out_of_window_move_rejected_%s' % e.check)
        else:
            need(False, 'control', 'an out-of-window move was accepted')
        # family conflict: move the width-4 role of call 435 into a bin already holding another helper of call 435
        z4 = moves['moves'][2]
        clash = next((zz['owner_replica'], zz['child'], zz['port']) for zz in rows
                     if zz['time'] == z4['time'] and zz['helper'] != z4['helper'])
        bad2 = copy.deepcopy(moves['moves'])
        bad2[2] = dict(z4, to_bin=list(clash))
        try:
            FC.run_pipeline(ctx, sched, apply(rows, bad2))
        except FC.CheckFailure as e:
            need(e.check == 'R-e.family_unique_per_call', 'control', 'family mutant rejected for the wrong reason')
            rejected.append('same_call_family_clash_rejected_%s' % e.check)
        else:
            need(False, 'control', 'a same-call family clash was accepted')
        print('negative controls: %s' % ', '.join(rejected), flush=True)
        # ---- independent check of PR2447's own optimal owner map (concurrent) ----------------------------------
        if not FC.commit_present(args.repo, HEAD_2447) and args.fetch:
            subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, 'refs/pull/2447/head'], check=True)
        need(FC.commit_present(args.repo, HEAD_2447), 'R-0.pins', 'PR2447 head absent (rerun with --fetch)')
        b7, rec7_in = FC.read_pinned(args.repo, HEAD_2447, PKG_2435, PINS_2447, 'PR2447')
        tpl7 = FC.template_2269(b7)
        spec7 = tpl7['spec']['expected']
        ctx7 = FC.context('pr2447', tpl7, 434, {p: words[p]['widths'] for p in words},
                          {p: words[p]['local'] for p in words},
                          dict(idle=[('new/SPEC.json', FC.as_profile(spec7['idle_remainder_profile'], 'R-c.idle', 's'))],
                               profile=[('new/SPEC.json', FC.as_profile(spec7['global_profile'], 'R-c.profile', 's')),
                                        ('new/PROFILE.json', FC.as_profile(FC.parse(b7, 'new/PROFILE.json'), 'R-c.profile', 'p'))],
                               scalars=[('roles', 'SPEC', spec7['hosted_residuals']),
                                        ('cross_replica_roles', 'SPEC', spec7['cross_replica_helper_roles']),
                                        ('rank_mass', 'SPEC', spec7['rank_mass'])]), plan_widths=True)
        rows7 = FC.parse(b7, 'OWNERS.json.gz')
        sched7 = FC.derive_schedule(ctx7['T'], tpl7['template'], ctx7['order'])
        rec7 = FC.run_pipeline(ctx7, sched7, rows7)
        need(rec7['idle'] == OPT_IDLE, 'R-c.idle', 'PR2447 idle is not the certified optimum')
        geo7 = FC.private_namespace(ctx7['W'], ctx7['R'], words['gauge44']['buffers'], rec7['max_hosted_family'])
        need(geo7['physical'] + geo7['zero_buffers'] == spec7['physical'], 'R-f.namespace', 'PR2447 physical stock')
        xg7 = FC.pending_axes_and_charts(sched7, phases, bases, rows7)
        need(xg7['actual_73column_charts'] == spec7['actual_73column_sigmas'], 'R-g.chart', 'PR2447 charts vs SPEC')
        need(FC.parse(b7, 'outer/OUTER-CLAIM.json')['kappa'].startswith(KAPPA_2447_DEC), 'R-0.pins', 'PR2447 kappa')
        need(wmu(rec7['profile'], OPT_ROOT + EPS, False) > ctx7['W'] and wmu(rec7['profile'], OPT_ROOT - EPS, True) < ctx7['W'],
             'R-c.root', 'PR2447 root')
        need(abs(Fraction(KAPPA_2447_DEC) - OPT_ROOT) < EPS, 'R-c.root', 'PR2447 kappa vs optimum root')
        diff_rows = sum(1 for x, y in zip(rows, rows7) if x != y)
        print('PR2447 (concurrent) map: R-a..R-g PASS with this independent checker; recount = its SPEC/PROFILE; idle = '
              'PR2442 optimum; %d charts = its SPEC; root within 1e-15 of the optimum = its kappa; it differs from PR2435 '
              'in %d of %d rows (this package: 4)' % (xg7['actual_73column_charts'], diff_rows, len(rows)), flush=True)
    except FC.CheckFailure as exc:
        print('FAIL_T74_2435_OPTIMAL_MAP %s' % exc)
        return 1
    canon = json.dumps(new, separators=(',', ':'), sort_keys=True).encode()
    if args.write_map:
        with open(os.path.join(HERE, 'OWNERS-OPT.json.gz'), 'wb') as f:
            f.write(gzip.compress(canon, mtime=0))
    out = dict(object='owner map for PR2435 words attaining the PR2442 pattern optimum', head=HEAD_2435,
               moves=moves['moves'], idle=rec['idle'], profile=rec['profile'],
               charts=xg['actual_73column_charts'], charts_pr2435=tpl['spec']['expected']['actual_73column_sigmas'],
               physical=geo['physical'] + geo['zero_buffers'], root_bracket=[str(OPT_ROOT - EPS), str(OPT_ROOT + EPS)],
               gain_over_pr2435=float(gain), canonical_map_sha256=hashlib.sha256(canon).hexdigest(),
               controls=rejected, python=sys.version.split()[0],
               pr2447=dict(head=HEAD_2447, idle=rec7['idle'], charts=xg7['actual_73column_charts'],
                           cross_replica_roles=rec7['cross_replica_roles'], rows_differing_from_pr2435=diff_rows,
                           independent_check='PASS'),
               not_checked=['PR2435 admission with the new chart count (invoice row bound), outer ledger; no kappa claim'])
    if args.out:
        with open(os.path.join(HERE, 'optimal_map.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_2435_OPTIMAL_MAP moves=4 idle=%s root=%.16f gain=+%.3e charts=%d controls=%d pr2447=verified no_new_kappa'
          % (json.dumps(rec['idle'], sort_keys=True).replace(' ', ''), float(OPT_ROOT), float(gain),
             xg['actual_73column_charts'], len(rejected)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
