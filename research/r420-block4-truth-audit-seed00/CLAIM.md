# Sprint claim and handoff

Initial claim posted on the coordination board: [D#1163, comment 18911525](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911525).
Result submitted as [PR #1383](https://github.com/CrocSwap/integer-mult-bounds/pull/1383).

- **Track / seed:** bit supplier, OS seed 0.
- **Base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- **Object:** PR1363 R420 phase-B block 4, frame 546; source slice `B[313:371]`, candidate slice `B[313:364]`.
- **Method:** derive the target from the source slice and exhaust all 4,096 Boolean inputs with a direct simulator; reject omitted and reversed gate controls.
- **Result:** source and 51-gate candidate implement the same pinned 12-wire map; no new circuit, supplier, or κ claim.
- **Reproduction:** `python3 -I -O -B research/r420-block4-truth-audit-seed00/verify.py`.

The audit is intentionally local. PR1363's reported complete-word savings and paid-profile check are retained as predecessor evidence, not reproved here.
