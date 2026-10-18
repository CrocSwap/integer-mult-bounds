# Selected-record preflight: reuse checked canonical paths

An **opt-in verifier prototype**, starting from canonical main
`7788b59946ebf3803dc38b6a19b47b4acb27f40b`, priority revision 5.
The complete selected source-binding check is **1.33–1.39 times faster** on
the measured host, saving about **58–81 ms per check**. This is a small
preflight improvement; no whole cold-replay or multiplication speedup is claimed.

The production checker, frozen inputs, selected record and two byte-pinned
consumer audits remain unchanged. The investigation is
[Discussion 2787](https://github.com/CrocSwap/integer-mult-bounds/discussions/2787).
Scope, overlap, source hashes, exact Git blobs and remaining obligations are in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json).

## Delta and why it preserves coverage

The retained `scripts/verify_selected_result.py` resolves each enumerated file
to check containment, then resolves all inventory paths again to build the set
of hash-covered primary-proof targets. The second pass is measurable on the
selected 1,579-file, 66,386,573-byte inventory, particularly its deep vendor paths.
An entry profile recorded 3,413 `Path.resolve` calls in one complete preflight.

[candidate.py](candidate.py) yields `(inventory_path, resolved_path)` from
`package_files` and accumulates the latter while hashing the former. The legacy
manifest remains excluded from both the inventory and proof coverage. The
modern inventory still rejects overlapping roots. The candidate's only other
changes are its location-dependent `ROOT`, documentation and attribution.

For a filesystem stable during one invocation, the reused canonical path is
exactly `(inventory_root / inventory_name).resolve()`, which the original
checker recomputes. Both manifest formats therefore give the same covered-path
set, including contained aliases. Complete inventory/hash equality still must
pass before that set can admit a primary proof. Certificate, arithmetic,
supplement, publication-pointer and optimized-CLI checks are retained.
Every invocation enumerates and hashes every source again; nothing is cached
between calls. Concurrent filesystem mutation remains outside the inherited
source-closure contract.

## Reproduce

From the repository root, using Python 3.12 or 3.14:

```sh
python3.12 -B research/selected-preflight-path-reuse/verify.py
python3.12 -B research/selected-preflight-path-reuse/benchmark.py \
  --pairs 9 --out /tmp/new-selected-preflight-benchmark.json
```

Use a fresh output path. No third-party dependencies or network access are
needed. Expected verification output is `PASS_SELECTED_PREFLIGHT_PATH_REUSE`.
These are explicit manual commands; this package does not register a generic
CI replay or replace the selected cold-replay command.

The verifier checks pinned source bytes, then runs the existing selected-result,
inventory-link and primary-proof suites against each engine: **25 inherited
groups plus four new groups per engine**, with no skipped groups permitted.
The extra groups exercise same-size source corruption with restored mtime,
same-content alias retargeting after success, an unhashed manifest selected as
primary proof, and overlapping nested roots. Both actual optimized CLIs must
also refuse execution. Both Python versions passed all 58 groups and both CLI
refusals. No independent human review is claimed.

## Measurements and limits

Nine alternating pairs per interpreter, one fresh child process per sample,
on a shared macOS 26.3.1 arm64 host with warm filesystem caches:

| Interpreter | Original median | Candidate median | Ratio |
| --- | ---: | ---: | ---: |
| CPython 3.12.14 | 289.6 ms | 208.8 ms | 1.39× |
| CPython 3.14.7 | 231.4 ms | 173.6 ms | 1.33× |

The timed region is the complete `check(record)` call. Import, interpreter
startup and benchmark source-pin overhead are excluded from this table.
The recorded full benchmark-worker process medians, including that overhead,
are 330.0 → 251.3 ms (3.12) and 278.6 → 222.5 ms (3.14). These worker processes
include the benchmark harness; they are not direct production-CLI timings.
Raw samples, interpreter/platform details and exact code/input bindings are in
[BENCHMARK-python312.json](BENCHMARK-python312.json) and
[BENCHMARK.json](BENCHMARK.json). Every sample checks the complete selected
inventory and returns the same exact kappa. Timings are measurements, never
acceptance thresholds or performance guarantees.

No complete selected construction replay, mathematical supplier admission,
other operating system, hosted CI or new kappa is claimed. Source-binding
preflight success retains the original checker’s limited meaning.

## Open next questions

Does this small repeated-preflight saving justify default adoption? First measure
its cumulative cost in the intended review workflow. If worthwhile, port the
delta while explicitly providing successor provenance for
`selected-binding-coverage-seeda342` and `selected-dependency-heads-audit`, which
pin the original checker. Their existing pins and evidence are preserved here;
production compatibility migration and their replays remain separate work.
The structured question is in [TASK.json](TASK.json).

## Credit

Douglas Colkitt wrote and integrated the original checker. Mihir Srivastava’s
PR841 supplies primary-proof provenance guards; yssite’s PR959 supplies inventory
symlink closure. Aaron Wang’s PR1864 and the selected dependency-head audit
retain their source-binding evidence. The contribution reproduces their guarded
checker as a prototype and preserves their regression suites.

Prepared by Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
