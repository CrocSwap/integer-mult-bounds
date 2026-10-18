#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""What PR2435's entrance raise actually changes, and what further raises are worth (standard library only).

PR2435 (jeremykothe2, head 324d7d35) raises the entrance frames of 24 copy-buffer helpers per word from dimension 1
to 2 on PR2322's words. It is a frame-only change (PR2446) and reports a conditional gain of 1.3164e-6 in kappa. This script
  1. decomposes the change per register with the vendored PR2387 frame-climb recount (both providers):
     - the climbs of the raised helpers themselves;
     - the climbs of their gate partners, which the refit drags along;
  2. checks that the PR2387 width-aware bin-pattern LP reproduces the realized gain (ceiling difference
     PR2322 -> PR2435);
  3. prices k further raises at PR2435's point, at selected k values between 1 and 26, two ways:
     - with PR2435's average per-raise local delta, partners included;
     - with only the raised helper's own climb change, i.e. a raise with no partner cost;
  4. censuses the remaining dimension-1 entering helpers: their shapes, and whether their entrance-frame gates
     lie in A only. A raise needs every gate at the entrance frame lifted together with its partners.
It is a pricing screen: no new raise is constructed or proven legal (entrance delivery; PR2446 scope).

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B entrance_raise.py [--repo PATH] [--fetch] [--remote URL] [--out]
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
    sys.stdout.write('FAIL_T74_ENTRANCE_RAISE refusing to run under python -O\n')
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
HEADS = {'pr2322': ('002304ef01c4416a127916169ae6d94c1bee052b', 'refs/pull/2322/head'),
         'pr2435': ('324d7d3590dc21003940a44cb0cbdc32b3620f25', 'refs/pull/2435/head')}
WORDS = {('pr2322', 'base'): ('research/t74-joint-owner-hillclimb/words/base.json.gz', 'f4dda9147af544ae4fe6d17582b8aa5e9916040b'),
         ('pr2322', 'extra'): ('research/t74-joint-owner-hillclimb/words/extra.json.gz', '471e4819c0c6b256e7b3999649f1391989d92e19'),
         ('pr2435', 'base'): ('research/gmx-t74-borrow43-handoff/new/borrow/words/BORROW-WORD-43base.json.gz',
                              '7e382c2d03ab32a62c3b0aa3d799612a126068af'),
         ('pr2435', 'extra'): ('research/gmx-t74-borrow43-handoff/new/borrow/words/BORROW-WORD-43extra.json.gz',
                               '29fa1b3a8b4618632116252bcbd6e2beac395d58')}
REALIZED_GAIN = 1.3163927958589024577e-6            # PR2435 body: exact kappa difference over PR2374


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def blob_id(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def vendored(rel, name, patch=None):
    path = os.path.join(HERE, rel)
    data = open(path, 'rb').read()
    need(blob_id(data) == VENDOR[rel][0] and hashlib.sha256(data).hexdigest() == VENDOR[rel][1], 'vendored pin ' + rel)
    src = data.decode()
    for old, new in (patch or []):
        need(src.count(old) == 1, 'patch anchor ' + rel)
        src = src.replace(old, new)
    mod = types.ModuleType(name)
    mod.__file__ = path
    exec(compile(src, path, 'exec'), mod.__dict__)
    return mod


def rank(vs):
    b = []
    for x in vs:
        for y in b:
            x = min(x, x ^ y)
        if x:
            b.append(x)
    return len(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    FC = vendored('vendor/pr2387/fill_check80.py', 'fc80', patch=[
        ("        d = len(F) - len(cur[r])\n", "        d = len(F) - len(cur[r])\n        EV.append((r, d, where, F))\n")])
    LP = vendored('vendor/pr2387/ceiling_lp.py', 'ceiling_lp')
    for commit, ref in HEADS.values():
        ok = subprocess.run(['git', '-C', args.repo, 'cat-file', '-e', commit + '^{commit}'], capture_output=True).returncode == 0
        if not ok and args.fetch:
            subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, ref], check=True)
    words, recs = {}, {}
    for key, (rel, blob) in WORDS.items():
        raw = subprocess.run(['git', '-C', args.repo, 'show', HEADS[key[0]][0] + ':' + rel], capture_output=True,
                             check=True).stdout
        need(blob_id(raw) == blob, 'word pin %s/%s' % key)
        w = json.loads(gzip.decompress(raw))
        FC.EV = []
        rec = FC.local_recount(w, '%s/%s' % key)
        need(dict(rec['paid']) == {int(k): v for k, v in w['report']['local_profile'].items()}, 'profile %s/%s' % key)
        ch, ev = defaultdict(list), defaultdict(list)
        for r, d, where, F in FC.EV:
            ev[r].append((d, where, F))
            if d:
                ch[r].append(d)
        words[key], recs[key] = w, dict(rec=rec, ch={r: tuple(sorted(v, reverse=True)) for r, v in ch.items()}, ev=ev)
    out = dict(object='PR2435 entrance raise: decomposition and further-raise prices')
    # ---- 1. decomposition -------------------------------------------------------------------------------------------
    dec = {}
    for prov in ('base', 'extra'):
        a, b = words[('pr2322', prov)], words[('pr2435', prov)]
        raised = sorted(int(k) for k in b['start_extra'] if a['start_extra'].get(k) != b['start_extra'][k])
        need(len(raised) == 24, prov + ': 24 raised entrances')
        ca, cb = recs[('pr2322', prov)]['ch'], recs[('pr2435', prov)]['ch']
        own, part, kinds = Counter(), Counter(), Counter()
        for r in set(ca) | set(cb):
            if ca.get(r) != cb.get(r):
                d = Counter(cb.get(r, ()))
                d.subtract(ca.get(r, ()))
                (own if r in raised else part).update(d)
                kinds['raised' if r in raised else ('X' if r < 112 else ('target' if r < 224 else 'helper'))] += 1
        dec[prov] = dict(raised=raised, registers_changed=dict(kinds),
                         own_delta={str(k): v for k, v in sorted(own.items()) if v},
                         partner_delta={str(k): v for k, v in sorted(part.items()) if v})
    need(dec['base']['own_delta'] == dec['extra']['own_delta'] and dec['base']['partner_delta'] == dec['extra']['partner_delta'],
         'providers agree')
    d = dec['extra']
    out['decomposition'] = dec
    print('1. PR2322 -> PR2435 (both providers): %s registers change; raised helpers %s, partners %s'
          % (d['registers_changed'], d['own_delta'], d['partner_delta']), flush=True)
    # ---- 2. LP calibration ----------------------------------------------------------------------------------------
    def case(key):
        rec = recs[key]['rec']
        return dict(inv=dict(Counter(rec['widths'])), p=dict(rec['paid']))

    def root(inv, p):
        LP.CASES['t'] = dict(inv={w_: inv.get(w_, 0) for w_ in LP.WID}, pg=dict(p), pe=dict(p))
        lo, hi = 0.0016, 0.0018
        for _ in range(45):
            mid = (lo + hi) / 2
            if LP.lp_mu_float('t', mid)[0] < 1:
                lo = mid
            else:
                hi = mid
        return lo
    c22, c35 = case(('pr2322', 'extra')), case(('pr2435', 'extra'))
    need(c22['p'] == case(('pr2322', 'base'))['p'] and c35['p'] == case(('pr2435', 'base'))['p'], 'provider profiles agree')
    r22, r35 = root(c22['inv'], c22['p']), root(c35['inv'], c35['p'])
    gain = r35 - r22
    need(abs(gain - REALIZED_GAIN) / REALIZED_GAIN < 1e-3, 'LP ceiling gain reproduces the realized PR2435 gain')
    out['calibration'] = dict(lp_root_pr2322=r22, lp_root_pr2435=r35, lp_gain=gain, realized_gain=REALIZED_GAIN)
    print('2. LP ceiling gain PR2322 -> PR2435 = %.4e vs realized kappa gain %.4e' % (gain, REALIZED_GAIN), flush=True)
    # ---- 3. further raises ------------------------------------------------------------------------------------------
    total = Counter({int(k): v for k, v in d['own_delta'].items()})
    total.update({int(k): v for k, v in d['partner_delta'].items()})
    per = {k: v / 24 for k, v in total.items()}
    need(all(abs(v - round(v)) < 1e-12 for v in per.values()), 'average per-raise delta is integral')
    per = {k: int(round(v)) for k, v in per.items()}
    own_only = {int(k): v // 24 for k, v in d['own_delta'].items()}
    ladder = []
    for k in (1, 2, 4, 6, 8, 10, 12, 16, 20, 26):
        rows = {}
        for name, delta in (('average', per), ('own_only', own_only)):
            inv = dict(c35['inv'])
            inv[8] -= k
            inv[7] += k
            p = Counter(c35['p'])
            for r, x in delta.items():
                p[r] += k * x
            rows[name] = root(inv, dict(+p)) - r35
        ladder.append(dict(k=k, **rows))
    out['per_raise_delta'] = dict(average={str(k): v for k, v in per.items()},
                                  own_only={str(k): v for k, v in own_only.items()})
    out['ladder'] = ladder
    best = max(ladder, key=lambda r: r['average'])
    print('3. further raises at PR2435 (width 8 -> 7 each): average pattern %s, own-only %s' % (per, own_only), flush=True)
    for r in ladder:
        print('   k=%2d  average %+.3e   own-only %+.3e' % (r['k'], r['average'], r['own_only']), flush=True)
    # ---- 4. census of remaining dim-1 entering helpers ---------------------------------------------------------------
    w = words[('pr2435', 'extra')]
    ev = recs[('pr2435', 'extra')]['ev']
    widths = dict(zip(recs[('pr2435', 'extra')]['rec']['live_helpers'], recs[('pr2435', 'extra')]['rec']['widths']))
    rem = [int(k) for k, F in w['start_extra'].items() if rank(F) == 1]
    shape, a_only = Counter(), 0
    for h in rem:
        first = next((dd for dd, wh, F in ev[h] if dd), None)
        shape[(widths[h], first)] += 1
        pre = [wh for dd, wh, F in ev[h][:next((i for i, x in enumerate(ev[h]) if x[0]), len(ev[h]))]]
        a_only += all(wh.startswith('A[') for wh in pre)
    out['census'] = dict(remaining_dim1_entrances=len(rem),
                         width_first_climb={'%d,%s' % k: v for k, v in sorted(shape.items(), key=str)},
                         entrance_gates_in_A_only=a_only)
    print('4. remaining dim-1 entering helpers: %d; (width, first climb) %s; entrance-frame gates in A only: %d'
          % (len(rem), dict(sorted(shape.items(), key=str)), a_only), flush=True)
    out['python'] = sys.version.split()[0]
    if args.out:
        with open(os.path.join(HERE, 'entrance_raise.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_ENTRANCE_RAISE lp_gain=%.4e realized=%.4e best_further=%+.3e@k=%d own_only_k1=%+.3e no_new_kappa'
          % (gain, REALIZED_GAIN, best['average'], best['k'], ladder[0]['own_only']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_ENTRANCE_RAISE %s\n' % e)
        sys.exit(1)
