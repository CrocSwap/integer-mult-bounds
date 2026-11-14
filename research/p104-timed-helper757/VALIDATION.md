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

All six registered commands passed. The fresh native and signed stages took
129.16 and 136.65 seconds. The source, row and physical checks also pass under
optimized Python; the price and complete application launchers reject that
mode before proof work, because their retained engines require assertions.

The official export of scientific commit
`61f985ed72c5e17c7237f180ecde0a7255ee1453` passed integrity checks. All six commands
then passed in 302.59 seconds from its read-only, Git-free extraction, with an
empty executable search path. All 135 exported package files kept their bytes.
See `data/COLD.json` and `data/VALIDATION.json`. The later documentation,
license-provenance and validation-receipt changes do not alter any scientific
file or retained input; their hashes are compared with this export.

Original Git readback matched all 109 retained files. The initial Git add
normalized five retained text files. A scoped `.gitattributes` rule now
preserves their exact bytes; the unpublished commit was corrected before
export. The committed-byte and executable-mode check passed on all 135 files.
The optional full-history preflight could not run because this checkout is
shallow. The scientific commit's direct parent is the pinned canonical main;
the complete source closure is committed and passes the Git-free replay.
No full-history preflight success is claimed.

The replay plan selects only this package. The first draft manifest exceeded
the shared 1200-second total timeout cap by 10 seconds. Its exact-row timeout
was reduced to 100 seconds; the manifest now passes, and that command finished
in 38.57 seconds in the cold replay. No scientific timeout was extended.
Hosted CI and independent substantive review are separate from these passes.

The predecessor reports a shared CI navigation failure: unchanged `docs/ci-verification.md`
names PR6030 while the selected record names PR7000. PR7276 addresses that
separate issue. This package does not include an unrelated workflow repair.
