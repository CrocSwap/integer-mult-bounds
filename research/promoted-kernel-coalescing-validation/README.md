# Full cold replay evidence

Both official executions started from absent output directories and rebuilt the
complete PR558 baseline, all three typed provider construction chains, every
final native/phase proof, and the complete physical admission. No local proof
or construction baseline was reused. All 41 root stages passed:

| Environment | Python | Seconds |
|---|---|---:|
| macOS arm64 | 3.14.8 | 261.034525 |
| Linux aarch64, DGX Spark 2 | 3.12.3 | 303.314542 |

`CROSS-PLATFORM.json` checks all 21 provider proof-content identities and every
numerical/semantic invoice field. Every root result field except runtime agrees.
The canonical result SHA-256, excluding only `seconds`, is
`036fdc4e146ab0777050e0c042b6bd2e45316c89a7f651a5ffd22aface8b00f0`.
Raw compressed bytes, paths, timings and derived receipt hashes may differ.
Each run independently validates the raw references before content comparison.

Each platform passed 24 new frame omission/overpromotion controls, 33 generic
local controls, 31 physical owner controls, 147 assembly controls, three phase
timing accept/reject pairs, three actual recompressions, 27 proof-content
mutations and 27 reference/metadata mutations. The exact phase replays cover
3015, 3015 and 2928 directed edges, plus 224 endpoint adapters per provider.
Inherited construction omission and coverage controls also run in full.

`SOURCE-VALIDATION.json` records the 259 unchanged vendor files and original
Git blob checks. `MODE-REJECTIONS.json` checks optimized/discovery rejection.
All recorded artifact digests were checked while collecting these receipts.
The frozen source manifest SHA-256 is
`ec29ea58a15a909e4314323141b59d22420dca61734724050d417b454d950152`.

PR584 appeared while these cold runs were underway and reports exactly the same
rate and construction. `PR584-COMPARISON.json` compares its pinned head
`e580557d85eb8b8a100361926252d120eb447a44`: identical owner bytes and expected
mathematical fields (only the comparison baseline differs). This package is a
bundled, portable independent realization of that rate, not a higher frontier.
PR584 itself was source-compared, not separately replayed here.

The `baseline/` directory separately preserves the previously published PR572
18-group repository checks on the identical base `db0e57b`. See
`BASELINE-REUSE.json` for file hashes and the original OpenMP failure/resume
boundary. This reused aggregate evidence is distinct from the freshly rebuilt
PR558 construction inside each official witness replay.

GitHub CI status is separate from these local results. This remains finite
conditional evidence, not an unconditional multiplication theorem or κ = 1.
