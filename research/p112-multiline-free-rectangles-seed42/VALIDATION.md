# Executed local validation

The exact implementation, proof and certificate digests are recorded in
`VALIDATION.json`. No external numerical dependencies are used.

- Registered Python 3.12.2 replay passed both commands and the package's
  metadata, live input and Git provenance checks.
- The primary certificate checks 2,553 cuts, all 28 coordinate symmetries,
  seven Gaussian-rational fixtures / 87,808 entries and 12 internal controls.
  The separate checker checks 6,216 anchor pairs / 31,080 spans, all proposed
  symmetries / 351,232 pairing entries, a 12,544-entry integer identity and
  six internal controls.
- Five external corrupted-input runs failed as intended: one omitted cut, a
  falsified baseline rank, a missing independent span-check count, a removed
  source pin and altered source bytes.
- Both commands passed under Python 3.14.6 with `-I -O -S -B` from a minimal
  relocated, read-only source export. All ten exported file hashes were
  identical before and after. Documentation added afterward is outside that
  runtime-input export; the checked source and certificate bytes are pinned.
- The repository's 20 `test_research_*.py` tests passed under Python 3.12.2.
  An earlier 3.14 run skipped its one explicitly 3.12-only replay test; the
  3.12 run covers it. A mistyped discovery pattern initially selected zero
  tests; that empty run is not counted as evidence.
- `scripts/verify_selected_result.py` passed. The selected-record baseline
  and the task card's complex-coefficient positive control also passed.
  These are the stated source/arithmetic checks, not a selected cold replay.
- The additive package was checked against refreshed upstream
  `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`; its two live inputs, selected
  record, contribution instructions and registered replay runner are unchanged
  from the research base. Patch application and whitespace are checked before
  submission.

The scope excludes physical realization, all-size compilation, shared-copy
billing, full supplier recurrence, native admission and a multiplication
proof. No proof assistant or independent human review was used. Hosted CI and
maintainer review are separate from these local checks. Ruff was unavailable
in the local interpreter and is not claimed as a passed check.
