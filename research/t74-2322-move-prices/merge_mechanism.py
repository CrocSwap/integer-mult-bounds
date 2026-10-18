#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Where the PR2339 target-climb merges come from, which lenders can produce them, and what a lender is worth.

Follow-up to move_prices.py, answering its open question "can the 26 (1,1)->(2) target merges be obtained without
the losing low-lender inventory change?".  Standard library only; reuses move_prices.py's pinned loaders.

  1. Mechanism (both providers, all 26 merged targets).  In the PR2269 words each merged target climbs through one
     intermediate frame dimension that disappears in the PR2339 words.  Every gate that touches the target at
     that skipped frame has a partner register that PR2339 removes (a low-alias helper).  Every merged target
     receives PR2339 anticipatory initial corrections, which run at frame 0 and pay nothing.  So the merge is the
     helper's early interaction with the target, replaced by a free frame-0 correction from a frame-0 lender.
  2. Lender capacity on the PR2322 words.  A frame-0 lender that takes over a FULL-ending role must climb to FULL
     (dimension 9 = H).  Its width therefore becomes 9 and it absorbs 9 - end_dim.  The census of helper end
     dimensions shows that only the 32 PR2226 lenders end below FULL with room for a 5-dimension take-over
     (end_dim 4).  The only other frame-0 helpers ending below FULL (8 ending at 7, 8 ending at 8) hand off at
     dimension 7-8 into first frames of dimension 4-5, which fails the rank-zero handoff condition (PR2339 README).
  3. Prices on the PR2322 words (LP-ceiling differences, PR2387 bin-pattern LP, both providers).  The PR2339
     pattern (width-4 lender -> 9) loses -1.91e-7 per alias, and still -7.8e-8 with a full merge credited to every
     alias.  A width-5 lender is no better.  The hypothetical higher-rank take-overs (8 -> 9, 7 -> 9) would be worth
     about +1.4e-6 and +0.85e-6 each, before any frame-raising cost.  This is the price tag on changing the
     rank-zero premise; nothing here constructs one.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits as in move_prices.py.
Usage: python3 -I -B merge_mechanism.py [--repo PATH] [--fetch] [--out]
"""

import argparse
import gzip
import importlib.util
import json
import os
import sys
import time
from collections import Counter

if not __debug__:
    sys.stdout.write('FAIL_T74_MERGE_MECHANISM refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('move_prices', os.path.join(HERE, 'move_prices.py'))
MP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MP)
need = MP.need


def span_dim(F):
    basis = []
    for v in F:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def load_word(repo, key):
    path, blob, sha = MP.WORDS[key]
    data = MP.git(repo, 'show', MP.COMMITS[key[0]][0] + ':' + path)
    need(MP.blob_id(data) == blob, 'word pin %s/%s' % key)
    return json.loads(gzip.decompress(data))


def target_gates(w, t):
    """(section, index, frame dimension, partner) for every framed gate on t in A, B and restore."""
    out = []
    for sec in ('A', 'B', 'restore'):
        for i, g in enumerate(w[sec]):
            if g[0] == 'add' and t in (g[1], g[2]) and g[-1] is not None:
                out.append((sec, i, span_dim(g[-1]), g[2] if g[1] == t else g[1]))
            elif g[0] == 'scale' and g[1] == t and g[-1] is not None:
                out.append((sec, i, span_dim(g[-1]), None))
    return out


def climb_dims(gates):
    seq = []
    for _s, _i, d, _p in gates:
        if d and (not seq or d > seq[-1]):
            seq.append(d)
    return seq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=MP.REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=MP.REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    lp, fc = MP.load_vendor()
    MP.ensure_commits(args.repo, args.fetch, args.remote)
    out = dict(object='PR2339 target-climb merges: mechanism, lender capacity and prices on the PR2322 words')

    # ---- 1. mechanism ------------------------------------------------------------------------------------------
    mech = {}
    for prov in ('base', 'extra'):
        a = MP.recount(args.repo, fc, ('pr2269', prov))
        b = MP.recount(args.repo, fc, ('pr2339', prov))
        w43, w80 = a['word'], b['word']
        merged = sorted(r for r in b['children'] if 112 <= r < 224 and a['children'][r] != b['children'][r])
        need(len(merged) == 26, 'expected 26 merged targets (%s)' % prov)
        removed80 = set(w80['removed']) - set(w43['removed'])
        corrected = Counter(c['target'] for c in w80['initial_corrections'])
        rows = []
        for t in merged:
            g43, g80 = target_gates(w43, t), target_gates(w80, t)
            d43, d80 = climb_dims(g43), climb_dims(g80)
            skipped = sorted(set(d43) - set(d80))
            need(len(skipped) == 1 and set(d80) <= set(d43), 'target %d: one skipped frame (%s %s)' % (t, d43, d80))
            partners = sorted({p for _s, _i, d, p in g43 if d == skipped[0]})
            need(partners and all(p in removed80 for p in partners),
                 'target %d: gates at the skipped frame all come from removed low-alias helpers' % t)
            need(corrected[t] >= 1, 'target %d receives anticipatory initial corrections' % t)
            rows.append(dict(target=t, dims_pr2269=d43, dims_pr2339=d80, skipped_dim=skipped[0],
                             partners_at_skipped_frame=partners, initial_corrections=corrected[t]))
        mech[prov] = dict(merged_targets=merged, corrected_targets=len(corrected), rows=rows)
    need([r['target'] for r in mech['base']['rows']] == [r['target'] for r in mech['extra']['rows']], 'providers')
    out['mechanism'] = mech
    print('mechanism: all 26 merged targets (both providers) skip exactly one intermediate frame; every gate at that '
          'frame in PR2269 comes from a helper PR2339 removes; each receives frame-0 initial corrections '
          '(%d of %d corrected targets merge)' % (len(mech['extra']['rows']), mech['extra']['corrected_targets']))

    # ---- 2. lender capacity census on the PR2322 words ----------------------------------------------------------
    cen = {}
    for prov in ('base', 'extra'):
        w = load_word(args.repo, ('pr2322', prov))
        rec = MP.recount(args.repo, fc, ('pr2322', prov))
        end = {int(k): span_dim(F) for k, F in w['helper_final'].items()}
        start = {int(k): span_dim(F) for k, F in w['start_extra'].items()}
        helpers = rec['widths']
        frame0 = {r: end.get(r, 9) for r in helpers if r not in start}
        by_end = Counter(frame0.values())
        need(all(rec['widths'][r] == frame0[r] for r in frame0), 'frame-0 helper width = end dimension')
        need(max(helpers.values()) <= 9, 'helper widths are bounded by the frame dimension H = 9')
        cen[prov] = dict(frame0_helpers_by_end_dim=dict(sorted(by_end.items())),
                         end4=sorted(r for r, e in frame0.items() if e == 4),
                         end7=sorted(r for r, e in frame0.items() if e == 7),
                         end8=sorted(r for r, e in frame0.items() if e == 8))
    need(cen['base']['frame0_helpers_by_end_dim'] == cen['extra']['frame0_helpers_by_end_dim'], 'census providers')
    pr2226 = sorted(r for r in cen['extra']['end4'] if 273 <= r <= 394)   # the PR2226 low lenders
    need(cen['extra']['end4'] == pr2226 and len(pr2226) == 32 and min(pr2226) == 273 and max(pr2226) == 394,
         'the frame-0 end-dimension-4 helpers are exactly the 32 PR2226 lenders in 273..394')
    c = cen['extra']['frame0_helpers_by_end_dim']
    need(c.get(4) == 32 and c.get(7) == 8 and c.get(8) == 8 and set(c) == {4, 7, 8, 9}, 'census %s' % c)
    out['lender_census'] = cen
    print('lender census (PR2322 words, frame-0 helpers by end dimension): %s; the 32 at dimension 4 are the PR2226 '
          'lenders 273..394' % c)

    # ---- 3. prices -----------------------------------------------------------------------------------------------
    base = lp.CASES['pr2322_control']

    def root(inv, pg, pe):
        lp.CASES['t'] = dict(inv=inv, pg=pg, pe=pe)
        lo, hi = 0.0015, 0.0020
        for _ in range(45):
            mid = (lo + hi) / 2
            if lp.lp_mu_float('t', mid)[0] < 1:
                lo = mid
            else:
                hi = mid
        return lo

    r0 = root(dict(base['inv']), base['pg'], base['pe'])
    removed_shape = (3, 2, 1, 1, 1)          # the width-8 helper every PR2339 low alias removes
    variants = [('PR2339 pattern: width-4 lender ending dim 4 -> 9', 4, (1, 1, 1, 1), (2, 1, 1, 1, 1, 1, 1, 1), 'rank-zero'),
                ('width-5 lender -> 9 (2+1+1 absorbed)', 5, (2, 1, 1, 1), (2, 2, 1, 1, 1, 1, 1), 'no such frame-0 lender'),
                ('width-7 lender ending dim 7 -> 9', 7, (3, 2, 1, 1), (3, 2, 1, 1, 1, 1), 'fails rank-zero'),
                ('width-8 lender ending dim 8 -> 9', 8, (3, 2, 1, 1, 1), (3, 2, 1, 1, 1, 1), 'fails rank-zero')]
    prices = []
    for name, lw, old, new, status in variants:
        need(sum(new) == 9 and sum(old) == lw, 'variant widths')
        row = dict(variant=name, lender_width=lw, lender_old=list(old), lender_new=list(new), status=status)
        for merges in (0, 1):
            inv = dict(base['inv'])
            inv[8] -= 1
            inv[lw] -= 1
            inv[9] += 1
            pg, pe = Counter(base['pg']), Counter(base['pe'])
            for P in (pg, pe):
                P.subtract(removed_shape)
                P.subtract(old)
                P.update(new)
                if merges:
                    P.subtract({1: 2})
                    P.update({2: 1})
            row['db_merges_%d' % merges] = root(inv, dict(+pg), dict(+pe)) - r0
        prices.append(row)
        print('%-48s [%s] db = %+.3e (no merge), %+.3e (one merge credited)'
              % (name, status, row['db_merges_0'], row['db_merges_1']))
    need(prices[0]['db_merges_1'] < 0 and prices[1]['db_merges_1'] < 0, 'realizable lender patterns lose')
    need(prices[2]['db_merges_0'] > 0 and prices[3]['db_merges_0'] > 0, 'higher-rank take-overs priced positive')
    out['prices_on_pr2322_words'] = prices
    out['conclusion'] = ('Under the rank-zero anticipatory handoff, the target merges come only with width-4 -> 9 '
                         'lenders and every such alias loses even with full merge credit; separating them requires a '
                         'changed handoff premise (lenders ending at dimension 7-8), priced at up to +1.4e-6 each '
                         'before frame-raising costs.')
    out['python'] = sys.version.split()[0]
    if args.out:
        with open(os.path.join(HERE, 'merge_mechanism.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_MERGE_MECHANISM merged=26 lenders_end4=32 pr2339_alias_db=%+.3e takeover8_db=%+.3e'
          % (prices[0]['db_merges_1'], prices[3]['db_merges_0']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except MP.Fail as e:
        sys.stdout.write('FAIL_T74_MERGE_MECHANISM %s\n' % e)
        sys.exit(1)
