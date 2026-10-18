# Batch source pins for registered research replay

The source-validation stage now reads its Git blobs through one
`git cat-file --batch -z` process. On the fixed 130-row fixture, local median
wall time falls by about 40 times. This is a tooling result; no mathematical
replay, new supplier, exponent saving or selected-frontier change is claimed.

## Scope and evidence

Original assignment: `replay-runtime`, selector nonce
`56f0ac74ea193d0ed3d48475463fca2a`, priority revision 2. The scope is refined
to the source-pin stage before registered mathematical replay. The baseline
profile measured 1.042 seconds for 130 source rows, including 0.999 seconds in
261 calls to the Git wrapper. The source-bound orientation command passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` before work began.

The implementation retains every exact Git blob ID, SHA256, live-input byte
comparison, originating-card check and replay-selection rule. It reads one blob
at a time, so it does not retain the entire source inventory in memory. There is
no persistent cache: a changed live input is rejected on the next validation,
and restoring it allows validation again. Catalogue/selected-record provenance
remains historical. Missing sources and non-blob Git objects are rejected;
the latter explicitly excludes malformed provenance entries naming a tree.

The benchmark uses synthetic registered-package inventories built from the
first 8 or 128 lexicographically ordered tracked `scripts/**/*.py` paths at
base `1f327c6f3e3a35271c5c141d381b540bab8ad005`, plus the two original
provenance rows. It loads the old validator from the pinned commit and the new
validator from the working tree, then compares their returned task/manifest
objects on identical fixtures. Fixture setup is excluded; after warmup, five
timing pairs alternate execution order. These are measurements of this stage
on this host, not a promise about whole replay time.

| Python | Rows | Git processes before → after | Median before | Median after | Ratio |
|---|---:|---:|---:|---:|---:|
| 3.12.14 | 10 | 21 → 1 | 0.106765 s | 0.007619 s | 14.01 |
| 3.12.14 | 130 | 261 → 1 | 1.281875 s | 0.032077 s | 39.96 |
| 3.14.7 | 10 | 21 → 1 | 0.089093 s | 0.006317 s | 14.10 |
| 3.14.7 | 130 | 261 → 1 | 1.109479 s | 0.026581 s | 41.74 |

All timing samples, source paths and environment details are in
[BENCHMARK-python312.json](BENCHMARK-python312.json) and
[BENCHMARK-python314.json](BENCHMARK-python314.json). Both runs used macOS
26.3.1 arm64 and Git 2.53.0. The 3.14 run also enabled Python optimization;
the control harness uses explicit checks. The registered replay uses ordinary
Python 3.12 as before.

Twelve failure controls reject changed blob IDs/SHA256 (including the last
row), missing sources, a wrong commit, omitted catalogue provenance, changed
original cards, escaping paths, live-input drift, an invalid duplicate row,
non-blob trees, truncated replies and a nonzero Git exit after the final reply.
Positive controls cover exact validation parity, restored input, later
catalogue changes, valid duplicate rows, empty/binary blobs, NUL content,
filenames containing spaces/newlines, and reaping the child on early close.
The existing onboarding suite passes all 12 tests on Python 3.12, including
bounded replay and dependency-selection controls.

The change is confined to `scripts/research_package.py` and this package.
Frozen evidence, source archives, suppliers and their mathematical commands
are unchanged. The batch reader needs Git's `cat-file --batch -z` interface;
older Git versions without it were not tested. Full multiplication proof,
supplier cold replays, hosted Linux results and independent human review are
outside the evidence reported here.

## Reproduce

From a full-history checkout with Git and Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/research-package-pin-batching --check-only
python3.12 -B scripts/research_package.py --package research/research-package-pin-batching
```

The registered hook runs all controls, three alternating timing pairs and the
existing onboarding tests. Timing has no flaky pass threshold; validation
parity, mutation rejection and the exact process-count reduction are enforced.
To repeat the five-pair measurements without writing tracked artifacts:

```sh
python3.12 -I -B research/research-package-pin-batching/verify.py --benchmark
python3 -I -O -B research/research-package-pin-batching/verify.py --benchmark
```

The predecessor script is pinned as provenance in [SOURCES.json](SOURCES.json)
because the patch changes its working bytes. The generator and existing tests
are pinned live inputs. All three are declared in [VERIFY.json](VERIFY.json)
for replay invalidation. [TASK.json](TASK.json) records scope and stopping rules.

## Open next questions

Does this speedup hold on the Linux/Python 3.12 replay runner? Run the same
registered hook there and retain its log, separating the deterministic process
reduction from host-dependent timing. Hosted execution was not observed during
the local benchmark. This matters for review throughput, not the mathematical
bound. The structured next question is in TASK.json.

## Credit and overlap

Douglas Colkitt designed the package format, source pins, historical/live input
distinction and explicit replay workflow retained here. Maxime Fleury's gzip
audit, following Antoine Olivier's independent replay, informed portability
triage. PR1298 concerns Windows codecs and process cleanup; this contribution
does not replace it. PR1461 accelerates rational annihilator checks, PR1559
repairs gzip rebuild comparisons, and PR1372 checks T37 role bindings.
They address different validation stages. The task claim is
[Discussion #1585](https://github.com/CrocSwap/integer-mult-bounds/discussions/1585).

Prepared by Arham Tahir with substantial OpenAI Codex assistance; no subagents.
Apache-2.0, with predecessor attribution retained.
