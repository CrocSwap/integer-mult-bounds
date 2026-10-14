# Notice

Apache-2.0 (`LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## New in this package

- `code/adapt.py`: writes `gen_r480.py`, `eleven/audit.py` and `eleven/local_audit.py` from PR #493's files
  by 8 listed string edits (each anchor checked to occur exactly once).
- `data/bitE8mut-r480.json.gz`: the R480 word. `verify.py` rebuilds it byte for byte from PR #493's frozen plan.
- `data/hosting-r480.json`: the hosting selection, nominated by PR #493's `discovery/host_select.py` (PR #442's
  integer programme) and rediscovered by `verify.py`.
- `verify.py`, `EXPECTED.json`, `MANIFEST.json`, `README.md`.

## Used from PR #493 (research/e8-bit-carrier-skeleton, eumemic, commit c3a9a43), unchanged

The generator and its modules (`code/skeleton/`), the frozen plan and partition (`data/skeleton/`), the relaxed
checker generator, `interface.py` and the mutants (`code/bit/independent/`, `code/bit/mutate_records*.py`), the
vendored PR #370 checker, exporters, cohort checkers and Gram check, the nine- and eleven-stage geometry, PR #472's
adapted emitter, audit, invoice and assembly (`code/eleven/`; audit.py and local_audit.py via code/adapt.py), PR #315's moment engines, the hub files under
`code/hub/`, and the cited complex receipts. The provenance and licences of those files are listed in PR #493's
`NOTICE.md`. Its `MANIFEST.sha256` is checked by step 0 of `verify.py`.
