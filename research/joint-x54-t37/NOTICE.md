# Attribution and license

New composition, provider rebind, adapted preparation and upper-bound scripts, and packaging by
Rohan Arun, with substantial AI assistance (Claude). New work is under Apache-2.0.

- **X54 slot.** The width-neutral eighth triangle-hybrid slot X54/E589 (holders 335, 367) is Jeremy Kothe's
  (jeremykothe2) `RECIPE-X54-ends7.json` from PR1130. The edits and frames are unchanged; only the base-word
  binding is new.
- **Builder and controls.** `vendor/barch/build_tri.py` and `vendor/barch/run_controls.py` are NewBArch's
  standard-library triangle-hybrid builder and controls, copied byte-for-byte from
  `research/gauge44-slots/construction/barch` (sha256 `0fba65b3…` and `42639bf6…`).
- **Base word.** The joint-entrance k8 word, its 27 entrance controls, native replay and local audit are from
  PR1148 (Thomas DiFiore/Codex) and its full local ancestry. They are used unchanged from PR1169's pinned
  `upstream-layout.tar.gz`.
- **T37 owner map and admission.** The T37 owner map, pattern flow, parent geometry, literal construction and
  strict admission tools are PR1169's (Rohan Arun/Codex), building on Ali Romman/Codex PR1129 (integer flow,
  matching decomposition and T37 audit) and PR1131's wave order. They are reused unchanged from the sibling
  package `research/three-demotions-t37-composition` (pinned in `SOURCE-PINS.json`).
- **Adapted scripts.**
  - `prepare_x54.py` adapts PR1169's `prepare.py`: the provider plan becomes an input, and the baseline label
    changes.
  - `all_t_bound_x54.py` adapts PR1148's `k8-joint-entrances/independent/all_t_bound.py`, itself from
    jon314159's PR942 with Chafik Boukhalfa's PR795/890 dual prices. Only the pinned plan and the source-root
    argument change.
- **Bit supplier.** The PR589 bit supplier is unchanged.

All original notices, licenses and AI disclosures in the cited packages are retained. This package does not
claim authorship of any of those components.
