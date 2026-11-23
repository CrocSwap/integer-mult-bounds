# Exact stored compiler fragments at partial matching cuts

This is a follow-up to the direct-circulant numerical interface in #8093,
prepared from the interrupted local compiler-cut audit. It proves that the
actual canonical rational compiler keeps its existing four fragment bounds
at a cut after any subset of complete one/two-wire gates in one matching.
The generic extra `sqrt(2)` factor is unnecessary for these source envelopes.
It does not change the precision selector or the selected multiplication bound.

## Precise result

The primitive FFT/shear word has only bank-local unitary gates and two
same-direction cross-bank spectral matchings. Its matrices have unitary
diagonal bank blocks and an off-diagonal block with additive norm budget.
Consequently prefixes, suffixes and both inverses have the existing bound
`1+M_g+M_h+2v`, including arbitrary complete-gate subsets.

The argument propagates through actual aligned parity macros, paired
generator compensation, and Full's source-timed active antichain. The
literal `Full.allocation` bound `K=2 L0 B H` remains valid, and arbitrary
segments retain the conservative `K^2` bound. Complete leading-section
conditioning, source component envelopes, rank, phase and per-atom defect
contracts remain explicit premises. `PROOF.md` gives the universal argument.

Brian/JoyboyBrian's #4755 already establishes the exact physical trace
identity. His #4976 establishes the sharp generic interpolation loss and
asks the source-alphabet question resolved here. Jose Manuel/jmbarrancoml
supplied the compiler and its original polynomial estimates. The new
contribution is their source-bound no-extra-loss composition, with explicit
control of the stored inverse and normalized suffix product.

## Exact boundary

A complete two-wire gate is the smallest unit covered. A swap performed by
overwriting one coordinate first has the singular intermediate map
`[[0,1],[0,1]]`; the inverse-cut theorem cannot cover that state. Replacing
gates with recursive services, changing the local alphabet, adding rounding
events or claiming a physical tape tariff requires new contracts. The
alternative field/native construction of #8092 is a different compiler.
No canonical assumption is removed, no new kappa is claimed, and no full
multiplier or production-sized transform is executed.

## Executed checks

The standard-library audit executes the pinned original factories and uses
its own exact Gaussian-rational matrix arithmetic, elimination, PSD
certificates and source-timestamp reconstruction. Normal and optimized
CPython 3.12.14 runs passed:

```sh
python3 -I -B audit.py
python3 -I -O -B audit.py
```

Expected marker: `PASS_SOURCE_ORDERED_FOUR_WAY_CUT_AUDIT`.

The checks cover 135 primitive cuts, 540 four-way PSD bounds, 540 additional
bank-invariant certificates, 885 Full cuts and 3,540 source-trace identities.
The Full cases include a nonzero approximate root, asymmetric zero-duration
atoms with simultaneous active fragments and reversed physical labels, and
the N=1 complex-scalar boundary. There are 492 proper partial Full cuts.
Controls reject missing inverse scope, nonunitary bank operations, wrong
scalar adjoints, generic zero-loss interpolation, opposite-direction
spectral shears, delayed zero-duration atoms and noncommuting factor order.

All 18 retained files are checked by SHA256, Git blob hash and byte length.
`EVIDENCE.json` binds the exact proof and checker hashes. This is finite
discrimination evidence accompanying the written quantified proof, not a
kernel proof or external human review. Separate review is pending.

## Source pins and integration

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
`ORIGINS.json` records all canonical and prior-PR sources. This directory
is self-contained and needs no network, NumPy or Mathlib.

Suggested integration: add this directory as `compiler-cuts/` in
`research/direct-circulant-production-precision`, retain its proof/review
boundary, and register the two exact commands in that package's existing
replay hook. Keep the original #8093 proof and selector unchanged. Do not
publish this draft before separate review and root verification.

## Open next questions

1. Can a reversible enlarged-state description control intermediate
   coordinate arithmetic with explicit scratch and rounding costs? Start
   from the swap splice counterexample; complete-gate invertibility is
   insufficient.
2. Can the retained all-size phase and rank contracts be independently
   certified? They remain separate from the fragment lemma and finite
   generator checks do not prove them universally.
3. For a changed recursive gate service, what local invariant bounds its
   internal fragments? Check same-direction bank geometry before importing
   this result.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Source notices and exact predecessor credits are retained in `NOTICE.md`.
Apache-2.0; no external human or proof-kernel acceptance is implied.
