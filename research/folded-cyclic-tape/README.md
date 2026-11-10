# Physical folded Gaussian boundary solve

**Result:** an actual fixed-role tape caller that folds original-order
right-hand sides, invokes the unchanged physical banded solver, and
returns every answer in original order. Its source-bound preparation
chooses precision and storage from a positive row gap, pays factor
serialization and all movement, and works for multiple right-hand sides.
An exact retained Gaussian Reference supplies a nontrivial periodic Schur
fixture through the complete physical interface.

**No new κ.** This addresses the physical-caller question retained in
CrocSwap/integer-mult-bounds#4879. It does not prove complete periodic
Gaussian inversion, selected/hole recovery or the outer multiplication
theorem. All five selected framework assumptions remain.

## What is new and what is inherited

The folded order and its single-arc bandwidth bound already belong to
#4879; they are not a new lemma here. The scalar `BandedSolve`, exact
signed arithmetic and actual word multiplier are unchanged dependencies
from #3851 and #3787. The correct interpretation of a stored pivot
reciprocal is inherited from #5319. The pinned row-gap elimination note
already supplies generic factor-growth bounds.

This contribution binds those results to a literal caller: both ordered
conversions, every RHS, complete child returns, restoration, cleanup,
inactive descendant ownership, encoded controls and retained storage are
present. The coefficient plan proves an error bound on actual rounded
inputs. Exact rational preparation is separately priced, including its
matrix access and serialization; it is not a free online helper.

The main numerical target is the **original rational Schur matrix**.
Preparation computes exact LU of that matrix before rounding factors and
pivot reciprocals. It does not silently reuse a theorem about a different
matrix or omit an initial matrix-rounding error. A caller that first
rounds its Schur matrix must add that distinct perturbation.

## Mathematical and physical contract

Let A have positive diagonal, row gap d>0 and row norm M. Its simultaneous
folded order must fit the supplied positive band b. For a prescribed
input radius R and target error 2^-t, the plan computes grid precision p
and signed width W. The actual rounded effective factors obey a proved
matrix perturbation and completed-equation residual bound. This gives
the final error for every admitted input, without selecting precision
from an observed test maximum.

`pages.prepare(A, band, target, radius)` produces the exact source-bound
plan. `factor_tapes.EncodedFactors(plan, rhs_count)` emits two persistent
factor banks and five distinct Count descriptors `(n,r,b,W,p)`. The
online call is

```python
returned = owner.run(*prepared.streams, rhs_tape, *prepared.counts)
# Physically read exactly r*n signed W-bit records in original order.
owner.consume()
```

Records use the unchanged two's-complement Signed convention, with
least-significant bit first. Lower rows are forward, storing distances
b down to one. Upper rows are backward, storing distances one through b
and then the rounded pivot reciprocal. The RHS and return are RHS-major.
The online algorithm does not decode a payload to a host integer.

A finite pending flag prevents reuse while a return remains owned, even
after its head reaches a trailing blank. Borrowed origins are inspected
through paid delimiter operations. The fixed inventory includes inactive
word-engine descendants, and the parent factory scope is suspended across
the child call. All nonoutput owned cells are blank at return; consumption
also erases the protected output. Historical blank capacity remains
charged after erasure.

## Complete cost

For r RHSs of length n, the unchanged child performs exactly `2rnb`
ordinary scalar products and `rn` wider reciprocal products. Its wider
operand has `2W+ceil(log2(b+1))+2` bits. Both factor banks are scanned on
every RHS. With Mv the inherited actual word cost, the generic online
bill is

```text
O(rn [b*Mv(W) + Mv(2W+ceil(log2(b+1))+2) + (b+1)W] + log(r+1)).
```

The plan includes the band and line counter widths in W, so #3787's
`Mv(v)=O(v log^2(v+2))` gives
`O(rn(b+1) W log^2(W+2) + log(r+1))`. Fold/unfold, local reversals,
source and return rewinds, output consumption and all erasures are paid.
Amortized encoded ripple counters avoid a full counter scan per bit.

The whole call retains `O(n(b+r+1)W + log(r+1))` cells, including factor
banks, input, protected output, scratch and erased backing. Across reuse,
take each role's maximum historical extent. Input-independent source and
rational Schur/factor preparation have their own explicit polynomial
time and space bounds in [PROOF.md](PROOF.md), followed by paid physical
serialization. Those setup terms can dominate a small batch and have not
been absorbed into an unspecified outer caller.

## Reproduction

Canonical upstream base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Python 3.12 and its standard library are sufficient. `SOURCES.json`
pins all ten live Reference/runtime inputs by Git blob and SHA256,
including the immutable source archives. Its remaining rows preserve
exact historical mathematical and task provenance.

From the repository root:

```sh
python3 -B scripts/research_package.py --package research/folded-cyclic-tape
```

Expected final marker: `PASS_REGISTERED_RESEARCH_PACKAGE`.
Six commands run the actual-source fixture, the separate transport
review and the separate allocation review, each normally and with `-O`.
All failure checks remain active with assertions disabled. The direct
source fixture is:

```sh
python3 -I -B research/folded-cyclic-tape/verify.py
```

Expected final marker: `PASS_PHYSICAL_FOLDED_REFERENCE`.
The direct scripts work in the committed export without Git. Normal
verification writes no files. `verify.py --write-receipt NEW_PATH` can
write a new receipt and refuses to overwrite one.

## Evidence and controls

The actual source is `Reference(9,1,1,2,3,32)`, with selected target
coordinates `[0,1,2,3,4,6,7,8,9]` and identity hole 5. Eliminating source
index 0 leaves an exact eight-row Schur matrix. It has folded band four;
target 16 and radius one give p=25 and W=30. Four signed real RHSs form
two complex inputs. The caller returns 32 physical records.

Three checks serve distinct purposes:

1. Every returned bit matches the complete integer page replay and a
   separate rational completed-row implementation.
2. Independent exact inversion of the original Schur matrix checks all
   64 matrix-product identity entries and bounds the actual physical
   error. Maximum component-l1 error is approximately `9.316e-8`.
3. Six original nonzero coefficients cross the source period cut.
   Omitting those coefficients or omitting the final unfold exceeds the
   allowed error, so the example exercises these interfaces materially.

`RESULT.json` retains the exact rational allowance, error, outputs and
source pins. The call executes 288 actual base-branch word products and
32,740,371 finite-alphabet read/write/move primitives, including literal
return consumption and erasure. It has 1,449 fixed owned roles and retains
8,672 owned cells plus 3,153 borrowed cells in this fixture. These are
primitive/cell receipts, with constant-factor binary simulation, not
complete Python VM counts or host-memory measurements. The FFT branch
of the inherited word routine is not newly exercised here.

The separate physical checker covers eight calls with singleton, odd,
even and decreasing sizes, 79 records, and exact nonuniform original
diagonal equations. Its controls reject descriptor aliases, inactive
descendant aliases, displaced input heads, a pending output on blank,
double consumption, short later RHSs and a zero reciprocal child failure.
All borrowed bytes/heads and full retained erasure are checked.

The separate numerical checker covers 27 signed cyclic-band matrices,
sizes one through nine, scales `1/128,1,16`, deterministic seed `720053`,
and two complex RHSs per matrix, plus the actual Reference Schur fixture.
The stopping rule is completion of that stated domain. It independently
checks effective matrices, inverse bounds, actual completed radii and
original-matrix errors. A scalar control distinguishes stored reciprocal
one-half from its effective upper diagonal two. This is finite
corroboration of the universal proof, not an impossibility search.

Review methods, corrections and limitations are in [REVIEW.md](REVIEW.md).
Separate source-aware AI review is disclosed; independent human or formal
proof-kernel acceptance is not claimed.

## Open next questions

1. Bind a complete periodic caller's actual Schur RHS assembly and
   eliminated-variable recovery to this service. Start with one exact
   reference, counted data-grid conversions and original-matrix inverse
   comparison. This package alone does not supply that caller.
2. For a caller eliminating several arcs, prove or validate the actual
   folded band before making its page plan. A single-arc `2w` allowance
   cannot be transferred automatically. Start with the caller's exact
   support and keep every repeated factor/application cost.
3. Establish the complete outer source/setup amortization and selected
   framework implications. Start from an actual axis range and RHS count;
   retain the explicit source, rational preparation and history-space
   bills until that absorption is proved.

These are remaining obligations at this component boundary, not claims
that no concurrent or later package can discharge them. Structured first
steps and blockers are retained in `TASK.json`.

## Attribution

Prepared for **@CubeJerry** with substantial OpenAI assistance in
implementation, proof, exact verification and separately assigned
source-aware numerical and physical review. Credit Nick Petalas (#4879),
Jose Manuel (#3851/#3787 and the retained Reference), the #5319 reciprocal
analysis, JoyboyBrian's retained row-gap/LU-growth proof, and Mason Hale's
interval/recovery lineage. The reference adapter is an unchanged reuse
from @CubeJerry's published halo component. Exact provenance and source
licenses are recorded in [NOTICE.md](NOTICE.md). Apache-2.0.
