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
| `exclusion_circuit.py` | `scripts/exclusion_circuit.py` | `0b1cccf86e2f5132ed286a26ef0a681a495740ea` | `research/skip-clones/SOURCE.json`, `research/split-skip/SOURCE.json` |
| `shared_point_circuit.py` | `scripts/shared_point_circuit.py` | `0b1cccf86e2f5132ed286a26ef0a681a495740ea` | `research/split-skip/SOURCE.json` |

The split-skip replay restores all five changed helpers named by its unchanged
manifest: the fused-block snapshot above, the exclusion circuit preserved in
`research/exclusion-embedding-masks/baseline.py`, the shared-point circuit
preserved in `research/shared-point-digest/baseline.py`, the partial-swap
shared-point helper in `research/partial-swap-digest/baseline.py`, and the sparse
fusion checker in `research/sparse-fusion-orbits-production/baseline.py`. These are
Wentao Li's retained baselines for the accepted support-mask, digest,
initialization and spectator-orbit optimizations. The sparse-fusion package
retains ToikY's orbit argument and Douglas R. Colkitt's original screen credit.
The exclusion and canonical shared-point copies
also match the PR53 parent `3ffd4021995c959ac02d12920e0279ae97dd03c7`.
The partial-swap baseline matches `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
and both clone manifests. The exclusion and shared-point snapshots in this
directory are retained exact reference copies; the replay uses the attributed
research baselines above. The skip-clones replay restores both its exclusion
and partial-swap dependencies.
Each replacement and reviewed live successor is independently authenticated;
missing pins, corrupted baselines, duplicate paths, untracked dependencies and
unknown live source changes reject before copying. No original checker is edited.

Use `python3 -B scripts/replay_historical_check.py r420` (add `--native` for
C++17/Boost), `reconciliation92`, `skip-clones`, or `split-skip`. These check historical finite
constructions/provenance; they do not recertify the current selected supplier or
formally verify the full multiplication theorem. The native R420 checks remain
required in their CI job; the split-skip replay includes its native producer.

The `skip-clones` replay includes the complete native producer, certificate
regeneration and adversarial tests. `split-skip` authenticates all five of
its historical replacements before copying anything. Its original native
producer command runs inside the same authenticated tree before the witnesses,
because its inherited skip-strips checker also pins the partial-swap helper.
The clone test module also
uses an isolated historical tree when invoked directly by unittest or the
isolated test runner; an already historical tree is used without nesting a
second copy. Other test modules, including Wentao Li's optimization controls,
continue to use the live scripts. No source pin is loosened or rewritten.

Copies are placed in a unique temporary directory under the checkout's ignored
`build/` directory and removed on exit. This keeps the multi-GB tracked tree
off memory-backed `/tmp` while test modules run concurrently.

Credit Scott Woolsey Biggart and Greer Guthrie for the R420 evidence; the retained
reconciliation records and their contributor attribution; Chafik Boukhalfa,
RaD/hipotures and Rohan Garg for the split-pair lineage; and the original source
headers. The snapshots retain the repository Apache-2.0 license. This maintenance
adapter was prepared by Dennis with substantial OpenAI Codex assistance.
The clone/split-skip compatibility extension was prepared with substantial
OpenAI Codex assistance and retains all original source headers and credits.
