#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact local word decompositions, numerical move prices and a certified owner-fill cap (standard library only).

Every frame climb of d dimensions on a register pays one recursive child of rank d (frame-climb rule of the vendored
PR2387 fill_check80.py, patched only to also record WHICH register paid each child).  So a change of the local words
is a set of per-register climb reshapes plus a change of the helper width inventory.  Mass is conserved
(local mass = 1856 + sum of helper widths, idle = bin capacity - hosted width), so only the shape of the
children matters, and the helper widths act through the width-aware bin-pattern LP of PR2387 / PR2360.

This script
  1. recounts per-register climbs of the pinned words of PR2312 (fb76f799), PR2322 (002304ef), PR2269 (b479fc55) and
     PR2339 (bf1742ae) and checks each recount against the word's own reported profile and width inventory;
  2. decomposes the realized changes PR2312 -> PR2322 (four handoffs) and PR2269 -> PR2339 (32 low + 5 high aliases)
     into per-register reshapes and checks that they add up exactly to the profile change;
  3. prices each move type at a = PR2374's claimed kappa by numerical re-solve of the bin-pattern LP (float simplex) and
     by LP-root differences, and calibrates against the realized PR2312 -> PR2322 gain;
  4. certifies (exact rational LP dual, 800-bit enclosures) that every legal whole-helper owner fill of the PR2322
     words has b < 0.001697195759, and that the certificate does not reject PR2374's claimed point;
  5. lists the untried sites with the PR2322 pre-handoff shape pattern and prices k more PR2322-type handoffs.
It is a pricing screen, not a construction: a priced handoff still needs a legal coherent handoff, native lowering,
an owner fill and the outer ledger.

Credits: PR2322 Vlado Vojdanovski (handoffs, words); PR2312 / PR2269 Jeremy Kothe (width exchange, borrow43 words);
PR2374 / PR2349 jeremykothe2, PR2363 mason-hale (owner fills on PR2322's words); PR2226 Cinna Davis (anticipatory
borrowing); PR2339 / PR2387 this author; PR2360 Jeremy Diviney and PR1129 Ali Romman (pattern-dual relaxation);
PR1319 / PR1297 T74 lineage.  Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage: python3 -I -B move_prices.py [--repo PATH] [--fetch] [--remote URL] [--out]
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
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_MOVE_PRICES refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
VENDOR = {  # byte copies of PR2387 head 20fb6953 (this author): (git blob, sha256)
    'vendor/pr2387/ceiling_lp.py': ('48362358660f74e0e235865df3e172494c191212',
                                    '63e2d35b07342508680e20f4b60c4da888acf4c771cd9b10400c21490f1491be'),
    'vendor/pr2387/fill_check80.py': ('557e0732bfe4c030436a11f5433143c10fa07821',
                                      '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    'vendor/pr2387/vendor/iter3/price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                                                  '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f'),
}
COMMITS = {'pr2312': ('fb76f799ccf078f51780076ebed3fd26b1db11c0', 'refs/pull/2312/head'),
           'pr2322': ('002304ef01c4416a127916169ae6d94c1bee052b', 'refs/pull/2322/head'),
           'pr2269': ('b479fc5567bc09ab9185bffe89b62594f36d74e5', 'refs/pull/2269/head'),
           'pr2339': ('bf1742aee4d855efb8bbd44a8419eddb33a679e5', 'refs/pull/2339/head')}
WORDS = {  # (word set, provider) -> (path, git blob, sha256); provider base = gauge44 (249 calls), extra (417 calls)
    ('pr2312', 'base'): ('research/gmx-t74-borrow43-width-exchange/new/borrow/words/BORROW-WORD-43base.json.gz',
                         '40effbbfe9b3664fe051d6e8a03220f09bf76676',
                         '4244149b59b287344b0e91aa50c6fa2a2491ee6c7a76d61cd352684a8182d005'),
    ('pr2312', 'extra'): ('research/gmx-t74-borrow43-width-exchange/new/borrow/words/BORROW-WORD-43extra.json.gz',
                          '2fe91bd80a6124bece6f80377ea20d1d02561af2',
                          '01d510cc4ba912567f6b02ea50b6b0e741ed231a3608de9c36e7eeccbdaf6cda'),
    ('pr2322', 'base'): ('research/t74-joint-owner-hillclimb/words/base.json.gz',
                         'f4dda9147af544ae4fe6d17582b8aa5e9916040b',
                         '93c32c9dc8ca18394b7f3afac2cb4fa8582a6cb77399441b5107b396e63ca0f9'),
    ('pr2322', 'extra'): ('research/t74-joint-owner-hillclimb/words/extra.json.gz',
                          '471e4819c0c6b256e7b3999649f1391989d92e19',
                          'aae6592eaa4cf8638f21d50c44d09d4f8a6bb079ddcf5e377711a10ee2ddb526'),
    ('pr2269', 'base'): ('research/gmx-t74-borrow43/new/borrow/words/BORROW-WORD-43base.json.gz',
                         '448dd795adba29392a90b34aa3f1b1b796c7e0bd',
                         '9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5'),
    ('pr2269', 'extra'): ('research/gmx-t74-borrow43/new/borrow/words/BORROW-WORD-43extra.json.gz',
                          '2b51ba96256283bbc5578f99b694c50edd8a0e35',
                          '87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734'),
    ('pr2339', 'base'): ('research/t74-low-alias-borrowing/words/BORROW-WORD-80base.json.gz',
                         'c5953dfdb0ee9ac0c2c73eb29e320582b4569d2b',
                         '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493'),
    ('pr2339', 'extra'): ('research/t74-low-alias-borrowing/words/BORROW-WORD-80extra.json.gz',
                          '852868543ed36efa799b3ed6dd76a0442b0d6ff1',
                          '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'),
}
KAPPA_2312 = Fraction('0.001696891067241618')        # PR2312 title / claim
KAPPA_2322 = Fraction('0.001697060296258836')        # PR2322 CLAIM.json
KAPPA_2374 = Fraction('0.001697194950901770426594081877309541199782925447437522970580')  # PR2374 body (58 digits)
CAP_2322 = '0.001697195759'
CALLS = {'base': 249, 'extra': 417}


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


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
    src = src.replace(old, old + '            CHILDREN[r].append(d)\n')   # the only change: record the payer
    fc = types.ModuleType('pr2387_fill_check80')
    fc.__file__ = path
    exec(compile(src, path, 'exec'), fc.__dict__)
    return lp, fc


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), capture_output=True, check=True).stdout


def ensure_commits(repo, fetch, remote):
    for name, (commit, ref) in COMMITS.items():
        ok = subprocess.run(['git', '-C', repo, 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode == 0
        if not ok and fetch:
            subprocess.run(['git', '-C', repo, 'fetch', '-q', remote, ref], check=True)
            ok = subprocess.run(['git', '-C', repo, 'cat-file', '-e', commit + '^{commit}'],
                                capture_output=True).returncode == 0
        need(ok, '%s commit %s absent (rerun with --fetch)' % (name, commit[:8]))


def recount(repo, fc, key):
    path, blob, sha = WORDS[key]
    data = git(repo, 'show', COMMITS[key[0]][0] + ':' + path)
    need(blob_id(data) == blob and hashlib.sha256(data).hexdigest() == sha, 'word pin %s/%s' % key)
    w = json.loads(gzip.decompress(data))
    fc.CHILDREN = defaultdict(list)
    rec = fc.local_recount(w, '%s/%s' % key)
    rep = w['report']
    need(dict(rec['paid']) == {int(k): v for k, v in rep['local_profile'].items()}, 'recounted profile %s/%s' % key)
    need(dict(Counter(rec['widths'])) == {int(k): v for k, v in rep['width_inventory'].items()},
         'recounted widths %s/%s' % key)
    removed = set(w['removed'])
    ch = {r: tuple(sorted(fc.CHILDREN.get(r, []), reverse=True)) for r in range(fc.REGISTERS) if r not in removed}
    need(Counter(d for c in ch.values() for d in c) + Counter(rec['copies']) == rec['paid'] or
         Counter(d for c in ch.values() for d in c) == rec['paid'] - Counter(rec['copies']), 'per-register sum %s/%s' % key)
    return dict(word=w, children=ch, paid=Counter(rec['paid']), widths=dict(zip(rec['live_helpers'], rec['widths'])),
                lenders={x[1] for x in w['warps']}, removed=removed)


def decompose(a, b):
    """Per-register reshapes from word a to word b; checks they add up to the profile change exactly."""
    gone = sorted(r for r in a['children'] if r not in b['children'])
    changed = sorted(r for r in b['children'] if r in a['children'] and a['children'][r] != b['children'][r])
    pred = Counter(a['paid'])
    for r in gone:
        pred.subtract(a['children'][r])
    for r in changed:
        pred.subtract(a['children'][r])
        pred.update(b['children'][r])
    need(+pred == b['paid'], 'decomposition does not add up')
    return gone, changed


def delta(minus=(), plus=()):
    c = Counter()
    for s in minus:
        c.subtract(s)
    for s in plus:
        c.update(s)
    return {k: v for k, v in c.items() if v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    lp, fc = load_vendor()
    ensure_commits(args.repo, args.fetch, args.remote)
    R = {k: recount(args.repo, fc, k) for k in WORDS}
    out = dict(object='PR2322 T74 words: per-register climb decomposition, move prices, owner-fill cap', a_price=str(KAPPA_2374))

    # ---- 2. realized decompositions -------------------------------------------------------------------------------
    HANDOFF = dict(helper=(1, 1, 1, 1), lender=((5, 1, 1, 1), (2, 1, 1, 1, 1, 1, 1)),
                   partner=((4, 1, 1, 1, 1), (3, 2, 1, 1, 1)))
    for prov in ('base', 'extra'):
        a, b = R[('pr2312', prov)], R[('pr2322', prov)]
        gone, changed = decompose(a, b)
        need(gone == [619, 621, 622, 623] and all(a['children'][r] == HANDOFF['helper'] for r in gone), 'PR2322 removed')
        xs = [r for r in changed if r < 112]
        need(xs == [1, 4, 6, 12] and all((a['children'][r], b['children'][r]) == HANDOFF['lender'] for r in xs),
             'PR2322 lenders')
        parts = [r for r in changed if r >= 224]
        need(parts == [616, 617, 618, 620] and all((a['children'][r], b['children'][r]) == HANDOFF['partner']
                                                    for r in parts), 'PR2322 partners')
        need(len(changed) == 8 and set(xs) <= b['lenders'] and not set(xs) & a['lenders'], 'PR2322 change set')
    out['pr2312_to_pr2322'] = dict(removed=[619, 621, 622, 623], lenders=[1, 4, 6, 12], partners=[616, 617, 618, 620],
                                   shapes={k: [list(x) for x in v] if k != 'helper' else list(v)
                                           for k, v in HANDOFF.items()}, both_providers=True)
    low = Counter()
    for prov in ('base', 'extra'):
        a, b = R[('pr2269', prov)], R[('pr2339', prov)]
        gone, changed = decompose(a, b)
        newl = sorted(b['lenders'] - a['lenders'])
        need(len(gone) == 37 and len(newl) == 37, 'PR2339 alias count')
        kinds = Counter()
        for r in newl:
            kinds[(a['children'][r], b['children'][r])] += 1
        tgt = Counter((a['children'][r], b['children'][r]) for r in changed if 112 <= r < 224)
        need(set(changed) - set(newl) == {r for r in changed if 112 <= r < 224}, 'PR2339 change set')
        low[prov] = dict(removed=Counter(a['children'][r] for r in gone), lenders=kinds, targets=tgt)
    out['pr2269_to_pr2339'] = {p: {k: [[list(x) if isinstance(x, tuple) else [list(y) for y in x], n]
                                       for x, n in sorted(v.items())] for k, v in d.items()} for p, d in low.items()}

    # ---- 3. move prices at a = PR2374 kappa ----------------------------------------------------------------------
    a0 = float(KAPPA_2374)
    h = lambda r: lp.h_float(r, a0)
    base = lp.CASES['pr2322_control']
    for prov, key in (('base', 'pg'), ('extra', 'pe')):
        need(dict(R[('pr2322', prov)]['paid']) == base[key], 'PR2387 pr2322_control case == recounted profile')
    need(dict(Counter(R[('pr2322', 'extra')]['widths'].values())) == base['inv'], 'PR2387 pr2322 inventory')
    lp.CASES['pr2312'] = dict(inv=dict(Counter(R[('pr2312', 'extra')]['widths'].values())),
                              pg=dict(R[('pr2312', 'base')]['paid']), pe=dict(R[('pr2312', 'extra')]['paid']))
    moves = {
        'pr2322_handoff': dict(inv={4: -1}, local=delta([HANDOFF['helper'], HANDOFF['lender'][0], HANDOFF['partner'][0]],
                                                         [HANDOFF['lender'][1], HANDOFF['partner'][1]])),
        'pr2339_low_alias': dict(inv={4: -1, 8: -1, 9: 1}, local=delta([(3, 2, 1, 1, 1), (1, 1, 1, 1)],
                                                                       [(2, 1, 1, 1, 1, 1, 1, 1)])),
        'pr2339_high_alias': dict(inv={5: -1}, local=delta([(2, 1, 1, 1), (5, 1, 1, 1)], [(2, 1, 1, 1, 1, 1, 1)])),
        'target_merge_1_1_to_2': dict(inv={}, local={1: -2, 2: 1}),
    }
    v0, _s, _d = lp.simplex([h(Rr - sum(p)) for Rr, p in lp.COLS], lp.rhs_of('pr2322_control'))
    root0 = lp.lp_root_float('pr2322_control')[0]

    def applied(k, mv):
        inv = dict(base['inv'])
        for w_, d_ in mv['inv'].items():
            inv[w_] += k * d_
        pg, pe = Counter(base['pg']), Counter(base['pe'])
        for r_, d_ in mv['local'].items():
            pg[r_] += k * d_
            pe[r_] += k * d_
        need(min(inv.values()) >= 0 and min(pg.values()) >= 0 and min(pe.values()) >= 0, 'move not applicable')
        return dict(inv=inv, pg=dict(+pg), pe=dict(+pe))

    def lp_root_wide(case):
        lo, hi = 0.0015, 0.0020
        for _ in range(50):
            mid = (lo + hi) / 2
            if lp.lp_mu_float(case, mid)[0] < 1:
                lo = mid
            else:
                hi = mid
        return lo

    out['move_prices'] = {}
    for name, mv in moves.items():
        lp.CASES['t'] = applied(1, mv)
        v1, _s, _d = lp.simplex([h(Rr - sum(p)) for Rr, p in lp.COLS], lp.rhs_of('t'))
        dlp = (v1 - v0) / 666
        dloc = sum(n * h(r) for r, n in mv['local'].items())
        db = lp_root_wide('t') - root0
        out['move_prices'][name] = dict(inventory_change=mv['inv'], local_change=mv['local'],
                                        mass_change=sum(r * n for r, n in mv['local'].items()),
                                        dLP_per_call=dlp, dlocal_per_call=dloc, net_per_call=dlp + dloc, db_one_move=db)
        print('%-24s inv %-22s local %-36s net/call %+.3e   db(one move, both providers) %+.3e'
              % (name, json.dumps(mv['inv']), json.dumps(mv['local']), dlp + dloc, db))
    mp = out['move_prices']
    need(mp['pr2322_handoff']['db_one_move'] > 0 and mp['pr2339_low_alias']['db_one_move'] < 0, 'move signs')
    need(abs(mp['pr2339_high_alias']['net_per_call']) < 1e-12, 'high alias is exactly price-neutral')
    for name in moves:
        need(mp[name]['mass_change'] == sum(w_ * d_ for w_, d_ in moves[name]['inv'].items()),
             'mass identity: local mass change = helper width change (%s)' % name)

    # calibration against realized claims
    r12 = lp.lp_root_float('pr2312')[0]
    out['calibration'] = dict(lp_root_pr2312=r12, lp_root_pr2322=root0, lp_predicted_gain=root0 - r12,
                              realized_gain=float(KAPPA_2322 - KAPPA_2312),
                              realized_fraction_pr2312=float(KAPPA_2312) / r12,
                              realized_fraction_pr2322=float(KAPPA_2322) / root0,
                              realized_fraction_pr2374=float(KAPPA_2374) / root0)
    print('calibration: LP ceiling gain PR2312 -> PR2322 = %.4e, realized claim gain = %.4e' %
          (root0 - r12, float(KAPPA_2322 - KAPPA_2312)))

    # ---- 4. certified owner-fill cap for the PR2322 words -----------------------------------------------------------
    ok, cert = lp.certify('pr2322_control', CAP_2322)
    need(ok, 'cap certificate for the PR2322 words')
    ok2, cert2 = lp.certify('pr2322_control', KAPPA_2374)
    need(not ok2, 'control: the certificate must not reject PR2374 (a legal fill is claimed there)')
    ok3, cert3 = lp.certify('pr2322_control', Fraction(KAPPA_2374) + Fraction(1, 10**12))
    out['owner_fill_cap'] = dict(case='PR2322 words (inventory and both profiles recounted here)', cap=CAP_2322,
                                 certificate=cert, control_pr2374_not_rejected=cert2,
                                 headroom_above_pr2374=float(Fraction(CAP_2322) - KAPPA_2374),
                                 lp_root_float=root0)
    print('certified: every legal whole-helper owner fill of the PR2322 words has b < %s (margin %.3g); '
          'PR2374 is not rejected; headroom <= %.3e' % (CAP_2322, cert['margin'], float(Fraction(CAP_2322) - KAPPA_2374)))

    # ---- 5. untried PR2322-pattern sites ------------------------------------------------------------------------------
    sites = {}
    for prov in ('base', 'extra'):
        w = R[('pr2322', prov)]
        ch = w['children']
        w4 = [r for r in w['widths'] if ch[r] == HANDOFF['helper']]
        xfree = [r for r in range(112) if ch[r] == HANDOFF['lender'][0] and r not in w['lenders']]
        blocks = defaultdict(list)
        for r in w4:
            blocks[(r - 224) // 8].append(r)
        rows = []
        for blk, regs in sorted(blocks.items()):
            mates = [(r, list(ch[r])) for r in range(224 + 8 * blk, 232 + 8 * blk) if r in ch]
            partners = [r for r, s in mates if s and s[0] == 4 and all(x == 1 for x in s[1:])]
            rows.append(dict(block=blk, width4_helpers=regs, partners_4_then_1s=partners,
                             removed_in_block=[r for r in range(224 + 8 * blk, 232 + 8 * blk) if r in w['removed']],
                             mates=mates))
        sites[prov] = dict(width4_1111_helpers=w4, free_x_5111_registers=xfree, blocks=rows)
    need(sites['base']['width4_1111_helpers'] == sites['extra']['width4_1111_helpers'] and
         sites['base']['free_x_5111_registers'] == sites['extra']['free_x_5111_registers'], 'sites differ by provider')
    s = sites['extra']
    exact = [r for r in s['blocks'] if r['partners_4_then_1s'] and
             all(len(m[1]) == 5 for m in r['mates'] if m[0] in r['partners_4_then_1s'])]
    kmax = min(len(s['width4_1111_helpers']), len(s['free_x_5111_registers']))
    ladder = []
    for k in (1, 2, 4, 8, kmax):
        lp.CASES['t'] = applied(k, moves['pr2322_handoff'])
        ladder.append([k, lp_root_wide('t') - root0])
    out['untried_sites'] = dict(width4_1111_helpers=s['width4_1111_helpers'],
                                free_x_5111_registers=s['free_x_5111_registers'],
                                blocks=s['blocks'], blocks_matching_pr2322_partner_shape=[r['block'] for r in exact],
                                lender_limited_kmax=kmax, db_for_k_more_pr2322_handoffs=ladder)
    print('untried: %d width-4 (1,1,1,1) helpers, %d unused (5,1,1,1) X registers; block(s) %s carry the exact PR2322 '
          'partner shape (4,1,1,1,1)' % (len(s['width4_1111_helpers']), len(s['free_x_5111_registers']),
                                          [r['block'] for r in exact]))
    for k, db in ladder:
        print('   %2d more PR2322-type handoffs (same reshapes): LP ceiling db = %+.3e' % (k, db))
    # the target-climb merges that accompany the PR2339 low aliases, priced on their own (no inventory change)
    for prov in ('base', 'extra'):
        need(all(delta([x], [y]) == {1: -2, 2: 1} for x, y in low[prov]['targets']),
             'PR2339 target changes are all one (1,1) -> (2) merge (%s)' % prov)
    nmerge = sum(low['extra']['targets'].values())
    need(nmerge == sum(low['base']['targets'].values()), 'PR2339 target merges per provider')
    lp.CASES['t'] = applied(nmerge, moves['target_merge_1_1_to_2'])
    out['pr2339_target_merges_alone'] = dict(count_per_word=nmerge, db_on_pr2322_words=lp_root_wide('t') - root0)
    print('the %d target merges (one (1,1)->(2) each) that accompany the PR2339 low aliases, alone on the PR2322 '
          'words: LP ceiling db = %+.3e' % (nmerge, out['pr2339_target_merges_alone']['db_on_pr2322_words']))
    out['scope'] = ('Pricing screen on fixed pinned words: moves are priced by their per-register climb reshapes and '
                    'width change only, through the PR2387 bin-pattern LP (windows, families, ports dropped). A priced '
                    'move is not a construction; the cap is a relaxation ceiling, not a kappa.')
    out['python'] = sys.version.split()[0]
    out['seconds'] = round(time.time() - t0, 1)
    if args.out:
        with open(os.path.join(HERE, 'move_prices.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_MOVE_PRICES cap=%s handoff_db=%+.3e low_alias_db=%+.3e high_alias_net=0 sites=%d/%d'
          % (CAP_2322, mp['pr2322_handoff']['db_one_move'], mp['pr2339_low_alias']['db_one_move'],
             len(s['width4_1111_helpers']), len(s['free_x_5111_registers'])))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_MOVE_PRICES %s\n' % e)
        sys.exit(1)
