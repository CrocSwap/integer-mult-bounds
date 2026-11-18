# SpecTSUR.lean: spec-break R42 Lemma TS + Lemma UR, kernel-only 
No sorry, no native_decide, ~8 s, 2.1 GB RSS. Axioms (all headline theorems): [propext, Classical.choice, Quot.sound].
Source: internal notes §1-5 + AUDIT42.md. Matrices over a field K, coordinates `n`; jobs `refl x y = 1 - x yᵀ`; ordered product `pp x y m` (prefix product).

**Product formula** (`pp_eq`, `zv_rec`, `ZN_eq`): `pp m = I - Z Yᵀ`, `Z N = X`, `N = I + strict-upper(G)`, `G_ij = y_i·x_j`. Proved by telescoping, any ordering.

**Lemma TS (`lemmaTS`).** char ≠ 2 (2 ≠ 0), product of m jobs = diag s (s = ±1), #flipped = m (tight). Then
(i) Gram y_i·x_j = 2 δ_ij (G = 2N, N unitriangular => G = 2I); (ii) x_i, y_i vanish on every unflipped coordinate (so jobs never touch a dark target); (iii) range(I - D) = span(x_i).
Paper true as written. Remarks: y_i·x_i = 2 is NOT a hypothesis, it is a conclusion; `tight_needed`: r = k cannot be dropped (two equal jobs on Fin 1 over ℚ multiply to I, r = 0 < k = 2, Gram not 2I).

**Lemma UR.**
- Upper (`UR_upper`): word in the unit group of matrices, letters inl = unit (rank(t-1) ≤ 1), inr = job; moving jobs right conjugates each unit by the jobs to its left (`ev_move`, mirror of R25Kill.ev_eq) => rank(ev w - J) ≤ #units, J = ordered product of ALL job letters.
- Lower (`UR_lower`): V = V₁ ⊕ V_dark (index `n₁ ⊕ nd`), J = (Gram-2I clique product) ⊕ I, D = diag s₁ ⊕ diag sd: rank(D - J) ≥ d + |k - r₁| (truncated subtraction, one term is 0). Uses rank(XYᵀ) = k (`rank_clique`, needs 2 ≠ 0), rank(I - diag s) = #flips (needs 2 ≠ 0), block-diagonal rank additivity (`rank_fromBlocks_diag_ge`, proved here, not in Mathlib).
- Combined (`UR_combined`): both with the SAME J, which is exactly the audit's hypothesis "the clique = ALL active jobs of μ" (UR_upper needs J = all active jobs, UR_lower needs J Gram-2I); D = word product. Conclusion U ≥ d + |k - r₁|.
- Not formalised as a theorem: the paper's "D₁ - J₁ = -2Π_R + 2Π_W" form (only the rank-subadditivity consequence is used, as in the audit); the "every job in some tight set => V = V₁ ⊕ V_dark" bookkeeping (taken as the block hypothesis).

**R26#10 (`r26_10`).** d = 1, r₁ = 0, k = 3 (ACE clique at μ = 13) as hypotheses => ucount w ≥ 4, so U = 3 impossible. `r26_arith`: the other five kills have the same arithmetic (#11-#14: (1,0,3); #8: (2,1,3) => 2+2 = 4).

**Verdict: no paper slip found** in TS or UR as audited (AUDIT42's fixes = the two hypotheses, now explicit). Hypotheses are exactly: char ≠ 2; tightness r = k for TS; clique = all active jobs (same J) for UR.
