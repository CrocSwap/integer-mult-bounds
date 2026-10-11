"""Lean texts of the rate lemmas of one unit (library; used by crate.py): the block list, the whole-block
fact, its sharpness, the per-rank fact and its sharpness.  Lean re-checks every number in the generated module.
"""
from fractions import Fraction
import foldlib as fl
from foldlib import frac_lean


NS = 'OAI.PowerSaving.BlockAccounting'


def block_text(name, u, A, B, s):
    P = fl.plan_block(u, A, B, s)
    assert P is not None, 'whole-block fact does not pass the rational check'
    m, W, H = u['m'], u['W'], u['H']
    eps = '%d/(10:ℝ)^%d' % (A, B)
    z = '(1 - %s)' % eps
    blk = 'blocks' + name
    o = []
    o.append('/-- **whole-block fact** of `%s` at exponent `1 - %d/10^%d`, fill parameter `s = %d`: the hypothesis `hnum` of `RAM.engine_program_group_list` (u = %d, W = %d).  Relative slack of the rational certificate: %.2e. -/' % (blk, A, B, s, m, W, P['slack_rel']))
    o.append('theorem fold_%s :' % name)
    o.append('    ((2:ℝ)^%d - 1) * moment %d %s %s' % (s, m, z, blk))
    o.append('      + ((%d:ℕ):ℝ) * (T %d %s (%d - 1) 1 + T %d %s 1 1)' % (W, m, z, m, m, z))
    o.append('      < (2:ℝ)^%d * ((%d:ℕ):ℝ) := by' % (s, W))
    terms = ' + ('.join('T %d %s %d %d' % (m, z, r, H[r]) for r in sorted(H)) + ' + 0' + ')' * (len(H) - 1)
    o.append('  have hsum : moment %d %s %s\n      = %s := rfl' % (m, z, blk, terms))
    for i, (r, n, L, N, v, q) in enumerate(P['rows'] + P['idle']):
        o.append('  have b%d : T %d %s %d %d ≤ %s :=' % (i, m, z, r, n, frac_lean(q)))
        o.append('    term_le %d %d %d (%s) %s _ (by norm_num) (by norm_num) (by norm_num) (by norm_num)' % (m, r, n, eps, frac_lean(L)))
        o.append('      (log_le_of_le_expsum _ _ %d (by norm_num) (by norm_num)' % N)
        o.append('        (by norm_num [Finset.sum_range_succ, Nat.factorial]))')
        o.append('      (by norm_num) (by norm_num)')
    o.append('  have e1 : ((2:ℝ)^%d - 1) = %d := by norm_num' % (s, 2 ** s - 1))
    o.append('  have e2 : (2:ℝ)^%d = %d := by norm_num' % (s, 2 ** s))
    o.append('  have e3 : ((%d:ℕ):ℝ) = %d := by norm_num' % (W, W))
    o.append('  have e4 : T %d %s (%d - 1) 1 = T %d %s %d 1 := rfl' % (m, z, m, m, z, m - 1))
    o.append('  rw [e1, e2, e3, e4, hsum]')
    o.append('  linarith')
    o.append('')
    return '\n'.join(o), P


def sharp_text(name, u, A1, B):
    P = fl.plan_sharp(u, A1, B)
    assert P is not None, 'no sharpness certificate at %d' % A1
    m, W, H = u['m'], u['W'], u['H']
    eps = '%d/(10:ℝ)^%d' % (A1, B)
    z = '(1 - %s)' % eps
    blk = 'blocks' + name
    o = []
    o.append('/-- **sharpness**: at exponent `1 - %d/10^%d` the moment of one unit is at least its number of live roles `%d`, so the moment criterion fails for EVERY table made of copies of the unit and idle roles (`FoldRate.block_fails`).  Relative excess of the rational certificate: %.2e. -/' % (A1, B, W, P['slack_rel']))
    o.append('theorem fold_%s_sharp : ((%d:ℕ):ℝ) ≤ moment %d %s %s := by' % (name, W, m, z, blk))
    terms = ' + ('.join('T %d %s %d %d' % (m, z, r, H[r]) for r in sorted(H)) + ' + 0' + ')' * (len(H) - 1)
    o.append('  have hsum : moment %d %s %s\n      = %s := rfl' % (m, z, blk, terms))
    for i, (r, n, L, s, nn, v, q) in enumerate(P['rows']):
        o.append('  have c%d : %s ≤ T %d %s %d %d :=' % (i, frac_lean(q), m, z, r, n))
        o.append('    term_ge %d %d %d (%s) %s _ (by norm_num) (by norm_num) (by norm_num) (by norm_num)' % (m, r, n, eps, frac_lean(L)))
        o.append('      (le_log_of_expbound _ _ %d %d (by norm_num) (by norm_num) (by norm_num)' % (s, nn))
        o.append('        (by norm_num [Finset.sum_range_succ, Nat.factorial]))')
        o.append('      (by norm_num)')
    o.append('  have e3 : ((%d:ℕ):ℝ) = %d := by norm_num' % (W, W))
    o.append('  rw [e3, hsum]')
    o.append('  linarith')
    o.append('')
    return '\n'.join(o), P


def rank_text(name, u, A, B, s):
    P = fl.plan_rank(u, A, B, s)
    assert P is not None, 'per-rank fact does not pass the rational check'
    m, W, D = u['m'], u['W'], u['D']
    eps = '%d/(10:ℝ)^%d' % (A, B)
    o = []
    o.append('/-- **per-rank fact** at exponent `1 - %d/10^%d`, fill parameter `s = %d`: the hypothesis `hnum` of `RAM.engine_program_group_perRank` (u = %d, W = %d, D = %d).  Relative slack: %.2e. -/' % (A, B, s, m, W, D, P['slack_rel']))
    o.append('theorem foldRank_%s :' % name)
    o.append('    (2:ℝ)^%d * ((%d:ℕ):ℝ) * (((%d:ℕ):ℝ) - ((%d:ℕ):ℝ)^(1 - %s)) < ((2:ℝ)^%d - 1) * ((%d:ℕ):ℝ) :=' % (s, W, m, m, eps, s, D))
    o.append('  FoldRate.rank_fact3 %d %d %d %d (%s) %s (by norm_num) (by norm_num) (by norm_num)' % (m, W, D, s, eps, frac_lean(P['L'])))
    o.append('    (log_le_of_le_expsum _ _ %d (by norm_num) (by norm_num)' % P['N'])
    o.append('      (by norm_num [Finset.sum_range_succ, Nat.factorial]))')
    o.append('    (by norm_num) (by norm_num)')
    o.append('')
    return '\n'.join(o), P


def list_text(name, u, doc):
    m, W, D, H = u['m'], u['W'], u['D'], u['H']
    blk = 'blocks' + name
    lst = '[' + ', '.join('(%d, %d)' % (r, H[r]) for r in sorted(H)) + ']'
    o = []
    o.append('/-- %s -/' % doc)
    o.append('def %s : List (ℕ × ℕ) := %s' % (blk, lst))
    o.append('')
    o.append('/-- total rank of one unit (= number of unit moves it stands for): `W * m - D` -/')
    o.append('theorem %s_rank : (%s.map fun b => b.1 * b.2).sum = %d * %d - %d := by' % (blk, blk, W, m, D))
    o.append('  norm_num [%s]' % blk)
    o.append('')
    o.append('/-- the same as a price: the unit list at the price list `r ↦ r` (shape of `hPid` in `RAM.engine_program_group_perRank`) -/')
    o.append('theorem %s_tally : (%s.map fun b => (b.2:ℝ) * ((b.1:ℕ):ℝ)).sum = ((%d:ℕ):ℝ) * ((%d:ℕ):ℝ) - ((%d:ℕ):ℝ) := by' % (blk, blk, W, m, D))
    o.append('  norm_num [%s]' % blk)
    o.append('')
    o.append('theorem %s_count : (%s.map fun b => b.2).sum = %d := by' % (blk, blk, sum(H.values())))
    o.append('  norm_num [%s]' % blk)
    o.append('')
    o.append('theorem %s_proper : ∀ b ∈ %s, 1 ≤ b.1 ∧ b.1 < %d := by' % (blk, blk, m))
    o.append('  decide')
    o.append('')
    return '\n'.join(o)


def rank_sharp_text(name, u, A1, B):
    """D <= W (m - m^(1-eps')) from a rational lower bound of log m"""
    m, W, D = u['m'], u['W'], u['D']
    eps = Fraction(A1, 10 ** B)
    L, s, nn = fl.gen_sharp.log_lower(m, 1, 12)
    x = eps * L
    if not (x <= 1 and D <= W * m * (x - x * x / 2)):
        return None
    e = '%d/(10:ℝ)^%d' % (A1, B)
    o = []
    o.append('/-- **per-rank sharpness**: at exponent `1 - %d/10^%d` the deficit of one unit is at most `W (m - m^z)`, so the per-rank inequality fails for EVERY table made of copies of the unit and idle roles (`FoldRate.rank_fails`). -/' % (A1, B))
    o.append('theorem foldRank_%s_sharp :' % name)
    o.append('    ((%d:ℕ):ℝ) ≤ ((%d:ℕ):ℝ) * (((%d:ℕ):ℝ) - ((%d:ℕ):ℝ)^(1 - %s)) :=' % (D, W, m, m, e))
    o.append('  FoldRate.rank_fact_sharp %d %d %d (%s) %s (by norm_num) (by norm_num) (by norm_num)' % (m, W, D, e, frac_lean(L)))
    o.append('    (le_log_of_expbound _ _ %d %d (by norm_num) (by norm_num) (by norm_num)' % (s, nn))
    o.append('      (by norm_num [Finset.sum_range_succ, Nat.factorial]))')
    o.append('    (by norm_num) (by norm_num)')
    o.append('')
    return '\n'.join(o)
