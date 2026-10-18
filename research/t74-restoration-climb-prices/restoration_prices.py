#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""End-of-call restoration climbs on the T74 PR2322 words: exact census, inherited cost context and numerical prices (stdlib only).

Under the frame-climb rule (vendored PR2387 fill_check80.local_recount), a FULL-cleanup helper climbs from its
last gate frame to FULL at the end of the call so that the inverse-reverse cleanup can run at FULL.  That end
climb pays recursive children.  A cold-restored (hyperplane-ended) helper (PR601 commuting cleanup, PR604/PR617
cold ends, PR2226 exact cold restoration) ends at a partial frame, pays no end climb, and needs one private zero
buffer instead.

This script
  1. recounts both pinned PR2322 words, labelling every paid child by the register and phase that paid it.  It
     checks each word's reported profile, then reports the end-climb census: FULL-cleanup helpers with end
     climbs, and the cold-restored helpers, which pay none.
  2. reads the cost context from PR2374's pinned files.  kappa = C - 1/F - B with F = 1e3046 and B = 1e-3022,
     so invoice items (zero buffers, CLEARs, adapters) enter kappa only through admission inequalities.  It also
     gives the physical headroom (parent_physical vs live + helpers + centres + buffers + 2) and the PR2322
     private-namespace bound NZ <= R on zero buffers.
  3. prices, with the PR2387 width-aware bin-pattern LP (pattern set extended to widths 3..9), the conversion of
     one FULL-cleanup helper of each (width, end-climb) class to a cold-restored end (its end-climb child
     removed, its width reduced by the end climb), each end-climb class in bulk, and all 355 as the ideal.
It does NOT show that any conversion is legal.  The commutation and restoration legality of moving a helper's
cleanup earlier is the open obligation.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B restoration_prices.py [--repo PATH] [--fetch] [--remote URL] [--out]
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
import types
from collections import Counter, defaultdict

if not __debug__:
    sys.stdout.write('FAIL_T74_RESTORATION_PRICES refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
VENDOR = {  # byte copies of PR2387 (this author), as vendored and pinned in PR2402
    'vendor/pr2387/ceiling_lp.py': ('48362358660f74e0e235865df3e172494c191212',
                                    '63e2d35b07342508680e20f4b60c4da888acf4c771cd9b10400c21490f1491be'),
    'vendor/pr2387/fill_check80.py': ('557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    'vendor/pr2387/vendor/iter3/price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                                                  '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f'),
}
PR2322 = ('002304ef01c4416a127916169ae6d94c1bee052b', 'refs/pull/2322/head')
PR2374 = ('5449da65da12bdfd94675dccc38731eaa91e93b6', 'refs/pull/2374/head')
WORDS = {'base': ('research/t74-joint-owner-hillclimb/words/base.json.gz', 'f4dda9147af544ae4fe6d17582b8aa5e9916040b',
                  '93c32c9dc8ca18394b7f3afac2cb4fa8582a6cb77399441b5107b396e63ca0f9'),
         'extra': ('research/t74-joint-owner-hillclimb/words/extra.json.gz', '471e4819c0c6b256e7b3999649f1391989d92e19',
                   'aae6592eaa4cf8638f21d50c44d09d4f8a6bb079ddcf5e377711a10ee2ddb526')}
PR2374_FILES = {
    'SPEC': ('research/gmx-t74-borrow43-handoff/SPEC.json', '5158049eeff8240d59528441d3f1fcfd8f420783',
             'da49a85190eac2b553fe982ed295b15fcde6d2dd449d976b503de25c277f2029'),
    'OUTER': ('research/gmx-t74-borrow43-handoff/outer/OUTER-CLAIM.json', 'e91f8dd77aa4a2a0acb1550026fa7e7b6b2bb525',
              'f3e40f917ad36e963b43adbcd2490f37211e863b9b68bdd83a6b1ad8a6169aae'),
    'INVOICE': ('research/gmx-t74-borrow43-handoff/code/invoice_allcold.py', '68f0d5aa64288b3ecb431cc2a8fdff8a114143cd',
                'bb213d0af12218ff7c9c572717e522d8bbeeb2856b87a253f4a7f44e0fd71f15'),
}
KAPPA_2374 = 0.0016971949509017704
EXPECT_CENSUS = {0: 1, 1: 249, 2: 42, 3: 64}
EXPECT_CLASSES = {(9, 1): 181, (9, 2): 34, (9, 3): 24, (8, 1): 58, (8, 2): 8, (8, 3): 40, (5, 1): 9, (4, 1): 1}


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), capture_output=True, check=True).stdout


def ensure(repo, commit, ref, fetch, remote):
    ok = subprocess.run(['git', '-C', repo, 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode == 0
    if not ok and fetch:
        subprocess.run(['git', '-C', repo, 'fetch', '-q', remote, ref], check=True)
        ok = subprocess.run(['git', '-C', repo, 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode == 0
    need(ok, 'commit %s absent (rerun with --fetch)' % commit[:8])


def pinned(repo, commit, path, blob, sha):
    data = git(repo, 'show', commit + ':' + path)
    need(blob_id(data) == blob and hashlib.sha256(data).hexdigest() == sha, 'pin ' + path)
    return data


def load_vendor():
    for rel, (blob, sha) in VENDOR.items():
        data = open(os.path.join(HERE, rel), 'rb').read()
        need(blob_id(data) == blob and hashlib.sha256(data).hexdigest() == sha, 'vendored pin ' + rel)
    spec = importlib.util.spec_from_file_location('pr2387_ceiling_lp', os.path.join(HERE, 'vendor/pr2387/ceiling_lp.py'))
    lp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lp)
    path = os.path.join(HERE, 'vendor/pr2387/fill_check80.py')
    src = open(path).read()
    old = '        if d:\n            paid[d] += 1\n            per_reg[r] += d\n'
    need(src.count(old) == 1, 'patch anchor in fill_check80.local_recount')
    src = src.replace(old, old + '            EVENTS.append((r, d, where))\n')   # only change: record payer and phase
    fc = types.ModuleType('pr2387_fill_check80')
    fc.__file__ = path
    exec(compile(src, path, 'exec'), fc.__dict__)
    return lp, fc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    lp, fc = load_vendor()
    ensure(args.repo, *PR2322, args.fetch, args.remote)
    ensure(args.repo, *PR2374, args.fetch, args.remote)
    out = dict(object='end-of-call restoration climbs of the PR2322 T74 words')

    # ---- 1. census -----------------------------------------------------------------------------------------------
    census = {}
    for prov, (path, blob, sha) in WORDS.items():
        w = json.loads(gzip.decompress(pinned(args.repo, PR2322[0], path, blob, sha)))
        fc.EVENTS = []
        rec = fc.local_recount(w, prov)
        need(dict(rec['paid']) == {int(k): v for k, v in w['report']['local_profile'].items()}, 'profile ' + prov)
        widths = dict(zip(rec['live_helpers'], rec['widths']))
        restored = {int(k) for k in w['helper_final']}
        endc = {r: d for r, d, where in fc.EVENTS if where == 'end frame'}
        full = [r for r in widths if r not in restored]
        hist = Counter(endc.get(r, 0) for r in full)
        classes = Counter((widths[r], endc[r]) for r in full if endc.get(r, 0) > 0)
        need(dict(hist) == EXPECT_CENSUS and len(full) == 356 and len(restored) == 78, 'census %s %s' % (prov, dict(hist)))
        need(all(endc.get(r, 0) == 0 for r in restored), 'cold-restored helpers pay no end climb')
        need(dict(classes) == EXPECT_CLASSES, 'classes %s' % prov)
        x_end = Counter(endc[r] for r in endc if r < 112)
        local_mass = sum(k * v for k, v in rec['paid'].items())
        census[prov] = dict(full_cleanup_helpers=len(full), cold_restored_helpers=len(restored),
                            end_climb_histogram={str(k): v for k, v in sorted(hist.items())},
                            end_climb_mass=sum(endc.get(r, 0) for r in full), local_mass=local_mass,
                            width_endclimb_classes={'%d,%d' % k: v for k, v in sorted(classes.items())},
                            x_end_climbs={str(k): v for k, v in sorted(x_end.items())},
                            convertible=sorted(r for r in full if endc.get(r, 0) > 0),
                            widths=widths, endc=endc)
    need(census['base']['convertible'] == census['extra']['convertible'], 'same convertible set in both providers')
    conv = {r: (census['extra']['widths'][r], census['extra']['endc'][r]) for r in census['extra']['convertible']}
    for prov in census:
        del census[prov]['widths'], census[prov]['endc']
    out['census'] = census
    c = census['extra']
    print('census (both providers): %d FULL-cleanup helpers, end climbs %s = %d rank units per call (%.1f%% of local '
          'mass %d); %d cold-restored helpers pay none'
          % (c['full_cleanup_helpers'], c['end_climb_histogram'], c['end_climb_mass'],
             100.0 * c['end_climb_mass'] / c['local_mass'], c['local_mass'], c['cold_restored_helpers']))

    # ---- 2. cost context from PR2374 -------------------------------------------------------------------------------
    raw = {k: pinned(args.repo, PR2374[0], *v) for k, v in PR2374_FILES.items()}
    geo = json.loads(raw['SPEC'])['geometry']
    outer = json.loads(raw['OUTER'])
    need('kappa = C - 1/F - B exactly (F = 1e3046, B = 1e-3022' in outer['fixed_grid_maximum'], 'PR2374 kappa formula')
    inv = raw['INVOICE'].decode()
    need('assert physical==live+helpers+centres+zero_buffers+2' in inv and 'physical<=parent_physical' in inv,
         'PR2374 physical-stock admission rule')
    live, helpers, centres, buffers_now = 66304, 434, 8, 78
    physical_now = live + helpers + centres + buffers_now + 2
    physical_all = physical_now + len(conv)
    need(physical_now == 66826 and physical_all <= geo['parent_physical'], 'physical headroom')
    need(buffers_now + len(conv) <= helpers, 'PR2322 private namespace NZ <= R')
    out['cost_context'] = dict(kappa_formula=outer['fixed_grid_maximum'][:120], parent_physical=geo['parent_physical'],
                               physical_now=physical_now, physical_if_all_converted=physical_all,
                               zero_buffers_now=buffers_now, zero_buffers_if_all=buffers_now + len(conv),
                               namespace_bound_R=helpers)
    print('cost context (PR2374): kappa = C - 1/F - B (F=1e3046, B=1e-3022), invoice items only enter admission; '
          'physical %d -> %d <= parent %d; zero buffers %d -> %d <= R = %d'
          % (physical_now, physical_all, geo['parent_physical'], buffers_now, buffers_now + len(conv), helpers))

    # ---- 3. prices ------------------------------------------------------------------------------------------------
    base = lp.CASES['pr2322_control']
    lp.WID = tuple(sorted(set(lp.WID) | {w - d for w, d in conv.values()}))
    lp.COLS = lp.patterns()
    a0 = 0.0016971957580326831            # LP ceiling root of the unchanged PR2322 words (PR2402)

    def apply(sel):
        inv_ = Counter(base['inv'])
        pg, pe = Counter(base['pg']), Counter(base['pe'])
        for r in sel:
            wd, d = conv[r]
            inv_[wd] -= 1
            inv_[wd - d] += 1
            pg[d] -= 1
            pe[d] -= 1
        need(min(inv_.values()) >= 0 and min(pg.values()) >= 0 and min(pe.values()) >= 0, 'conversion count')
        return {w_: inv_.get(w_, 0) for w_ in lp.WID}, dict(+pg), dict(+pe)

    def wmu(case, a):
        lp.CASES['t'] = dict(inv=case[0], pg=case[1], pe=case[2])
        return lp.lp_mu_float('t', a)[0] * lp.W_LIVE

    def root(case, lo, hi, it=40):
        for _ in range(it):
            mid = (lo + hi) / 2
            if wmu(case, mid) < lp.W_LIVE:
                lo = mid
            else:
                hi = mid
        return lo

    w0 = wmu(apply([]), a0)
    need(abs(w0 - lp.W_LIVE) < 1e-6, 'extended pattern set reproduces the PR2322 LP root')
    rows = []
    for cls in sorted(set(conv.values())):
        sel = [r for r in conv if conv[r] == cls][:1]
        db = root(apply(sel), a0 - 1e-5, a0 + 5e-5) - a0
        rows.append(dict(width=cls[0], end_climb=cls[1], count=sum(1 for v in conv.values() if v == cls), db_one=db))
        print('  one (width %d, end climb %d) helper cold-restored: db = %+.3e   [%d such helpers]'
              % (cls[0], cls[1], db, rows[-1]['count']))
    bulk = {}
    for d in (1, 2, 3):
        sel = [r for r in conv if conv[r][1] == d]
        bulk[str(d)] = dict(count=len(sel), lp_root=root(apply(sel), a0, 0.0025))
        print('  all %3d end-climb-%d helpers: LP ceiling %.10f (%+.2f%%)'
              % (len(sel), d, bulk[str(d)]['lp_root'], 100 * (bulk[str(d)]['lp_root'] / a0 - 1)))
    r_all = root(apply(list(conv)), a0, 0.0025)
    print('  ideal, all %d: LP ceiling %.10f (%+.2f%% over the PR2322 ceiling; PR2374 claims %.10f)'
          % (len(conv), r_all, 100 * (r_all / a0 - 1), KAPPA_2374))
    need(all(r['db_one'] >= -1e-12 for r in rows) and r_all > a0 * 1.05, 'prices')
    out['prices'] = dict(a0=a0, one_helper=rows, bulk_by_end_climb=bulk, all_converted_lp_root=r_all,
                         all_converted_gain=r_all / a0 - 1, pattern_widths=list(lp.WID), patterns=len(lp.COLS))
    out['scope'] = ('Pricing screen and census only: legality of moving any FULL-cleanup helper to a cold-restored end '
                    '(cleanup commutation, restoration gates and their frames) is not checked; prices are LP-ceiling '
                    'differences on the fixed PR2322 bin stock.')
    out['python'] = sys.version.split()[0]
    if args.out:
        with open(os.path.join(HERE, 'restoration_prices.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_RESTORATION_PRICES full_cleanup=356 end_climb_mass=%d convertible=%d one_d1=%+.3e one_d3=%+.3e '
          'ideal=%+.2f%% no_new_kappa' % (c['end_climb_mass'], len(conv),
                                          [r for r in rows if (r['width'], r['end_climb']) == (9, 1)][0]['db_one'],
                                          [r for r in rows if (r['width'], r['end_climb']) == (9, 3)][0]['db_one'],
                                          100 * (r_all / a0 - 1)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_RESTORATION_PRICES %s\n' % e)
        sys.exit(1)
