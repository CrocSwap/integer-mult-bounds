#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent check of PR2435's T74 owner map, local words and complex endpoint (standard library only).

PR2435 (jeremykothe2, head 324d7d35) claims conditional kappa = 0.0016985113436976293... It raises the entrance
frames of 24 copy-buffer helpers per word (width 8 -> 7) on PR2322's handoff construction and adds an exact owner
fill (OWNERS.json.gz, 289,044 roles). This script re-checks the owner map and the words with an implementation
written independently of PR2435's code: the vendored PR2387 fill_check80.py (this author), used unchanged as a
library. It checks:

  * the words: frame-climb recount of both BORROW-WORDs, which must equal the reported profile {1:2359, 2:632,
    3:330, 4:120, 5:38, 8:8} and width inventory {4:33, 5:9, 7:62, 8:90, 9:240}, the 8 COPY children and the
    zero buffers;
  * the owner map, under hosting rules R-a..R-e with windows rebuilt from GLOBAL-TEMPLATE events and compared
    with PR2435's new/PLAN.json windows:
      - R-a one role per (call, helper) with the correct width;
      - R-b capacity, disjointness and prefix-filling;
      - R-c recount of idle and global profiles;
      - R-d every role inside its window;
      - R-e family rules;
  * R-f, the PR2322 private-namespace geometry with physical = live + helpers + centres + buffers + 2 = 66,826;
  * R-g, X2 pending-axis disjointness and the count of distinct 73-column charts, compared with SPEC
    actual_73column_sigmas;
  * each recount against PR2435's SPEC: idle {1:20824, 3:6695, 5:1, 48:25302}, the global profile, the role
    counts and the rank mass;
  * the complex root of the recounted global profile, certified to +-1e-15 around the claimed kappa with
    800-bit enclosures (vendored ceiling_lp / iteration-3 price_check);
  * the negative controls of fill_check80, adapted to PR2435's words: mutated rows, windows, families,
    namespace, word profile and pending axes must all be rejected.

PR2435's words differ from PR2322's only in frames (24 entrances and the gate frames around them); the exact replay is
frame-blind, so it re-confirms the unchanged scalar word but does not test the new mechanism.  Not checked: whether the
parent delivers each raised copy buffer at its two-dimensional entrance frame; native lowering, invoice, outer.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B check_2435.py [--repo PATH] [--fetch] [--remote URL] [--out]
"""

import argparse
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
    sys.stdout.write('FAIL_T74_2435_FILL_INDEPENDENT refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
VENDOR = {  # byte copies of this author's PR2387 code (also vendored, pinned, in PR2402)
    'vendor/pr2387/fill_check80.py': ('557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    'vendor/pr2387/ceiling_lp.py': ('48362358660f74e0e235865df3e172494c191212',
                                    '63e2d35b07342508680e20f4b60c4da888acf4c771cd9b10400c21490f1491be'),
    'vendor/pr2387/vendor/iter3/price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                                                  '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f'),
    'vendor/pr2315/words_check.py': ('0b646b9d5583c75a78e0c2dd7e9cfffa02055058',
                                     'b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6'),
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
    'CLAIM.json': ('98f7ddd17ac6aee5845dc60eca39fd2e0f304e16', '8b60a69829037f5c15e7102f7ac3db3592859d68581ac1be0c993b290816c6c1'),
    'outer/OUTER-CLAIM.json': ('556f72136acd4dbbbd53ba48849faacf4cf64b56', '42947f62e7caf297f3712a42299dcf13ad68169eddb10ccad95b54c30853c8bb'),
}
HEAD_2322 = '002304ef01c4416a127916169ae6d94c1bee052b'          # PR2322 words, for the frame-only diff
WORDS_2322 = {'base': ('research/t74-joint-owner-hillclimb/words/base.json.gz', 'f4dda9147af544ae4fe6d17582b8aa5e9916040b'),
              'extra': ('research/t74-joint-owner-hillclimb/words/extra.json.gz', '471e4819c0c6b256e7b3999649f1391989d92e19')}
KAPPA_2435_DEC = '0.001698511343697629329051733814187744630805511096704593311278'        # PR2435 body, 58 digits
KAPPA_2435 = Fraction(KAPPA_2435_DEC)
EPS = Fraction(1, 10 ** 15)
HELPERS, REMOVED = 434, 46


def load(rel, name):
    path = os.path.join(HERE, rel)
    data = open(path, 'rb').read()
    blob, sha = VENDOR[rel]
    if hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() != blob or hashlib.sha256(data).hexdigest() != sha:
        raise SystemExit('FAIL_T74_2435_FILL_INDEPENDENT vendored pin ' + rel)
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
    args = ap.parse_args()
    t0 = time.time()
    FC = load('vendor/pr2387/fill_check80.py', 'pr2387_fill_check80')
    LP = load('vendor/pr2387/ceiling_lp.py', 'pr2387_ceiling_lp')
    need = FC.need
    try:
        if not FC.commit_present(args.repo, HEAD_2435) and args.fetch:
            subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, 'refs/pull/2435/head'], check=True)
        need(FC.commit_present(args.repo, HEAD_2435), 'R-0.pins', 'PR2435 head absent (rerun with --fetch)')
        if not FC.commit_present(args.repo, FC.HEAD_2269) and args.fetch:   # template DATA-PHASES pin (R-g)
            subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, 'refs/pull/2269/head'], check=True)
        b, rec_in = FC.read_pinned(args.repo, HEAD_2435, PKG_2435, PINS_2435, 'PR2435')
        tpl = FC.template_2269(b)                       # PLAN/SPEC/ORDER/DISPATCH/CONSTRUCTION consistency
        need(FC.parse(b, 'outer/OUTER-CLAIM.json')['kappa'].startswith(KAPPA_2435_DEC), 'R-0.pins',
             'claimed kappa (58 digits) is not a prefix of PR2435 outer/OUTER-CLAIM.json kappa')
        spec = tpl['spec']['expected']
        words = {}
        for pid, tag in (('gauge44', 'base'), ('extra', 'extra')):
            words[pid] = FC.load_word(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % tag,
                                      'new/borrow/receipts/AUDIT-43%s.json' % tag, '2435-' + tag, REMOVED)
        prof = {1: 2359, 2: 632, 3: 330, 4: 120, 5: 38, 8: 8}
        inv = {4: 33, 5: 9, 7: 62, 8: 90, 9: 240}
        for pid in words:
            need(dict(words[pid]['local']) == prof, 'R-c.local', pid + ' recounted local profile')
            need(dict(Counter(words[pid]['widths'])) == inv, 'R-a.word', pid + ' recounted width inventory')
        print('words: both providers recount to profile %s and width inventory %s (%d helpers, %d zero buffers)'
              % (prof, inv, HELPERS, len(words['gauge44']['buffers'])), flush=True)
        # what PR2435 changed relative to PR2322's words: only frames (entrance raise), nothing scalar
        if not FC.commit_present(args.repo, HEAD_2322) and args.fetch:
            subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, 'refs/pull/2322/head'], check=True)
        need(FC.commit_present(args.repo, HEAD_2322), 'R-0.pins', 'PR2322 head absent (rerun with --fetch)')
        frame_diff = {}
        for tag in ('base', 'extra'):
            rel, blob2322 = WORDS_2322[tag]
            raw = FC.git(args.repo, 'show', HEAD_2322 + ':' + rel)
            need(FC.blob_id(raw) == blob2322, 'R-0.pins', 'PR2322 word pin ' + tag)
            old = json.loads(gzip.decompress(raw))
            new = FC.parse(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % tag)
            strip = lambda g: g[:-1] if isinstance(g, list) and g and g[0] in ('add', 'scale') else g
            diff = dict(start_extra=sorted(int(k) for k in set(old['start_extra']) | set(new['start_extra'])
                                           if old['start_extra'].get(k) != new['start_extra'].get(k)))
            for sec in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
                need(len(old[sec]) == len(new[sec]) and all(strip(x) == strip(y) for x, y in zip(old[sec], new[sec])),
                     'R-c.local', tag + ': non-frame change in section ' + sec)
                diff[sec + '_frames'] = sum(1 for x, y in zip(old[sec], new[sec]) if x != y)
            for key in ('ports', 'centers', 'center_frames', 'target_levels', 'helper_final', 'removed',
                        'initial_corrections', 'warps'):
                need(old[key] == new[key], 'R-c.local', tag + ': %s changed' % key)
            need(len(diff['start_extra']) == 24, 'R-c.local', tag + ': expected 24 raised entrances')
            frame_diff[tag] = diff
        print('PR2322 -> PR2435 words: only frames differ (24 start_extra entrances, %d A-gate and %d B-gate frames per '
              'word); registers, coefficients, warps, centres, ends and cleanup identical'
              % (frame_diff['base']['A_frames'], frame_diff['base']['B_frames']), flush=True)
        # exact word checks of this author's iteration-3 words_check.py (PR2315): warps, frames, exact replay
        WC = load('vendor/pr2315/words_check.py', 'pr2315_words_check')
        word_checks = {}
        for tag in ('base', 'extra'):
            w = FC.parse(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % tag)
            Pw = WC.parse_borrow(w)
            wres = WC.check_all_warps(Pw)
            fr = WC.frame_check(Pw)
            need(dict(fr['paid']) == prof and dict(fr['inventory']) == inv and fr['helpers'] == HELPERS, 'R-c.local',
                 tag + ' words_check frame recount')
            rf = WC.replay(Pw)
            WC.replay(Pw, dual=True)
            word_checks[tag] = dict(warps=len(wres), warp_dims=dict(Counter(x['dim'] for x in wres)),
                                    x_lenders=[x['lender'] for x in wres if x['lender'] < Pw['v']], replay=rf)
        need(word_checks['base']['warps'] == word_checks['extra']['warps'] == 46, 'R-c.local', 'warp count')
        # negative control: one flipped B-gate coefficient must break the exact replay
        w = FC.parse(b, 'new/borrow/words/BORROW-WORD-43base.json.gz')
        i = next(k for k, g in enumerate(w['B']) if g[0] == 'add')
        w['B'][i] = [w['B'][i][0], w['B'][i][1], w['B'][i][2], -w['B'][i][3]] + w['B'][i][4:]
        rejected_flip = False
        try:
            WC.replay(WC.parse_borrow(w))
        except WC.Reject:
            rejected_flip = True
        need(rejected_flip, 'R-c.local', 'control: a flipped B coefficient was accepted by the exact replay')
        print('words (PR2315 words_check): 46 warps each (G invertible, K_G symplectic, Fourier rank 0); frames nested; '
              'exact replay forward and dual with arbitrary dirty inputs (%d independent inputs): Y += X, everything '
              'else and the %d zero buffers restored; a flipped B coefficient is rejected (the replay is frame-blind, so '
              'it re-confirms the unchanged scalar word, not the raised entrances)'
              % (word_checks['base']['replay']['independent_inputs'], word_checks['base']['replay']['buffers']), flush=True)
        claims = dict(idle=[('new/SPEC.json idle_remainder_profile',
                             FC.as_profile(spec['idle_remainder_profile'], 'R-c.idle', 'spec')),
                            ('PR2435 body', Counter({1: 20824, 3: 6695, 5: 1, 48: 25302}))],
                      profile=[('new/SPEC.json global_profile', FC.as_profile(spec['global_profile'], 'R-c.profile', 's')),
                               ('new/PROFILE.json', FC.as_profile(FC.parse(b, 'new/PROFILE.json'), 'R-c.profile', 'p'))],
                      scalars=[('roles', 'new/SPEC.json hosted_residuals', spec['hosted_residuals']),
                               ('cross_replica_roles', 'new/SPEC.json', spec['cross_replica_helper_roles']),
                               ('idle_remainders', 'new/SPEC.json', spec['idle_remainders']),
                               ('rank_mass', 'new/SPEC.json', spec['rank_mass'])])
        ctx = FC.context('pr2435-T74', tpl, HELPERS, {p: words[p]['widths'] for p in words},
                         {p: words[p]['local'] for p in words}, claims, plan_widths=True)
        rows = FC.parse(b, 'OWNERS.json.gz')
        sched = FC.derive_schedule(ctx['T'], tpl['template'], ctx['order'])
        print('windows: %d rebuilt from %d expanded events (%d bridges) = PR2435 new/PLAN.json windows'
              % (len(sched['windows']), sched['events'], sched['bridges']), flush=True)
        rec = FC.run_pipeline(ctx, sched, rows)
        print('R-a..R-e PASS: roles=%d = %d x %d; cross-replica %d; occupied bins %d of %d'
              % (rec['roles'], rec['calls'], rec['helpers_per_call'], rec['cross_replica_roles'], rec['occupied_bins'],
                 rec['bins']), flush=True)
        print('R-c recount = SPEC/PROFILE/body: idle=%s profile=%s mass=%d deficit=%d'
              % (rec['idle'], rec['profile'], rec['rank_mass'], rec['deficit']), flush=True)
        # R-f: private namespace geometry
        need(words['gauge44']['buffers'] == words['extra']['buffers'], 'R-f.zero_buffers', 'same buffers in both words')
        geo = FC.private_namespace(ctx['W'], ctx['R'], words['gauge44']['buffers'], rec['max_hosted_family'])
        # PR2322's rule injects the zero buffers into the reserved tableau (physical = W + R + 8 + 2); PR2435 (after
        # PR2309/PR2349) charges them as separate physical stock: physical = W + R + 8 + NZ + 2.  Check both.
        nz = geo['zero_buffers']
        need(geo['physical'] == ctx['W'] + ctx['R'] + 8 + 2 and geo['physical'] + nz == spec['physical'] == 66826,
             'R-f.namespace', 'physical %d + %d buffers vs SPEC %d' % (geo['physical'], nz, spec['physical']))
        print('R-f namespace: PR2322 rule physical %d = %d + %d + 8 + 2 with %d zero buffers in the reserved tableau; '
              'PR2435 charges them separately: %d + %d = SPEC physical %d'
              % (geo['physical'], ctx['W'], ctx['R'], nz, geo['physical'], nz, spec['physical']), flush=True)
        # R-g: pending axes and 73-column charts
        ports = [FC.parse(b, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % t)['ports'] for t in ('base', 'extra')]
        phases, pports, recph = FC.load_phases(args.repo, tpl['template'], ports)
        bases = FC.owner_bases(pports)
        xg = FC.pending_axes_and_charts(sched, phases, bases, rows)
        need(xg['actual_73column_charts'] == spec['actual_73column_sigmas'], 'R-g.chart',
             'charts %d vs SPEC actual_73column_sigmas %d' % (xg['actual_73column_charts'], spec['actual_73column_sigmas']))
        print('R-g X2: %d pending-axis checks disjoint; %d distinct 73-column charts = SPEC actual_73column_sigmas'
              % (xg['pending_axis_checks'], xg['actual_73column_charts']), flush=True)
        # negative controls (fill_check80's set; its word-tamper control is pointed at this PR's base word)
        shim = {'words/BORROW-WORD-80base.json.gz': b['new/borrow/words/BORROW-WORD-43base.json.gz']}
        orig_load_word = FC.load_word
        FC.load_word = lambda blobs, rel, audit, label, removed, *a, **k: orig_load_word(blobs, rel, audit, label,
                                                                                         REMOVED, *a, **k)
        try:
            rejected = FC.controls(ctx, sched, rows, words, shim, phases, bases)
        finally:
            FC.load_word = orig_load_word
        print('negative controls rejected: %d (%s)' % (len(rejected), ', '.join(
            c['name'].split(' ')[0] + '->' + c['rejected_by'] for c in rejected)), flush=True)
        # complex root of the recounted global profile
        P = LP.P
        gp = {int(k): v for k, v in rec['profile'].items()}

        def wmu(a, upper):
            tot = Fraction(0)
            for r, n in gp.items():
                ll, lu = P.log_enclosure(73, r)
                el, eu = P.exp_enclosure((a.numerator * ll) // a.denominator, P.cdiv(a.numerator * lu, a.denominator))
                tot += n * Fraction(r * (eu if upper else el), 73 * P.ONE)
            return tot
        need(wmu(KAPPA_2435 + EPS, False) > ctx['W'] and wmu(KAPPA_2435 - EPS, True) < ctx['W'], 'R-c.root',
             'recounted global profile root is not within 1e-15 of PR2435 kappa')
        print('root of the recounted global profile certified within +-1e-15 of PR2435 kappa %s'
              % str(float(KAPPA_2435)), flush=True)
    except FC.CheckFailure as exc:
        print('FAIL_T74_2435_FILL_INDEPENDENT %s' % exc)
        return 1
    except Exception as exc:   # e.g. words_check.Reject: report, never pass
        print('FAIL_T74_2435_FILL_INDEPENDENT %s: %s' % (type(exc).__name__, exc))
        return 1
    out = dict(object='PR2435 owner map, words and complex endpoint, independent recount', head=HEAD_2435,
               inputs=rec_in, recount=dict(idle=rec['idle'], profile=rec['profile'], roles=rec['roles'],
                                           cross_replica_roles=rec['cross_replica_roles'], rank_mass=rec['rank_mass'],
                                           deficit=rec['deficit']),
               namespace=dict(physical_pr2322_rule=geo['physical'], zero_buffers=geo['zero_buffers'], physical_charged=geo['physical'] + geo['zero_buffers']),
               charts=xg['actual_73column_charts'], controls_rejected=[c['name'] for c in rejected],
               word_checks=word_checks, frame_only_diff_vs_pr2322=frame_diff,
               root_bracket=[str(KAPPA_2435 - EPS), str(KAPPA_2435 + EPS)], python=sys.version.split()[0],
               not_checked=['legality of the 24 raised entrance frames (parent delivery at dimension 2); the change is '
                            'frame-only, so the scalar replay does not test it', 'native lowering, invoice, precision '
                            'tapes, outer ledger'])
    if args.out:
        with open(os.path.join(HERE, 'check_2435.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_2435_FILL_INDEPENDENT roles=%d idle=%s physical=%d charts=%d controls=%d root=kappa_2435+-1e-15'
          % (rec['roles'], json.dumps(rec['idle'], sort_keys=True).replace(' ', ''), geo['physical'] + geo['zero_buffers'],
             xg['actual_73column_charts'], len(rejected)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
