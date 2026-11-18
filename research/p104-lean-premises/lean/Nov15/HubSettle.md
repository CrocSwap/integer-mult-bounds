# HubSettle.lean: rebuild joint-hub derivation (alt/r2; internal log ALT r1/r2). No sorry, ~6 s, 2.1 GB RSS
Imports the RankLaw olean (see header). Axioms: [propext, Classical.choice, Quot.sound].

**Setting** (matrix level, any field K).
- V-enders' end rows after the mid program (both hubs deleted): [X_n | X_0], with columns split as non-G0 | G0. Their targets: [R_n | R_0].
- Non-V rows: G0-parts R_n0 and targets F_n0. Their non-G0 parts are hub-invariant and assumed exact.
- U0 spans `kerPart X_n X_0` = {y·X_0 : y·X_n = 0}; V0 spans `kerPart R_n R_0`. Both are indexed by the same ιU (n = |ιU|; 616 on #7623).
- `Valid M`: R_n0·M = F_n0 and the V mix exists for [X_n | X_0·M] (RankLaw.VMixM).

**Why a prefix is a right multiplication** (`run_mapRows`).
- In TokenCancel's op model, any linear change L of the initial rows commutes with the whole run, provided L fixes the tokens of later births.
- So a {0}-prefix acting on the {0}-born rows turns the end rows into [X_n | X_0·M].
- With no MOVE into {0} and none out of V (TokenCancel T1), the deleted hub ops are exactly such a prefix plus a V suffix. That reduction stays the [C]/T1 input.

**Results.**
- `prefix_valid` (the gauge is GL_n). Assume:
  - one valid prefix M⋆ exists (the native's);
  - rows(R_n0) + rows(U0) span K^{G0} (square invertible stack on #7623).

  Then for EVERY invertible G, any M with R_n0·M = F_n0 and U0·M = G·V0 is valid.
  - Proof: M − M⋆ kills rows(R_n0) and sends rows(U0) into span V0, so it shifts the V-ender span only inside its own kernel part (0 ⊕ span V0).
- `prefix_formula`: if [R_n0; U0] is square (via e) with unit det, then M = [R_n0;U0]⁻¹[F_n0; G·V0] satisfies both block equations and the spanning hypothesis.
- `prefix_gauge` (converse): every valid M has U0·M = G·V0 for some G. G is invertible when U0 and V0 have independent rows and M is invertible.
- `vmix_unique`: once M is fixed, the V mix is unique if [X_n | X_0·M] has independent rows. `vmix_not_unique_example` shows that hypothesis is needed.
- `det_prefix_gauge`: det M_G = det G · det M_1.

**Localisation A = ℤ[1/m]** (any ring A with φ : A → F).
- `solve_inGL`: if A1 = [R_n0;U0] and B = [F_n0;G·V0] are A-matrices with unit determinants, the F-solution M lies in GL_n(A).
- `inGL_det_ratio`: if M ∈ GL_n(A), then only the RATIO det B / det A1 must be (the image of) a unit.

Why this rules out the round-1 "non-dyadic" artefact:
- r1 used RREF Q-bases. They are a Q-gauge: U0 and V0 change by Q-invertible H, H', so A1 and B are not A-matrices with unit dets.
- By `det_prefix_gauge` the determinant of M moves by det G (likewise for the U0 base change), and a non-unit det means M ∉ GL(A). That is what r1 saw ("smooth M, det not a unit, factor fails at pivot 1059").
- With A-unimodular bases (r2: det[R_n0;U0A] and det[F_n0;V0A] are smooth units) and G = I, `solve_inGL` puts M in GL(A). So the failure was a property of the gauge, not of the word, as ALT r2 concluded.

**Finding (prose false as written).** "M ∈ GL(A) iff the determinants are units of A": the "if" holds (`solve_inGL`), the "only if" is false.
- `iff_false_example`: over ℤ ⊂ ℚ, A1 = B = (2) gives M = 1 ∈ GL(ℤ) with det A1 = 2 a non-unit.
- Minimal fix: "if both determinants are A-units then M ∈ GL(A); conversely M ∈ GL(A) forces only det B / det A1 ∈ A^×".

**Scope.**
- The existence of one valid prefix (the native's) is an input. Without it the "psi" condition can fail (ALT r2 jsearch: 1,153 such deletions), and no gauge helps.
- "The V mix is unique" needs rank X[G1] = |G1|, checked [C] on #7623.
