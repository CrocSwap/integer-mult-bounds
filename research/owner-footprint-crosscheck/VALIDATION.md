# Independent replay validation

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Candidate: PR727 `71ba94c981477b3527ef21dd0f8140e795a7664d`. Status: independent finite verification of footprint accounting and local performance corroboration; no new optimization, κ or full theorem claim.

## Same-input complete-check measurements

Each local interpreter ran 15 alternating fresh-process pairs, with seed 89 selecting candidate-first in the first pair. Every full receipt and diagnostic matched. Both engines pay the same frozen-input admission harness; this differs from PR727’s direct-CLI reference timing setup. These measurements corroborate the speedup direction on another environment and do not claim to reproduce the author’s absolute times or percentages. OS file caches were not flushed; there is no timing threshold. The independent endpoint oracle is validated before timing and is not inserted into the timed checker.

| macOS arm64 | Reference median (s) | Pinned PR727 median (s) | Less wall time | CPU medians (s) |
| --- | ---: | ---: | ---: | ---: |
| Python 3.12.12 | 0.303022 | 0.274185 | 9.52% | 0.251173 → 0.235388 |
| Python 3.14.7 | 0.297138 | 0.272085 | 8.43% | 0.239472 → 0.222909 |

Raw samples and implementation fingerprints are in `evidence/python312.json` and `evidence/python314.json`. The 60 timed complete executions produced exactly `OWNER-CHECK.json`, SHA-256 `ec82a647bc3567efef91a1588c86f012cdbb5decac0c25a9f38ba5d11762a092`. Timings include startup, imports, identical pin checks, all original owner/native/profile checks, exact rational moments and receipt writing. Peak RSS is about 125 MB for both engines; no memory reduction is claimed. No full supplier-replay or multiplication-runtime performance follows.

## Passed local checks

```sh
python3 -I -B research/owner-footprint-crosscheck/verify.py
python3 -I -O -B research/owner-footprint-crosscheck/verify.py
python3 -I -B research/owner-footprint-crosscheck/benchmark.py --pairs 15 --out /tmp/pr727-independent-benchmark.json
make selected-record-check
python3 -B -m unittest discover -s tests -p test_selected_result.py -v
```

The complete differential/endpoint check passes on CPython 3.12.12 and 3.14.7. Coverage is explicit in `README.md`: 35,424 roles, 16,128 endpoint-recounted bins, 21,500 exhaustive cases, 6,000 sequential operations, nine full-map controls, five actual-source mutations and four pin controls. Optimized Python passes too. The complete output and derived state are compared, not just the pass marker.

A minimal export containing this package and the 17 original pinned source/context files passes under isolated optimized Python from a path containing spaces, with `/` as its working directory. No Git history, network or installed dependency is needed. The four vendored PR727 files match the exact Git blob IDs returned for its pinned head; notices and proof are byte-identical. The new independent runner refuses drift before importing the vendored code.

A final source-inventory check correctly rejected one untracked `exact_intervals.cpython-312.pyc` created by the exploratory in-process pilot without `-B`. The comparison found no missing or changed reviewed file. Removing only that agent-generated cache restored the clean source inventory. Published commands use `-B`.

The unchanged selected-record checker, all five existing selected-record tests and all seven historical checkpoint source inventories pass. Original tracked files, selected metadata and `upstream/` remain unchanged. Final diff, source fingerprints and artifact consistency are checked before submission.

## Scope limits

The endpoint algorithm independently checks footprint bounds, disjointness, cardinality and compact-prefix/idle accounting. It does not establish physical legality of the provided windows or independently reconstruct supplier algebra. PR727’s original 19-control harness is not republished or claimed to have been rerun; this package supplies its own explicitly scoped oracle and controls. No full `make verify`, cold construction, full controller/47-inequality assembly, Lean, remote CI or independent human-review pass is claimed. All inherited all-size, hosting, precision/tape and analytic assumptions remain.

Substantial OpenAI Codex assistance; prepared by Brian / JoyboyBrian under Apache-2.0. PR727 and construction attribution is retained in `README.md` and the unmodified vendored notice.
