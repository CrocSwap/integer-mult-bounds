# Rank-8 rigidity passes to supersets

Notation and the system (E) are those of PR1212 (`research/complex-rank8-decoder-rigidity/PROOF.md` at head
`57099cb5`, §0). For a set L of root lines, call L *rigid* if every L × L matrix K of rank at most 8 over a field
of characteristic 0 that satisfies (E) on L equals `D (2 G_L) D⁻¹` for an invertible diagonal D. Finite facts
marked **[X]** are recomputed by this package's `verify.py` (check id `X`).

## Lemma 10 (extension)

**Lemma 10.** Let L ⊂ L′ be sets of lines with L rigid and with the roots of L spanning R⁸. Suppose that for
every i ∈ L′ \ L, the lines j ∈ L with G_ij = 0 span `r_i^⊥`. Then L′ is rigid.

*Proof.* Let K′ have rank at most 8 and satisfy (E) on L′. Its principal submatrix K′[L,L] satisfies (E) on L
and has rank at most 8. So K′[L,L] = D (2 G_L) D⁻¹ = 2 D R Rᵀ D⁻¹, where R is the L × 8 matrix of the roots
r_j (Gram units). R has rank 8, so K′[L,L] has rank 8, and so does K′.

Because rank K′ = rank K′[L,L] = 8, every row of K′ is a combination of the rows indexed by L. Write
K′[i,:] = y_iᵀ K′[L,:]. On the columns L this reads K′[i,L] = y_iᵀ K′[L,L] = 2 u_iᵀ Rᵀ D⁻¹ with
u_i = Rᵀ D y_i ∈ R⁸. That is, K′_ij = 2 ⟨u_i, r_j⟩ / d_j for j ∈ L.

(E) gives K′_ij = 0 for every j ∈ L orthogonal to i. These r_j span `r_i^⊥`, so u_i = c_i r_i for some
scalar c_i. The same argument on columns gives K′_ji = 2 d_j ⟨r_j, w_i⟩ with w_i = c′_i r_i.

Next, compare entries between two new lines i, i′. Since K′[i,:] = y_iᵀ K′[L,:], we get
K′_ii′ = y_iᵀ K′[L,i′] = 2 c′_i′ y_iᵀ D R r_i′, and y_iᵀ D R = u_iᵀ = c_i r_iᵀ by definition. So
K′_ii′ = 2 c_i c′_i′ G_ii′ for all new i, i′. Taking i = i′, (E) gives
K′_ii = 4 c_i c′_i = 4, so c′_i = 1/c_i. Set d_i = c_i for the new lines. Then K′_ab = 2 G_ab d_a / d_b
for all a, b ∈ L′. ∎

The proof uses the constraints of (E) only on new-versus-old orthogonal pairs and on the new diagonal. The
constraints between two new lines hold automatically. It needs no zero exclusion, no pivot and no class
structure.

Both hypotheses matter:

- **Rank.** A rank-one term supported on the odd entries of a new row satisfies (E). It gives a rank-9
  solution that is not gauge **[control.rank9-escapes]**.
- **Span.** If the orthogonal old lines span only a hyperplane of `r_i^⊥`, there is a rank-8 extension of a
  gauge solution that satisfies (E) and is not gauge **[control.span-needed]**.

## Theorem (bi-frame supersets)

**Theorem.** Let F1, F2 be disjoint frames and S ⊆ F1 ∪ F2. Then the live set E8 \ S is rigid.

*Proof.* W(E8) is transitive on the 2025 frames **[model.frame-transitivity]**, and its elements preserve
(E) and the gauge form (PR1212 §0). So take F1 = FRAME0, which puts F2 inside P112.

The unit L = E8 \ (FRAME0 ∪ F2) is rigid in each of the three FRAME0-stabiliser orbits of F2
**[unit.frame-orbits]**:

- type (2,2,2,2): PR1212, Theorem 1′;
- type (4,4): PR1389;
- type (1,…,1): PR1399.

For every one of the 1260 units and every one of the 16 lines i ∈ FRAME0 ∪ F2, the live lines orthogonal to i
span `r_i^⊥`. There are at least 52 of them in each case **[lemma10.span-condition]**. The roots of L span R⁸,
because L also contains a line non-orthogonal to i: i has 56 such lines in E8, and at most 15 of them are
removed. Lemma 10 then applies to L ⊂ E8 \ S. ∎

**Corollary (floor).** On each of these live sets, every decoder with exactly eight costly terms in the E-graph
model has cst ≥ 72 − |S| when |S| ≤ 15, and cst ≥ 56 when |S| = 16. The proof is PR1212 §8 verbatim with
PR968's Theorem 4(b); see `research/complex-frame-pair-decoders/PROOF.md` §4. It inherits PR968's cited premise
(F6).

## Which intermediate punctures this reaches

Now take S = FRAME0 ∪ X with X ⊂ P112. The question is when FRAME0 ∪ X lies in the union of two disjoint
frames.

- **Exactly when X lies in a frame inside P112.** Running over all pairs of disjoint frames whose union
  contains FRAME0, the sets (F1 ∪ F2) \ FRAME0 are exactly the 1260 frames inside P112
  **[census.biframe-covers]**.
- **P111.** Every line of P112 lies in a type-(2,2,2,2) frame inside P112 **[census.p111-from-2222]**. So
  P111 rigidity follows from PR1212's Theorem 1′ alone. This is a second proof of PR1389's P111 result. It
  needs neither PR1389's three-row class argument nor P111's own zero-exclusion certificate.
- **P110.** Every orthogonal pair in P112 lies in a type-(2,2,2,2) frame inside P112. So all 3304
  orthogonal-pair P110 units are rigid, again from PR1212 alone **[census.table]**.
- **P105–P109.** The covered X are counted below **[census.table]**. The "cheapest" column gives the
  first rigid P104 type that contains X, in the order PR1212, then PR1399, then PR1389.

| \|X\| | unit | all X | orthogonal X | covered X | cheapest: PR1212 / PR1399 / PR1389 |
|---:|---|---:|---:|---:|---|
| 1 | P111 | 112 | 112 | 112 | 112 / 0 / 0 |
| 2 | P110 | 6216 | 3304 | 3304 | 3304 / 0 / 0 |
| 3 | P109 | 227920 | 31024 | 29232 | 14784 / 14336 / 112 |
| 4 | P108 | 6210820 | 94892 | 77868 | 22512 / 53760 / 1596 |
| 5 | P107 | 134153712 | 82656 | 70560 | 18816 / 50176 / 1568 |
| 6 | P106 | 2392407864 | 39088 | 35280 | 9408 / 25088 / 784 |
| 7 | P105 | 36227890512 | 10592 | 10080 | 2688 / 7168 / 224 |

**What is not reached.**

- Any X containing an odd pair. No frame contains an odd pair, so Lemma 10 from a P104 unit cannot apply.
  At P110 these are 2912 pairs in two stabiliser orbits, of sizes 224 and 2688. Write T_x for the four FRAME0
  lines not orthogonal to x. In the 224-orbit T_x = T_y; in the 2688-orbit T_x and T_y share two lines
  **[census.p110-odd-orbits]**.
- Orthogonal sets X that do not extend to a frame inside P112, for example 1792 of the 31024 orthogonal
  triples.

For |X| ≥ 4 the covered X are a small fraction of all X, so most of P105–P108 is still open.
