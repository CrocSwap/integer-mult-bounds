# Notice

Apache-2.0 (`LICENSE`, copied from #493's package). Prepared by eumemic with substantial Anthropic Claude
assistance.

## New in this package

- `code/gen_p3.py` (the generator of the punctured word: the L3 skeleton of #543 restricted to the live lines, the
  pseudo-target totals, the phase-A mini-nodes and extra carriers), `code/pwordl.py` (word builder for a live subset
  of the 120 lines; output in the bitE8/1 layout with the `ports_geom` and `punctured` fields introduced by #545),
  `data/bitE8mut-p111.json.gz` (the word), `data/punct.json` (its frozen parameters), `discovery/choose.py` and
  `discovery/search.py` (the nomination of P and of the parameters; not run by `verify.sh`).
- `code/gen_p3.py` carries `derive`, `ex_part` and `plan_thirds` from #543's `code/gen_l3.py` (eumemic), and
  `data/plan-l3.json` is #543's CP-SAT plan, unchanged. `code/nodeopt.py`, `code/planio.py`, `code/mutants.py`,
  `code/mutrec_b.py` and `code/provenance.py` are #543's files, unchanged.
- `code/xcheck_p.py`: #543's independent checker `code/xcheck.py` with nine listed edits for v <= 120 live labels
  (root-line enumeration of the lattice, frame closure and target frames over the live labels) and a new part T (the
  frame and COPY rank of every retained total at the scatter, and whether it is the hyperplane of a punctured line).
- `code/mutants_p.py` (punctured-design controls), `code/adapt9p.py` (#510's nine-stage files parameterised for
  v <= 120 and any copy ranks, the way #545's `adapt.py` parameterises #493's eleven-stage files), `code/cited.py`,
  `code/receipt_kappa.py`, `code/summary.py`, `verify.sh`, `EXPECTED.json`, `DEPENDS.json`, `requirements.txt`,
  `data/complex-b.json`, `data/selection9-p111.json` and `data/hosting11-p111.json` (frozen nominations of #442's
  hosting programme, rediscovered by `verify.sh`), `.github/workflows/e8-bit-p111.yml`.

## Vendored, byte-identical (git blob ids in `SOURCE-pr*.json`, checked by `code/provenance.py`)

- **PR #510 (DreamingOfClouds, with Claude Opus 5.5 via Claude Code), commit 64edee1** (`vendor/pr510/`): the same 19
  files as #543's package (#510's nine-stage chain with the files it vendors from #463, #443, #442 and #315, and #503's
  R480 word). Their notices are listed in #543's NOTICE and in the files.
- **PR #545 (DreamingOfClouds, with Claude Opus 5.5 via Claude Code; draft), commit 376426f** (`vendor/pr545/`):
  `code/adapt.py` and `code/punct_cfg.py`, run unchanged on this package's word; `data/bitE8mut-v111-r489.json.gz`,
  `data/hosting-v111-r489.json` and `EXPECTED.json` (a control).
- **PR #548 (Dugongue), commit 66dbc2b** (`data/complex/pr548/`): `EXPECTED.json` and `evidence/EXACT-ASSEMBLY.json`.
- **PR #544 (chafreaky, with OpenAI Codex assistance), commit 4858bb3** (`data/complex/pr544/`): `EXPECTED.json` and
  the Linux exact-assembly receipt.
- **PR #535 (icekylinx, with GPT-6 Astra assistance), commit 8b758a1** (`data/complex/pr535/`): `EXPECTED.json` and
  `evidence/audit/EXACT-ASSEMBLY-PR493.json`.

## Used from main, unchanged (pinned in `DEPENDS.json`)

- `research/e8-bit-carrier-skeleton` (PR #493, eumemic): the skeleton modules and D4 partition the generator imports,
  #370's checker (run here in #545's v <= 120 form), the official cohort checkers, `gram_frames.py`, the record
  exporter, the geometries and the eleven-stage chain that #545's `adapt.py` parameterises, #442's hosting programme,
  the R489 word, the control receipts and #315's engines.
- `research/direct-delivery504-global/EXPECTED.json` (PR #531, icekylinx): its complex b and kappa.

## Cited, not rebuilt

Complex coarse savings in `data/complex-b.json`, each bound to its PR's receipt by `code/cited.py`: PR #548 (primary;
open), PR #544 and PR #535 (open), PR #531 (merged), and PR #484, #471 and #458 (controls).

## Ideas used

- PR #545 (DreamingOfClouds): the punctured-star unit. Nine lines are neither sources nor targets; each retained total
  is a pseudo-target that reads what the removed target would read, at frame rank 7, so the decoder constant is 63;
  the rank-mass identity with v and the decoder constant as parameters; the parameterisation of the hub chain.
- PR #543 (eumemic): the R420 L3 skeleton with keepers read by targets and rewritten in phase B.
- PR #493 (eumemic), PR #503 and #510 (DreamingOfClouds), PR #425 (Zhihao Chen / jacklightChen), PR #370 (Dylan Crow),
  PR #472, #445, #443 (chafreaky), PR #442 (DaysSky), PR #463 and #315 (DreamingOfClouds), PR #386 (Zhihao Chen): the
  skeleton, the scalar-interface lemma, the format, and the pricing pipelines.
- PR #523 (icekylinx): the puncture pattern on the complex side, cited by #545.
- Jacob Sussman introduced the E8 unit.
