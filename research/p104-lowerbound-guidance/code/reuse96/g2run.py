"""REUSE96 g2run.py: R=2 Q5 run with NO owned descents (SAT --absmove, L=16): Y-carrier rendezvous, monotone GTD lifetimes."""
from eng import *
from f2mass import all_mass, rankQ
P = [1, 2, 7, 11, 13]; n = 4; F = Field(2); fs = frozenset
ops = [('INIT', ('O', 0), fs({0, 13})), ('MOVE', ('Y', 2), fs({0, 11, 13, 6})), ('ADD', ('O', 0), 1, ('Y', 2)),
 ('INIT', ('O', 1), fs({0, 12})), ('MOVE', ('Y', 3), fs({0, 13})), ('ADD', ('O', 0), 1, ('Y', 3)),
 ('ADD', ('Y', 1), 1, ('O', 0)), ('MOVE', ('Y', 1), fs({0, 12})), ('ADD', ('O', 1), 1, ('Y', 1)),
 ('MOVE', ('Y', 1), fs({0, 1, 12, 13})), ('ADD', ('X', 0), 1, ('Y', 1)), ('MOVE', ('Y', 3), fs({0, 10, 13, 7})),
 ('ADD', ('X', 2), 1, ('Y', 3)), ('MOVE', ('Y', 0), fs({0, 2, 12, 14})), ('ADD', ('O', 1), 1, ('Y', 0)),
 ('ADD', ('X', 1), 1, ('Y', 0)), ('MOVE', ('O', 0), fs({0, 1, 12, 13})), ('ADD', ('Y', 1), 1, ('O', 0)),
 ('ADD', ('X', 0), 1, ('Y', 1)), ('MOVE', ('O', 1), fs({0, 11, 12, 7})), ('ADD', ('X', 2), 1, ('O', 1)),
 ('ADD', ('X', 3), 1, ('O', 1)), ('CLEAR', ('O', 0)), ('CLEAR', ('O', 1))]
R = replay(n, P, F, dict(nh=1), ops)
desc = 0; ch = {}
for op in ops:
    if op[0] == 'INIT': ch[op[1]] = op[2]
    if op[0] == 'MOVE' and op[1][0] == 'O':
        if not ch[op[1]] <= op[2]: desc += 1
        ch[op[1]] = op[2]
print('bad', R.bad, 'pinned errs', R.pinned(), 'R(ascent) =', R.cost, 'owned descents =', desc)
Rec = R.rec(); odd, idx, dist = all_mass(P)
pat = sum(1 << i for i, (t, s) in enumerate(odd) if Rec[t][s])
print('odd pattern', sorted(odd[i] for i in range(len(odd)) if pat >> i & 1))
print('F2 mass', dist[pat], 'rank_F2', rankQ(P, odd, pat))
