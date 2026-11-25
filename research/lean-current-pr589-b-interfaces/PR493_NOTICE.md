# Notice

Apache-2.0 (`LICENSE`). Prepared by eumemic with substantial Anthropic Claude assistance.

## New in this package

- `code/skeleton/`: the D4 quad-skeleton geometry (`geom.py`), the word builder with source registers as gate
  destinations (`wordkit.py`), the generator (`gen.py`) and an E8 root-line helper (`e8.py`, #370's Hamming
  coordinates and line order).
- `data/skeleton/plan-skB.json` (CP-SAT plan nominated by `discovery/plan.py`), `data/skeleton/d4part-pairs.json`
  (the 5-pair D4 partition, found by `discovery/d4part.py`), `data/bit/bitE8mut-r489.json.gz` (the word),
  `data/eleven/hosting.json` (frozen hosting selection nominated by `discovery/host_select.py` with #442's integer
  programme), `data/eleven/residual-isometries.json` (the frame-zero record of #443's isometry format: every helper of
  this word enters at frame zero).
- `code/bit/independent/relax.py` (generates the relaxed #370 checker), `interface.py` (#425 lemma hypotheses),
  `mutate_mut.py` (word-level mutants and hypothesis controls), `code/bit/mutate_records_mut.py` (record-level
  mutable-source mutants).
- `code/eleven/adapt.py` and the adapted files it checks, `code/eleven/{emit,audit,local_audit}.py` (PR #472's files
  plus 19 listed edits: R = 489, package paths, a `--hosting` argument, one frame-zero entrance instead of eleven).
- `code/eleven/assemble.py`: PR #472's bit invoice and pricing arithmetic with R as a parameter, and its outer
  assembly run once per cited complex supplier.
- `code/cited.py`, `data/complex-b.json`, `verify.sh`, `EXPECTED.json`, `requirements.txt`, `discovery/`,
  `.github/workflows/e8-bit-carrier-skeleton.yml`.

## Vendored, byte-identical (git blob ids in `SOURCE-pr*.json`, checked by `code/provenance.py`)

- **PR #370 (Dylan Crow / utcorvusvolat-dotcom, with Anthropic Claude assistance), commit b7fe9cd:** the independent
  checker `checkword.py` and its controls `mutate.py`; `export_records.py`, `mutate_records.py`, `stage_cohort.py`;
  PR #266's official cohort checkers as generalised there (`legality_h.cpp`, `columns_h.cpp`, NCOPY); nlohmann/json
  (`json.hpp`, MIT licence in its header); `gram_frames.py`; PR #315's engines (`code/pricing/`, DreamingOfClouds);
  the R865 word `data/bit/bitE8-r865.json.gz` (read only for the E8 label table by the geometry scripts); `LICENSE`.
- **PR #381 (DaysSky, assisted with Claude), commit 00765b2:** `columns_k.cpp`.
- **PR #386 (Zhihao Chen / jacklightChen, with OpenAI Codex assistance), commit dd11cf8:** the nine-stage bit geometry
  `code/nine/geometry.py` (parent geometry checked by the eleven-stage audit) and `portable-include/bits/stdc++.h`.
- **PR #436 (eumemic, with Anthropic Claude assistance), commit 8f6b829:** `code/provenance.py`.
- **PR #445 (chafreaky, with OpenAI Codex assistance), commit 40ab91d:** `code/hub/r740-hosted-eleven/code/geometry.py`
  (eleven-stage geometry), `row_bound.py` (orthogonal-cover row bound), `emit.py` and `data/selection.json` (used
  unchanged for the PR #445 control).
- **PR #451 (chafreaky, with OpenAI Codex assistance), commit f3a3815:** `code/hub/r740-hosted-rank149/`: its
  eleven-stage bit emitter (byte-identical to PR #445's), frozen selection, R740 rank149 word and isometries
  (PR #451 control).
- **PR #472 (chafreaky, with OpenAI Codex assistance), commit 259c684,** and files its branch carries unchanged:
  - `code/hub/e8-r715-whole-hosted/`: PR #472's eight-replica pooled emitter, independent audit, local projector
    audit and assembly (the originals of the adapted files), its R715 word, isometries and frozen hosting (used
    unchanged for the PR #472 control);
  - `code/hub/e8-r740-replica32/`: PR #443 (chafreaky): `bank_routes.py`, `tile_m.py`, `e8core.py`, the R740 rank138
    word and its isometries (PR #445 control); PR #315's engines (DreamingOfClouds) in `code/engines/`;
  - `code/hub/idle-axis-hosting/hosting_core.py`: PR #442 (DaysSky, with Anthropic Claude assistance).
- **Receipts (`data/complex/`):** `EXPECTED.json` of PR #484 (DreamingOfClouds, 035845c), PR #471 (Dugongue,
  56b3da6), PR #458 (chafreaky, 44e9eae), PR #448 (higherbeing, 359022b), and of the bit-bound frontier PRs #483
  (Dugongue, 3738c3c), #473 (rohanarun, c7590f1) and #478 (Dugongue, bea1d52).

The repository-level files `certificates/joint-dual-kappa.json`, `certificates/joint-dual-validation.json` and
`research/joint-dual/SOURCE.json` in this branch are byte-identical to rohanarun's PR #318 (a45747d). They repair
stale root-file pins so the repository's joint check passes; #417, #436 and #439 carry the same repair.

## Cited, not rebuilt

Complex coarse savings in `data/complex-b.json`, each bound to its PR's `EXPECTED.json` by `code/cited.py`:
PR #484 (primary; draft, conditional on its Lemmas A and G), PR #471 (the complex supplier of #473, #478 and #483),
PR #458 (the complex supplier of #472) and PR #448 (information only; disputed cross-copy split). No complex
construction is rebuilt here.

## Ideas used

PR #425 (Zhihao Chen, with OpenAI Codex assistance): the scalar-interface lemma that permits source registers as
gate destinations when the full-frame cleanup restores them. PR #463 (DreamingOfClouds, with Claude Opus 5.5): the
carrier bound (three registers leave a source's line). PR #433 (icekylinx): source rows written on the bit side.
PR #442 (DaysSky): idle-axis hosting of whole residuals. Jacob Sussman introduced the E8 unit.
