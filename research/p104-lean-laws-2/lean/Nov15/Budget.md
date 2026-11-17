# Budget.lean: BRIDGETREE budget closures (B1(a)-(d), H1s). Self-contained: SYL.lean is copied in, then namespace BUDGET. 0 sorry, ~5 s, 2.2 GB.
Setting: a field K with 2 ≠ 0; units are rank-one updates 1 − x yᵀ, and the product formula comes from SYL. Every hypothesis below is stated explicitly in Lean.
- `budget_identity` (B1(a), arithmetic): N = Σ N_i and n = Σ|P_i| + |S| ⇒ ρ = N − n = Σ β_i − |S| (in ℤ).
- `piece_neg_on_private` (B1(a), block step, column form): if the total Q·M_i·Q' = −I, the other pieces fix e_j (j ∈ P_i, where P_i means roles touched only by piece-i units, as an audit of the note corrects), and Q is invertible, then M_i e_j = −e_j. The row form is the same lemma applied to transposes.
- `single_mem_span`, `span_bound`, `beta_ge_d_ge_two` (B1(b)):
  - from M e_j = −e_j and the product formula, e_j ∈ V_i = span{x};
  - |P| + dim proj_S V ≤ dim V ≤ N_i;
  - a stage block x̂ with a left inverse (Lemma S) in proj_S V gives d ≥ 2.
  - So β_i ≥ d_i ≥ 2. The same lemmas apply to y via transposes.
- `b1c`, `b1c_budget` (B1(c), corrected): four groups on (h1, h2, A, B) with the support zeros and the cross relations ŷ_iᵀx̂_j = ±I. If both the x-span and the y-span of the split piece have dimension ≤ 2, there is a contradiction. Hence β ≥ 3, as a budget statement and not d ≥ 3. This replaces b1.sing run 2 by linear algebra: x̂3 = x̂2 and ŷ3 = ŷ2, then the 2×2 H-blocks give 1 = −1. It uses only the cross pairs 1-2, 1-3, 1-4, 2-4 in both directions.
- `b1d_c3` / `b1d_c4` (B1(d)): (2,3,2) with |S| = 4 gives 7 > 6; four pieces with β_i ≥ 2 give 8 > 6.
- `cayley_one_sub`: (I+R)ABᵀ = R − I ⇒ I − BᵀA is invertible. I+R does not need to be invertible here.
- `cayley_one_add`: with R invertible, I + BᵀA is invertible.
- `h1s` / `h1s_later` (H1s): from X_r[S_i] = A Z_rᵀ, Y_a[S_i] = B W_aᵀ and G[a,r] = ±W_a Z_rᵀ (W, Z invertible), Y_a[Ph]ᵀX_r[Ph] = W(I ∓ C)Zᵀ is invertible, so the number of piece hubs is ≥ 2. The Singular std = <1> step is now a linear-algebra proof, not a hypothesis.
Hypotheses taken from the notes, not derived: Lemma S (G − K = WZᵀ at ρ = 2, so the Gram blocks are ±W_a Z_bᵀ), the twisted Lemma S factorization and Cayley relation (CALLERTHEORY S'), the supports and confinement (which roles each group or unit touches), and that the S-span E_i contains the stage blocks.
Axioms: [propext, Classical.choice, Quot.sound] for all 13 (the b1d lemmas: propext, Quot.sound). Not done: C3 and S' themselves, Lemma Q, B2, NB, and the fam3e repricing.
