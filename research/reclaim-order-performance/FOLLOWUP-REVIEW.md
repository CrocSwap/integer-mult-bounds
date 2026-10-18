# Compiler and certificate follow-up review

This review addresses the [PR #797 triage request](https://github.com/CrocSwap/integer-mult-bounds/pull/797#issuecomment-6160965282).
The two-line change preserves the complete compiler word. Fresh compilation
at both supported historical sizes passed on 2026-10-14. No code correction
was needed. The result remains a verifier improvement with no new kappa.

## Exact inputs

The reviewed PR head is `b879e8472547bd820ce81b1b9c0463176fe5151c`.
Its original base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Refreshed main is `418e40eb2572d930b58c1cf9b82b41c0fc7ee08d`.
The original compiler at that main commit is byte-identical to `reference.py`.
Every input in `SOURCES.json` still matches its digest. The PR can therefore
be reviewed against the same default compiler. This does not compare its
speed with the indexed adapters in [PR #175](https://github.com/CrocSwap/integer-mult-bounds/pull/175) or [PR #779](https://github.com/CrocSwap/integer-mult-bounds/pull/779).

## Code and binding audit

`contains` reads two immutable frame descriptions. Its sort key reads the
rank and slot ID. Before a dependent row is found, `ins` changes only the
local elimination basis. It does not change the retired set or any frame.
Both loops thus visit the same eligible slots in the same order. The first
clearing operation is followed by removal of that slot and immediate return.
No later predicate can observe the changed frame. The allocation path is
also unchanged. This proves equality of the emitted word by induction over
calls to `acquire`; the finite runs below are separate regression evidence.

The three changed historical JSON files have exactly four changed fields:

| File | Changed fields |
| --- | --- |
| `research/joint-dual/SOURCE.json` | The compiler digest in `files` |
| `certificates/joint-dual-kappa.json` | The compiler digest in `local_source_sha256` and `source_manifest_sha256` |
| `certificates/joint-dual-validation.json` | `certificate_sha256` |

A recursive, type-sensitive JSON comparison found no other change. These
are source bindings. No numerical field, selected word or paid profile
changed. The historical [PR #626](https://github.com/CrocSwap/integer-mult-bounds/pull/626) / [PR #543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) context belongs to the original
base; it is not the current selected frontier.

## Fresh execution and retained checks

Both sizes ran once, sequentially. The request for lower scheduling priority
failed with `nice: setpriority: Operation not permitted`, so the runs used
normal priority. This diagnostic is outside the compiler receipts.
The actual output paths were new files in the maintenance directory.
The interpreter was Python 3.14.7 on macOS arm64. To reproduce these runs,
use new output paths such as those below:

```sh
python3 -B scripts/experiments/joint_dual_compiler.py --h 23 --output /tmp/reclaim-h23.json --word /tmp/reclaim-h23-word.json.gz
python3 -B scripts/experiments/joint_dual_compiler.py --h 25 --output /tmp/reclaim-h25.json --word /tmp/reclaim-h25-word.json.gz
```

Both commands exited 0. Their decompressed words match the committed
`certificates/joint-dual-word-23.json.gz` and `joint-dual-word-25.json.gz`
byte for byte. Their full receipts match the corresponding `compiled`
objects in `certificates/joint-dual-compiler.json`, with JSON types preserved.
The runs check 34,230 and 44,938 dirty basis vectors in both orientations,
all physical frame inclusions, and the admitted [PR #55](https://github.com/CrocSwap/integer-mult-bounds/pull/55) scalar graph.
`FOLLOWUP-REVIEW.json` records the exact output and log digests.

The three alternating reference/candidate benchmark pairs and the 18-group
validation remain the prior evidence in `BENCHMARK.json` and
`VALIDATION.json`. The reference compiler, native CRT profiles, mutation
suite and complete selected replay were not run again in this follow-up.
No new timing ratio, remote CI result or complete theorem is claimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is an author-side follow-up, not independent human review or a merge
approval.
