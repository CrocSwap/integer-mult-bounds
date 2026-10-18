# Exact compiled reader tables for the PR845 replay

**Verification tooling; no new mathematics or κ.** The opt-in compiled-table
engine runs Mihir Srivastava's complete P112 single-lift verifier about **1.40×
faster** in five alternating fresh-process pairs on macOS arm64 / CPython
3.12.13. Both engines reproduce every field of its committed certificate:
511 support certificates, 3,272 sign cases, 128 conflicting kernels and all
nine inherited controls. The original package is unchanged.

## What changes

PR845's `constraint_rows` repeatedly evaluates the same reader bases against
the same live labels. `ConstraintMemo` in [verify.py](verify.py) computes the
eight-by-112 table with the **original exact evaluator**, then builds every
original ordered constraint row. An instrumented complete replay counts
979,776 targeted evaluations in the reference and 896 in the candidate.

The cache key contains all ordered basis entries and all labels. Each call
snapshots their current values; it caches neither coefficients nor X. The LRU
holds at most four tables of 896 integers. Only the fixed-size built-in integer
list/tuple domain uses this path. Other inputs retain the original builder,
including its failure behavior. There is no cross-process cache or persisted
reuse receipt.

Every other predecessor check runs unchanged. Acceptance compares the whole
certificate using canonical, type-sensitive JSON, including ordered row hashes,
original-row support minors, exact kernels, conflict ports and control outputs.
Rank or histogram agreement alone is insufficient. Live inputs are admitted
by exact SHA256 before import; an omitted source pin fails.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-reader-memo-seed92
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/p112-reader-memo-seed92 outcome=completed`.
The registered replay compares both full engines, runs five focused test groups
under optimization, and invokes PR845's unchanged independent checker.

For a single faster, source-bound complete replay, create a fresh output:

```sh
reader_work=$(mktemp -d)
python3.12 -I -B research/p112-reader-memo-seed92/verify.py \
  --engine memo --output "$reader_work/REPLAY.json"
```

Expected: `PASS_P112_READER_MEMO_ENGINE engine=memo`. The output contains the
entire predecessor certificate and cache statistics. Existing files are never
overwritten. The default engine is `compare`, which deliberately runs both
full replays and therefore takes longer than either single engine.

To repeat the paired benchmark:

```sh
reader_work=$(mktemp -d)
python3.12 -I -B research/p112-reader-memo-seed92/verify.py \
  --pairs 5 --report "$reader_work/BENCHMARK.json"
```

Expected: `PASS_P112_READER_MEMO` with `supports=511 signs=3272
conflicting_kernels=128 inherited_controls=9 controls=13 pairs=5`, and complete
certificate digest
`d1140c3af508b420ab63b1de5fb29af9ed47631492ab1eb7d5b19b06a7d83646`.
Timing ratios are reported and never used as a mathematical pass threshold.

## Evidence and limits

[BENCHMARK.json](BENCHMARK.json) records all five pairs and their environment.
Median complete worker-process time is **1.965451 s → 1.402593 s** (1.4013×).
This includes source admission, imports, the complete verifier, full-certificate
comparison and output writing. It excludes the parent driver's controls and
comparison of child outputs. Median time inside the unchanged `run()` boundary
is **1.911796 s → 1.347156 s** (1.4191×). These are local workload measurements,
not a hardware-independent, selected cold-replay or multiplication speed claim.

Thirteen additional controls cover ordered and mutated bases, mutated labels,
uncached X/coefficients, integer-equal float failures, eviction/recomputation,
erased reader values, omitted/reordered constraints, a type-altered rank receipt,
and a missing source pin. Five tests additionally cover every proof section,
lazy/fallback inputs, source drift, duplicate pins/JSON, actual optimized
workers, read-only relocation in a path with spaces and preserving output after
failure. PR845's separate integer-minor/set-elimination checker also passes;
that implementation and its independent-method credit belong to its predecessor.

This contributes finite replay equivalence and tooling. It does not prove the
all-real-parameter theorem anew, admit a physical supplier or audit the full
multiplication theorem. Selected cold replay, native/Lean builds and hosted CI
are not claimed. All-size/compiler, realization, hosting, precision/tape,
analytic transfer and bit H1–H5 obligations remain separate.

## Sources, assignment and attribution

Exact research base: **`9ef085e6c07c8590329ad00b7eac382aef06124c`**.
[SOURCES.json](SOURCES.json) pins all eight live inputs with Git blob IDs and
SHA256, plus historical provenance. The reviewed PR845 head is
`125ce25bdae421627b56077adc14940c2d0aa52f`. The selected record at this base is
PR1094, conditional κ = `836330098538459/500000000000000000`, reviewed in
`docs/research/community-batch1099-review.md`; its complete command is
`make frontier1094-verify`. That selected replay was not run for this isolated
tooling contribution.

OS seed **92**, verification engineering, selected this object after screening
three narrow candidates. [TASK.json](TASK.json) and [CLAIM.md](CLAIM.md) record
the selection, bounds and [sprint claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18915419).
The final overlap coverage and limitations are recorded in TASK.json.
#1144 accelerates a different P112 free-sink determinant checker; #1584 the
finite-bit edge scorer; #1452/#1595 source-pin reads. The active cold phase
replay claim concerns different inputs and kernels. No pending code is imported.

Credit **Mihir Srivastava / @mihir-s-05 (PR845)** for the theorem, geometry,
certificate and both original checkers; **DreamingOfClouds (PR717/PR446)** for
geometry and the inherited physical interpretation; **Joel Pulikkan /
GamingPuzzled (PR620)** for the coordinate cost 64 and retained lineage.
Prepared for **Charan (@theon199)** with substantial **OpenAI Codex assistance**
in profiling, implementation, verification and writing. No subagents or
independent human review. New material is Apache-2.0; predecessor sources and
notices, `upstream/` and the selected frontier remain unchanged.

## Open next questions

Maintainers can review whether to adopt this table preparation in PR845's
frozen package. Start with the registered replay and paired benchmark, then
migrate source pins deliberately if approved. That review and pin migration
block adoption; this package remains opt-in. No additional mathematical search
is justified by the verifier speedup.
