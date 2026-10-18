# Integer-pair rank for the complete Eisenstein floor replay

This optional adapter replaces the 359 exact `Q(omega)` rank calls in
[PR2017](https://github.com/CrocSwap/integer-mult-bounds/pull/2017)'s complete
Eisenstein floor verifier with denominator-cleared integer-pair elimination.
The complete verifier, full output and seven original negative controls remain
unchanged. Its 311 F4 and 209 Q rank calls still use the original functions.
No frozen source, selected record or existing verifier is edited.

On the measured CPython 3.12.7 Windows fixture, six alternating fresh-process
timing pairs after warmup gave these medians:

| Same fixture | Original | Integer K-rank | Ratio |
| --- | ---: | ---: | ---: |
| Complete replay, including imports and source authentication | 1.43271 s | 1.20969 s | 1.184x |
| All 359 actual K-rank calls | 0.485263 s | 0.057389 s | 8.456x |

[BENCHMARK.json](BENCHMARK.json) retains every observation, order, interpreter,
platform, adapter hashes and complete-output byte digest. Each timed matrix
is a frozen copy of the actual call input; the full ordered call digest must
match RESULT.json before timing. The full replay ranges were
1.14770–2.24239 s and 0.85541–1.56985 s respectively. Concurrent machine load
was uncontrolled. These are observed local timings, not a universal speed
guarantee or a multiplication speedup. Reproduction requires output equality;
it does not require any timing threshold.

The initial instrumented profile found 879 rank calls consuming about 4.535 s
of 6.141 s in `main`; Fraction arithmetic dominated. Those profiler timings
include instrumentation and are not the before/after benchmark above.

## Exactness and retained coverage

[PROOF.md](PROOF.md) proves the algorithm for every finite rectangular matrix
of rational pairs representing `a+b*omega`, with `omega^2+omega+1=0`.
Each row first clears rational denominators. Elimination multiplies by the
nonzero pivot and subtracts a multiple of its row, then removes the common
integer content. Every step is an invertible row operation over the field.
There is no numerical tolerance, modular rank inference, matrix cache or
cached mathematical success.

The primary verifier first runs the unchanged original and compares each
actual K call to the new routine, including input preservation. It then runs
the entire original again with the adapter and compares complete stdout.
[RESULT.json](RESULT.json) binds the ordered full K-call census and retained
receipt. An intentionally wrong K-rank routine is rejected by the unchanged
verifier, so output equality is not checked only against a new oracle.

[independent.py](independent.py) replaces every K entry with its two-by-two
rational multiplication block and checks that rational rank equals twice
K-rank. Separate Fraction elimination covers 9,009 matrices: exhaustive small
rectangles, rational denominators, singular and empty cases, unequal dimensions,
duplicated rows and large integer scales. Additional controls cover the
Eisenstein relation, a bad mod-two specialization, floating near-dependence,
same-object input mutation, and rejected ragged/float/bool inputs.

[integrity.py](integrity.py) runs a complete Git-free export, corrupts each
source before import, and tests a bool/int receipt mutation. Source SHA-256
and Git blobs are authenticated before code executes. A source change fails
closed; it does not silently reuse the old result. The entry domain remains
exact rational pairs, not arbitrary Python numeric objects.

## Run

For the faster complete replay, using standard-library Python 3.12:

```sh
python3.12 -I -O -B research/eisenstein-integer-rank/replay.py
```

For the complete registered verification of the adapter:

```sh
python3.12 scripts/research_package.py --package research/eisenstein-integer-rank
```

To repeat the optional timing with a fresh output filename:

```sh
python3.12 -I -O -B research/eisenstein-integer-rank/benchmark.py --output /tmp/eisenstein-benchmark.json
```

Use any writable, absent output path on Windows. `replay.py --original` runs
the authenticated original for a matched timing control. Default verification
writes nothing; the benchmark refuses to overwrite an existing file.

## Scope, sources and credit

This is a tooling result. It does not add to the C=40 proof, change a paid
profile, establish a new supplier or claim a new exponent. Integer coefficient
growth may make this method unattractive on other matrices; no general
complexity or all-replay speed claim is made. The source files are pinned at
canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` in
[SOURCES.json](SOURCES.json). [TASK.json](TASK.json) records the runtime card,
first working baseline, overlap coverage and follow-up questions.

Credit Jose Manuel (@jmbarrancoml) for PR2017's exact K/F4/Q verifier and floor
proof, and Jonathan Lam, Joel Pulikkan / GamingPuzzled for the retained
geometry. Their original source notices remain untouched. Primitive integer
elimination and restriction of scalars are standard methods. PR2537 is a
separate rational nullspace fast path; its returned-basis problem and the
recycled initializer are not changed here. New work by ywz65 with substantial
OpenAI Codex assistance in profiling, derivation, implementation, testing,
writing and review. Separate agent review is not independent human review.
Apache-2.0.

## Open next questions

1. Does this adapter help other exact Eisenstein replay fixtures? Capture their
   complete rank-call sequences and compare full receipts before proposing
   shared integration. Their sources and coverage are not certified here.
2. Can fraction-free rational elimination reduce the remaining 209 Q-call
   cost? Profile that path independently and retain exact full output; this
   package deliberately leaves its implementation unchanged.
3. When does integer coefficient growth outweigh saved Fraction operations?
   Benchmark large, high-rank rational-pair matrices with explicit height and
   dimensions before claiming a broader runtime policy.
