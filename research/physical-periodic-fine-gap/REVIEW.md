# Independent review of the full periodic caller

Prepared for @CubeJerry by a separate source-aware OpenAI verifier.
Apache-2.0. This is independent mathematical and implementation review, not
proof-kernel verification or human acceptance. No new κ.

## Scope and reviewed bytes

The review checks the new caller's composition against the original fixed
Reference, its physical coordinate interfaces, and its claimed streaming
invoice. It reuses the authenticated original Reference definition and the
fixed physical tape runtime. Its expected inverse is not computed by RUN,
folded LU, the two-pass Schur formula, or the author's rounded-stage oracle.
The inherited RUN and folded components retain their own stated contracts.

Reviewed implementation SHA256:

* `periodic_consumer.py`:
  `30f49f7392028a086156975a2eaf76291c8318cc59f02d9bd9dadf79d6321017`
* `periodic_tapes.py`:
  `bc5149050244e403bb876b96019534377ec37e032f9bc9299d2e9471d09dec04`
* `periodic_pages.py`:
  `6d17558c953f794010393b87ca2f5cbfcca1952b8d7580d268e841b7b4cac45e`

`original_periodic_oracle.py` and `transport_review.py` are portable review
modules. The first accepts the actual returned integer vectors, source
Reference, grid, declared bound and optional requested bound. The second
accepts a fresh/consumed physical owner and an always-active `need` function.
Neither uses `assert` for required checks. The integrating verification runner
must call them in normal and optimized isolated Python modes.

## Original-matrix numerical evidence

For each fixture the oracle requests **every entry of the full target-sized
narrow Reference matrix**, including identity holes and original period-wrap
entries. It performs rational Gauss-Jordan inversion with pivot search and
checks every entry of the resulting original matrix/inverse identity. It then
acts on both original complex input components and compares the actual
physical output. Selected coordinates are independently reconstructed as
`i + floor(k*i/S + 1/2)`; every hole's row and column are checked against the
identity, and its returned word must equal its original input word exactly.

| Fixed Reference | Original target | Matrix identity checks | Maximum component-l1 error | Declared allowance |
|---|---:|---:|---:|---:|
| `(7,2,2,1,3,96)` | 9 | 81 | `1.11609808344402e-15` | `2.862191843175298e-7` |
| `(17,1,2,2,3,96)` | 18 | 324 | `3.4765812786614546e-19` | `7.203156040163306e-10` |

The first fixture has holes 2 and 7 and two nonzero original wrap entries.
The second has hole 9 and six such entries. All hole words are exact.
Complete rational errors and residuals, rather than only the decimal display,
are preserved in the review receipts and recomputed by the verifier.

A negative control forms a different original matrix by deleting its nonzero
wrap-lift entries, inverts that matrix independently, and compares its action
with the same actual output. The wrong-model errors are respectively
`7.943390911829424e-7` and `7.459051065668735e-7`; both exceed the declared
allowances. The first does **not** exceed the looser requested `2^-16`; the
second also exceeds its requested `2^-24`. This control is a demonstrated
wrong-target discrepancy, not an executed mutation of the production caller.
The author's separately implemented rounded-schedule comparison provides the
complementary exact-bit check; a loose numerical tolerance alone would not.

These inverse comparisons were executed on the two recorded physical
outputs in normal mode, and the final portable oracle in isolated optimized
mode. The complete integrating runner re-executes the actual physical calls.
The reviewed finite fixtures use the word engine's base branch. They do not
independently certify its unexecuted recursive FFT branch.

## Physical coordinate and ownership evidence

`transport_review.run` executes the real extraction/merge helpers with signed
six-bit words on seven target positions, four selected positions and three
holes. Expected selected data and original-order merged records are formed
by a direct finite-coordinate oracle independent of the consumer's traversal.
Helpers run with payload decoding disabled and constructors sealed while
encoded arithmetic uses the owner's fixed pool. The review checks all borrowed
bodies and heads before and after, then checks all 4,602 owned roles for blank
retained backing and canonical origins.

The following guards were executed in normal and isolated optimized modes:

* Duplicate external input/mask roles reject before execution.
* A descendant-owned role supplied as an external input rejects, even though
  it is inactive and blank.
* A moved original input head rejects and retains its entry head and bytes.
* A target mask with too few selected entries rejects at its cardinality check.
* A truncated target mask rejects at the required next mask bit.
* Both extraction failures restore every borrowed body/head and erase the
  complete owner; no child numerical call is needed to expose these failures.
* A constructed pending-output state, with its head moved to the trailing
  blank, rejects reentry. Public `consume` then clears and releases it. This
  deliberately checks that guard's state predicate; it is not claimed as a
  second complete numerical run.

A same-cardinality but differently placed mask gives a different expected
coordinate map and is detected by the independent mapping oracle. The caller
only checks mask shape/cardinality. **Source semantics are a preparation
premise**, established by the authenticated producer and original-source
comparison; arbitrary same-cardinality tampering is not authenticated online.
This is the intended prepared-port contract, not an extra hidden source lookup.
The author's executed toward-zero/floor and complete-dot/productwise-rounding
controls check different numerical mechanisms and complement this review.

## Composition and cost findings

The physical schedule agrees with the stated two-call identity. The first
RUN pass consumes each native result completely while restricting its output
to the boundary mask; the second consumes that mask while subtracting the
next correction from the original source input. Native page and source heads
advance monotonically through all runs and rewind only after a complete pass.
Six reused local coefficient buffers are cleared by their live prefixes, not
by their historical maximum sizes. Every RUN and folded return is consumed
before child reuse. The parent scope suspends around child execution.

If run i has n_i positions, cutoff L_i and r_i=ceil(n_i/L_i), each residual
page has R_i=3n_i+2L_i(r_i-1)<=5n_i records. Hence the six extracted banks have
4n_i+2R_i<=14n_i native records. Four real dispatches per complex call charge
four times this volume, not a fresh full catalogue scan for each run. Reading
all native returns, both grid conversions, and all source/target scans remains
O(TP+SP) movement. Fixed-many header products involve encoded bit lengths
O(log(P+1)(log(n_i+1)+log(P+1))); their cost is absorbed by O(n_i P),
as are descriptor
comparisons and amortized encoded loop counters.

The band window invariant is exactly coordinates i-b through i+b in folded
order. Each row uses 2b+1 signed products, one completed accumulation, and one
rescaling. Its source head advances monotonically; only the O(b)-record local
windows are copied/cleared per row. Four applications per complex call use
4m(2b+1) scalar products. Two public folded solves contribute 2m(2b+1) more.
The total folded-owner product count is therefore 6m(2b+1), independently
predicting 150 and 624 observed base products in the two fixtures.

The complete favorable invoice in `PHYSICAL.md`,

`O(TP + S M(P) + sum_i sum_j M(N_ij P) + mb M(P))`,

retains packed arguments N_ij P with N_ij<=2L_i; they must not be replaced
by scalar P arguments. The source preparation and serialization bill remains
separate and polynomial, and cannot be charged away as a free entry oracle.
Retained space includes every fixed role's historical maximum and still-live
prepared pages, not just the final short run or the final active lease count.
The reused native `Tape.clear` stops at the current first blank and does not
rescan an old blank tail; this was independently checked in the earlier RUN
runtime review and its unchanged source was reused here.

No blocking discrepancy was found in the reviewed source/physical seam.
The theorem still assumes correctly prepared pages, a radius-compliant input,
the fixed Reference admission gate, and the inherited exact word routine.
It proves the stated narrow inverse interface, not the broad/normalization or
outer multiplication assembly obligations. Finite agreement and this review
do not remove those assumptions or establish a stronger κ.
