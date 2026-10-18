# Concept transfers, implementation and measured scope

Two distinct concepts are being used in this lane. Only the first currently has a positive literal allocation; its κ effect is small. The second has exact constructive algebra and bounded source-specific searches, but no positive native word yet. These are not two significant realized κ mechanisms.

## 1. Primitive conformal pattern augmentation, with a literal chronology lift

**External concept.** Integer-kernel circuit augmentation distinguishes a feasible multi-column change from single-item local moves. See De Loera, Hemmecke and Lee, *On Augmentation Algorithms for Linear and Integer-Linear Programming* ([author preprint](https://arxiv.org/abs/1408.3518), [full proof](https://arxiv.org/pdf/1408.3518)), especially the definitions of circuits and conformal-minimal integer kernel vectors on pages 3–4. We use one explicitly checked direction, not a Graver-basis oracle, a complete augmentation algorithm or a new complexity guarantee.

**Actual pattern relation.** Order four patterns as cap-32 triple-9, cap-32 double-9, empty cap-48, and cap-48 five-9. Their columns in the two capacity-count rows and the width-9 demand row are

```
A = [[1, 1, 0, 0],
     [0, 0, 1, 1],
     [3, 2, 0, 5]].
z = (5, -5, 1, -1).
```

Then `Az = 0`. The first three columns have determinant 1, so the kernel is one-dimensional; all four coefficients of z are nonzero and their gcd is 1. Consequently z is a primitive support-minimal integer circuit. It is also conformal-minimal in the full pattern matrix: a conformal subvector has zero outside this support, is a scalar multiple of z, and its final coordinate lies in `{0,-1}`. The scalar is therefore 0 or 1. No intermediate nonzero conformal integer kernel vector exists.

**Constructive effect.** Five copies of PR #2942's actual T74 pattern mix contain the required five double-9 cap-32 bins and one five-9 cap-48 bin. Adding z preserves every capacity total and helper-width demand. The complete paid change is `5 H5 − 5 H14 + H48 − H3`. This is a finite pattern-semigroup saturation step, with denominator 5 coming from the actual optimal basis. It supplies no theorem that every fractional packing can be saturated chronologically.

The literal source lift was separately constructed: a width-9 residual relay in each copy moves the early rank-14 vacancy to a later admissible window, then five actual donor roles fill the five vacancies. All 1,358,640 roles, source windows, family labels, masks, compact prefixes and the complete rank mass pass in `t370-cap-02/OWNERS.json`. The exact root bracket reaches the source's fractional cap. The neutral relay ablation has zero paid gain; the complete circuit gains only about 9.51 × 10⁻¹⁰ over PR #2942. This is not a significant second mechanism for the campaign target.

**Shared-library precedent.** Actual canonical Mathlib `LinearAlgebra/Matrix/Rank.lean` was inspected at `rank_submatrix_le`, `rank_reindex` and `rank_eq_finrank_span_cols`; SHA-256 `cb30d58a4ca42e71a175ec32c46f4490e832e7e4c90ce00f855d0b9d207360f5`. These supply rank/minor background, not a formal Graver theorem or a fresh kernel check. The displayed integer circuit and its primitive proof are checked directly here.

**Prior-use matches.** PR #2843/#2857/#2930 already use chronological flow, integer pattern mixes and edge coloring. Our earlier PR #2863 already uses multi-copy residue concentration and exact LP attainment. Neither edge coloring nor concentration is advertised as new. The new checked instance is the rank-14 circuit and its strict-window relay on the actual PR #2942 inventory. The external augmentation viewpoint makes the indivisible multi-pattern step explicit, but does not establish priority.

## 2. Coupled primal/dual basis construction for cold helper directions

**External concept.** A low-rank change must carry its dual/inverse data, rather than choose a sparse primal column alone. Classical inverse-update and partitioned-matrix methods are described and derived in Hager, *Updating the Inverse of a Matrix* ([author-hosted paper](https://people.clas.ufl.edu/hager/files/update-1.pdf), Sections 1–2). This is mathematical background; no claimed native cost bound is borrowed from that paper. The specific shear chart below is proved directly.

**Constructive chart.** Work over the dyadic rationals. Suppose c is a column, a a row, `c_p = 1` and `a c = 1`. Set `u = c − e_p`, and let β have entries `β_p = 0`, `β_j = −a_j` for `j ≠ p`. Define `L = I + u e_pᵀ`, `U = I + e_p β`, and `S = LU`. Both rank-one added matrices square to zero. Hence their inverses are obtained by changing the signs, and each is a product of explicit commuting transvections with determinant 1. Direct multiplication gives `S e_p = c` and

```
e_pᵀ S⁻¹ = (e_pᵀ − β)(I − u e_pᵀ)
            = (1 + βu)e_pᵀ − β = a,
```

because `a c = 1` implies `a_p = 1 − Σ_{j≠p} a_j c_j`. The input and inverse-output charts use at most `4(s−1)` scalar transvections in total when the union of their supports has s coordinates. Dyadic coefficients remain exact; their precision, scalar execution and any promoted native frames must still be paid.

For the actual invertible zero-frame helper word H, the corresponding internal direction and readout are `v = Hc`, `α = aH⁻¹`; exactly `αv = 1`. If several columns and rows are supplied, the analogous identity is `ΑV = I`. The catalogue verified all 3,136 cross-pairings of the 56 original directions. This constructs actual coordinate data; it is not efficient recovery from bare orbit existence.

When the involved cold helpers have an identical final frame, the inverse chart may be emitted only after they have all reached that frame, avoiding an extra positive terminal climb. The input chart and every changed prefix must still be independently realized and priced. A valid scalar S does not by itself license a native frame change, a fixed cut/centre change or a free common-label conversion.

**Actual bounded tests.** `SPARSE-COLD-PAIR-SCREEN.json` records 1,430 exact dyadic two-column combinations. `SPARSE-COLD-GROUP-SCREEN.json` expands to the actual same-final-frame groups of size 3–4, with normalized coefficients from `{0,±1,±2,±1/2}`. Neither produced a direction whose complete primal/dual support fits the current covariant cut/endpoint ceilings. Some dual directions fit, but the corresponding primal footprint does not. These are scoped trial outcomes, not general impossibility results, and not the requested positive research deliverable. The compiler lane is changing the basis and interface representation before another exact attempt.

**Shared-library precedent.** Actual canonical Mathlib `LinearAlgebra/Matrix/Transvection.lean` was read at `transvection_mul_transvection_same`, `det_transvection_of_ne`, `TransvectionStruct.inv_mul`, `mul_inv`, and both reverse-inverse product identities; SHA-256 `c8c60dfbda7a09877a884aa2c7ce385f24f5370bb2a456cc20aae872c7dd41ef`. Project `CodeMatrixRecovery20260913.lean` was read at `rowMap`, `reconstruct` and `reconstruct_from_ratios`; SHA-256 `ddbf5968a7ef5667139dec9f6075e6ac5a9badae8ea55c998583261a70342231`. These preserve actual inverses and supplied scalar conditions; they give no native source or runtime oracle. No Lean process was run.

**Prior-use matches and limits.** Elementary matrix charts, exact primal/dual reconstruction and transvections are classical. The previous TENSOR volume and earlier TI/code-equivalence project notes already use them as abstract recovery tools. The attempted application here is to actual cold-helper columns, dual rows, native warp covariance, fixed source cuts and a complete paid supplier. It has not yet yielded a successful changed supplier and is not claimed as a first global use.

## Evidence and sufficient-claim discipline

The initial full-library-eligible retrieval returned lexical/source-only and unreviewed notes, including records with `sorry`. Those entries were not promoted to established results; actual canonical source bodies above were read. This is targeted retrieval, not a semantic audit of the entire library. The current positive physical retiming pair is credited to the physical lane and is separately bound in `retime-pair-cap-01/`; its two moves use one mechanism. Complete native/source/global/outer admission and a second significant independent mechanism remain root-owned requirements.

## Realized inherited-mechanism composition

The subsequently frozen `combined-cap-01` composes actual PR #2942 normal45 words with actual PR #2948 declared rewrites. It is not a success of the failed cold-basis search above. Marius-Paul Dumitrean receives credit for the four paired normal45 extractions; Jeremy Kothe receives credit for the nine rewrites and their published profile. The physical lane independently found a retiming pair already present in PR #2948, so no priority claim is made. Our new contribution is an explicitly audited joint supplier, its literal cap-attaining T370 allocation, and actual four-way complete-cost comparisons.

The two inherited structural changes exceed the significant-gain threshold separately: the normal45 leave-one-out loss exceeds 27.05% of total gain, while removing all nine rewrites loses over 72.97%. These comparisons come from four actual word pairs and four separately checked complete allocations. Local free-operator audit receipts are not full phase/native or recursive release receipts. The root campaign owns complete admission; see `COMBINED-CONSTRUCTION.md` for precise scope, source pins, profiles and proof.
