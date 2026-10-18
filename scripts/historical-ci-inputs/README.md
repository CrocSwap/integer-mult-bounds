# Historical CI input snapshots

These are exact Git blobs, not new source pins or changes to the selected result.
The maintenance launcher `scripts/replay_historical_check.py` verifies each blob
against its unchanged predecessor manifest, copies tracked working files into a
temporary tree, replaces only the declared historical inputs there, and executes
the original checkers. It works with shallow CI checkouts and changes no live
source file. The live Makefile must still preserve its entire authenticated
historical prefix; appended targets are allowed, prefix mutations reject. All other inputs remain the current tracked working
bytes, so their
original checker conditions and corruption controls remain active. After replay,
every tracked file in the temporary tree must still have its initial byte hash
(including the authenticated historical replacement), preserving the original
reproducibility gate as well as protecting the live checkout.

| Snapshot | Original path | Source commit | Consumer |
| --- | --- | --- | --- |
| `selected-result.json` | `certificates/selected-result.json` | `5c5567d15bd019186519a4db267914257b5f1ac0` | `research/r420-two-sided-basis/SOURCES.json` |
| `Makefile` | `Makefile` | `b84ba67156a01f9c2cb34fe1e3cb1dcdeab00d9c` | `research/community-reconciliation92-audit/MANIFEST.json` |
| `audit_fused_block.py` | `scripts/audit_fused_block.py` | `6e564879f51ae16f23d392e9e196c605f36d90df` | `research/split-skip/SOURCE.json` |

The split-skip replay restores all three exact helpers named by its unchanged
manifest: the fused-block snapshot above, the exclusion circuit preserved in
`research/exclusion-embedding-masks/baseline.py`, and the shared-point circuit
preserved in `research/shared-point-digest/baseline.py`. The latter two are
Wentao Li's retained baselines for the accepted support-mask and digest
optimizations. Both also match the PR53 parent `3ffd4021995c959ac02d12920e0279ae97dd03c7`.
Each replacement and reviewed live successor is independently authenticated;
missing pins, corrupted baselines, duplicate paths, untracked dependencies and
unknown live source changes reject before copying. No original checker is edited.

Use `python3 -B scripts/replay_historical_check.py r420` (add `--native` for
C++17/Boost), `reconciliation92`, or `split-skip`. These check historical finite
constructions/provenance; they do not recertify the current selected supplier or
formally verify the full multiplication theorem. The native R420 checks and the
split-skip producer remain required in their CI jobs.

Credit Scott Woolsey Biggart and Greer Guthrie for the R420 evidence; the retained
reconciliation records and their contributor attribution; Chafik Boukhalfa,
RaD/hipotures and Rohan Garg for the split-pair lineage; and the original source
headers. The snapshots retain the repository Apache-2.0 license. This maintenance
adapter was prepared by Dennis with substantial OpenAI Codex assistance.

## Reviewed scheduler and UTF-8 successors

The reconciliation92 snapshot also restores `scripts/run_parallel.py` from
`b84ba67156a01f9c2cb34fe1e3cb1dcdeab00d9c`, exactly matching its unchanged
`integrated_files` pin. UTF-8 child mode preserves the original Unicode JSON
loads on Windows. The live worker-memory, assertion-environment and
direct-script cancellation improvements remain unchanged and separately
authenticated before replay.

`tooling-exact` runs all seven original exact-accelerator commands inside a
private snapshot. It restores `scripts/verify_hpe_lean_binding.py` from
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, matching the unchanged Clifford
state benchmark's context pin. The cold-interface checker executes this helper
indirectly. Child interpreters
therefore use explicit UTF-8 mode, retaining the frozen bytes and matching
the current live helper's UTF-8 behavior without modifying its source. All frozen
source manifests, rejection controls and final unchanged-file gates remain.

Both new snapshots retain their original headers and Apache-2.0 licensing.
Credit the historical reconciliation contributors, ywz65's UTF-8 repair,
the worker-budgeting/assertion-protection/direct-script cancellation
contributors in the retained Git history.
Adapter and failure controls: Dennis, with substantial OpenAI Codex assistance.

The reconciliation92 snapshot also restores `scripts/verify_parallel.py` from
the same `b84ba671...` commit, matching its unchanged manifest pin. The live
direct-script cancellation successor is independently authenticated and kept.

## Complete legacy graph families

The accepted three-target digest optimization has a narrower target shape than
older copied/strip/pair graph variants. Their original generic digest is retained
in Wentao Li's `research/partial-swap-digest/baseline.py`. The legacy community,
producer, strip and pair Make targets and the seven affected test modules run in
private, source-authenticated copies with that original digest. Every original
command and the final tracked-byte gate remain; live optimized performance tests
continue to run on the live source. This is historical compatibility, not a fix
or validation of the optimized helper for other target shapes.

The split-skip snapshot now restores all five mismatching helpers, including
`scripts/audit_sparse_fusion.py` (exact bytes from
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, matching its frozen SOURCE.json).
Its producer runs inside the same authenticated copy as its witness and tests.
The legacy producer group also restores the corresponding original partial-swap
certificate from that commit. The new `partial-swap-context.json` records this
context separately; its digest is cross-checked against the unchanged digest
benchmark's BASE_CERT_SHA256 by a regression test. The current live certificate
and all predecessor manifests remain unchanged. Exact Git baseline objects for
the performance tests are fetched only in the tests matrix group.

Credit Wentao Li's preserved optimization baselines, the copied/strip/pair graph
contributors and retained source headers. Adapter and regression controls:
Dennis, with substantial OpenAI Codex assistance; Apache-2.0.

## Ledger review contexts

`tooling-ledger` retains the current ledger checker, but restores the historical
HPE helper required by `community-hyperplane599-audit/SOURCE.json` and the original
K492 HPE transport helper pinned by `community-k492-audit/SOURCE.json`. The latter
snapshot is from `5c5567d15bd019186519a4db267914257b5f1ac0`; the unchanged review
pins authenticate both. The reviewed UTF-8 and integer-row transport successors
remain untouched in the live checkout. Current ledger records and archive
controls are still checked; this does not roll the ledger back to an older copy.
All unit and corruption tests continue to run separately against the live tree.
Credit the K492 owner-repair authors and Wentao Li's production optimization,
along with the original helper headers. Adapter: Dennis with OpenAI Codex.

The ledger snapshot also restores exact source bytes for subsequent accepted
factory pins, CI documentation, scheduling, data-corner and assertion-safety
updates. Each is checked directly against the unchanged per-PR coverage record,
not an invented new historical pin. The full current ledger, decisions and
archive checks still run. This is an integrity audit of the historical reviewed
bytes, not a claim that later live implementations are unchanged or reviewed
by that historical batch. Live tests and production jobs retain those successors.

| Snapshot | Historical path | Exact source commit |
| --- | --- | --- |
| `ledger-frontier741-SOURCE-PINS.json` | `research/complex-factory5-resynthesis/SOURCE-PINS.json` | `2cdd93d0250554e5160edbb8535c4500c4227349` |
| `ledger-frontier741-verify.py` | `research/complex-factory5-resynthesis/verify.py` | `2cdd93d0250554e5160edbb8535c4500c4227349` |
| `ledger-frontier741-SOURCES.json` | `research/supplier-circuit-consolidation/SOURCES.json` | `2cdd93d0250554e5160edbb8535c4500c4227349` |
| `ledger-frontier741-ci-verification.md` | `docs/ci-verification.md` | `877def00b10effdf176ec93d0d3e2e93f2f452e9` |
| `ledger-frontier890-verify_complex741_parallel.py` | `scripts/verify_complex741_parallel.py` | `3b83e4f14825ce1ae038a8c8159f130646991086` |
| `ledger-batch932-run_isolated_tests.py` | `scripts/run_isolated_tests.py` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch932-test_isolated_test_runner.py` | `tests/test_isolated_test_runner.py` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch932-README.md` | `research/data-corner-performance/README.md` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch932-SOURCE.json` | `research/data-corner-performance/SOURCE.json` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch932-replay.py` | `research/data-corner-performance/replay.py` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch932-test_replay.py` | `research/data-corner-performance/test_replay.py` | `550746fd233635cfdb08b36f9f27e1d434ffd4e1` |
| `ledger-batch1047-README.md` | `research/p112-free-sink-audit97/README.md` | `e2e0960be93535e867210dac58dc77d832cbc8dd` |
| `ledger-batch1047-independent.py` | `research/p112-free-sink-audit97/independent.py` | `e2e0960be93535e867210dac58dc77d832cbc8dd` |
| `ledger-batch1099-README.md` | `research/r439-omission-atlas-seed81/README.md` | `0a31ad88419a4eebf515d3df4f6732c4e38c0029` |
| `ledger-batch1099-verify.py` | `research/r439-omission-atlas-seed81/verify.py` | `0a31ad88419a4eebf515d3df4f6732c4e38c0029` |

Nested ledger/reconciliation replays carry an SHA256-authenticated complete
tracked-input catalogue into Git-free copies, including the final byte gate.
A real nested replay regression exercises this path under an optimized parent.
The live isolated-runner extension and its failure-reporting test are separately
admitted as exact successor hashes in the current ledger checker; no frozen
coverage manifest is rewritten and arbitrary changes still reject.

Historical selected-record checks now resolve only their own exact archived
HPE supplement, after authenticating both the known live UTF-8 successor and the
original snapshot. The current selected record continues to check its live
supplements strictly. This permits both records to be checked in the same tree
without globally substituting a source version required by just one of them.
The CI-input test runs directly on the live tree; all 35 live pins and trigger
coverage controls remain active. Neither selected record nor checkpoint changes.
