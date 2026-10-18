"""ERR1 -- erratum to #595: dyadic exact decoders reach rank_Q G totals, below rank_F2 B0.  usage: err1.py   (reads ../lib only)
B0 = (J + G) mod 2 is the pairing of the root pattern (ones where the line inner product is even, the diagonal included).
For each unit the decoder M = P Q^T = G is rebuilt in exact rationals and checked: P Q^T == G, all denominators powers of two,
M_tt != 0, M_ts = 0 wherever B0_ts = 1 (s != t); then the total count n = rank_Q G is compared with rank_F2 B0 and the Thm C
block ranks r_j = rank_F2 B0[R_j, A_j] are printed."""
import io, contextlib, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
with contextlib.redirect_stdout(io.StringIO()):
    import ade
from dyadic import dyadic_decoder
for nm, L in [('E6', ade.E6b()), ('E7', ade.E7()), ('E8', ade.E8()), ('A4', ade.A(4)), ('A6', ade.A(6)), ('A8', ade.A(8))]:
    G, idx, P, Q = dyadic_decoder(L); v = len(L); n = len(idx)
    ok = all(sum(P[t][j] * Q[s][j] for j in range(n)) == G[t, s] for t in range(v) for s in range(v))
    dy = all(f.denominator & (f.denominator - 1) == 0 for r in P + Q for f in r)
    B0 = (1 + G) % 2; r2 = ade.f2rank(B0)
    pat = all(G[t, t] != 0 for t in range(v)) and all(G[t, s] == 0 for t in range(v) for s in range(v) if t != s and B0[t, s] == 1)
    rs = []
    for j in range(n):
        R = [t for t in range(v) if P[t][j] != 0]; A = [t for t in range(v) if Q[t][j] != 0]
        rs.append(ade.f2rank(B0[np.ix_(R, A)]))
    print(f"{nm} v {v} totals {n} exact P Q^T == G: {ok} dyadic: {dy} rankF2 B0 {r2}")
    print(f"{nm} M = G has M_tt != 0 and M_ts = 0 where B0_ts = 1: {pat} | totals {n} < rankF2 B0 {r2}: {n < r2}")
    print(f"{nm} block ranks r_j {rs} sum {sum(rs)}")
