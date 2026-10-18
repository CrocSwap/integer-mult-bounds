# Rank-8 rigidity on P112 minus an odd pair

Notation, (E), equations (2), (E0), (E2), and Lemmas 2–8 are those of PR1212
(`research/complex-rank8-decoder-rigidity/PROOF.md` at head `57099cb5`). Lemma 9 and the "Step 1" argument are
those of PR1399 (`research/complex-rank8-rigidity-p104-admissible/PROOF.md` at head `4e1ba3a1`). Finite facts
marked **[X]** are recomputed by this package's `verify.py` (check id `X`, with `u` one of `meet4` and `meet2`).

**Theorem.** Let x, y ∈ P112 with G_xy = ±1, and let L = P112 \ {x, y}. Let K be an L × L matrix over a field of
characteristic 0 with rank K ≤ 8 that satisfies (E). Then K = D (2 G_L) D⁻¹ for an invertible diagonal D.

**Corollary.** In the E-graph model, every decoder with exactly eight costly terms on such a unit has
cst ≥ 62 = 72 − 10. This is PR968's Theorem 4(b) with p = 10, reached through PR1212 §8 verbatim. With
PR1419, which covers the orthogonal pairs, this holds on every P110 unit, i.e. P112 minus any two lines.

## Reduction to two units

The FRAME0 stabiliser permutes the 2912 odd pairs of P112 in two orbits, of sizes 224 and 2688. They are
distinguished by how many FRAME0 lines are odd to both x and y: 4 or 2 **[orbits.odd-pairs]**. By PR1212 §10
transport, it suffices to treat one representative per orbit. Each has a pinned pivot frame F inside L, listed
as root vectors in `verify.py` **[u.unit]**. Relative to F the D4 facts of PR1212 Lemma 2 hold
**[u.d4-structure]**.

The class profiles (live rows per class) are **[u.class-profile]**:

- `meet4`: 24 complete classes, 2 with three live rows, and 2 empty (FRAME0 itself);
- `meet2`: 22 complete classes, 2 with three live rows, and 4 with two.

## Inputs

Write I for the lines of complete classes and J for the other non-pivot live lines (6 for `meet4`, 14 for
`meet2`).

- **(I2) Zero exclusion.** No entry of a_i = K[i,F] or b_i = K[F,i] vanishes on T_i, for any rank-8
  solution and any non-pivot live line i **[u.zero-exclusion]**. Rank K = 8 because K[F,F] = 4I, so
  K = K[:,F] K[F,:] / 4, and a_i, b_i are supported on T_i by (E). Each clause family of the CNF is then a
  necessary condition on the zero pattern:
  - *two*: for orthogonal i, j with T_i ∩ T_j = {k, k′}, the sum a_ik b_jk + a_ik′ b_jk′ = 0, so one
    product vanishes exactly when the other does;
  - *four*: for orthogonal i, j with T_i = T_j, a sum of four products is 0, so exactly one of them cannot
    be nonzero;
  - *diag*: a_i · b_i = 16;
  - *trans*: for a complete class C, A_C B_Cᵀ = 16 I because the class's rows are pairwise orthogonal
    **[u.d4-structure]**, so A_C and B_C are nonsingular and have a nonzero transversal (PR1212 Lemma 3).

  With the clause "some pattern variable is true" added, the CNF is refuted by a shipped DRUP proof. It is
  replayed by `verify.py`'s own two-watched-literal RUP checker, and the proof's SHA256 and the CNF's digest
  are pinned. Three controls back this up:
  - the gauge pattern satisfies the CNF without that clause **[u.cnf-consistent]**;
  - the same proof fails without that clause **[u.control-needs-zero-clause]**;
  - unit propagation alone does not refute the formula **[u.control-bogus-proof]**.

  PR1212's independent `rup_check` also accepts both proofs, with the same lemma counts. That was run once and
  is recorded in the README; `verify.py` does not depend on it.
- **(I3)** Every live group of every complete class has a live witness **[u.lemma5-witnesses]**.
- **(I4)** All 14 blocks carry a complete class, and complete classes in distinct blocks glue through every
  shared pivot pair **[u.lemma6-blocks-gluing]**.
- **Lemma 9 input.** For each line of J, the column pairs of T_i witnessed by lines of I connect T_i. In
  fact all six pairs are witnessed for every line, and the sign identity holds for every witness
  **[u.lemma9-propagation]**.

## Proof

**Step 1** is PR1399's Step 1 verbatim. PR1212's Lemma 5 applies to each complete class, using (I2), (I3) and
the class's own equations. Lemma 6 applies to the set of complete classes, using (I4). Together they give
nonzero g_f and d′_j with a_jf = d′_j ε_jf g_f and b_jf = 4 (d′_j g_f)⁻¹ ε_jf for j ∈ I.

**Step 2.** PR1399's Lemma 9 applies to each line of J, three-row and two-row alike. It needs only Step 1's
form on I and the witness connectivity, so a_i = λ_i ε_i ∘ g and b_i = 4/λ_i · ε_i / g. The witnessed (E2)
equations have rank 3 on a_i|T and on b_i|T, with these kernels **[u.lemma9-solution-line]**.

**Assembly.** Every non-pivot live line is now in PR1212 §7's form, and §7 gives K = D (2G) D⁻¹. An exact
rational control checks the assembly on all 110 live lines **[u.assembly-control]**. ∎
