"""Group G1: exact F2 costs of root-unit decoders (the T^2 threshold table).  For each unit the exact T-block decoder M = P Q^T = Gram (pure Fractions),
its zero pattern, and the exact F2 cost sum_j rank_F2 B[R_j, A_j] of an admissible pairing B.  B0 = full orthogonal pattern."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from roots import *; from units import *
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
def row(name, L, P, Q, B, label):
    v = len(L); T = len(P[0]); ex = exact(L, P, Q); adm = admissible(L, B); br = block_ranks(P, Q, B)
    print("UN %s v=%d T=%d rank(L)=%d decoder exact (M = Gram): %s; B admissible: %s; %s; block ranks %s; cost %d; T^2 = %d; cost - v = %d" % (
        name, v, T, rank(L), ex, adm, label, br, sum(br), T * T, sum(br) - v))
for nm in ('D4', 'D5', 'D6'):
    L = unit(nm); P, Q = decoder_std(L); row(nm, L, P, Q, b0(L), 'standard coordinates, B = B0')
L = unit('E6'); e6 = json.load(open(os.path.join(DATA, 'e6_best.json')))
P, Q = decoder(L, e6['basis']); B = [[(e6['rows'][t] >> s) & 1 for s in range(len(L))] for t in range(len(L))]
row('E6', L, P, Q, B, 'stored basis and stored B (found by local search from B0)')
print("UN E6 B0 in the stored basis costs %d; in the first-independent basis %d" % (sum(block_ranks(P, Q, b0(L))), sum(block_ranks(*decoder(L, first_basis(L)), b0(L)))))
for nm in ('E7', 'E8'):
    L = unit(nm); P, Q = decoder(L, first_basis(L)); row(nm, L, P, Q, b0(L), 'first independent lines as basis, B = B0')
for nm in ('A4', 'A5', 'A6'):
    L = unit(nm); P, Q = decoder(L, first_basis(L)); row(nm, L, P, Q, b0(L), 'first independent lines as basis, B = B0 (upper bound only)')
print("UN T^2 vs v for roots: D4 16 vs 12, D5 25 vs 20, D6 36 vs 30, E6 36 vs 36, E7 49 vs 63, E8 64 vs 120")
