This opt-in tool speeds up the historical ternary frame checker by caching results for exact ordered frame pairs. It retains both orientations, every physical edge, and the existing rational arithmetic. Complete matrix-and-edge transcripts and published small-control fields for h=8 and h=9 match the retained checker. Timings use alternating fresh processes. The h=29 construction is not replayed, and kappa is unchanged.

Douglas Colkitt wrote the retained checker. Zhihao Chen's PR7 supplied the earlier five-subset motif and common-pair geometry. Hanson Sun prepared this contribution with substantial OpenAI Codex assistance. See CLAIM.json for scope, SOURCES.json for pins, and evidence/ for checks and measurements.

```sh
python3 -B research/ternary-frame-cache/verify.py --out /tmp/ternary-frame-cache-93 --pairs 3
```

Expected: `PASS_IDENTICAL_TERNARY_FRAME_REPLAY 84672 edges; ... ratio of medians`.
Output directory: fresh. Dependencies: Python 3.11+ standard library on macOS or Linux.

| Input | Orientations | Physical edges | Rank sum per orientation | Decreasing dimensions per orientation |
|---|---:|---:|---:|---:|
| h=8 | 2 | 9,464 | 5,936 | 224 |
| h=9 | 2 | 75,208 | 33,084 | 324 |

```text
intern(A) = intern(B)  iff  A == B entrywise over Q
key(old, new) = (intern(old), intern(new))
value(old, new) = (rank(new-old), rank(new)-rank(old))
cache lifetime = one verify_invocation_frames call
per-edge predicate = rank(new-old) == abs(rank(new)-rank(old))
projection key = immutable rational row tuple U; ambient H fixed within the call
```

[Adaptation diff](evidence/ADAPTATION.diff) · [Source pins](SOURCES.json) · [Task card](CLAIM.json)

| Verification | Reproduction |
|---|---|
| Semantic controls, exact traces, alternating timing pairs | Command above |
| Controls only | `python3 -B research/ternary-frame-cache/test_package.py` |
| Original ternary tests | `python3 -B -m unittest discover -s tests -p test_ternary_side.py -v` |
| Source selection binding | `python3 -B scripts/verify_selected_result.py` |

| Boundary | Status |
|---|---|
| h=8,9 graph receipts and arbitrary-input scalar controls | Replayed in both engines |
| Both full physical-frame edge streams | Compared entry by entry, including every rational numerator and denominator |
| Missing common pair, singular Gram, non-idempotence, wrong target, wrong role count | Rejected by both engines |
| Same-rank unequal frames, reversed transitions, exact hash collisions, identity reuse | Targeted cache controls |
| Source mutations | All 20 pinned dependencies individually rejected |
| Omitted, duplicated, reordered or changed edge/matrix records | Comparator controls |
| Python `-O`, existing output directory | Refused |
| h=29 DAG and complete historical ternary assembly | Not replayed |
| Selected frontier1094 construction and all-size theorem | Not replayed or proved |
| Upstream, frozen source, selected certificate, default checker | Unchanged |

License: Apache-2.0. Source arithmetic and construction credit: Douglas R. Colkitt; prior F3 motif: Zhihao Chen, [PR7](https://github.com/CrocSwap/integer-mult-bounds/pull/7). Related tooling: [PR154](https://github.com/CrocSwap/integer-mult-bounds/pull/154) (scheduling and paired-cube frames), [PR367](https://github.com/CrocSwap/integer-mult-bounds/pull/367) (PR364 integer elimination). Exact heads and scope differences: [CLAIM.json](CLAIM.json).

| Python 3.14.6, macOS arm64; three alternating pairs | Reference | Cached |
|---|---:|---:|
| Median wall seconds | 11.525 | 6.775 |
| Maximum observed RSS, MiB | 96.297 | 105.172 |

Ratio of medians: **1.70**. [Timing and exact receipts](evidence/benchmark-python314.json) · [18 control tests](evidence/controls-python314.log) · [Initial bottleneck profile](evidence/profile-python314.txt).

Measurement boundary: complete small-control worker processes, including source admission, DAG construction, scalar checks and result writing; no tracing in timed runs. Shared host; OS caches not flushed. No speed threshold. Peak memory includes the complete worker, not only the caches.

Python 3.11: **18/18** controls; **84,672/84,672** edge records; exact transcripts equal across Python versions. [Complete replay receipt](evidence/benchmark-python311.json) · [Controls](evidence/controls-python311.log) · [Original tests and source binding](evidence/validation.json).
