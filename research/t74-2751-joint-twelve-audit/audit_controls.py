# SPDX-License-Identifier: Apache-2.0
"""Negative controls of the PR #2751 audit.  Every control builds one mutant (a changed word, fill, published file or
claimed number), runs it through the function the main check uses (the whole word pipeline, scope B's word_diff,
scope C's checks on the mutant's own analysis, scope D's price/pricing_checks, or the single rule function named
in the record), and requires a rejection by exactly the named rule (audit_lib.expect).  Pipeline-level mutants that
are meant to reach a later check are made self-consistent first: their report fields and PROVIDERS entry are
forged to their own recount, and a re-ordered or extended word gets its own re-derived cleanup.  Controls whose
check cannot be reached through the main pipeline (an earlier check rejects every such mutant) run the named rule
function and say so in their name (': check_<name>') or are in a *_function group.  Hypothesis controls assert the
word and the exact list of flipped booleans (expect(..., attrs=...)).
"""
import copy
from collections import Counter

import audit_diff as AD
import audit_lib as AL
import audit_pricing as AP
import audit_reconcile as AR
import audit_words as AW
import check_fill as CF
import check_words as CW
import fill_check80 as FC
import words_check as WC
from audit_common import AuditFail, need

V = AL.V
expect = AL.expect


def climb_split(w):
    """check_words.climb_split_mutant on the word without its corrections, corrections restored afterwards (the
    corrections carry no frame)."""
    w2 = dict(w)
    w2['initial_corrections'] = []
    m, rec = CW.climb_split_mutant(w2)
    m['initial_corrections'] = copy.deepcopy(w['initial_corrections'])
    return m, rec


def forged(m, prov):
    """Forge the mutant's report fields and PROVIDERS entry to its own recount."""
    fr = AL.forge(m)
    return dict(prov, actual_paid_profile=AL.hist(fr['paid']), widths=list(fr['helper_widths']))


def a_block_index(w, lender):
    return next(k for k, g in enumerate(w['A'][:w['prelude_events']]) if g[0] == 'warp' and g[1] == lender and g[2] > 0)


# ------------------------------------------------------------------------------------------------ words ---
def word_controls(tag, w, prov, report33, groups):
    S = AW.SPEC_2751
    pipe, fn, plumb = groups['words_pipeline'], groups['words_function'], groups['plumbing']
    T = '[%s] ' % tag

    def run(m, p=prov):
        return lambda: AW.word_pipeline(m, S, p)

    m = AL.mutant(w)
    m['report']['local_profile'] = report33
    expect(pipe, T + "report.local_profile replaced by PR2733's", 'words.report_fields', run(m), word=tag)
    cs, cs_rec = climb_split(w)
    expect(pipe, T + 'climb-split mutant (one A gate gets an intermediate frame), report unchanged',
           'words.report_fields', run(cs), word=tag, mutant=cs_rec)
    expect(pipe, T + "PROVIDERS entry with PR2733's profile", 'words.providers',
           run(w, dict(prov, actual_paid_profile=report33)), word=tag)
    m = AL.mutant(cs)
    AL.forge(m)
    expect(pipe, T + 'climb-split mutant, report forged to its recount', 'words.providers', run(m), word=tag)
    m = AL.mutant(w)
    del m['start_extra']['640']
    expect(pipe, T + 'helper 640 starts at frame 0 instead of [30] (width 8 -> 9), report and PROVIDERS forged',
           'words.registers', run(m, forged(m, prov)), word=tag)
    m = AL.mutant(w)
    del m['cut'][0]
    expect(pipe, T + 'cut gate 0 dropped (175 cut gates), report and PROVIDERS forged', 'words.cut_census',
           run(m, forged(m, prov)), word=tag)
    m = AL.mutant(w)
    m['cut'][0] = ['add', V + 21] + m['cut'][0][2:]
    expect(pipe, T + 'cut gate 0 retargeted onto lifted target 21, report and PROVIDERS forged', 'words.cut_census',
           run(m, forged(m, prov)), word=tag)
    m = AL.mutant(w)
    m['A'].insert(0, ['scale', V + 2, 1, 1, [45]])
    m['prelude_events'] += 1
    m['target_levels']['2'] = [45]
    expect(pipe, T + 'extra identity lift of the uncut target 2 to [45], report and PROVIDERS forged',
           'words.lifted', run(m, forged(m, prov)), word=tag)
    m = AL.mutant(cs)
    expect(pipe, T + 'climb-split mutant, report and PROVIDERS forged', 'words.profile_claim',
           run(m, forged(m, prov)), word=tag)
    idx = AW.pair_gates(w)
    m = AL.mutant(w)
    m['B'][idx[(33, 49)][0]][4] = 4
    expect(pipe, T + 'recovery 33 += 49/2 -> 33 += 49/4', 'wc.replay', run(m), stage='forward replay, before cleanup',
           word=tag)
    m = AL.mutant(w)
    for c in m['initial_corrections']:
        c['operator_word'] = [-k for k in c['operator_word']]
    expect(pipe, T + 'all 36 initial corrections with K^-1 instead of K', 'wc.replay', run(m),
           stage='forward replay, before cleanup', word=tag)
    m = AL.mutant(w)
    m['initial_corrections'] = m['initial_corrections'][1:]
    expect(pipe, T + 'initial correction #0 dropped', 'words.counts', run(m), word=tag)
    m = AL.mutant(w)
    m['initial_corrections'][0]['source'] = 0
    expect(pipe, T + 'initial correction #0 sourced from X0 (not at frame 0)', 'words.corrections', run(m), word=tag)
    # dual-only: a cleanup item that is a no-op forward and leaves a buffer non-zero in the dual orientation
    P = AL.parse_word(w)
    h = next(r for r in sorted(P['live']) if r >= 2 * V and r not in P['restored'] and P['end'][r] == P['full'])
    b = min(P['buffers'])
    m = AL.mutant(w)
    m['cleanup'] = [['add', h, b, 1, 1, list(w['cleanup'][0][-1])]] + m['cleanup']
    fwd = AL.replay(AL.parse_word(m), False)
    need(fwd['orientation'] == 'forward', 'control: forward replay of the dual-only mutant')
    expect(pipe, T + 'dual-only: cleanup prefixed with H%d += buffer %d (forward replay accepts it)' % (h, b),
           'wc.replay', run(m), stage='dual replay, buffers after cleanup', word=tag, forward_replay_accepted=True)
    m = AL.mutant(w)
    m['warps'][46][4] = list(m['warps'][46][3])
    expect(pipe, T + 'warp record 47: E := U', 'wc.warp', run(m), word=tag)
    m = AL.mutant(w)
    k = a_block_index(m, 33)
    m['A'][k][4] = [30]
    m['A'][k + 5][3] = [30]
    expect(pipe, T + 'A-prelude K_47 of lender 33 sent to line 30 instead of 45', 'wc.warp', run(m), word=tag)
    m = AL.mutant(w)
    regs = lambda g: {g[1], g[2]} if g[0] == 'add' else {g[1]}  # noqa: E731
    k = next(k for k in range(len(m['cleanup']) - 1) if not regs(m['cleanup'][k]) & regs(m['cleanup'][k + 1])
             and m['cleanup'][k] != m['cleanup'][k + 1])
    m['cleanup'][k], m['cleanup'][k + 1] = m['cleanup'][k + 1], m['cleanup'][k]
    expect(pipe, T + 'cleanup items %d and %d (disjoint registers) swapped' % (k, k + 1), 'words.cleanup', run(m),
           word=tag)
    m = AL.mutant(w)
    jx, jy = idx[(74, 83)]
    need(not set(regs(m['B'][jy + 1])) & {74, 83} and not any(rec[0] in (jy + 1, jy + 2) for rec in m['warps']),
         'control: B[%d] does not commute with the 74/83 recovery' % (jy + 1))
    m['B'][jy], m['B'][jy + 1] = m['B'][jy + 1], m['B'][jy]
    m['cleanup'] = AL.rederive_cleanup(m)
    expect(pipe, T + 'recovery 83 -= 74 moved one (commuting) item later, cleanup re-derived', 'words.pairs.adjacent',
           run(m), word=tag)
    hand = dict((rec[1], rec[0]) for rec in w['warps'])
    for (x, y), (jx, jy) in sorted(idx.items()):
        for r in (x, y):
            need(hand[r] > jy + 1, 'control: handoff of %d is not after B[%d]' % (r, jy + 1))
            m = AL.mutant(w)
            F = list(m['B'][jy][-1])
            AL.insert_B(m, jy + 1, [['scale', r, 2, 1, F], ['scale', r, 1, 2, F]])
            m['cleanup'] = AL.rederive_cleanup(m)
            expect(pipe, T + 'no-op %d *= 2; %d *= 1/2 inserted after the %d/%d recovery, cleanup re-derived'
                   % (r, r, x, y), 'words.pairs.untouched', run(m), word=tag)
    # the window's other end: one value-preserving touch as the last B item before the register's handoff K_op
    ops = dict((rec[1], i) for i, rec in enumerate(w['warps'], 1))
    for (x, y), (jx, jy) in sorted(idx.items()):
        for r in (x, y):
            op = ops[r]
            p = w['warps'][op - 1][0]
            need(all(i < op for i, rec in enumerate(w['warps'], 1) if rec[0] == p and i != op),
                 'control: a later warp record shares the handoff position of %d' % r)
            m = AL.mutant(w)
            m['B'].insert(p, ['scale', r, 1, 1, list(m['warps'][op - 1][3])])
            for i, rec in enumerate(m['warps'], 1):
                if rec[0] > p or i == op:
                    rec[0] += 1
            need(m['warps'][op - 1][0] == p + 1 and m['B'][p][:4] == ['scale', r, 1, 1],
                 'control: the identity scale of %d is not B[handoff - 1]' % r)
            m['cleanup'] = AL.rederive_cleanup(m)
            expect(pipe, T + 'identity scale %d *= 1 (frame U of K%d) inserted as the last B item before the handoff '
                   'K%d of %d (pair %d/%d), cleanup re-derived' % (r, op, op, r, x, y), 'words.pairs.untouched',
                   run(m), word=tag)
    # census: only targets_written changes (176 gates kept, nothing lifted written)
    P0 = AL.parse_word(w)
    c0 = AW.cut_census(w, P0)
    written = Counter(g[1] for g in w['cut'])
    k = next(k for k, g in enumerate(w['cut']) if written[g[1]] >= 2)
    free = max(t for t in c0['untouched_targets'] if str(t) not in w['target_levels'])
    m = AL.mutant(w)
    m['cut'][k][1] = V + free
    cm = AW.cut_census(m, AL.parse_word(m))
    changed = sorted(key for key in S['census'] if cm[key] != S['census'][key])
    need(changed == ['targets_written'], 'control: census mutant changes %r' % changed)
    expect(pipe, T + 'cut gate %d moved from a target written twice to the unwritten unlifted target %d (176 gates, '
           '%d targets written), report and PROVIDERS forged' % (k, free, cm['targets_written']), 'words.cut_census',
           run(m, forged(m, prov)), word=tag)

    # function-level controls (the mutant is rejected earlier in the pipeline; the named rule function is run on it)
    m = AL.mutant(w)
    m['A'].insert(0, ['scale', V + 23, 1, 1, [30]])
    m['prelude_events'] += 1
    m['target_levels']['23'] = [30]
    Pm = AL.parse_word(m)
    frm = CW.frame_recount(Pm)
    expect(fn, T + 'identity line-30 lift of target 23 (centres 9 and 240 split): check_centres', 'words.centres',
           lambda: AW.check_centres(AW.centre_paths(Pm, frm), S), word=tag)

    P0 = AL.parse_word(w)
    fr0 = CW.frame_recount(P0)
    expect(fn, T + 'lifted frames checked against line 30 instead of 45: check_lifted', 'words.lifted',
           lambda: AW.check_lifted(P0, AW.lift_climbs(P0, fr0, w['prelude_events']), dict(S, lifted_frame=[30])),
           word=tag)
    expect(fn, T + 'lift climbs located with a zero-length prelude: check_lifted', 'words.lifted',
           lambda: AW.check_lifted(P0, AW.lift_climbs(P0, fr0, 0), S), word=tag)

    def lenders(m):
        return lambda: AW.check_lenders(m, AW.track(m)[0])
    m = AL.mutant(w)
    k = a_block_index(m, 33)
    del m['A'][k + 5]
    m['prelude_events'] -= 1
    expect(fn, T + 'A-prelude inverse K_47^-1 of lender 33 removed: check_lenders', 'words.lenders.count', lenders(m),
           word=tag)
    m = AL.mutant(w)
    AL.delete_B(m, idx[(33, 49)][0])
    expect(fn, T + 'recovery 33 += 49/2 dropped: check_lenders', 'words.lenders.B', lenders(m), word=tag)
    m = AL.mutant(w)
    k = a_block_index(m, 33)
    m['A'][k + 6:k + 6] = [['add', 33, 49, -1, 1, list(m['A'][k][3])]]
    m['A'][k:k] = [['add', 33, 49, 1, 1, list(m['A'][k][3])]]
    m['prelude_events'] += 2
    expect(fn, T + '33 += 49 before its A-prelude K_47 (undone after K_47^-1): check_lenders', 'words.lenders.A',
           lenders(m), word=tag)
    m = AL.mutant(w)
    k = a_block_index(m, 33)
    m['A'][k][2], m['A'][k + 5][2] = 48, -48
    expect(fn, T + 'A-prelude block of lender 33 uses K_48: check_lenders', 'words.lenders.ops', lenders(m), word=tag)
    for r in AW.TWELVE:
        m = AL.mutant(w)
        k = a_block_index(m, r)
        need(m['A'][k + 5][:3] == ['warp', r, -m['A'][k][2]], 'control: A-prelude block of lender %d' % r)
        F = list(m['A'][k][3])
        m['A'][k + 6:k + 6] = [['scale', r, 1, 2, F]]
        m['A'][k:k] = [['scale', r, 2, 1, F]]
        m['prelude_events'] += 2
        expect(fn, T + 'lender %d doubled before its A-prelude K (halved after K^-1): check_lenders' % r,
               'words.lenders.A', lenders(m), word=tag)
        m = AL.mutant(w)
        op = next(i for i, rec in enumerate(m['warps'], 1) if rec[1] == r)
        p = m['warps'][op - 1][0]
        m['B'].insert(p, ['scale', r, 2, 1, list(m['warps'][op - 1][3])])
        for i, rec in enumerate(m['warps'], 1):
            if rec[0] > p or i == op:
                rec[0] += 1
        expect(fn, T + 'lender %d doubled just before its B handoff K%d: check_lenders' % (r, op), 'words.lenders.B',
               lenders(m), word=tag)

    def pairs(m):
        def f():
            Pm = AL.parse_word(m)
            frm = CW.frame_recount(Pm)
            ix = AW.pair_gates(m)
            _, gr, _ = AW.track(m, [j for v in ix.values() for j in v])
            AW.check_pairs(m, Pm, frm, ix, gr)
        return f
    m = AL.mutant(w)
    AL.insert_B(m, 10, [['add', 33, 49, 1, 1, list(m['B'][10][-1])]])
    expect(fn, T + 'an extra B gate 33 += 49: pair_gates', 'words.pairs.gates', lambda: AW.pair_gates(m), word=tag)
    m = AL.mutant(w)
    k = next(k for k, g in enumerate(m['A']) if g[:5] == ['add', 33, 49, -1, 2])
    m['A'][k][4] = 4
    expect(fn, T + 'A gate 33 -= 49/2 (A[%d]) -> 33 -= 49/4: check_pairs' % k, 'words.pairs.prestate', pairs(m),
           word=tag)
    for (x, y), (jx, jy) in sorted(idx.items()):
        F = list(w['B'][jx][-1])
        for r, which in ((x, 'x'), (y, 'y')):
            m = AL.mutant(w)
            AL.insert_B(m, jx, [['scale', r, 2, 1, F]])
            expect(fn, T + 'pair %d/%d: %s row (%d) doubled just before the recovery: check_pairs' % (x, y, which, r),
                   'words.pairs.prestate', pairs(m), word=tag)
        m = AL.mutant(w)
        m['B'][jx][4] = 4
        expect(fn, T + 'recovery %d += %d/2 -> %d += %d/4: check_pairs' % (x, y, x, y), 'words.pairs.restored',
               pairs(m), word=tag)
    m = AL.mutant(w)
    k = next(k for k, g in enumerate(m['cleanup']) if g[0] == 'add' and g[2] < AL.nregs(m))
    m['cleanup'][k][3] = -m['cleanup'][k][3]
    expect(fn, T + 'cleanup add %d (reading a live register) negated: tracker through cleanup' % k, 'words.tracker',
           lambda: AW.tracker_check(AW.track(m)[2]), word=tag)
    # plumbing: a paid climb injected into the recount at each recovery-gate label must be rejected
    P = AL.parse_word(w)
    fr = CW.frame_recount(P)
    _, gr, _ = AW.track(w, [j for v in idx.values() for j in v])
    msgs = []
    for (x, y), js in sorted(idx.items()):
        for j in js:
            bad = dict(fr)
            bad['climbs'] = dict((r, list(lst)) for r, lst in fr['climbs'].items())
            bad['climbs'].setdefault(x, []).append((CW.inserted_gate_label(j, w['warps']), 1))
            AL.AC.attempt('plumbing ' + T + str(j))
            try:
                AW.check_pairs(w, P, bad, idx, gr)
            except AuditFail as e:
                need(str(e).startswith('words.pairs.paid_climbs:'), 'control: injected climb rejected by %s' % e)
                msgs.append(str(e))
                continue
            raise AuditFail('negative control ACCEPTED: climb injected at B[%d]' % j)
    plumb.append(dict(control=T + 'rank-1 paid climb injected at each of the 8 recovery-gate labels in turn',
                      expected='words.pairs.paid_climbs', rejected_by='words.pairs.paid_climbs', injections=len(msgs),
                      word=tag, message=msgs[0][:120]))


# ------------------------------------------------------------------------------------------------- diff ---
def diff_controls(tag, wn, wo, frn, fro, secn, seco, out):
    T = '[%s] ' % tag

    def run(m=wn, o=wo, a=frn, b=fro, sa=secn, sb=seco):
        return lambda: AD.word_diff(m, o, a, b, sa, sb)
    m = AL.mutant(wn)
    m['precondition'][0][3] = -m['precondition'][0][3]
    expect(out, T + 'PR2751 precondition[0] coefficient negated', 'diff.fields', run(m), word=tag)
    m = AL.mutant(wn)
    m['removed'] = [699 if r == 700 else r for r in m['removed']]
    expect(out, T + 'PR2751 removes 699 instead of 700', 'diff.removed', run(m), word=tag)
    m = AL.mutant(wn)
    m['start_extra']['640'] = [31]
    expect(out, T + 'PR2751 helper 640 starts at [31]', 'diff.start_extra', run(m), word=tag)
    m = AL.mutant(wn)
    m['target_levels']['21'] = [44]
    expect(out, T + 'PR2751 target 21 declared at [44]', 'diff.target_levels', run(m), word=tag)
    m = AL.mutant(wn)
    m['report']['width_inventory'] = dict(m['report']['width_inventory'], **{'4': 25})
    expect(out, T + 'PR2751 report.width_inventory changed', 'diff.report', run(m), word=tag)
    m = AL.mutant(wn)
    k = next(k for k in range(m['prelude_events'], len(m['A'])) if m['A'][k][0] == 'add')
    m['A'][k][3] = -m['A'][k][3]
    expect(out, T + 'PR2751 A[%d] (after the prelude) coefficient negated' % k, 'diff.A', run(m), word=tag)
    m = AL.mutant(wn)
    k = AR.p_blocks(m)[55]['start']
    m['A'][k + 1][1] = V + 23
    expect(out, T + 'PR2751 prelude block of 55 writes target 23 instead of 21', 'diff.A', run(m), word=tag)
    m = AL.mutant(wn)
    AL.insert_B(m, 300, [list(m['B'][300])])
    expect(out, T + 'PR2751 B[300] duplicated', 'diff.B', run(m), word=tag)
    m = AL.mutant(wn)
    j = AW.pair_gates(m)[(85, 98)][0]
    m['B'][j][5] = list(m['B'][j][5]) + [1]
    expect(out, T + 'PR2751 recovery gate 85 += 98/2 with one more frame vector (moved gates not literal)', 'diff.B',
           run(m), word=tag)
    m = AL.mutant(wn)
    m['warps'][50][2] = list(m['warps'][49][2])
    expect(out, T + 'PR2751 warp record 51 with the G of record 50', 'diff.warps', run(m), word=tag)
    m = AL.mutant(wn)
    del m['cleanup'][0]
    expect(out, T + 'PR2751 cleanup item 0 dropped', 'diff.cleanup', run(m), word=tag)
    cs, _ = climb_split(wn)
    Pc = AL.parse_word(cs)
    frc = CW.frame_recount(Pc)
    expect(out, T + 'PR2751 recount replaced by its climb-split mutant\'s', 'diff.profile_delta',
           run(a=frc, sa=AW.sections(frc)), word=tag)
    cs, _ = climb_split(wo)
    frc = CW.frame_recount(AL.parse_word(cs))
    expect(out, T + 'PR2733 recount replaced by its climb-split mutant\'s', 'diff.profile_delta',
           run(b=frc, sb=AW.sections(frc)), word=tag)


# -------------------------------------------------------------------------------------------- reconcile ---
def reconcile_controls(tag, ana, pub, echo, raw, out_pipe, out_fn):
    """ana: dict(a96, a33, a51) of the real words; pub: PR2720 RESULT providers[tag]; raw: (PR2720 bytes, PR2696
    bytes)."""
    T = '[%s] ' % tag
    a96, a33, a51 = ana['a96'], ana['a33'], ana['a51']
    w96, w33, w51 = a96['w'], a33['w'], a51['w']

    def run(m96=None, m33=None, m51=None, p=pub, e=echo):
        def f():
            AR.reconcile_checks(AR.analyse(m96) if m96 is not None else a96,
                                AR.analyse(m33) if m33 is not None else a33,
                                AR.analyse(m51) if m51 is not None else a51, p, e)
        return f
    expect(out_fn, T + 'PR2720 input bytes with one extra byte', 'reconcile.pr2720_inputs',
           lambda: AR.check_inputs(raw[0] + b'\n', raw[1]), word=tag)
    expect(out_fn, T + 'PR2696 word bytes with one extra byte', 'reconcile.pr2720_inputs',
           lambda: AR.check_inputs(raw[0], raw[1] + b'\n'), word=tag)

    def blk(w, x, fn):
        return AR.mutate_block(w, x, fn)

    def without(w, t):
        """w with every P-block write to target t removed (all four P blocks)."""
        for x in AR.P_SRC:
            w = blk(w, x, lambda body: [g for g in body if g[1] != V + t])
        return w

    def fr(c):
        return [c.numerator, c.denominator]
    m = blk(w96, 33, lambda body: body + [['add', V + 2, 33, 1, 4, list(body[0][5])]])
    expect(out_pipe, T + 'PR2696 P block of 33 also writes target 2', 'reconcile.Q_support', run(m96=m), word=tag)
    expect(out_pipe, T + 'PR2696 P blocks without their writes to target 23 (support 34,50,108)', 'reconcile.Q_support',
           run(m96=without(w96, 23)), word=tag)
    m = blk(w96, 33, lambda body: [g[:3] + [-g[3]] + g[4:] for g in body])
    expect(out_pipe, T + 'PR2696 P block of 33 negated (det +1/16)', 'reconcile.Q_det', run(m96=m), word=tag)
    p = copy.deepcopy(pub)
    p['determinant'] = '1/16'
    expect(out_pipe, T + 'PR2720 published determinant 1/16', 'reconcile.Q_det', run(p=p), word=tag)
    c55 = AR.p_blocks(w96)[55]['adds']
    m = blk(w96, 33, lambda body: [g[:3] + fr(AL.Fraction(g[3], g[4]) + 2 * c55[g[1] - V]) + g[5:] for g in body])
    expect(out_pipe, T + 'PR2696 P block of 33 plus twice that of 55 (det unchanged)', 'reconcile.Q_matrix',
           run(m96=m), word=tag)
    p = copy.deepcopy(pub)
    p['matrix'] = [list(r) for r in zip(*pub['matrix'])]
    expect(out_pipe, T + 'PR2720 published matrix transposed (det unchanged)', 'reconcile.Q_matrix', run(p=p),
           word=tag)
    m = AL.mutant(w96)
    m['A'].insert(m['prelude_events'], ['add', V + 108, V + 23, 1, 1, [30]])
    expect(out_pipe, T + 'PR2696 with Y108 += Y23 right after the prelude', 'reconcile.Q_cut', run(m96=m), word=tag)
    m = AL.mutant(w96)
    k = next(k for k, g in enumerate(m['cut']) if g[2] == 57 and g[1] == V + int(pub['zero_reader_witnesses']['57']))
    free = [t for t in AW.cut_census(m, AL.parse_word(m))['untouched_targets'] if str(t) not in m['target_levels']]
    m['cut'][k][1] = V + max(free)
    expect(out_pipe, T + 'PR2696 cut gate %d of centre 57 moved to the uncut unlifted target %d' % (k, max(free)),
           'reconcile.zero_readers',
           run(m96=m), word=tag)
    p = copy.deepcopy(pub)
    second = a96['cut']['zero_readers'][57][1]
    p['zero_reader_witnesses'] = dict(pub['zero_reader_witnesses'], **{'57': second})
    expect(out_pipe, T + 'PR2720 zero-reader witness of centre 57 = %d (not the least)' % second,
           'reconcile.zero_readers', run(p=p), word=tag)
    m = AL.mutant(w96)
    targets = [g[1] for g in m['cut'] if g[2] == 9 and str(g[1] - V) in m['target_levels']]
    big = sorted(free)[-len(targets) - 1:-1]
    for g in m['cut']:
        if g[2] == 9 and g[1] in targets:
            g[1] = V + big[targets.index(g[1])]
    expect(out_pipe, T + 'PR2696 cut gates of centre 9 on lifted targets moved to uncut unlifted targets %r' % big,
           'reconcile.cut_floor', run(m96=m), word=tag)
    p = copy.deepcopy(pub)
    p['forced_centres'] = [9, 92, 224]
    expect(out_pipe, T + 'PR2720 published forced centres without 240', 'reconcile.cut_floor', run(p=p), word=tag)
    p = copy.deepcopy(pub)
    p['invoice'] = dict(pub['invoice'], **{'1': pub['invoice']['1'] - 1})
    expect(out_pipe, T + 'PR2720 published invoice with one H1 fewer', 'reconcile.cut_floor', run(p=p), word=tag)
    p = copy.deepcopy(pub)
    t0 = sorted(p['omitted_residual'])[0]
    p['omitted_residual'][t0][0][2] = str(-AL.Fraction(p['omitted_residual'][t0][0][2]))
    expect(out_pipe, T + 'PR2720 published omitted residual of target %s with one sign flipped' % t0,
           'reconcile.residual', run(p=p), word=tag)
    m = AL.mutant(w96)
    k = next(k for k, g in enumerate(m['B']) if g[0] == 'add' and V <= g[1] < 2 * V and g[2] - V in AR.P_TARGETS)
    m['B'][k][3] *= 2
    expect(out_pipe, T + 'PR2696 target-target gate B[%d] reading a P row doubled' % k, 'reconcile.residual',
           run(m96=m), word=tag)
    m = AL.mutant(w96)
    m['B'].insert(len(m['B']) // 2, ['scale', V + 5, 0, 1, None])
    for rec in m['warps']:
        if rec[0] > len(m['B']) // 2:
            rec[0] += 1
    Tm, leaks, _ = AR.continuation(m)
    expect(out_fn, T + 'PR2696 with a zero scale of target 5 in B: check_T', 'reconcile.T_rank',
           lambda: AR.check_T(dict(T=Tm, leaks=leaks)), word=tag)
    m = blk(w96, 33, lambda body: [body[0][:3] + [-body[0][3]] + body[0][4:]] + body[1:])
    am = AR.analyse(m)
    expect(out_fn, T + 'PR2696 E_P and T with the Q of a mutant (one 33 coefficient flipped): check_etq',
           'reconcile.ETQ', lambda: AR.check_etq(a96, 'reconcile.ETQ', q_from=am), word=tag)
    # PR2751 side
    m = blk(w51, 33, lambda body: [g[:1] + [V + 23 if g[1] == V + 21 else g[1]] + g[2:] for g in body])
    expect(out_pipe, T + 'PR2751 P block of 33 writes target 23 instead of 21', 'reconcile.pr2751_zero_on_2720_rows',
           run(m51=m), word=tag)
    m = blk(w51, 33, lambda body: body + [['add', V + 2, 33, 1, 2, list(body[0][5])]])
    expect(out_pipe, T + 'PR2751 P block of 33 also writes target 2', 'reconcile.pr2751_support', run(m51=m), word=tag)
    expect(out_pipe, T + 'PR2751 P blocks without their writes to target 21 (support 37,47,110)',
           'reconcile.pr2751_support', run(m51=without(w51, 21)), word=tag)
    c55 = AR.p_blocks(w51)[55]['adds']
    m = blk(w51, 33, lambda body: [g[:3] + fr(c55[g[1] - V]) + g[5:] for g in body])
    expect(out_pipe, T + 'PR2751 P block of 33 with the coefficients of 55 (rank 3)', 'reconcile.pr2751_rank',
           run(m51=m), word=tag)
    m = blk(w51, 33, lambda body: [g[:3] + [2 * g[3]] + g[4:] for g in body])
    expect(out_pipe, T + 'PR2751 P block of 33 doubled (det 1)', 'reconcile.pr2751_det', run(m51=m), word=tag)
    m = blk(w51, 33, lambda body: [g[:3] + [-g[3]] + g[4:] for g in body])
    expect(out_pipe, T + 'PR2751 P block of 33 negated (det -1/2)', 'reconcile.pr2751_det', run(m51=m), word=tag)
    m = AL.mutant(w51)
    m['cut'][0] = ['add', V + 21] + m['cut'][0][2:]
    expect(out_pipe, T + 'PR2751 cut gate 0 writes target 21', 'reconcile.pr2751_not_cut_written', run(m51=m),
           word=tag)
    m = AL.mutant(w51)
    k = next(k for k, g in enumerate(m['B']) if g[0] == 'add' and V <= g[1] < 2 * V and V <= g[2] < 2 * V)
    m['B'][k][3] *= 2
    expect(out_pipe, T + 'PR2751 target-target gate B[%d] doubled' % k, 'reconcile.T_identical', run(m51=m), word=tag)
    m = blk(w51, 33, lambda body: [body[0][:3] + [-body[0][3]] + body[0][4:]] + body[1:])
    am = AR.analyse(m)
    expect(out_fn, T + 'PR2751 E_P and T with the Q of a mutant (one 33 coefficient flipped): check_etq',
           'reconcile.pr2751_ETQ', lambda: AR.check_etq(a51, 'reconcile.pr2751_ETQ', q_from=am), word=tag)
    expect(out_fn, T + 'PR2751 mutant with one 33 coefficient flipped: check_echo', 'reconcile.echo',
           lambda: AR.check_echo(a96, a33, am, echo), word=tag)
    e = dict(old_alias=echo['old_alias'], new_alias=dict(echo['new_alias']))
    h = AD.NEW_ALIAS[85]
    e['new_alias'][h] = dict((t, -c) for t, c in echo['new_alias'][h].items())
    expect(out_fn, T + 'echo of helper %d negated: check_echo' % h, 'reconcile.echo',
           lambda: AR.check_echo(a96, a33, a51, e), word=tag)
    e = dict(old_alias=dict(echo['old_alias']), new_alias=echo['new_alias'])
    h = AD.OLD_ALIAS[33]
    e['old_alias'][h] = dict((t, 2 * c) for t, c in echo['old_alias'][h].items())
    expect(out_fn, T + 'echo of helper %d doubled: check_echo' % h, 'reconcile.echo',
           lambda: AR.check_echo(a96, a33, a51, e), word=tag)
    hypothesis_controls(T, tag, w33, w51, run, out_pipe, a33['E'])


def hypothesis_controls(T, tag, w33, w51, run, out, E33):
    """One pipeline control per computed PR2720 boolean (reconcile.hypotheses), each asserting the word and the exact
    list of flipped booleans: PR2733 mutants flip one kept boolean of PR2733 (all of which must hold), PR2751
    mutants flip one boolean of PR2751's expected pattern."""
    K = dict((k.split('_')[0], k) for k in AR.EXPECTED_PATTERN_2751)

    def hyp(name, who, keys, **words):
        expect(out, T + name, 'reconcile.hypotheses', run(**words),
               attrs=dict(who=who, flipped=sorted(K[k] for k in keys)), word=tag)
    m = AL.mutant(w33)
    need(m['warps'][46][1] == 33 and m['warps'][46][2] != w51['warps'][46][2], 'control: PR2733 record 47')
    m['warps'][46][2] = copy.deepcopy(w51['warps'][46][2])
    hyp('PR2733 B warp record 47 (lender 33) with PR2751\'s G: only h1a (and h1)', 'PR2733', ['h1', 'h1a'], m33=m)
    m = AL.mutant(w33)
    b = AR.p_blocks(m)[33]
    need(m['A'][b['start']][4] == [30], 'control: PR2733 P block of 33 line')
    m['A'][b['start']][4] = [45]
    m['A'][b['end']][3] = [45]
    hyp('PR2733 A-prelude block of 33 sends its port to line 45, adds unchanged: only h1b (and h1)', 'PR2733',
        ['h1', 'h1b'], m33=m)
    m = AL.mutant(w33)
    need(AD.OLD_ALIAS[33] in m['removed'], 'control: PR2733 removes 640')
    m['removed'] = [r for r in m['removed'] if r != AD.OLD_ALIAS[33]]
    hyp('PR2733 with helper %d not removed (33 aliases no removed helper): only h1c (and h1)' % AD.OLD_ALIAS[33],
        'PR2733', ['h1', 'h1c'], m33=m)
    m = AL.mutant(w33)
    pe = m['prelude_events']
    extra, cancel = AR.k_block(m, 33, 2, 1, 4), AR.k_block(m, 33, 2, -1, 4)
    m['A'][pe:pe] = cancel
    m['A'][0:0] = extra
    m['prelude_events'] += len(extra)
    hyp('PR2733 with an extra compensation term K47 x33/4 on target 2 at the A boundary (cancelled right after it): '
        'only h2a', 'PR2733', ['h2a'], m33=m)
    m = AL.mutant(w33)
    extra, cancel = AR.k_block(m, 33, 23, 1, 8), AR.k_block(m, 33, 23, -1, 8)
    m['A'][pe:pe] = cancel
    m['A'][0:0] = extra
    m['prelude_events'] += len(extra)
    hyp('PR2733 with an extra compensation term K47 x33/8 on target 23 at the A boundary (support unchanged, Q '
        'changed; cancelled right after it): only h2a', 'PR2733', ['h2a'], m33=m)
    m = AL.mutant(w33)
    k = len(m['B']) // 2
    F = list(m['B'][k][-1])
    AL.insert_B(m, k, [['add', 0, V + 5, 1, 1, F], ['add', 0, V + 5, -1, 1, F]])
    hyp('PR2733 with X0 += Y5; X0 -= Y5 inserted at B[%d] (target read into a non-target, T unchanged): only h2b' % k,
        'PR2733', ['h2b'], m33=m)
    m = AL.mutant(w33)
    z = min(int(h) for h in m['helper_final']) + AL.nregs(m)
    AL.insert_B(m, k, [['add', z, V + 5, 1, 1, F], ['scale', V + 5, 0, 1, F], ['add', V + 5, z, 1, 1, F],
                       ['add', z, V + 5, -1, 1, F]])
    hyp('PR2733 with Y5 parked in buffer %d, scaled by 0 and restored at B[%d] (T unchanged): h2c, and h2b by the '
        'target reads' % (z, k), 'PR2733', ['h2b', 'h2c'], m33=m)
    m = AL.mutant(w33)
    pe = m['prelude_events']
    m['A'][pe:pe] = AR.k_block(m, 33, 2, 1, 4)
    hyp('PR2733 with an uncancelled K47 x33/4 on target 2 just after the A boundary: only h3', 'PR2733', ['h3'], m33=m)
    # E_P values changed on the same support: T maps x33/16 on target 108 and -x33/16 on target 23 to x33/8 on row 23
    m = AL.mutant(w33)
    m['A'][pe:pe] = AR.k_block(m, 33, 108, 1, 16) + AR.k_block(m, 33, 23, -1, 16)
    E0, Em = E33, AR.analyse(m)['E']
    sup = lambda E: sorted((t, k) for t, e in E.items() for k in e)  # noqa: E731
    need(Em != E0 and sup(Em) == sup(E0) and sorted(t for t in E0 if Em[t] != E0[t]) == [23],
         'control: the h3 value mutant does not change E_P on row 23 only, on the same support')
    hyp('PR2733 with uncancelled K47 x33/16 on target 108 and K47 -x33/16 on target 23 just after the A boundary '
        '(E_P row 23 changed, E_P support unchanged): only h3', 'PR2733', ['h3'], m33=m)
    m = AL.mutant(w51)
    free = AW.cut_census(m, AL.parse_word(m))['untouched_targets']
    m['cut'][0][1] = V + max(t for t in free if str(t) not in m['target_levels'])
    hyp('PR2751 cut gate 0 moved to an untouched unlifted target: only the cut incidences', 'PR2751', ['cut'], m51=m)
    m = AL.mutant(w51)
    q = m['centers'][0]
    readers = sorted(set(g[1] - V for g in m['cut'] if g[2] == q))
    for t in readers:
        m['target_levels'][str(t)] = [45]
    hyp('PR2751 with every target written by centre %d declared at [45] (no zero reader): only the zero readers' % q,
        'PR2751', ['zero'], m51=m)
    m = AL.mutant(w51)
    m['center_frames'][0] = m['center_frames'][0][:-1]
    need(len(WC.span(m['center_frames'][0])) == 7, 'control: rank-7 centre frame')
    hyp('PR2751 centre %d frame with one vector dropped (rank 7): only the rank-8 producers' % m['centers'][0],
        'PR2751', ['rank8'], m51=m)
    m = AL.mutant(w51)
    for t in AR.P_TARGETS:
        m['A'].insert(0, ['scale', V + t, 1, 1, [30]])
        m['target_levels'][str(t)] = [30]
    m['prelude_events'] += len(AR.P_TARGETS)
    hyp('PR2751 with line-30 lifts of 23,34,50,108: only the line-30 cut frames', 'PR2751', ['line30'], m51=m)
    m = AL.mutant(w33)
    need(m['target_levels']['23'] == [30], 'control: PR2733 target 23 at [30]')
    m['target_levels']['23'] = [45]
    hyp('PR2733 with target 23 declared at [45] instead of [30]: only the line-30 cut frames', 'PR2733', ['line30'],
        m33=m)


def quote_controls(readme, recon, quotes, out):
    """reconcile.quotes on mutated README text and reconcile.providers on differing provider booleans (function
    level: the README is a pinned input and the providers' booleans are computed)."""
    expect(out, 'PR2720 README with one line inserted at the top: check_quotes', 'reconcile.quotes',
           lambda: AR.check_quotes('\n' + readme))
    lines = readme.split('\n')
    padded = [(q, a, b + 1, t) if q == 'h3' else (q, a, b, t) for q, a, b, t in AR.PR2720_QUOTES]
    need(not lines[36].strip() and any(q == 'h3' and b == 37 for q, a, b, t in padded),
         'control: PR2720 README line 37 is not blank')
    expect(out, 'hypothesis 3 cited as README lines 33-37 (padded with the blank line 37, same normalised text): '
           'check_quotes', 'reconcile.quotes', lambda: AR.check_quotes(readme, quotes=padded))
    txt = readme.replace('use only original R inputs', 'use only original P inputs')
    need(txt != readme, 'control: hypothesis 2 clause not found')
    expect(out, 'PR2720 README hypothesis 2 reading "use only original P inputs": check_quotes', 'reconcile.quotes',
           lambda: AR.check_quotes(txt))
    txt = readme.replace('a chart of that input', 'a copy of that input')
    need(txt != readme and all('chart of that input' not in c for _, _, c, _ in AR.HYPOTHESIS_CLAUSES),
         'control: hypothesis 1 wording outside the clauses not found')
    expect(out, 'PR2720 README hypothesis 1 reading "a copy of that input" (outside every evaluated clause): '
           'check_quotes', 'reconcile.quotes', lambda: AR.check_quotes(txt))
    bad = [(k, q, c.replace('original R inputs', 'original P inputs'), h) for k, q, c, h in AR.HYPOTHESIS_CLAUSES]
    expect(out, 'hypothesis 2a clause misquoted as "use only original P inputs": check_quotes', 'reconcile.quotes',
           lambda: AR.check_quotes(readme, clauses=bad))
    bad = [(q, c.replace('descending', 'ascending'), st) for q, c, st in AR.PREMISES_NOT_EVALUATED]
    expect(out, 'premise misquoted as "the ascending private-copy model": check_quotes', 'reconcile.quotes',
           lambda: AR.check_quotes(readme, premises=bad))
    rx = dict(recon, extra=dict(recon['extra'], pr2751=dict(recon['extra']['pr2751'], hypotheses=dict(
        recon['extra']['pr2751']['hypotheses'], rank8_producers=False))))
    expect(out, 'extra provider with rank8_producers false for PR2751: reconciliation_record', 'reconcile.providers',
           lambda: AR.reconciliation_record(quotes, rx))


def wiring_controls(words, expected_checks, out):
    """words.wiring on provider records whose word spec differs (self-check of verify.py's wiring), and
    self_checks.ran on a registry with one check missing."""
    counts = dict(expected_checks)
    del counts['words.wiring']
    expect(out, 'self-check registry without words.wiring: check_self_checks', 'self_checks.ran',
           lambda: AL.check_self_checks(counts, expected_checks))
    recs = dict((t, words[t]['pr2751']) for t in words)
    bad = dict(recs, extra=dict(recs['extra'], claims_checked=[k for k in recs['extra']['claims_checked']
                                                               if k != 'census']))
    expect(out, 'extra provider ran without the census claim: check_wiring', 'words.wiring',
           lambda: AW.check_wiring(bad))
    bad = dict(recs, extra=dict(recs['extra'], spec_sha256=AL.sha(dict(AW.SPEC_2751, census=dict(cut_gates=176)))))
    expect(out, 'extra provider ran a weakened census spec (same claim keys): check_wiring', 'words.wiring',
           lambda: AW.check_wiring(bad))
    expect(out, 'only the base provider ran: check_wiring', 'words.wiring',
           lambda: AW.check_wiring(dict(base=recs['base'])))


# ---------------------------------------------------------------------------------------------- pricing ---
def fill_controls(ctx, out):
    """ctx: the PR2751 pricing context (rows, drows, order, disp, widths, local, sc, helpers).  Each fill mutant
    breaks exactly one rule and must be rejected by it in both implementations."""
    rows, drows, order, disp, widths, local, sc, R = (ctx[k] for k in ('rows', 'drows', 'order', 'disp', 'widths',
                                                                       'local', 'sc', 'helpers'))
    fam, fam_at, bins, top, wd = AP.fill_index(rows, order, disp, widths, sc)

    def both(name, rule, rr, changes):
        dr = list(drows)
        for q in changes:
            dr[q] = CF.fc_row(rr[q], order, disp, widths, sc['pair_of'], sc['side_of'])
        if len(rr) < len(drows):
            dr = dr[:len(rr)]
        expect(out, name + ' (own check_rows)', rule, lambda: AP.own_rows(rr, order, disp, widths, local, sc, R))
        expect(out, name + ' (vendored fill_check80)', rule, lambda: AP.vendored_rows(dr, order, disp, widths, local,
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
        for o2 in range(AP.T):
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


def legal_move(rows, order, disp, widths, sc):
    """A fill that still satisfies R-a..R-e but has a different idle histogram: the top slice of a bin with at least
    two slices moves to an empty bin of the same owner and child (same window, same family pair), on a port whose
    family is free in that call.  Returns (rows, changed index, description)."""
    fam, fam_at, bins, top, wd = AP.fill_index(rows, order, disp, widths, sc)
    for b in sorted(bins):
        if len(bins[b]) < 2:
            continue
        q = top[b][0]
        t, h, o, c, p, off = rows[q]
        w = wd(rows[q])
        for p2 in range(V):
            if (o, c, p2) not in bins and (t, fam(o, c, p2)) not in fam_at and w <= sc['rank'][c]:
                rr = list(rows)
                rr[q] = [t, h, o, c, p2, 0]
                return rr, q, 'top slice of bin %r (width %d) moved to the empty bin %r' % (b, w, (o, c, p2))
    raise AuditFail('control: no legal move found')


def pricing_controls(ctx, out):
    """ctx: everything the pricing pipeline used (see verify.py)."""
    p51, p33 = ctx['p51'], ctx['p33']
    claim51, profile51, claim33 = ctx['claim51'], ctx['profile51'], ctx['claim33']
    args = (claim51, profile51, claim33, ctx['local_delta'], ctx['readme51'], ctx['phys_counts'])
    order, disp, sc = ctx['order51'], ctx['disp51'], ctx['sc51']

    # the complete profile: a legal re-hosting changes it (computed side), CLAIM/PROFILE changed (published side)
    rr, q, desc = legal_move(ctx['fill51']['rows'], order, disp, p51['widths'], sc)
    p51m = AP.price(dict(ctx['fill51'], rows=rr), order, disp, ctx['words51'], ctx['recounts51'], sc)
    need(p51m['own']['profile'] != p51['own']['profile'], 'control: the legal move does not change the profile')
    expect(out, 'PR2751 fill with one legal re-hosting (%s; R-a..R-e pass in both implementations)' % desc,
           'pricing.profile_claim', lambda: AP.pricing_checks(p51m, p33, *args), legal_fill_rules_passed=True)
    expect(out, 'fill_check80 result of the re-hosted fill against check_rows of the published fill',
           'pricing.two_impl', lambda: AP.compare_impl(p51['own'], p51m['fc']))
    del p51m                       # each re-priced fill is released before the next one (peak memory)

    def disagree(fc):
        return dict(fc, profile=dict(fc['profile'], **{'1': fc['profile']['1'] + 1}))
    expect(out, 'PR2733 fill priced through price() with the vendored implementation\'s profile given one more rank-1 '
           'child', 'pricing.two_impl', lambda: AP.price(ctx['fill33'], ctx['order33'], ctx['disp33'], ctx['words33'],
                                                         ctx['recounts33'], ctx['sc33'], fc_hook=disagree))
    four = dict(pr2751=p51, pr2733=p33, pr2766=p51, pr2767=p33)
    expect(out, 'PR2733 pricing record without its two-implementation comparison: check_two_impl_ran',
           'pricing.two_impl_ran', lambda: AP.check_two_impl_ran(dict(four, pr2733=dict(p33, two_impl=None))))
    expect(out, 'only PR2751 and PR2733 priced: check_two_impl_ran', 'pricing.two_impl_ran',
           lambda: AP.check_two_impl_ran(dict(pr2751=p51, pr2733=p33)))
    p = dict(profile51, **{'48': profile51['48'] + 1})
    expect(out, 'PR2751 PROFILE.json with one more rank-48 child', 'pricing.claim_files',
           lambda: AP.pricing_checks(p51, p33, claim51, p, *args[2:]))
    c = dict(claim51, profile=dict(claim51['profile'], **{'48': claim51['profile']['48'] + 1}))
    expect(out, 'PR2751 CLAIM.json and PROFILE.json both with one more rank-48 child', 'pricing.profile_claim',
           lambda: AP.pricing_checks(p51, p33, c, c['profile'], *args[2:]))
    prof = dict(p51['own']['profile'])
    prof[1] += 1
    expect(out, 'complete profile with one more rank-1 child: check_mass', 'pricing.mass', lambda: AP.check_mass(prof))
    rr, q, desc = legal_move(ctx['fill33']['rows'], ctx['order33'], ctx['disp33'], p33['widths'], ctx['sc33'])
    p33m = AP.price(dict(ctx['fill33'], rows=rr), ctx['order33'], ctx['disp33'], ctx['words33'], ctx['recounts33'],
                    ctx['sc33'])
    expect(out, 'PR2733 fill with one legal re-hosting (%s)' % desc, 'pricing.idle_identical',
           lambda: AP.pricing_checks(p51, p33m, *args))
    del p33m
    cs, rec = climb_split(ctx['words33']['gauge44'])
    rec33 = dict(ctx['recounts33'], gauge44=CW.frame_recount(AL.parse_word(cs)))
    p33c = AP.price(ctx['fill33'], ctx['order33'], ctx['disp33'], ctx['words33'], rec33, ctx['sc33'])
    expect(out, 'PR2733 priced with the local profile of its climb-split base word', 'pricing.delta',
           lambda: AP.pricing_checks(p51, p33c, *args))
    del p33c
    txt = ctx['readme51'].replace('physical66801', 'physical66802')
    need(txt != ctx['readme51'], 'control: README stock statement not found')
    expect(out, 'PR2751 README stock statement 66802', 'pricing.physical',
           lambda: AP.pricing_checks(p51, p33, claim51, profile51, claim33, ctx['local_delta'], txt,
                                     ctx['phys_counts']))
    m = AL.mutant(ctx['words51']['gauge44'])
    del m['helper_final'][sorted(m['helper_final'], key=int)[0]]
    widths, ended = CF.word_widths(m)
    expect(out, 'stock from a word with one private buffer fewer: physical', 'pricing.physical',
           lambda: AP.physical((len(widths), len(ended)), ctx['readme51']))
    prof51 = p51['own']['profile']
    C, S = ctx['C'], ctx['straddle']
    for name, a, rule in (('C + 1e-24', C + AP.E24, 'pricing.endpoint_accept'),
                          ('the straddle point S (enclosure contains 1)', S, 'pricing.endpoint_accept'),
                          ('C - 1e-24', C - AP.E24, 'pricing.endpoint_reject'),
                          ('S - 1e-24 (so that S must be rejected)', S - AP.E24, 'pricing.endpoint_reject')):
        expect(out, 'endpoint claimed at %s' % name, rule, lambda a=a: AP.endpoint_check(prof51, a, a + AP.E24))
    c = dict(claim51, complex_upper=str(AL.Fraction(claim51['complex_upper']) + AL.Fraction(1, 10 ** 25)))
    expect(out, 'CLAIM complex_upper + 1e-25', 'pricing.endpoint_format',
           lambda: AP.pricing_checks(p51, p33, c, *args[1:]))
    c = dict(claim51, complex_lower=str(C - AL.Fraction(1, 10 ** 25)))
    expect(out, 'CLAIM complex_lower - 1e-25 (25 digits)', 'pricing.endpoint_format',
           lambda: AP.pricing_checks(p51, p33, c, *args[1:]))
    expect(out, 'FILL with its columns reordered', 'pricing.fill_format',
           lambda: AP.price(dict(ctx['fill51'], columns=list(reversed(ctx['fill51']['columns']))), order, disp,
                            ctx['words51'], ctx['recounts51'], sc))
    k = AL.Fraction(claim51['kappa'])
    expect(out, 'CLAIM kappa + 1e-70', 'pricing.kappa', lambda: AP.kappa_check(k + AP.KAPPA_TERMS[1], C))
    expect(out, 'kappa against C + 1e-70', 'pricing.kappa', lambda: AP.kappa_check(k, C + AP.KAPPA_TERMS[1]))
    C33 = AL.Fraction(claim33['complex_lower'])
    expect(out, 'PR2751 profile in place of PR2733 at PR2751 C: check_improvement', 'pricing.improvement',
           lambda: AP.check_improvement(prof51, prof51, C, C33))
    # PR2733's head refit (a63c55ff)
    ch, H33 = ctx['claim_head'], ctx['H2733']
    expect(out, 'PR2733 head CLAIM with PR2751\'s complete profile (accepted at PR2751 C)', 'pricing.head_rejected',
           lambda: AP.head_comparison(prof51, dict(ch, global_profile=AL.hist(prof51)), C, H33))
    expect(out, 'PR2733 head CLAIM complex_lower = PR2751 C + 1e-24', 'pricing.head_gap',
           lambda: AP.head_comparison(prof51, dict(ch, complex_lower=str(C + AP.E24)), C, H33))
    gp = dict(ch['global_profile'])
    gp['8'], gp['7'] = gp['8'] - 1, gp['7'] + 1
    expect(out, 'PR2733 head profile with one rank-8 child at rank 7', 'pricing.head_delta',
           lambda: AP.head_comparison(prof51, dict(ch, global_profile=gp), C, H33))
    expect(out, 'PR2733 head CLAIM compared against another commit', 'pricing.head_claim',
           lambda: AP.head_comparison(prof51, dict(ch, comparison=dict(ch['comparison'], head='0' * 40)), C, H33))
    # schedule, order, template, dispatch, widths
    inv = list(order)
    i, j = inv.index((0, 5)), inv.index((1, 5))
    inv[i], inv[j] = inv[j], inv[i]
    expect(out, 'per-replica stage inversion (replica 5)', 'order.projection',
           lambda: AP.schedule(ctx['tpl'], ctx['t37'], inv))
    k = next(k for k in range(len(order) - 1) if order[k][1] != order[k + 1][1] and
             CF.block_windows(ctx['tpl'], order[:k] + [order[k + 1], order[k]] + order[k + 2:], sc['stage_pair'],
                              sc['rank'])[0] != sc['win'])
    o2 = order[:k] + [order[k + 1], order[k]] + order[k + 2:]
    sched2 = FC.derive_schedule(AP.T, ctx['tpl'], o2)
    expect(out, 'block-rule windows of the order against the event-rule windows of the order swapped at %d' % k,
           'windows.block_vs_event', lambda: CF.windows_agree(sc['win'], sched2))
    src = ctx['tpl']['execution_schedule']
    q = next(q for q, e in enumerate(src[:30]) if e['kind'] == 'bridge')
    tpl_bad = dict(ctx['tpl'], execution_schedule=src[:q] + [dict(src[q], dst_replica=1)] + src[q + 1:])
    expect(out, 'template bridge event %d given a cross-replica field' % q, 'template.cross_replica_field',
           lambda: AP.schedule(tpl_bad, ctx['t37'], order))
    expect(out, 'dispatch with its last entry dropped', 'pricing.dispatch',
           lambda: AP.dispatch_map(ctx['dispatch51'][:-1], order))
    expect(out, 'PR2751 words priced with the PR2733 recounts', 'pricing.widths',
           lambda: AP.price(ctx['fill51'], order, disp, ctx['words51'], ctx['recounts33'], sc))


def others_controls(ctx, out):
    import audit_others as AO
    p66, p67 = ctx['p66'], ctx['p67']
    raw = dict(ctx['raw66'], fill=ctx['raw66']['fill'] + b'\n')
    expect(out, '#2766 vendored FILL bytes with one extra byte', 'others.inputs',
           lambda: AO.check_inputs(raw, ctx['raw51']))
    m = AL.mutant(ctx['words67']['gauge44'])
    m['report']['local_profile'] = dict(m['report']['local_profile'], **{'1': m['report']['local_profile']['1'] + 1})
    expect(out, '#2767 base word report.local_profile with one more rank-1 child', 'others.report_fields',
           lambda: AO.recount(m))
    rr, q, desc = legal_move(ctx['fill67']['rows'], ctx['order67'], ctx['disp67'], p67['widths'], ctx['sc67'])
    p67m = AP.price(dict(ctx['fill67'], rows=rr), ctx['order67'], ctx['disp67'], ctx['words67'], ctx['recounts67'],
                    ctx['sc67'])
    expect(out, '#2767 fill with one legal re-hosting (%s)' % desc, 'others.identical',
           lambda: AO.others_checks(p66, p67m, ctx['claim66'], ctx['profile67']))
    prof = dict(ctx['profile67'], **{'48': ctx['profile67']['48'] + 1})
    expect(out, '#2767 new/PROFILE.json with one more rank-48 child', 'others.declared',
           lambda: AO.others_checks(p66, p67, ctx['claim66'], prof))
    c = dict(ctx['claim66'], profile=dict(ctx['claim66']['profile'], **{'48': ctx['claim66']['profile']['48'] + 1}))
    expect(out, '#2766 CLAIM.json profile with one more rank-48 child', 'others.declared',
           lambda: AO.others_checks(p66, p67, c, ctx['profile67']))
    p33, top67, new67, commit33 = ctx['p33'], ctx['profile67_top'], ctx['profile67'], ctx['commit33']
    prof33, prof67 = p33['own']['profile'], p67['own']['profile']
    top = dict(top67, **{'1': top67['1'] + 1})
    expect(out, '#2767 top-level PROFILE.json with one more rank-1 child', 'others.pr2767_top_profile',
           lambda: AO.check_pr2767_profiles(top, new67, prof67, prof33, p33, commit33))
    # wiring self-check: the comparator must be scope D's computed PR2733 profile object
    expect(out, '#2767 top-level PROFILE.json compared with itself: check_pr2767_profiles', 'others.pr2767_comparator',
           lambda: AO.check_pr2767_profiles(top67, new67, prof67, top67, p33, commit33))
    expect(out, '#2767 top-level PROFILE.json compared with an int-keyed copy of itself (equal values, not the '
           'computed object): check_pr2767_profiles', 'others.pr2767_comparator',
           lambda: AO.check_pr2767_profiles(top67, new67, prof67, AL.intkeys(top67), p33, commit33))
    expect(out, '#2767 top-level PROFILE.json compared with PR2733 CLAIM.json global_profile (published, not '
           'computed): check_pr2767_profiles', 'others.pr2767_comparator',
           lambda: AO.check_pr2767_profiles(top67, new67, prof67, ctx['claim33']['global_profile'], p33, commit33))
    expect(out, '#2767 top-level PROFILE.json compared with the #2767 pricing record\'s profile: '
           'check_pr2767_profiles', 'others.pr2767_comparator',
           lambda: AO.check_pr2767_profiles(top67, new67, prof67, prof67, p67, commit33))
    expect(out, 'PR2733 pricing record without its two-implementation comparison: check_pr2767_profiles',
           'others.pr2767_comparator',
           lambda: AO.check_pr2767_profiles(top67, new67, prof67, prof33, dict(p33, two_impl=None), commit33))


def downstream_controls(dws, refs, record, prs, out, raws):
    """Scope F: one mutant per rule of downstream_word / downstream_structure (the functions of the main check), on
    the later PRs' words, and the coverage self-check on a record without one PR / one provider.  raws: {input key:
    (bytes, (git blob, sha256) pin)}."""
    import audit_others as AO
    data, _ = raws['w2833_base']
    expect(out, '#2833 base word bytes read against the #2802 base pin: downstream_word', 'downstream.input',
           lambda: AO.downstream_word(data, raws['w2802_base'][1]))
    data = raws['w2751_base'][0]
    expect(out, 'PR2751 base word bytes read against the #2833 base pin: downstream_word', 'downstream.input',
           lambda: AO.downstream_word(data, raws['w2833_base'][1]))
    expect(out, 'PR2751 base word (a copy) checked in place of a later word: downstream_structure',
           'downstream.distinct', lambda: AO.downstream_structure(AL.mutant(refs['base']), refs['base']))
    expect(out, 'PR2751 extra word checked against itself: downstream_structure', 'downstream.distinct',
           lambda: AO.downstream_structure(refs['extra'], refs['extra']))
    rec = dict((k, v) for k, v in record.items() if k != '2833')
    expect(out, 'scope F record without #2833: check_downstream_coverage', 'downstream.coverage',
           lambda: AO.check_downstream_coverage(rec, prs))
    rec = dict(record, **{'2802': dict(record['2802'], words=dict(base=record['2802']['words']['base']))})
    expect(out, 'scope F record with only the base word of #2802: check_downstream_coverage', 'downstream.coverage',
           lambda: AO.check_downstream_coverage(rec, prs))
    m = AL.mutant(dws[2833]['base'])
    j, gx, gy = AO.pair_items(m, 85, 98)
    m['B'][j][5] = list(gx[5]) + [1]
    expect(out, '#2833 base word: recovery 85 += 98/2 with one more frame vector', 'downstream.pair_frames',
           lambda: AO.downstream_structure(m, refs['base']))
    m2 = AL.mutant(dws[2827]['base'])
    j, gx, gy = AO.pair_items(m2, 74, 83)
    m2['B'][j + 1], m2['B'][j + 2] = m2['B'][j + 2], m2['B'][j + 1]
    expect(out, '#2827 base word: recovery 83 -= 74 moved one item later', 'downstream.pairs',
           lambda: AO.downstream_structure(m2, refs['base']))
    m3 = AL.mutant(dws[2802]['base'])
    k = next(k for k, g in enumerate(m3['A'][:m3['prelude_events']]) if g[0] == 'warp' and g[1] == 55 and g[2] == 48)
    m3['A'][k][4] = [30]
    expect(out, '#2802 base word: A-prelude chart of op 48 sends its port to line 30', 'downstream.charts',
           lambda: AO.downstream_structure(m3, refs['base']))
    m4 = AL.mutant(dws[2818]['extra'])
    m4['warps'][49][2] = list(m4['warps'][48][2])
    expect(out, '#2818 extra word: B record of op 50 with the G of op 49', 'downstream.charts',
           lambda: AO.downstream_structure(m4, refs['extra']))
    m5 = AL.mutant(dws[2824]['extra'])
    del m5['target_levels']['21']
    expect(out, '#2824 extra word without lifted target 21', 'downstream.lifted',
           lambda: AO.downstream_structure(m5, refs['extra']))
