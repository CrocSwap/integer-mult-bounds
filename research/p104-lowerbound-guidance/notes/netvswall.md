# NETVSWALL NV (Nov 20, Sonnet, small exact). Own code: nv.py (exact decoder min mass, Singular GB over QQ), netcheck.py (network -> polynomial system), enum_run.py / enum2.py (exhaustive network enumeration), decall.py, e8shard.py / e8sub*.py / e8e7.py (restrict the verified E8-56 decoder to label shards). Logs: dec3.log e3_*.log e4_*.log.
Setting. Label set P = odd-weight vectors of F2^h (Q = Gram mod 2; diagonal cells odd). Wall target: M o Q = diag(c), every c_p != 0, c free over Q (diag nonzero encoded by an inverse variable z_p). Decoder mass = sum of rank_F2 Q[D,S] over rows (w,v). Network = nodes (a_k >= b_k), D = sum dim(a_k/b_k), gathers on a_k, deposits on b_k^perp, relay j->k iff b_j <= a_k, M = G(I-H)^-1 F. Zero-drop nodes (a=b) are allowed (pure relays).
Why this differs from NETATTR: its minimal instance is a LOCAL target. Here the target is the full diagonal wall requirement, and I also enumerate ALL legal edge sets (H free incl. 0) over ALL chart pairs.

## 1. Decoder side [C exact]
- m(P) = n for every P at h=3 (n<=4, dec3.log). h=4: n=5 sets {1,2,4,8,7} and {1,2,4,7,11}: all covers (incl. extra rows) with total price <= n-1 INFEASIBLE (GB = <1>), ~40-50 s each. n>=6 at h=4: cover enumeration blows up (not decided).
- Smallest known m(P) < n [C, upper bound by an explicit decoder; lower bound NOT claimed]: restrict the verified E8-56 decoder (8 rows, all price 7) to a shard of lines.
  - Gram rank 7: P = the 63 E7 lines (lines orthogonal to one line of the 120): 7 rows of price 7 = 49 < 63. P = the 52 P104 ports orthogonal to line 117: rows [6,5,5,5,5,6,6] = 38 < 52. Each is a hyperplane section of the label space (labels of the shard lie in v^perp with v.v = 0, so the form is degenerate and the label multiset lives in F2^7).
  - No shard of Gram rank <= 6 beats n (best gain exactly 0, e.g. n=30 rank 5 mass 30; n=24 rank 7 sub-space, n=16 rank 6, n=8 rank 4). Subspace shards of dim 4..7 of P104: gain 0; dim 8: gain 14 (n=52).
  - So the smallest h where I can exhibit a decoder beating n is Gram rank 7; the true minimum is unknown (small cases h<=4 exact: none). Consistent with D56.md ("no symplectic port set below h=9"), which concerns native sets; shards are non-symplectic.

## 2. Network side [C exact; supports every legal edge set, scalars any rationals]
Exhaustive over all chart pairs (a >= b) with D <= n-1, all topological orders, ALL legal relay edges as free variables, Singular GB over QQ: "FEASIBLE" would mean some network with D <= n-1 realises M o Q = diag(c != 0).
- h=3, all P (n<=4), 2 and 3 nodes: 2688 + 64 systems for the full P, 0 feasible. Four nodes (enum2): see logs (partial results at the bottom).
- h=4, all 28 P up to coordinate permutation (n=3..8), 2 nodes: 0 feasible (about 1100-1500 systems per P at n=6,7; most (m=2) sets die on the covering condition union_k A_k = P).
- h=4, 3 nodes, n=3,4: 0 feasible so far (e4_3_small.log).
- CONTROL [C]: enumeration at D <= 6 on the full h=3 set finds FEASIBLE networks, first at D = n = 4 (2 nodes + 1 relay: a=F2^3,b=0 and a=F2^3,b=<3,5,6>). So the pipeline finds feasible networks when they exist, none below n.
- Relay-free nodes are decoder rows with price <= d_k (pairing rank of b^perp x a), so relay-free D >= m(P) holds by construction; any counterexample must contain a relay.

## 3. Verdict
- NO toy where networks beat decoders. On every small P exhaustively covered (h<=4, <=3 nodes; h=3 <=4 nodes if finished), D_net >= n = m(P). Evidence supports D_net >= m but is NOT informative about the Wall56 regime: m(P) = n on all sets where the search is exact, so the comparison "D_net < m" collapses to "D_net < n", which the F2/RS bounds (NETDOUBLE: D >= rank(I+X_walk), integral D >= n) already forbid for integral networks. The genuine question needs P with m < n, i.e. Gram rank >= 7 (E7 shard, n=63, m <= 49), where exhaustive search is impossible (charts in F2^7: ~10^6 pairs per node, 63 labels).
- Observation [P, from NETATTR tree inequality]: a relay network is the decoder with rows (u_j, f_j), u_j = G N e_j supported on the union of deposit sets of j's descendants; price_j = dim a_j - dim(a_j cap intersect_{k below j} b_k). It beats the natural map only through xf/xb; whether another map exists is the global question.

STATUS at hand-off: enum2 h=3 m=4 (e3_4b.log) done for P={1},{7},{1,2},{1,7},{1,2,4},{1,2,7} (0 feasible); full P={1,2,4,7} still running; h=4 m=3 (e4_3_small.log) n=3 and part of n=4 done, 0 feasible. Both jobs are mine and keep appending; machine load ~8 slows them 4-5x.
