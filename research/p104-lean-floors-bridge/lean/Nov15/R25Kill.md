# R25Kill.lean: SPECBREAK R25 kill of the 546 outer words, fully formal on top of LemmaPG. No sorry, ~8 s, 2.4 GB RSS
Lane LEAN-NEXT8, Nov 16. Source: cards/WILD/SPECBREAK/R25/THEORY.md §1, §3; RESULT25.md items 2 and 4.
Axioms: [propext, Classical.choice, Quot.sound]. The word count uses [propext] only.

Build (imports the LemmaPG olean):
  lake env lean -o .lake/build/lib/lean/Nov15/LemmaPG.olean Nov15/LemmaPG.lean
  lake env lean Nov15/R25Kill.lean

**Model.**
- Factors are Mathlib's `LinearMap.transvection f v` (x ↦ x + f(x)·v), so ρ = I − x yᵀ with f = −y and v = x.
  - Jobs (`IsRefl`) have f v = −2. Units (`IsTv`) have f v = 0; degenerate x = 0 or y = 0 is allowed, so U′ < U is covered.
- Products live in the unit group of End V. A word is a `List (G ⊕ G)`:
  - `inl` letters stay in place, `inr` letters are moved right;
  - multiplication order is used throughout, and any interleaving is allowed.
- V = E × F × W, as in LemmaPG.
  - D1 = `T δ` and D2 = `T (−δ)`, where δ = D1|V_− is any involution with det δ = −1 (e.g. diag(−1, 1)).
  - D3 = `S (−1)`, and the pin is σ = `S s` = I ⊕ s ⊕ I with s a reflection of V_−.

**§1 Reductions.**
- `ev_eq` (R1 and R2, "units/b's to the right"):
  - word = (product of the staying letters) · Π(each moved letter conjugated by the staying letters to its right).
- `P3_iff` (R2): fix the shape of the word (where a and a′ sit, and the two moved slots). Then:
  - moved letters in a conjugation-closed set R with product D exist iff A⁻¹D = r1·r2 with r1, r2 ∈ R;
  - this holds for every interleaving, and the converse rebuilds b and b′ (`realize`);
  - `refl_closed`: reflections are conjugation-closed (`tv_closed` for units).
- The rank consequences rank(A − I) ≤ 2 and rank(A − D3) ≤ 2 are proved inside `kill_mu1`.

**§2 (R3).**
- `near_sigmaA` and `near_Asigma` cover A_q = σA and A_q = Aσ. In both:
  - rk(D1A_q − D1σ) ≤ rk(A − I);
  - rk(D1A_q − D2σ) ≤ rk(A − D3);
  - D1σ = T(δs) and D2σ = T(−δs). These identities (`T_mul_S`, `T_neg_eq₁/₂`) are exactly where the pin enters (σD3 = D3σ).
- In `kill_mu1`:
  - X := D1·A_q = g1⁻¹ (needs δ² = 1), so rk(X − I) ≤ U ≤ 2;
  - LemmaPG then applies with w = δs, det w = (−1)(−1) = 1 (`det_refl` via Mathlib `transvection.det`).

**§3 Kill.**
- `tv_list_invol`: over 2 ≠ 0, a product of ≤ 2 transvections that is an involution equals I.
  - This merges the prose's two steps ("det 1 ⇒ rank ∈ {0, 2}" and "rank 2 contradicts R15 Lemma 3") into one elementary lemma.
  - It needs no det and no R15 import.
  - Proof: with c = f1 v2 and d = f2 v1, f2∘g² = f2 at v1 and v2 gives (cd)² = 0, so N = g − I has N³ = 0. Then N² = −2N gives 4N = 0.
- Rank 0: A_q = D1, so A = T(sδ) or T(δs).
  - `eq_one_of_rk_T`: rk(T u − I) ≤ 2 ⇒ u = I.
  - `rk_T1_D3`: rk(T 1 − D3) ≥ 4, which contradicts rk(A − D3) ≤ 2.
- `kill_mu1`. Hypotheses:
  - the μ1 word has staying letters [σ, a, a′] or [a, a′, σ] (q outer);
  - its moved letters are ≤ 2 units, and its product is D1;
  - the μ3 word has staying letters [a, a′], moved letters ≤ 2 reflections, and product D3.
  - Conclusion: False.
- `kill_mu2`: the e1 ↔ e2 mirror. It is `kill_mu1` with δ ↦ −δ (det(−δ) = det δ in dimension 2) and the μ3 word with its tags swapped.
- `kill_outer`: q outer at μ1 OR at μ2 ⇒ False. No consistency between the three words' interleavings is assumed, which is stronger than "one global order".
- `n_jobs`, `n_middle`, `n_words` (by `decide`):
  - there are 30 job words, and 4 have q strictly inside both pairs;
  - with C(7,2) = 21 unit placements that gives 630 words, 84 middle and 546 killed.

**Prose check.** No statement found false.
- Small imprecision in §3, rank-0 case:
  - for A = σD1 the V_− block is sδ, not w = δs. It is conjugate to w (sδ = s·w·s⁻¹), so the conclusion "= I" is unchanged.
  - Lean treats the two cases separately.
- The rank-1 sub-case is not "excluded by det" in Lean: `tv_list_invol` kills ranks 1 and 2 together.

**Not covered.** The 84 middle words (MID, SPEC-BREAK R26, still in progress: R26/ has scripts only, no finished proof). U = 4 cores.
