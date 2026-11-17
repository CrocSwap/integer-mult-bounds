# SpecCOV.lean: Lemma COV (corrected), kernel-only
No sorry, no native_decide, 5 s / 2.0 GB. Axioms (all theorems): [propext, Classical.choice, Quot.sound]. Imports `Nov15.SpecTSUR` (pp, Xm, Zm, Nm, product formula `ZN_eq`, `sum_ZY`, `Nm_isUnit`) and `Nov15.Budget` (`SYL.sylvester`).
Source: a spec-break note (item 2), after its audit.

- `char_syl`: product of m reflections P = I - Z Yᵀ, `Z N = X`, N unitriangular: `dim span x + dim span y ≤ m + rank(I - P)` (Sylvester, no char/pairing hypotheses).
- `cover_dim`: subadditivity with overlap corrections: `dim span(v '' union) + #flagged ≤ Σ dim span(v '' S_i)`, a flagged character sharing a factor f (v f ≠ 0) with the earlier union. `finrank_le_cover`: uncovered factors cost ≤ 1 each given span = V.
- `COV_flag` (general form): factors F with x_f, y_f spanning V (note A1: ALL M = 6+U factors); character i has ordered active factors `idx i 0..mm i - 1`, product D i, rank(I-D i) ≤ r i. `2n + 2·#flagged ≤ Σ(r_i + mm_i) + 2·#uncovered factors`.
- `COV_R35`: the exact shape of the audited statement. Factors = jobs J ⊕ Fin U units; character i has active jobs `Sj i` (k_i = |Sj i|) and units iff `q i` (u_i = U or 0), each active factor listed once (`hact`, `hinj`). Overlap = shares a job with an earlier character (x_j ≠ 0 ≠ y_j) OR the unit block with an earlier character (units nonzero). Conclusion: `2n + 2·#overlaps ≤ Σ(r_i + k_i + u_i) + 2·#uncovered jobs + 2U·[no character has units active]`.
- `cov_needs_span`: A1 (spanning) cannot be dropped.

Verdict: the note's statement is TRUE as written (hypotheses made explicit: spanning, per-character product + rank bound, overlap needs a shared factor with nonzero x and y). Not needed: char != 2, y·x = 2, tightness. r_i = #flipped targets enters only via `rank(I - D) ≤ r_i`. Not formalised: the note table/survivor arithmetic (item 3-4), and an earlier "U-free" statement being false (its failure is the U term in the conclusion; no separate theorem).
