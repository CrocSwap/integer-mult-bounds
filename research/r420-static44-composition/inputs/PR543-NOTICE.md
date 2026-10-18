# Notice

Apache-2.0 (`LICENSE`, copied from #493's package). Prepared by eumemic with substantial Anthropic Claude
assistance.

## New in this package

- `code/gen_l3.py` (the generator), `code/nodeopt.py` (bill-aware realization of the block nodes), `code/planio.py`
  (plan loader), `data/plan-l3.json` (the CP-SAT plan, nominated by `discovery/planL3.py` and `discovery/planL3b.py`)
  and `data/bitE8mut-r420.json.gz` (the word).
- `code/xcheck.py` (independent exact replay and interleaved-interface audit), `code/mutants.py` (word-level mutation
  controls), `code/mutrec_b.py` (record-level phase-B mutants, adapted from #493's `mutate_records_mut.py`).
- `code/adapt11.py` (R-specific copies of #493's eleven-stage audit files; the same six edits #503's `adapt.py`
  makes for R = 480).
- `code/provenance.py` (adapted from #493's, itself from #381's), `code/cited.py`, `code/summary.py`, `verify.sh`,
  `EXPECTED.json`, `DEPENDS.json`, `requirements.txt`, `data/complex-b.json`, `data/selection9-r420.json` and
  `data/hosting11-r420.json` (frozen nominations of #442's hosting programme, rediscovered by `verify.sh`),
  `.github/workflows/e8-bit-r420.yml`.

## Vendored, byte-identical (git blob ids in `SOURCE-pr*.json`, checked by `code/provenance.py`)

- **PR #510 (DreamingOfClouds, with Claude Opus 5.5 via Claude Code), commit 64edee1** (`vendor/pr510/`):
  - `e8-r480-nine-stage/code/assemble9.py` (#463's nine-stage invoice and #493's outer-assembly loop),
    `code/adapt.py`, `data/selection9-r480.json` and `EXPECTED.json`;
  - the files #510 vendors from PR #463 (DreamingOfClouds; head cdf0c1c):
    - `e8-r715-eleven-stage-whole/code/{global_k,emit_k,audit_parent_k,audit_hosted_k,hosting_k,bank_routes_k}.py`,
      derived from PR #443 and PR #444 (chafreaky, with OpenAI Codex assistance), PR #442 (DaysSky, with Claude) and
      PR #386 (Zhihao Chen, with OpenAI Codex assistance);
    - `e8-r740-replica32/code/{config,bank_routes,tile_m,e8core}.py` (PR #443, chafreaky) and `engines/` (PR #315's
      moment engines, DreamingOfClouds);
    - `idle-axis-hosting/hosting_core.py` (PR #442, DaysSky, with Anthropic Claude assistance);
  - `e8-r480-dead-totals/data/bitE8mut-r480.json.gz`: PR #503's R480 word (DreamingOfClouds), as carried by #510's
    branch.
- **PR #535 (icekylinx, with GPT-6 Astra assistance), commit 8b758a1** (`data/complex/pr535/`): `EXPECTED.json` and
  `evidence/audit/EXACT-ASSEMBLY-PR493.json` (the same blobs as at 25f9b7c).

## Used from main, unchanged (pinned in `DEPENDS.json`)

- `research/e8-bit-carrier-skeleton` (PR #493, eumemic): the skeleton modules and D4 partition the generator imports;
  #370's checker and its relaxed copy; the official cohort checkers (#266 as generalised by #370; #381's
  `columns_k.cpp`); `gram_frames.py`; the record exporter and mutants; #386's nine-stage and #445's eleven-stage
  geometry; #472's eleven-stage emitter, audit and assembly as adapted there; #442's hosting programme
  (`discovery/host_select.py`); the R489 word; the control receipts. Provenance and licences of those files are in
  that package's `NOTICE.md`.
- `research/direct-delivery504-global/EXPECTED.json` (PR #531, icekylinx, with GPT-6 Astra assistance): its complex b
  and κ.

## Cited, not rebuilt

Complex coarse savings in `data/complex-b.json`, each bound to its PR's receipt by `code/cited.py`: PR #535 (primary;
open), PR #531 (merged), and PR #484, #471 and #458 (controls). No complex construction is rebuilt here.

## Ideas used

- PR #493 (eumemic): the D4 quad skeleton with sources as carriers.
- PR #503 (DreamingOfClouds): the nine totals on dead registers, hosted by the last eligible register.
- PR #510 (DreamingOfClouds): the nine-stage pricing of these words. DreamingOfClouds' LP in #493's thread gives 480
  under the hypothesis this word avoids.
- PR #425 (Zhihao Chen / jacklightChen, with OpenAI Codex assistance): the scalar-interface lemma.
- PR #535's `PR510-MUTABLE-SOURCE-CARRYOVER.md` (icekylinx): the role-independent bit-side pullback argument.
- PR #370 (Dylan Crow / utcorvusvolat-dotcom): the bitE8/1 format, its independent checker and the decoder totals.
- PR #472, #445, #443 (chafreaky), PR #442 (DaysSky), PR #463 and #315 (DreamingOfClouds), PR #386 (Zhihao Chen): the
  pricing pipelines.
- Jacob Sussman introduced the E8 unit.
