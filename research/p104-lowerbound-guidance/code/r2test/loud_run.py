"""R2TEST: the R=2 run for Q5={1,2,7,11,13}, odd-cell target t0:y2+y3, t2:y0+y1+y2, t3:y0+y1+y3 (GF(2)), replayed with SP's engine/FA/F2-mass."""
from eng import *
from fa import gfa
from f2mass import all_mass, rankQ
P = [1, 2, 7, 11, 13]; n = 4; F = Field(2)
fs = frozenset
ops = [('INIT', ('O', 0), fs({0, 13})),
 ('MOVE', ('Y', 2), fs({0, 13})), ('ADD', ('O', 0), 1, ('Y', 2)),
 ('MOVE', ('Y', 3), fs({0, 10, 13, 7})), ('ADD', ('O', 0), 1, ('Y', 3)),
 ('MOVE', ('O', 0), fs({0, 1, 12, 13})), ('ADD', ('X', 0), 1, ('O', 0)),
 ('MOVE', ('O', 0), fs({0, 12})),
 ('MOVE', ('Y', 0), fs({0, 12})), ('ADD', ('O', 0), 1, ('Y', 0)),
 ('MOVE', ('Y', 1), fs({0, 1, 12, 13})), ('ADD', ('O', 0), 1, ('Y', 1)),
 ('MOVE', ('O', 0), fs({0, 11, 12, 7})), ('ADD', ('X', 3), 1, ('O', 0)), ('ADD', ('X', 2), 1, ('O', 0)),
 ('CLEAR', ('O', 0))]
meta = dict(nh=1, Xch=[span([q]) for q in P], Ych=[fs([0])] * 5, Hch=[fs([0])])
R = replay(n, P, F, meta, ops)
print('bad', R.bad, 'pinned errs', R.pinned(), 'cost', R.cost)
Rec = R.rec(); print('Rec rows', [[s for s in range(5) if Rec[t][s]] for t in range(5)])
odd, idx, dist = all_mass(P)
pat = sum(1 << i for i, (t, s) in enumerate(odd) if Rec[t][s])
print('F2 decoder mass of realised odd pattern', dist[pat], 'rank_F2(Q o Rec)', rankQ(P, odd, pat), '=> mass > R' if dist[pat] > R.cost else '')
tg = {(0,2),(0,3),(2,0),(2,1),(2,2),(3,0),(3,1),(3,3)}
print('odd pattern == target:', {odd[i] for i in range(len(odd)) if pat >> i & 1} == tg)
fa = gfa(n, P, F, meta, ops); print('FA', fa)
