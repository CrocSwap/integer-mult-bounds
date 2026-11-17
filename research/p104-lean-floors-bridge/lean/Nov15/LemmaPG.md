# LemmaPG.lean: SPECBREAK R25 Lemma PG, fully general. No sorry, ~7 s, 2.2 GB RSS
Lane LEAN-NEXT7, Nov 16. Source: cards/WILD/SPECBREAK/R25/THEORY.md §2, RESULT25.md item 3. Self-contained, namespace LemmaPG.
Axioms (3 printed): [propext, Classical.choice, Quot.sound].

**Statement (`lemmaPG`).** K is any field with 2 ≠ 0. V = E × F × W, with finrank E = finrank F = 2 (V_Q, V_−) and W (V_0, the ancillas) any finite-dimensional space.
- w ∈ End F with det w = 1. T w = (−I_E) ⊕ w ⊕ I_W, so T₊ = T w and T₋ = T (−w). These are block diagonal; that is the pin.
- If rank(X − I), rank(X − T₊) and rank(X − T₋) are all ≤ 2, then X * X = 1.
- Every w and every ancilla dimension. No dimension-4 reduction, no genericity, no Singular.

**Characteristic.** Characteristic 0 is NOT needed. 2 ≠ 0 is enough, and it is necessary.
- `char_two_counterexample`: if 2 = 0, take w = 1 and W = K. Then T₊ = T₋ = I.
- X = I − (projection onto W) has rank(X − I) ≤ 1, but X² = X ≠ I.
- So the lemma holds over every field of characteristic ≠ 2, ℚ and ℂ included. R25's "every hand step needs only char ≠ 2" is confirmed, and the Singular step can be dropped.

**Proof (new, uniform; differs from R25's generic/CH + Gröbner split).**
- (0) CH in dimension 2: w² = t·w − 1 (`ch2`). Only this identity is used, not det itself.
- (1) w cannot have both eigenvalues 1 and −1. So WLOG −1 is not an eigenvalue: otherwise swap w ↔ −w, which swaps T₊ and T₋.
- (2) K0 := ker(X − I) and K₋ := ker(X − T₋) have codim ≤ 2. K0 ∩ K₋ ⊆ ker(I − T₋) = V_0.
  - Since codim V_0 = 4, we get K0 + K₋ = V and K0 ∩ K₋ = V_0, so V_0 ⊆ K0 (`sup_inf_of_count`).
- (3) X = I on K0 and X = T₋ on K₋. So X² = I iff (I + T₋)k ∈ K0 for every k ∈ K₋.
  - Since V_0 ⊆ K0, this means (0, (1 − w)k_−, 0) ∈ K0.
- (4a) Case K0 ∩ K₊ ⊆ V_0. Then K0 + K₊ = V. Write k = a + b with a ∈ K0 and b ∈ K₊.
  - The T₊ equation gives a_Q = 0 and (w − 1)a_− = 2w·k_−.
  - Applying (w − 1) and using CH: 2(w − 1)k_− = (t − 2)a_−, since w is injective. So (1 − w)k_− = ((2 − t)/2)·a_− ∈ K0.
- (4b) Otherwise some u ∈ K0 ∩ K₊ has u_− ≠ 0 and w·u_− = u_−. Then t = 2 and (1 − w)² = 0.
  - ker(1 − w) is either all of F or the line K·u_−. Either way (1 − w)k_− ∈ K·u_− ⊆ K0.

**Hypotheses as used.**
- dim V_Q = dim V_− = 2 enters only through codim V_0 = 4 (step 2) and through CH plus the line argument in F (step 4b).
- The rank-2 bounds enter only as codim ker ≤ 2.
- Not formalized: the reductions §1 (R1–R3) and the kill §3 of THEORY.md. Those use R15 Lemma 3 and the word structure, and remain prose [T].
- Not touched: the "middle-word" MID lemma (SPEC-BREAK round 26).
