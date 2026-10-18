# Coordinated cold-ended owner repair: validation

Conditional **κ = 0.001625744726006285**; conservative **κ = 0.001625744723187284**.

Both complete fresh replays passed on Python 3.14.8: macOS in **271.517718 seconds**, Linux aarch64 in **309.898414 seconds**. Each executed **42 top-level stages**, rebuilt the baseline and both native providers with no reused artifacts, and sealed **43 output artifacts**. Nested baseline checks are retained in its receipt. The additional declarative and independent map/native-profile/rational-moment checks also passed under `-I -O -B`.

The results agree except for elapsed time. The independent exact-check receipts and fourteen native artifacts are byte-identical. Both source manifests still pass after replay. See `CROSS-PLATFORM.json`; platform directories contain the actual logs and hash-bound receipts.

All **23 controller** and **114 assembly** mutation controls remain required, along with the retained local, omission, phase-timing and generated-identity controls. Five additional malformed declarations were rejected even with Python optimization enabled; `DECLARATION-CONTROLS.json` records them. `SOURCE-REVIEW.json` confirms unchanged inherited runtime, provider contracts and recipes relative to PR614.

`fork-flush/` records the four fresh-context probes, rational selection, and selected-session continuation. The initial probes started from the same all-JP8 snapshot, not PR614. The new public PR614 input arrived during the round and was provided only after selection. This is a bounded application of the strategy with nominal eight-minute horizons, three concurrent worker slots and closure overhead, not an equal-compute replication, an optimality claim or proof of distinct idea-basin escape. `search/` contains nomination receipts; solver objectives are not certificates.

The source package is [complex-cold-owner-repair](../complex-cold-owner-repair/README.md). Validation evidence remains outside its manifest. All inherited all-size and realization assumptions remain open; no unconditional theorem, completed Lean proof, practical speedup or κ=1 result is claimed.
