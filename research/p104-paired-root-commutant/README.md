# Paired roots: exact decomposition criterion and the four-thin boundary

**No new κ.** This package proves an algebraic reduction for corank-two roots built from two orthogonal shear planes per full stage. It isolates the first possible genuinely coupled root and explains why a smaller thin-query count alone does not improve the complete signed invoice.

## Result

For at least two full stages, each consisting of two consecutive mutually orthogonal rank-one transvections, the grouped primal commutant is exactly isomorphic to the commutant of the two-dimensional dual thin reflections. The explicit map is proved in [THEOREM.md](THEOREM.md). All full-pair orientation parameters can first be removed without changing a grouped stage operator.

Every such corank-two root with zero or two thin queries consequently decomposes over the coefficient field into two corank-one roots. The statement covers every stage count, thin placement and full-pair gauge in that model. Four thin queries are sufficient for an indecomposable example: explicit six-field and 38-field dyadic witnesses have scalar grouped commutant. A separate six-vertex example has a strongly connected rank-one Gram graph but decomposable grouped stages, so graph connectivity alone is not a test for this native interface.

The 38-field witness preserves the 18 full stage operators and masks of the two `chain(9|9)` copies in CrocSwap/integer-mult-bounds#6902 after removing their two unused fields. Its four thin queries replace six. The target and paid histograms each lose exactly 208 rank-one entries, so every signed moment is unchanged. This is a structural result, not a better multiplication exponent.

## Provenance and novelty

Base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

- CrocSwap/integer-mult-bounds#6888, head `936a8a19896a56afbf428da6f7c29c175f348935`, supplies the transvection/reflection duality. The part needed here is rederived in the proof.
- CrocSwap/integer-mult-bounds#6902, head `e4d42607f24d7a049b0fca329dc4c34882405c25`, supplies the fixed two-plane native interface and the retained root used for exact mask and invoice comparison.
- The chain geometry originates in CrocSwap/integer-mult-bounds#6833. The scoped old-native optimality work in CrocSwap/integer-mult-bounds#6839 and CrocSwap/integer-mult-bounds#6877 does not prove the present grouped-operator commutant theorem.

The new contribution is a full commutant correspondence, its uniform zero/two-thin classification, the sharp four-thin witness, and the graph-test counterexample. No predecessor native, supplier admission, or compiler claim is reverified here. The frozen predecessor root is retained byte for byte with SHA256 in `SOURCES.json`; no unmerged Git objects or network access are needed to run this package.

## Reproduction and checks executed

From the repository root, using Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-paired-root-commutant
```

Expected: `PASS_PAIRED_ROOT_COMMUTANT`, `PASS_FINITE_FIELD_COMMUTANT_STRESS`
and `PASS_REGISTERED_RESEARCH_PACKAGE`.

The check regenerates both witnesses and proves their finite matrix identities over exact rational numbers. It checks all isotropy, root products, orthogonal pairs, full-block normalization, coordinate-mask support and prefix commutation. A direct primal linear-equation solver, which does not read dual data, checks the small commutants. The 38-field witness is checked by direct primal thin-commutator equations inside its independently constructed eight-dimensional full-stage commutant. Six two-thin cases cover both parities, separated and coincident gaps, nontrivial full-pair bases, and scaled thin vectors; a six-thin example checks the general correspondence beyond the sharp boundary.

Negative controls reject a wrong primal entry, reclassifying a nonorthogonal pair to manufacture a two-thin example, nonconsecutive full pairs, a missing mask coordinate, and an attempted lift of a noncommuting dual matrix. The zero-thin example independently distinguishes the individual-summand commutant from the grouped-stage commutant. Both ordinary and optimized Python executions are recorded in `CHECKS.json`; checks use explicit exceptions rather than assertions.

These exact computations are certificate checks and alternate finite implementations of the algebra. The uniform assertions are proved in `THEOREM.md`; a finite test domain is not presented as their proof. `generate.py --output DIR` reproduces the two generated fixture objects in an explicitly supplied directory.

[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) records the lead's mathematical
review and separately implemented 45-case finite-field check over F3, F5 and
F7, with fixed-seed gauges, scaled thin vectors and direct primal commutant
equations. It imports no author or predecessor scientific code. Its controls
reject an incorrect closure product and characteristic two; its finite
coverage is explicitly bounded.

## Scope and limitations

The theorem works over a field of characteristic different from two. Its direct-sum basis may use non-dyadic coefficients. A mask can couple algebraically decomposable components, so neither mask compatibility nor the paid bill automatically splits. Scalar commutant proves absence of a nontrivial invariant direct sum; it does not assert absence of every proper invariant subspace.

The four-thin root is not submitted as a physical caller. A preliminary generic emission increased ordinary work and did not establish the predecessor's raw-work envelope. The formal invoice cancellation is exact, but it does not discharge A6 owned ascent, LAMBDA pricing, BIT admission, compiler compatibility, or the five inherited framework assumptions. There is no selected-frontier edit and no claim that the shared native's current bound is optimal in a broader model.

## Open next questions

- Determine when the lifted idempotent commutes with all data masks and admits a dyadic basis. Start with the exact thin-two projections and solve their mask-commutation equations; the current theorem deliberately leaves this obligation open.
- Find a four-thin coordinate representation or placement with a strictly improved complete profile and an actual merged-idle proof. The retained witness shows that indecomposability alone is insufficient.
- Investigate larger corank or a native capable of nonorthogonal pairs only with a new complete bill. Those changes leave the normal-form hypotheses and are not excluded here.

Structured follow-ups are in `TASK.json`.

## Credit and license

Contributed by @CubeJerry with substantial OpenAI GPT-6 Astra assistance for research, proof, implementation and prose. Credit to DreamingOfClouds and the predecessor contributors named in `NOTICE` for the duality, chain root and shared-native construction. Apache-2.0; inherited source credit is preserved. Independent lead review is separate from the author's executed checks.
