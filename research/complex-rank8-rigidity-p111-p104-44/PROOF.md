# Rank-8 rigidity on P111 and the type-(4,4) P104 units

Notation, equations (E), (1), (2), (E0), (E2), (E4) and Lemmas 2–8 are those of PR1212
(`research/complex-rank8-decoder-rigidity/PROOF.md` at head `57099cb5`). Finite facts marked
**[X]** are recomputed by this package's `verify.py` (check id `X`). Facts marked **[1212: X]** are
PR1212's checks, which `verify.py --pr1212-dir` replays from blob-pinned files.

**Theorem.** Let L be a P111 unit (P112 minus one line) or one of the 28 type-(4,4) P104 units, and let
K be an L × L matrix over a field of characteristic 0 with rank K ≤ 8 that satisfies (E). Then
K = D (2 G_L) D⁻¹ for an invertible diagonal D.

**Corollary.** In the E-graph model, every decoder with exactly eight costly terms has cst ≥ 63 on P111 and
cst ≥ 56 on the type-(4,4) units. This is PR968's floor at p = 9 and p = 16, reached through PR1212's §8
verbatim. PR717's P111 decoders attain 63. Sharpness at 56 on the (4,4) units is not checked; PR968's
frame-pair decoders do not exist on them.

By PR1212 §10 transport, the stabiliser of FRAME0 is transitive on the 112 lines and on the 28 type-(4,4)
frames **[1212: G.line-orbits, G.frame-orbits]**. It therefore suffices to treat one representative of each,
with PR1212's pivot F **[pr1212.*.pivot-vectors]**. Zero exclusion (Lemma 8) holds on both
representatives with these pivots **[1212: G.P111.zero-exclusion, G.P104-44.zero-exclusion]**.

Call a class *usable* if it has at least three live rows.

## Profiles

- **P111:** 25 complete classes, one class C* with three live rows, and two empty classes
  **[P111.class-profile]**. C*'s block contains no other usable class.
- **Type (4,4):** 24 complete classes and four empty ones, so two complementary blocks carry nothing
  **[P104-44.class-profile]**.

In both units every live non-pivot line lies in a usable class **[\*.lines-in-usable-classes]**.

## Lemma 5′ (three-row classes)

Let C be a class with live rows 1, 2, 3 (row 4 dead) and support T = {a, b, c, d}. Then, for nonzero
scalars δ_i and γ_f,

    a_if = δ_i ε_if γ_f,      b_if = 4 δ_i⁻¹ ε_if γ_f⁻¹.

*Proof.* By (E4) and (E0) the 3 × 4 class matrices satisfy A_C B_Cᵀ = 16 I₃, so both have rank 3.

Each of the three row matchings of Lemma 2(d) has exactly one pair inside {1, 2, 3}, and the three pairs are
distinct **[\*.three-row-lemma]**. So every column pair has one live group. Its Step-1 witness exists
**[\*.group-witnesses]**. Step 1 of PR1212's Lemma 5 then applies to that group, and by the same argument
with a and b exchanged, to b as well. This uses (E2) in the order a_j · b_i and zero exclusion of a_j.

With the rows of u_if = a_if ε_if written as (1, x_i, y_i, z_i) and the columns labelled as in PR1212
Step 3, the group relations are:

- from {1,2}: x₁ = x₂ and y₁/z₁ = y₂/z₂;
- from {1,3}: y₁ = y₃ and x₁/z₁ = x₃/z₃;
- from {2,3}: z₂ = z₃ and x₂/y₂ = x₃/y₃.

Put x = x₁ = x₂, y = y₁ = y₃, Z = z₂ = z₃, and let z = z₁, Y = y₂, X = x₃ be the remaining entries. Then
Y = yZ/z and X = xZ/z, and the third ratio gives xy = XY = xyZ²/z², so Z = ±z.

- Z = z gives equal rows: this is the stated form for a.
- Z = −z gives the rows (1, x, y, z), (1, x, −y, −z), (1, −x, y, −z). The class's own sign rows, normalised
  to a first row and column of +1, have the same group structure, so they equal this pattern. Then
  A_C = diag(δ) D_r J D_c diag(γ) has rank 1, which contradicts rank 3 **[\*.three-row-lemma]**.

The same holds for b, so b_if = δ′_i ε_if γ′_f.

Within-class equations then require Σ_f ε_if ε_jf w_f = 0 for i ≠ j, where w_f = γ_f γ′_f. The three
products ε_i ∘ ε_j of distinct live rows are independent and orthogonal to the all-ones vector
**[\*.three-row-lemma]**, so they span its orthogonal complement and w = μ·1. Finally (E0) gives
4 δ_i δ′_i μ = 16. ∎

With two live rows this step fails: one product leaves w three free directions
**[control.two-row-not-forced]**.

## Lemma 6′ (gluing)

Lemma 5 (complete classes) and Lemma 5′ give every usable class C a column scaling γ^C.

**Relation (5) between classes.** For usable classes C ≠ C′ in distinct blocks through {k, k′}, any live
orthogonal pair i ∈ C, j ∈ C′ whose supports meet in exactly {k, k′} yields relation (5), exactly as in
PR1212.

**Well-defined ratio.** For every pivot pair, the usable classes whose support contains it are nonempty and
connected by such witnessed relations **[\*.gluing-connected]**. So ρ_kk′ := γ^C_k / γ^C_k′ is well
defined.

**Cocycle.** Inside one usable class, ρ_kk′ ρ_k′k″ = ρ_kk″. Fix a base point k₀ and set g_k := ρ_{k k₀}.
For k, k′ ≠ k₀:

- If the block of {k, k′, k₀} is usable, then ρ_kk′ = g_k / g_k′ directly.
- Otherwise there is an m whose triples {k, k′, m}, {k, m, k₀} and {k′, m, k₀} all lie in usable blocks
  **[\*.gluing-cocycle]** (every base point works on both units). Then
  ρ_kk′ = ρ_km ρ_mk′ = (g_k / g_m)(g_m / g_k′).

This is a multiplicative identity, so it holds over any field. The additive rank 21 = 28 − 7
**[\*.cocycle-rank]** is a cross-check only.

Hence γ^C = c_C g|_T for every usable class C. ∎

The path condition is not vacuous. With four of the twelve usable (4,4) blocks removed, the relations drop
to rank 17 and no base point passes **[control.path-condition-bites]**.

## Assembly

PR1212 §7 applies verbatim to all live non-pivot lines, which lie in usable classes. It gives
K = D (2G) D⁻¹. An exact rational control checks the assembly on both units
**[\*.assembly-control, control.perturbed-fails]**. ∎
