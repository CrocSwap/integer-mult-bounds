# Exact rational containment without constructing joined bases

**Verification tooling; No new κ.** This optional adapter speeds up the complete
historical mixed-point frame audits at h=10 and h=12. It changes only the
`contained(U,V)` predicate in the running process. The original circuits, row
reduction, Gram checks, orthogonal complements, selected frames, forward/reverse
nesting and endpoint checks all run unchanged.

Five alternating fresh-process pairs on Linux x86_64 / CPython 3.12.14 gave median
total wall time **2.798839 → 2.520628 seconds** (1.110×, 9.94% less time) and median
peak RSS **89,128 → 73,748 KiB** (17.26% less). All ten complete mathematical
payloads match byte-for-byte after canonical JSON encoding. These are local
measurements on this historical audit, not a hardware-independent guarantee,
selected-supplier speedup or integer-multiplication speedup. A separate one-pair
validation measured 1.033×; timings vary and never determine correctness.

## Reproduce

From a full repository checkout on Linux or macOS, Python 3.12 and its standard
library (the inherited benchmark uses the POSIX `resource` module):

```sh
python3 -B scripts/research_package.py --package research/rational-containment-performance
```

Expected final messages include:

```text
PASS_RATIONAL_CONTAINMENT calls=42860 kernel_mutants=4 source_mutants=6 frame_mutants=2 adapter_controls=2
PASS_REGISTERED_RESEARCH_PACKAGE research/rational-containment-performance outcome=completed
```

The command checks metadata and Git/SHA256 source pins, runs independent kernel
tests normally and under `-O`, rejects four faulty arithmetic kernels, compares
three complete audit executions, checks source/frame/adapter failure controls,
and measures one alternating-benchmark pair. Allow about 25 seconds on this host;
there is no timing threshold. No network is needed. Full Git history is needed
for the generic hook's historical provenance checks.

For persistent replay evidence, use a new output directory:

```sh
python3 -I -B research/rational-containment-performance/verify.py --output /tmp/containment-review
```

To repeat the five-pair measurement (fresh output file required):

```sh
python3 -I -B research/rational-containment-performance/benchmark.py --pairs 5 --output /tmp/containment-benchmark.json
```

`adapter.py --engine reference|annihilator|compare --output /tmp/new.json`
executes the unchanged predecessor benchmark via `runpy`. Comparison mode checks
each live inclusion query with both implementations. The adapter refuses changed
source bytes, existing output paths and optimized Python, because inherited
checker assertions must remain enabled. Kernel guards work under `-O`.

## Exact identity and compatibility

The reference computes `basis(sorted(set(U+V))) == V`. Its basis convention is
integer primitive reduced rows with positive, increasing leading pivots and zero
entries in every other row's pivot column. The canonical representative of a
rational row space is unique: scale each row of its rational RREF to the unique
primitive integer row with positive pivot. Thus a noncanonical V cannot equal the
reference's output, even when it spans the same space. The adapter preserves
that **False** result; it does not silently broaden the reference predicate.

For canonical V, let its rows be v_i, pivot columns p_i and positive pivots c_i.
Put L = lcm(c_i). A row u belongs to span_Q(V) exactly when, for every nonpivot
column j,

```text
L*u[j] - sum_i u[p_i] * (L/c_i) * v_i[j] = 0.
```

Indeed the only possible coefficients of u in these rows are u[p_i]/c_i.
The resulting combination already agrees at every pivot; the displayed equations
check every remaining coordinate. Dividing each equation by its positive integer
GCD preserves its zeros. This proves the replacement identity over Q, including
non-unit pivots. No modular or floating-point acceptance is used.

`kernel.py` validates rectangular tuples of built-in integer rows before any cache
lookup. It then checks the canonical convention, builds these sparse annihilator
equations and tests every source row. Source rows may be dependent or zero.
Empty targets accept exactly zero source rows; a full canonical target has no
nonpivot equations. Width zero and empty presentations are covered. The kernel
is coordinate algebra and does not assume the ambient `9I-J` form is definite.

The per-instance LRU stores at most 8,192 immutable target/equation entries,
keyed by the full target value. Input validation precedes lookup, including on
hits, so equal-valued floats or booleans cannot borrow an integer cache entry.
No whole-audit verdict or external receipt is cached. Eviction only recomputes
exact equations. Matrix size is not bounded by the entry-count limit. The process
adapter is intended for sequential use, not concurrent monkey-patching.

Malformed/noninteger inputs now raise explicit errors within the adapter's
kernel. Equivalence is claimed for rectangular integer matrices of common width,
the domain generated by the pinned historical checker, not arbitrary Python
objects or ragged arrays.

## Evidence and completed coverage

[BENCHMARK.json](BENCHMARK.json) retains every one of the five alternating pairs,
wall and child CPU times, peak RSS, interpreter/platform, code hashes and the
complete mathematical payload. Each arm starts a new interpreter and empty
application caches. Both arms receive the same source pins and run the same
h=10/h=12 benchmark; filesystem caches were not flushed. No CPU affinity was
set, no samples were dropped and no timing threshold was applied.

[VALIDATION.json](VALIDATION.json) records the complete verification result:

- All **42,860** inclusion calls and **7,614** distinct targets agree exactly.
- The full audit payload SHA256 is
  `faa0f9c0159a6e70d4e2cfcdb4012ea62ef350bd26b81312d11da4a770f8b218`.
  The ordered source/target/answer transcript SHA256 is
  `26d55e53c7e9f7ae83b3f3d3c4e9c91735e57f11a1f0db54bb02e895bc867157`.
- Eight kernel test methods pass normally and under optimized Python. They cover
  all **5,460** coordinate-subspace pairs through dimension six, all **4,096**
  pairs of binary 2×3 presentations, **288** seed-88 signed cases through dimension
  twelve, non-unit/127-bit pivots, noncanonical/empty/dependent presentations,
  cache eviction and invalid input after cache hits. The general oracle uses
  independently written Fraction elimination and does not import the predecessor.
- Four arithmetic mutations produce test failures, not execution errors: dropped
  equations, reversed signs, omitted pivot denominators and accepted noncanonical
  targets. All six live-source mutations reject.
- Actual compiled-frame controls reject a decreasing side frame and invalid output
  injection with the same error in both engines. Existing-output and `-O` adapter
  controls also reject.

The full historical `make verify`, selected `make frontier1094-verify`, Lean/native
builds and remote CI were not run. No selected construction or frozen source file
is modified. Finite tests corroborate the algebra and implementation; they are
not a formal proof of the multiplication theorem. All inherited compiler,
realization, hosting, precision/tape, analytic and bit-interface assumptions remain.

## Assignment, provenance and overlap

Exact base: `410026dc5513b87db92ae98571d1d5984c69a983` (fetched upstream main).
At that base, the selected conditional result is PR1094,
κ = **0.001672660197076918**, audited source head
`0fc329d0bec93ca7cd288eaea1295172e8789810`, with the PR589/PR555 bit supplier.
The selected record, actual PR1094 construction and batch1099 review were read;
no pending title was used as the accepted bound.

The first OS-random draw was **88**, assigning verification engineering. The
local claim in [TASK.json](TASK.json) records three candidates and the bounded
choice (88 mod 3 = 1), method, time budget and finish deadline. The `replay-runtime`
card is refined to one historical audit. The first profile measured 42,860
inclusion calls, motivating this specific replacement. This does not reopen the
mixed-point construction's negative result or attempt a stronger bound.

The six live inputs and their base Git blobs/SHA256 are pinned in
[SOURCES.json](SOURCES.json); [VERIFY.json](VERIFY.json) registers precisely their
CI invalidation scope. The selected record/catalogue are historical provenance,
not moving runtime inputs. No external libraries are required.

Nearest work:

- Richard Hoekstra's [PR239](https://github.com/CrocSwap/integer-mult-bounds/pull/239),
  head `fd687eecd781631bc38ae8b03a83d00c13f05aa7`, supplied the incorporated
  dual-Gram optimization, independent tests and complete customer benchmark used
  unchanged here. The source/target cut construction is Douglas Colkitt's work.
- Richard Hoekstra's pending
  [PR1234](https://github.com/CrocSwap/integer-mult-bounds/pull/1234), head
  `8812ca21c43f5cea16276c7fa539fa8d1559b0f1`, changes normalization and complements
  on the same customer. This package instead changes the inclusion predicate,
  and does not import that patch or claim a combined speedup.
- Aman's [PR367](https://github.com/CrocSwap/integer-mult-bounds/pull/367), head
  `522285db971642c2d744cc8d45f2a5ade3a55e19`, accelerates rank and canonical-basis
  calculation for a different PR364 workload. No code is imported from it.

Live public PR search pages, the discussion list/start-here/handoff posts, the
review ledger and local negative-result note were checked. The repository overlap
helper also ran offline; it reported no usable remote cache. This is scoped
coverage, not an exhaustive novelty certificate. No pinned sprint issue was
visible. Under the donor's API-unavailable workflow, the claim/result are retained
locally; no reservation issue or upstream PR is created.

The final refresh confirmed main remained at the stated base and PR1234 remained
at its pinned head. Its actual Git diff changes only `primitive` and `orthogonal`,
corroborating the distinct inclusion scope. Focused fresh PR/discussion searches
found no additional same-predicate task; this remains limited search coverage.
The local claim has one result update and the fork branch link in TASK.json.

## Open next questions

The smallest useful follow-up is to pin a reviewed PR1234 implementation and
repeat the same exact decision transcript and paired benchmarks with both changes.
This could establish whether the savings compose; it needs separate source pins
and cannot be inferred from the present measurements. See the structured next
question in [TASK.json](TASK.json). Direct activation in the historical verifier
also requires maintainer review and any affected provenance updates.

## Credit and license

Prepared for **@CubeJerry with substantial OpenAI Codex assistance** in analysis,
implementation, experiments, verification and packaging. No independent human
review is claimed. Douglas Colkitt's historical construction and frame semantics,
Richard Hoekstra's PR239 and concurrent PR1234, and Aman's separate PR367 remain
credited above. All predecessor files are retained unchanged. New material is
Apache-2.0 under the repository's LICENSE; existing source-specific notices remain.
