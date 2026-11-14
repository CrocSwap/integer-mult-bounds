# Exact all-order rank bounds at selected same-cell source pairs

**Scoped source theorem; no new kappa.** A10 removed genericity for an unshifted normalized binary Gaussian core, while warning that diagonal similarities do not preserve ordinary Stein rank. This package works directly with selected adjacent pairs in the retained column-normalized, unrounded, alias-deleted narrow source factor, retaining its phase and chirp.

Let `s_l` be distinct odd source primes, `t_l` their dyadic target sides with `s_l<t_l<2s_l`, `delta_l=t_l-s_l`, and `a=pi alpha^2` for common positive integer `alpha`. Put `N=2^g` and `R_N=2 ceil((N+3)/5)`. For any even `2<=r<=R_N`, the finite condition

    s_l - 1 - delta_l - 2r^2 - r > 0

ensures at least that many good starting indices on each axis. Each gives a nonwrapping same-cell adjacent pair. **Every combination of these selected pairs**, tensored together, has ordinary nilpotent Stein rank at least `r` in **every vertex order**, as does its exact inverse. The count is over starting indices / centered phase residues, not distinct phase cells.

For the retained fine gap `delta_l/s_l<=1/p^2`, with `p>=3` and `s_l>=p^4`, one may take

    r = min(R_N, 2 floor(sqrt(s_min)/4)).

There are then at least `s_l/3-1` good starting indices per axis. The source prime scale makes this cap `exp(Theta(p^(1-epsilon)))`; groups below the cap receive the full predecessor generic rank floor pointwise. Larger groups receive the square-root-prime floor, not a linear-in-`N` claim.

## Why the actual coefficients work

The source uses `q_j=floor((t/s)j+1/2)` and `beta_j=(t/s)j-q_j`. Its same-cell pair is exactly `[[1,U],[V,1]]`, where

    U=exp(-a A/s), V=exp(-a B/s),
    A=2t-s+2s beta_i, B=s-2s beta_i, A+B=2t.

At most `2r^2+r` nonzero residues of `A` allow a collision among `uA+vB mod s` for `0<=u,v<=r`. At most `delta` odd lifts leave the same-cell range. Nonzero `A` also excludes the terminal index, so the pair remains inside the original physical period.

A predecessor symmetric matching minor remains a nonzero polynomial in the directed variables `U,V`, because its symmetric restriction is nonzero. Every individual degree is at most `r`. Local box injection and CRT keep its monomials separate after substituting a common transcendental base. Gelfond-Schneider therefore makes each selected minor nonzero. Each order is handled separately, preserving the degree bound. A general Schur-complement/reversal identity gives the inverse result; the pair is invertible because `UV<1`. [PROOF.md](PROOF.md) gives all details.

## Source and cost limits

The matrix is the selected tensor of the displayed, already column-normalized source `G`. It is not the raw resampling Gaussian, full periodized matrix, rounded stored matrix, arbitrary phase or scheduled capped interior. Its inverse is not a principal section of a larger source inverse. No diagonal-similarity invariance, larger-section transfer, Cp-bit margin or coefficient-production theorem is asserted.

A sequential exact selector costs at most `O(g s_max^2 poly(log s_max))` bit work and logarithmic local scratch, plus input/output indices. It scans difference pairs without hashing or random-access tables. At the retained scale this is a standalone `exp(o(p))` setup bill. It produces indices, not Gaussian coefficients, generators or a full caller.

Any expression using ordinary lower/upper triangular Toeplitz generator products requires at least `r` terms. A format storing both full length-`N` vectors per term needs at least `2Nr` scalar slots. This specifies a dense-format obstruction; it is not a general circuit, runtime, memory or multiplication lower bound. All five framework assumptions, selected #7000 and its accepted conditional bound remain unchanged.

## Reproduction and evidence

Python 3.12 and standard library, from the repository root:

```sh
python3 -I -W error -B research/selected-phase-binary-rank/verify.py
python3 -I -O -W error -B research/selected-phase-binary-rank/verify.py
python3 -B scripts/research_package.py --package research/selected-phase-binary-rank
```

The first two commands are read-only and print JSON status `PASS_SELECTED_PHASE_BINARY_RANK`. [RESULT.json](RESULT.json) records the identical normal/optimized primary output. The verifier authenticates five retained inputs; checks 93 bounded prime/size cases, 6,680 nonzero residues and 184,488 complete box values; verifies 2,402 admitted source pairs; checks seven exact fine-prime fixtures; and expands 11 directed minors with 570 nonzero terms, comparing entry-first and polynomial-first specialization. Fourteen controls cover phase cuts, the finite endpoint, degree and denominator failures, malformed source domains, insufficient guards and inverse/section confusion.

The primary matching-path/poly helpers are adapted with credit from A10. Independent mathematical and computational review is recorded separately. Finite checks corroborate the written proof; they do not test transcendence or prove the all-size theorem by enumeration. No full predecessor supplier suite, native replay, selected cold replay, Lean, Docker or hosted CI is claimed.

## Pins and credit

Canonical base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. [SOURCES.json](SOURCES.json) pins canonical provenance and [DEPENDENCIES.json](DEPENDENCIES.json) pins retained inputs. Immediate predecessors: [A9 generic all-order theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/085b30f8e036f69421d5953d0993ac4974ec3f24) and [A10 exact fine-prime core theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/da06a3d10e06870a0279e33dd5056ded8d7e7a38). [SOURCES.md](SOURCES.md) records source locations and Gelfond's original theorem, p. 628. [OVERLAP.md](OVERLAP.md) records bounded overlap and the approved strengthening.

Credit Chafik Boukhalfa's [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786), Vlado Vojdanovski's [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673), IdeaOuter's shift work credited in [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758), Jeremy Kothe and the preserved bilateral/source lineage, and Douglas Colkitt/OpenAI's framework. Gelfond, Schneider, CRT, path determinants and Schur complements are classical predecessors.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance. The lead proposed the phase specialization and all-residue count; the worker derived the source proof, selector costs and primary checks; a separate AI worker reviewed the critical mathematics and source. No human or formal-kernel acceptance is claimed. Apache-2.0; original source notices remain unchanged.

## Open next questions

1. Can an explicit minor or singular-value margin justify a Cp-bit rounded version? Qualitative transcendence gives no such margin.
2. Can the direct phase argument cover arbitrary phases or a pinned larger scheduled tile? Selection and compression change the interface.
3. Can aliases and actual stored coefficients be incorporated with a complete production and error bill? They are separate matrices from the present exact source pair.

## Executed independent review

`review/REVIEW.md` records a separate proof and exact checker, with 135 small cases, 8952 residues, 505752 exponent-box values, four fine-prime fixtures, 48 full directed determinants and six controls. Normal/optimized receipts agree. Run `python3 -I -W error -B research/selected-phase-binary-rank/review/independent_check.py --package research/selected-phase-binary-rank`, also with `-O`; both are registered in VERIFY.json. Finite evidence corroborates the written universal proof.
