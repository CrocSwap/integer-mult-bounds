# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- This package is the closures-only follow-up of the author's #2338 (*Decoder floors are tight in the frontier format*, open, the parent); the model, notation and the theorems it extends (Theorem R, Theorem P) are #2338's, which in turn build on #446, #595, #1590, #2111, #2125, #2162, #2228, #2244, #2277 (author's own).
- **Direct puncture predecessors** (cited from their PR statements; not re-derived; different decoder classes): **#631** (vectorsss), **#875** (mightyOil), **#939** (RossRichardson), **#1171** (3xcalibur-tech): E8 star label-decoder puncture exclusion through `p = 119` (the star-copy ratio `63/111`); **#1020** (woklerx), **#1521** (bbMisk), **#1180** (woklerx), **#1609** (ToikY): general / one-sided decoders at `p ≤ 27`; **#1212** (burntout76), **#1389**, **#1399**, **#1419**, **#1425**, **#1292**: global / local rank-8 gauge rigidity of the masked system on P112, P120, P111, all P104 units, P105-P110 (cited where rigidity of the rank-8 realisation is needed; not re-proved); **#1187 / #1455 / #1304 / #1614**: fixed P104 / A8 decoders on specific punctures; **#968** (themilkman216): P104 unit and the 8-term floor. Related swarm work cited only: #2582, #2536, #2515 (ywz65), #2450 (thakrarsagar), #1633 (bbMisk), #1224 (joaqcoo), #2293, #2311, #2379 (audits of the author's earlier work).
- Tools: kissat 4.0.4 (SAT; never CaDiCaL); `drat-trim` (Marijn Heule and Nathan Wetzler), not vendored, optional.
- No file is copied from another contributor. `lib/*.py`, `scripts/provenance.py`, `data/h4_F1.json` and `LICENSE` are the author's own files from the package of #2338 / #2277; `evidence/` holds the author's working-card scripts and logs, copied unchanged.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `checks/c1, c2, c4`, `sat/e7hit.py`; `data/logs`, `data/states`, `evidence/` are exports of the author's working cards (PUNCT5, PUNCT-MID, PUNCTTHEORY, STRAYS-H10, H11) taken on Oct 15, 2026.
