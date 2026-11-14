# Validation

The construction and complete application passed locally on CPython 3.12.16,
macOS arm64, with the standard library and assertions enabled.

- Exact forward and reverse rows, all erased rows and four changed-word
  controls passed. `data/EXACT.json` records the deterministic result.
- Both directed full prices and the fixed-invoice ceiling passed.
- All 512 forward and adjoint columns of the new paid child passed.
- The complete native stage passed in 122.93 seconds. It includes all 38
  affected lineage pairs, grid, owned/COPY, ordinary and precision checks.
- The complete signed stage passed in 138.64 seconds. It includes 17 calls,
  3,040 catalogue maps, 104 main boundaries, 13,600 native contacts, tape
  accounting and all 58 outer predicates. See `data/FINAL.json`.

The first selected-binding check failed because this sparse checkout lacked
147 unchanged selected-source files. Those exact main-branch files were
materialized. The metadata binding check then passed. This did not run the
selected supplier or change its files.

Registered replay, optimized-mode controls, committed-byte checks and the
official Git-free export check are pending at this checkpoint. Hosted CI and
independent substantive review are not yet claimed.

The predecessor reports a shared CI navigation failure: unchanged `docs/ci.md`
names PR6030 while the selected record names PR7000. PR7276 addresses that
separate issue. This package does not include an unrelated workflow repair.
