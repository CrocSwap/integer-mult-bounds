# Exact integer rows in the complete QQ16 replay

This opt-in adapter accelerates one function in the complete frozen QQ16
caller: `research/joint-query/verify_scalar.py:replay`. Every literal event
still executes on all 712 independent input columns. The original caller,
source reconstruction, scalar formulas, native frames, Gaussian columns,
ordered proofs and corruption controls remain in use. The five original
output files and stdout must be byte-identical; complete scalar maps from
all nine invocations must also agree, including the corrupted words.

The local words and original verifiers are the contribution of **Ali Romman**
in [PR1969](https://github.com/CrocSwap/integer-mult-bounds/pull/1969), exact
head `a6e6ad3936f67b8f63b5b68c5e75d540610a65e7`, integrated with the reviewed
scope recorded in `docs/research/community-efficient1000-review.md`. The new
contribution is an exact execution representation and its caller comparison.
It changes no construction, supplier, selected result, or frozen source.

## Why this representation is equivalent

Represent each sparse rational row by `(d, a)`, where `d` is a positive integer
and the represented coefficient at key `j` is `a[j]/d`. The denominator is
shared by the row rather than reconstructed for each coefficient operation.
At entry, take the least common multiple of the coefficient denominators
(one for an empty row) and multiply each numerator by the appropriate integer.
Input dictionaries are copied independently, even when the caller aliases them.

For an ADD with reduced rational coefficient `p/q`, let target and source
denominators be `d_t` and `d_s`. Set

```
D = lcm(d_t, d_s*q)
A = D/d_t
B = p*D/(d_s*q).
```

The new target numerator is `A*a_t[j] + B*a_s[j]`; dividing by `D` gives
exactly the original target plus `(p/q)` times the source. All quantities
computed in the loop are integers. The original guard requires distinct
source and target registers, so updating the private target dictionary cannot
change the source being read. SCALE multiplies numerators by `p` and the
denominator by `q`; CLEAR replaces only an allowed owned private row by
`(1,{})`. Non-scalar retained events use the original whitelist and leave
these common-chart scalar rows unchanged. Induction over the literal event
sequence proves equality of every represented coefficient, without a dyadic
assumption or a finite-field heuristic. Conversion to `Fraction` at return
reduces each exact coefficient.

The sparse dictionary convention is also preserved. SCALE keeps explicit
zero-valued keys. ADD removes a zero key only when the original source loop
visits that key; untouched keys remain. This matters for exact dictionary
equality, even though explicit zeros do not change the linear map. The adapter
accepts exact `int` or `Fraction` initial values; its production caller supplies
only Fraction basis rows. Floats, booleans and complex values are outside the
declared adapter domain and are refused. No general Python duck-typing
compatibility is claimed.

## Source boundary and coverage

`SOURCES.json` binds 29 runtime inputs by exact Git blob and SHA-256, including
all five original Python modules, the certificate, source archive and all
original proof/review evidence consumed by the caller. They are authenticated
on every invocation. Modules execute from the authenticated source bytes;
there is no imported bytecode or persistent verdict cache. Historical task
catalogue and selected-record pins stay historical provenance.

Only the scalar replay function is replaced. `replay.py:main` itself executes
unchanged with a loader that supplies the authenticated original modules and
the single function substitution. `source_data.read_git` still reads the
original archive from commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` and
checks its exact hash. The corresponding current archive is independently
pinned here; it is not substituted for the historical read.

Both arms retain:

- Nine scalar invocations: B and F, both composed orders, and the five original
  timing/private-clear corruptions. Each has all 712 initial rows. The receipt
  binds every returned row and coefficient, including all dirty helper inputs.
- Both original data inverse orders, 16 conserved selected sums, 480 restored
  borrowed helpers, eight zeroed owned private outputs and exact scalar bills.
- All 37 native cases, 16,384 exact Gaussian basis columns, original phase,
  translation, owner-action and inverse-sign controls, and the ordered actual,
  noncentral and singular examples.

Original `REPLAY.json` still identifies the original sources. A separate
`ADAPTER.json` explicitly records the selected implementation, adapter source
hash and all nine scalar-map digests, so this is not presented as an execution
of unmodified code. `verify.py` compares every byte of the five original
outputs and stdout, with no field exclusions. It additionally compares the
complete nine-call trace and checks 768 exact prefixes of 96 synthetic words,
including odd denominators, signs, zero coefficients, cancellation and aliased
initial dictionaries. Six original error guards agree in exception and message.
Changed scalar-map and original receipt controls are rejected. The separate
test mutates each of the 29 runtime files in disposable copies and requires
source-pin refusal; later unrelated provenance files do not invalidate runtime.

## Measurements

`BENCHMARK.json` records paired alternating fresh-process runs on the same
machine. Timings include the complete original caller, source authentication,
the same complete-map trace instrumentation and all original checks. They are
descriptive observations, not acceptance gates or forecasts for other hosts.
No OS cache flush or process isolation from unrelated machine load is claimed.

On native Windows 11 / CPython 3.12.7, three alternating pairs gave median
**26.82 s reference versus 20.63 s integer rows: 1.30x, or 23.1% less elapsed
time**. Individual reference runs were 25.25, 26.82 and 35.57 seconds; integer
runs were 19.72, 20.63 and 21.07 seconds. The slow third reference run is
retained, not discarded. Every pair reproduced the same five original output
files and nine complete scalar-map digests. The comparison is between the
two instrumented arms described above, not a selected-frontier timing claim.

The initial CPython 3.12.7 profile of the unchanged caller took 90.9 seconds
under cProfile. Its nine scalar replays accounted for 29.5 seconds; the scalar
module's sparse `add` routine accounted for 33.5 seconds including formula
work. These profile numbers diagnose the bottleneck and are not compared to
unprofiled timings. The separate benchmark is the before/after comparison.

## Reproduce

From a full repository checkout with the source commit available, Python 3.12
and Git, using only the standard library:

```sh
python3.12 -I -O -B research/qq16-integer-row-replay/verify.py
python3.12 -I -O -B research/qq16-integer-row-replay/test_adapter.py
python3.12 scripts/research_package.py --package research/qq16-integer-row-replay
python3.12 -I -O -B research/qq16-integer-row-replay/adapter.py --out /tmp/qq16-fast
python3.12 -I -O -B research/qq16-integer-row-replay/benchmark.py --pairs 3 --out /tmp/qq16-benchmark.json
```

Expected verification status: `PASS_QQ16_INTEGER_ROW_REPLAY`. The adapter's
default engine is `integer`; `--engine reference` keeps the original Fraction
replay. Outputs go only to the explicit output directory. Frozen inputs and
historical source files are never edited.

## Decision and limits

The assigned verifier-engineering card is refined to this measured whole-caller
bottleneck. Under revision 5's expansion gate: the input/output contract is
unchanged and source-bound; exact representation equivalence is proved above;
local caller equality and source invalidation are executable evidence; native
hosting, movement, recursive precision and the supplier invoice remain unknown
and are not charged zero. This experiment narrows verification work and does
not expand the QQ16 construction family. Stop if complete equality fails or
paired whole-caller timing gives no material benefit.

The optimization is opt-in. It does not alter the standard selected cold
replay or claim a full multiplication theorem. Denominators need not be reduced
after every event and may grow in other words; no universal runtime or memory
improvement is claimed. Runtime still requires Git and the original source
commit. No Git-free full-caller or arbitrary source-loader contract is claimed.

## Open next questions

Should a maintained successor caller adopt this representation? The first step
is an explicit maintainer decision about the frozen source contract, followed
by the same complete output and failure-control comparison. This package
supplies an opt-in boundary and measurements, not an automatic repin. No
further optimization campaign is justified by this result alone; the remaining
native, ordered and source-reconstruction stages were deliberately unchanged.

Prepared by **ywz65** with substantial **OpenAI Codex** assistance. Apache-2.0.
Retain `research/joint-query/NOTICE.md` and its source-specific notices for the
Ali Romman, gauge44/T16 and centre-encoding/cover-algebra/residual-syndrome/
coherent-port/interface proof lineage. This package claims none of those
constructions or original verification methods as new work.
