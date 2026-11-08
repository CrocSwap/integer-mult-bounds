# Complete physical fine-gap periodic Reference inverse

This package joins the completed ordinary-run and folded-boundary components
into one coefficient-bound physical periodic inverse. It executes both
block-inverse passes, the two boundary matrix applications, the folded Schur
solve, every conversion between unequal native grids, and the target-sized
complex selected/identity-hole interface. The original input and all prepared
pages are restored; the caller consumes one protected output. **No new κ.**

The old Schur identity, q-factorization, word multiplication, convolution and
folded band solver are inherited. What is new is their complete source-bound
physical composition, including a source-prepared common/native precision
budget and enlarged second-call radius. The latter matters: independently
checked unit-radius inputs produce a second block-solver RHS larger than one.
The source gate rejects a fixed Reference when its omitted tail cannot fund
the requested accuracy; extra execution precision cannot remove that error.

## Reproduction

From the repository root, with the two checked component commits present:

```bash
python -I -B research/physical-periodic-fine-gap/verify.py
```

Expected first success line:

```text
PASS_PHYSICAL_PERIODIC_FINE_GAP
```

The following JSON receipt records exact page/source hashes, the physical
word-product bill, original-reference inverse checks, restoration/erasure,
and executed negative controls. The registered default is the nine-target
lifecycle fixture: ordinary runs 2,4,1 use native grids 89,89,62 and carriers
145,145,91. One fixed owner therefore grows, shrinks and processes a singleton
while also exercising genuine wrap couplings, interior rows and two holes.
The same command with `-O` is registered independently.

An extended target18 source is available with `--main`. It exercises source
halfwidth2, folded half-band6, ordinary runs9,8 and nonempty interiors. This
longer replay was also executed; it is explicitly outside the default bounded
verification command. Its saved evidence and independent original-source
comparison are documented in `REVIEW.md` and `RESULT.json`.

## Exact result and proof locations

`periodic_pages.py` prepares actual rational Reference run blocks, masks,
SB/K banks and the unchanged native solver pages, without inspecting an
online RHS. `NUMERICAL.md` proves source compatibility, conversion/radius
budgets and the full complex error bound, with a separately charged corollary
for the corresponding ideal periodic narrow operator.

`periodic_consumer.py` executes a single complex RHS using fixed physical
roles and encoded Count/Signed control. `PHYSICAL.md` proves the sequential
catalogue/window invariants and gives the complete bill, including all page
extraction, copying, restoration, conversion, returned-word consumption and
retained high-water space. `periodic_tapes.py` pays for physical preparation
of every borrowed page and descriptor.

For common scalar width P, native run windows N_ij and boundary size m, the
online bill is

    O(TP + S M(P) + sum_i sum_j M(N_ij P) + mb M(P)),

where b<=4w−2 and M is the inherited exact word-product cost. One complex RHS
makes four real RUN calls per ordinary run and two folded solves; all four
SB/K applications are included. Under the stated fine-gap parameter regime
and inherited word bound this gives
O(S p log²p + (K_source+1)w² p log²p), with input-independent exact rational
preparation and page emission paid separately. No scalar-width bound is used
for the longer packed convolution arguments.

## Verification and limitations

The physical result is compared bit for bit with an external exact integer
schedule and independently with the full original rational Reference inverse
using Gauss-Jordan elimination. The source/Schur check uses inverse principal
subblocks, independently of the producer's direct Schur/LU construction.
Actual physical controls distinguish toward-zero conversion from negative
arithmetic-floor shifting, and completed-dot rounding from rounding each
product prematurely. Alias, inactive-descendant alias, truncated-header and
unconsumed-output controls exercise the fixed-owner boundary. Omitting period
cut coefficients fails the source contract; removing original wrap entries
also violates the declared numerical allowance in both physical fixtures.

The finite fixtures exercise the inherited base word branch; the larger FFT
branch and its universal contract are inherited, not newly replayed here.
Finite replay validates instances and the implementation. The all-size result
rests on the proofs and the frozen component contracts, including the word
routine's published assumptions. Positive nonidentity Reference geometry,
source admission, the promised input radius, canonical distinct ports, paid
source preparation and the caller's output-consumption contract remain
explicit. This package does not supply the complete outer Gaussian/tensor,
normalization, CRT or multiplication caller, and does not discharge all five
selected framework assumptions. Source caches and earlier prepared banks
remain charged while retained.

## Provenance and attribution

Canonical research base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The new-component source pins are public fork commits:

- RUN: `41defd0faaad9656e5f0c3d15445cb94e61077ea`.
- Folded solver, cumulative on RUN: `d8c9d2c366925682e03cb9e38bc1a9c7d8d16c1b`.

`SOURCES.json` pins complete input bytes and Git blobs, including the nested
word-runtime archives. This resolves the periodic-composition question in
`research/physical-fine-gap-run/TASK.json`; it extends the mechanism of
CrocSwap/integer-mult-bounds#5571 using the physical interfaces of
CrocSwap/integer-mult-bounds#3851 and #3787. Folding and the effective rounded
Schur analysis are inherited through the folded component from
CrocSwap/integer-mult-bounds#4879 and #5319. The older
CrocSwap/integer-mult-bounds#5483 binds a different inverse-block interface
and is credited as a physical caller precedent, not treated as this solver.

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance. Separate
AI workers developed the physical caller and coefficient/error proof; separate
source-aware AI reviewers checked original matrices, physical ownership,
precision and complete costs. This attribution does not claim human review
or proof-kernel certification. Apache-2.0; predecessor notices are retained.

## Open next questions

The next mathematical task is to bind this complete prepared inverse to the
actual outer fine-gap Gaussian recovery caller, including its source grid,
batching, tensor schedule and normalization/error budget. Its significance
is that a locally complete inverse can affect the multiplication proof only
when that full caller's costs and inherited hypotheses are checked. A first
step is an exact common-Reference page/interface map to the current core and
halo components, followed by the complete composed error and tape invoice.
This package leaves that source/caller composition unimplemented; it does not
assume those independent component results automatically compose.
