# One-pass historical replay snapshots

Historical replay setup now reads each tracked source once, writes those bytes
to an independent file, and hashes the same bytes. It removes the destination
read previously performed immediately after `shutil.copyfile`. The complete
tracked inventory, authenticated historical replacements and final
`verify_unchanged` destination check remain in place.

This is verifier engineering under revision 5's `replay-runtime` card. It changes
no mathematical predicate, source pin, frozen archive or selected frontier.
The scoped claim and status are in [Discussion #2732](https://github.com/CrocSwap/integer-mult-bounds/discussions/2732).

## Measurement

[BENCHMARK.json](BENCHMARK.json) records three alternating baseline/candidate
pairs on macOS 27.0.1 arm64 and CPython 3.12.15. The baseline is exactly
`scripts/replay_historical_check.py` from main
`bcdf338bf10ed70f1b3a0325fdd429677920d089`, authenticated against
[SOURCES.json](SOURCES.json) before import. The candidate hash is in the receipt.

| Setup implementation | Three runs, seconds | Median, seconds |
| --- | --- | --- |
| Baseline | 7.444, 7.625, 7.759 | 7.625 |
| One pass | 6.236, 5.388, 5.391 | 5.391 |

The measured median speedup is **1.41 times**, or about **29% less setup time**.
This is a warm filesystem measurement on one host. It does not measure the
mathematical tests, the full CI job, multiplication runtime or kappa.

Each run uses the same 45,160-file path list from the baseline commit and the
same working source bytes. At measurement, the two changed paths in that list
were the runner and its test module; the new package files are outside that
baseline inventory. The source totals 2,274,831,662 bytes. Every returned
path/digest map agrees exactly across all six runs. Every destination is then
read and hashed by the unchanged `verify_unchanged` outside the timed setup.
The receipt binds the complete expected map with `snapshot_sha256`.

The retained [profile](PROFILE.txt), on CPython 3.12.15, measured 9.307 seconds
in setup, with 5.285 seconds in 45,160 `shutil.copyfile` calls. An earlier
exploratory profile on CPython 3.9.6 identified the same bottleneck. The reported
speedup uses unprofiled Python 3.12 runs in alternating order.

## Reproduce and verify

From the repository root, using Python 3.12:

```sh
python3.12 -B -W error research/historical-snapshot-one-pass/benchmark.py --pairs 3 --out /tmp/historical-copy-benchmark.json
python3.12 -B -W error -m unittest discover -s tests -p test_historical_check.py -v
python3.12 -B -W error scripts/replay_historical_check.py r420
python3.12 scripts/research_package.py --package research/historical-snapshot-one-pass
```

The benchmark refuses to overwrite an existing receipt. It accepts one to five
pairs and requires the baseline Git history. Each snapshot is a fresh temporary
directory removed before the next run. The benchmark imports the authenticated
baseline without changing its code and passes the same root, configuration,
input directory and path list to both implementations. It does not copy a
cached successful result or exclude any baseline tracked file.

The registered replay runs the 16 historical-overlay tests with warnings treated
as errors. Three new tests cover empty, binary and multi-megabyte files;
independent source/destination edits; a short write; and a write error. Existing
tests retain changed/missing source pins, corrupt historical inputs, duplicate
replacements, untracked inputs, path/symlink rejection, multiple overlays and
post-replay artifact mutation.

The R420 historical replay passes through the full CLI, including its four
tests and final destination check. Five isolated-runner caller tests also pass,
as do the 16 overlay tests on Python 3.14.8. Independent read-only review found
no correctness blocker after source inspection, pin checks and 21 focused tests.
It did not repeat the complete benchmark or mathematical replay.

Two other real CLI probes reject inherited source changes already present at
the baseline. `skip-clones-tests` rejects `scripts/partial_swap/shared.py` and
`reconciliation92` rejects `scripts/run_parallel.py`. The untouched baseline
runner also reproduces the skip-clones failure. For both rejected inputs, their
working bytes equal the baseline Git bytes and differ from the historical pin.
[VALIDATION.json](VALIDATION.json) records the exact expected and actual hashes.
These commands are not counted as passes. Their historical pins and rejection
gates are preserved; repairing those overlays is a separate task.

## Resource and compatibility scope

The production change adds no loop or cache. The existing tracked-file loop
still visits each path once. `data` is released after each hash, before the next
file read. As before, hashing uses one whole-file byte buffer. The largest file
in this measured fixture is 67,620,716 bytes. A short write raises `ValueError`;
ordinary read/write errors propagate and the caller's temporary-directory
context cleans up. Historical replacement authentication is unchanged.
Touched Python files also pass the configured Ruff checks. Import order,
unused fixture bindings and context-manager layout were cleaned up locally;
the runner and benchmark have executable modes matching their shebangs.

Power of Ten rule 3 requires a managed-runtime deviation. CPython and pathlib
allocate file buffers dynamically; a preallocated no-allocation steady state is
outside this tool's existing contract. The scope is this finite repository
snapshot. One-file buffer lifetime and the fixed path list constrain live data,
and the complete destination checks and large-file test exercise the copy.
Follow up with bounded streaming if repository source files outgrow this model.
The benchmark's ordinary importlib loading, under rule 8, is confined to the
SHA256-authenticated historical runner and the explicit live candidate. It
avoids rewriting or duplicating the predecessor implementation.

No Linux or Windows speedup, full selected cold replay, new supplier or theorem
verification is claimed. The input fixture must stay stable during comparison,
as with the existing snapshot tool. Platform-specific `copyfile` fast paths may
give different results. All-size/compiler, hosting, precision and analytic
assumptions are unaffected.

## Scope and credit

Dennis supplied the historical overlay runner and its authentication gates.
Wentao Li's frozen skip-clones source and the retained predecessor contributors
remain credited by their packages; their bytes are unchanged. The benchmark
uses the existing `skip-clones-tests` overlay, rather than a replacement
mathematical fixture. New work is Apache-2.0.

The final overlap refresh covered 757 open PRs and 1,358 discussion records,
with complete pagination at 2026-10-15 18:56 and 18:58 UTC respectively. Targeted live
search also checked the runner name. PR #2579 addresses test completion and
PR #2625 addresses cancellation, both in `run_isolated_tests.py`. They do not
optimize historical snapshot setup. These searches omit arbitrary diffs and
most closed PR bodies, so they do not establish novelty. Exact heads and scope
are in [TASK.json](TASK.json).

## Open next questions

Does this setup gain persist on Ubuntu CI and the other supported Python
versions? This matters because `copyfile` uses different platform fast paths.
Run the same three-pair benchmark and retain all file/digest and destination
checks. An independent Linux runner was unavailable in this session. The
structured question is in `TASK.json`.

Which authenticated historical inputs should restore the two rejected replay
commands? First reconcile the expected/actual pairs in `VALIDATION.json` against
retained historical sources, with a separate overlap check and successor review.
This contribution retains the failures and their frozen pins.
