# Select same-cell source pairs whose tensor and inverse retain a rank floor in every order

## Change and exact result

The exact fine-prime core theorem leaves physical phase/chirp transfer open because ordinary Stein rank is not invariant under diagonal similarity. This package works directly with selected adjacent same-cell pairs in the retained column-normalized, unrounded, alias-deleted narrow coefficient array. It keeps their actual phase/chirp coefficients and respects the original finite period.

For N=2^g, let R_N=2 ceil((N+3)/5). On each original source axis, let s be its odd prime, t its dyadic target, and delta=t-s. For even 2<=r<=R_N, there are at least

    s - 1 - delta - 2r^2 - r

good starting indices whenever that quantity is positive. Every combination of the selected pairs yields a tensor with ordinary nilpotent Stein rank at least r in every vertex order. Its exact inverse has the same floor. These counts concern starting indices / centered phase residues, not distinct phase cells.

With the retained fine gap delta/s<=1/p^2, p>=3 and s>=p^4, the theorem admits

    r = min(R_N, 2 floor(sqrt(s_min)/4)),

with at least s/3-1 good indices per axis. This turns the predecessor generic floor into a pointwise selected-source statement, up to an explicit square-root-prime cap. No new kappa is claimed.

## Why the claim is new relative to the pinned predecessors

[The generic all-order result](https://github.com/CubeJerry/integer-mult-bounds/commit/085b30f8e036f69421d5953d0993ac4974ec3f24) supplies nonzero matching minors. [The exact core specialization](https://github.com/CubeJerry/integer-mult-bounds/commit/da06a3d10e06870a0279e33dd5056ded8d7e7a38) trims those minors and specializes unshifted core parameters by CRT and Gelfond-Schneider. Neither transfers ordinary rank through the physical similarities.

Here the literal same-cell pair is [[1,U],[V,1]], with U=exp(-pi alpha^2 A/s), V=exp(-pi alpha^2 B/s), A+B=2t. A difference-root count excludes at most 2r^2+r residues that collide on the directed degree box. At most delta additional odd lifts leave the same-cell range, and the zero residue already excludes the terminal index. Symmetric restriction certifies a nonzero directed polynomial; CRT separates its monomials, and a common transcendental base gives pointwise nonvanishing. Each order is specialized separately. A general Schur-complement/reversal identity proves the inverse statement without assuming symmetry.

The bounded overlap and the single approved pivot from a restricted K-family to all residues are recorded in the package. Classical CRT, Gelfond-Schneider, path determinants and Schur complements are credited rather than claimed as new.

## Costs, limits and remaining obligations

A sequential selector scans difference pairs with no hashing or free matrix access. Its conservative bill is O(g s_max^2 poly(log s_max)) bit work, logarithmic local scratch and paid input/output indices. It produces indices only. Coefficients, generators, permutation transport, inverse data and precision remain separate obligations.

An ordinary lower/upper Toeplitz generator expression needs at least r terms in every order. Separately materializing the two full vectors for every term needs at least 2Nr scalar slots. This is a specified dense-format obstruction, not a general algorithm, circuit, memory or multiplication lower bound.

The matrix is already the source's column-normalized G. It is not the raw resampling Gaussian, full alias-summed periodic matrix, rounded stored matrix, arbitrary phase, scheduled capped interior or larger section. Its inverse is the selected tensor's inverse, not a section of a larger inverse. Exact transcendence gives no Cp-bit margin. All five framework assumptions and selected #7000 remain unchanged.

## Reproduction and evidence

Canonical base e54523517d0f03e58352e647c403a5af3e525a57; package-only addition, exact source/dependency pins retained.

```sh
python3 -I -W error -B research/selected-phase-binary-rank/verify.py
python3 -I -O -W error -B research/selected-phase-binary-rank/verify.py
python3 -B scripts/research_package.py --package research/selected-phase-binary-rank
```

The direct normal and optimized commands print PASS_SELECTED_PHASE_BINARY_RANK with identical JSON. The primary verifier authenticates five retained inputs, checks 93 bounded cases / 6,680 nonzero residues / 184,488 complete box values, verifies 2,402 admitted source pairs and seven actual fine-prime fixtures, and expands 11 directed minors with 570 terms. Fourteen negative controls cover phase cuts, finite endpoints, domain/degree/denominator failures, insufficient guards and inverse-section confusion. Independent proof/source and exact computation review is retained separately. Finite checks corroborate the proof; transcendence is a cited theorem, not a numerical oracle.

No predecessor supplier suite, native caller, selected cold replay, formal kernel or hosted CI is claimed. Open questions are quantitative rounding margins, arbitrary/scheduled phases, larger tiles and the actual alias/production interface.

## Credit and assistance

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The lead proposed the phase specialization and all-residue strengthening; the worker derived the source map, proof, selector costs and primary checks; separate AI review checked the mathematics and source. No independent human acceptance is claimed.

Credit Chafik Boukhalfa / #1786, Vlado Vojdanovski / #1673, IdeaOuter's fractional-shift work credited in #1758, Jeremy Kothe and the retained bilateral/source lineage, Douglas Colkitt/OpenAI's framework, and the two explicitly pinned predecessor packages. Gelfond and Schneider's classical theorem is an explicit input; the original Gelfond theorem on p. 628 was read. Original notices and Apache-2.0 terms are preserved.

## Executed independent review

`review/REVIEW.md` records a separate proof and exact checker, with 135 small cases, 8952 residues, 505752 exponent-box values, four fine-prime fixtures, 48 full directed determinants and six controls. Normal/optimized receipts agree. Run `python3 -I -W error -B research/selected-phase-binary-rank/review/independent_check.py --package research/selected-phase-binary-rank`, also with `-O`; both are registered in VERIFY.json. Finite evidence corroborates the written universal proof.
