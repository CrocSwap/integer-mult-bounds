# SPDX-License-Identifier: Apache-2.0
"""Scope B: PR #3015's two final words (and PR #2979's parent words as positive controls) through this contributor's
lineage checks, with the vendored byte-pinned modules as libraries and no code of either PR.

word_pipeline(w, declared, expect) runs, in this order (each step raises with its own rule id):
  parse (vendored parser + validated initial corrections; wc.format / words.corrections)
  -> warp algebra of every B record (wc.warp)
  -> literal frame recount (wc.frame): paid local profile, width inventory, helper widths
  -> words.counts (live inputs, helpers, private buffers, warp records, initial corrections = expect)
  -> words.report_fields (the word's own report equals the recount)
  -> words.declared (the recount equals the declared local profile and inventory of EDITS.json / CLAIM.json)
  -> forward replay and dual replay of all live inputs in the free-operator model through cleanup and the target
     endpoint (wc.replay, orientation recorded)
  -> the own exact tracker through restore and cleanup (words.tracker: targets Y_t + X_t, restored registers their own
     input and every private buffer zero before cleanup; the final identity and zero buffers after cleanup)
  -> words.cleanup (the literal cleanup equals the own inverse-reverse re-derivation, frames aside, every item at FULL)
  -> words.buffers (the cleanup's private buffers are exactly the helper_final endpoints, one each).
Standard library only; Python 3.8-compatible syntax.
"""
from collections import Counter

import audit_lib as AL
import check_words as CW
import words_check as WC
from audit_common import need

V = AL.V


def counts(P, w):
    return dict(live=len(P['live']), helpers=len([r for r in P['live'] if r >= 2 * V]), buffers=len(P['buffers']),
                warps=len(w['warps']), corrections=len(w.get('initial_corrections', [])),
                a_prelude_events=w['prelude_events'],
                sections=dict((k, len(w[k])) for k in ('A', 'B', 'restore', 'cut', 'precondition', 'compensation',
                                                       'cleanup')))


def check_counts(c, expect):
    got = dict((k, c[k]) for k in expect)
    need(got == dict(expect), 'words.counts: %r != %r' % (got, dict(expect)))


def check_report(P, fr):
    need(fr['paid'] == P['claimed_profile'] and fr['inventory'] == P['claimed_inventory'],
         'words.report_fields: report %r %r != recount %r %r' % (P['claimed_profile'], P['claimed_inventory'],
                                                                  fr['paid'], fr['inventory']))


def check_declared(fr, declared):
    prof = AL.intkeys(declared['local_profile'])
    inv = AL.intkeys(declared['width_inventory'])
    need(fr['paid'] == prof and fr['inventory'] == inv,
         'words.declared: recount %r %r != declared %r %r' % (fr['paid'], fr['inventory'], prof, inv))


def check_cleanup(w):
    mine = AL.rederive_cleanup(w)
    need([g[:-1] for g in mine] == [g[:-1] for g in w['cleanup']],
         'words.cleanup: the literal cleanup is not the own inverse-reverse re-derivation')
    full = WC.span([1 << b for b in range(9)])
    need(all(WC.span(g[-1]) == full for g in w['cleanup']), 'words.cleanup: an item is not at FULL')
    return dict(items=len(mine), literal_equal=True, all_at_full=True)


def check_buffers(w, P):
    n = 2 * V + w['report']['R']
    touched = set()
    for g in w['cleanup']:
        for r in ((g[1],) if g[0] == 'warp' else ((g[1], g[2]) if g[0] == 'add' else (g[1],))):
            if r >= n:
                touched.add(r)
    ends = set(int(k) + n for k in w['helper_final'])
    need(touched == ends == set(P['buffers']), 'words.buffers: cleanup buffers %d != helper_final endpoints %d'
         % (len(touched), len(ends)))
    return dict(private_buffers=len(ends), offset=n)


def track(w):
    """One exact forward pass of the own tracker (audit_lib rows: every live register its own symbol, private buffers
    zero, warp letters as formal words) through corrections, precondition, compensation, A, cut, B with its warps,
    restore and cleanup.  Returns the pre-cleanup and final conditions (rule words.tracker, see tracker_check)."""
    rows = AL.init_rows(w)
    n = AL.nregs(w)
    removed = set(w['removed'])
    restored = set(int(k) for k in w['helper_final'])
    live = [r for r in range(n) if r not in removed]
    pre = None
    for sec, i, g in AL.events(w, cleanup=True):
        if sec == 'cleanup' and pre is None:
            pre = dict(targets_final=all(rows[V + t] == AL.target_final(t) for t in range(V)),
                       restored_own=all(rows[r] == AL.own_symbol(r) for r in restored),
                       buffers_zero=all(not rows[b + n] for b in restored),
                       rows_with_operator_words=sum(1 for r in live if any(wd for _, wd in rows[r])))
        AL.apply(rows, g)
    need(pre is not None, 'words.tracker: empty cleanup')
    final = all(rows[r] == (AL.target_final(r - V) if V <= r < 2 * V else AL.own_symbol(r)) for r in live)
    return dict(pre, final_identity=final, buffers_zero_after=all(not rows[b + n] for b in restored),
                live=len(live), buffers=len(restored), cleanup_items=len(w['cleanup']))


def tracker_check(check):
    need(check['targets_final'] and check['restored_own'] and check['buffers_zero'],
         'words.tracker: pre-cleanup state %r' % dict((k, check[k]) for k in ('targets_final', 'restored_own',
                                                                               'buffers_zero')))
    need(check['final_identity'] and check['buffers_zero_after'], 'words.tracker: final identity after cleanup')


def word_pipeline(w, declared, expect):
    P = AL.parse_word(w)
    warps = WC.check_all_warps(P)
    fr = CW.frame_recount(P)
    c = counts(P, w)
    check_counts(c, expect)
    check_report(P, fr)
    if declared is not None:
        check_declared(fr, declared)
    fwd = AL.replay(P, False)
    dual = AL.replay(P, True)
    check = track(w)
    tracker_check(check)
    cl = check_cleanup(w)
    bf = check_buffers(w, P)
    rec = dict(counts=c, profile=AL.hist(fr['paid']), inventory=AL.hist(fr['inventory']), mass=fr['mass'],
               helper_widths_sha256=AL.sha(fr['helper_widths']), warp_records=len(warps),
               centre_copy_children=sorted(sum(1 for d in c_['children']) for c_ in fr['copy_paths']),
               replay_forward=fwd, replay_dual=dual, tracker=check, cleanup=cl, buffers=bf,
               independent_inputs=fwd['independent_inputs'])
    return rec, P, fr
