#!/usr/bin/env python3
"""No H1+H1 -> H2 fusion pair in the #4610 word by free scalar rewiring (negative result, no new kappa).

Mark (Matarener), with substantial Claude Code (Claude) assistance. Apache-2.0.

Reads only the public #4610 package (Cao Yifan / intqwq):
  research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz
  research/kappa-round3-warp-20261022/ARITHMETIC.json
and the bar of research/fragmentation-ceiling (DreamingOfClouds, #5226).

Question (#5226 Theorem B, #5243): is there a field with two consecutive rank-1 climbs E->F->G whose events
can be re-wired with free same-frame scalar operations so that it pays one rank-2 climb E->G instead?
Each such fusion lowers the fragmentation loss by 2 - 2^t* = 0.0041868 per call.

This script certifies, exactly and in a few seconds, the structural obstruction:
  (S1) every consecutive rank-1 pair has at least one event touching the field at the intermediate frame F;
  (S2) for every pair whose intermediate events are plain ADDs (1261 of 1363 per orientation) at least one
       partner field never occupies the target frame G at any time of the program, so the intermediate
       interaction cannot be moved after a merged climb;
  (S3) only 12 pairs (cold helpers at frame 0) have all partners in the start frame E at some time, and each
       is blocked before the merged climb by exactly one read of the partner by a main field at F, and that
       main never shares a frame with the helper afterwards;
  (P)  any repair that adds a paid job costs >= 1^t* = 1 > 0.0041868 (and a descent >= 1.99022, #5226 Thm D).
The exact row-level compensation searches (tools/compsearch.py, tools/cascade.py; 6 and 50 minutes) are
recorded in RESULT.json as evidence, not replayed here.

Usage: python3 -I -W error -B verify.py [--write]
Exit 0 and marker PASS_NO_FUSION_PAIR_SCALAR_REWIRING iff every assertion passes and RESULT.json matches.
"""
import collections
import gzip
import hashlib
import json
import os
import sys
from decimal import Decimal as D, getcontext

getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W3 = os.path.join(ROOT, 'research', 'kappa-round3-warp-20261022')
BAR = D('0.0030233')
WORD_SHA256 = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
COLD_PAIRS = [241, 243, 257, 259, 273, 275, 289, 291, 305, 307, 401, 417]


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def pw(x, t):
    x = D(x)
    return D(0) if x == 0 else (t * x.ln()).exp()


def load_word():
    with open(os.path.join(W3, 'ACTUAL-WORD.json.gz'), 'rb') as fh:
        raw = fh.read()
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, 'ACTUAL-WORD.json.gz bytes changed')
    return json.loads(gzip.decompress(raw))


def index(prog):
    """touch[role] = [(idx, kind, partner)], hist[role] = [(idx, new_frame)], climbs[f] = [(idx, a, b, r)]"""
    touch = collections.defaultdict(list)
    hist = collections.defaultdict(list)
    climbs = collections.defaultdict(list)
    for i, e in enumerate(prog):
        k = e[0]
        if k == 'climb':
            r = ('L', e[2])
            climbs[e[2]].append((i, e[3], e[4], e[5]))
            touch[r].append((i, 'climb', None))
            hist[r].append((i, e[4]))
        elif k == 'warp':
            r = tuple(e[1])
            touch[r].append((i, 'warp', None))
            hist[r].append((i, e[4]))
        elif k == 'center':
            r = ('C', e[1])
            touch[r].append((i, 'center', None))
            hist[r].append((i, e[3]))
        elif k == 'scalar':
            g = e[1]
            d = tuple(g[1])
            if g[0] in ('add', 'copy'):
                s = tuple(g[2])
                touch[d].append((i, 'dst:' + g[0], s))
                touch[s].append((i, 'src:' + g[0], d))
            else:
                touch[d].append((i, 'dst:' + g[0], None))
            if g[0] == 'clear':
                hist[d].append((i, e[2]))
    return touch, hist, climbs


def frame_at(start, hist, r, t):
    f = start.get(r)
    for i, ff in hist[r]:
        if i <= t:
            f = ff
        else:
            break
    return f


def structural(word, orient, control=None):
    """S1-S3 on one orientation. control='drop-main-read' deletes the blocking read of the first cold pair."""
    c = word['canonical']
    fr = c['frames']
    prog = list(word['programs'][orient])
    if control == 'drop-main-read':
        # the read  L70 += -L240  at frame 72 between the climbs of L240 (backward) / its transpose (forward)
        idx = [i for i, e in enumerate(prog) if e[0] == 'scalar' and e[1][0] == 'add'
               and sorted((tuple(e[1][1]), tuple(e[1][2]))) == [('L', 70), ('L', 240)] and e[2] == 72]
        need(len(idx) == 1, 'control read not found')
        prog[idx[0]] = ['phase', 'control_deleted_read']
    touch, hist, climbs = index(prog)
    start = {('L', i): f for i, f in enumerate(c['start'])}
    nf = len(c['start'])
    # H1/H2 replay check as in fragmentation-ceiling/verify.py
    cur = list(c['start'])
    for e in prog:
        if e[0] == 'climb':
            f, a, b, r = e[2], e[3], e[4], e[5]
            need(cur[f] == a and r == len(fr[b]) - len(fr[a]) and r > 0, 'climb not nested/ranked: %r' % (e,))
            cur[f] = b
        elif e[0] == 'warp':
            f, a, b = e[1][1], e[3], e[4]
            need(cur[f] == a and len(fr[a]) == len(fr[b]), 'warp changes dimension: %r' % (e,))
            cur[f] = b
    need(cur == list(c['final']), 'final frames')
    out = collections.Counter()
    out['climbs'] = sum(len(v) for v in climbs.values())
    out['rank1_climbs'] = sum(1 for v in climbs.values() for x in v if x[3] == 1)
    cold_detail = []
    feasible_pairs = []
    for f, cl in climbs.items():
        for (i1, E, F, r1), (i2, F2, G, r2) in zip(cl, cl[1:]):
            if r1 != 1 or r2 != 1:
                continue
            # F2 may differ from F when the field is warped between the climbs (those pairs are counted below)
            out['pairs'] += 1
            between = [t for t in touch[('L', f)] if i1 < t[0] < i2]
            if not between:
                out['idle_pairs'] += 1
                continue
            if any(t[1] not in ('src:add', 'dst:add') for t in between):
                out['pairs_with_warp_or_nonadd'] += 1
                continue
            out['pure_add_pairs'] += 1
            partners = [P for _, _, P in between]
            ever_G = all(any(ff == G for _, ff in hist[P]) or start.get(P) == G for P in partners)
            ever_E = all(any(ff == E for _, ff in hist[P]) or start.get(P) == E for P in partners)
            if not ever_G:
                out['pure_add_pairs_partner_never_in_G'] += 1
            if ever_E:
                out['pure_add_pairs_all_partners_ever_in_E'] += 1
            # exact relocation test (frame-level): move every intervening event to a time when the field
            # (in E before the merged climb, in G after it) and its partner share a frame, with the partner's
            # value unchanged (field is dst) or only receiving commuting adds (field is src) in between.
            n = len(prog)
            nxt = min([t[0] for t in touch[('L', f)] if t[0] > i2], default=n)
            prv = max([t[0] for t in touch[('L', f)] if t[0] < i1], default=-1)

            def quiet(P, lo, hi, p_is_dst):
                for i, k, _ in touch[P]:
                    if lo < i < hi:
                        if k == 'climb':
                            continue
                        if p_is_dst and k == 'dst:add':
                            continue
                        if (not p_is_dst) and k.startswith('src:add'):
                            continue
                        return False
                return True
            ok_late = ok_early = True
            for j, k, P in between:
                p_is_dst = k.startswith('src')
                good = False
                for ci, _ in [(i2, None)] + [(ii, ff) for ii, ff in hist[P] if i2 < ii < nxt]:
                    if frame_at(start, hist, P, ci) == G and quiet(P, j, ci + 1, p_is_dst):
                        good = True
                        break
                ok_late = ok_late and good
                good = False
                for ci, _ in [(prv, None)] + [(ii, ff) for ii, ff in hist[P] if prv < ii < i1]:
                    if frame_at(start, hist, P, max(ci, 0)) == E and quiet(P, ci, j, p_is_dst):
                        good = True
                        break
                ok_early = ok_early and good
            if ok_late or ok_early:
                out['relocatable_pairs'] += 1
                feasible_pairs.append((f, i1, i2, 'late' if ok_late else 'early'))
            if ever_E and f in COLD_PAIRS + [x - 1 for x in COLD_PAIRS]:
                # S3 detail: the single blocking read of the partner by a main at F
                need(len(between) == 1, 'cold pair has one intervening event')
                j, k, P = between[0]
                p_enter = max([i for i, ff in hist[P] if i < j and ff == F], default=-1)
                # backward: a main reads P (M += q P); forward (the transpose): the main feeds P (P += q M)
                reads = [(i, M) for i, kk, M in touch[P] if p_enter < i < j and kk in ('src:add', 'dst:add')]
                mains = [M for _, M in reads if M[1] < 224]
                shared_later = []
                for i, M in reads:
                    for tt, ff in hist[M]:
                        if tt > i and (ff == G or ff == E):
                            shared_later.append((M, tt, ff))
                cold_detail.append(dict(field=f, partner=P[1], E=E, F=F, G=G, blocking_events=[(i, M[1]) for i, M in reads],
                                        main_readers=len(mains), reader_later_in_E_or_G=shared_later))
    for key in ('idle_pairs', 'pairs_with_warp_or_nonadd', 'pure_add_pairs', 'pure_add_pairs_partner_never_in_G',
                'pure_add_pairs_all_partners_ever_in_E', 'relocatable_pairs'):
        out[key] += 0
    return dict(out), cold_detail, feasible_pairs


def main():
    write = '--write' in sys.argv
    word = load_word()
    with open(os.path.join(W3, 'ARITHMETIC.json'), encoding='utf-8') as fh:
        A = json.load(fh)
    need(sum(A['local_paid'].values()) == 3298 and A['local_paid']['1'] == 2201, 'ARITHMETIC local_paid census')
    result = dict(schema='fusion-pair-scalar-rewiring/1', word_sha256=WORD_SHA256, bar=str(BAR), orientations={})
    for orient in ('forward', 'backward'):
        out, cold, feas = structural(word, orient)
        need(out['climbs'] == 3290 and out['rank1_climbs'] == 2201, '%s climb census' % orient)
        need(out['pairs'] == 1363, '%s: 1363 consecutive rank-1 pairs' % orient)
        need(out['idle_pairs'] == 0, 'S1: an idle pair exists')
        need(out['pure_add_pairs'] == 1261 and out['pairs_with_warp_or_nonadd'] == 102, '%s pair classes' % orient)
        need(out['pure_add_pairs_partner_never_in_G'] == 1261, 'S2: some pure-add pair has every partner in G at some time')
        need(out['pure_add_pairs_all_partners_ever_in_E'] == 12, 'S3: 12 cold pairs')
        need(out.get('relocatable_pairs', 0) == 0 and not feas, 'a relocatable pair exists: %r' % (feas,))
        need(len(cold) == 12 and all(len(x['blocking_events']) == 1 and x['main_readers'] == 1 and not x['reader_later_in_E_or_G']
                                     for x in cold), 'S3 detail: one main event on the partner, no later shared frame')
        result['orientations'][orient] = dict(census=out, cold_pairs=cold)
        print('[%s] %s' % (orient, json.dumps(out, sort_keys=True)))
    # positive control: deleting the blocking main read makes the first cold pair relocatable in both orientations
    for orient in ('forward', 'backward'):
        out, _, feas = structural(word, orient, control='drop-main-read')
        need(out['relocatable_pairs'] == 1 and len(feas) == 1 and feas[0][0] in (240, 241), 'control: %r' % (feas,))
        print('[control %s] deleting the main read makes exactly one pair relocatable: %r' % (orient, feas))
    # negative control: a wrong climb rank is rejected by the H2 replay
    bad = json.loads(json.dumps(word))
    for e in bad['programs']['backward']:
        if e[0] == 'climb':
            e[5] += 1
            break
    try:
        structural(bad, 'backward')
    except AssertionError:
        print('[control] corrupted climb rank rejected')
    else:
        need(False, 'corrupted word accepted')
    # prices at the bar t* and at the #4610 root
    prices = {}
    for name, t in (('bar_0.0030233', 1 - BAR), ('root_4610', 1 - D('0.0030217758'))):
        merge = 2 - pw(2, t)
        extra_job = pw(1, t)
        descent = pw(1, t) + pw(10, t) - pw(9, t)
        need(extra_job > merge * 200 and descent > merge, 'price order')
        prices[name] = dict(t=str(t), merge_gain_1plus1_to_2=str(merge), extra_rank1_job=str(extra_job), descent_price_thmD=str(descent),
                            needed_per_call_for_bar='0.0209331969')
        print('[price %s] merge gain %s, one extra paid rank-1 job %s, descent %s' % (name, merge, extra_job, descent))
    need(abs(D(prices['bar_0.0030233']['merge_gain_1plus1_to_2']) - D('0.0041868')) < D('1e-6'), 'merge value of #5226 [10]')
    result['prices'] = prices
    result['row_level_searches'] = {
        'note': 'exact rational row engine (same convention as PR #5377 native.py); run by tools/compsearch.py and tools/cascade.py '
                'on the backward word; 6 and 50 minutes; not part of the registered replay',
        'compsearch_backward': dict(pairs=1261, deficits=2111, repayable_deficits=12, fully_repayable_pairs=0,
                                    repayable_deficits_description='the 12 partner-helper deficits of the cold pairs, repaid at frame 0 before the climbs; '
                                                                   'the main-read deficit of each of these pairs is never repayable'),
        'cascade_backward': dict(pair_variants=2522, successes=0, repayments=0, dead_over_24_deficient_fields=1446, unfinished_with_deficits=1076,
                                 sampling='frames with more than 80 members tested every 100th version'),
        'forward': 'not run to completion; the forward program is the transpose of the backward program and shows the same obstruction (S1-S3 above)',
    }
    path = os.path.join(HERE, 'RESULT.json')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if write:
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    else:
        with open(path, encoding='utf-8', newline='') as fh:
            need(fh.read() == text, 'RESULT.json differs from the recomputed result; run with --write to refresh')
    print('PASS_NO_FUSION_PAIR_SCALAR_REWIRING')


if __name__ == '__main__':
    main()
