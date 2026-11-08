# Physical seven-product matrices at the boundary-page caller

**No new κ.** This package implements the fixed-tape seven-product matrix
kernel left open by CrocSwap/integer-mult-bounds#5059, then substitutes it into
that unchanged rounded two-pass boundary function. The algebraic identity,
rounded block theorem and original page protocol are inherited from #4186
and #5059; the new result is their exact physical kernel and caller refinement.

**The measured small instance gets slower.** On the actual B=4 caller fixture,
scalar products fall from 768 to 588, but checked-transaction tape actions rise
from 44,814,681 to 212,425,677. The result establishes the asymptotic subcubic
implementation with complete movement and space accounting. It does not claim
a finite-size speedup, an improved supplier certificate or a complete lower
multiplication bound.

## Exact kernel and complete invoice

`SevenProduct.run(first, second, block, width, wide)` accepts two B²-entry
row-major integer matrices, with `B=2^ell`, w-bit signed input records, and
`wide=2w+ell+2`. It returns their exact unrounded product at that width. The
input counts, current recursion dimension, all numerical data and copy lengths
remain encoded. A flat traversal parks parent quadrant/accumulator data and
one finite continuation on a physical stack; it uses no host recursive stack,
indexed matrix fetch or decoded dimension. One fixed arithmetic owner executes
all `7^ell` signed scalar products. There is no precision parameter P.

With `U=w+ell+2`, `V=2w+4ell+4`, `L=1+ell+ceil(log2(w+2))` and the inherited
scalar time/space services `M(U), S_word(U)`, the complete kernel bound is

\[
 O\bigl(B^{\log_2 7}[M(U)+V L^3]\bigr),\qquad
 O(B^2V+S_{word}(U))\text{ fresh storage}.
\]

This includes quadrant extraction/reassembly, signed intermediate arithmetic,
all parent-frame parking/restoration, input promotion, exact return narrowing,
metadata, erasure and return consumption. Erased historical backing remains
charged on reuse. `PROOF.md` supplies the universal argument and inherited
scalar-service boundary; finite fixtures do not replace that proof.

## Actual caller integration

`FastBoundaryPages` is a separate, explicitly dyadic entry. The old general
positive-B `BoundaryPages` remains unchanged. The adapter retains its exact
`run` and `pass_blocks` function, including all P-rounding sites, partial-row
and partial-RHS zero checks, and both whole-row reversals. It invokes the
child while suspending its own scratch scope, copies the complete exact wide
product, and consumes the child before continuing. Full deep-role alias checks
precede metadata reads, and an explicit pending flag protects moved outputs.

For `K=ceil(n/B)` and `J=ceil(R/B)`, the two-pass invocation executes exactly
`2(2K-1)J` matrix products and `2(2K-1)J*7^ell` real scalar children. Keep the
ceilings when n or R is smaller than B. `BOUNDARY.md` gives the complete
additional scan/control bill, retained space, separately paid reference/page
setup and the exact numerical composition argument.

The principal source fixture executes unchanged `Core.gather` and
`Core.first_cell` on three distinct signed complex payloads, yielding six
actual RHS columns and five Schur rows. B=4 therefore exercises two row blocks,
two RHS batches, nonzero coupling, padding and both reversals. The physical
encoded `prepare_pages` creates the coefficient banks. The reference is the
inherited fixture's exact `LU(round_P(S))`, with P=16 and w=32. No additional
claim against original S is inferred from this supplied reference.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/physical-seven-product-matrix
```

All six registered commands must pass: the kernel, inherited caller and
separate independent implementation checks, each under normal and optimized
Python (`-I -O -B`). Expected JSON statuses are `PASS_PHYSICAL_SEVEN_PRODUCT`,
`PASS_FAST_BOUNDARY_CALLER` and `PASS_INDEPENDENT_SEVEN_PRODUCT`. Inputs are
hashed before numerical loading. Exported replays require the 19 declared
canonical input files, including the unchanged authenticated nested archives;
no Git or network operation is needed by those replays.

The actual caller command is:

```sh
python3 -I -B research/physical-seven-product-matrix/boundary_verify.py
```

It compares all returned bits against both the unchanged classical physical
caller and the independent exact rounded-block oracle, repeats the full
transaction on the same owner, and exercises the singleton/empty-coupling
case. The full n=5,R=6,B=4 checker deliberately costs substantially more than
one invocation: it includes baseline, two fast executions, source preparation
and negative controls. The six-command package usually takes several minutes.

## Verification and limitations

The author kernel checker covers B=1,2,4,8, signed inputs, metadata sharing,
odd/even signs, cancellation and the most-negative signed input. It checks the
exact classical answer, literal scalar/node/frame counts, pending return,
borrowed restoration and all retained backing. Nine malformed-input/ownership
controls and two executed kernel mutations check missing updates and inadequate
internal headroom. Fresh and previously widened owners perform identical
current narrow-call actions while retaining different storage histories.

The separate source-aware AI verifier uses a direct cubic exact-integer
oracle, without the seven-product schedule, and independent fixture loading,
physical output reads and reachable-role enumeration. Its cancellation cases
make signed intermediate overflow distinguishable even when the final answer
fits. The caller checks seven structural/lifecycle controls, including a short
coupling page after a completed child, and independently tracks constructor
roles: 1338 for the kernel, 2658 for the integrated caller. Finite replays use
the unchanged scalar engine's base branch; its all-size FFT branch is inherited.
Neither review is human acceptance or a proof-kernel certificate.

`RESULT.json` retains finite evidence. Action counts mean finite-alphabet
reads, writes and unit moves. They exclude host interpreter overhead and
external observers; binary simulation has a fixed encoding factor. The caller
counts cover the declared checked transaction, including consumption and an
output-head scan, and the fast pending-output probe. Source setup and packing
are reported separately and remain charged in the complete invoice.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`SOURCES.json` pins every source, `TASK.json` records the inherited card and
scope refinement, and `REVIEW.md` records the separate review. The complete
selected multiplication bound and all five global assumptions remain unchanged.

## Open next questions

1. Bind this fast many-column service to a complete source family using the
   existing #5500 reference-growth and #5506 normalized-return work, with every
   grid conversion, field gather and setup lifetime paid. A finite collection
   of three actual payloads does not establish a new outer many-field source.
2. Reduce the observed small-instance overhead through one proved hybrid
   threshold or frame schedule, while preserving exact product semantics,
   complete movement and retained-history accounting.
3. Extend the explicitly dyadic entry only after proving and pricing the
   padding or mixed-size ABI. The old general-B classical entry remains usable.

Contribution by @CubeJerry, with substantial OpenAI Codex assistance in
research, implementation, proof, integration and verification. The kernel,
caller integration and independent mathematical/physical audit were developed
by separate AI researchers. `NOTICE.md` credits the predecessor mechanisms
and retained source files. Repository Apache-2.0 licensing applies.
