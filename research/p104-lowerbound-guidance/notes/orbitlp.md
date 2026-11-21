# ORBITLP OL (Nov 20, Opus, theory + exact compute). Own code in this dir. venv python, 1 proc, threads=1; C for enumeration (rect.c 2 min, < 1 GB).
Why not a retread: FULLWALL §2 did a monotone orbit LP on P112 only; W9 §3 and W57 §3 bounded test-set and frame duals. Here: P104, exact duals over ALL
rectangles, plus a complementary-slackness filter that settles which laws can ever reach 56, and a new E8-tight rank law (§3) that HC/VC did not have.

VERDICT: Wall56 NOT proved; 8-row mod-4 price <= 6 NOT ruled out. Found:
(a) a closed first-moment barrier on P104 [C exact duals + P];
(b) the DOUBLING LEMMA [P]: C >= rank_F2(I+X) (HC had rank/2). It is tight at E8 (56 = 56) and gives a new bound for split decoders, 104 (was 52).

## 1. First-moment orbit LP on P104 [C, exact]
- Geometry: 104 labels, 759 frames, |Aut| = 384 (aut.bin re-verified: each perm preserves Q and the frame set). Port orbits 32/48/24, frame orbits 20. rank_Q Q = 104.
- Rows: every maximal rectangle (D,S) = (L∩M, L∩K^perp), M label-closed, K ≤ M. lcs.c finds 4,802,502 label-closed subspaces (16,681 Aut orbits).
  rect.c computes each rectangle's exact F2 price and its Aut-symmetrised coefficients. This gives 5,596,046 distinct profiles (prof.npy).
- Families: FRAME (>= 8 active rows per frame, any m) and DIAG (each port lies in D∩S of some row). LP with column generation; the dual is re-checked exactly against all 5.6M profiles (verify_dual.py, 0 violations).
  FRAME only: LP = 11.1543. Certified bound 3485639/312500 = 11.1540 (dual_F.json).
  FRAME + DIAG: LP = 16.4966. Certified bound 20620539/1250000 = 16.4964 (dual_FD.json).
- SOUND: the E8-56 decoder (x8fix data, 8 rows of price 7, 0 mod-4 violations) is feasible. Each E8 row meets all 759 frames and |D∩S| = 28.
  The dual LHS of an E8 row is 1.39 (F) and 2.89 (FD), far below its price 7.
- Fractional optimum: only price-1 rows. These are odd bicliques, mostly with D∩S = ∅, each meeting 300-600 frames. This is the same picture as P112 (FULLWALL 18.9).

## 2. Complementary-slackness filter [P, short]
- Let a family of valid inequalities sum_k f_j(row_k) >= b_j be given, over any type refinement (supports, odd patterns, values). If its LP over type counts is >= 56, then E8 (feasible, cost 56) is LP-optimal.
  Every Aut image of E8, and E8 plus any price-0 rows, is then optimal too. So every inequality with positive dual weight is TIGHT on all of them.
  Corollary: LP(family) >= 56 implies LP(its E8-tight subfamily) >= 56. Slack laws can raise the LP value, but they can never be part of a 56 certificate.
- Laws that are slack at E8 [C]:
  DIAG cover: E8 covers each port 2x (96 ports) or 4x (8 ports).
  VC diagonal charging: sum|P_k| = 224 vs 104; o(t) = 4 on 8 ports, so every Aut-orbit sum is slack.
  Lifted rank with Qt = Q or (J+G)∘(J+G): 344 vs 104.
  Line/Hall port covers: 4 rows per port vs 1.
  Tight: FRAME. A rank-2 Phi (zero on even cells, diagonal nonzero) has its ports split into cliques A_pq by orientation (x_t^perp, y_t) in P^1, and it vanishes on A_pq × A_qp [P].
  If U has a single class, Phi is a scaled J ⊕ J, i.e. two frame laws [P]. The multi-class case is not settled [CONJ: no new tight law].
- So every row-additive support or rank certificate built from these families stays at most 11.154 if it is E8-tight. The diag/rank families add slack only.
  This explains rigorously why VC/VC2's charging stalls at 42 in the branch that contains E8. A 56 proof needs E8-TIGHT laws that are not row-additive.

## 3. DOUBLING LEMMA [P] — any number of rows, half-integer decoders (via HC's mod-4 reduction)
Setting: rows w_k = a_k + 2w'_k, v_k = b_k + 2v'_k (mod 4); D_k, S_k = supports mod 4; r_k = rank_F2 Q[D_k,S_k]; C = sum r_k. All matrices over F2 and masked to odd cells.
Y = sum diag(w'_k) Q diag(b_k), Z = sum diag(a_k) Q diag(v'_k), E = sum diag(w'_k) Q diag(v'_k), X = (N/2 mod 2), N = sum (a_k b_k^T)∘Q. HC: Y + Z = I + X.
LEMMA (master form). For ANY F2 vectors y_k ⊆ D_k and z_k ⊆ S_k:
  C >= rank [[Ŷ, *],[0, Ẑ]] >= rank Ŷ + rank Ẑ,  where Ŷ = sum diag(y_k) Q diag(b_k) and Ẑ = sum diag(a_k) Q diag(z_k).
Proof: P_k = [diag(y_k); diag(a_k)] · Q · [diag(b_k), diag(z_k)] factors through Q[D_k,S_k], so rank P_k <= r_k.
  The sum of the P_k is [[Ŷ, *],[sum diag(a_k)Qdiag(b_k), Ẑ]]. Its lower-left block is 0 by the mod-2 law. A block-triangular matrix has rank >= rank Ŷ + rank Ẑ. ∎
- Taking y = w', z = v' gives C >= rank Y + rank Z >= rank(I+X). HC had C >= rank(I+X)/2, from rank B_k <= 2r_k. The twisted block shares one price between the Y- and Z-parts.
- O-FORM [P]: let O be the set of ports with an odd w-entry in some row and an odd v-entry in some row. Then rank(I+X) = 104 − |O| + rank(I+X)[O,O]. Proof: X is supported on (odd-w ports) × (odd-v ports); eliminate the unit rows and columns.
  So any mod-4 decoder with C <= 55 has |O| >= 49 + rank(I+X)[O,O].
- SPLIT decoders (no port odd on both sides) cost >= 104. Here |O| = 0. VC5's split bound was max(|A|,|B|,52).
- TIGHTNESS [C dbl.py]: E8-56 gives C = 56 = rank[[Y,E],[0,Z]] = 28+28 = rank(I+X), |O| = 104.
  Doubled trivial 0/1 decoder: C = 208 = master max (y = 1_D, z = 1_S).
  Checked against the proved inequalities (all hold, often with equality): GL8(Z4) images of E8, splits, cancel pairs, zeroed ports, and 2 random walks (C = 90).
  HC's per-row rank B_k = 14 = 2 r_k at E8 is exactly the factor this lemma removes.
- The bound is not row-additive. It is a matroid rank (Rado): rho_B = max_y rank Ŷ = min_J [dim sum_{t∈J} R_t + |L∖J|], with R_t = span{b_k∘Q_t : t ∈ D_k}. rho_A is the same by columns.

## 4. What is still missing (the next law)
- Wall56 for half-integer decoders, ANY m ⟸ [CONJ, E8-tight] rho_A + rho_B >= 56 for every mod-4 decoder of P104. Equivalently: no decoder has both master maxima small.
  rank(I+X) >= 56 alone is FALSE: 0/1 decoders have X = I. Those are caught by the master max (208 on the doubled trivial decoder), not by y = w'.
- Lower bound needed: the subspaces R_t = span{b_k∘Q_t} (and R'_s) must be spread over many ports. Cheap rows (7-dim side) give R_t ⊆ (8-dim pieces).
  Route: Rado's min over J, plus the frame law (every frame has >= 8 active rows), plus all-or-nothing in the 8-row case.
- 8-row mod-4, price <= 6: §3 adds |O| >= 49 to VC/VC2. Branch cases are not redone.
FILES: geo.py, dump.py, lcs.c, rect.c, lpcg.py, verify_dual.py, dual_F.json, dual_FD.json, e8.py (e8W/e8V.npy = E8-56), carry*.py, dbl.py, dbl2.py, walk.py, verify.sh. prof.npy (1 GB) can be regenerated by rect.c.
