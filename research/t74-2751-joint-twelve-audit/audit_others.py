# SPDX-License-Identifier: Apache-2.0
"""Scope E (optional): PR #2766 (head e6df920c, research/complex-routing-leaf-fusion) reuses PR2751's words' recovery
with PR2733-head's frame refit and PR2751's fill, order and dispatch (vendored byte-identically); PR #2767 (head
e8b771ba, research/gmx-t74-borrow43-handoff) reaches eight rank-eight centres by another route (its four partner
corrections are inline warps at the start of B) with its own fill.  Checked here (rule ids others.*): the four
words' literal frame recounts equal their report fields (others.report_fields; #2767's eight inline B warps are
parsed by parse_inline, their chart algebra checked with check_words.a_warp_algebra); #2766's vendored fill, order
and dispatch are byte-identical to PR2751's (others.inputs); both complete profiles are priced by the same two
implementations as scope D and are identical (others.identical) and each equals its own declared profile
(#2766 CLAIM.json, #2767 new/PROFILE.json; others.declared).  Word replays, endpoints and kappas of #2766/#2767 are
not checked here.  Computed observation (others.pr2767_top_profile, not a defect): #2767's top-level
research/gmx-t74-borrow43-handoff/PROFILE.json equals PR2733@2761b52b's complete profile as computed here (scope D's
PR2733 pricing record, two implementations compared), while its new/PROFILE.json equals the recomputed (improved) one;
a wiring self-check (others.pr2767_comparator) requires the comparator to be that computed object, not a #2767 file.

Scope F (data only, no replay): the words of the later PRs #2802 (17b2ee6e), #2818 (175822ae), #2824 (f1826afe),
#2827 (4dc1286a) and #2833 (e9307b48) are parsed as JSON from the bytes read (downstream_word: git blob id and sha256
computed from those bytes and required to equal the pin, downstream.input) and compared structurally with PR2751's word
of the same provider (downstream_structure, rule ids downstream.*): the word is not PR2751's (72 warp records against
PR2751's 65, downstream.distinct); the four pair recoveries x += y/2; y -= x for 33/49, 55/101, 74/83, 85/98 are
present as unique adjacent gate pairs (downstream.pairs) with frames identical to PR2751's (positions may differ;
downstream.pair_frames); the A-prelude charts of ops 47-50 (lenders 33, 55, 74, 85) send PR2751's ports to line 45,
open and close exactly as in PR2751, and the B records of ops 47-50 equal PR2751's (downstream.charts); the twelve
lifted targets and their frames equal PR2751's (downstream.lifted).
"""
import gzip
import json
from collections import defaultdict

import audit_common as AC
import audit_lib as AL
import audit_pricing as AP
import check_words as CW
import words_check as WC
from audit_common import need


def parse_inline(w):
    """A word whose B list carries warp items ['warp', reg, k, U, E]: those items are removed before the vendored
    parser (warp record positions re-indexed), and put back into P['B_items'] at their places afterwards (the frame
    recount treats them like record warps: frame must equal U, moves to E, no charge).  Returns (P, inline items)."""
    B = w['B']
    gates_before = []
    n = 0
    for g in B:
        gates_before.append(n)
        n += g[0] != 'warp'
    gates_before.append(n)
    w2 = dict(w)
    w2['B'] = [g for g in B if g[0] != 'warp']
    w2['warps'] = [[gates_before[rec[0]]] + list(rec[1:]) for rec in w['warps']]
    P = AL.parse_word(w2)
    by_pos = defaultdict(list)
    for wr in P['warps']:
        by_pos[w['warps'][wr['op'] - 1][0]].append(wr)
    items, inline, gi = [], [], 0
    for j in range(len(B) + 1):
        for wr in by_pos.get(j, []):
            items.append(('warp', wr['lender'], wr['op'], wr['U'], wr['E']))
        if j < len(B):
            g = B[j]
            if g[0] == 'warp':
                need(len(g) == 5 and WC.is_int(g[1]) and WC.is_int(g[2]) and 1 <= abs(g[2]) <= len(P['warps']),
                     'others.report_fields: inline B warp %d' % j)
                it = ('warp', g[1], g[2], WC.span(g[3]), WC.span(g[4]), list(g[3]), list(g[4]))
                items.append(it[:5])
                inline.append(it)
            else:
                items.append(P['sections']['B'][gi])
                gi += 1
    need(gi == len(P['sections']['B']), 'others.report_fields: B re-assembly')
    P['B_items'] = items
    return P, inline


def recount(w):
    """Warp algebra (records and inline items) and the literal frame recount; equal to the word's report fields."""
    P, inline = parse_inline(w)
    WC.check_all_warps(P)
    for it in inline:
        CW.a_warp_algebra(P, it)
    fr = CW.frame_recount(P)
    need(fr['paid'] == P['claimed_profile'] and fr['inventory'] == P['claimed_inventory'],
         'others.report_fields: report != recount')
    return fr, len(inline)


def check_inputs(raw66, raw51):
    bad = sorted(k for k in raw66 if raw66[k] != raw51[k])
    need(not bad, 'others.inputs: #2766 vendored %r differ from PR2751\'s' % bad)


def others_checks(p66, p67, claim66, profile67):
    prof66, prof67 = p66['own']['profile'], p67['own']['profile']
    need(prof66 == prof67, 'others.identical: #2766 %r != #2767 %r' % (prof66, prof67))
    need(prof66 == AL.intkeys(claim66['profile']) and prof67 == AL.intkeys(profile67),
         'others.declared: complete profiles != declared (#2766 CLAIM.json, #2767 new/PROFILE.json)')
    return dict(pr2766=AP.summary(p66), pr2767=AP.summary(p67), identical=prof66 == prof67,
                pr2766_equals_declared=prof66 == AL.intkeys(claim66['profile']),
                pr2767_equals_declared=prof67 == AL.intkeys(profile67))


def check_pr2767_profiles(top67, new67, prof67, comparator, priced33, commit33):
    """others.pr2767_top_profile: #2767's top-level PROFILE.json equals the comparator, PR2733@commit33's complete
    profile as computed here; its new/PROFILE.json equals the recomputed #2767 complete profile prof67 (as
    others.declared).  Wiring self-check first (others.pr2767_comparator): the comparator is the very profile object of
    priced33, scope D's PR2733 pricing record (int ranks, two-implementation comparison recorded), it is neither of
    #2767's PROFILE.json objects, and it differs from prof67.  The record carries the comparator's histogram and
    source commit and the computed equalities."""
    own = priced33.get('own') if isinstance(priced33, dict) else None
    two = priced33.get('two_impl') if isinstance(priced33, dict) else None
    need(isinstance(own, dict) and comparator is own.get('profile') and comparator is not top67 and
         comparator is not new67 and isinstance(comparator, dict) and comparator and
         all(type(k) is int for k in comparator) and isinstance(two, dict) and two.get('profile_equal') is True and
         two.get('roles') == own.get('roles') and comparator != prof67,
         'others.pr2767_comparator: the comparator is not the computed PR2733@%s complete profile (pricing record)'
         % str(commit33)[:8])
    top_equal, new_equal = AL.intkeys(top67) == comparator, AL.intkeys(new67) == prof67
    need(top_equal, 'others.pr2767_top_profile: top-level PROFILE.json %r != PR2733@%s complete profile %r'
         % (top67, str(commit33)[:8], AL.hist(comparator)))
    need(new_equal, 'others.pr2767_top_profile: new/PROFILE.json != recomputed profile')
    AL.ran('others.pr2767_top_profile')
    return dict(top_level_PROFILE_equals_pr2733_2761b52b_complete=top_equal, new_PROFILE_equals_recomputed=new_equal,
                top_level_PROFILE=AL.hist(AL.intkeys(top67)), new_PROFILE=AL.hist(AL.intkeys(new67)),
                comparator=dict(profile=AL.hist(comparator), commit=commit33, roles=own['roles'],
                                source='PR2733 FILL.json.gz at this commit priced here by check_rows and fill_check80 '
                                       '(pricing.pr2733; equal to its CLAIM.json global_profile)'),
                note='computed observation, not a defect: the top-level PROFILE.json carries PR2733@2761b52b\'s '
                     'complete profile and new/PROFILE.json the improved one')


# ---------------------------------------------------------------------------------- scope F: downstream ---
D_PAIRS = ((33, 49), (55, 101), (74, 83), (85, 98))
D_PSRC = (33, 55, 74, 85)
D_OPS = (47, 48, 49, 50)
D_WARP_RECORDS = (72, 65)     # warp records of every later word and of PR2751's word (pinned data; downstream.distinct)


def downstream_word(raw, pin):
    """downstream.input: the git blob id and sha256 computed from the bytes actually parsed equal the pin (blob,
    sha256); returns (the word parsed from those bytes, the computed identity)."""
    ident = dict(git_blob=AC.git_blob_id(raw), sha256=AC.sha256(raw), bytes=len(raw))
    need((ident['git_blob'], ident['sha256']) == tuple(pin), 'downstream.input: bytes parsed are git blob %s, sha256 '
         '%s, not the pin %r' % (ident['git_blob'], ident['sha256'][:12], tuple(pin)))
    AL.ran('downstream.input')
    return json.loads(gzip.decompress(raw).decode('utf-8')), ident


def pair_items(w, x, y):
    jx = [j for j, g in enumerate(w['B']) if g[0] == 'add' and g[1] == x and g[2] == y]
    jy = [j for j, g in enumerate(w['B']) if g[0] == 'add' and g[1] == y and g[2] == x]
    need(len(jx) == 1 and len(jy) == 1 and jy[0] == jx[0] + 1 and not any(rec[0] == jy[0] for rec in w['warps']),
         'downstream.pairs: pair %d/%d gates %r %r are not one adjacent pair' % (x, y, jx, jy))
    gx, gy = w['B'][jx[0]], w['B'][jy[0]]
    need(gx[:5] == ['add', x, y, 1, 2] and gy[:5] == ['add', y, x, -1, 1],
         'downstream.pairs: pair %d/%d is not x += y/2; y -= x (%r, %r)' % (x, y, gx[:5], gy[:5]))
    return jx[0], gx, gy


def prelude_chart(w, x):
    items = [g for g in w['A'][:w['prelude_events']] if g[0] == 'warp' and g[1] == x]
    return items


def downstream_structure(w, ref):
    """The scope-F checks of the module docstring for one later word w against PR2751's word ref of the same
    provider.  Returns the per-word record."""
    need(w is not ref and (len(w['warps']), len(ref['warps'])) == D_WARP_RECORDS,
         'downstream.distinct: the word checked has %d warp records and PR2751\'s %d, expected %r (is it PR2751\'s '
         'word?)' % (len(w['warps']), len(ref['warps']), D_WARP_RECORDS))
    pairs = []
    for x, y in D_PAIRS:
        j, gx, gy = pair_items(w, x, y)
        j0, rx, ry = pair_items(ref, x, y)
        need(gx[5] == rx[5] and gy[5] == ry[5], 'downstream.pair_frames: pair %d/%d frames %r %r != PR2751 %r %r'
             % (x, y, gx[5], gy[5], rx[5], ry[5]))
        pairs.append(dict(pair=[x, y], gates=[j, j + 1], pr2751_gates=[j0, j0 + 1], frame=list(gx[5])))
    charts = []
    for x, op in zip(D_PSRC, D_OPS):
        got, want = prelude_chart(w, x), prelude_chart(ref, x)
        need(len(want) == 2 and want[0][2] == op and want[0][4] == [45] and got == want,
             'downstream.charts: A-prelude chart of op %d (lender %d) %r != PR2751 %r' % (op, x, got, want))
        need(len(w['warps']) >= op and w['warps'][op - 1][1:] == ref['warps'][op - 1][1:],
             'downstream.charts: B record of op %d differs from PR2751\'s' % op)
        charts.append(dict(op=op, lender=x, port=list(got[0][3]), line=list(got[0][4]),
                           B_position=w['warps'][op - 1][0], pr2751_B_position=ref['warps'][op - 1][0]))
    need(w['target_levels'] == ref['target_levels'], 'downstream.lifted: lifted targets %r != PR2751 %r'
         % (sorted(w['target_levels'], key=int), sorted(ref['target_levels'], key=int)))
    AL.ran('downstream.structure')
    return dict(pairs=pairs, prelude_charts=charts, lifted_targets=sorted(int(k) for k in w['target_levels']),
                lifted_frames=sorted(set(AL.canon(F) for F in w['target_levels'].values())),
                B_items=len(w['B']), warp_records=len(w['warps']))


def check_downstream_coverage(downstream, prs):
    """downstream.coverage: every later PR of scope F was checked on both providers."""
    need(sorted(downstream) == sorted(str(p) for p in prs) == ['2802', '2818', '2824', '2827', '2833'] and
         all(sorted(r['words']) == ['base', 'extra'] for r in downstream.values()),
         'downstream.coverage: checked %r' % dict((k, sorted(r['words'])) for k, r in downstream.items()))
    AL.ran('downstream.coverage')
