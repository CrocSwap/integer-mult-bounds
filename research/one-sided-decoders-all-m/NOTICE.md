# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- Model and notation: **#1224** (joaqcoo; one-sided nine-term decoders as overcomplete representations), the author's **#2338**, **#2277**, **#2724** (dense pairing, Theorem R, case (b) at `m = 9`), with **#1180**, **#1633**, **#1815 / #1212** cited from their statements, not re-derived.
- The gain law cited in the README is philippeVV's (Discussion #1587, follow-up 6).
- Imported merged results (README §2): #1212 Theorem 1 (Gram realisation), #2338 Theorem R (dense pairing). Classical: Bourbaki, *Groupes et algèbres de Lie*, Ch. V §3.3 and VI §1.7 (stabilisers of points are parabolic), used in the proof of C3.
- Tools: Python (standard library), `numpy`, `scipy` (HiGHS), `sympy`; a C compiler for `lemmaN.c`, `ncount*.c`, `mu76.c`. No SAT solver.
- No file is copied from another contributor. `checks/lib.py, common2.py, frames_data.py, manifest_check.py` come from the author's package `research/nine-term-outside-colspace` (#2724);
  all other scripts are the author's working-card scripts (cards OS-CHARGE, OS-CHARGE2, SMALL2), with absolute paths removed and the E8 frame loaded from `data/p104_frames.json`.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `checks/check_logs.py, g78.py, flats_classify.py, symcheck.py, cover761.py` (the latter from the auditor's check of the (7,6,1) cover shape), `rootswap_audit.py` (moved from `audit/`), the extra `k = 3, 4, 5` loop at the end of `checks/rootswap.py`, `data/`, `evidence/logs`.
