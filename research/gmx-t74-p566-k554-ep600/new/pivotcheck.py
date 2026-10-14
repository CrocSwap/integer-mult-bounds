"""Sign-aware exactness check for pivot-kernel steps (generalises rebuild.py's `inserted_reads_where_pivot_is_initial`).

Correctness of a kernel step rests on EXACT equality of the complete B + early-cleanup map over every register (exact Fractions) and on the
remaining cleanup being identical (both taken unchanged from rebuild.py's `analyse`), plus the real audits. The retained rebuild.py also demands
that every inserted read of the pivot q sees q's initial value (q's row == identity) and that q is written exactly twice. Some pivots (e.g. 554)
are restored by two early-cleanup gates, the second of which is `scale q by -1`, so after the restore q holds -q. A read placed there is still
exact when its coefficient is taken with that sign. This module therefore checks: every inserted read sees q's row = s*I with s in {+1,-1}
(rows(seq[:p])[q] == {q: s}); the map check then proves the coefficients carry the right sign. A negative control (all tail gates with their
coefficients negated, i.e. the sign NOT accounted) must FAIL the map check.
"""
from fractions import Fraction as Q
import copy

def _seq(RB, B1, C1, E1):
    return list(B1) + [C1[i] for i in E1]

def check_signed(RB, name, base, new, edit, q):
    B1, C1, E1 = RB.compile_edits(base, edit)
    res = dict(word=name)
    res['scalar_program_matches'] = (B1 == [RB.ops(g) for g in new['B']] and C1 == [RB.ops(g) for g in new['cleanup']] and E1 == [i for i, U in new['early_cleanup']])
    res['interfaces_identical'] = all(base.get(k) == new.get(k) for k in RB.INTERFACE)
    a = RB.analyse(base, B1, C1, E1, q)
    seq = _seq(RB, B1, C1, E1)
    signs = {}
    for p in a['new_read_positions']:
        row = RB.rows(seq[:p]).get(q, {q: Q(1)})
        signs[p] = (int(row[q]) if (len(row) == 1 and q in row and row[q] in (1, -1)) else None)
    a['inserted_read_signs'] = {str(p): s for p, s in signs.items()}
    a['inserted_reads_see_signed_identity'] = all(s is not None for s in signs.values())
    a['inserted_read_q_rows'] = {str(p): {str(k): str(v) for k, v in RB.rows(seq[:p]).get(q, {q: Q(1)}).items()} for p in signs}
    a['inserted_read_effective_coefficients'] = {str(p): (str(Q(seq[p][3], seq[p][4]) * signs[p]) if signs[p] is not None else None) for p in signs}
    a['exact'] = (a['b_tail_map_rows_differing'] == 0 and a['remaining_cleanup_identical'] and a['inserted_reads_see_signed_identity'])
    res.update(a)
    res['pass'] = res['scalar_program_matches'] and res['interfaces_identical'] and res['exact']
    return res

def _coef(g): return Q(g[3], g[4])

def _set_coef(g, c):
    c = Q(c); g[3], g[4] = c.numerator, c.denominator

def _map_fails(RB, base, ed2, q):
    B1, C1, E1 = RB.compile_edits(base, ed2)
    return RB.analyse(base, B1, C1, E1, q)['b_tail_map_rows_differing'] > 0

def tamper_controls(RB, base, edit, q):
    """Controls that must all FAIL the exact map check: (a) sign not accounted: every new gate's coefficient negated; (b) sign not accounted
    on the tail gates only; (c) each single new gate's coefficient moved by one dyadic step (x2). Returns dict name -> failed(bool); all must be True."""
    out = {}
    def gates(ed): return [g for _, g in ed.get('insert', [])] + [g for _, g in ed.get('tail', [])]
    ed = copy.deepcopy(edit)
    for g in gates(ed): _set_coef(g, -_coef(g))
    out['all_new_gates_sign_flipped'] = _map_fails(RB, base, ed, q)
    if edit.get('tail'):
        ed = copy.deepcopy(edit)
        for _, g in ed['tail']: _set_coef(g, -_coef(g))
        out['tail_gates_sign_flipped'] = _map_fails(RB, base, ed, q)
    n = len(gates(edit))
    for k in range(n):
        ed = copy.deepcopy(edit); g = gates(ed)[k]; _set_coef(g, 2 * _coef(g))
        out['gate%d_coefficient_x2' % k] = _map_fails(RB, base, ed, q)
    return out
