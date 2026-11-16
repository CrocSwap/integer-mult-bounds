# RDEP2 — R-dep s>=2 / N2; tight m s+t<=7; O4-2 DR §6 overlap GAP + shared-swap-line term (Oct 16)
## STATE
- RDEP2: ~75k. Read PLAN, TWOSIDE, AUDIT-TS, O4-2, AUDIT-K1, BX README. Working on (c) (pure theory). (a),(b) not started.
- RDEP2: DONE ~95k tokens. (c) done as theory (§1-§3 below). (a) R-dep s>=2/N2 and (b) tight m s+t<=7: NOT attempted (budget); status unchanged from TWOSIDE §2 / BX R2-R3.

Labels: PROVEN (here, mod named imports) / OPEN. No scripts (no finite step used). Notation O4-2 §1-§6.

## §1 DR without SEP: one inequality replaces the matroid-union condition (PROVEN mod O4-2 Lemma T, M2, Pay(b),(c) — none uses SEP)
Row side. T_D := lines carrying a sigma=1 D-row-swap (one per line, M2); T_X := distinct swap lines of X-type column pivots; T := T_D ∪ T_X.
Every v ∈ T lies in ∪S_a: the swap term j at v (j ∉ Pi; for X lines j = rho_b, ok since Pi ∩ Pi' = ∅) has o_j := p_j − C'x_j = Σ_a omega_j[a] lambda_a,
p_j(v) = 0, (C'x_j)(v) ≠ 0, so o_j(v) ≠ 0. Take V_a := a basis (label rank) of T ∩ S_a in Pay(b): c(pi_a) >= rank_l(T∩S_a) − r_a, r_a := r_a(V_a) <= dim(U_{S_a} ∩ Z_A);
Pay(c) (no SEP) still gives r_a >= 1 only for F_col / X' / O and r_a <= 1 for F_col, X'. Then, exactly as DR §5 (#X counted with multiplicity = |T_X| + SH_row,
|T_D ∩ T_X| <= #XM_row):
  **(IN_row) Σ_a rank_l(T ∩ S_a) >= |T|  suffices** (only the set T itself; no condition on subsets T' — the §6 "matroid-union" condition was stronger than needed).
**Theorem DR' (PROVEN, any s,t >= 1, SU both sides, Pi ∩ Pi' = ∅, SEP dropped):**
  cost(D) >= 64 − #F_row − #F_col − Σ_O r_a − Σ_O' r'_b − #XM − #SH − δ_row − δ_col,  δ_row := (|T| − Σ_a rank_l(T∩S_a))^+ (dually δ_col),
  SH := #(surplus X/X' pivots sharing a swap line) = (#X − |T_X|) + (#X' − |T'_X'|)  (AUDIT-K1's fix term, now derived).
(Under F_col the r=1 "|V''| odd >= 3" refinement used orthonormal V and is dropped; F_col is counted in #F_col anyway.)

## §2 The class lemma and when δ = 0 (PROVEN mod Pay(a)'s "pairwise non-orthogonal swap lines ⇒ Bd[V,V] = I ⇒ independent labels")
Class of v ∈ T: P(v) := (lambda_1(v),...,lambda_s(v)) ∈ P(K^s) (≠ 0 by §1). v ∈ S_a ⇔ P(v)_a ≠ 0.
**Lemma CL.** Two lines of T in the same class are not orthogonal. Hence each class C is Ω-orthonormal, so rank_l(C) = |C|.
*Proof.* Let j swap at v, o_j ∈ L := span(lambda). supp(o_j) ∩ O_{u_v} = {v} (O4 §(i): p_j and C'c_v both vanish on O_{u_v} ∖ {v} ⊇ v^⊥). If P(w) = c P(v), c ≠ 0, then every element of L
takes at w c times its value at v, so o_j(w) = c o_j(v) ≠ 0, w ∉ O_{u_v} ⊇ v^⊥. ∎ (This is exactly where SEP was used in Pay(a); SEP = "one class per direction".)
**Corollary (list colouring ⇒ δ_row = 0).** Let H be the graph on classes (C ~ C' iff some v ∈ C, v' ∈ C' are orthogonal). If H has a proper colouring a(C) with a(C) ∈ supp P(C),
then V_a := ∪_{a(C)=a} C ⊆ T∩S_a is pairwise non-orthogonal, orthonormal, independent, and Σ_a rank(T∩S_a) >= Σ_a |V_a| = |T|. In particular δ_row = 0 if
 (i) SEP holds on T only (each v ∈ T in exactly one S_a) — weaker than SEP; or (ii) the classes admit a system of distinct representatives a(C) ∈ supp P(C), e.g. whenever
 the class vectors are linearly independent in K^s (a nonzero maximal minor contains a nonzero permutation term) — in particular #classes <= 1, or 2 classes.
General bound: δ_row <= min over matchings M (classes → coordinates in supp) of Σ_{C unmatched} |C|; δ_row > 0 ⇒ Hall fails (one-way: the colouring route can still give 0).
 Size bound (C6 g-table): with n_a := |T∩S_a| <= 11, δ_row = Σ_a (n_a − rank_a) − (Σ_a n_a − |T|) and n_a − rank_a <= 0 (n_a<=3), 1 (4), n_a−4 (5..8), n_a−5 (9..11).
**Necessary shape of δ_row > 0:** s >= 2; some T∩S_a has F2-dependent labels, so >= 4 lines (g(2) = 2: three labels are independent) from >= 2 classes joined in H;
a Hall violation: a set 𝒦 of >= 3 classes with |∪_{C∈𝒦} supp P(C)| < |𝒦| (e.g. K = F2, s = 2: all three points of P(F2^2) occur); |S_a| <= 11 (SU at pivot). Exact residue (c1) = such configurations.

## §3 SH-move: the shared-swap-line surplus is an exact m-decreasing move (PROVEN; transpose of O4-2 XM-move)
pi_a, pi_a' row pivots (x = 0, p = lambda_a, lambda_a') both column swaps at w: y_a' = c y_a (both ∝ c_w). e := q_a' − c q_a = Σ_b e_b mu_b is pure column-outside.
(e = 0: q's proportional, Lemma D merge.) Identity: lambda_a q_a^T + lambda_a' q_a'^T = (lambda_a + c lambda_a') q_a^T + Σ_b e_b lambda_a' mu_b^T; add e_b lambda_a' to p_{rho_b}
(rho_b ≠ pi_a, pi_a' since Pi ∩ Pi' = ∅): exact, m − 1 terms. Cost: the merged term has rows ⊆ S_a ∪ S_a', columns A_a; U_{A_a} = U_{A_a'} = W_w (Lemma T column step
under SU), so its cost <= rho(S_a,A_a) + rho(S_a',A_a') = c(pi_a) + c(pi_a') (pairing rank is subadditive in the row span). rho_b's row grows: increase <= dim(U_{S'_b} ∩ Z_{R_rho_b}) =: def'(rho_b).
**Δ <= Σ_{b ∈ supp e} def'(rho_b),** and def'(rho_b) >= 1 forces Z_{R_rho_b} ≠ 0, hence (catalogue, SU) rho_b ∈ F_row ∪ X ∪ O' (def' <= 1 for F_row, X).
So an SH pair is removed at zero cost (m −> m−1, one X' credit lost and one r = 1 debit lost) unless supp e meets the already-residual column pivots F_row ∪ X ∪ O'.
The e = 0 (Lemma D) branch carries the same caveat. The move is separate from DR' (DR' already debits #SH); it only serves to drive SH to 0. Caveat (same as XM-move): the result is not in Pi-normal form (direction a' loses its pivot); re-gauging before re-applying DR' is bookkeeping not redone here.

## Exact residue after RDEP2
(c1) δ_row/δ_col > 0: s >= 2 configurations of §2 (>= 3 linearly dependent classes on swap lines, a dependent T∩S_a with >= 4 lines). Finite in principle (|S_a| <= 11) — not run.
(c2) SH pairs whose e meets F_row ∪ X ∪ O' column pivots (Δ <= #such), plus the re-gauging bookkeeping of §3 and of the XM-move.
(c3) §6 O-move/O-residue, F, XM unchanged; O4-2 §7 (SU failure, K_small ≠ K^s, forced Pi∩Pi' ≠ ∅) untouched. DR' keeps every DR hypothesis except SEP (SU, Pi∩Pi'=∅, catalogue, L3.1, micro.py, chk1; catalogue/L3.1/S0 unaudited per AUDIT-K1).  (a), (b): unchanged (TWOSIDE §2, BX R2/R3).
