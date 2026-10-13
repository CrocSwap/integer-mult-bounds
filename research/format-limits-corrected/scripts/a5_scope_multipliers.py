"""A. Format ceiling, rev. 2: how much each scope assumption is worth (ceiling multipliers if it is relaxed).

Each variant of skel.profile drops one rule of the scope and recomputes the certified root at s = 3, 5, ..., 13:
  copyfree       copy charge x -> 0 (non-star totals with no pairing-rank floor; star scope broken);
  idlefree       the B_K idle frame changes cost nothing;
  idle_onechild  all idle frame changes of one copy batched into one child (cross-stretch batching);
  nosplit        bridges moved off the idle stretches (no split pre-stretch);
  loc_h          data local climbs batched up to the window h (cross-register batching inside a stage);
  idlefree_loch  idle free and local batching to h at once;
  window w-1     a family whose stage window is one smaller at the same copy ratio x.
Multiplier = (best-s root of the variant) / (best-s root of the theorem), and the same at s = 9.
These are the multipliers quoted in the rule table of README section B.
"""
from fractions import Fraction as Fr

from report import check, finish, near
from skel import X

S_LIST = (3, 5, 7, 9, 11, 13)
UNITS = {'bit-111/63': (8, 63, 111), 'cx-112/64': (9, 64, 112)}
VARIANTS = ('copyfree', 'idlefree', 'idle_onechild', 'nosplit', 'loc_h', 'idlefree_loch', 'window-1')
# (best-s multiplier, s = 9 multiplier), two decimals
EXPECTED = {
    'bit-111/63': {'copyfree': (6.77, 2.79), 'idlefree': (1.67, 2.14), 'idle_onechild': (1.19, 1.55),
                   'nosplit': (1.15, 1.18), 'loc_h': (1.12, 1.03), 'idlefree_loch': (1.79, 2.28),
                   'window-1': (1.16, 1.16)},
    'cx-112/64': {'copyfree': (6.91, 2.83), 'idlefree': (1.68, 2.15), 'idle_onechild': (1.20, 1.55),
                  'nosplit': (1.15, 1.18), 'loc_h': (1.08, 1.02), 'idlefree_loch': (1.79, 2.27),
                  'window-1': (1.14, 1.14)},
}


def roots(h, x, variant):
    out = {}
    for s in S_LIST:
        r = X(s, h, 1, x, variant)
        out[s] = r['hi'] if r else Fr(0)
    return out


for name, (h, cst, v) in UNITS.items():
    x = Fr(cst, v)
    base = roots(h, x, 'thm')
    b_best = max(base.values())
    for var in VARIANTS:
        rr = roots(h - 1, x, 'thm') if var == 'window-1' else roots(h, x, var)
        best = max(rr.values())
        sb = max(rr, key=rr.get)
        mult = (float(best / b_best), float(rr[9] / base[9]))
        exp = EXPECTED[name][var]
        check('A5.%s.%s' % (name, var), near(mult[0], exp[0], 2) and near(mult[1], exp[1], 2),
              'best %.4e (s = %d): x%.2f;  s = 9: x%.2f' % (best, sb, mult[0], mult[1]))
finish()
