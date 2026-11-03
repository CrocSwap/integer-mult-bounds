# Integer Taylor evaluation reduces complete query replay time by 37.88%

This contribution was produced by Nick Petalas. Claim type: scoped
implementation-equivalence proof with exact finite conformance and a local
complete-command performance measurement. No new kappa is claimed.

The complete frozen PR4440 scientific caller takes a median 7.509418 seconds
with its original exact rational exponential and 4.665133 seconds with
integer Taylor evaluation, a 37.88% reduction. Five alternating fresh-process
pairs have separated ranges, 7.328053 to 8.100158 seconds versus 4.486905 to
4.762185 seconds. All ten processes succeed, return identical complete
scientific results and have identical exponential trace hashes.

The implementation retains all 98 exponential calls and 4,704 Taylor steps.
It computes the same fixed polynomial and geometric remainder using integer
Horner evaluation and two final Fraction constructions. Every lower and
upper endpoint is exactly equal to its original rational value. Terms,
precision, source inputs, scientific conditions, expected result and rejection
controls are unchanged. [PROOF.md](PROOF.md) derives the exact formula.

The complete scientific output hash is
`a23e6b7b885145dc969f1ae98d2f0e47c1d746bcb9097ac583ac1e731f40f880`.
The ordered exponential trace hash is
`55c4507231de5e66d7d34e57e16659c8b88e5e55e7a09a1598114f6acdc2a6b4`.
Verification additionally compares every complete input/output tuple directly;
the trace hash is a compact receipt, not the sole equivalence test.

## Measurement

The separate baseline cProfile run executes the complete original verifier.
It attributes most runtime to Fraction arithmetic and gcd reductions in the
two rational tail calculations. The integer path removes the repeated
Fraction reductions only in mixed_target_probe.exp_interval. Matrix
products, logarithms and the primary independent interval engine remain.
Profiling overhead is excluded from the timing comparison.

Raw baseline seconds are `7.647484, 7.509418, 8.100158, 7.328053, 7.389403`.
Candidate seconds are `4.486905, 4.762185, 4.758530, 4.665133, 4.499728`.
Each timer includes a fresh process, source imports and authentication,
the full scientific caller, complete receipt comparison, exact-call trace
hashing and full scientific output serialization. Parent-side JSON parsing
is outside timing. Both modes use identical instrumentation and workload.
The benchmark rejects errors and mismatched outputs or work counts. Timing
is never a CI pass threshold.

Environment: CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. Entry load
averages were 7.36, 8.93 and 5.27. Concurrent work was present, so baseline
and candidate alternate. The measured gain applies to this environment
and exact complete caller, not every workload or host.

## Reproduce

From the repository root, with the interpreter used locally:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/query-controller-integer-taylor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/query-controller-integer-taylor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/query-controller-integer-taylor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/query-controller-integer-taylor --check-source-history --check-modes
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/query-controller-integer-taylor/benchmark.py --pairs 5
```

Another CPython 3.12 executable may replace the absolute path. Standard
library only. Direct verification prints `PASS_QUERY_CONTROLLER_INTEGER_TAYLOR`;
registered replay ends with `PASS_REGISTERED_RESEARCH_PACKAGE`. The benchmark
prints a generated timing report. Redirect generated outputs outside the
checkout. Source-bound receipts are generated on stdout and hash every new
package file.

The verifier authenticates 26 declared source inputs, compares both full
caller results and all 98 exact exponential records, and retains every
existing scientific check. A separate powers/factorials oracle checks 158
rational endpoint fixtures, including large denominators and the accepted
bit-capacity boundary. Seven invalid inputs reject. Three real arithmetic
mutants exercise missing remainder, changed polynomial and a rounded-down
upper endpoint. A displayed scientific result can survive an omitted tiny
tail, so the exact endpoint comparison is a separate mandatory guard.
All checks use explicit exceptions and remain active under optimized Python.

## Source and credit

[ywz65's PR2552](https://github.com/CrocSwap/integer-mult-bounds/pull/2552),
head `35d29b05f2947545092cfe515961c3706ef2ce89`, supplies the integer Taylor
method and asks whether it helps other retained interval engines. Its ceiling
uses a variable stopping index, dyadic rounding and a different remainder.
This contribution answers that question for the separate fixed 48-step
rational engine and the entire PR4440 caller. Standard integer arithmetic
and Horner evaluation are background; no literature-priority claim is made.

Cinna Davis's [PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440)
supplies the unchanged caller, expected result and scientific conclusions.
The retained source proofs preserve zxv's native, factorization and tail
work, Jacob Alan Sussman's integer compiler, and the earlier native, BIT,
precision and outer contributors. No predecessor scientific result is
audited or claimed as new. All frozen source files and credit lines remain
unchanged. No matrix-product substitution is included.

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The selected metadata orientation passed. [TASK.json](TASK.json)
refines the replay-runtime card; [SOURCES.json](SOURCES.json) binds all live
inputs and historical provenance. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358936)
records the current scope and its correction. Live claims, local locks,
recent account work, main README/formula terms and merged PRs were searched.
The overlap cache reports complete pagination for 346 open PRs and 6,226
Discussion records at its recorded timestamps. Those searches do not cover
unpublished work or arbitrary historical diffs.

## Limitations

The exact kernel accepts int/Fraction inputs in 0<=x<1, with numerator and
denominator bit lengths at most 16,384. Floats, booleans, larger inputs and
other exponential remainder contracts are outside its implementation domain.
Module substitution is local to a separate process, not a shared thread-safe
library. No original engine or source pin is edited. Wider adoption needs its
own applicability, dependency and complete-caller measurements.

The historical PR4440 replay is the behavior-preservation workload. Its
scientific review status is inherited. The result admits no supplier,
changes no selected frontier and discharges none of the five framework
assumptions. No selected cold replay, native all-width proof, rounded
multiplier, physical execution, Lean or Docker run is supplied. Independent
human and formal proof-kernel review are unclaimed.

The new kernel has no recursion or cache and exactly 48 bounded iterations.
Each function fits within 60 physical lines. Input bit limits and a 128-call
adapter cap bound mathematical storage and trace length. Python dynamically
allocates integers and Fraction objects, a fixed-allocation deviation with
those finite capacities as compensating controls. Fixed-path source module
loading and the one invocation-local replacement are explicit. Warning-strict
normal and optimized runs supply interpreter diagnostics; no external static
analyzer or fixed-heap guarantee is claimed.

## Open next questions

Can a source-specific integer evaluation help another exact moment engine
with a different polynomial or remainder? First pin one engine, derive its
exact endpoint formula and time the unchanged complete caller. Neither
endpoint equivalence nor a speed result for that other engine is supplied.
No further optimization or production migration is reserved here.

New work is Apache-2.0.
