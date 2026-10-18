# Exact interval reuse for selected-word lever planning

The unchanged seven-lever planner spends most of its time recomputing exact
child-cost intervals. This opt-in process-local session reuses those immutable
rational intervals while executing every model check, relaxation sum and ceiling
bisection again. Both initial and repeated execution produce the **same complete
ordered rational trace and original stdout** as the uncached engine.

On the recorded CPython3.12 run, three interleaved repetitions have medians
**2.494202263 s uncached** and **0.035259292 s warm**, a **70.74x** ratio.
The first fill is only **1.135x** faster. These are measurements of the specified
planning fixture, including source/context checks, trace construction,
serialization, hashing and full comparison. Process startup, module construction,
the untimed reference and separate failure controls are outside that timed
boundary. This is not a speed claim for the selected full cold replay.

No production entry point or predecessor file is changed. The planning model
and its favorable-relaxation limitations remain those of
[complex-local-word-ceiling](../complex-local-word-ceiling/README.md), prepared
by Douglas Colkitt with Claude assistance. No new saving or exponent is claimed.

## Reused value and retained execution

The engine returns an interval for `(r/m)^(1-a)` from exact Fraction logarithm
and exponential bounds. Only `child_cost(r,m,a)` is memoized, and only when
r and m are exact Python integers and a is exactly `Fraction`. Its precision,
r, m, and reduced rational numerator/denominator form the entry key.
Numeric equality does not conflate a float with a Fraction. Supported traced
forms that are ineligible for memoization, including floating-point exponents
and keyword calls, execute the original operation. Diagnostic trace values
are limited to built-in scalars/containers and exact Fraction objects.

| One unchanged seven-lever fixture | Uncached | Initial fill | Warm |
|---|---:|---:|---:|
| `ceiling` calls | 7 | 7 | 7 |
| `model` checks | 263 | 263 | 263 |
| `relax` evaluations | 263 | 263 | 263 |
| `child_cost` requests | 1,238 | 1,238 | 1,238 |
| Child intervals computed | 1,238 | 1,084 | 0 |
| Reused intervals | 0 | 154 | 1,238 |

The original engine already memoizes logarithms. Both reference and optimized
sessions retain that behavior; the comparison does not remove the reference's
existing reuse. Every warm fixture still reads the profile, computes paid and
idle mass, checks the halving/rank/count constraints, and follows every original
bisection point. Changed local counts are not a cache key because profiles are
not cached: their arithmetic and search execute afresh using applicable child
intervals. The cache is a bounded LRU, at most8,192 pairs per session; this
fixture retains1,084 pairs.

`session.py` creates a private module from the authenticated engine bytes and
executes the unchanged `levers.py` against it. Every model, child, relaxation
and ceiling event records all arguments, keyword arguments, return fields and
types, in execution order. The baseline trace has1,771 events and906,846
canonical bytes. Timed runs compare the full canonical trace and stdout before
stopping the timer; the receipt retains its hash, counts and exact ceiling
results. No rounded decimal, partial field list or speed threshold determines
mathematical equality.

## Dependency and trust boundary

A session checks both source files by SHA256 before loading. It checks them
again at each public operation and fixture boundary, and before each ceiling
inside the fixture. It also checks the current Fraction source file, Python
runtime identity, precision value/type and every loaded callable binding.
The cache belongs exclusively to that authenticated module and precision
context. A changed source or context **clears the cache and rejects** the
operation. Restoring the original context requires fresh interval computation;
a new intended source version requires a new explicitly authenticated session.

The source comparison uses bytes, not path, file length or modification time.
The tests change both engine and fixture bytes while preserving length and
mtime. Precision and exponential-function replacement are also rejected before
a warm value can be returned. New rank, modulus and exact exponent values miss
the cache; evicted values are recomputed by the original engine.

This is serial, process-local reuse in a trusted interpreter. No persisted
cache, external cache entries or past successful proof receipt is accepted.
The private module/cache must not be modified behind the public API. The code
protects normal dependency/configuration drift, not hostile code running inside
the same Python process. The fixture restores its temporary `ceiling` import
alias and `sys.path`, including a preexisting `None` import sentinel.

## Evidence and reproduce

From the repository root, standard-library Python3.12:

```sh
python3.12 -B scripts/research_package.py --package research/exact-child-interval-reuse
```

This runs a fresh uncached/fill/warm comparison, twelve controls, historical
benchmark binding checks and five entry-point test groups. The default command
is read-only. To measure this machine and interpreter anew:

```sh
python3.12 -I -O -B research/exact-child-interval-reuse/benchmark.py \
  --out /tmp/new-exact-interval-benchmark.json
```

The output path must not exist. The benchmark runs an untimed independent
uncached reference, fresh uncached and fill fixtures, then three interleaved
uncached/warm pairs. Every timed run compares the full proof-relevant trace.
`BENCHMARK.json` is historical measurement data, not a promise of performance
elsewhere. `check_benchmark.py` validates its driver/adapter/source bindings,
complete per-run evidence and timing arithmetic; it does not remeasure time.

`RESULT.json` records deterministic exact evidence separately from timings.
`verify.py --emit-result NEW_PATH` explicitly regenerates it without overwriting
existing evidence. The original profiling run found1,238 child calls and2.771
of2.850 instrumented seconds in `exp`; those cProfile numbers are diagnostic
and are not the speed comparison above.

Twelve controls/boundaries cover rank/modulus/exponent changes, eviction,
float/Fraction aliasing, uncached keyword forms, a changed local profile,
invalid halving cap, excess mass, negative count, same-size/same-mtime source
changes, precision changes, function replacement and import-state restoration.
Five entry-point groups reject altered exact receipts, missing timed coverage,
changed source bytes, malformed JSON and attempts to overwrite evidence.

The registered CPython3.12 replay and measurement passed locally. A Git-free read-only15-file execution export reproduced the complete exact
receipt under Python3.14 and passed all controls unchanged. Its separate
benchmark measured2.501852956s uncached versus0.032662474s warm (76.60x),
with1.148x first-fill speed. Both full timing receipts are retained in
`BENCHMARK.json` and `BENCHMARK-PY314.json`; `VALIDATION.json` records the
export and environment. Hosted CI is
separate; the existing manifest-aware package workflow selects both declared
source dependencies. No whole selected replay, native compiler or proof
assistant is run by this package.

Source commits/blobs/digests are in `SOURCES.json`; task and overlap history are
in `TASK.json`. New code and documentation are by Gareth Davidson with substantial
OpenAI Codex assistance, Apache-2.0. No independent human review is claimed.

## Open next questions

- How much reuse occurs in a real stream of different candidate profiles?
  Measure a source-pinned candidate sequence with the same full-trace comparison,
  including miss rates, bounded-cache evictions and first-fill cost. Repeating
  these seven levers does not establish that workload's speedup.
- Should this opt-in session be integrated into a production planner? First
  review the serial API, dependency checks and memory budget against a concrete
  caller. Integration and broader runtime claims are not part of this package.
