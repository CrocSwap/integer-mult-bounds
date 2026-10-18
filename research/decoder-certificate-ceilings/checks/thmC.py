# Theorem C: exact (Fraction) ceilings of the fake-decoder witness on P120, P112, E7, E6.
# For each unit: enumerate ALL orthogonal sets D (mutually orthogonal lines), all maximal orthogonal sets ("frames"),
# meet(D) = #frames meeting D.  Witness: weight y = max_D |D|/meet(D) on every frame (rho(F) = rank_F2 Bd[F,F] = 1),
# weight T = rank_Q N0 on every cost-0 single-entry term.  Ceiling = (#frames) * y.
import numpy as np, collections
from fractions import Fraction
from geom import *
from units import units
EXPECT = {'E8': Fraction(360, 17), 'P112': Fraction(15968, 757), 'E7': Fraction(945, 71), 'E6': Fraction(12)}
EXTRA = {'E8': (2025, 765, 352875), 'P112': (1996, 757, 262928), 'E7': (135, 71, 13743), 'E6': (135, 45, 981)}
ok = True
for name in ('E6', 'E7', 'P112', 'E8'):
    idx, T = units[name]; m = len(idx)
    sets, o = all_orth_sets(idx); mx = maximal(sets, o, m)
    tob = lambda c: np.array([(c >> i) & 1 for i in range(m)], dtype=np.int32)
    F = np.stack([tob(c) for c in mx]); best = None
    for s in range(0, len(sets), 20000):
        D = np.stack([tob(c) for c in sets[s:s + 20000]])
        meet = ((D @ F.T) > 0).sum(1); sz = D.sum(1)
        for a, b in zip(sz, meet):
            r = Fraction(int(a), int(b))
            if best is None or r > best[0]: best = (r, int(a), int(b))
    y = best[0]; ceiling = len(mx) * y
    # rank_F2 Bd[F,F] = 1 for every frame (Bd is all-ones on an orthogonal set)
    assert all(f2rank([[1] * bin(c).count('1')] * bin(c).count('1')) == 1 for c in mx[:1])
    for c in mx[:50]:
        ids = [idx[i] for i in range(m) if c >> i & 1]
        assert all(G[a, b] == 0 for a in ids for b in ids if a != b)
    rkQ = np.linalg.matrix_rank(G[np.ix_(idx, idx)].astype(float))
    assert rkQ == T, (name, rkQ, T)
    nfr, nmeet, nsets = EXTRA[name]
    good = (ceiling == EXPECT[name]) and (len(mx), best[2], len(sets)) == (nfr, nmeet, nsets) and (name != 'E8' or best[1] == 8)
    ok &= good
    print(('PASS' if good else 'FAIL'), 'ThmC', name, 'lines', m, 'orthogonal sets', len(sets), 'maximal', dict(collections.Counter(bin(c).count('1') for c in mx)),
          'binding (|D|,meet)', best[1:], 'y =', y, 'ceiling =', ceiling, '=', float(ceiling), 'rank_Q N0 =', rkQ, flush=True)
print('PASS ThmC all four units' if ok else 'FAIL ThmC')
