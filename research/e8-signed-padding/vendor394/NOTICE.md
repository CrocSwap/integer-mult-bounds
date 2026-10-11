# Notice

Apache-2.0 (`LICENSE`). Prepared by Chafik Boukhalfa (chafreaky) with substantial Anthropic Claude assistance.

- `data/pr390/prefix18.json.gz`, `sink-audit.json`, `prewhite.json` are Dugongue's PR #390 (`research/e8-prefix-restoration/data/`, head 0e790f2), byte-identical (git blobs 51f3ea73, ef2b6f9e, 527a2ea4), Apache-2.0 (`data/pr390/LICENSE-pr390`).
  - `prewhite.json` is used only as a regression target.
  - #390's scripts (`complex-hetero-compose.py`, `root-global.py`, `root-heterobanks.cpp`) were read as data. Their bracket rule and bank assignment are re-implemented in `code/emit.py` and `code/clean.py`. None of #390's scripts were run.
- `complex/gx/gx.py`, `gxcore.py` are by Jacob Sussman (wht-power-saving-lean `9c94857`, Apache-2.0); upstream LICENSE/NOTICE are kept in `complex/`.
- `data/gcert1-e8-r783-far.json.gz` is our #378 word, and `data/bit/bitE8-kernel.json.gz` is our #382 bit word (derived from utcorvusvolat-dotcom's #370). Both are byte-identical.
- `code/engines/*` are PR #315's engines (DreamingOfClouds; eumemic; the #144/#23 lineage), as in our earlier packages.
- `code/e8core.py`, `cxkernel.py`, `cxretime.py`, `cxcheck.py`, `cxop.py` and `layout_bk.py` (DaysSky's B_K rule, #363) are copied unchanged from our `research/e8-far-nine-complex`.
- New here: `code/word.py`, `code/sinks.py`, `code/emit.py`, `code/clean.py` and `data/sinks-e8clean.json`.
- #352 (`complex_splice.emit`), #363 and #377 (`PROOF.txt`, `global_nine.py`, `RECIPE-9.json`) were read as data only.
