"""CHECKED (exact): the label data behind Theorem 3 (dense polar law) on the six root units, and the block-rank law on E8.
 (a) odd-or-zero, k = rank_F2(G mod 2), rank_F2 B = k+1, T(k+1) against v.
 (b) E8, all 120 x 120 normal pairs: r(C(a),C(b)) = 9, r(N(a),C(b)) = 8, r(N(a),N(b)) = 8 (a.b even or a = b) / 7 (a.b odd), where N(a) = lines
     non-orthogonal to a (a excluded), C(a) = N(a) u {a}."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from exact import rank_f2
from units import UNITS, E8, gram, bmasks, block_rank

EXPECT = {'D4': (2, 3, 12), 'D5': (4, 5, 20), 'D6': (4, 5, 30), 'E6': (6, 7, 36), 'E7': (6, 7, 49), 'E8': (8, 9, 72)}
for name, (L, T) in UNITS.items():
    G = gram(L)
    v = len(L)
    oz = all(G[t][s] % 2 == 1 for t in range(v) for s in range(v) if t != s and G[t][s] != 0)
    k = rank_f2([sum(((G[t][s] % 2) << s) for s in range(v)) for t in range(v)])
    rb = rank_f2(bmasks(G))
    kk, rbb, vv = EXPECT[name]
    check('P1.labels-' + name, oz and k == kk and rb == rbb and v == (12, 20, 30, 36, 63, 120)[list(EXPECT).index(name)],
          '%s: v=%d T=%d odd-or-zero %s, k=%d, rank B=%d (=k+1), T(k+1)=%d, min(v,T(k+1))=%d' % (name, v, T, oz, k, rb, T * (k + 1), min(v, T * (k + 1))))

G = gram(E8)
v = 120
Br = bmasks(G)
N = lambda a: [t for t in range(v) if G[a][t] != 0 and t != a]
Ns = [N(a) for a in range(v)]
ok_cc = ok_nc = ok_nn = True
cnt = {'cc': 0, 'nc': 0, 'nn_even': 0, 'nn_odd': 0}
for a in range(v):
    for b in range(v):
        cc = block_rank(Br, Ns[a] + [a], Ns[b] + [b])
        nc = block_rank(Br, Ns[a], Ns[b] + [b])
        nn = block_rank(Br, Ns[a], Ns[b])
        odd = a != b and G[a][b] % 2 == 1
        ok_cc &= cc == 9
        ok_nc &= nc == 8
        want = 7 if odd else 8
        ok_nn &= nn == want
        cnt['cc'] += 1; cnt['nc'] += 1
        cnt['nn_odd' if odd else 'nn_even'] += 1
check('P1.law-E8-CC', ok_cc, 'E8: r(C(a),C(b)) = 9 = k+1 for all %d ordered pairs' % cnt['cc'])
check('P1.law-E8-NC', ok_nc, 'E8: r(N(a),C(b)) = 8 = k (one dead-type normal) for all %d ordered pairs' % cnt['nc'])
check('P1.law-E8-NN', ok_nn, 'E8: r(N(a),N(b)) = 8 for a = b or a.b even (%d pairs), 7 for a.b odd (%d pairs): the 8/7 rule of #968' % (cnt['nn_even'], cnt['nn_odd']))
finish()
