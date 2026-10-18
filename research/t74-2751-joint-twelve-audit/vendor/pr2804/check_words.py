# SPDX-License-Identifier: Apache-2.0
"""Scope A: the two changed T74 local words of PR #2530 (evidence/eight-alias-{base,extra}.json.gz).

What is proved (in the lineage's free-operator, frame-climb model of the vendored words_check.py, PR2315):
  * endpoint: an exact replay over Q<free group on the warp letters> with all 646 live registers as independent
    (dirty) symbols and the 78 private buffers at zero gives Y_t += X_t with every other register restored and
    every buffer zero (forward), and X -= Y (dual, g^-T) with every buffer zero before and after cleanup, for both
    words (the orientation that ran is recorded with each replay's diagnostics);
  * warps: all 58 warp records and all 24 A-phase warp items pass the GF(2) and symplectic rank-zero checks
    (G invertible, K_G symplectic, fixes L_0 and L_FULL, maps L_U to L_E, Fourier rank 0, no double lender);
  * paid profile: the literal frame-chain recount gives profile {1:2369,2:632,3:320,4:118,5:26,7:8}, widths
    {4:33,5:9,7:62,8:78,9:240}, 422 helpers, local mass 5251, 8 centre COPY paths [7,1] and 16 line-[30] targets,
    equal to the claim (claims.profile_widths) and to the words' report fields (claims.report_fields); check_fill
    takes its local profiles from this recount;
  * diff against PR2462 (words read at ef34071f): 8 helpers removed, 32 echo reads deleted (4 per removed helper,
    all before its first write), exactly the nine README restorations inserted, the 50 old warp records unchanged
    (positions follow the B alignment) and 8 appended, the A prelude extended by 12 identity lifts and 8 blocks
    "warp K_op (port line -> [30]), 4 target adds, inverse warp" where op is the lender's own B handoff operator,
    everything else identical (base and extra carry the same edits);
  * the restorations: exact rows show every lender holds exactly X_r at its new handoff warp (forward orientation;
    the dual replay checks the whole word's final map and buffers only); the ALIASES partner column equals the
    source register of each lender's inserted restoration add; the nine inserted gates (their frame-recount labels
    re-derived from the raw warp positions, the label formula checked on every B gate including those that share a
    position with a warp, and required to be exactly those nine B items) cause zero paid climbs, recorded per gate
    with its frame dimension; each of the 16 lifted targets is charged one rank-1 climb in the prelude;
  * cleanup: PR2530's cleanup equals the own inverse-reverse re-derivation literally (4529 items, all at FULL), and
    the word with the re-derived cleanup replays identically (part of the main check, not a positive control);
  * side checks: the only new non-unit scalar kind is the B-phase scale 1/2 (all scalars dyadic, scales dyadic
    units, enforced by the parser); largest free-algebra row L1 and denominator unchanged from PR2462 (diagnostic
    only); 724 touched registers = 646 live + 78 buffers, no removed register touched; eight-providers.json widths
    and paid profiles equal the recount;
  * negative controls (per word; see word_controls), each asserting the check that rejects it and, for the
    replays, which orientation rejected and whether before or after cleanup: 9 word mutations through full_check;
    each of the 9 inserted gates mutated, through full_check (rejected by the forward replay before cleanup),
    through the handoff rows, and with the own re-derived cleanup through full_check with the dual replay only
    (rejected at the final map after that cleanup, as are 3 word endpoint mutants); a dual-only cleanup mutant
    (a forward no-op that leaves a buffer non-zero in the dual orientation), accepted by the forward replay and
    rejected by full_check through the dual replay; a climb-split mutant (one rank-2 climb of two registers each
    made 1 + 1, every charge still equal to its width, report unchanged) rejected by claims.profile_widths, and the
    word with its report.local_profile altered rejected by claims.report_fields; 3 replay-only forward controls for
    mutants the warp/frame checks stop first; one cleanup coefficient negated; one PR2462 echo read moved past its
    helper's first write; a wrong ALIASES partner.
    Plumbing (checker non-vacuity, not a word property): a rank-1 paid climb injected into the recount at each of
    the nine inserted gates in turn is rejected by the zero-climb check.  Positive control: the same checker
    reproduces PR2462's own claims on PR2462's words.
Scope limits: warp letters are abstract.  The physical identity of K_op shared by the A prelude and the B handoff
(exact Clifford phases, Gaussian monomial lifts) and native precision/prefix bits are NOT checked here.
"""
import copy
import json
from collections import Counter, defaultdict
from fractions import Fraction

import words_check as WC
from audit_common import AuditFail, attempt, need, positive

V = 112
CLAIM_2530 = dict(profile={1: 2369, 2: 632, 3: 320, 4: 118, 5: 26, 7: 8}, widths={4: 33, 5: 9, 7: 62, 8: 78, 9: 240},
                  live=646, helpers=422, warps=58, a_warps=24, mass=5251, buffers=78)
CLAIM_2462 = dict(profile={1: 2363, 2: 632, 3: 326, 4: 120, 5: 34, 7: 4, 8: 4}, widths={4: 33, 5: 9, 7: 62, 8: 86, 9: 240},
                  live=654, helpers=430, warps=50, a_warps=8, mass=5315, buffers=78)
# (PR2462 helper removed by PR2530, the source register that takes over its role, that source's joint partner)
ALIASES = ((656, 49, 33), (657, 83, 74), (658, 98, 85), (660, 101, 55), (632, 68, 4), (648, 80, 88), (649, 88, 80),
           (633, 31, 12))
LIFTED_2530 = [23, 29, 32, 34, 35, 45, 48, 50, 59, 73, 75, 82, 84, 86, 93, 108]
LIFTED_2462 = [23, 34, 50, 108]
# The nine inserted B gates described in the PR README, in word order (frames recorded, not pinned).
RESTORATIONS = [['add', 88, 80, 1, 2], ['add', 80, 88, -1, 1], ['scale', 68, 1, 2], ['add', 68, 4, -1, 1],
                ['add', 31, 12, 1, 2], ['add', 49, 33, -1, 1], ['add', 101, 55, -1, 1], ['add', 83, 74, -1, 1],
                ['add', 98, 85, -1, 1]]


# ------------------------------------------------------------------------------------------------ parsing ---
def parse_ext(w):
    """words_check.parse_borrow, extended to A-phase warp items ['warp', reg, k, U, E] (k<0 applies G^-1)."""
    w2 = copy.deepcopy(w)
    a_items = w2['A']
    w2['A'] = [g for g in a_items if g[0] != 'warp']
    P = WC.parse_borrow(w2)

    def frame_lit(F):
        WC.need(isinstance(F, list) and all(WC.is_int(x) and 0 < x < (1 << P['h']) for x in F), 'format', 'bad frame')
        return WC.span(F)

    A = []
    for i, g in enumerate(a_items):
        if g[0] == 'warp':
            WC.need(len(g) == 5 and WC.is_int(g[1]) and WC.is_int(g[2]) and 1 <= abs(g[2]) <= len(P['warps']),
                    'format', 'A warp %d' % i)
            A.append(('warp', g[1], g[2], frame_lit(g[3]), frame_lit(g[4]), list(g[3]), list(g[4])))
        else:
            A.append(WC.conv_gate(g, lambda F: None if F is None else frame_lit(F), 'A[%d]' % i))
    P['A'] = A
    P['sections']['A'] = A
    return P


def a_warp_algebra(P, item):
    """An A-phase warp uses the B record's G (or G^-1): it must carry span U onto span E with rank-zero K_G."""
    _, reg, k, U, E, Ul, El = item
    rec = P['warps'][abs(k) - 1]
    cols = rec['G'] if k > 0 else WC.mat_inverse(rec['G'], P['h'])
    WC.need(cols is not None, 'awarp', 'singular G')
    fake = dict(op=k, pos=-1, lender=reg, G=cols, U_list=Ul, E_list=El, U=U, E=E)
    return WC.check_warp(fake, P['h'], set(P['live']), P['v'])


# ------------------------------------------------------------------------------------ frame-chain recount ---
def frame_recount(P):
    """Literal frame chain: precondition/compensation at frame 0 on targets only; every A, B and restore gate
    climbs its registers (a strict climb pays one child of its rank); A and B warps are rank zero and need the
    current frame to equal U exactly; each centre pays one COPY child per distinct nested served level; all live
    registers climb to their end frames; cleanup runs at FULL.  Each register's total charge must equal its width."""
    v, full = P['v'], P['full']
    cur = {r: P['start'][r] for r in P['live']}
    paid, per_reg, climbs = Counter(), Counter(), {}

    def istarget(r):
        return v <= r < 2 * v

    def climb(r, F, where):
        WC.need(r in cur, 'frame', 'register %d not live (%s)' % (r, where))
        WC.need(WC.contains(cur[r], F), 'frame', 'non-nested climb of %d at %s' % (r, where))
        d = len(F) - len(cur[r])
        if d:
            paid[d] += 1
            per_reg[r] += d
            climbs.setdefault(r, []).append((where, d))
        cur[r] = F

    for i, g in enumerate(P['pre']):
        WC.need(g[-1] == () and istarget(g[1]), 'frame', 'pre gate %d not a frame-0 target gate' % i)
        for r in WC.regs_of(g):
            climb(r, (), 'pre[%d]' % i)
    plain = [x for x in P['A'] if x[0] != 'warp'] + [x for x in P['B_items'] if x[0] != 'warp'] + list(P['post'])
    WC.need(not any(g[0] == 'add' and not istarget(g[1]) and istarget(g[2]) for g in plain), 'frame',
            'non-target reads a target')
    a_warps = []
    for i, g in enumerate(P['A']):
        if g[0] == 'warp':
            reg, U, E = g[1], g[3], g[4]
            WC.need(reg in cur and not istarget(reg), 'frame', 'A warp on non-live/target %d' % reg)
            WC.need(cur[reg] == U, 'frame', 'A warp %d: frame of %d != U' % (i, reg))
            a_warps.append(a_warp_algebra(P, g))
            cur[reg] = E
            continue
        WC.need(g[-1] is not None, 'frame', 'unframed A gate')
        for r in WC.regs_of(g):
            climb(r, g[-1], 'A[%d]' % i)
    for t in range(v):
        WC.need(cur[v + t] == P['target_levels'].get(t, ()), 'frame', 'target %d off level after A' % t)
    for q, U in zip(P['centers'], P['center_frames']):
        WC.need(cur[q] == U, 'frame', 'centre %d frame' % q)
    served = dict((q, set()) for q in P['centers'])
    for i, g in enumerate(P['cut']):
        WC.need(g[0] == 'add' and g[-1] is None and istarget(g[1]) and g[2] in served, 'frame', 'cut %d' % i)
        served[g[2]].add(cur[g[1]])
    copy_paths = []
    for q, U in zip(P['centers'], P['center_frames']):
        prev, path = U, []
        for T in sorted(served[q], key=lambda S: (-len(S), S)):
            WC.need(WC.contains(T, prev), 'frame', 'copy levels not nested at centre %d' % q)
            if T != prev:
                paid[len(prev) - len(T)] += 1
                path.append(len(prev) - len(T))
            prev = T
        copy_paths.append(dict(centre=q, dim=len(U), children=path, served_dims=sorted(len(T) for T in served[q])))
    for i, it in enumerate(P['B_items']):
        if it[0] == 'warp':
            L, k, U, E = it[1], it[2], it[3], it[4]
            WC.need(L in cur and not istarget(L), 'frame', 'B warp lender')
            WC.need(cur[L] == U, 'frame', 'B warp %d: lender %d frame != U' % (k, L))
            cur[L] = E
        else:
            WC.need(it[-1] is not None, 'frame', 'unframed B gate')
            for r in WC.regs_of(it):
                climb(r, it[-1], 'B[%d]' % i)
    for i, g in enumerate(P['post']):
        for r in WC.regs_of(g):
            climb(r, g[-1], 'post[%d]' % i)
    for r in P['live']:
        climb(r, P['end'][r], 'end')
    for i, it in enumerate(P['cleanup']):
        WC.need(it[-1] == full, 'frame', 'cleanup %d not FULL' % i)
        for r in ((it[1],) if it[0] == 'warp' else WC.regs_of(it)):
            WC.need(r in P['buffers'] or cur.get(r) == full, 'frame', 'cleanup touches non-FULL %d' % r)
    for r in P['live']:
        WC.need(per_reg[r] == len(P['end'][r]) - len(P['start'][r]), 'frame', 'charge of %d != its width' % r)
    helpers = [r for r in P['live'] if r >= 2 * v]
    widths = [len(P['end'][r]) - len(P['start'][r]) for r in helpers]
    return dict(paid=dict(sorted(paid.items())), inventory=dict(sorted(Counter(widths).items())), helper_widths=widths,
                helpers=len(helpers), copy_paths=copy_paths, a_warps=a_warps, climbs=climbs,
                mass=sum(k * c for k, c in paid.items()))


ORIENTATIONS = ('forward', 'dual')


def run_replay(P, dual):
    """words_check.replay in one orientation.  The returned diagnostics carry the orientation that was run, and a
    rejection (WC.Reject) is annotated with it (e.orientation), so reject_stage can say which replay rejected."""
    orientation = ORIENTATIONS[1] if dual else ORIENTATIONS[0]
    try:
        diag = WC.replay(P, dual=dual)
    except WC.Reject as e:
        e.orientation = orientation
        raise
    return dict(diag, orientation=orientation)


def forward_replay(P):
    """The forward free-operator replay (Y_t += X_t).  Before cleanup it requires every buffer to be zero, every
    target to hold Y_t + X_t and every restored cold register its own input; after cleanup, the final map and every
    zero buffer back at zero."""
    return run_replay(P, False)


def dual_replay(P):
    """The dual-orientation free-operator replay (X -= Y, g^-T).  Before cleanup it requires only that every buffer
    is zero (it has no target or restored-register check), so an endpoint error of the word is rejected after cleanup,
    at the final map; after cleanup it also requires every zero buffer to be back at zero, which a cleanup can violate
    in the dual orientation alone (see dual_only_mutant)."""
    return run_replay(P, True)


def full_check(w, orientations=ORIENTATIONS):
    """Parse, warp algebra, frame recount and the exact replays of one word (raises WC.Reject): forward and dual for
    the main check; the dual controls run the same path with orientations=('dual',) only."""
    P = parse_ext(w)
    warps = WC.check_all_warps(P)
    fr = frame_recount(P)
    fwd = forward_replay(P) if 'forward' in orientations else None
    dual = dual_replay(P) if 'dual' in orientations else None
    return P, warps, fr, fwd, dual


def summarize(P, warps, fr, fwd, dual):
    return dict(live=len(P['live']), helpers=fr['helpers'], warps=len(warps), a_warps=len(fr['a_warps']),
                profile=fr['paid'], widths=fr['inventory'], mass=fr['mass'], buffers=len(P['buffers']),
                copy_paths=[[c['centre'], c['children']] for c in fr['copy_paths']],
                lifted_targets=sorted(P['target_levels']), target_levels=sorted(set(P['target_levels'].values())),
                replay_forward=fwd, replay_dual=dual, cleanup_items=len(P['cleanup']))


def check_claims(tag, P, fr, claim, lifted, copy_children):
    """The recount must equal the stated claim (claims.profile_widths) and the word's own report fields
    (claims.report_fields); rejections read 'claims.<id>: <tag> ...'."""
    need(fr['paid'] == claim['profile'] and fr['inventory'] == claim['widths'], 'claims.profile_widths: %s %r %r'
         % (tag, fr['paid'], fr['inventory']))
    need(fr['paid'] == P['claimed_profile'] and fr['inventory'] == P['claimed_inventory'],
         'claims.report_fields: %s report %r %r' % (tag, P['claimed_profile'], P['claimed_inventory']))
    need(fr['helpers'] == claim['helpers'] and len(P['live']) == claim['live'] and len(P['buffers']) == claim['buffers'],
         'claims.register_counts: ' + tag)
    need(fr['mass'] == claim['mass'], 'claims.local_mass: ' + tag)
    copy_total = sum(sum(c['children']) for c in fr['copy_paths'])
    need(fr['mass'] == sum(fr['helper_widths']) + 2 * V * 8 + copy_total, 'claims.mass_identity: ' + tag)
    need(sorted(P['target_levels']) == lifted and all(F == WC.span([30]) for F in P['target_levels'].values()),
         'claims.lifted_targets: ' + tag)
    need(Counter(d for c in fr['copy_paths'] for d in c['children']) == Counter(copy_children),
         'claims.centre_children: ' + tag)
    return dict(mass_identity='%d = %d helper widths + %d sources + %d targets + %d COPY'
                % (fr['mass'], sum(fr['helper_widths']), V * 8, V * 8, copy_total))


# ------------------------------------------------------------------------------- structural diff vs PR2462 ---
def regs(g):
    return tuple(g[1:3]) if g[0] == 'add' else (g[1],)


def structural_diff(wn, wo):
    """Align old B (removed helper h renamed to its lender r) with new B; classify every difference."""
    ren = dict((h, r) for h, r, _ in ALIASES)
    need(sorted(set(wn['removed']) - set(wo['removed'])) == sorted(ren) and set(wo['removed']) <= set(wn['removed']),
         'diff: newly removed helpers')

    def rn(g):
        g = list(g)
        for k in ((1, 2) if g[0] == 'add' else (1,)):
            g[k] = ren.get(g[k], g[k])
        return g

    old, new = wo['B'], wn['B']
    i = j = 0
    deleted, inserted, frame_changed, old_to_new = [], [], [], {}
    while i < len(old) or j < len(new):
        if i < len(old) and j < len(new) and rn(old[i]) == new[j]:
            old_to_new[i] = j
            i, j = i + 1, j + 1
        elif i < len(old) and j < len(new) and rn(old[i])[:-1] == new[j][:-1]:
            frame_changed.append(i)
            old_to_new[i] = j
            i, j = i + 1, j + 1
        elif i < len(old) and old[i][0] == 'add' and V <= old[i][1] < 2 * V and old[i][2] in ren:
            deleted.append(i)
            i += 1
        elif j < len(new):
            inserted.append(j)
            j += 1
        else:
            deleted.append(i)
            i += 1
    need(not frame_changed, 'diff: B gates with changed frames')
    need([new[j][:-1] for j in inserted] == RESTORATIONS, 'diff: inserted gates are not the README restorations')
    echoes = Counter(old[i][2] for i in deleted)
    need(all(old[i][0] == 'add' and V <= old[i][1] < 2 * V and old[i][2] in ren for i in deleted), 'diff: non-echo deletion')
    need(echoes == Counter(dict((h, 4) for h in ren)), 'diff: 4 echo reads per removed helper')
    for h in sorted(ren):
        first = next(k for k, g in enumerate(old) if g[1] == h)
        need(all(k < first for k in deleted if old[k][2] == h), 'diff.echo_order: echo of %d after its first write' % h)
    # warps: old records unchanged except position (which follows the B alignment), 8 records appended
    wo_, wn_ = wo['warps'], wn['warps']
    need(len(wn_) == len(wo_) + 8 and all(a[1:] == b[1:] for a, b in zip(wo_, wn_)), 'diff: old warp records')
    following = sum(1 for a, b in zip(wo_, wn_) if a[0] in old_to_new and b[0] == old_to_new[a[0]])
    need(following == len(wo_), 'diff: old warp positions do not follow the B alignment')
    new_lenders = [rec[1] for rec in wn_[len(wo_):]]
    need(sorted(new_lenders) == sorted(r for _, r, _ in ALIASES), 'diff: new warp lenders')
    # A prelude: 12 identity lifts, then one block per new lender using that lender's own handoff operator
    pe_n, pe_o = wn['prelude_events'], wo['prelude_events']
    need(wn['A'][pe_n:] == wo['A'][pe_o:] and wn['A'][pe_n - pe_o:pe_n] == wo['A'][:pe_o], 'diff: A outside new prelude')
    pre = wn['A'][:pe_n - pe_o]
    new_lifts = sorted(set(LIFTED_2530) - set(LIFTED_2462))
    need([g[:4] for g in pre[:len(new_lifts)]] == [['scale', V + t, 1, 1] for t in new_lifts]
         and all(g[4] == [30] for g in pre[:len(new_lifts)]), 'diff: prelude identity lifts')
    op_of = dict((rec[1], k) for k, rec in enumerate(wn_, 1))
    blocks, rest = [], pre[len(new_lifts):]
    need(len(rest) == 6 * 8, 'diff: prelude block count')
    for b in range(8):
        blk = rest[6 * b:6 * b + 6]
        L, k = blk[0][1], blk[0][2]
        need(blk[0][0] == 'warp' and k == op_of[L] and blk[5][:3] == ['warp', L, -k] and blk[0][3:] == blk[5][3:][::-1],
             'diff: prelude block %d warp pair' % b)
        need(all(g[0] == 'add' and g[2] == L and V <= g[1] < 2 * V and g[4] in (2, 4) and abs(g[3]) == 1 for g in blk[1:5]),
             'diff: prelude block %d target adds' % b)
        blocks.append(dict(lender=L, op=k, U=blk[0][3], E=blk[0][4], targets=[g[1] - V for g in blk[1:5]]))
    need(sorted(bl['lender'] for bl in blocks) == sorted(new_lenders), 'diff: prelude lenders')
    same = dict((s, wn[s] == wo[s]) for s in ('precondition', 'compensation', 'cut', 'restore', 'ports', 'centers',
                                               'center_frames', 'helper_final', 'initial_corrections'))
    need(all(same.values()), 'diff: unchanged sections %r' % same)
    se_o = dict((k, v) for k, v in wo['start_extra'].items() if int(k) not in ren)
    need(se_o == wn['start_extra'] and all(wo['start_extra'][str(h)] == [30] for h in ren), 'diff: start_extra')
    removed_frames = Counter(json_key(wo['start_extra'][str(h)]) for h in ren)
    return dict(B_old=len(old), B_new=len(new), deleted_echoes=len(deleted), inserted=len(inserted),
                inserted_gates=[[j] + new[j] for j in inserted], warps_old=len(wo_), warps_new=len(wn_),
                old_warp_positions_following_alignment=following,
                new_warps=[[k + 1] + rec[:2] + rec[3:] for k, rec in enumerate(wn_) if k >= len(wo_)],
                prelude_old=pe_o, prelude_new=pe_n, prelude_blocks=blocks,
                removed_helper_start_frames=dict(sorted(removed_frames.items())),
                echo_reads_before_first_write=dict((str(h), sorted(k for k in deleted if old[k][2] == h)) for h in sorted(ren)),
                unchanged=sorted(k for k, v in same.items() if v)), inserted


def json_key(x):
    return json.dumps(x, separators=(',', ':'))


def alias_partners(aliases, inserted_gates):
    """The partner column of ALIASES must be the source register of the lender's inserted restoration add(s),
    read from the word's inserted gates ([j, kind, target, source, ...]); returns {lender: [partner]}."""
    got = defaultdict(set)
    for g in inserted_gates:
        if g[1] == 'add':
            got[g[2]].add(g[3])
    want = dict((r, set([p])) for _, r, p in aliases)
    need(dict(got) == want, 'aliases.partner: ALIASES partner column %r != inserted restoration sources %r'
         % (sorted((r, sorted(v)) for r, v in want.items()), sorted((r, sorted(v)) for r, v in got.items())))
    return dict((str(r), sorted(v)) for r, v in sorted(got.items()))


# --------------------------------------------------------------------------- exact rows of the restorations ---
def _apply(rows, g):
    if g[0] == 'add':
        t, s, c = g[1], g[2], Fraction(g[3], g[4])
        dst = rows[t]
        for key, val in list(rows[s].items()):
            nv = dst.get(key, 0) + c * val
            if nv:
                dst[key] = nv
            else:
                dst.pop(key, None)
    elif g[0] == 'scale':
        c = Fraction(g[2], g[3])
        rows[g[1]] = dict((k, v * c) for k, v in rows[g[1]].items())
    else:
        reg, k = g[1], g[2]
        rows[reg] = dict(((var, word[1:] if word and word[0] == -k else (k,) + word), val)
                         for (var, word), val in rows[reg].items())


def _fmt(row):
    def name(x):
        return 'X%d' % x if x < V else ('Y%d' % (x - V) if x < 2 * V else 'H%d' % x)
    return ' + '.join('%s*%s%s' % (v, 'K%s.' % '.'.join(map(str, w)) if w else '', name(x))
                      for (x, w), v in sorted(row.items()))


def restoration_rows(wn, inserted):
    """Own minimal exact replay up to the end of B: rows of the touched registers before/after each inserted gate
    and of each lender/partner just before its handoff warp.  Every new lender must hold exactly X_r there."""
    rows = dict((r, {(r, ()): Fraction(1)}) for r in range(2 * V + wn['report']['R']) if r not in set(wn['removed']))
    for sec in ('precondition', 'compensation', 'A', 'cut'):
        for g in wn[sec]:
            _apply(rows, g)
    by_pos = defaultdict(list)
    for op, rec in enumerate(wn['warps'], 1):
        by_pos[rec[0]].append((op, rec[1]))
    watch = set(r for _, r, _ in ALIASES) | set(p for _, _, p in ALIASES)
    gates, handoffs = [], {}
    ins = set(inserted)
    for i in range(len(wn['B']) + 1):
        for op, L in by_pos[i]:
            if L in watch:
                handoffs[L] = dict(op=op, B_pos=i, row=_fmt(rows[L]))
            _apply(rows, ['warp', L, op])
        if i < len(wn['B']):
            g = wn['B'][i]
            before = dict((r, _fmt(rows[r])) for r in regs(g)) if i in ins else None
            _apply(rows, g)
            if before is not None:
                gates.append(dict(B=i, gate=g[:-1], before=before, after=dict((r, _fmt(rows[r])) for r in regs(g))))
    for _, r, _ in ALIASES:
        need(handoffs[r]['row'] == '1*X%d' % r, 'restoration.handoff: lender %d is %s at its handoff' % (r, handoffs[r]['row']))
    return dict(gates=gates, handoff_rows=dict((str(r), handoffs[r]) for r in sorted(handoffs)))


def inserted_gate_label(j, warps):
    """frame_recount's label 'B[k]' of raw gate B[j]: k counts the B items before it, and the warps of position p
    run before B[p] (words_check.parse_borrow), so k = j + #{warp records at positions <= j}."""
    return 'B[%d]' % (j + sum(1 for rec in warps if rec[0] <= j))


def label_formula(P, warps):
    """inserted_gate_label(j) must name the parsed B item of raw gate B[j] for every B gate (not only the nine
    inserted ones), and some B gate must share its position with a warp record, so the `<=` boundary of the
    formula is exercised."""
    b_index = [k for k, it in enumerate(P['B_items']) if it[0] != 'warp']
    need(len(b_index) == len(P['sections']['B']), 'climbs.labels: parsed B gate count')
    bad = [j for j in range(len(b_index)) if inserted_gate_label(j, warps) != 'B[%d]' % b_index[j]]
    need(not bad, 'climbs.labels: label formula wrong for raw B gates %r' % bad[:5])
    positions = set(rec[0] for rec in warps)
    boundary = sum(1 for j in range(len(b_index)) if j in positions)
    need(boundary > 0, 'climbs.labels: no B gate shares its position with a warp (boundary case not exercised)')
    return dict(B_gates_checked=len(b_index), gates_with_a_warp_at_their_position=boundary)


def inserted_climbs(P, fr, inserted, prelude_events, warps):
    """The inserted gates must cause no paid climb; each lifted target pays one rank-1 climb inside the prelude.
    The label set is guarded: exactly the nine README restorations, each label (re-derived from the raw warp
    positions) naming the parsed B item of that inserted gate."""
    need(len(inserted) == len(RESTORATIONS) == 9, 'climbs.labels: %d inserted gates, expected 9' % len(inserted))
    b_index = [k for k, it in enumerate(P['B_items']) if it[0] != 'warp']
    where = dict(('B[%d]' % b_index[j], j) for j in inserted)
    need(len(where) == 9 and sorted(where) == sorted(inserted_gate_label(j, warps) for j in inserted)
         and all(P['B_items'][b_index[j]] is P['sections']['B'][j] for j in inserted),
         'climbs.labels: inserted-gate labels are not exactly the nine inserted B items')
    gates, hits = [], []
    for label, j in sorted(where.items(), key=lambda x: x[1]):
        paid = sorted([r, d] for r, lst in fr['climbs'].items() for w, d in lst if w == label)
        hits += [[label] + x for x in paid]
        it = P['sections']['B'][j]
        gates.append(dict(B=j, label=label, registers=list(WC.regs_of(it)), frame_dim=len(it[-1]), paid_climbs=paid))
    need(not hits, 'climbs.inserted_gate_paid: restoration gates pay climbs %r' % hits[:5])
    first = {}
    for t in P['target_levels']:
        w, d = fr['climbs'][V + t][0]
        need(w.startswith('A[') and int(w[2:-1]) < prelude_events and d == 1, 'lift of target %d not a rank-1 prelude climb' % t)
        first[str(t)] = w
    return dict(inserted_gates=gates, inserted_gate_paid_climbs=len(hits), lift_climbs=first)


def climb_injection_control(P, fr, inserted, prelude_events, warps):
    """Negative control: for each inserted gate in turn, a rank-1 paid climb of its first register is added to a
    copy of the recount at that gate's label (computed from the raw warp positions) and must be rejected by the
    zero-climb check of inserted_climbs."""
    msgs = []
    for j in inserted:
        bad = dict(fr)
        bad['climbs'] = dict((r, list(lst)) for r, lst in fr['climbs'].items())
        r = WC.regs_of(P['sections']['B'][j])[0]
        bad['climbs'].setdefault(r, []).append((inserted_gate_label(j, warps), 1))
        try:
            inserted_climbs(P, bad, inserted, prelude_events, warps)
        except AuditFail as e:
            need(str(e).startswith('climbs.inserted_gate_paid:'), 'control: injected climb at B[%d] rejected by %s' % (j, e))
            msgs.append(str(e))
            continue
        raise AuditFail('negative control ACCEPTED: paid climb injected at inserted gate B[%d]' % j)
    return dict(control='rank-1 paid climb injected at each of the %d inserted gates in turn' % len(msgs),
                mutant='recount with an injected climb', expected='climbs.inserted_gate_paid',
                rejected_by=','.join(sorted(set(m.split(':', 1)[0] for m in msgs))), injections=len(msgs),
                message=msgs[0][:100])


# ----------------------------------------------------------------------------------------- cleanup ---
def rederive_cleanup(w):
    """Own inverse-reverse of the non-target word (A after the prelude, B with warps at their positions, restore),
    restored cold helpers renamed to their buffer r+n, every item at FULL."""
    n = 2 * V + w['report']['R']
    restored = set(map(int, w['helper_final']))
    full = [1 << b for b in range(9)][::-1]

    def buf(r):
        return r + n if r in restored else r

    fwd = list(w['A'][w['prelude_events']:])
    by_pos = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        by_pos[rec[0]].append((rec[1], op))
    for p in range(len(w['B']) + 1):
        fwd += [['warp', r, op] for r, op in by_pos[p]]
        if p < len(w['B']):
            fwd.append(w['B'][p])
    fwd += w['restore']
    out = []
    for g in reversed(fwd):
        if g[0] == 'warp':
            out.append(['warp', buf(g[1]), -g[2], full])
        elif not (V <= g[1] < 2 * V):
            if g[0] == 'add':
                out.append(['add', buf(g[1]), buf(g[2]), -g[3], g[4], full])
            else:
                out.append(['scale', buf(g[1]), g[3], g[2], full])
    return out


def cleanup_literal(wn, wo):
    """PR2530's cleanup equals the own inverse-reverse re-derivation literally (frames aside), every item is at
    FULL, and it has 9 + 8 more items than PR2462's (the inverses of the inserted gates and of the new warps)."""
    mine = rederive_cleanup(wn)
    need([g[:-1] for g in mine] == [g[:-1] for g in wn['cleanup']], 'cleanup.literal: own inverse-reverse != PR cleanup')
    full = WC.span([1 << b for b in range(9)])
    at_full = sum(1 for g in wn['cleanup'] if WC.span(g[-1]) == full)
    need(at_full == len(wn['cleanup']), 'cleanup.full: frame not FULL')
    need(len(wn['cleanup']) - len(wo['cleanup']) == len(RESTORATIONS) + 8, 'cleanup.count: +9 inverses +8 inverse warps')
    return dict(items=len(mine), pr2462_items=len(wo['cleanup']), items_at_full=at_full,
                literal_equal=[g[:-1] for g in mine] == [g[:-1] for g in wn['cleanup']])


# --------------------------------------------------------------------------------------- controls ---
def _find_B(w, pred):
    return next(i for i, g in enumerate(w['B']) if pred(g))


def _shift_warps(w, at, delta):
    for rec in w['warps']:
        if rec[0] > at or (delta > 0 and rec[0] >= at):
            rec[0] += delta


def _m_flip(t, s):
    def f(w):
        w['B'][_find_B(w, lambda g: g[:3] == ['add', t, s] and g[3] == -1 and g[4] == 1)][3] = 1
    return f


def _m_half_to_one(w):
    w['B'][_find_B(w, lambda g: g[:2] == ['scale', 68] and g[2:4] == [1, 2])][3] = 1


def _m_drop_31(w):
    i = _find_B(w, lambda g: g[:3] == ['add', 31, 12])
    del w['B'][i]
    _shift_warps(w, i, -1)


def _m_prelude_coeff(w):
    i = next(k for k, g in enumerate(w['A'][:w['prelude_events']]) if g[0] == 'add' and g[2] == 49)
    w['A'][i][3] *= -1


def _m_prelude_drop_31(w):
    k = next(k for k, g in enumerate(w['A']) if g[0] == 'warp' and g[1] == 31 and g[2] > 0)
    del w['A'][k:k + 6]
    w['prelude_events'] -= 6


def _m_prelude_wrong_op(w):
    for k, g in enumerate(w['A']):
        if g[0] == 'warp' and g[1] == 49:
            g[2] = 52 if g[2] > 0 else -52


def _m_prelude_no_inverse(w):
    del w['A'][next(k for k, g in enumerate(w['A']) if g[0] == 'warp' and g[1] == 49 and g[2] < 0)]
    w['prelude_events'] -= 1


def _m_low_frame(w):
    w['B'][_find_B(w, lambda g: g[:3] == ['add', 49, 33])][-1] = [30]


def _m_drop_level(w):
    del w['target_levels']['29']


def _m_warp_E(w):
    w['warps'][50][4] = list(w['warps'][50][3])


def _m_extra_read(w):
    w['B'].insert(186, ['add', V + 29, 49, 1, 1, w['B'][186][-1]])
    _shift_warps(w, 186, 1)


# Word mutations not covered by GATE_MUTATIONS: (name, mutation, words_check id of full_check's first rejection).
WORD_MUTATIONS = [
    ('drop 31+=12/2', _m_drop_31, 'replay'), ('flip prelude coefficient (49)', _m_prelude_coeff, 'replay'),
    ('drop prelude block for 31', _m_prelude_drop_31, 'replay'),
    ('prelude uses wrong operator 52 for 49', _m_prelude_wrong_op, 'warp'),
    ('prelude missing inverse warp', _m_prelude_no_inverse, 'frame'),
    ('inserted gate at too-low frame [30]', _m_low_frame, 'frame'), ('drop target level 29', _m_drop_level, 'frame'),
    ('new warp 51 E := U', _m_warp_E, 'warp'), ('extra target<-lender read', _m_extra_read, 'frame')]


def _m_set(pred, k, val):
    def f(w):
        w['B'][_find_B(w, pred)][k] = val
    return f


# One mutation of each of the nine inserted gates (sign flip, or the 1/2 scale made 1).
GATE_MUTATIONS = [
    ('flip 49-=33', _m_flip(49, 33)), ('flip 83-=74', _m_flip(83, 74)), ('flip 98-=85', _m_flip(98, 85)),
    ('flip 101-=55', _m_flip(101, 55)), ('68/=2 -> 68*=1', _m_half_to_one), ('flip 68-=4', _m_flip(68, 4)),
    ('flip 80-=88', _m_flip(80, 88)),
    ('flip 88+=80/2', _m_set(lambda g: g[:3] == ['add', 88, 80] and g[3:5] == [1, 2], 3, -1)),
    ('flip 31+=12/2', _m_set(lambda g: g[:3] == ['add', 31, 12] and g[4] == 2, 3, -1))]
# Word mutants that full_check rejects before the free-operator replay: the forward replay alone must reject them.
FORWARD_REPLAY_ONLY = ('prelude uses wrong operator 52 for 49', 'extra target<-lender read', 'prelude missing inverse warp')
# Word endpoint mutants (besides the nine gate mutants) also given to the dual replay alone.
DUAL_WORD_MUTANTS = ('drop 31+=12/2', 'flip prelude coefficient (49)', 'drop prelude block for 31')
# Word mutants (besides the nine gate mutants) also given to the handoff-row check.
HANDOFF_WORD_MUTANTS = ('prelude missing inverse warp',)

STAGE_FORWARD_BEFORE_CLEANUP = 'forward replay, before cleanup'
STAGE_DUAL_FINAL_MAP = 'dual replay, final map after cleanup'
STAGE_DUAL_BUFFERS_AFTER_CLEANUP = 'dual replay, buffers after cleanup'
# The dual-only cleanup mutant: (live helper h, zero buffer b) of the prepended cleanup add h += b (both words).
DUAL_ONLY_ADD = (399, 977)
# Where the package's own (AuditFail) word checks reject.
STAGE_OF_RULE = {'restoration.handoff': 'handoff rows (forward exact replay up to each lender\'s handoff warp)',
                 'cleanup.literal': 'cleanup comparison with the own inverse-reverse',
                 'diff.echo_order': 'structural diff against PR2462', 'aliases.partner': 'ALIASES partner column'}


def reject_stage(e):
    """Where a words_check rejection happened: the check family, and for the replay which orientation rejected
    (e.orientation, set by run_replay) and whether before or after cleanup (the forward replay checks targets and
    restored registers before cleanup; both orientations check the buffers before and after cleanup and the final
    map)."""
    if e.check != 'replay':
        return {'format': 'parse', 'anticipatory': 'parse', 'warp': 'warp algebra', 'frame': 'frame recount'}.get(e.check,
                                                                                                                 e.check)
    o = getattr(e, 'orientation', None)
    if e.msg.startswith('final map wrong'):
        return '%s replay, final map after cleanup' % (o or ('dual' if e.msg.endswith('(dual)') else 'forward'))
    if e.msg.startswith(('target ', 'restored ')):
        return '%s replay, before cleanup' % (o or 'forward')
    if e.msg.startswith('a buffer is non-zero before cleanup'):
        return '%s replay, buffers before cleanup' % (o or 'unknown')
    if e.msg.startswith('a zero buffer is not returned'):
        return '%s replay, buffers after cleanup' % (o or 'unknown')
    return '%s replay, other' % (o or 'unknown')


def expect_word_reject(out, tag, name, expected, stage, fn, **extra):
    """Negative control on one word: fn() must raise, by the check `expected` (a words_check id, or the 'rule' prefix
    of an AuditFail message) and, if `stage` is given, at that stage.  The record says where it was rejected."""
    attempt('%s (%s word)' % (name, tag))
    try:
        fn()
    except WC.Reject as e:
        got, where, msg = e.check, reject_stage(e), e.msg
    except AuditFail as e:
        msg = str(e)
        got = msg.split(':', 1)[0]
        where = STAGE_OF_RULE.get(got, got)
    else:
        raise AuditFail('negative control ACCEPTED: %s (%s word)' % (name, tag))
    need(got == expected and (stage is None or where == stage), 'control %s (%s word): rejected by %s at %r (%s), '
         'expected %s%s' % (name, tag, got, where, msg[:80], expected, '' if stage is None else ' at %r' % stage))
    rec = dict(control=name, mutant=name, word=tag, expected=expected, rejected_by=got, stage=where, message=msg[:120])
    rec.update(extra)
    out.append(rec)


def echo_order_mutant(wo, h):
    """PR2462's word with the last echo read of helper h before h's first write moved to just after that first write
    (warp records stay on their items).  structural_diff must then reject it by diff.echo_order."""
    old = wo['B']
    first = next(k for k, g in enumerate(old) if g[1] == h)
    e = max(k for k in range(first) if old[k][0] == 'add' and V <= old[k][1] < 2 * V and old[k][2] == h)
    B = list(old)
    B.insert(first, B.pop(e))        # after the pop the first write is at first - 1
    warps = [[rec[0] - 1 if e < rec[0] <= first else rec[0]] + list(rec[1:]) for rec in wo['warps']]
    return dict(wo, B=B, warps=warps)


def dual_only_mutant(wn, P):
    """PR2530's word with ['add', h, b, 1, 1, FULL] prepended to its cleanup (h, b = DUAL_ONLY_ADD): in the forward
    orientation the live helper h (at FULL after B) adds the zero buffer b, a no-op; in the dual orientation the same
    item is b -= h, which leaves the buffer b non-zero after cleanup.  The forward replay must accept it and
    full_check must reject it through the dual replay alone."""
    h, b = DUAL_ONLY_ADD
    need(b in P['buffers'] and h in P['live'] and h >= 2 * V and P['end'][h] == P['full'],
         'control dual-only: %d is not a zero buffer or %d not a live helper at FULL' % (b, h))
    return dict(wn, cleanup=[['add', h, b, 1, 1, list(wn['cleanup'][0][-1])]] + list(wn['cleanup']))


def _frame_sequence(P):
    """The framed items in frame_recount's order (prelude frames 0 first): [(section, index, registers, frame,
    is_warp)], a warp entering its lender at E."""
    seq = []
    for sec, items in (('A', P['A']), ('B', P['B_items']), ('post', P['post'])):
        for i, g in enumerate(items):
            if g[0] == 'warp':
                seq.append((sec, i, (g[1],), g[4], True))
            else:
                seq.append((sec, i, tuple(WC.regs_of(g)), g[-1], False))
    return seq


def climb_split_mutant(w):
    """Negative control of the recount against the claim (the word's report unchanged): the first A gate after the
    prelude whose registers all sit at its frame G (climb 0) and all climb exactly 2 at their next framed item (a
    gate, not a warp, or the end frame) gets the intermediate frame G + v, v the smallest vector of every register's
    next frame outside G.  Each of those rank-2 climbs becomes 1 + 1: every per-register charge still equals its
    width and the mass is unchanged, only the climb split (the paid profile) changes.  Returns (mutant, record)."""
    P = parse_ext(w)
    cur = dict((r, P['start'][r]) for r in P['live'])
    for g in P['pre']:
        for r in WC.regs_of(g):
            cur[r] = ()
    seq = _frame_sequence(P)
    before = []
    for _, _, regs, F, _ in seq:
        before.append(dict((r, cur[r]) for r in regs))
        for r in regs:
            cur[r] = F
    last = dict((r, (None, P['end'][r])) for r in P['live'])
    nxt = [None] * len(seq)
    for k in range(len(seq) - 1, -1, -1):
        regs, F = seq[k][2], seq[k][3]
        nxt[k] = dict((r, last[r]) for r in regs)
        for r in regs:
            last[r] = (k, F)
    for k, (sec, i, regs, G, is_warp) in enumerate(seq):
        if sec != 'A' or is_warp or i < w['prelude_events'] or any(before[k][r] != G for r in regs):
            continue
        if any(q is not None and seq[q][4] for q, _ in nxt[k].values()):
            continue
        if any(len(N) - len(G) != 2 for _, N in nxt[k].values()):
            continue
        v = next((v for v in range(1, 1 << P['h']) if len(WC.span(list(G) + [v])) == len(G) + 1
                  and all(WC.contains(WC.span(list(G) + [v]), N) for _, N in nxt[k].values())), None)
        if v is None:
            continue
        m = copy.deepcopy(w)
        m['A'][i][-1] = list(w['A'][i][-1]) + [v]
        return m, dict(gate='A[%d]' % i, kind=w['A'][i][0], registers=list(regs), frame_dim=[len(G), len(G) + 1],
                       added_vector=v, split='2 -> 1 + 1 for each register')
    raise AuditFail('control: no gate for the climb-split control')


def cleanup_coefficient_mutant(wn):
    """PR2530's word with the coefficient of its first cleanup add negated."""
    cl = [list(g) for g in wn['cleanup']]
    k = next(i for i, g in enumerate(cl) if g[0] == 'add')
    cl[k][3] = -cl[k][3]
    return dict(wn, cleanup=cl)


def word_controls(tag, wn, wo, inserted, controls, P, fr):
    """Negative controls of one word, each asserting the check (and, where it matters, the stage) that rejects it:
      words_full_check   9 word mutations through full_check, as shipped (cleanup not re-derived);
      gates_full_check   each of the 9 inserted gates mutated, through full_check as shipped: rejected by the
                         forward replay before cleanup (the cleanup is never reached);
      gates_handoff_rows the 9 gate mutants and the missing inverse warp through restoration_rows (lender != X_r);
      dual_replay_rederived_cleanup  the 9 gate mutants and 3 word endpoint mutants with the own re-derived cleanup
                         (which must differ from the shipped one whenever B changed), through full_check with the
                         dual replay only (the main check's code path): rejected at the final map after that cleanup;
      words_dual_only    the dual-only cleanup mutant (dual_only_mutant): the forward replay must accept it, and
                         full_check (forward and dual, as the main check) must reject it by the dual replay, at the
                         buffers after cleanup;
      words_recount      the climb-split mutant (climb_split_mutant; report unchanged) must be rejected by
                         claims.profile_widths, and the unchanged word with report.local_profile altered by
                         claims.report_fields (the recount, not the report, is what is checked against the claim);
      forward_replay_only  the 3 word mutants that full_check stops at the warp or frame check, through the forward
                         replay alone;
      cleanup_literal, diff_echo_order  one PR cleanup coefficient negated; one echo read of PR2462's helper 656
                         moved past its first write."""
    mutants = {}
    for name, f, expected in WORD_MUTATIONS:
        w = mutants[name] = copy.deepcopy(wn)
        f(w)
        expect_word_reject(controls['words_full_check'], tag, name, expected, None, lambda: full_check(w))
    for name, f in GATE_MUTATIONS:
        w = mutants[name] = copy.deepcopy(wn)
        f(w)
        expect_word_reject(controls['gates_full_check'], tag, name, 'replay', STAGE_FORWARD_BEFORE_CLEANUP,
                           lambda: full_check(w))
    for name in [g for g, _ in GATE_MUTATIONS] + list(HANDOFF_WORD_MUTANTS):
        w = mutants[name]
        expect_word_reject(controls['gates_handoff_rows'], tag, name, 'restoration.handoff', None,
                           lambda: restoration_rows(w, inserted))
    for name in FORWARD_REPLAY_ONLY:
        w = mutants[name]
        expect_word_reject(controls['forward_replay_only'], tag, name, 'replay', STAGE_FORWARD_BEFORE_CLEANUP,
                           lambda: forward_replay(parse_ext(w)))
    for name in [g for g, _ in GATE_MUTATIONS] + list(DUAL_WORD_MUTANTS):
        w = mutants[name]
        w['cleanup'] = rederive_cleanup(w)
        changed = sum(1 for a, b in zip(w['cleanup'], wn['cleanup']) if a[:-1] != b[:-1]) + abs(len(w['cleanup'])
                                                                                               - len(wn['cleanup']))
        need(changed > 0 or w['B'] == wn['B'], 'control %s (%s word): re-derived cleanup equals the shipped one '
             'although B changed' % (name, tag))
        expect_word_reject(controls['dual_replay_rederived_cleanup'], tag, name, 'replay', STAGE_DUAL_FINAL_MAP,
                           lambda: full_check(w, orientations=('dual',)), rederived_cleanup_items_changed=changed)
    # dual-only coverage: a cleanup item that is a no-op forward and leaves a buffer non-zero in the dual orientation
    wd = dual_only_mutant(wn, P)
    try:
        fwd_d = forward_replay(parse_ext(wd))
    except WC.Reject as e:
        raise AuditFail('control dual-only (%s word): the forward replay rejects it (%s), so it is not dual-only'
                        % (tag, e.msg[:80]))
    expect_word_reject(controls['words_dual_only'], tag, 'cleanup prepended with %d += zero buffer %d (a forward no-op)'
                       % DUAL_ONLY_ADD, 'replay', STAGE_DUAL_BUFFERS_AFTER_CLEANUP, lambda: full_check(wd),
                       forward_replay_alone='accepted (%s orientation, %d independent inputs)'
                       % (fwd_d['orientation'], fwd_d['independent_inputs']))
    # the recount, not the word's report, is checked against the claim
    ws, split = climb_split_mutant(wn)
    Ps = parse_ext(ws)
    frs = frame_recount(Ps)
    need(frs['mass'] == fr['mass'] and frs['inventory'] == fr['inventory'] and frs['helper_widths'] == fr['helper_widths']
         and frs['paid'] != fr['paid'], 'control climb split (%s word): charges/widths not kept or profile unchanged %r'
         % (tag, frs['paid']))
    expect_word_reject(controls['words_recount'], tag, 'climb split 2 -> 1 + 1 at %s (report unchanged)' % split['gate'],
                       'claims.profile_widths', None,
                       lambda: check_claims('PR2530 ' + tag, Ps, frs, CLAIM_2530, LIFTED_2530, {7: 8, 1: 8}),
                       recount_profile=dict((str(k), v) for k, v in sorted(frs['paid'].items())), **split)
    rep_bad = dict(wn['report'], local_profile=dict(wn['report']['local_profile']))
    rep_bad['local_profile']['1'] -= 1
    rep_bad['local_profile']['2'] += 1
    wr = dict(wn, report=rep_bad)
    expect_word_reject(controls['words_recount'], tag, 'report.local_profile with one rank-1 climb reported as rank 2 '
                       '(word unchanged)', 'claims.report_fields', None,
                       lambda: check_claims('PR2530 ' + tag, parse_ext(wr), frame_recount(parse_ext(wr)), CLAIM_2530,
                                            LIFTED_2530, {7: 8, 1: 8}))
    expect_word_reject(controls['cleanup_literal'], tag, 'one PR cleanup coefficient negated', 'cleanup.literal', None,
                       lambda: cleanup_literal(cleanup_coefficient_mutant(wn), wo))
    h = ALIASES[0][0]
    expect_word_reject(controls['diff_echo_order'], tag, 'PR2462 echo read of helper %d moved past its first write' % h,
                       'diff.echo_order', None, lambda: structural_diff(wn, echo_order_mutant(wo, h)))


# ------------------------------------------------------------------------------------ diagnostics ---
def coefficient_growth(w, dual):
    """Free-algebra replay of every section incl. cleanup: largest row L1 norm and largest denominator.  A
    comparative diagnostic (old vs new word), not the native prefix bound."""
    n = 2 * V + w['report']['R']
    rows = dict((r, {(r, ()): Fraction(1)}) for r in range(n) if r not in set(w['removed']))
    for r in map(int, w['helper_final']):
        rows[r + n] = {}
    best = [Fraction(0), 1]

    def note(r):
        vals = rows[r].values()
        best[0] = max(best[0], sum(abs(x) for x in vals))
        best[1] = max([best[1]] + [x.denominator for x in vals])

    def do(g):
        if g[0] == 'add':
            t, s, c = g[1], g[2], Fraction(g[3], g[4])
            if dual:
                t, s, c = s, t, -c
            dst = rows[t]
            for key, val in list(rows[s].items()):
                nv = dst.get(key, 0) + c * val
                if nv:
                    dst[key] = nv
                else:
                    dst.pop(key, None)
            note(t)
        elif g[0] == 'scale':
            c = Fraction(g[2], g[3])
            c = 1 / c if dual else c
            rows[g[1]] = dict((k, x * c) for k, x in rows[g[1]].items())
            note(g[1])
        else:
            letter = (g[2], dual)
            rows[g[1]] = dict(((var, wd[1:] if wd and wd[0] == (-g[2], dual) else (letter,) + wd), x)
                              for (var, wd), x in rows[g[1]].items())

    for sec in ('precondition', 'compensation', 'A', 'cut'):
        for g in w[sec]:
            do(g)
    by_pos = defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        by_pos[rec[0]].append((rec[1], op))
    for p in range(len(w['B']) + 1):
        for r, op in by_pos[p]:
            do(['warp', r, op])
        if p < len(w['B']):
            do(w['B'][p])
    for sec in ('restore', 'cleanup'):
        for g in w[sec]:
            do(g)
    return dict(max_row_l1=str(best[0]), max_denominator=best[1])


def scalar_census(wn, wo):
    """Kinds of non-unit scalars per section, new minus old: the only new kind must be the B-phase scale 1/2."""
    def census(w):
        c = Counter()
        for sec in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
            for g in w[sec]:
                if g[0] == 'scale':
                    c[(sec, 'scale', str(Fraction(g[2], g[3])))] += 1
                elif g[0] == 'add' and Fraction(g[3], g[4]) not in (1, -1):
                    c[(sec, 'add', str(Fraction(g[3], g[4])))] += 1
        return c
    cn, co = census(wn), census(wo)
    new_kinds = sorted('%s %s %s' % k for k in cn if k not in co)
    need(new_kinds == ['B scale 1/2'], 'scalar census: new non-unit scalar kinds %r' % new_kinds)
    return new_kinds


def register_namespace(w):
    """Every touched register is a live X/Y/helper or a private buffer r+704 of a helper_final r; no removed
    register is touched; warp lenders are distinct and live; centres are live."""
    removed = set(w['removed'])
    live = set(range(2 * V)) | set(r for r in range(2 * V, 2 * V + w['report']['R']) if r not in removed)
    buffers = set(int(r) + 2 * V + w['report']['R'] for r in w['helper_final'])
    touched = set()
    for sec in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
        for g in w[sec]:
            touched.update((g[1], g[2]) if g[0] == 'add' else (g[1],))
    lenders = [x[1] for x in w['warps']]
    need(touched <= live | buffers and not touched & removed, 'namespace: register outside live/buffers')
    need(set(w['centers']) <= live and len(set(lenders)) == len(lenders) and set(lenders) <= live, 'namespace: lenders/centres')
    return dict(touched=len(touched), live_touched=len(touched & live), buffers_touched=len(touched & buffers),
                lenders=len(lenders))


def providers_check(provs, frs):
    """evidence/eight-providers.json: per-provider widths (register order) and actual_paid_profile = own recount."""
    out = {}
    for pid, tag in (('gauge44', 'base'), ('extra', 'extra')):
        need(provs[pid]['widths'] == frs[tag]['helper_widths'], 'providers: %s widths' % pid)
        need(dict((int(k), v) for k, v in provs[pid]['actual_paid_profile'].items()) == frs[tag]['paid'],
             'providers: %s profile' % pid)
        out[pid] = len(provs[pid]['widths'])
    return out


# ---------------------------------------------------------------------------------------------- run ---
def run(inp, log):
    res, controls = {}, defaultdict(list)
    words = {}
    for tag in ('base', 'extra'):
        words['new', tag] = inp.json('w2530_%s' % tag)
        words['old', tag] = inp.json('w2462_%s' % tag)
    frs = {}
    for tag in ('base', 'extra'):
        wn, wo = words['new', tag], words['old', tag]
        P, warps, fr, fwd, dual = full_check(wn)
        Po, warps_o, fr_o, fwd_o, dual_o = full_check(wo)
        frs[tag] = fr
        r = dict(pr2530=summarize(P, warps, fr, fwd, dual), pr2462=summarize(Po, warps_o, fr_o, fwd_o, dual_o))
        need(len(warps) == CLAIM_2530['warps'] and len(fr['a_warps']) == CLAIM_2530['a_warps'], tag + ': warp counts')
        need(len(warps_o) == CLAIM_2462['warps'] and len(fr_o['a_warps']) == CLAIM_2462['a_warps'], tag + ': PR2462 warps')
        r['pr2530']['identity'] = check_claims('PR2530 ' + tag, P, fr, CLAIM_2530, LIFTED_2530, {7: 8, 1: 8})
        r['pr2462']['identity'] = check_claims('PR2462 ' + tag, Po, fr_o, CLAIM_2462, LIFTED_2462, {7: 4, 1: 4, 8: 4})
        positive('pr2462_%s_word' % tag)
        need(all(x['orientation'] == o for x, o in ((fwd, 'forward'), (dual, 'dual'), (fwd_o, 'forward'),
                                                    (dual_o, 'dual'))), tag + ': replay orientations')
        log('words/%s: PR2530 word passes warps (%d + %d A-phase), frame recount %s widths %s mass %d, exact replay '
            'forward+dual on %d independent inputs with %d zero buffers; positive control: PR2462 word reproduces '
            'its own profile %s on %d inputs' % (tag, len(warps), len(fr['a_warps']), fr['paid'], fr['inventory'],
                                                 fr['mass'], len(P['live']), len(P['buffers']), fr_o['paid'],
                                                 len(Po['live'])))
        r['diff'], inserted = structural_diff(wn, wo)
        r['aliases_partner'] = alias_partners(ALIASES, r['diff']['inserted_gates'])
        r['restorations'] = restoration_rows(wn, inserted)
        r['climbs'] = inserted_climbs(P, fr, inserted, wn['prelude_events'], wn['warps'])
        r['climbs']['label_formula'] = label_formula(P, wn['warps'])
        ctl = climb_injection_control(P, fr, inserted, wn['prelude_events'], wn['warps'])
        ctl['word'] = tag
        controls['plumbing_inserted_climbs'].append(ctl)
        r['cleanup'] = cleanup_literal(wn, wo)
        # main check (not a positive control): the word with the own re-derived cleanup replays identically
        _, _, _, fwd_r, dual_r = full_check(dict(wn, cleanup=rederive_cleanup(wn)))
        r['cleanup']['rederived_cleanup_word_replays_equal'] = fwd_r == fwd and dual_r == dual
        need(r['cleanup']['rederived_cleanup_word_replays_equal'], tag + ': word with re-derived cleanup replays differently')
        r['growth'] = dict((name, dict((o, coefficient_growth(w, o == 'dual')) for o in ('forward', 'dual')))
                           for name, w in (('pr2530', wn), ('pr2462', wo)))
        need(r['growth']['pr2530'] == r['growth']['pr2462'], tag + ': coefficient growth changed')
        r['scalar_kinds_new'] = scalar_census(wn, wo)
        r['namespace'] = register_namespace(wn)
        log('words/%s: diff vs PR2462 = %d echo deletions, the 9 README restorations, %d->%d warps, prelude %d->%d; '
            'lenders hold X_r at handoff; 0 paid climbs at the 9 inserted gates (frame dims %s; label formula on %d B '
            'gates); PR cleanup = own inverse-reverse (%d items); growth %s'
            % (tag, r['diff']['deleted_echoes'], r['diff']['warps_old'], r['diff']['warps_new'], r['diff']['prelude_old'],
               r['diff']['prelude_new'], [g['frame_dim'] for g in r['climbs']['inserted_gates']],
               r['climbs']['label_formula']['B_gates_checked'], r['cleanup']['items'], r['growth']['pr2530']))
        word_controls(tag, wn, wo, inserted, controls, P, fr)
        bad_aliases = tuple((h, r_, 85 if r_ == 49 else p_) for h, r_, p_ in ALIASES)
        expect_word_reject(controls['aliases_partner_column'], tag, 'ALIASES partner of lender 49 changed 33 -> 85',
                           'aliases.partner', None, lambda: alias_partners(bad_aliases, r['diff']['inserted_gates']))
        log('words/%s: negative controls rejected by their named checks: %s'
            % (tag, dict((k, sum(1 for c in v if c['word'] == tag)) for k, v in sorted(controls.items()))))
        res[tag] = r
    need(res['base']['diff'] == res['extra']['diff'], 'base and extra carry different structural edits')
    res['providers'] = providers_check(inp.json('providers2530'), frs)
    res['shared'] = dict(zero_buffers=len(inp.json('w2530_base')['helper_final']),
                         helper_widths_equal=frs['base']['helper_widths'] == frs['extra']['helper_widths'])
    need(res['shared']['helper_widths_equal'], 'providers have different ordered widths')
    return res, dict(controls)
