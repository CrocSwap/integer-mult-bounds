"""CHECKED (exact Fractions): explicit exact decoders whose dense-B F2 cost equals the floors of Theorem 4 / Corollary 3.1.
Each decoder is verified to satisfy P Q^T = Gram (up to the stated factor) on every live line pair, then priced with the dense pairing B
(B_ts = 1 iff t = s or r_t _|_ r_s):  cost = sum_j rank_F2 B[supp p_j, supp q_j].
Rows: E8 72 (8 x 9), P112 64 (8 x 8), P104 56 (8 x 7, frame-pair decoder, rebuilt), E7 49 (7 x 7), E7 minus a 7-frame 42 (7 x 6),
D4 12 (4 x 3), D6 30 (6 x 5), D5 20 (= v)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from units import E8, E7, UNITS, gram, first_frame, decoder_cost, true, unit_vectors
import p104


def row(ident, name, roots, basis, v, T, want_cost, want_rank):
    ok, cost, ranks, P, Q = decoder_cost(roots, basis)
    check(ident, ok and len(roots) == v and cost == want_cost and ranks == [want_rank] * T,
          '%s: v=%d, T=%d, M = Gram exact: %s, term ranks %s, cost %d (expected %d = %dx%d)' % (name, len(roots), T, ok, sorted(set(ranks)), cost, want_cost, T, want_rank))
    return cost


# E8: coordinate basis (also a frame of roots gives the same number)
row('D1.E8-coord', 'E8 coordinate decoder', E8, unit_vectors(8), 120, 8, 72, 9)
G8 = gram(E8)
F = first_frame(G8, 8)
row('D1.E8-frame', 'E8 decoder in the first orthogonal frame of roots', E8, [true(E8[i]) for i in F], 120, 8, 72, 9)
# P112 = E8 minus the frame F0 used as the decoder basis (the removed lines are exactly the basis)
live = [E8[i] for i in range(120) if i not in set(F)]
row('D1.P112', 'P112 = E8 - F0, basis F0', live, [true(E8[i]) for i in F], 112, 8, 64, 8)
# E7
G7 = gram(E7)
F7 = first_frame(G7, 7)
row('D1.E7', 'E7 decoder in a 7-frame of roots', E7, [true(E7[i]) for i in F7], 63, 7, 49, 7)
live7 = [E7[i] for i in range(63) if i not in set(F7)]
row('D1.E7-frame', 'E7 minus the 7-frame (new unit), basis = removed frame', live7, [true(E7[i]) for i in F7], 56, 7, 42, 6)
# D4, D6, D5 in coordinates
for n, vv, rk in ((4, 12, 3), (5, 20, 4), (6, 30, 5)):
    L = UNITS['D%d' % n][0]
    row('D1.D%d' % n, 'D%d coordinate decoder' % n, L, unit_vectors(n), vv, n, n * rk, rk)
# P104: frame-pair decoder (#968 mechanism) rebuilt with our dense B
G, F0, frames, F1, sols = p104.build()
ok, ranks, live104 = p104.cost_of_pairs(G, sols[0], set(F0) | set(F1))
check('D1.P104', ok and len(live104) == 104 and ranks == [7] * 8 and sum(ranks) == 56,
      'P104 = E8 - F0 - F1: P Q^T = 2 Gram on 104 live lines: %s; 8 terms of rank %s, cost %d (= 8x7); %d frames in the 112-pool, first admissible F1 has %d decoders' % (ok, sorted(set(ranks)), sum(ranks), len(frames), len(sols)))
# structure of the P104 decoder: dead normals, A^T B = 2I
al = [a for a, b in sols[0]]
be = [b for a, b in sols[0]]
struct = all(G[al[k]][be[l]] == 0 for k in range(8) for l in range(8) if k != l) and all(G[al[k]][be[k]] % 2 == 1 for k in range(8))
check('D1.P104-structure', struct and set(al) | set(be) == set(F0) | set(F1) and sum(a in F0 for a in al) == 4 and sum(a in F1 for a in al) == 4,
      'alpha_k . beta_l = 0 (k != l), alpha_k . beta_k odd, the 16 normals are exactly the dead lines F0 u F1, 4 of the alpha_k in F0 and 4 in F1')
finish()
