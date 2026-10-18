# SPDX-License-Identifier: Apache-2.0
"""Declared gate rewrites on the PR2917 (mason-hale) words: nine exactness-preserving retimes in four classes.

Warp-lender carrier entries and timing rewrites by Jeremy Kothe (jeremykothe2), with AI assistance, on mason-hale's PR2917 nine paired
extractions, Jeremy Diviney's PR2908 construction and the inherited PR2894/PR2857/PR2833 words. This module is pure.
Rewrite classes: R-retime (carrier entry of a restored helper moved earlier and its later duplicate deleted), A3779-cut-start-read
(one read moved to the start of the cut), PM-carrier-lender-entry (PreloadMove carrier entries taken from lender registers),
B-carrier-retime (a PreloadMove carrier raise in phase B replaced by the same lender gate at its unraised frame in phase A; the B-position of every
phase warp is shifted by the number of deleted B gates before it).
Every rewrite is a set of literal edits, addressed by index in the SOURCE word and checked against the exact old gates; edits of
different rewrites must not overlap.  Compensation, cut, helper endpoints, buffers and the prelude are unchanged (B and the warp positions only as stated);
paid profile, width inventory and cleanup are re-derived by the inherited frame rules.
"""
import copy
import preload_move as pm

SECTIONS = ('A', 'B', 'restore')
ALLOWED = {'A', 'B', 'restore', 'warps', 'report', 'cleanup'}
CLASSES = ('R-retime', 'A3779-cut-start-read', 'PM-carrier-lender-entry', 'B-carrier-retime')
PROFILE = {'1': 2407, '2': 641, '3': 281, '4': 111, '5': 26, '8': 8}
INVENTORY = {'4': 26, '5': 2, '7': 62, '8': 96, '9': 222}


def apply(word, rewrites, check_declared=True):
    pm.require(tuple(sorted({r['cls'] for r in rewrites})) == tuple(sorted(CLASSES)) or not check_declared, 'all three declared rewrite classes')
    x = copy.deepcopy(word)
    taken = {s: [] for s in SECTIONS}
    edits = []
    for rw in rewrites:
        pm.require(rw['cls'] in CLASSES, 'declared class')
        for e in rw['edits']:
            s, a, b = e['section'], e['start'], e['stop']
            pm.require(s in SECTIONS and 0 <= a <= b <= len(word[s]), 'edit address')
            pm.require(a >= word['prelude_events'] or s != 'A', 'no prelude edit')
            pm.require(word[s][a:b] == e['old'], ('old gates differ from the declared preimage', rw['id'], s, a))
            pm.require(e['old'] != e['new'], 'nonvacuous edit')
            for (c, d) in taken[s]:
                pm.require(b < c or d < a, ('overlapping or adjacent rewrites', rw['id'], s, a))
            taken[s].append((a, b))
            edits.append((s, a, b, e['new']))
    for s, a, b, new in sorted(edits, key=lambda t: (t[0], -t[1], -t[2])):
        x[s][a:b] = copy.deepcopy(new)
    # phase warps address B positions: shift by the net length change of the B edits entirely before them
    bedits = [(a, b, len(new) - (b - a)) for s, a, b, new in edits if s == 'B']
    for rec in x['warps']:
        p = rec[0]
        pm.require(not any(a < p < b for a, b, _ in bedits), 'no warp inside an edited B span')
        rec[0] = p + sum(d for a, b, d in bedits if b <= p and a < p)
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    z = copy.deepcopy(x)
    z['A'] = z['A'][z['prelude_events']:]
    x['cleanup'] = pm.derive_cleanup(z, pm.restored_of(word))
    pm.require({k for k in word if word[k] != x[k]} <= ALLOWED, 'only A, restore, report and cleanup change')
    for k in ('cut', 'compensation', 'helper_final', 'start_extra', 'removed', 'prelude_events'):
        pm.require(x[k] == word[k], ('unchanged section', k))
    if check_declared:
        pm.require(profile == PROFILE and inventory == INVENTORY, ('declared paid profile and inventory', profile, inventory))
    ledger = dict(rewrites=[r['id'] for r in rewrites], local_profile=profile, width_inventory=inventory,
                  edits=len(edits), A_len=(len(word['A']), len(x['A'])), restore_len=(len(word['restore']), len(x['restore'])))
    return x, ledger
