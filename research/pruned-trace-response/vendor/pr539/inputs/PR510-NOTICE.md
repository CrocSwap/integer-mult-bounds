# Notice

Apache-2.0 (`LICENSE`). Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

## New in this package

- `code/assemble9.py`: the nine-stage bit invoice of PR #463's `assemble_k.py` (verbatim; its complex half is dropped)
  followed by PR #493's per-supplier outer-assembly loop (verbatim).
- `code/adapt.py`: writes the adapted `audit_parent_k.py` (2 listed edits, each anchor checked to occur exactly once).
- `data/selection9-r480.json`: the nine-stage hosting selection, nominated by PR #442's programme through the vendored
  `emit_k.py --discover` and rediscovered by `verify.py`.
- `code/findings/levels.py` (frame-level register visits). `code/findings/flowlp2.py` (the junk-dimension min-flow LP) and
  `code/findings/piv0.py` (pivot classes) are byte-identical copies of DreamingOfClouds research scripts (Claude Sonnet 5.5 /
  Claude Opus 5.5 via Claude Code), not from a PR; sha256 in `SOURCE.json`.
- `verify.py`, `EXPECTED.json`, `MANIFEST.json`, `SOURCE.json`, `README.md`.

## Vendored, byte-identical (`vendor/`; git blob ids and sha256 in `SOURCE.json`, recomputed by `verify.py`)

From PR #463 (DreamingOfClouds, branch e8-carrier-rekid-r715, head cdf0c1c6540df987467988fd771340670f4136f3):
- `research/e8-r715-eleven-stage-whole/code/{global_k,emit_k,audit_parent_k,audit_hosted_k,hosting_k,bank_routes_k}.py`
  (DreamingOfClouds with Claude Opus 5.5, derived from PR #443 and PR #444 by chafreaky with OpenAI Codex, PR #442 by
  DaysSky with Claude, and PR #386 by Zhihao Chen with OpenAI Codex; lineage per file in `SOURCE.json`);
- `research/e8-r740-replica32/code/{config,bank_routes,tile_m,e8core}.py` and `engines/{moment,base_two_moment,outer}.py`
  (PR #443, chafreaky with OpenAI Codex; the engines are PR #315's, DreamingOfClouds);
- `research/idle-axis-hosting/hosting_core.py` (PR #442, DaysSky with Claude).

## Used from the parents, unchanged

- PR #503 (`research/e8-r480-dead-totals`): the R480 word and its verifier, run as the parent.
- PR #493 (`research/e8-bit-carrier-skeleton`, eumemic): the checkers (`columns_k.cpp` and its headers), the residual
  isometry record, the nine-stage geometry builder (through the parent run) and the cited complex receipts
  (`data/complex-b.json`). Provenance and licences are listed in PR #493's `NOTICE.md`.
