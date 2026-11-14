# Prove Gaussian symmetry limits through diagonal gauges and physical rounding

This package closes a specific gap left by
[the heterogeneous-width theorem](https://github.com/CubeJerry/integer-mult-bounds/tree/be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7/research/heterogeneous-gaussian-symmetries):
its normalized ideal kernels did not cover arbitrary diagonal gauges, the
actual anchored physical broad/narrow square blocks, or approximate inverse
tables. The normalized entry-pair ratio recovers the Gaussian metric through
both independent diagonal gauges. The resulting exact and quantitative
theorems keep the source phases, grid correspondence and all precision factors
explicit.

**No new kappa.** The selected complete bound remains conditional with
kappa `0.00363005817`, and all five foundational assumptions remain. This
is a source-bound analytic-recovery obstruction and a reusable precision
interface, not a general displacement-rank or multiplication runtime bound.

## Exact result

For a heterogeneous shifted Gaussian tensor H on the same square Cartesian
row/column grid and any invertible complex diagonal L,R, let G=LHR. Then

`Gxy Gyx/(Gxx Gyy) = exp(-2 sum_i gamma_i (xi-yi)^2)`.

All exact commuting vertex permutations are therefore signed-coordinate
isometries. With distinct widths, every such permutation is an involution.
The exact monomial centralizer is also determined: writing
`G=A K B`, where K is unshifted and `Q=AB`, it consists precisely of
`c A P A^-1`, where P preserves K and Q and c is any nonzero scalar.
Weighted matrix order may be infinite; only P's vertex cycles are bounded.

Over all gauges, the least possible cycle count is exactly `ceil(T/2)`.
The predecessor's specified dense cycle-boundary format stores two families
of c full T-vectors, so its minimum is `2T ceil(T/2)` scalar slots. This
counts that format, including its prescribed zero slots. It does not rule
out implicit, compressed, separable or unrelated representations.

## Physical source and error boundary

For the retained actual narrow square block inside one phase cell, the
diagonal is exactly one and all entries are at most one, even before its
chirp is removed. For the matching centered broad block, the complete
normalizer is retained: entries are at most `alpha^-g` and the diagonal
floor is at least

`alpha^-g exp[-(b/4) sum_i(1+theta_i B_i)^2]`.

These direct physical bounds avoid a needless chirp-condition loss for the
normalized ratio. The distinct fine-prime widths and their separation are
inherited from the exact predecessor and pinned source notes.

For entrywise error epsilon, entry bound M and diagonal floor delta,
the normalized ratio error is at most `24M epsilon/delta^2`. Twice this
quantity must be below the unit-edge/nonedge and axis-color separation.
For an approximate inverse, the transfer first pays
`||E||_2<=T epsilon` and then the forward error bound
`2T^3 M^2 epsilon`, with explicit invertibility and margin conditions.

In the retained fine-prime regime, the physical floors, color gap and
local tile dimension have logarithms o(p), so Cp-bit entry errors satisfy
the margins eventually. Inverse coefficient magnitudes separately use the
retained chirp guard and shifted-symbol bound. This is a representability
and perturbation statement, not a free inverse-construction algorithm.

The rounded source specialization is all-broad or all-narrow. It requires
matching square grids and the stated same-cell phases. A mixed family needs
its own separation argument. Global periodic wraps, cross-cell coefficients,
identity holes, rectangular blocks, independent row/column permutations,
Schur pivots, repeated copies and an actual current whole caller remain
outside this result. Source acquisition, setup, gauge application, transport
and coefficient access stay charged.

## Evidence and reproduction

`PROOF.md` supplies the universal algebra, geometry, all-parameter source
inequalities, inverse transfer and cost scope. `verify.py` imports no
predecessor executable. It authenticates three exact proof/source inputs,
searches all 81,464 vertex permutations for each of forward and exact-inverse
targets across nine small fixtures, and checks 922 rational physical-source
exponent identities. Separate rational perturbation calculations cover the
forward and inverse margins.

The rational local parameters test the displayed source identities and
phase inequalities; they are not a finite prime-construction instance or
a complete production coefficient page.

Eleven controls include tiny gauges rounding a distinct-width matrix to
nonzero identity, a commuting monomial of infinite order whose permutation
is involutive, omitted diagonal-product conditions, inverse pair-ratio
misuse, the difference between an inverse section and a section inverse,
outside-cell phases, and invalid mixed-width edge bands. Finite checks
corroborate the proof; they do not establish universal quantifiers.

Run from the repository root:

```sh
python3.12 -I -W error -B research/gauged-physical-gaussian-symmetries/verify.py
python3.12 -I -O -W error -B research/gauged-physical-gaussian-symmetries/verify.py
python3.12 -B scripts/research_package.py --package research/gauged-physical-gaussian-symmetries
```

Direct commands are read-only and print JSON with status
`PASS_GAUGED_PHYSICAL_GAUSSIAN_SYMMETRIES`. Recording a new receipt requires
explicit `--write PATH`. `RESULT.json` records primary executed coverage;
separate review assets, when included by the orchestrator, identify their
own independently executed methods and limits.

## Source pins, novelty and credit

Canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`.
`DEPENDENCIES.json` pins the exact C6 proof at
`be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7` and the canonical fractional-shift
and fine-prime notes. `SOURCES.json` binds repository provenance;
`OVERLAP.json` records bounded exact PR-body comparisons and live searches.
The published predecessor proof was compared directly with its exact remote
contents. No full-history checkout gate is inferred from a shallow cache.

The diagonal-scaling invariant, finite-box isometries and Neumann identity
are classical. Novelty here is the exact monomial and physical source/error
boundary omitted by the predecessor, not a claim to invent those tools.
Production denominator work in CrocSwap/integer-mult-bounds#6099 and the
weighted periodic inverse in CrocSwap/integer-mult-bounds#5216 have distinct
domains and remain credited. Their global caller obligations are not closed.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit the preceding orbit and heterogeneous-width packages, Vlado
Vojdanovski's capped phase-cell work, the fractional-shift and fine-prime
lineage, and the retained source attributions. The lead orchestrator proposed
the invariant/error objective; the worker independently derived and checked
the source bounds, exact centralizer and controls. Separate AI-agent review
is not human or formal-kernel acceptance.

## Open next questions

1. Can one actual source tile use an implicit or non-cycle generator format
   with a fully paid application below the current axis-wise cost? Start by
   specifying coefficient access, setup, precision, inverse and transport
   costs; the dense-format floor alone does not decide that question.
2. Can the normalized invariant be adapted to rectangular or independently
   indexed row/column blocks? Their diagonal matching and underlying
   permutation problem must be specified first.
3. Can an actual rounded periodic/current-caller matrix be identified with
   this local boundary, including wraps, cross-cell entries, identity holes
   and all error transfer? The present source specialization supplies only
   the stated physical square factors.

## Independent review

`review/REVIEW.md` records a separate rational-complex checker and direct weighted commutator solution, with no imports from the author mathematical implementation. It checks 822 complete permutations for each forward/inverse target across six fixtures, 1,252 physical-source exponent identities, the precision inequalities and ten negative controls. Normal and optimized receipts agree. The physical entry-error tolerance does not establish that the actual global source pipeline supplies that error; that obligation remains explicit.

```sh
python3.12 -I -W error -B research/gauged-physical-gaussian-symmetries/review/independent_check.py --package research/gauged-physical-gaussian-symmetries
python3.12 -I -O -W error -B research/gauged-physical-gaussian-symmetries/review/independent_check.py --package research/gauged-physical-gaussian-symmetries
```
