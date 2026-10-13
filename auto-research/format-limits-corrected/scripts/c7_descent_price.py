"""C. Per-call pricing of a paid descent on the frontier pipelines.

c7_descent_toy.py shows exactly that a rank-1 descent of a register followed by its re-climb costs two extra rank-1
children (2 units of data mass) in the local word.  The local word runs in every call (#555: s T = 288 stage-replicas;
#568: 72 calls), so by the deficit identity m W - mass = D each descent per local word lowers D by 2 per call and adds
two rank-1 children per call.  This script prices that on the published global profiles with the certified pressure
root, hosting held fixed, for one and two rank-1 descents per local word.
"""
from fractions import Fraction as Fr

from cert import root_bracket
from report import VENDOR, check, finish, load_json, near

EXPECTED = {('#555', 1): -5.630, ('#555', 2): -11.257, ('#568', 1): -5.646, ('#568', 2): -11.290}
e555 = load_json(VENDOR / 'pr555' / 'EXPECTED.json')
p568 = load_json(VENDOR / 'pr568' / 'PLAN.json.gz')
WORDS = {'#555': ({int(k): z for k, z in e555['nine']['profile'].items()}, 64, 10272, 288),
         '#568': ({int(k): z for k, z in p568['profile'].items()}, 73, 2560, 72)}
for name, (P, m, D, calls) in WORDS.items():
    _, h0 = root_bracket(P, m, D, hi=Fr(1, 100))
    for n in (1, 2):
        Q = dict(P)
        Q[1] = Q.get(1, 0) + 2 * n * calls
        _, h = root_bracket(Q, m, D - 2 * n * calls, hi=Fr(1, 100))
        pct = 100 * float(h / h0 - 1)
        check('C7.price.%s.%d' % (name, n), near(pct, EXPECTED[name, n], 3),
              '%d rank-1 descent(s) per local word, paid in all %d calls: %+.3f%% of the supplier value' % (n, calls, pct))
finish()
