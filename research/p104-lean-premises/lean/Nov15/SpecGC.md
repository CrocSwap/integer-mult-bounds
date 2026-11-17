# Nov15/SpecGC.lean 
Formalises the J = 7 kill tools: R68 (GC/II, TWIN, SPLIT-EQ; AUDIT68 SOUND-WITH-FIXES) and R71 L1 (AUDIT71). Kernel-only: no sorry, no native_decide; `#print axioms` on all 14 headline theorems = [propext, Classical.choice, Quot.sound]. 12 s / 2.1 GB. Builds on SpecTS (`model_commute`, `lemmaTS_model`, `refl_sq`), SpecINV (`inv_word`, `det_refl`, `one_sub_pp`), PadLift (`rank_blockdiag`), SpecTSUR (`ev/jobsP/uconj/ucount`, `UR_upper`).
**Verdict: no paper statement is false as written (no counterexample).** Wording fixes only (below).

## Proved
- `jobs_commute` (= `SpecTS.model_commute`): jobs of one tight character commute.
- TWIN: `twin_coeff` (Gram 2I: `y_t . v = 2 c_t`), `twin_rule` (x_j in span x_t, y_j in span y_t, y_j.x_j = 2, every t != t0 adjacent (y_t.x_j = 0 = y_j.x_t) => `refl x_j y_j = refl x_t0 y_t0`, i.e. g_j = g_t), `twin_empty` (all adjacent => dead), `twin_model` (Gram from Lemma TS).
- Split: `split_word` (word with inl = the h odd-man reflections (y.x = 2), inr = commuting involutions: `ev w = R * jobsP w`, `rank(R-1) <= h`, `jobsP w` an involution; h = 1 => R = 1 - x y^T, y.x = 2; only inl letters are conjugated, `uconj_forms_c`). `K_data`: b reflections with Gram 2I => product K involution, `rank(1-K) = b` (non-vacuity example included).
- Kill count: `gap_le` (|r-b| <= rank(D-K)), `gc_strict` (J = RK, rank(1-R) <= h, U + h < gap => False), `gc_h0` (U <= gap, U >= 1 => False; equality: rank(D-K) = gap => D,K commute via `idem_nested`/`invol_commute` => INV), `gc_h1` (R = 1 - x y^T, U+1 <= gap => False: D,K commute, E = DK, rank(R-E) < rank(1-E) => x in col, y in row (`mem_range_of_rank_lt`) => Ex = -x, yE = -y => ER = RE => g = ER involution => INV). Word versions `gc_dead_h0/h1/strict` use `word_up_inv` (rank(D-J) <= U; g involution => rank(D-J) <= U-1).
- SPLIT-EQ: `split_eq_invol` (eps = +-1, det J_K = +-1, rank(eps - J_K) <= [det J_K != eps^(dim K)] => J_K^2 = I; rank-1 outer product + det lemma), `split_eq_dead` (block coordinates (Unit + kappa) + omega: D = eps on V1, J = sigma + J_K + I: `d + [eps != sigma] + [det J_K != eps^dim K] < U`, i.e. the SPLIT bound is never attained when U >= 1).
- L1: `L1` (ucount w = 1, J^2 = I, M = D J: (M-1)^2 = 0, rank(M-1) <= 1, nilpotent (M-1) = unipotent M, tr M = n, det M = 1).

## Wording fixes / hypotheses made explicit
1. RESULT68 "det J_K = -eps^(m-1)": correct exactly when dim K = m-1 (AUDIT68); Lean states the exponent as `Fintype.card n = dim K`.
2. GC kills need U >= 1 (U = 0, gap = 0 is not a contradiction); equality cases use INV (hinv hypothesis), the strict case only the upper bound.
3. h = 1 equality needs only `rank(R-E) < rank(1-E)`; it also uses K^2 = I, which `split_word` supplies from "K letters are commuting involutions" (the classes of the paper must be pairwise commuting involutions).
4. L1 needs J^2 = I (then M = D J = D J^-1 = g is one conjugated transvection); without it M != g.
5. Still INHERITED/unaudited: the model setting of SpecTS (what is a tight character, which jobs are H/K, the r = #flipped targets and b = #odd classes counts: r, b enter as `rank(1-D)`, `rank(1-K)`; for diagonal D use `SpecTSUR.rank_one_sub_diag`, for K use `K_data`).
