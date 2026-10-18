# Independent mathematical audit

The proposed construction is valid in the stated **forward, common-chart,
monotone correction model**. Exactly 78 source-acquisition lifetimes are
necessary and sufficient for correcting Y0 and Y1 together. Under the
additional requirement that every new helper enters at ZERO and exits at FULL,
with dimension-gap transport charges, the sharp added rank mass is 702.
The displayed ADD count and rank histogram are those of this word; their
individual optimality is not proved.

This review uses the fixed source files at base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The one-target predecessor is
[PR #2393](https://github.com/CrocSwap/integer-mult-bounds/pull/2393), inspected
at `8b3e3a22c9e957990863ef60a561072dfcf08271`. Its README supplies the
source-acquisition argument and poses the two-target sharing question. Its
executables were neither imported nor copied. The reviewed `CIRCUIT.json`
has SHA256 `c34d94128decc426e7528302ab2570967293a1b293f184fdd89fd376addd61f9`.

## Model checked

Original X registers are immutable and retain their fixed frame paths. Added
reads may use X registers and new helpers only. No added read may use an
original G/Q/D/private register or any Y target. Added operations consist of
scalar additions within one common frame and upward transports of new helpers.
The original event order is retained by this construction. Target writes are
additive. The coefficients do not depend on input values.

Every new helper has an independent arbitrary dirty input. Restoration means
the same **logical value in its final FULL chart**; the physical entry and exit
arrays are not asserted equal. The inherited eight owned private-copy
allocation/copy/descent/discard lifetimes of the original word remain present;
they do not become additional reversible dirty inputs.

The lower bound allows arbitrary source/target retiming consistent with their
retained paths, arbitrary same-frame relays, arbitrary rational coefficients,
and cancellation. It does not require the lower-bound candidate to restore its
helpers. Every helper lifetime must start source-independent, and its frames
must remain monotone. Reinitializing a physical helper starts a new lifetime.

## Finite premises and lower bound

Reconstruct the 120 E8 root lines using doubled integer coordinates, normalize
the first nonzero coordinate positive, remove the fixture's two eight-line
frames, and sort the remaining 104 ports. Let
`C[t,s] = delta(t,s) - dot(root[t],root[s])/8`. This reproduces the required
correction to the original G/2 channel.

The independent check derives these facts from the two frozen inputs:

* Both correction rows have 48 nonzero coefficients, all `+1/2` or `-1/2`.
  Their intersection has 18 sources; their union has 78.
* For **each of the 96 required target-source pairs**, the initial source line
  is contained in the target's final eight-dimensional frame. The first source
  expansion already contains a vector outside that frame. All later source
  frames contain the first expansion. Thus only the initial line can be used
  by a monotone dependence path to that target.
* Every target frame is contained in its endpoint. There is no equal-frame
  source-to-target contact anywhere on either retained path. The 78 required
  initial source lines are distinct.
* The endpoint intersection J has dimension seven and contains all 18 shared
  initial lines. The shared ratios `C[1,s]/C[0,s]` are nine `+1` and nine `-1`.

For a concrete witness, shared source X2 starts on line `<228>`. Its first
expansion contains vector 8, which lies outside both endpoints. The program
constructs an escape witness for every required pair; their canonical digest
is `b7a1c65174cf595d09308dd7bc53b70fd791dc71d093fda67249834b1196f465`.

For each source in the union, choose a target with nonzero correction
coefficient. That coefficient requires a directed dependence path from the
source into an added write to this target. A path's frames can only increase,
so all its frames must lie in the target's endpoint. The finite escape premise
forces its first source read to occur on the source's initial line. The
no-contact premise forces this read into a new helper.

Choose one such read for each union source. A monotone helper lifetime cannot
visit two different one-dimensional frames: those frames are incomparable.
Consequently these 78 reads require 78 distinct lifetimes. Cancellation cannot
avoid the conclusion: without a dependence path the corresponding coefficient
is identically zero for all choices of scalar coefficients.

This is a written proof for arbitrary word length and rational mixing in the
specified fixed-path model, with its finite geometric premises checked
exhaustively. It is not a bounded search. Neither a 96-lifetime bound nor a
sum of 48 over all 104 targets follows: a shared acquisition can serve multiple
targets. The argument also does not apply when original-channel helper reads,
source-dependent descents, or changed source paths are allowed.

The initial-only premise is essential. For a changed-path countermodel, let
two sources start on `<1>` and `<2>`, then both expand to `K=<1,2>`. Let the
target go from ZERO to K. One dirty helper can compensate its input into the
target at ZERO, rise to K, read both sources there, and deliver their weighted
sum. Afterwards the helper and both sources rise to FULL, where subtracting
the two captured terms restores the helper. Distinct initial lines alone
therefore do not imply two lifetimes; the first-expansion escape premise
excludes exactly this later common-frame acquisition.

## Construction and restoration algebra

There are 30 sources exclusive to each target and 18 shared sources. Give each
union source one helper Ns. For an exclusive source set
`z_s = d_s + C[t,s] x_s`; for a shared source set
`z_s = d_s + C[0,s] x_s`. Capture each source once at its initial line.

For the exclusive groups, gather their 30 values into one collector at the
appropriate endpoint Ht. For the shared group, move all 18 helpers to J. Pick
a shared pivot a of ratio `-1` and b of ratio `+1`, put `u = z_a`, `v = z_b`,
and perform

```
u += v
v -= u/2
for each shared nonpivot s:
    u += z_s
    v += (ratio_s/2) z_s
```

The result is exactly

```
u = sum_shared z_s
2v = sum_shared ratio_s z_s.
```

The two pivot updates are elementary determinant-one shears, so no extra
clean register is needed. Deliver u to Y0 with coefficient one and v to Y1
with coefficient two, using the legal upward paths `J -> H0` and `J -> H1`.
The two exclusive collectors give the other two deliveries.

At ZERO, before any capture, the word subtracts every exclusive `d_s` from
its target, and subtracts `d_s` and `ratio_s d_s` from Y0 and Y1 respectively
for each shared helper. These 96 initial scalar additions cancel precisely
the dirty contributions in the four later deliveries. The original word
contributes G/2, so Y0 and Y1 finish as `y0+x0` and `y1+x1`.

All helpers then reach FULL. Reverse every gather shear in reverse order,
including the shared half-shears, while all source helpers remain available.
This restores each helper to its own `z_s`. Finally subtract the original
capture term using Xs at FULL. Every new logical dirty input is restored.
The original word never reads a Y register and never writes an X register,
so the two added blocks do not perturb its G/2 contribution or its helpers.

## Exact finite replay and accounting

Run the independent, standard-library-only checker with assertions disabled:

```sh
python3 -I -O -B research/p104-two-target-sharing/independent.py
```

The checker consumes the fixed certificate; it never generates a missing
certificate. It imports no constructor, primary checker, predecessor checker,
or frame library. It uses dense integer coefficient vectors with one normalized
power-of-two denominator per row and Gaussian elimination over F2. The expected
endpoint is derived from the root coordinates, not from constructor metadata.

The replay checked all **358 independent input columns** and all **128,164
endpoint coefficients**, including every original dirty input and every new
dirty input, through all **4,734 events**. All 104 source rows, 72 original
dirty rows, and 78 new dirty rows restore; Y0/Y1 have the desired identity
correction and the other 102 Y rows retain G/2. All final frames match.
The original 4,058-event, 280-column channel also passed independently as
a baseline. These are exact coefficient comparisons, not sampled inputs.

| Added quantity | Exact value |
| --- | ---: |
| Helper lifetimes | 78 |
| Scalar additions | 440 |
| Source reads | 156 |
| Upward transports | 236 |
| Final writes to Y0 / Y1 | 2 / 2 |
| Rank profile | 142 H1 + 16 H2 + 18 H6 + 60 H7 |
| Rank mass | 702 |

The ADD decomposition is 96 dirty compensations, 78 captures, 92 gather
shears, four deliveries, 92 reverse shears, and 78 source cleanups. Every
monotone ZERO-to-FULL lifetime pays nine rank units by telescoping dimension
gaps, so the construction attains `78*9 = 702`. This sharpness depends on that
entrance/exit convention; it is not a transport floor when entrance or exit
frames may be granted for free.

There is a concrete tradeoff. Give each of the 96 nonzero correction entries
its own dirty helper, compensate at ZERO, capture at its source line, deliver
at its target endpoint, and clean up at FULL. That direct word uses 96 helpers,
864 boundary rank mass, and only 384 ADDs (four per entry). Thus the present
word saves 18 helpers and 162 rank units at the price of 56 extra scalar ADDs.
Its lower helper count is not a claim of scalar-ADD or combined-cost optimality.

Across every executed prefix, the maximum reduced logical scalar numerator
is 3 and the largest denominator is 4. Those bounds concern logical linear
coefficients only, not physical Clifford amplitudes or a recursive precision
budget. The independent endpoint digest is
`06bb7a80bd66611a948726ae308162ef3be1ace6add12a4dbe28a9e4efb8d930`;
its serialization includes the full column order and every normalized integer
row, after exact endpoint comparisons have already passed.

Seven controls reject for the intended reason: removed initial dirty
compensation, removed capture, a reversed half-mix sign, removed unmerge,
removed final cleanup, wrong transport charge, and wrong-frame source read.
Reordering every added frame basis is accepted as an equivalent presentation.
Unexpected acceptance is raised outside the exception handler. The reported
run used Python 3.14.6.

## Remaining obligations

No native Clifford recipes or global phases for the new transports are
verified here. New scalar/address lowering, physical precision, chronological
global owners, residual and idle recursive children, the other 102 target
corrections, all-size admission, and any resulting recursive moment remain
separate obligations. The original channel's native proof does not certify
the newly introduced transports merely because the logical charts agree.
This result does not claim a full supplier, a new kappa, a reverse-orientation
supplier, an independent human review, or a formal-kernel proof.

The relevant next handoff is to extend acquisition sharing to additional
targets while keeping an explicit restored word and a complete local invoice.
A native-complex or frame specialist must separately discharge the new
transport recipes and phase obligations before claiming physical realization.

This proof audit and separate interpreter were written with substantial
OpenAI Codex assistance by the exact-circuit-verification specialist.
Apache-2.0; predecessor authors and frozen artifacts retain their attribution.
