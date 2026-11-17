# Nov15/SpecRankP2.lean 
Formalises the U = 4 step of the #7 kill (RB4 item 4 / AUDIT item (c)), extends SpecRankP (`rank_ge_four`) and SpecINV (`inv_rank`). Kernel-only: no sorry, no native_decide; all 7 `#print axioms` = [propext, Classical.choice, Quot.sound]. 13 s / 2.1 GB (needs SpecRankP.olean built with -o first).

## Result: the paper step is TRUE, and stronger than stated (no strata needed)
ρ = I - e1 (2 e1*)ᵀ = diag(-1 on e1, +1 elsewhere) (`rho`, `rho_eq_refl`), J = I - x yᵀ with y·x = 2 ARBITRARY x, y (no V, Y, pairing, q(v) hypothesis), N = ρΔ = diag(-1 on e1, S; +1 on ancillas).
- `anc_zero`/`anc_zero_both`: rank(N - I + x yᵀ) ≤ 4 ⇒ x and y vanish on every ancilla (kernel-dimension count: if x has an ancilla coordinate, ker ↪ K^ancillas, so rank ≥ 5; y by transpose). Any field with 2 ≠ 0.
- `JNJ`: x, y supported on {e1} ∪ S, y·x = 2 ⇒ J N J = N (so J commutes with N, J² = 1).
- `rhoJ_invol`, `Jrho_invol`: rank(Δ - ρJ) ≤ 4 ⇒ PΔP = Δ for P = ρJ; same for P = Jρ. (Δ - ρJ = ρ(N - J), Δ - Jρ = (N - J)ρ.)
Consequence: the whole Singular stratum analysis (st1/st00/st01, dim V = 1, A/B/C0/C1) is subsumed by a 1-page argument valid for ALL x, y, in every characteristic ≠ 2 (closes "char p > 2" for this step).
- `spec7_dead_U34`: char ≠ 2, U ∈ {3,4}, Λ = P⁻¹Δ i.e. P·pp(xt,yt,U) = Δ with transvection units (y_i·x_i = 0), P ∈ {ρJ, Jρ}, x_J ∈ V ∋ e1, dim V ≤ 2 ⇒ False. Proof: det P = 1, im(P - I) ⊆ V ⇒ rank(Δ - P) ≥ 4 (SpecRankP); Δ - P = -P(1 - Λ) so rank ≤ rank(1-Λ) ≤ U (kills U = 3); U = 4 ⇒ rank ≤ 4 ⇒ PΔP = Δ ⇒ Λ² = 1 ⇒ inv_rank gives rank(1-Λ) ≤ 3 < 4.

## Not proved (hypotheses)
Theorem A (Λ_μ is a product of U transvections), and the 15-class / KB reduction that for every one of the 720 job orders some unit character has P_μ ∈ {ρJ_Y, J_Yρ} (RB3/RB4 3a/3b, Lemma CIL) are hypotheses (`hΛ`, `hP`). U ≥ 5 not covered. Note the Lean theorem needs no ancilla count, V-pairing or char-0 hypothesis. The RB4 general "two reflections with q(v)=0 ⇒ involution" claim remains unproved here (and the AUDIT found it false on a stratum); it is not needed.
