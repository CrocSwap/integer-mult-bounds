# One-basis closure for the historical PR886 bit-frame audit

**Verification tooling; no new kappa.** This opt-in adapter accelerates Seth
Burkart's incorporated PR886 checker on its exact PR589 and PR555 words and
degraded PR589 positive control. It preserves every complete receipt, every
closure result, every enumerated assignment and the exact moment comparisons.
No source, default verifier, selected record or `upstream/` file is changed.

The old closure routine computes a fresh modular rank for each candidate line.
The replacement builds one echelon basis per input mask and reduces remaining
lines against it. The original sufficient Hadamard guard still justifies
rational rank; the implementation also enforces that guard without assertions.
See [PROOF.md](PROOF.md) for the equivalence argument and its precise domain.

## Reproduce

From a full repository checkout, using standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/bit-frame-closure-basis
```

Expected: nine test groups pass, `PASS_BIT_FRAME_CLOSURE_BASIS` reports the
three rows below with `no_new_kappa: true`, and the registered runner prints
`PASS_REGISTERED_RESEARCH_PACKAGE research/bit-frame-closure-basis outcome=completed`.

| Complete case | Closure entries compared | Assignments | Non-nesting rejected | Improving components |
| --- | ---: | ---: | ---: | ---: |
| PR589 tuned word | 2,202 | 398 | 55 | 0 |
| PR555 base word | 2,073 | 360 | 42 | 0 |
| Degraded PR589 control | 2,202 | 398 | 55 | 37 |

The 6,477 closure entries are compared directly between the reference and
candidate, including their input masks, closed masks and ranks. They are a
sum across three cases, not a claim of 6,477 distinct mathematical masks.
`EXPECTED.json` was generated using only the unchanged reference. Both engines
must match its complete reports and original stdout digests. The degraded
control must recover the exact tuned profile.

A single opt-in execution is:

```sh
python3 -I -B research/bit-frame-closure-basis/run.py --case pr589 --engine basis
```

Use `--engine reference` for the frozen checker. The wrapper prints its entire
original receipt plus closure inventory hashes. `--closure-output /tmp/fresh.json`
also exports every closure; the destination must be fresh and outside the repo.
The wrapper rejects `-O`; the verifier launches assertion-enabled isolated
children even if its parent inherited `PYTHONOPTIMIZE`.

## Performance experiment

The orientation profile found 179,707 rank calls consuming 9.55 of 11.99
instrumented seconds on the tuned word. Those profiler numbers motivated the
change; they are not the benchmark speedup. The first uninstrumented complete
comparison measured 10.05 s to 1.85 s and matched all 2,202 closures. Repeated
measurements give median complete-suite time **32.61348 s to 5.90754 s
(5.52066x)** on macOS arm64 / CPython 3.12.12, over five alternating pairs.
Every raw sample and the implementation hashes are retained in `BENCHMARK.json`.
The verifier checks those bindings and the timing summary arithmetic without
requiring a speed threshold. See `VALIDATION.md` for the executed checks.

Repeat the alternating benchmark with a fresh external output path:

```sh
python3.12 -I -B research/bit-frame-closure-basis/benchmark.py --pairs 5 \
  --output /tmp/bit-frame-closure-benchmark.json
```

Each engine runs all three complete cases in fresh interpreters, with source
admission, the full enumeration, exact arithmetic, output serialization and
receipt comparison. Pair order alternates. OS caches are not flushed; timings
are local descriptive measurements on a shared host, not a performance gate.
No selected-frontier replay or multiplication-runtime speedup follows.

## Independent checks and failure controls

The separate Fraction Gauss-Jordan oracle checks 1,100 cases: all 512 masks of
a nine-row synthetic table, all 16 masks under all 24 permutations of a
four-row nonunit-pivot table, and 111 E8 singletons plus 93 seeded E8 masks of
sizes zero through ten. These are bounded implementation checks, not an
exhaustive enumeration of all subsets of 111 lines. Seed 93 fixes the extra
masks; the actual reference closure inventory is checked in full separately.

Failure controls catch false membership, lost pivots, a rational/modular alias
outside the Hadamard domain, malformed coordinates and masks, stale cross-word
state, corruption of each of the five consumed inputs, missing or duplicate
pins, missing or duplicate adaptation anchors, and disabled inherited
assertions. The mathematical negative controls exercise the kernel beyond
source-hash rejection. Normal and optimized-parent execution are distinguished
in `VALIDATION.md`.

## Scope, provenance and credit

Base: `2de86c77b4127d2f01f504e0c7c5e4db737caa3c`. The selected record at that
base is PR1094's conditional `836330098538459/500000000000000000`; this package
does not change or re-prove it. `SOURCES.json` pins exact input Git blobs and
SHA256 bytes, with historical selected-record/catalogue provenance. `TASK.json`
records the assignment, three considered tasks, local claim, stopping rule and
overlap coverage. No pinned sprint coordination issue existed.

Seth Burkart (`SethBurkart123`) supplied PR886, source head
`881f72ec596a5c6d7aba801153792292ecc39737`, with disclosed Claude Code assistance.
This package uses the **integrated refinement**, whose exact interval comparisons
and Hadamard guard were added in maintainer commit
`3b83e4f14825ce1ae038a8c8159f130646991086`, rather than the submitted floating-point
decision logic. Credit Douglas Colkitt for that review and arithmetic integration.
DreamingOfClouds supplied PR589's word and tuner on eumemic's PR555 and the
PR543/545/510 lineage. All predecessor files and notices remain in place.

CubeJerry's pending PR1459/1461 use related basis/annihilator ideas for rational
frame containment in different historical checkers. Sagar Thakrar's PR1433
batches a different Boolean omission replay. Those are related verification
work, not dependencies or priority claims for basic elimination reuse.
PR933/1345 investigate distinct gate-reordering classes; this work neither
reopens those searches nor changes PR886's fixed-word conclusion.

Only the historical frame audit is accelerated. Native supplier admission,
physical hosting, a selected cold replay, all-size compiler/realization,
precision/tape, analytic transfer and a full Lean multiplication theorem are
outside this package. Hosted CI is reported separately from local checks.

New material: Ross Richardson with substantial OpenAI Codex assistance in
implementation, proof explanation, tests and validation. Apache-2.0; no
subagents were used.

## Open next questions

Profile one pinned PR933 or PR1345 transport checker to see whether closure is
also a material cost there. Its mutable-state and rank contracts must be
checked before reuse. This package supplies no speed or correctness claim for
those checkers; `TASK.json` records that first step and its blockers.

After production promotion of `frameopt.close` (`research/bit-frame-closure-production/`), the historical pairwise `frameopt.py` digest remains pinned as **provenance** only. Live CI inputs no longer include that path; the adapter still loads the working-tree checker and replaces `close` for the basis engine.
