# QZBUILD QZB (Nov 20, Opus; construction + exact verification). Own code: qzcore/qzfast (word-level model + batched LM),
qzword (model -> C1-schema word), qzcheck (independent exact replay over Q(i)[D] at q = 1,-1,i,-i), qzchain (exact CB chain),
qzml (exact ML-chain), qzdrive/qzclimb/qzclimb2/qzexact (numeric search + rational fixing). 1 heavy proc, threads = 1.
Why this differs: QZERO proved Q = 0 words exist (C1, k3) and the LIFT reduction; nobody had BUILT a Q = 0 word at k >= 4.

## 0. Word-level model [P, derivation; validated C exact on every built word]
Pull every D-incidence back to the start frame: incidence e = rank-1 idempotent pi_e = v_e w_e^T (+frame, q = 1).
A HOST(s,t,a,b) with its two contacts gives the twist V_t = I + 2ab(vs ws^T + vt wt^T) - 2a vs wt^T - 2b(1+ab) vt ws^T.
The -frame (q = -1) has pi^-_e = L_e^{-1} pi_e L_e, with L_e = product of the twists up to e.
Legal  <=>  prod_e (I + (D^{S_e} - 1) pi^{+-}_e) = diag(D^M) in both frames, and prod V_t = -I.
Any such rational data assembles into a legal C1-schema word (prefix matrices + ADD/SCALE + LAMBDA wrappers).
Check: C1's design was re-solved numerically, rationalised and re-verified exactly (w_c1design.json, 107.91).

## 1. Laws met on the way
- [P] CB model (every stage block a coordinate projection). Tightness n = 2k-2 forces a NESTED CHAIN U_1 c ... c U_{k-1} = U_k = all.
  Reason: a laminar forest gives n <= 2k - 2*#leaves. Then d_j = rank(P_j + I) = |U_j| - 2(j-1).
  A "reset" (d_j = 0 mid-word) forces lambda = -1 at the next stage. Proof: col/row spaces of a rank-2 + rank-2 split.
  So the CB optimum is |U_j| = 2j, with all-singleton roles of degrees 2 x (k, k-1, ..., 2).
- [P] Pure-role sign: a role whose pieces are all coordinate (pi = e_r e_r^T) is fixed by every twist, so prod V e_r = e_r. Contradiction.
  Pure roles therefore need non-coordinate (relayed) pieces.
- [P] Middle pieces. A piece placed after time j must commute with P_j (both frames). In the chain frame that means it is a
  (-1)-eigenvector pair of P_j, and that space has dim 2(j-1). Pieces at the start or end are frame-free.

## 2. Builds (all [C exact], qzcheck LEGAL at 4 q with symbolic D, WF, a,b != 0, ab != -1, D >= 2, |Iota| = 2k = n+2)
- CB chain (qzchain.py, chain_k*.json): k3 107.91 (= C1 class), k4 108.21, k5 100.24, k6 87.60.
- ML-chain (qzml.py, ml_k*.json): the chain frame plus, at every level j = 2..k-1, 2 pieces with stage set = all later stages.
  Each piece is a (-1)-eigenvector pair of P_j, flag-biorthogonalised. J blocks are J_t = E_{U_t} - (earlier pieces), with rank 4
  (2 contacts + 2 idle singletons) at the middle stages. The numeric climb found the k4 case first (113.84); the general recipe is exact.
  qz1 (independent) on ml_k5: Legal, |Iota| 10 = 2k = n+2, rank K 2, prod V = -I, K-block dets 5, -43/6, 9/4, 23/4, 7 (lambda != -1).

| k | best real (ML) | HP(k) | bar 128.891 | real - bar | real - HP |
|---|---|---|---|---|---|
| 4 | 113.843 | 127.395 | | -15.05 | -13.55 |
| 5 | 115.426 | 133.804 | | -13.47 | -18.38 |
| 6 | 115.219 | 137.557 | | -13.67 | -22.34 |
| 7 | 114.191 | 139.867 | | -14.70 | -25.68 |
| 8 | 112.773 | 141.321 | | -16.12 | -28.55 |
| 9 | 111.172 | 142.235 | | -17.72 | -31.06 |
| 10 | 109.497 | 142.792 | | -19.39 | -33.30 |
| 11 | 107.806 | 143.107 | | -21.09 | -35.30 |
| 12 | 106.132 | 143.251 | | -22.76 | -37.12 |
| 13 | 104.492 | 143.273 | | -24.78 | -38.78 |
NOT LOUD. The best real ĉ peaks at k5 (115.43) and falls about 1.2-1.7 per stage after that. The type-LP / HP is loose by 18-39 on built words.

## 3. Numeric negatives (word-level solver, residual stalls; evidence only, not proofs)
- k3, C1 masks with the 4 idles merged into two {0,1} pieces (= HP(3) 115.42): all 30 order/placement combos stall at 5e-4.
  The stall limit is ab -> -1 (lambda = -1) with entries blowing up.
- ML k5 with the 6 middle idles merged into 2 end/start pieces {1,2,3} (126.11): stalls at 1e-3 or worse (warm and random starts).
- RB nested k5 frame (113.96), 3 orders x 3 tries: no solution. CB-reset k4 (116.1): stalls at 1e-2 (lambda = -1 limit, as proved).
- Climb from ML k5 (merge moves, all placements): see section 4.
- Rational fixing of generic numeric solutions often lands on irrational coordinates. Exact words came from the theory recipes.

## 4. Climb log (t_climbml5.log)
Warm-started merge climb from the exact ML k5 word, every placement (start/end/around the stages), 3 tries each.
All 47 candidate merges (values 117.68-119.06) failed: min residual 1.7, typical 3-7. ML k5 is a local maximum for merges
[C numeric, weak: 3 warm tries/candidate]. The k4 random-start climb from the chain reached exactly the ML k4 design (113.84) and stopped.

## 5. What it suggests
- Singletons are the cost driver. The ML words carry 4k-4 singletons (2k mains + 2k-4 idles). The idles are forced in chain frames:
  middle pieces at time t are capped by dim ker(P_t + I) = 2(t-1), and ML saturates that cap.
- [CONJ] true caller law (Q = 0, lambda != -1) is closer to ~115 at k5 and decreasing than to HP(k)'s 143.
  The LP misses the per-time eigenspace capacity: pieces placed in the middle need -1 eigenvectors of the prefix, at most 2(t-1) by time t.
  A type row "#pieces covering stage t placed before t <= 2(t-1)" is order-dependent. Start/end pieces escape it and are the open case.
