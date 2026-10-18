# SPDX-License-Identifier: Apache-2.0
"""Scope A: the two changed T74 local words of PR #2751 (inputs/WORD-{base,extra}.json.gz at 4cfbb0cc).

word_pipeline runs, in this order, on one word (each step raises with its own rule id):
  parse (vendored parser + validated initial corrections) -> warp algebra of every B record (wc.warp) -> literal
  frame recount incl. the A-phase warp algebra (wc.frame, wc.warp) -> words.counts -> words.report_fields ->
  words.providers -> words.registers -> words.cut_census -> words.centres -> words.lifted -> words.profile_claim ->
  forward replay -> dual replay (wc.replay, stage recorded) -> words.cleanup -> words.pairs.gates -> words.tracker ->
  words.lenders.* -> words.pairs.*.
The claim checks compare with `spec`; a key absent from spec is recorded, not asserted (the positive controls on the
PR2733 and PR2696 words give only what their own CLAIM.json states).  Lender and pair checks always run.

Claims of PR2751 checked here (README 'Construction and cost', PROOF.md, inputs/PROVIDERS.json, the words' report):
local profile {1:2366,2:646,3:297,4:120,5:26,8:8}; 415 helpers and 72 private buffers; all eight centre children rank
eight; lifted targets 14,21,37,41,43,47,52,78,99,104,106,110 at frame [45], none read by a cut gate; the twelve
(removed helper, recovered source, partner) assignments with the pair restorations x += y/2; y -= x for 33/49,
55/101, 74/83, 85/98.  Audit expectations (not PR statements, derived from the inherited cut section and word shape):
176 unframed cut gates writing 88 targets, 65 warp records, 24 A-prelude warp items, 36 initial corrections, 639
independent inputs, widths {4:26,5:9,7:62,8:78,9:240} (= the word's own report) and local mass 5223.
"""
from collections import Counter

import audit_lib as AL
import check_words as CW
import words_check as WC
from audit_common import AuditFail, need

V = AL.V
TWELVE = (33, 55, 74, 85, 49, 83, 98, 101, 68, 80, 88, 31)
PAIRS = ((33, 49), (55, 101), (74, 83), (85, 98))
SPEC_2751 = dict(
    counts=dict(warps=65, a_warps=24, corrections=36),
    profile={1: 2366, 2: 646, 3: 297, 4: 120, 5: 26, 8: 8},
    widths={4: 26, 5: 9, 7: 62, 8: 78, 9: 240}, helpers=415, buffers=72, live=639, mass=5223,
    census=dict(cut_gates=176, targets_written=88, lifted_written=[]),
    centres_all_rank8=True,
    lifted=[14, 21, 37, 41, 43, 47, 52, 78, 99, 104, 106, 110], lifted_frame=[45])
CLAIM_KEYS = ('counts', 'profile', 'widths', 'helpers', 'buffers', 'live', 'mass', 'census', 'centres_all_rank8', 'lifted')


# ------------------------------------------------------------------------------------------- tracker ---
def track(w, watch_B=()):
    """One exact forward pass of the own tracker through restore and cleanup.  Returns (handoffs, gate_rows, check):
    handoffs = the lender row immediately before every A-phase and B-phase warp; gate_rows[j] = rows of B[j]'s
    registers before and after B[j] for j in watch_B; check = the pre-cleanup and final conditions of the
    vendored forward replay, evaluated on the tracker's rows (rule words.tracker)."""
    rows = AL.init_rows(w)
    n = AL.nregs(w)
    removed = set(w['removed'])
    restored = set(int(k) for k in w['helper_final'])
    live = [r for r in range(n) if r not in removed]
    watch_B = set(watch_B)
    handoffs, gate_rows, pre = [], {}, None
    for sec, i, g in AL.events(w, cleanup=True):
        if sec == 'cleanup' and pre is None:
            pre = dict(targets_final=all(rows[V + t] == AL.target_final(t) for t in range(V)),
                       restored_own=all(rows[r] == AL.own_symbol(r) for r in restored),
                       buffers_zero=all(not rows[b + n] for b in restored),
                       rows_with_operator_words=sum(1 for r in live if any(wd for _, wd in rows[r])))
        if g[0] == 'warp' and sec in ('A', 'Bwarp'):
            handoffs.append(dict(section='A' if sec == 'A' else 'B', index=i, lender=g[1], op=g[2],
                                 own=rows[g[1]] == AL.own_symbol(g[1]), row=AL.fmt(rows[g[1]])))
        if sec == 'B' and i in watch_B:
            regs = (g[1], g[2]) if g[0] == 'add' else (g[1],)
            before = dict((r, dict(rows[r])) for r in regs)
            AL.apply(rows, g)
            gate_rows[i] = dict(before=before, after=dict((r, dict(rows[r])) for r in regs))
            continue
        AL.apply(rows, g)
    need(pre is not None, 'words.tracker: empty cleanup')
    final = all(rows[r] == (AL.target_final(r - V) if V <= r < 2 * V else AL.own_symbol(r)) for r in live)
    check = dict(pre, final_identity=final, buffers_zero_after=all(not rows[b + n] for b in restored),
                 live=len(live), buffers=len(restored), cleanup_items=len(w['cleanup']))
    return handoffs, gate_rows, check


def tracker_check(check):
    need(check['targets_final'] and check['restored_own'] and check['buffers_zero'],
         'words.tracker: pre-cleanup state %r' % dict((k, check[k]) for k in ('targets_final', 'restored_own',
                                                                               'buffers_zero')))
    need(check['final_identity'] and check['buffers_zero_after'], 'words.tracker: final identity after cleanup')


# ---------------------------------------------------------------------------------------- claim checks ---
def sections(fr):
    """Paid children per section of the recount (A, B, post = restore, end, pre) plus the cut COPY children."""
    sec = {}
    for r, lst in fr['climbs'].items():
        for where, d in lst:
            key = where.split('[')[0]
            sec.setdefault(key, Counter())[d] += 1
    for c in fr['copy_paths']:
        for d in c['children']:
            sec.setdefault('cut', Counter())[d] += 1
    return dict((k, AL.hist(v)) for k, v in sorted(sec.items()))


def cut_census(w, P):
    """Every cut item is an unframed add target += c * centre; returns the census (targets as offsets)."""
    gates = w['cut']
    centres = set(P['centers'])
    for i, g in enumerate(gates):
        need(isinstance(g, list) and len(g) == 6 and g[0] == 'add' and g[5] is None,
             'words.cut_census: cut item %d is not an unframed add' % i)
        need(V <= g[1] < 2 * V and g[2] in centres, 'words.cut_census: cut item %d is not target += c*centre' % i)
    written = sorted(set(g[1] - V for g in gates))
    lifted = set(P['target_levels'])
    per_centre = dict((str(q), sorted(g[1] - V for g in gates if g[2] == q)) for q in P['centers'])
    return dict(cut_gates=len(gates), targets_written=len(written), target_offsets_written_sha256=AL.sha(written),
                lifted_written=sorted(lifted & set(written)),
                untouched_targets=sorted(set(range(V)) - set(written)),
                coefficients=dict((k, v) for k, v in sorted(Counter('%d/%d' % (g[3], g[4]) for g in gates).items())),
                gates_per_centre=dict((q, len(t)) for q, t in per_centre.items()),
                per_centre_sha256=AL.sha(per_centre))


def check_census(census, spec):
    if 'census' in spec:
        want = spec['census']
        got = dict((k, census[k]) for k in want)
        need(got == want, 'words.cut_census: %r != %r' % (got, want))


def centre_paths(P, fr):
    return [dict(centre=c['centre'], dim=c['dim'], children=c['children'], served_dims=c['served_dims'])
            for c in fr['copy_paths']]


def check_centres(paths, spec):
    if spec.get('centres_all_rank8'):
        bad = [[p['centre'], p['dim'], p['children']] for p in paths if p['dim'] != 8 or p['children'] != [8]]
        need(len(paths) == 8 and not bad, 'words.centres: centre COPY paths not all [8] at rank 8: %r' % bad)


def lift_climbs(P, fr, prelude_events):
    out = {}
    for t in sorted(P['target_levels']):
        lst = fr['climbs'].get(V + t, [])
        first = lst[0] if lst else None
        ok = (first is not None and first[0].startswith('A[') and int(first[0][2:-1]) < prelude_events
              and first[1] == 1)
        out[str(t)] = dict(first_climb=list(first) if first else None, rank1_prelude_lift=ok)
    return out


def check_lifted(P, lifts, spec):
    if 'lifted' in spec:
        got = sorted(P['target_levels'])
        need(got == spec['lifted'], 'words.lifted: lifted targets %r != %r' % (got, spec['lifted']))
        frame = WC.span(spec['lifted_frame'])
        bad = [t for t, F in P['target_levels'].items() if F != frame]
        need(not bad, 'words.lifted: targets %r not at frame %r' % (sorted(bad), spec['lifted_frame']))
        need(all(v['rank1_prelude_lift'] for v in lifts.values()), 'words.lifted: a lift is not a rank-1 prelude climb')


# ---------------------------------------------------------------------------------- lenders and pairs ---
def check_lenders(w, handoffs):
    """All twelve aliased lenders: exactly one A-prelude K_op (k > 0) and its inverse, exactly one B handoff, the
    same operator at both places, and the lender row is exactly X_r immediately before each K_op."""
    out = {}
    b_op = dict((rec[1], k) for k, rec in enumerate(w['warps'], 1))
    for r in TWELVE:
        a_pos = [h for h in handoffs if h['section'] == 'A' and h['lender'] == r and h['op'] > 0]
        a_neg = [h for h in handoffs if h['section'] == 'A' and h['lender'] == r and h['op'] < 0]
        b = [h for h in handoffs if h['section'] == 'B' and h['lender'] == r]
        need(len(a_pos) == 1 and len(a_neg) == 1 and len(b) == 1,
             'words.lenders.count: lender %d has %d A K_op, %d A inverse, %d B handoffs' % (r, len(a_pos), len(a_neg),
                                                                                          len(b)))
        need(a_pos[0]['op'] == b[0]['op'] == b_op[r] and a_neg[0]['op'] == -b_op[r],
             'words.lenders.ops: lender %d uses A op %d, B op %d' % (r, a_pos[0]['op'], b[0]['op']))
        need(a_pos[0]['own'], 'words.lenders.A: lender %d holds %s before its A-prelude K%d' % (r, a_pos[0]['row'],
                                                                                              a_pos[0]['op']))
        need(b[0]['own'], 'words.lenders.B: lender %d holds %s before its B handoff K%d' % (r, b[0]['row'], b[0]['op']))
        out[str(r)] = dict(op=b[0]['op'], A_index=a_pos[0]['index'], A_inverse_index=a_neg[0]['index'],
                           B_position=w['warps'][b[0]['op'] - 1][0], row_A=a_pos[0]['row'], row_B=b[0]['row'])
    own_b = sorted(h['op'] for h in handoffs if h['section'] == 'B' and h['own'])
    return dict(lenders=out, B_warps=sum(1 for h in handoffs if h['section'] == 'B'), B_warps_own_input_ops=own_b)


def pair_gates(w):
    """For each pair (x, y): the unique B add x += c y and the unique B add y += c' x (rule words.pairs.gates); their
    coefficients are then fixed by check_pairs' exact pre- and post-states (1/2 and -1)."""
    idx = {}
    for x, y in PAIRS:
        jx = [j for j, g in enumerate(w['B']) if g[0] == 'add' and g[1] == x and g[2] == y]
        jy = [j for j, g in enumerate(w['B']) if g[0] == 'add' and g[1] == y and g[2] == x]
        need(len(jx) == 1 and len(jy) == 1, 'words.pairs.gates: pair %d/%d gates %r %r' % (x, y, jx, jy))
        idx[(x, y)] = (jx[0], jy[0])
    return idx


def touches(g, r):
    return r in ((g[1], g[2]) if g[0] == 'add' else (g[1],))


def check_pairs(w, P, fr, idx, gate_rows):
    """The four pair recoveries: adjacent gates x += y/2; y -= x (no warp between them), exact pre-states
    x = (X_x - X_y)/2 and y = X_x + X_y, both originals restored, neither register touched by any B item between the
    recovery and its own handoff (which follows the recovery), and no paid climb at either gate (frame-recount labels
    from the raw warp positions, label formula checked on every B gate)."""
    labels = CW.label_formula(P, w['warps'])
    hand = dict((rec[1], rec[0]) for rec in w['warps'])
    half = AL.ONE / 2
    out = []
    for x, y in PAIRS:
        jx, jy = idx[(x, y)]
        need(jy == jx + 1 and not any(rec[0] == jy for rec in w['warps']),
             'words.pairs.adjacent: pair %d/%d gates at B[%d], B[%d]' % (x, y, jx, jy))
        bx, by = gate_rows[jx]['before'][x], gate_rows[jx]['before'][y]
        need(bx == {(x, ()): half, (y, ()): -half} and by == {(x, ()): AL.ONE, (y, ()): AL.ONE},
             'words.pairs.prestate: pair %d/%d before recovery: %s | %s' % (x, y, AL.fmt(bx), AL.fmt(by)))
        ax, ay = gate_rows[jy]['after'][x], gate_rows[jy]['after'][y]
        need(ax == AL.own_symbol(x) and ay == AL.own_symbol(y),
             'words.pairs.restored: pair %d/%d after recovery: %s | %s' % (x, y, AL.fmt(ax), AL.fmt(ay)))
        for r in (x, y):
            p = hand[r]
            between = [k for k in range(jy + 1, min(p, len(w['B']))) if touches(w['B'][k], r)]
            need(jy < p and not between, 'words.pairs.untouched: register %d touched at B%r between its recovery B[%d] '
                 'and its handoff before B[%d]' % (r, between[:4], jy, p))
        paid = []
        for j in (jx, jy):
            lab = CW.inserted_gate_label(j, w['warps'])
            paid += [[lab, r, d] for r, lst in sorted(fr['climbs'].items()) for wh, d in lst if wh == lab]
        need(not paid, 'words.pairs.paid_climbs: recovery gates of %d/%d pay climbs %r' % (x, y, paid[:4]))
        out.append(dict(pair=[x, y], gates=[jx, jy], gate_items=[w['B'][jx][:5], w['B'][jy][:5]],
                        gate_frame=list(w['B'][jx][-1]),
                        gate_frame_dim=len(WC.span(w['B'][jx][-1])), before=[AL.fmt(bx), AL.fmt(by)],
                        after=[AL.fmt(ax), AL.fmt(ay)], handoff_positions=[hand[x], hand[y]],
                        labels=[CW.inserted_gate_label(j, w['warps']) for j in (jx, jy)], paid_climbs=len(paid)))
    return dict(pairs=out, label_formula=labels)


# ------------------------------------------------------------------------------------------ pipeline ---
def word_pipeline(w, spec, provider=None, stop_after=None):
    """The main per-word check (see the module docstring for the order).  provider: this word's PROVIDERS.json entry
    or None.  Returns (record, P, fr)."""
    P = AL.parse_word(w)
    warps = WC.check_all_warps(P)
    fr = CW.frame_recount(P)
    counts = dict(warps=len(warps), a_warps=len(fr['a_warps']), corrections=len(P['corrections']))
    if 'counts' in spec:
        need(counts == spec['counts'], 'words.counts: %r != %r' % (counts, spec['counts']))
    need(fr['paid'] == P['claimed_profile'] and fr['inventory'] == P['claimed_inventory'],
         'words.report_fields: report %r %r != recount %r %r' % (P['claimed_profile'], P['claimed_inventory'],
                                                                 fr['paid'], fr['inventory']))
    if provider is not None:
        need(AL.intkeys(provider['actual_paid_profile']) == fr['paid'] and provider['widths'] == fr['helper_widths'],
             'words.providers: PROVIDERS entry != recount (profile or ordered widths)')
    copy_total = sum(sum(c['children']) for c in fr['copy_paths'])
    regs = dict(widths=fr['inventory'], helpers=fr['helpers'], buffers=len(P['buffers']), live=len(P['live']),
                mass=fr['mass'])
    need(fr['mass'] == sum(fr['helper_widths']) + 2 * V * 8 + copy_total, 'words.registers: mass identity')
    for k in ('widths', 'helpers', 'buffers', 'live', 'mass'):
        if k in spec:
            need(regs[k] == spec[k], 'words.registers: %s %r != %r' % (k, regs[k], spec[k]))
    census = cut_census(w, P)
    check_census(census, spec)
    paths = centre_paths(P, fr)
    check_centres(paths, spec)
    lifts = lift_climbs(P, fr, w['prelude_events'])
    check_lifted(P, lifts, spec)
    if 'profile' in spec:
        need(fr['paid'] == spec['profile'], 'words.profile_claim: recount %r != claim %r' % (fr['paid'], spec['profile']))
    if stop_after == 'claims':
        return None, P, fr
    fwd = AL.replay(P, False)
    dual = AL.replay(P, True)
    mine = AL.rederive_cleanup(w)
    full = WC.span(AL.FULL_LIST)
    at_full = sum(1 for g in w['cleanup'] if WC.span(g[-1]) == full)
    need([g[:-1] for g in mine] == [g[:-1] for g in w['cleanup']] and at_full == len(w['cleanup']),
         'words.cleanup: shipped cleanup != own inverse-reverse re-derivation (or not at FULL)')
    idx = pair_gates(w)
    handoffs, gate_rows, tcheck = track(w, [j for v in idx.values() for j in v])
    tracker_check(tcheck)
    lenders = check_lenders(w, handoffs)
    pairs = check_pairs(w, P, fr, idx, gate_rows)
    sources = sorted(set(s for _, s, _, _ in P['corrections']))
    rec = dict(
        independent_inputs=len(P['live']), counts=counts, profile=AL.hist(fr['paid']), sections=sections(fr),
        widths=AL.hist(fr['inventory']), helpers=fr['helpers'], buffers=len(P['buffers']), mass=fr['mass'],
        mass_identity='%d = %d helper widths + %d + %d + %d COPY' % (fr['mass'], sum(fr['helper_widths']), V * 8, V * 8,
                                                                     copy_total),
        helper_widths_sha256=AL.sha(fr['helper_widths']),
        warp_records_U_eq_E=sum(1 for a in warps if a['U_eq_E']),
        a_warp_plain_fourier_distances=sorted(set(a['plain_fourier_distance'] for a in fr['a_warps'])),
        correction_sources=sources, correction_source_start_dims=[len(P['start'][s]) for s in sources],
        correction_ops=[list(x) for x in sorted(set(word for _, _, _, word in P['corrections']))],
        centre_paths=paths, lifted_targets=sorted(P['target_levels']),
        lifted_frames=sorted(set(AL.canon(sorted(F)) for F in P['target_levels'].values())), lift_climbs=lifts,
        census=census, replay_forward=fwd, replay_dual=dual,
        cleanup=dict(items=len(w['cleanup']), items_at_full=at_full, own_inverse_reverse_items=len(mine),
                     literal_equal_own_inverse_reverse=[g[:-1] for g in mine] == [g[:-1] for g in w['cleanup']]),
        tracker=tcheck, lenders=lenders, pairs=pairs)
    rec['claims_checked'] = sorted(k for k in CLAIM_KEYS if k in spec)
    rec['spec_sha256'] = AL.sha(spec)
    return rec, P, fr


def check_wiring(recs):
    """Wiring self-check (rule words.wiring): the PR2751 word pipeline ran on both providers with the identical
    full claim spec SPEC_2751 (every claim key checked, same spec fingerprint)."""
    want = (sorted(CLAIM_KEYS), AL.sha(SPEC_2751))
    got = dict((tag, (r['claims_checked'], r['spec_sha256'])) for tag, r in sorted(recs.items()))
    need(sorted(got) == ['base', 'extra'] and all(v == want for v in got.values()),
         'words.wiring: providers ran different word specs %r' % dict((t, v[0]) for t, v in got.items() if v != want))
    AL.ran('words.wiring')
    return dict(providers=sorted(got), claims_checked=want[0], spec_sha256=want[1])
