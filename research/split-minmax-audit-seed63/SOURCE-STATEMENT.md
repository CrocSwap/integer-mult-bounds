# PR2162 section 3 — frozen audit input

Source: CrocSwap/integer-mult-bounds, commit `113a718265c62aec301c5695f4bfb9c421bef7ab`, `research/char2-jets/README.md`.
Original author: DreamingOfClouds; substantial Claude Opus 5.5 assistance.
Apache-2.0; repository LICENSE applies. Only section 3 is retained.

## 3. The generic-rank / split bound

By Lemma GR the best bound of this kind is GR(B) := rank over F2(X, Y) of B ∘ XYᵀ (X_tj, j ∈ π(t), Y_sj, j ∈ σ(s), indeterminates). **PROVEN (Lemma Split).** Mod 2, det(B ∘ XYᵀ) = Σ_σ Π_t B_{tσ(t)} x(t)·y(σ(t)); the coefficient of the monomial Π_t x_{a(t)}(t) Π_s y_{b(s)}(s) is per(B ∘ K_ab) = det_F2(B ∘ K_ab), with K_ab[t, s] = [a(t) = b(s)], and after permuting B ∘ K_ab = ⊕_c B[R′_c, A′_c] with R′_c = a⁻¹(c) ⊆ R_c, A′_c = b⁻¹(c) ⊆ A_c. The same argument on minors gives
 **GR(B) = SPL(B) := max over row-partitions {R′_c ⊆ R_c} and column-partitions {A′_c ⊆ A_c} of Σ_c rank B[R′_c, A′_c]**,
and GR(B) = v iff a *perfect split* exists (three square nonsingular submatrices, one inside each block, whose row sets partition the lines and whose column sets partition the lines); a perfect split gives cost(B) ≥ v directly.
**Quoted, not proved here:** the independent-matching (Rado–Edmonds type) min-max SPL(B) = min_{S,T ⊆ [v]} (v − |S|) + (v − |T|) + Σ_c rank_F2 B[S ∩ R_c, T ∩ A_c]. "≤" is elementary; equality is cited from the matroid-union / linking-system literature from memory. CHECKED (recorded, `scripts/t9.py`): 300 random instances, v = 3–6, 92 of them with SPL < v, 0 mismatches. **Conditional corollary:** if (A) holds for every sub-configuration, then Σ_c rank B[S ∩ R_c, T ∩ A_c] ≥ |S ∩ T| ≥ |S| + |T| − v, so SPL(B) = v; hence, *given the min-max*, (A) at T = 3 ⟺ every admissible B on every configuration has a perfect split. The anti-Fano obstruction of §4 is an obstruction to the *diagonal* (CR2) form only, never to the generic form (GR = v for 100 random B at each of four densities on `tied_min`, `cex_min_1`, `gad`, `aff14`, `cex_joint_v7`: recorded, `scripts/t7.py`).
