"""Exact finite check of the cross-copy slot in the model of #451's trace note.

Model (as in research/cross-family-residual-obstruction of #451): a family's address is (x, y) in F_q^m x F_q^m; the
rank-r coordinate operator on a set S of coordinates exchanges x_i and y_i for i in S.  Two copies A and B of one pair
are idle; a child of rank r acts on A's pending set S_A and on B's pending set S_B.  A residual of width w <= r
from an invocation inside the window is hosted either whole on A (#442) or split, w1 coordinates on A and w2 on B
(#448), and the child keeps the remainder on each family.

Checked exactly, as permutations of the two-family address space:
  (1) the trace note's comparison: the residual factor alone differs between the two placements (its claim, confirmed);
  (2) the complete program: residual factor(s) followed by the remainder children equals the original children
      Gamma_A x Gamma_B for BOTH placements, so the two placements realise the same program.
Also the whole-on-A placement is impossible when w > r, while the split still works: the case cross-copy hosting
is for.  Standard library only.  usage: python3 -B toy_two_family_check.py"""
import itertools, json, sys
def families(q, m):
    one = list(itertools.product(range(q), repeat=2 * m))
    return [(f, w) for f in range(2) for w in one]
def exchange(states, index, sets, m):
    """permutation exchanging x_i <-> y_i for i in sets[family] on each family"""
    out = []
    for f, w in states:
        w = list(w)
        for i in sets[f]: w[i], w[m + i] = w[m + i], w[i]
        out.append(index[f, tuple(w)])
    return out
def compose(p, r): return [p[r[i]] for i in range(len(r))]      # apply r then p
def fixed(p): return sum(i == j for i, j in enumerate(p))
def check(q, m, r, w, w1):
    states = families(q, m); index = {s: i for i, s in enumerate(states)}; E = lambda a, b: exchange(states, index, {0: a, 1: b}, m)
    S = list(range(r))                                 # the child's pending set on each copy (same coordinates by symmetry)
    gamma = E(S, S)                                     # original children: Gamma_A x Gamma_B
    res = {}
    if w <= r:                                          # #442: whole residual on A
        piece = S[:w]; rem_A = S[w:]
        factor = E(piece, []); remainder = E(rem_A, S)
        res['whole_on_A'] = dict(factor_fixed=fixed(factor), program_equals_original=compose(remainder, factor) == gamma)
    w2 = w - w1; assert 0 < w1 <= r and 0 < w2 <= r     # #448: split across A and B
    pA, pB = S[:w1], S[:w2]
    factor = E(pA, pB); remainder = E(S[w1:], S[w2:])
    res['split_A_B'] = dict(factor_fixed=fixed(factor), program_equals_original=compose(remainder, factor) == gamma)
    if w <= r: res['factors_differ_as_in_note'] = res['whole_on_A']['factor_fixed'] != res['split_A_B']['factor_fixed']
    res.update(q=q, m=m, child_rank=r, residual_width=w, pieces=[w1, w2], dimension=len(states))
    return res
rows = [check(3, 2, 2, 2, 1), check(3, 3, 2, 2, 1), check(3, 3, 3, 2, 1), check(2, 4, 3, 4, 2), check(3, 3, 2, 3, 2)]
for row in rows:
    assert row['split_A_B']['program_equals_original']
    if 'whole_on_A' in row: assert row['whole_on_A']['program_equals_original'] and row['factors_differ_as_in_note']
    else: assert row['residual_width'] > row['child_rank']
out = dict(status='PASS_TWO_FAMILY_PROGRAM_IDENTITY', rows=rows,
           conclusion='In the coordinate-exchange model the residual factor differs between placements (the trace note), '
                      'but the complete program, factor(s) followed by the remainder children, equals the original children '
                      'Gamma_A x Gamma_B for the whole-on-A placement and for the split placement alike; when w > r only the split exists.')
print(json.dumps(out, indent=1))
