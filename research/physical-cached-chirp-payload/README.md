# Source-bound physical cached chirp payload pass

**No new κ.** This package implements one chirp or conjugate-chirp pass on
actual complex coefficient fields in the axis-zero polynomial layout of
CrocSwap/integer-mult-bounds#4100. It closes the physical payload/intermediate
multiplier interleaving obligation left in the first open question of
`research/pr4100-chirp-odometer-tariff/README.md` (#4325), for the precise
prepared-source and inherited arithmetic boundary stated below.

The cached suffix identity, numerical stability and table-walk lemmas are
inherited. In particular, #5987 already proves the stronger largest-axis-fastest
travel bound. The new work is an executable encoded controller, its certified
source tables, actual scalar-word calls, complete movement/ownership invoice,
and independent checks against the original phase. The distinct source08
caller in #3935 and encoded monomial phases in #5375 do not implement this
cached-table schedule. The bounded successor search found no completed
consumer of this exact interface; it was not an exhaustive archive claim.

## Result

For dyadic radices `t_i>=2`, odd slopes `s_i`, largest radix `t_0` fastest,
and `T=product(t_i)`, the exact diagonal multiplier is

\[
 a(x)=\prod_i \exp(-\pi\mathrm i s_i x_i^2/t_i).
\]

A polynomial record contains `t_0` consecutive complex coefficient pairs.
`CachedChirp.run(payload, shape, tables, width, precision, conjugate=False)`
consumes this layout directly and returns the same layout. Each component is
a `W`-bit two's-complement word on a common `2^-f` grid. Shape, carry digits,
counts and addresses remain encoded; neither dimension nor record count is
an unbounded host control variable during execution.

The controller uses cached suffix products with fewer than `2T` updates,
four inherited exact scalar products per completed complex multiplication,
and one truncation per completed component. All table travel, counter-field
work, offset products, cache replacement, output consumption and restoration
are included. With `M(W)` the pinned word service's complete tariff, its
online cost is

\[
 O(T M(W)+TW+d^2W)=O(TW\log^2(W+2)).
\]

Here `d^2<=9T/8`; the final equality uses the inherited all-size word contract.
No hidden `Td` scan or per-record full-table rewind is admitted. Current
storage is `O(TW+W sum_i t_i+dW)` plus the word service's `O(W)` backing;
all earlier per-role high-water extents remain charged after erasure.

The source producer emits certified inward grid approximations in the unit
disk, with each component at most two ulps from its exact phase. For actual
input modulus at most `R`, the returned component-l1 error is at most

\[
 2\{R(3d-1)+1\}\,2^{-f}.
\]

The producer chooses `f` and `W` to meet the requested absolute error and
retain an already finer input grid. `SOURCE.md` pays its rational arithmetic,
coefficient serialization and retained interval-cache history explicitly.
That Python preparation is justified by a sequential polynomial simulation;
it is not presented as a literally metered fixed-tape elementary generator.

## Reproduce

From the repository root, using the standard library only:

```sh
python3 -B scripts/research_package.py --package research/physical-cached-chirp-payload
```

Expected result: all four registered commands pass. The two entry points emit
`PASS_CACHED_CHIRP_PAYLOAD` and `PASS_INDEPENDENT_CACHED_CHIRP` in their JSON
receipts. Each runs normally and with assertions disabled (`-I -O -B`).
The input manifest authenticates all five live source files, including the
unchanged nested arithmetic cohort. No network or Git command is used by the
registered replays; source checkout metadata is unnecessary after export.

A direct executable replay is:

```sh
python3 -I -B research/physical-cached-chirp-payload/verify.py
```

`RESULT.json` retains the exact finite receipts and negative-control outcomes.
Its counters concern the declared checked transactions; they are not measurements
of the whole Python interpreter or a proof of the asymptotic theorem.

The source instance `(t_0,t_1)=(8,4)`, `(s_0,s_1)=(7,3)`, `R=1`, target ten
uses `f=14`, `W=17`, and returns all 32 signed complex coefficients in each
mode. There are exactly 264 scalar products per pass. Smaller calibration
families cover variable depth, unequal later axes, complete carry chains,
`d=1`, exact quarter roots, zero rounded factors and width reuse.

Nine structural/ownership guards reject with the expected reason. Executed
consumer mutations detect a lost higher carry offset and omitted conjugation.
A grow/shrink comparison requires identical current transaction action
counts on fresh and previously widened owners while preserving their
different retained backing volumes. Reported action counts cover **run,
literal output read, rejected pending call and consume**, not bare-run cost.

## Independent evidence

The source reviewer uses directed integer-square-root half-angle enclosures,
without the producer's pi/Taylor machinery. It certifies 342 source rows and
342 conjugates in five families and rejects six semantic mutations. The
physical reviewer separately executes both actual-source modes and checks
the returns against one combined original exponent per tensor coordinate,
without the author's cached or rounded-chain expectation.

Its component-l1 errors are at most approximately `0.00013164` and
`0.00012679`, below the admitted `3/4096`. A disposable physical subclass
which rounds scalar products before their complex sums returns zero where
the correct completed product returns one. Both paths use the real inherited
scalar engine and complete cleanup. Independent object-graph traversal finds
exactly all 1322 declared tape roles, including inactive descendants; all are
erased at canonical origins after consumption. Borrowed bytes and heads are
preserved. These are source-aware AI checks, not human or proof-kernel approval.

## Scope and remaining obligations

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`SOURCES.json` records exact Git blobs and SHA256s; `TASK.json` preserves the
selected task card and its narrowed obligation. `PROOF.md` gives the universal
controller/cost argument, `SOURCE.md` the numerical and setup argument,
`ORACLE.md` the independent enclosure proof, and `REVIEW.md` the review scope.

The unit-disk/phase/radius properties are certified prepared-input premises;
the physical structural scan does not authenticate arbitrary replacement
coefficient pages. Payload-grid conversion, if needed by a larger caller,
must be priced there. Finite physical tests use the word engine's base branch;
its general FFT branch is an inherited pinned theorem and implementation.
The recorded all-size source proof and code review are distinct from finite
replay coverage.

## Open next questions

Open next questions are to bind both endpoint passes to a complete chirp
convolution with its actual normalization and intermediate rounding; to lower
the elementary source preparation to a literal encoded generator; and to
account for grid conversion and table lifetimes across an actual outer family.
`TASK.json` records specific first steps and blockers. No full Fourier or
Gaussian caller, CRT supplier, integer recovery, selected-assumption removal
or improvement to the complete multiplication exponent is claimed.

Contribution by @CubeJerry with substantial OpenAI Codex assistance in
research, implementation, proof and verification. A separate source-aware
AI researcher supplied the certified source preparation, and another supplied
the independent half-angle and physical checks. See `NOTICE.md` for predecessor
credit. Repository Apache-2.0 licensing applies.
