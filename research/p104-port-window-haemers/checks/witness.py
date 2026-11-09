"""The 14-port representation at k = 2 with inner dimension 17: exact rank over Q, F_2 and F_3, every forced zero, controls."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools
from common import *

Wd = load('witness14.json')
k, R = Wd['k'], Wd['inner_dim']
K, others = Wd['K'], Wd['others']
S = K + others
coords = {int(t): c for t, c in Wd['coords'].items()}
dt = lambda a, b: dot(PORTS[a], PORTS[b])

req(k == 2 and R == 17 and len(S) == 14 and set(coords) == set(S), 'witness: 14 ports, k = 2, inner dimension 17, every port has a coordinate pair')
req(all(dt(a, b) == 0 for a, b in itertools.combinations(K, 2)), 'the 8 ports of K are pairwise orthogonal (dot 0)')
req(all(sum(dt(t, c) for c in K) == 2 for t in others), 'each of the 6 other ports has exactly two odd neighbours in K')
req(len({c for cs in coords.values() for c in cs}) == 17 and all(len(set(cs)) == 2 for cs in coords.values()), 'all 17 coordinates are used and each port occupies two distinct ones')

def build(coords):
    """W = U: row (t, i) is the unit vector e_{coords[t][i]}; B = U U^T, a 28 x 28 integer matrix."""
    rows = [(t, [int(c == coords[t][i]) for c in range(R)]) for t in S for i in range(k)]
    return rows, [[sum(x * y for x, y in zip(r1, r2)) for _, r2 in rows] for _, r1 in rows]

def mask_report(B, pairs_zero=None):
    """Ordered pairs of distinct ports with dot 0 (forced zero blocks), violations among them, and singular diagonal blocks."""
    fz = viol = sing = 0
    for a, s in enumerate(S):
        for b, t in enumerate(S):
            blk = [[B[k * a + i][k * b + j] for j in range(k)] for i in range(k)]
            if a == b:
                if blk[0][0] * blk[1][1] - blk[0][1] * blk[1][0] == 0:
                    sing += 1
            elif dt(s, t) == 0:
                fz += 1
                viol += any(x for r in blk for x in r)
    return fz, viol, sing

rows, B = build(coords)
fz, viol, sing = mask_report(B)
req(fz == 150 and viol == 0 and sing == 0, 'forced-zero ordered pairs: %d, violations: %d, singular diagonal blocks: %d' % (fz, viol, sing))
req(all(B[k * a + i][k * a + j] == int(i == j) for a in range(len(S)) for i in range(k) for j in range(k)), 'diagonal blocks are the identity I_2')
rq, r2, r3 = rank_q(B), rank_mod(B, 2), rank_mod(B, 3)
req((rq, r2, r3) == (17, 17, 17), 'rank B = %d over Q, %d over F_2, %d over F_3 (rank 17 < 18 = 9k)' % (rq, r2, r3))
BKK = [[B[k * a + i][k * b + j] for b in range(8) for j in range(k)] for a in range(8) for i in range(k)]
req(rank_q(BKK) == 16, 'the K ports alone force rank 16 = 8k')
# the 6 other ports force their coordinates: with only the 16 K-coordinates the rank would be 16, and 17 is used
req(sum(1 for t in others if 16 in coords[t]) == 2, 'exactly two of the six ports use the one extra coordinate')

# five of the ports induce a 5-cycle, and the coordinates on them are the two-coordinate clique cover of that cycle
C5 = [62, 68, 101, 63, 95]
edges5 = sorted((a, b) for a, b in itertools.combinations(C5, 2) if dt(a, b))
req(edges5 == sorted([(62, 68), (68, 101), (101, 63), (63, 95), (62, 95)]), 'ports 62, 68, 101, 63, 95 induce a 5-cycle in the odd graph (5 edges, each vertex of degree 2)')
# controls
def mutate(coords, t, i, new):
    c = {u: list(v) for u, v in coords.items()}
    c[t][i] = new
    return c
planted = None
for t in others:
    for i in range(2):
        for s in S:
            if s != t and dt(t, s) == 0:
                for new in coords[s]:
                    if new not in coords[t]:
                        planted = planted or (t, i, new)
t, i, new = planted
rows_m, Bm = build(mutate(coords, t, i, new))
fzm, violm, singm = mask_report(Bm)
req(violm > 0, 'control: giving port %d a coordinate of an orthogonal port (replacing its coordinate %d) creates %d forced-zero violations' % (t, coords[t][i], violm))
# a pair with dot 1 that shares a coordinate cannot be declared forced zero
pair = next((a, b) for a, b in itertools.combinations(S, 2) if dt(a, b) == 1 and set(coords[a]) & set(coords[b]))
a, b = S.index(pair[0]), S.index(pair[1])
req(any(B[k * a + i][k * b + j] for i in range(k) for j in range(k)), 'control: the adjacent pair (%d, %d) shares a coordinate, so B is nonzero there; declaring it forced zero would be a violation' % pair)
# a mutated witness with a repeated coordinate in one port has a singular diagonal block
c2 = {u: list(v) for u, v in coords.items()}
c2[others[0]][1] = c2[others[0]][0]
_, B2 = build(c2)
req(mask_report(B2)[2] > 0, 'control: repeating a coordinate inside one port makes its diagonal block singular')
finish('PASS_WITNESS')
