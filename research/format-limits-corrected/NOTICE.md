# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from
the repository root).

## New in this package

Everything under `scripts/` and `data/` except `data/vendor/`, plus `README.md`, `verify.sh`, `SOURCES.json`,
`DEPENDS.json`, `requirements.txt` and `MANIFEST.sha256`.

## Vendored, unchanged (git blob ids in `SOURCES.json`, checked by `scripts/provenance.py`)

- **#555 (eumemic), commit 65a6bc1**: the p111 bit word `bitE8mut-p111.json.gz` and its `EXPECTED.json`.
- **#569 (DominikScholz), commit 1424da8**: the width-7 and four-cold provider words (`FULL-WORD.json.gz`).
- **#571 (DominikScholz), commit b7bdc5a**: the combined-eight-local provider word.
- **#568 (jeremykothe2), commit 71c99ac**: `research/complex-multicold/data/PLAN.json`, stored gzip-compressed (the
  blob id is of the decompressed file).
- **#543 (eumemic), commit 2065fe4**: `research/e8-bit-r420/EXPECTED.json`.
- **#545 (DreamingOfClouds), commit 376426f**: `research/e8-punctured111-star/EXPECTED.json`.

## Other inputs

- `data/toys/sol_p3_cone_R16.json`: the p = 3 paired-cube program (h = 6, v = 8, R = 16) in the gcert/1 format of Jacob
  Sussman's checker, the same toy instance as #446's.
- `data/prices/pr569-provider-calls.json`: the 72 (time, provider) pairs of #569's `research/larger-gain/global/width7/
  PLAN.json` (blob id recorded in the file).

## Used from main, unchanged (pinned by sha256 in `DEPENDS.json`)

- #531 (icekylinx):
  - the exact Clifford compiler `research/direct-delivery504-global/vendor/clifford/clifford_exact.py`;
  - the word helpers `vendor/gk/gk_word.py` and `gk_common.py`;
  - the word `evidence/local/FULL-WORD.json.gz`;
  - the geometry `inputs/hamming/PROTOTYPE.json`.
- #523 (icekylinx): the hosting windows `research/punctured112-global/inputs/ASYNC112-PLAN.json`.
- #510 (DreamingOfClouds): `research/e8-r480-nine-stage/EXPECTED.json`.
- The census anchors (`data/census/anchors.json`) cite, read-only:
  - the upstream paper (`upstream/build/sections/*.tex`);
  - #493's checkers (eumemic and contributors);
  - #509 / #516's Lean files (DreamingOfClouds);
  - #442's hosting proof (DaysSky);
  - #130's general frame lemma note (icekylinx);
  - the five-stage bank files (#276 lineage);
  - the maintainer's review documents.

## Results and constructions this package builds on (credit)

**Interfaces, lemmas and checkers:**

- the upstream paper (`upstream/build/sections`);
- **#130** (icekylinx): the general Clifford frame lemma for arbitrary binary subspaces;
- **#370** (utcorvusvolat-dotcom): the first E8 bit word and its checker;
- **#386** (jacklightChen): compressed windows;
- **#425** (jacklightChen): the mutable-basis interface and scalar-interface lemma;
- **#433** (icekylinx): split centres;
- **#442** (DaysSky): idle-axis whole-residual hosting and its stream model;
- **#446** (DreamingOfClouds, open): Theorems A–C, used as premises;
- **#458** (chafreaky): the one-helper-per-family rule;
- **#493** (eumemic): the bit carrier skeleton, checkers and outer assembly;
- **#509 / #516** (DreamingOfClouds): Lemmas G and A in Lean;
- **#514** (Dugongue): the repeated-axis identities C_v² = X_v.

**Words and pipelines read by the checks:**

- **#510** and **#545** (DreamingOfClouds);
- **#543** and **#555** (eumemic);
- **#523** and **#531** (icekylinx): the punctured 112-port complex unit and direct delivery;
- **#568** (jeremykothe2);
- **#569** and **#571** (DominikScholz).

**Lineage the measured words build on (credited, not read by any script):**

- **#535** (icekylinx): post-centre kernels;
- **#552** (Dugongue): the static44 harness lineage of the complex words;
- **#558** and **#564** (eumemic): rank-5 pivots and cold kernels;
- **#588** (jeremykothe2): frame coalescences on the #569 regime (cited in C.8, not reproduced).

**Split-residual hosting:**

- **#448** (higherbeing): the cross-copy split-residual construction;
- **#451** (chafreaky): its trace obstruction.
