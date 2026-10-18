# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- Setting, notation, peeling, the DP / LP / Pencil / triple rules and the root-swap family: the author's **#2816**; Basis Lemma, direction list, Lemma S66 and the Parity Lemma: the author's **#2826**; both build on **#2338**, **#2277**, **#2724** (ours). The model is **#1224** (joaqcoo; one-sided nine-term decoders as overcomplete representations). **#2784** (ours) is cited for case (c).
- The gain law cited in the README is philippeVV's (Discussion #1587, follow-up 6).
- Tools: Python (standard library), `numpy`, `scipy` (`symlp.py`, as in #2816); a C compiler for `s6x.c` and `k3.c`. No SAT solver.
- No file is copied from another contributor. `checks/gen.py` and `checks/manifest_check.py` are copies of the author's files in #2826; `checks/dpX.py` and `checks/symlp.py` are copies of the author's files in #2816; all other scripts are the author's working-card scripts, with absolute paths removed where noted in `SOURCES.json`.
- `checks/gen3.py` and `checks/k3.c` are the independent second implementation (a separate working card of the author: own coordinates, labels, direction derivation, group, flat enumeration, qualifier test and refinement; no code shared with the first implementation).

## New in this package

Everything under `research/one-sided-excess-three/`: `README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `checks/`, `data/`, `evidence/logs`.
