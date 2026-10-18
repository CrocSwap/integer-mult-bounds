# SPDX-License-Identifier: Apache-2.0
"""Negative controls of the PR #3015 audit.  Every control mutates a word, a fill, a claim or an expectation and
runs it through the function the main check uses; it must be rejected by exactly the named rule id (audit_lib.expect
counts the attempt before the mutant runs and records the control only after the rejecting rule was asserted).
Standard library only; Python 3.8-compatible syntax.
"""
import copy
from fractions import Fraction as Q

import audit_edit as AE
import audit_fill as AF
import audit_kappa as AK
import audit_lib as AL
import audit_words as AW
import check_fill as CF
import check_words as CW
import fill_check80 as FC
import words_check as WC
from audit_common import AuditFail, need

expect = AL.expect
V = AL.V
FULL = [1 << b for b in range(9)][::-1]
STAGE_FWD = 'forward replay, before cleanup'
STAGE_DUAL_BUF = 'dual replay, buffers after cleanup'


def tagged(tag, name):
    return '[%s] %s' % (tag, name)


def forge(m):
    """Report fields made equal to the own recount, so only the independent checks can reject."""
    AL.forge(m)
    return m


# ---------------------------------------------------------------------------------------------- scope A/B ---
def edit_controls(tag, wp, wc, edit, declared, expect_counts, Pp, chp, frp, out, replay_stage=None):
    a, old, new = edit['start'], edit['old'], edit['new']
    nn = len(new)
    T = lambda n: tagged(tag, n)   # noqa: E731
    pipeline = lambda m: AW.word_pipeline(m, declared, expect_counts)   # noqa: E731

    def chain_of(m):
        return AE.own_chain(AL.parse_word(m))

    # 1-2 dropped new gate: diff, then replay (report forged so that only the replay can reject)
    m = AL.mutant(wc)
    del m['restore'][a + 1]
    expect(out, T('new gate 2 dropped: own diff'), 'edit.hunk', lambda: AE.own_diff(wp, m, edit))
    m2 = forge(AL.mutant(m))
    m2['cleanup'] = AL.rederive_cleanup(m2)
    expect(out, T('new gate 2 dropped, report forged, cleanup re-derived: forward replay'), 'wc.replay',
           lambda: AL.replay(AL.parse_word(m2), False), stage=STAGE_FWD)
    # 3 flipped coefficient of new gate 1: net operator, replay, own tracker
    flipped = copy.deepcopy(new)
    flipped[0][3] = -flipped[0][3]
    expect(out, T('new gate 1 coefficient flipped: net operator'), 'edit.net_operator',
           lambda: AE.net_operator(old, flipped))
    m = forge(AL.mutant(wc))
    m['restore'][a][3] = -m['restore'][a][3]
    m['cleanup'] = AL.rederive_cleanup(m)
    expect(out, T('new gate 1 coefficient flipped, cleanup re-derived: forward replay'), 'wc.replay',
           lambda: AL.replay(AL.parse_word(m), False), stage=STAGE_FWD)
    expect(out, T('new gate 1 coefficient flipped, cleanup re-derived: own tracker'), 'words.tracker',
           lambda: AW.tracker_check(AW.track(m)))
    # 4 frames not re-solved: the old frame on all three new gates (legal word, no saving)
    m = AL.mutant(wc)
    for j in range(a, a + nn):
        m['restore'][j][-1] = copy.deepcopy(old[0][-1])
    expect(out, T('old frame kept on the three new gates: declared profile'), 'words.declared',
           lambda: AW.check_declared(CW.frame_recount(AL.parse_word(m)), declared))
    expect(out, T('old frame kept on the three new gates: attribution (no delta)'), 'edit.delta',
           lambda: AE.attribution(chp, chain_of(m), {1: -2, 2: 1}, [63]))
    # 5 gate-1 frame below the current frames of its registers (both implementations)
    m = AL.mutant(wc)
    m['restore'][a][-1] = m['restore'][a][-1][:-1]
    expect(out, T('new gate 1 frame with one generator dropped: vendored recount'), 'wc.frame',
           lambda: CW.frame_recount(AL.parse_word(m)))
    expect(out, T('new gate 1 frame with one generator dropped: own chain'), 'chain.monotone', lambda: chain_of(m))
    # 6 gate-3 frame = the old frame instead of FULL (legal, no saving)
    m = AL.mutant(wc)
    m['restore'][a + 2][-1] = copy.deepcopy(old[0][-1])
    expect(out, T('new gate 3 at the old rank-8 frame instead of FULL: declared profile'), 'words.declared',
           lambda: AW.check_declared(CW.frame_recount(AL.parse_word(m)), declared))
    # 7 parent restore kept
    m = AL.mutant(wp)
    m['report'] = copy.deepcopy(wc['report'])
    expect(out, T('candidate with the parent restore section: own diff'), 'edit.hunk', lambda: AE.own_diff(wp, m, edit))
    # 8 declared address shifted
    expect(out, T('declared hunk shifted by one gate: own diff'), 'edit.hunk',
           lambda: AE.own_diff(wp, wc, dict(edit, start=a - 1, stop=a + 1)))
    # 9 ratio 2 in the new block
    two = copy.deepcopy(new)
    two[0][3], two[2][3] = 2 * two[0][3], 2 * two[2][3]
    expect(out, T('new block with ratio 2 (61 += 2*63 ... 61 -= 2*63): net operator'), 'edit.net_operator',
           lambda: AE.net_operator(old, two))
    m = forge(AL.mutant(wc))
    m['restore'][a][3], m['restore'][a + 2][3] = 2 * m['restore'][a][3], 2 * m['restore'][a + 2][3]
    m['cleanup'] = AL.rederive_cleanup(m)
    expect(out, T('new block with ratio 2, cleanup re-derived: forward replay'), 'wc.replay',
           lambda: AL.replay(AL.parse_word(m), False), stage=STAGE_FWD)
    # 10 stale cleanup: accepted by both replays (same net operator), rejected by the literal re-derivation
    m = AL.mutant(wc)
    m['cleanup'] = copy.deepcopy(wp['cleanup'])
    P = AL.parse_word(m)
    fwd_ok = AL.replay(P, False) is not None
    dual_ok = AL.replay(P, True) is not None
    need(fwd_ok and dual_ok, 'control: the stale cleanup must pass both replays (same net operator)')
    expect(out, T('parent cleanup on the candidate (passes both replays): literal cleanup check'), 'words.cleanup',
           lambda: AW.check_cleanup(m), replays_accept=True)
    # 11 edit outside the allowed sections
    m = AL.mutant(wc)
    m['A'][m['prelude_events'] + 5][-1] = list(FULL)
    expect(out, T('one A gate frame changed as well: own diff'), 'edit.sections', lambda: AE.own_diff(wp, m, edit))
    # 12 extra gate elsewhere in restore (length changes), and a same-length change outside the hunk
    m = AL.mutant(wc)
    m['restore'].append(copy.deepcopy(new[2]))
    expect(out, T('a copy of new gate 3 appended to restore: own diff'), 'edit.hunk', lambda: AE.own_diff(wp, m, edit))
    m = AL.mutant(wc)
    m['restore'][100][3] = -m['restore'][100][3]
    expect(out, T('restore gate 100 (outside the hunk) coefficient flipped, same length: own diff'), 'edit.hunk',
           lambda: AE.own_diff(wp, m, edit))
    # 13 declared old block tampered
    bad_old = copy.deepcopy(old)
    bad_old[1][3] = -bad_old[1][3]
    expect(out, T('declared old block with a flipped coefficient: own diff'), 'edit.hunk',
           lambda: AE.own_diff(wp, wc, dict(edit, old=bad_old)))
    # 14 attribution: the symmetric rewrite (63 as carrier) moves the saving to register 61
    F1, F, F3 = AE.ech(new[0][-1]), AE.ech(old[0][-1]), AE.ech(new[2][-1])
    sym, _ = AE.rewrite(wp, a, old[1][2], old[0][2], F1, F, F3, Q(old[1][3], old[1][4]),
                        Q(old[0][3], old[0][4]) / Q(old[1][3], old[1][4]))
    forge(sym)
    expect(out, T('symmetric rewrite (63 as carrier): attribution names 61, not 63'), 'edit.attribution',
           lambda: AE.attribution(chp, chain_of(sym), {1: -2, 2: 1}, [63]))
    expect(out, T('parent against itself: attribution (no delta)'), 'edit.delta',
           lambda: AE.attribution(chp, chp, {1: -2, 2: 1}, [63]))
    # 15 own chain against a recount with one more rank-1 child
    fr2 = dict(frp, paid=dict(frp['paid']))
    fr2['paid'][1] += 1
    expect(out, T('two implementations: vendored recount with one more rank-1 child'), 'edit.two_impl',
           lambda: AE.two_impl(chp, fr2))


def word_controls(tag, wc, wp, declared, expect_counts, out):
    T = lambda n: tagged(tag, n)   # noqa: E731
    n = 2 * V + wc['report']['R']
    restored = set(int(k) for k in wc['helper_final'])
    helper = next(r for r in range(2 * V, n) if r not in set(wc['removed']) and r not in restored)
    buf = n + min(restored)
    # 16 dual-only cleanup mutant: forward and the own tracker accept, the dual replay rejects
    m = AL.mutant(wc)
    m['cleanup'].insert(0, ['add', helper, buf, 1, 1, list(FULL)])
    P = AL.parse_word(m)
    need(AL.replay(P, False) is not None, 'control: the dual-only mutant must pass the forward replay')
    AW.tracker_check(AW.track(m))
    expect(out, T('cleanup prepended with helper %d += zero buffer %d (forward replay and own tracker accept): word '
                  'pipeline, rejected by the dual replay' % (helper, buf)), 'wc.replay',
           lambda: AW.word_pipeline(m, declared, expect_counts), stage=STAGE_DUAL_BUF, forward_and_tracker_accept=True)
    # 17-18 report fields
    m = AL.mutant(wc)
    m['report']['local_profile']['1'] += 1
    expect(out, T('report local_profile with one more rank-1 child'), 'words.report_fields',
           lambda: AW.check_report(AL.parse_word(m), CW.frame_recount(AL.parse_word(m))))
    m = AL.mutant(wc)
    m['report']['width_inventory']['9'] -= 1
    m['report']['width_inventory']['8'] += 1
    expect(out, T('report width_inventory with one width-9 helper counted as width 8'), 'words.report_fields',
           lambda: AW.check_report(AL.parse_word(m), CW.frame_recount(AL.parse_word(m))))
    # 19 declared profile of the parent given for the candidate
    parent_declared = dict(local_profile=wp['report']['local_profile'], width_inventory=wp['report']['width_inventory'])
    expect(out, T('candidate recount against the parent\'s declared profile'), 'words.declared',
           lambda: AW.check_declared(CW.frame_recount(AL.parse_word(wc)), parent_declared))
    # 20 a restore gate outside the hunk dropped (report forged, cleanup re-derived): replay and tracker
    m = forge(AL.mutant(wc))
    del m['restore'][100]
    m['cleanup'] = AL.rederive_cleanup(m)
    expect(out, T('restore gate 100 dropped, report forged, cleanup re-derived: forward replay'), 'wc.replay',
           lambda: AL.replay(AL.parse_word(m), False), stage=STAGE_FWD)
    expect(out, T('restore gate 100 dropped, report forged, cleanup re-derived: own tracker'), 'words.tracker',
           lambda: AW.tracker_check(AW.track(m)))
    # 21 cleanup item moved below FULL
    m = AL.mutant(wc)
    m['cleanup'][0][-1] = list(FULL[:-1])
    expect(out, T('first cleanup item at a rank-8 frame'), 'words.cleanup', lambda: AW.check_cleanup(m))
    # 22 cleanup with its first item dropped
    m = AL.mutant(wc)
    del m['cleanup'][0]
    expect(out, T('first cleanup item dropped: literal cleanup check'), 'words.cleanup', lambda: AW.check_cleanup(m))
    # 23 buffers: a helper_final endpoint removed (its buffer stays in the cleanup)
    m = AL.mutant(wc)
    del m['helper_final'][str(min(restored))]
    expect(out, T('helper_final endpoint %d removed, cleanup kept (its buffer is no longer declared)' % min(restored)),
           'wc.frame', lambda: AW.word_pipeline(m, declared, expect_counts), stage='frame recount')
    # 24 counts
    expect(out, T('expected helper count 409'), 'words.counts',
           lambda: AW.check_counts(AW.counts(AL.parse_word(wc), wc), dict(expect_counts, helpers=409)))


# ------------------------------------------------------------------------------------------------ scope C ---
def fill_controls(ctx, out):
    rows, drows, order, disp, widths, local, sc, R = (ctx[k] for k in ('rows', 'drows', 'order', 'disp', 'widths',
                                                                       'local', 'sc', 'helpers'))
    fam, fam_at, bins, top, wd = AF.fill_index(rows, order, disp, widths, sc)

    def both(name, rule, rr, changes):
        dr = list(drows)
        for q in changes:
            dr[q] = CF.fc_row(rr[q], order, disp, widths, sc['pair_of'], sc['side_of'])
        if len(rr) < len(drows):
            dr = dr[:len(rr)]
        expect(out, name + ' (own check_rows)', rule, lambda: AF.own_rows(rr, order, disp, widths, local, sc, R))
        expect(out, name + ' (vendored fill_check80)', rule, lambda: AF.vendored_rows(dr, order, disp, widths, local,
                                                                                      sc, R))
    both('last fill role dropped', 'R-a.count', rows[:-1], [])
    b = next(b for b in sorted(bins) if len(bins[b]) >= 2)
    q1, q2 = sorted(bins[b], key=lambda k: rows[k][5])[:2]
    rr = list(rows)
    rr[q2] = rows[q2][:5] + [rows[q1][5]]
    both('fill role %d moved onto the offset of role %d in bin %r' % (q2, q1, b), 'R-b.overlap', rr, [q2])
    b = next(b for b in sorted(bins) if top[b][1] + 1 <= sc['rank'][b[1]] and len(bins[b]) >= 2)
    q = top[b][0]
    rr = list(rows)
    rr[q] = rows[q][:5] + [rows[q][5] + 1]
    both('top slice of bin %r lifted by one cell (gap below it)' % (b,), 'R-b.prefix', rr, [q])
    found = None
    for q, (t, h, o, c, p, off) in enumerate(rows):
        s, r = order[t]
        for o2 in range(AF.T):
            lo, hi = sc['win'][o2, c]
            if o2 != o and not lo < t <= hi and (t, fam(o2, c, p)) not in fam_at and not (
                    o2 == r and sc['pair_of'][c] == sc['stage_pair'][s]):
                found = (q, o2)
                break
        if found:
            break
    q, o2 = found
    rr = list(rows)
    rr[q] = [rows[q][0], rows[q][1], o2] + rows[q][3:]
    both('fill role %d re-hosted at owner %d outside its window' % (q, o2), 'R-d.window', rr, [q])
    found = None
    for q, (t, h, o, c, p, off) in enumerate(rows):
        s, r = order[t]
        c2 = next((c2 for c2 in sorted(sc['rank']) if sc['pair_of'][c2] == sc['stage_pair'][s]
                   and (t, fam(r, c2, p)) not in fam_at), None)
        if c2 is not None:
            found = (q, r, c2)
            break
    q, r, c2 = found
    rr = list(rows)
    rr[q] = [rows[q][0], rows[q][1], r, c2] + rows[q][4:]
    both('fill role %d re-hosted on its caller\'s active pair (owner %d, child %d)' % (q, r, c2), 'R-e.active_pair',
         rr, [q])


def pricing_controls(ctx, out):
    pc, pp = ctx['pc'], ctx['pp']
    order, disp, sc, fill = ctx['order'], ctx['disp'], ctx['sc'], ctx['fill']
    profile15, claim15 = ctx['profile15'], ctx['claim15']
    rr, q, desc = AF.legal_move(fill['rows'], order, disp, pc['widths'], sc)
    pm = AF.price(dict(fill, rows=rr), order, disp, ctx['words_c'], ctx['rec_c'], sc)
    need(pm['own']['profile'] != pc['own']['profile'], 'control: the legal move does not change the profile')
    expect(out, 'fill with one legal re-hosting (%s; R-a..R-e pass in both implementations): PROFILE.json' % desc,
           'fill.profile_file', lambda: AF.check_profile(pm['own']['profile'], profile15, 'fill.profile_file'),
           legal_fill_rules_passed=True)
    expect(out, 'fill with one legal re-hosting: idle remainders against PR2979', 'fill.idle',
           lambda: AF.check_idle(pm['own'], pp['own']))
    expect(out, 'fill_check80 result of the re-hosted fill against check_rows of the published fill', 'fill.two_impl',
           lambda: AF.compare_impl(pc['own'], pm['fc']))
    del pm
    expect(out, 'the fill priced with the parent words\' recounts against PR3015\'s CLAIM profile',
           'fill.profile_claim', lambda: AF.check_profile(pp['own']['profile'], claim15['profile'], 'fill.profile_claim'))
    p = dict(profile15, **{'48': profile15['48'] + 1})
    expect(out, 'PROFILE.json with one more rank-48 child', 'fill.profile_file',
           lambda: AF.check_profile(pc['own']['profile'], p, 'fill.profile_file'))
    prof = dict(pc['own']['profile'])
    prof[1] += 1
    expect(out, 'complete profile with one more rank-1 child: rank mass', 'fill.mass', lambda: AF.check_mass(prof))
    expect(out, 'parent against parent with the R1 local delta: complete delta', 'fill.delta',
           lambda: AF.check_delta(pp['own']['profile'], pp['own']['profile'], {1: -2, 2: 1}))
    expect(out, 'complete delta against the local delta with the wrong sign', 'fill.delta',
           lambda: AF.check_delta(pc['own']['profile'], pp['own']['profile'], {1: 2, 2: -1}))
    c = dict(claim15, zero_buffers=90, physical_families=claim15['physical_families'] - 1)
    expect(out, 'CLAIM with 90 private buffers and the stock lowered by one', 'fill.physical',
           lambda: AF.physical(pc['helpers'], pc['buffers'], c))
    expect(out, 'physical stock from one private buffer fewer than the CLAIM', 'fill.physical',
           lambda: AF.physical(pc['helpers'], pc['buffers'] - 1, claim15))
    expect(out, 'dispatch with its last entry dropped', 'fill.dispatch',
           lambda: AF.dispatch_map(ctx['dispatch_list'][:-1], order))
    rec_bad = dict(ctx['rec_c'])
    rec_bad['gauge44'] = dict(rec_bad['gauge44'], helper_widths=[rec_bad['gauge44']['helper_widths'][0] + 1]
                              + list(rec_bad['gauge44']['helper_widths'][1:]))
    expect(out, 'recount with the first helper width raised by one against the word', 'fill.widths',
           lambda: AF.price(fill, order, disp, ctx['words_c'], rec_bad, sc))

    def disagree(fc):
        return dict(fc, profile=dict(fc['profile'], **{'1': fc['profile']['1'] + 1}))
    expect(out, 'vendored implementation\'s profile given one more rank-1 child before the comparison',
           'fill.two_impl', lambda: AF.price(fill, order, disp, ctx['words_c'], ctx['rec_c'], sc, fc_hook=disagree))
    expect(out, 'FILL with its columns reordered', 'fill.format',
           lambda: AF.price(dict(fill, columns=list(reversed(fill['columns']))), order, disp, ctx['words_c'],
                            ctx['rec_c'], sc))
    inv = list(order)
    i, j = inv.index((0, 5)), inv.index((1, 5))
    inv[i], inv[j] = inv[j], inv[i]
    expect(out, 'per-replica stage inversion (replica 5)', 'order.projection',
           lambda: AF.schedule(ctx['tpl'], ctx['t37'], inv))
    k = next(k for k in range(len(order) - 1) if order[k][1] != order[k + 1][1] and
             CF.block_windows(ctx['tpl'], order[:k] + [order[k + 1], order[k]] + order[k + 2:], sc['stage_pair'],
                              sc['rank'])[0] != sc['win'])
    o2 = order[:k] + [order[k + 1], order[k]] + order[k + 2:]
    sched2 = FC.derive_schedule(AF.T, ctx['tpl'], o2)
    expect(out, 'block-rule windows of the order against the event-rule windows of the order swapped at %d' % k,
           'windows.block_vs_event', lambda: CF.windows_agree(sc['win'], sched2))
    src = ctx['tpl']['execution_schedule']
    q = next(q for q, e in enumerate(src[:30]) if e['kind'] == 'bridge')
    tpl_bad = dict(ctx['tpl'], execution_schedule=src[:q] + [dict(src[q], dst_replica=1)] + src[q + 1:])
    expect(out, 'template bridge event %d given a cross-replica field' % q, 'template.cross_replica_field',
           lambda: AF.schedule(tpl_bad, ctx['t37'], order))


# ------------------------------------------------------------------------------------------------ scope D ---
def kappa_controls(ctx, out):
    prof, prof_p = ctx['profile_c'], ctx['profile_p']
    C, C79 = ctx['C'], ctx['C79']
    CA = ctx['CA']
    # each enclosure has its own straddle point (the vendored one is far tighter than the own one)
    for label, mom, S in (('own enclosure', AK.moment, ctx['straddle']), ('vendored enclosure', CA.moment, ctx['straddle_vendored'])):
        for name, a, rule in (('C + 1e-24', C + AK.E24, 'kappa.endpoint_accept'),
                              ('the straddle point S (enclosure contains 1)', S, 'kappa.endpoint_accept'),
                              ('C - 1e-24', C - AK.E24, 'kappa.endpoint_reject'),
                              ('S - 1e-24 (so that S must be rejected)', S - AK.E24, 'kappa.endpoint_reject')):
            expect(out, 'endpoint claimed at %s (%s)' % (name, label), rule, lambda a=a, mom=mom: AK.endpoint_check(prof, a, mom=mom))
    expect(out, 'C with 25 digits', 'kappa.endpoint_format', lambda: AK.endpoint_format(C + Q(1, 10 ** 25)))
    expect(out, 'C = 0', 'kappa.endpoint_format', lambda: AK.endpoint_format(Q(0)))
    k = ctx['kappa']
    expect(out, 'CLAIM kappa + 1e-70', 'kappa.kappa', lambda: AK.kappa_check(k + AK.KAPPA_TERMS[1], C))
    expect(out, 'kappa against C + 1e-70', 'kappa.kappa', lambda: AK.kappa_check(k, C + AK.KAPPA_TERMS[1]))
    gain = ctx['claimed_gain']
    expect(out, 'claimed gain + 1e-24', 'kappa.gain', lambda: AK.gain_check(k, ctx['kappa79'], gain + AK.E24))
    expect(out, 'gain of PR2979 over itself', 'kappa.gain', lambda: AK.gain_check(ctx['kappa79'], ctx['kappa79'], Q(0)))
    expect(out, 'improvement with the new profile in place of the old one', 'kappa.improvement',
           lambda: AK.improvement(prof, prof, C, C79))
    expect(out, 'improvement with the roles of the two claims swapped', 'kappa.improvement',
           lambda: AK.improvement(prof, prof_p, C79, C))

    def shifted(p, a):
        lo, hi = CA.moment(p, a)
        return lo + Q(1, 10 ** 20), hi + Q(1, 10 ** 20)
    expect(out, 'vendored enclosure shifted by 1e-20 (disjoint from the own one, verdict changes)', 'kappa.two_impl',
           lambda: AK.two_impl(prof, C, shifted))

    def shifted_down(p, a):
        lo, hi = CA.moment(p, a)
        return lo - Q(1, 10 ** 50), hi - Q(1, 10 ** 50)
    expect(out, 'vendored enclosure shifted by -1e-50 (disjoint from the own one, same verdict)', 'kappa.two_impl',
           lambda: AK.two_impl(prof, C, shifted_down))
    expect(out, 'prediction started from a C above the root', 'kappa.predict',
           lambda: AK.predict_endpoint(prof, C + AK.E24))
    bad = dict(prof)
    bad[1] = -1
    expect(out, 'profile with a negative count', 'kappa.profile', lambda: AK.moment(bad, C))
    expect(out, 'profile with a rank-73 child', 'kappa.profile', lambda: AK.moment(dict(list(prof.items()) + [(73, 1)]), C))


# ------------------------------------------------------------------------------------------------ scope E ---
def journal_controls(ctx, out):
    fill, edits = ctx['fill'], ctx['edits']
    e = copy.deepcopy(edits)
    e[0][1][5] += 1
    expect(out, 'journal edit 0 with its preimage offset raised by one', 'journal.preimage',
           lambda: AF.apply_journal(fill, e))
    e = copy.deepcopy(edits)
    e.append(copy.deepcopy(edits[0]))
    expect(out, 'journal with its first edit repeated', 'journal.index', lambda: AF.apply_journal(fill, e))
    e = copy.deepcopy(edits)
    e[0][2][1] += 1
    expect(out, 'journal edit 0 whose new row changes the helper', 'journal.row', lambda: AF.apply_journal(fill, e))
    prof = dict(ctx['profile_j'])
    prof[13] = prof.pop(14)
    expect(out, 'journaled profile against PR3018\'s RESULT profile with its rank-14 child at rank 13',
           'journal.profile', lambda: AF.check_profile(prof, ctx['result18']['profile'], 'journal.profile'))
    fj, _ = AF.apply_journal(fill, edits[:-1])
    expect(out, 'journal with its last edit dropped: the fill priced', ctx['last_edit_dropped_rule'],
           lambda: AF.price(fj, ctx['order'], ctx['disp'], ctx['words_p'], ctx['rec_p'], ctx['sc']))
