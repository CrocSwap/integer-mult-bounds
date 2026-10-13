# Notice

Apache-2.0 (`LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## New in this package

- `code/punct_cfg.py`: the one configuration (v, R, live labels, totals map, CST) of the punctured chain.
- `code/adapt.py`: writes adapted copies of nine of PR #493's files (`emit`, `audit`, `local_audit`, `assemble`,
  `host_select`, the nine- and eleven-stage `geometry`, the independent checker, `mutate_records`) by 56 listed string edits
  (each anchor checked to occur exactly the listed number of times). The parent tree is never modified.
- `code/word/` (`pword.py`, `gen_punct.py`): the punctured word builder (PR #493's generator logic restricted to a live port
  subset, nine pseudo-target totals). Written for this package; imports the parent's `geom`, `e8`, `wordkit` and plan.
- `code/price/pricex.py`: the exact pricing harness (local-histogram replay of the word, the same whole-residual hosting
  programme, `moment.certify`), validated against the registered R489 / R480 values; only its package path was changed.
- `code/mutants.py`, `code/compose_control.py`: the mutation controls and the composition/control with the cited complex b.
- `code/adapt503.py`: PR #503's `adapt.py`, byte-identical (DreamingOfClouds, with Claude Opus 5.5), used only to build the
  stock R480 control chain for the regression.
- `data/bitE8mut-v111-r489.json.gz` (the word; `verify.py` rebuilds it byte for byte), `data/hosting-v111-r489.json` (the hosting
  selection nominated by `host_select.py` and rediscovered by `verify.py`), `data/control-r480/` (PR #503's R480 word, hosting
  selection and EXPECTED.json, byte-identical copies), `data/complex/pr535/EXPECTED.json` (PR #535's receipt, byte-identical,
  git blob id in `data/complex-b.json`), `verify.py`, `EXPECTED.json`, `MANIFEST.json`, `README.md`.

## Used from PR #493 (research/e8-bit-carrier-skeleton, eumemic, commit c3a9a43), unchanged

The skeleton modules and frozen plan, the vendored PR #370 checker and its relaxation, `interface.py` and the mutants, the
exporter, the official cohort checkers and the Gram check, PR #472's emitter, audit, invoice and assembly (as adapted by #493
and by `code/adapt.py`), the hosting modules, PR #315's moment engines, the hub files under `code/hub/`. Provenance and
licences of those files are listed in PR #493's `NOTICE.md`; its `MANIFEST.sha256` is checked by step 0 of `verify.py`.
