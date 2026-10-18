#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Can FULL-cleanup helpers of the T74 PR2322 words be cold-restored? A constructive screen (standard library only).

PR2429 found that 355 FULL-cleanup helpers of the PR2322 words pay 525 rank units per call of end-of-call
restoration climbs, and priced the ideal of cold-restoring all of them at +10.8% of the LP ceiling. This script
tests the existing cold-restoration contract (PR2226 / PR601 lineage) on those helpers. Under that contract a
helper is restored inside the word at a partial frame, and a private zero buffer stands in for it in the FULL
cleanup.

1. Single-gate screen (exact).  In the inverse-reverse cleanup, find the helpers whose restoration is one write
   (h -= c s) with a dependency cone of only that gate, so that it commutes to the end of the forward word.
   Join h's frame with the source's frame and keep the helpers with a positive frame saving.
2. Construction (exact).  For each screened helper, build the converted word on the pattern of the existing
   restore sections, which restore the helper and also clear its input from every reader, X registers
   included:
     - append the restoring gate, then r -= a*h for every reader r, all at the join F of the frames of h, of
       its source and of every reader;
     - set helper_final = F;
     - make the cleanup buffer-free: reads of h before the restoring gate j read -c*s, and gate j and later
       reads of h are dropped.
   Then run the vendored PR2315 exact replay (forward and dual, arbitrary dirty inputs) and frame check. The
   construction follows the adversarial reviewer's correction of a first attempt.
3. Time-resolved frame heuristic (known proof gap; not an established upper bound).
   After h's last use, every variable of h's accumulated content must reach h through a gate chain that starts
   at a register holding it at that time. Frames only grow, so h's restored frame contains cur(h) plus the
   frame of such a holder for every variable. So the saving is at most
       s(h) = min(end climb, 9 - max_x min_{holder r} rank(cur(h) + cur(r))).
   This argument has the holder-substitution gap described in README.md. Its output is exploratory,
   priced numerically with the PR2387 width-aware LP (widths 3..9); the labels do not certify a bound.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B restoration_screen.py [--repo PATH] [--fetch] [--remote URL] [--out]
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
import types
from collections import Counter, defaultdict
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_COLD_RESTORATION_SCREEN refusing to run under python -O\n')
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
    'vendor/pr2315/words_check.py': ('0b646b9d5583c75a78e0c2dd7e9cfffa02055058',
                                     'b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6'),
}
HEAD_2322 = '002304ef01c4416a127916169ae6d94c1bee052b'
WORDS = {'base': ('research/t74-joint-owner-hillclimb/words/base.json.gz', 'f4dda9147af544ae4fe6d17582b8aa5e9916040b'),
         'extra': ('research/t74-joint-owner-hillclimb/words/extra.json.gz', '471e4819c0c6b256e7b3999649f1391989d92e19')}
N_REG, FULL_DIM = 704, 9
LP_ROOT_2322 = 0.0016971957580326831     # PR2402


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
    if patch is None:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    src = data.decode()
    for old, new in patch:
        need(src.count(old) == 1, 'patch anchor in ' + rel)
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


def basis(vs):
    b = []
    for x in vs:
        for y in b:
            x = min(x, x ^ y)
        if x:
            b.append(x)
    return b


def make_forward_rows(WC):
    import inspect
    src = inspect.getsource(WC.replay)
    src = src[:src.index("    diag = {}")] + "    return rows\n"
    src = src.replace("def replay(P, dual=False):", "def forward_rows(P, dual=False):")
    ns = dict(WC.__dict__)
    exec(src, ns)
    return ns['forward_rows']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    FC = vendored('vendor/pr2387/fill_check80.py', 'fc80', patch=[
        ('    for r in live:\n        climb(r, end[r], \'end frame\')',
         '    FINAL_CUR.update(cur)\n    for r in live:\n        climb(r, end[r], \'end frame\')'),
        ('        if d:\n            paid[d] += 1\n            per_reg[r] += d\n',
         '        if d:\n            paid[d] += 1\n            per_reg[r] += d\n            EV.append((r, d, where))\n')])
    WC = vendored('vendor/pr2315/words_check.py', 'words_check')
    LP = vendored('vendor/pr2387/ceiling_lp.py', 'ceiling_lp')
    global forward_rows
    forward_rows = make_forward_rows(WC)
    ok = subprocess.run(['git', '-C', args.repo, 'cat-file', '-e', HEAD_2322 + '^{commit}'], capture_output=True).returncode == 0
    if not ok and args.fetch:
        subprocess.run(['git', '-C', args.repo, 'fetch', '-q', args.remote, 'refs/pull/2322/head'], check=True)
    out = dict(object='cold restoration of FULL-cleanup helpers, PR2322 T74 words')
    for prov, (rel, blob) in WORDS.items():
        raw = subprocess.run(['git', '-C', args.repo, 'show', HEAD_2322 + ':' + rel], capture_output=True, check=True).stdout
        need(blob_id(raw) == blob, 'word pin ' + prov)
        w = json.loads(gzip.decompress(raw))
        FC.FINAL_CUR, FC.EV = {}, []
        rec = FC.local_recount(w, prov)
        cur_end = dict(FC.FINAL_CUR)
        endc = {r: d for r, d, wh in FC.EV if wh == 'end frame'}
        restored = {int(k) for k in w['helper_final']}
        widths = dict(zip(rec['live_helpers'], rec['widths']))
        full = sorted(h for h in widths if h not in restored and endc.get(h, 0) > 0)
        need(len(full) == 355, prov + ': 355 FULL-cleanup helpers with end climbs (PR2429)')
        # ---- 1. single-gate screen -------------------------------------------------------------------------------
        cl = w['cleanup']
        writes = defaultdict(list)
        for j, g in enumerate(cl):
            if g[0] in ('add', 'scale'):
                writes[g[1]].append(j)
        screened = []
        commuting = 0
        for h in full:
            Wh = writes.get(h, [])
            if not Wh:
                continue
            p = max(Wh)
            needed, cone = {h}, set()
            for j in range(p, -1, -1):
                g = cl[j]
                if g[0] in ('add', 'scale', 'warp') and g[1] in needed:
                    cone.add(j)
                    if g[0] == 'add':
                        needed.add(g[2])
            if not cone <= set(Wh) or len(Wh) != 1 or cl[Wh[0]][0] != 'add':
                continue
            commuting += 1
            s = cl[Wh[0]][2]
            if s not in cur_end:
                continue
            saving = FULL_DIM - rank(list(cur_end[h]) + list(cur_end[s]))
            if saving > 0:
                screened.append((h, Wh[0], s, saving))
        # ---- 2. construct and replay ------------------------------------------------------------------------------
        # Construction (follows the existing restore sections, which also clear restored inputs from their readers,
        # X registers included): append the restoring gate, then clear every reader r of h's input with
        # r -= a*h, all at the join F of the frames of h, s and every reader; the cleanup becomes buffer-free
        # (reads of h before the restoring cleanup gate j become reads of -c*s; gate j and later reads of h dropped).
        P0 = WC.parse_borrow(w)
        WC.replay(P0)
        WC.replay(P0, dual=True)                       # positive control: the unmodified word replays
        attempts = []
        for h, j, s, _sv in screened:
            g = w['cleanup'][j]
            c = Fraction(g[3], g[4])
            w1 = copy.deepcopy(w)
            w1['restore'].append(['add', h, s, g[3], g[4], basis(list(cur_end[h]) + list(cur_end[s]))])
            rows1 = forward_rows(WC.parse_borrow(w1))
            restored1 = restored | {h}
            readers = {r: val for r, row in rows1.items() if r not in restored1 and not 112 <= r < 224
                       for (var, word), val in row.items() if var == h}
            F = basis(list(cur_end[h]) + list(cur_end[s]) + [x for r in readers for x in cur_end[r]])
            w2 = copy.deepcopy(w)
            w2['restore'].append(['add', h, s, g[3], g[4], F])
            for r, a in sorted(readers.items()):
                q = -a
                w2['restore'].append(['add', r, h, q.numerator, q.denominator, F])
            w2['helper_final'][str(h)] = F
            newcl = []
            for k, x in enumerate(w['cleanup']):
                x = list(x)
                if k == j:
                    continue
                if x[0] == 'add' and x[2] == h:
                    if k > j:
                        continue
                    q = Fraction(x[3], x[4]) * (-c)
                    x = ['add', x[1], s, q.numerator, q.denominator, x[5]]
                newcl.append(x)
            w2['cleanup'] = newcl
            try:
                P2 = WC.parse_borrow(w2)
                WC.check_all_warps(P2)
                WC.frame_check(P2)
                WC.replay(P2)
                WC.replay(P2, dual=True)
                verdict = 'PASS'
            except WC.Reject as e:
                verdict = str(e)
            attempts.append(dict(helper=h, source=s, readers=len(readers),
                                 x_readers=sum(1 for r in readers if r < 112), joined_frame_dim=rank(F),
                                 saving=FULL_DIM - rank(F), verdict=verdict))
        need(len(screened) == 8, prov + ': expected 8 single-gate candidates')
        need(all(a['verdict'] == 'PASS' and a['saving'] == 0 for a in attempts),
             prov + ': expected legal conversions with zero saving: %s' % attempts)
        # ---- 3. time-resolved frame bound ---------------------------------------------------------------------------
        P = P0
        warpE = {wr['op']: wr['E'] for wr in P['warps']}
        items = list(P['pre']) + list(P['A']) + list(P['cut']) + list(P['B_items']) + list(P['post'])
        tlast = {}
        for i, it in enumerate(items):
            for r in ((it[1], it[2]) if it[0] == 'add' else (it[1],)):
                tlast[r] = i
        due = defaultdict(list)
        for h in full:
            due[tlast.get(h, -1)].append(h)
        rows = {r: {(r, ()): Fraction(1)} for r in P['live']}
        cur = {r: tuple(P['start'][r]) for r in P['live']}
        bound = {}

        def evaluate(h):
            acc = {var for var, _ in rows[h] if var != h}
            if not acc:
                return endc[h]
            holders = defaultdict(list)
            for r, row in rows.items():
                if r != h:
                    for var, _ in row:
                        if var in acc:
                            holders[var].append(r)
            worst = 0
            for x in acc:
                if not holders[x]:
                    return 0
                worst = max(worst, min(rank(list(cur[h]) + list(cur[r])) for r in holders[x]))
            return max(0, min(endc[h], FULL_DIM - worst))

        for h in due.get(-1, []):
            bound[h] = evaluate(h)
        for i, it in enumerate(items):
            if it[0] == 'add':
                t, s, c = it[1], it[2], it[3]
                dst = rows[t]
                for key, val in rows[s].items():
                    nv = dst.get(key, 0) + c * val
                    if nv:
                        dst[key] = nv
                    else:
                        dst.pop(key, None)
                if it[4] is not None:
                    cur[t] = it[4]
                    cur[s] = it[4]
            elif it[0] == 'scale':
                for key in rows[it[1]]:
                    rows[it[1]][key] *= it[2]
                if it[3] is not None:
                    cur[it[1]] = it[3]
            elif it[0] == 'warp':
                reg, k = it[1], it[2]
                letter = (abs(k), 0, 1 if k > 0 else -1)
                inverse = (letter[0], letter[1], -letter[2])
                rows[reg] = {(var, word[1:] if (word and word[0] == inverse) else (letter,) + word): val
                             for (var, word), val in rows[reg].items()}
                cur[reg] = tuple(warpE[abs(k)])
            for h in due.get(i, []):
                bound[h] = evaluate(h)
        need(set(bound) == set(full), prov + ': bound for every helper')
        out[prov] = dict(full_cleanup_helpers=len(full), single_gate_commuting=commuting,
                         single_gate_with_frame_saving=len(screened), attempts=attempts,
                         attempts_with_x_readers=sum(1 for a in attempts if a['x_readers']),
                         bound_histogram={str(k): v for k, v in sorted(Counter(bound.values()).items())},
                         bound_total=sum(bound.values()), end_climb_mass=sum(endc[h] for h in full),
                         bound=bound, endc={h: endc[h] for h in full}, widths={h: widths[h] for h in full})
        print('[%s] single-gate commuting restorations %d (all with a source-frame saving); all %d legal once the input '
              'readers are cleared (exact replay forward/dual PASS), but clearing them joins the frame to FULL: saving 0'
              % (prov, commuting, len(attempts)), flush=True)
        print('[%s] time-resolved frame bound over all 355: savings %s = %d of %d end-climb dims'
              % (prov, out[prov]['bound_histogram'], out[prov]['bound_total'], out[prov]['end_climb_mass']), flush=True)
    need(out['base']['bound'] == out['extra']['bound'], 'providers agree')
    # ---- price the bound -----------------------------------------------------------------------------------------
    B = LP.CASES['pr2322_control']
    LP.WID = tuple(range(3, 10))
    LP.COLS = LP.patterns()
    inv, pg, pe = Counter(B['inv']), Counter(B['pg']), Counter(B['pe'])
    e = out['extra']
    for h, s in e['bound'].items():
        if s:
            d, wd = e['endc'][h], e['widths'][h]
            inv[wd] -= 1
            inv[wd - s] += 1
            for Pp in (pg, pe):
                Pp[d] -= 1
                if d - s:
                    Pp[d - s] += 1
    LP.CASES['t'] = dict(inv={w_: inv.get(w_, 0) for w_ in LP.WID}, pg=dict(+pg), pe=dict(+pe))
    lo, hi = 0.0016, 0.0020
    for _ in range(36):
        mid = (lo + hi) / 2
        if LP.lp_mu_float('t', mid)[0] < 1:
            lo = mid
        else:
            hi = mid
    out['frame_bound_lp_root'] = lo
    out['frame_bound_gain'] = lo / LP_ROOT_2322 - 1
    print('frame-bound price: LP ceiling %.10f (%+.2f%%; PR2429 ideal +10.80%%)' % (lo, 100 * out['frame_bound_gain']))
    for prov in ('base', 'extra'):
        for k in ('bound', 'endc', 'widths'):
            out[prov][k] = {str(h): v for h, v in out[prov][k].items()}
    out['python'] = sys.version.split()[0]
    if args.out:
        with open(os.path.join(HERE, 'restoration_screen.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_COLD_RESTORATION_SCREEN single_gate=8 legal=8 saving=0 frame_bound=%d/525 frame_bound_gain=%+.2f%% '
          'no_new_kappa' % (out['extra']['bound_total'], 100 * out['frame_bound_gain']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_COLD_RESTORATION_SCREEN %s\n' % e)
        sys.exit(1)
