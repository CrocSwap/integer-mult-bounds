# Validation and benchmark

2026-10-13 UTC, Windows 11, CPython 3.14.5; exact base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08. Standard library only. All inputs and predecessor files remain unchanged.

The certificate was generated explicitly and then replayed without regeneration:

```text
python -I -B research/emitted-local-integer-replay-seed90/verify.py
python -I -O -B research/emitted-local-integer-replay-seed90/verify.py --benchmark
```

Expected and observed PASS:

```text
PASS_EMITTED_LOCAL_INTEGER_S90 columns=704 orientations=2 retained_controls=25 extra_controls=7 scalar_prefixes=39386
```

The second command verifies the saved mathematical certificate, then refreshes only the separate benchmark. It compiles both retained checker variants with optimize=0, preserving all inherited assertions. Direct full per-prefix entry-list equality is checked; recorded hashes are evidence rather than a replacement for that equality.

Three fresh-process pairs alternate reference/integer order. Every pair has the same LF-normalized complete receipt hash `13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17` and stdout hash `dd643a58258431c3b07d3b06d9060c49677fa23b4fafc9f10988ed1f6867bd9a`. Complete receipt bytes also agree within each same-host differential run.

| Pair | Reference audit seconds | Integer audit seconds | Audit wall ratio | Total process ratio |
| --- | ---: | ---: | ---: | ---: |
| 1 | 6.299954 | 2.614847 | 2.409301 | 2.332497 |
| 2 (integer first) | 6.150977 | 2.570825 | 2.392608 | 2.298070 |
| 3 | 6.540728 | 2.680407 | 2.440199 | 2.355223 |

The median total process ratio is 2.332497, complete audit wall ratio 2.409301, and audit CPU ratio 2.461078. Raw samples and implementation/source hashes are in BENCHMARK.json. The audit interval includes source authentication, compilation, imports inside the retained checker, input reads, both complete orientations, all 25 mutations, receipt writing and stdout capture. The total process interval additionally includes interpreter and adapter startup. Archive preparation and the independent differential verifier are outside these timing intervals. An earlier exploratory pair had contention; it is not used in the final three-pair receipt. Timings are descriptive and not mathematical acceptance conditions.

The original driver rejected every mutation with the same exception type and arguments in both engines. Two intentionally faulty arithmetic engines additionally fail the full retained checker. The complete certificate has no timing fields. LF-normalized source/receipt text tolerates CRLF differences. The input gzip containers are immutable source artifacts copied verbatim from the pinned archive, with both container and payload hashes recorded; no regenerated gzip-container equality is claimed.

`python -I -B scripts/verify_selected_result.py` passed the separate selected-record control at exact kappa `836330098538459/500000000000000000`. `make verify` was attempted and could not execute because `make` is unavailable. No complete cold-chain/native replay or hosted CI is claimed. A harmless Python installation relocation warning precedes successful Python runs on this host.
