# Notice

Apache-2.0 (`LICENSE`). Prepared by Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance.

- `data/pr390/prefix18.json.gz`, `sink-audit.json`, `prewhite.json` are Dugongue's PR #390 (`research/e8-prefix-restoration/data/`, head 0e790f2), byte-identical (git blobs 51f3ea73, ef2b6f9e, 527a2ea4), Apache-2.0 (`data/pr390/LICENSE-pr390`).
  - `prewhite.json` is used only as a regression target.
  - #390's scripts (`complex-hetero-compose.py`, `root-global.py`, `root-heterobanks.cpp`) were read as data. Their bracket rule and bank assignment are re-implemented in `code/emit.py` and `code/clean.py`. None of #390's scripts were run.
- `data/pr398/signed25.json.gz` and `VALIDATION.json` are Dugongue's PR #398 (`research/e8-signed-prefix/data/`, head c3251c8), byte-identical (git blobs 23a6396d, 3b1a9bb6), Apache-2.0 (`data/pr398/LICENSE-pr398`). `VALIDATION.json` is used only as the control target. #398's scripts (`reconstruct.py`, `complex-compose.py`, `global-template.py`, `outer.py`) were read as data; its bank rule and profile formula are re-implemented in `code/clean.py`. None of its scripts were run. The R781 word carries #376's (applecrusher) helper substitutions.
- `code/bootstrap.py` re-implements #392's (rohanarun) pricing tail, which #398 also uses.
- `complex/gx/gx.py`, `gxcore.py` are by Jacob Sussman (wht-power-saving-lean `9c94857`, Apache-2.0); upstream LICENSE/NOTICE are kept in `complex/`.
- `data/gcert1-e8-r783-far.json.gz` is our #378 word, and `data/bit/bitE8-kernel.json.gz` is our #382 bit word (derived from utcorvusvolat-dotcom's #370). Both are byte-identical.
- `code/engines/*` are PR #315's engines (DreamingOfClouds; eumemic; the #144/#23 lineage), as in our earlier packages.
- `code/e8core.py`, `cxkernel.py`, `cxretime.py`, `cxcheck.py`, `cxop.py` and `layout_bk.py` (DaysSky's B_K rule, #363) are copied unchanged from our `research/e8-far-nine-complex`.
- `code/word.py` and `code/sinks.py` are unchanged from our #394 (`research/e8-clean-padding`); `code/emit.py` is #394's with a `setR` switch for R = 781.
- `data/pr401/selection.json`, `BANK-PATTERNS.json`, `RESULT.json` are Dugongue's PR #401 (`research/e8-response-subspaces/`, head 7844f72: `frames/selection.json`, `architecture/inputs/BANK-PATTERNS.json`, `RESULT.json`), byte-identical (git blobs 6e75d62b, dae63550, fa8bd211), Apache-2.0 (`data/pr401/LICENSE-pr401`). `RESULT.json` supplies #401's bit coarse bound and the b/kappa control. #401's scripts (`frames/reconstruct.py`, `architecture/banks.py`) were read as data; its entrance construction and bank-pattern assignment are re-implemented in `code/entrance.py` and `code/resynth401.py`. None of #401's scripts were run.
- #400 (rohanarun) was read as data; its R781 heterogeneous-bank composition was re-implemented during our exploration but is not part of this package's word (it is superseded by #401's mixed residual banks).
- `code/clean.py` and `data/sinks-e8clean3.json` are our #399 package, run as a control; `code/cxcheck.py` skips #401 entrance shears in its flipped-sign control.
- New here: `code/redesign.py`, `code/search.py`, `code/entrance.py`, `code/resynth401.py`, `data/designs-e8resynth401.json`; `code/sinks.py` gains an optional cached-analysis argument in `find_adv`.
- #352 (`complex_splice.emit`), #363 and #377 (`PROOF.txt`, `global_nine.py`, `RECIPE-9.json`) were read as data only.
