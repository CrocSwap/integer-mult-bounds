# NETATTR NA (Nov 20, Opus, theory + small exact). Own code in this dir: common.py, rects.py, exact.py (min decoder mass: F2 cover enumeration + Singular GB over QQ), netgen.py, inst5.py/cl5.py/rank1.py/test5.py (h=5 relay instance), cx3.py, cx4.py, cx4brute.py, cx4df.py, shrink.py (counterexamples), chainfuzz.py, chainx.py, chainmin.py, netfuzz.py, tight.py, bowtie.py, bowtie_rulectrl.py. Logs: nf_h4.log, nf_h4ctrl.log, cmin_h4_df.log. 1 python proc + Singular subprocesses, threads=1.
How this differs from NET2DEC, NETDOUBLE and NETTENSOR: those lanes bound D with potentials (ranks of chart images). This lane asks for the UPHASE-type object: actual decoder rows built from clusters of nodes, with Σ price ≤ D. Then Wall56 applies directly.

VERDICT: the deliverable is the MINIMAL NETWORK WHERE EVERY CLUSTER MAP FAILS. A positive theorem holds for a sharp class.
- [P] Counterexample: 2 nodes, 1 relay, D = 2, a 0/1 network.
  - h=3: the decoder must reproduce M∘Q exactly, and the failure is at a diagonal cell.
  - h=4: only the off-diagonal odd cells are required (the diagonal is free), and it still fails.
- Every decoder needs mass ≥ 3 > D in both cases. So no LOCAL (per-cluster) future-attribution map network ⇒ decoder with Σ price ≤ D exists, not even in the weakest, diagonal-free form.
- [P] BOWTIE theorem plus TIGHT-CHAIN contraction: clusters that are bowties after contracting tight chains give one row each, with price ≤ the cluster's drop. Any rational scalars. Hence D ≥ m(P104) ≥ 56 under Wall56 for that class.
- The obstruction is exactly a NON-TIGHT relay (free ascent e = dim a_k − dim b_j ≥ 1) from a depositing node into a gathering node. This is the network form of UPHASE's excluded "multi-epoch" lifetime. Here it is a genuine gap, not an artefact of the method.

## 0. Setting
- NetW over odd labels q_p ∈ F2^h. Node k has charts b_k ⊆ a_k and drop d_k; D = Σ d_k.
- Supports: F_kp ≠ 0 ⇒ q_p ∈ a_k (gather); G_tk ≠ 0 ⇒ q_t ⊥ b_k (deposit). A relay H_kj (j→k) needs b_j ⊆ a_k.
- M = G(I−H)^{-1}F over Q. The target is T = M∘Q on odd cells; even cells are free.
- Decoder: rows (w_i, v_i) over Q with Σ_i (w_i v_i^T)∘Q = T on odd cells. Price_i = rank_F2 Q[supp w_i, supp v_i] (UPHASE §3). Mass = Σ price.
- A CLUSTER MAP is local: the rows assigned to a relay-component K must reproduce K's own odd-cell contribution T_K. This is forced, because every odd cell is visible and the other clusters are arbitrary.

## 1. Brief's first check: the h=5 relay instance (net2dec/ngmin5.log, μ4 = 7 > 6) [C exact]
- The two nodes plus the relay, taken as ONE cluster, give ONE row of price 4 = D (rank1.py): w = (1,1,3,3,1,5/3,1) on readers {1,7,8,14,19,21,28}, v = content r_k.
- Why it works: a_k = b_j (a tight relay), so j's readers cannot see k's gathers (§3, TIGHT-CHAIN).
- Mass ≤ 3 is impossible (exact.py: no cover). So the cluster map is optimal there. The per-node Smith failure is not a cluster failure.

## 2. Positive results [P]
(a) NATURAL MAPS for a 2-node chain j→k. Write A=a_j, B=b_j, A'=a_k, B'=b_k.
- Forward rows (g_j,f_j), (g_k,r_k): mass ≤ D + xf, where xf = dim A − dim(A∩A').
- Backward rows (g_j+ηg_k, f_j), (g_k,f_k): mass ≤ D + xb, where xb = dim(B+B') − dim B'.
- Merged single row (g_k + g_j/η, r_k) when e = dim A' − dim B = 0:
  - price ≤ dim A − dim B' = D;
  - it is exact on odd cells, because f_k lives on labels in A' = B, which are even against j's readers.
- So a chain admits mass ≤ D whenever xf·xb·e = 0. It always admits mass ≤ D + min(xf,xb) ≤ D + min(d_j,d_k).
- D = 1 chains and h = 2 always work: forcing xf, xb, e ≥ 1 is impossible there.

(b) BOWTIE THEOREM.
- A bowtie is a relay-component consisting of:
  - an in-arborescence into a hub (relays point toward the hub), where any of these nodes may gather;
  - an out-arborescence from the hub, where any of these nodes may deposit;
  - no deposits in the in-part, and no gathers in the out-part (the hub may do both).
- Then M_K = w v^T exactly, with v = content of the hub and w = (GN)[:,hub].
- price ≤ rank(U × V) with U = Σ_out b_l^⊥ and V = Σ_in a_k. Since U^⊥ ⊆ b_hub ⊆ V:
  price ≤ (dim V − dim b_hub) + (dim b_hub − dim U^⊥) ≤ Σ_in d + Σ_{out∖hub} d.
- Tree inequality: dim A_k − dim b_k ≤ Σ_{subtree} d, where A_k = a_k + Σ_children A_j. The proof uses submodularity and b_j ⊆ A_j ∩ a_k. The out-part uses the ⊥-dual.
- Special cases: relay-free networks (NET8/E8: one row per node, Σ = 56 = D exactly), in-forests with depositing roots, out-forests, and rendezvous (gatherers → hub → depositors).
- [C] bowtie.py, 2000 trials each at h = 4, 5, 6: 0 odd-cell mismatches, 0 price > drop; tight in 17, 21 and 28 cases.
  - Control with deposits and gathers on both sides: 1921/2000 mismatches.
  - Control with the relay rule dropped: price > drop in 6 (h=5) and 11 (h=6) cases.

(c) TIGHT-CHAIN CONTRACTION.
- Setting: a relay path k_1→…→k_s with a_{i+1} = b_i (tight), external relays entering only at k_1 and leaving only at k_s, and gathers/deposits allowed at every chain node.
- On odd cells this path equals ONE node with a = a_{k_1}, b = b_{k_s}, drop = Σ d, content r_{k_s}, and readers rescaled by 1/Π η.
- Proof: r_{k_s} − (Πη) r_l = gathers at nodes below l, which lie in labels of a_k ⊆ b_l, so they are even against readers ⊥ b_l. The contracted node is chart-legal.
- => THEOREM: if every relay-component becomes a bowtie after tight-chain contraction, there is a decoder with Σ price ≤ D, one row per component. So D ≥ m(P) for the realised pattern, and Wall56 ⇒ D ≥ 56 for that class.
- [C] tight.py: tight-relay networks with ≤ 3 nodes and branching allowed, 120/120 have mass ≤ D. [CONJ] this holds for all tight-relay networks; that statement is not proved.

## 3. THE MINIMAL COUNTEREXAMPLES [P, hand proofs; brute-force cover checks in cx3.py / cx4df.py]
(i) Exact form. h = 3, ports = the 4 odd labels {1,2,4,7}, all scalars 1.
- Node j: a = <1,4>, b = <5>, gathers {1,4}, deposits {7}.
- Node k: a = <2,5>, b = <2>, gathers {7}, deposits {1,4}.
- Relay j→k is legal (<5> ⊆ <2,5>). D = 1 + 1 = 2.
- Odd cells: T(1,1) = T(1,7) = T(4,4) = T(4,7) = T(7,1) = T(7,4) = 1 and T(7,7) = 0.
- Proof:
  1. One row would need Q[{1,4,7},{1,4,7}], which has F2-rank 3. So the decoder has two price-1 rows.
  2. A price-1 rectangle never contains both (1,1) and (4,4), (1,1) and (4,7), or (7,1) and (4,4) (each 2×2 closure has rank 2). So R1 ⊇ {1,7}×{1,7} and R2 ⊇ {4,7}×{4,7}.
  3. Within each row, rank-1 forces w(7)v(7) = T(7,1)·T(1,7)/T(1,1) = 1.
  4. So cell (7,7) receives 1 + 1 = 2 ≠ 0. ∎
- With the original instance scalars (cx3.py) the same argument gives −1 + −1 ≠ 0.

(ii) Diagonal-free form (the wall-relevant local requirement). h = 4, all scalars 1.
- Node j: a = <1,4>, b = <5>, gathers {1,4}, deposits {7}.
- Node k: a = <2,5>, b = <7>, gathers {2}, deposits {11,14}.
- Relay j→k. D = 2; e = xf = xb = 1.
- Off-diagonal odd cells: nonzero (7,1), (7,4), (11,1), (11,2), (14,2), (14,4), all equal to 1. The cell (7,2) is odd with target 0. No diagonal cell is involved.
- Proof:
  1. One row needs F2-rank 3.
  2. The incompatibility graph of the 6 cells (a price-1 rectangle cannot hold both cells of a pair) has edges c1c4, c1c5, c2c4, c2c5, c2c6, c3c5, c3c6. Its 2-colouring is unique: R1 ⊇ {7,11}×{1,2} and R2 ⊇ {7,14}×{2,4}.
  3. No cell of one class lies in the other row.
  4. Rank-1 forces w_i(7)v_i(2) = 1 in each row, so (7,2) receives 2 ≠ 0. ∎
- [C] cx4df.py: all 19,132 rectangles of price ≤ 2 over all port subsets; 49 covers, all of this form. The min mass is 3 (forward map).
- shrink.py derived this instance from a random one.

What the counterexamples share:
- The failing cell is a j-reader × k-gather odd cell, i.e. it lies in the ascent block b_j^⊥ × a_k, whose rank is e.
- Mod 2 the obstruction vanishes (2 = 0), consistent with RS / NETDOUBLE F2 bounds. The gap is dyadic.
- Minimality:
  - 2 nodes is minimal (relay-free networks map);
  - D = 2 is minimal (D = 1 always maps, §2a);
  - h = 3 is minimal for the exact form (h = 2 cannot have xf, xb, e ≥ 1);
  - for the diagonal-free form, h = 4. [C, sampled] h = 3 diagonal-free: 0/150 failures at D ≤ 3.

## 4. Fuzz [C] (exact.py: F2 cover enumeration is complete; Singular GB = <1> proves infeasibility; "feasible" means GB ≠ <1>, i.e. solvable over Q̄, and single-row cases are checked exactly over Q)
- Random legal DAGs, h=4, 2–4 nodes, D ≤ 6 (nf_h4.log): 127 feasible, 0 failures. Random charts rarely give xf, xb, e ≥ 1 with a depositing upstream.
- Control with the relay rule ignored (nf_h4ctrl.log): 3 failures in 102.
- Structured chains with xf, xb ≥ 1 (chainmin.py):

| h | target | D | failures / trials |
|---|---|---|---|
| 3 | exact | 2 | 2/150 |
| 4 | exact | 2 | 9/150 |
| 4 | diagonal-free | 2 | 16/400 |
| 4 | diagonal-free | ≤ 3 | 12/150 |

- Every failure has e ≥ 1, as §2a forces.

## 5. Consequences
- C1 [P] (from §3) "network of cost D ⇒ decoder of mass ≤ D" is FALSE as a target-level statement, even diagonal-free and even for single 2-node clusters. Any network → Wall56 reduction must use the GLOBAL condition M∘Q = diag. By N2D O1, a global reduction is equivalent to the goal itself. Future attribution with clusters cannot close NET-D56 without extra structure.
- C2 [P] Corollary: the §3(ii) target is realised by a network of drop 2 but by no bowtie or tight network of drop ≤ 2. So network normal forms (rewiring to bowties at no extra drop) do not exist in general.
- C3 What remains for D ≥ 56 under Wall56 is exactly the networks that contain a non-tight relay from a depositing node into a gathering node, after contraction. The open questions:
  (a) can such a relay be priced: is mass ≤ D + Σ_{bad relays} e_jk?
  (b) can a P104 diagonal network be shown to avoid such relays, or can they be removed GLOBALLY using diag + Wall56-tightness?
  (c) toy NetWall vs Wall: find a small odd-label set P where the min network drop for the odd PATTERN is < m(P). That would show no reduction exists at all.

NEXT:
- (c) is the decisive test. Use small h (4 or 5), with exact.py for m(P) and a search over network drops.
- A Lean lane for §3(ii) (finite, hand proof above) and the BOWTIE theorem (tree inequality plus rank-1).

## LEANCONTRACT addendum (Nov 20, Lean, kernel-checked: Nov15/NetContract.lean; notes cards/WILD/NOVEL/leancontract/NOTES.md)
- 2c is now [P] in Lean for iterated SERIES contraction (j has the single out-relay to k, k the single in-relay from j, a_k = b_j): legal network, drop EXACTLY preserved, G N F preserved on ODD cells only (even cells lose G_j F_k/eta). With BNet: mass(pattern) <= D(original) if some iterated contraction is a bowtie; Wall as hypothesis. Toy: tight chain, not a bowtie, bowtie after one contraction.
- Gaps: (a) branching tight edges (extra in-relay at k or extra out-relay at j) not contracted; (b) closure under contraction does not imply bowtie; (c) non-tight relays untouched (the NA 3 gap); (d) 56 corollary needs Wall56@Q96 as hypothesis.
