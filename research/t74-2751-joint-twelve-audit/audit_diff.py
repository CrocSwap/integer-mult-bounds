# SPDX-License-Identifier: Apache-2.0
"""Scope B: the exact structural change from PR2733@2761b52b (PR2751's stated comparison base) to PR2751, per word.

word_diff(wn, wo, frn, fro) checks, in this order (rule ids diff.*):
  fields         the differing top-level fields are exactly A, B, base, cleanup, removed, report, start_extra,
                 target_levels and warps (precondition, compensation, cut, restore, initial_corrections, helper_final,
                 centers, center_frames, ports, prelude_events and kind are identical);
  removed        PR2751 removes 696, 697, 698, 700 instead of 640, 641, 642, 644 (the other 61 are common);
  start_extra    the only start-frame changes: 640/641/642/644 live at [30], 696/697/698/700 (formerly [45]) gone;
  target_levels  {23,34,50,108} at [30] are replaced by {21,37,47,110} at [45]; the other eight are unchanged;
  report         only report.local_profile differs;
  A              A after the prelude is identical; the prelude is 12 identity lifts and 12 blocks [K_op, four
                 target adds reading the lender, K_op^-1]; the blocks of 49,83,98,101,68,80,88,31 are unchanged up to
                 order; those of 33,55,74,85 keep their operator and port but move from line 30 on targets
                 {23,34,50,108} to line 45 on targets {21,37,47,110};
  B              with the partner-alias roles renamed (in PR2733, a partner source x acts as helper OLD_ALIAS[x] from
                 its handoff on; in PR2751 it acts as NEW_ALIAS[x]), the edit script against PR2751's B consists of
                 exactly: one echo block of 640/641/642/644 re-instated (replacing two old target gates, which the four
                 new helper sandwiches reproduce exactly), one deleted block of 16 echo reads of 696/697/698/700, the
                 four recovery pairs inserted (each adjacent x += y/2; y -= x) and the same eight gates (literally,
                 frames included) deleted from just before PR2733's partner handoff; the raw edit script, re-applied,
                 reproduces PR2751's B;
  warps          65 records in both; every record keeps its lender; the 61 records of other lenders are unchanged
                 apart from position; the four partner records (ops 47-50) carry new G and E;
  cleanup        both cleanups are their words' own inverse-reverse, so the cleanup changes by exactly the change in
                 non-target B items (+4: the four sandwich gates);
  profile_delta  only the cut section of the recount differs ({1:4,7:4,8:4} -> {8:8}) and the paid-profile delta is
                 exactly {1:-4,7:-4,8:+4} = 4(H8-H7-H1) (PR2751 README, PROOF.md).
It also returns the echo coefficient maps of the two echo blocks, used by scope C (each partner correction equals
the echo of the helper it replaces).
"""
import difflib
import json
from collections import Counter

import audit_lib as AL
import words_check as WC
from audit_common import need

V = AL.V
P_SRC = (33, 55, 74, 85)
OLD_ALIAS = {33: 640, 55: 641, 74: 642, 85: 644}    # PR2733/PR2696: helper role of each partner source
NEW_ALIAS = {33: 696, 55: 697, 74: 698, 85: 700}    # PR2751 (PROOF.md assignments)
PAIRS = ((33, 49), (55, 101), (74, 83), (85, 98))
EXPECTED_FIELDS = ['A', 'B', 'base', 'cleanup', 'removed', 'report', 'start_extra', 'target_levels', 'warps']
EXPECTED_DELTA = {1: -4, 7: -4, 8: 4}


def jd(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def prelude(w):
    """(lifts, blocks) of A[:prelude_events]: lifts [target offset, frame]; blocks {lender: dict(op, U, E, adds)}."""
    A, pe = w['A'], w['prelude_events']
    lifts, blocks, i = [], {}, 0
    while i < pe:
        g = A[i]
        if g[0] == 'scale':
            need(g[2:4] == [1, 1] and V <= g[1] < 2 * V, 'diff.A: prelude item %d is not an identity target lift' % i)
            lifts.append([g[1] - V, g[4]])
            i += 1
            continue
        blk = A[i:i + 6]
        need(len(blk) == 6 and blk[0][0] == 'warp' and blk[0][2] > 0 and blk[5][:3] == ['warp', blk[0][1], -blk[0][2]]
             and blk[5][3:] == blk[0][3:][::-1] and all(x[0] == 'add' and x[2] == blk[0][1] and V <= x[1] < 2 * V
                                                        for x in blk[1:5]),
             'diff.A: prelude block at %d is not [K, 4 target adds, K^-1]' % i)
        need(blk[0][1] not in blocks, 'diff.A: two prelude blocks for lender %d' % blk[0][1])
        blocks[blk[0][1]] = dict(op=blk[0][2], U=blk[0][3], E=blk[0][4], at=i,
                                 adds=sorted([x[1] - V, x[3], x[4], x[5]] for x in blk[1:5]))
        i += 6
    return lifts, blocks


def renamed_B(wo):
    """PR2733's B with the partner-alias roles renamed onto PR2751's naming."""
    hand = dict((rec[1], rec[0]) for rec in wo['warps'] if rec[1] in OLD_ALIAS)
    inv_new = dict((h, x) for x, h in NEW_ALIAS.items())
    out = []
    for i, g in enumerate(wo['B']):
        g = list(g)
        for k in ((1, 2) if g[0] == 'add' else (1,)):
            x = g[k]
            if x in OLD_ALIAS and i >= hand[x]:
                g[k] = OLD_ALIAS[x]
            elif x in inv_new:
                g[k] = inv_new[x]
        out.append(g)
    return out


def block_rows(items):
    """Free-symbol replay of a list of raw items: every touched register starts as its own symbol."""
    regs = sorted(set(r for g in items for r in ((g[1], g[2]) if g[0] == 'add' else (g[1],))))
    rows = dict((r, AL.own_symbol(r)) for r in regs)
    for g in items:
        AL.apply(rows, g)
    return rows


def echo_map(items, helpers):
    """{helper: {target offset: coefficient of the helper's own symbol}} over target rows after the block."""
    rows = block_rows(items)
    out = dict((h, {}) for h in helpers)
    for r, row in rows.items():
        if V <= r < 2 * V:
            for (var, wd), c in row.items():
                if var in out:
                    need(wd == (), 'diff.B: operator word in an echo block')
                    out[var][r - V] = c
    return out


def classify(op, a, b):
    """Kind of one non-equal opcode of the renamed B diff (a: renamed old items, b: new items)."""
    tag = op[0]
    old_al = set(OLD_ALIAS.values())
    if tag == 'replace':
        echo = [g for g in b if g[0] == 'add' and V <= g[1] < 2 * V and g[2] in old_al]
        sand = [g for g in b if g[0] == 'add' and g[1] in old_al and not (V <= g[2] < 2 * V)]
        if (len(echo) + len(sand) == len(b) and all(g[0] == 'add' and V <= g[1] < 2 * V and g[2] not in old_al
                                                     and not (V <= g[2] < 2 * V) for g in a) and echo):
            return 'echo_reinstated'
    if tag == 'delete' and all(g[0] == 'add' and V <= g[1] < 2 * V and g[2] in P_SRC for g in a):
        return 'echo_deleted'
    if tag == 'insert' and len(b) == 2 and (b[0][1], b[0][2]) in PAIRS and b[0][:5] == ['add', b[0][1], b[0][2], 1, 2] \
            and b[1][:5] == ['add', b[0][2], b[0][1], -1, 1]:
        return 'pair_inserted'
    if tag == 'delete' and len(a) % 2 == 0 and a and all(
            (a[k][1], a[k][2]) in PAIRS and a[k][:5] == ['add', a[k][1], a[k][2], 1, 2]
            and a[k + 1][:5] == ['add', a[k][2], a[k][1], -1, 1] for k in range(0, len(a), 2)):
        return 'pairs_deleted'
    return 'OTHER'


def word_diff(wn, wo, frn, fro, secn, seco):
    """The checks of the module docstring on PR2751's word wn against PR2733's word wo (frn, fro: their frame
    recounts; secn, seco: their section splits).  Returns the computed change set."""
    fields = sorted(k for k in set(wn) | set(wo) if wn.get(k) != wo.get(k))
    need(fields == EXPECTED_FIELDS, 'diff.fields: differing fields %r' % fields)
    rem = dict(added=sorted(set(wn['removed']) - set(wo['removed'])),
               dropped=sorted(set(wo['removed']) - set(wn['removed'])),
               common=len(set(wn['removed']) & set(wo['removed'])))
    need(rem['added'] == sorted(NEW_ALIAS.values()) and rem['dropped'] == sorted(OLD_ALIAS.values()),
         'diff.removed: %r' % rem)
    keys = sorted(set(wn['start_extra']) | set(wo['start_extra']), key=int)
    se = [[int(k), wo['start_extra'].get(k), wn['start_extra'].get(k)] for k in keys
          if wo['start_extra'].get(k) != wn['start_extra'].get(k)]
    want_se = sorted([h, None, [30]] for h in OLD_ALIAS.values()) + sorted([h, [45], None] for h in NEW_ALIAS.values())
    need(se == want_se, 'diff.start_extra: %r' % se)
    tl_old = dict((int(k), v) for k, v in wo['target_levels'].items() if wn['target_levels'].get(k) != v)
    tl_new = dict((int(k), v) for k, v in wn['target_levels'].items() if wo['target_levels'].get(k) != v)
    need(tl_old == dict((t, [30]) for t in (23, 34, 50, 108)) and tl_new == dict((t, [45]) for t in (21, 37, 47, 110)),
         'diff.target_levels: removed %r added %r' % (tl_old, tl_new))
    rep = sorted(k for k in set(wn['report']) | set(wo['report']) if wn['report'].get(k) != wo['report'].get(k))
    need(rep == ['local_profile'], 'diff.report: differing report fields %r' % rep)
    pe = wn['prelude_events']
    need(pe == wo['prelude_events'] and wn['A'][pe:] == wo['A'][pe:], 'diff.A: A after the prelude differs')
    lo, bo = prelude(wo)
    ln, bn = prelude(wn)
    need(sorted(bo) == sorted(bn) and len(bn) == 12 and len(ln) == len(lo) == 12, 'diff.A: prelude shape')
    need(sorted(t for t, _ in lo) == sorted(int(k) for k in wo['target_levels']) and
         sorted(t for t, _ in ln) == sorted(int(k) for k in wn['target_levels']), 'diff.A: prelude lifts != lifted set')
    strip = lambda b: dict((k, v) for k, v in b.items() if k != 'at')  # noqa: E731
    unchanged = sorted(L for L in bn if strip(bn[L]) == strip(bo[L]))
    changed = []
    for L in sorted(set(bn) - set(unchanged)):
        o, n = bo[L], bn[L]
        changed.append(dict(lender=L, op=n['op'], port=n['U'], E_old=o['E'], E_new=n['E'],
                            targets_old=sorted(a[0] for a in o['adds']), targets_new=sorted(a[0] for a in n['adds'])))
    need(sorted(c['lender'] for c in changed) == list(sorted(P_SRC)) and all(
        c['op'] == bo[c['lender']]['op'] and c['port'] == bo[c['lender']]['U'] and c['E_old'] == [30]
        and c['E_new'] == [45] and c['targets_old'] == [23, 34, 50, 108] and c['targets_new'] == [21, 37, 47, 110]
        for c in changed), 'diff.A: changed prelude blocks %r' % [c['lender'] for c in changed])
    # B: raw edit script reproduces the new list; renamed edit script is exactly the explained change set
    a_raw, b_raw = [jd(g) for g in wo['B']], [jd(g) for g in wn['B']]
    raw_ops = [o for o in difflib.SequenceMatcher(None, a_raw, b_raw, autojunk=False).get_opcodes() if o[0] != 'equal']
    rebuilt, i = [], 0
    for tag, i1, i2, j1, j2 in raw_ops:
        rebuilt += wo['B'][i:i1] + wn['B'][j1:j2]
        i = i2
    rebuilt += wo['B'][i:]
    need(rebuilt == wn['B'], 'diff.B: raw edit script does not reproduce the new B')
    ren = renamed_B(wo)
    a_ren = [jd(g) for g in ren]
    ops = [o for o in difflib.SequenceMatcher(None, a_ren, b_raw, autojunk=False).get_opcodes() if o[0] != 'equal']
    kinds = []
    for o in ops:
        kinds.append(classify(o, ren[o[1]:o[2]], wn['B'][o[3]:o[4]]))
    count = dict(Counter(kinds))
    need(count == {'echo_reinstated': 1, 'echo_deleted': 1, 'pair_inserted': 4, 'pairs_deleted': 1},
         'diff.B: renamed edit script %r' % count)
    ins = [g for o, k in zip(ops, kinds) if k == 'pair_inserted' for g in wn['B'][o[3]:o[4]]]
    dele = [g for o, k in zip(ops, kinds) if k == 'pairs_deleted' for g in ren[o[1]:o[2]]]
    need(sorted(map(jd, ins)) == sorted(map(jd, dele)) and len(ins) == 8,
         'diff.B: the inserted recovery gates are not the deleted ones (frames included)')
    o_re = [o for o, k in zip(ops, kinds) if k == 'echo_reinstated'][0]
    o_de = [o for o, k in zip(ops, kinds) if k == 'echo_deleted'][0]
    new_blk, old_gates = wn['B'][o_re[3]:o_re[4]], wo['B'][o_re[1]:o_re[2]]
    echo_items = [g for g in new_blk if V <= g[1] < 2 * V and g[2] in OLD_ALIAS.values()]
    need(block_rows(new_blk) == block_rows(old_gates + echo_items),
         'diff.B: the re-instated block is not the old gates plus the echo reads')
    deleted_raw = wo['B'][o_de[1]:o_de[2]]
    need(all(g[2] in NEW_ALIAS.values() for g in deleted_raw), 'diff.B: deleted echo block reads other registers')
    echo_old_alias = echo_map(new_blk, list(OLD_ALIAS.values()))      # in PR2751, where 640.. are live
    echo_new_alias = echo_map(deleted_raw, list(NEW_ALIAS.values()))  # in PR2733, where 696.. are live
    b_edits = [dict(kind=k, op=o[0], old=[o[1], o[2]], new=[o[3], o[4]]) for o, k in zip(ops, kinds)]
    # warps
    need(len(wn['warps']) == len(wo['warps']), 'diff.warps: record count')
    pchanged, moved, same = [], [], []
    for k, (a, b) in enumerate(zip(wo['warps'], wn['warps']), 1):
        need(a[1] == b[1], 'diff.warps: op %d changes its lender' % k)
        if a[1] in P_SRC:
            need(a[2] != b[2] and a[4] != b[4], 'diff.warps: partner op %d keeps its G or E' % k)
            pchanged.append(dict(op=k, lender=b[1], pos=[a[0], b[0]], G_changed=a[2] != b[2], E_old=a[4], E_new=b[4],
                                 U_span_equal=WC.span(a[3]) == WC.span(b[3]),
                                 E_new_contains_45=WC.contains(WC.span([45]), WC.span(b[4])),
                                 E_old_contains_30=WC.contains(WC.span([30]), WC.span(a[4]))))
        else:
            need(a[1:] == b[1:], 'diff.warps: op %d of lender %d changes beyond its position' % (k, a[1]))
            (moved if a[0] != b[0] else same).append(k)
    # cleanup: both are their own inverse-reverse (checked in scope A); the size change is the non-target B change
    nt = lambda B: sum(1 for g in B if not (V <= g[1] < 2 * V))  # noqa: E731
    need([g[:-1] for g in AL.rederive_cleanup(wo)] == [g[:-1] for g in wo['cleanup']] and
         len(wn['cleanup']) - len(wo['cleanup']) == nt(wn['B']) - nt(wo['B']),
         'diff.cleanup: cleanup change %d != non-target B change %d' % (len(wn['cleanup']) - len(wo['cleanup']),
                                                                       nt(wn['B']) - nt(wo['B'])))
    # sections and profile delta
    sec_diff = sorted(k for k in set(secn) | set(seco) if secn.get(k) != seco.get(k))
    delta = AL.counter_delta(frn['paid'], fro['paid'])
    need(sec_diff == ['cut'] and delta == EXPECTED_DELTA, 'diff.profile_delta: differing sections %r, delta %r'
         % (sec_diff, delta))
    return dict(
        fields=fields, removed=rem, start_extra=se, target_levels=dict(removed=sorted(tl_old), added=sorted(tl_new)),
        report_fields=rep, A_after_prelude_identical=wn['A'][pe:] == wo['A'][pe:], prelude_blocks_unchanged=unchanged,
        prelude_blocks_changed=changed, prelude_block_order=dict(old=[L for L, _ in sorted(bo.items(), key=lambda x: x[1]['at'])],
                                                                  new=[L for L, _ in sorted(bn.items(), key=lambda x: x[1]['at'])]),
        B=dict(old=len(wo['B']), new=len(wn['B']), renamed_edits=b_edits, raw_opcodes=len(raw_ops),
               raw_edit_script_sha256=AL.sha([list(o) for o in raw_ops]),
               moved_recovery_gates=[g[:5] for g in ins], echo_block_reinstated_old_gates=[g[:5] for g in old_gates]),
        warps=dict(partner_records=pchanged, moved_only=len(moved), identical=len(same)),
        cleanup=dict(old=len(wo['cleanup']), new=len(wn['cleanup']), nontarget_B=[nt(wo['B']), nt(wn['B'])]),
        sections=dict(differing=sec_diff, cut_old=seco['cut'], cut_new=secn['cut']),
        profile_delta=AL.hist(delta),
        echo=dict(old_alias_in_pr2751=dict((h, AL.canon(m)) for h, m in sorted(echo_old_alias.items())),
                  new_alias_in_pr2733=dict((h, AL.canon(m)) for h, m in sorted(echo_new_alias.items())))), \
        dict(old_alias=echo_old_alias, new_alias=echo_new_alias)
