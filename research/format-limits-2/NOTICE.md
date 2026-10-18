# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from
the repository root).

## New in this package

Everything under the four section directories except `inputs/` and the existing logs and notes under `evidence/`
(which are shipped unchanged apart from the path removal named in `SOURCES.json`), plus `README.md`, `verify.sh`,
`scripts/provenance.py`, `SOURCES.json`, `requirements.txt` and `MANIFEST.sha256`.

## Vendored, unchanged (git blob ids in `SOURCES.json`, checked by `scripts/provenance.py`)

Files of these PRs (commit in `SOURCES.json`), stored verbatim or gzip-compressed:

- **#531** (icekylinx): `PROTOTYPE.json` and `PACKET-PROGRAMS.json` (the direct-delivery geometry and packet programs).
- **#555** (eumemic): `research/e8-bit-p111/EXPECTED.json` (the bit invoice, row P2).
- **#595** (DreamingOfClouds): `a5_scope_multipliers.py`, `skel.py`, `cert.py`, `report.py` (E1 re-runs them unchanged).
- **#622** (jeremykothe2): the verifier `coupled_frames_base.py` (S4); the #622 / #623 ck and jp8 provider words are vendored from their audit copies inside #656.
- **#626** (chafreaky): `PLAN.json`, README literal, `hpe_audit_local.py`, `GENERATED-IDENTITY-CONTROLS.json`.
- **#635** (jeremykothe2), **#646** (jeremydiviney), **#649** (jeremykothe2): `PLAN.json` profiles (row P3).
- **#645** (icekylinx): `PLAN.json` and `FULL-WORD.json.gz` of the gauge44 word (G1, G2).
- **#656** (jeremykothe2): `PLAN.json`, `FULL-WORD.json.gz`, the audit copies of the ck and jp8 words (C1-C3, Y, F, O rows).
- Three files of main at the base commit: `upstream/build/sections/03-motifs.tex`, `04-swap.tex`, `notes/general-clifford-frames.tex`
  (the upstream paper and the frame notes; line anchors of S2-S4).

## Rebuilt, not files of any PR

Canonical words rebuilt locally (the gauge44 word of #656 and the ck word of #626); each is pinned by the hashes the PR itself
publishes (`SOURCES.json`, `derived`).

## Results and constructions this package builds on (credit)

- **#595** (DreamingOfClouds): the format ceiling, census and lemmas that rows E1, E2, P1 and S1-S4 correct or extend; **#446** (DreamingOfClouds, open): Theorem C.
- **#593, #591, #617, #622, #623** (jeremykothe2): hyperplane-ended helpers and the K-triangle skeleton (G3, O2).
- **#604** (DreamingOfClouds): cold factory-scratch helpers (G1, G3).
- **#626** (chafreaky): the owner repair whose profile the invoice calculus prices.
- **#645** (icekylinx): Gauge44 (G1, G2); **#646** (jeremydiviney): signed-root K480 (G1, O2); **#649, #656, #659, #664, #676** (jeremykothe2): the gauge44 lineage and the frontier words.
- **#531** (icekylinx), **#555** (eumemic): the 504-helper direct delivery and the punctured bit unit.
- **#620** (GamingPuzzled): the E8 decoder floors (the complex P112 decoder of cost 64 is theirs, D1; bit P111 63 is theirs, D3); **#631**: the star-ratio puncture bound 63/111 (D3); **#661** (yuj1r0): R420 phase-B frames at fixed order (F1);
  **#665** (Mister-Meeseeks): the rehosting boundary (F2); **#589** (DreamingOfClouds): the bit transport cited by #649.

## Overlap check with recent swarm PRs

- **#698** (thakrarsagar): exact certificate that the selected CK supplier's B-phase frames minimise the paid moment over all reassignments preserving circuit, gate order and end-of-B frames. Cited in P5, F1 and F2; it covers the CK B-phase part of their fixed-order frame statements (not jp8, not the A phase); the rest of those rows is distinct.

- **#703** (Mister-Meeseeks): asymmetric Hurwitz E8 copy cost exactly 10 (scoped negative on #620's quaternionic lines). Related to D1/D3, not a duplicate of any row.
- **#705** (littleBro): determinant obstruction for rank-homogeneous register paths. Related to S2 and F2, not a duplicate.
- **#711** (thakrarsagar): R420 adjacent A swaps force both frames (bit side). Related to F2 (time shifts) and #661, not a duplicate.
- **#683** (Mister-Meeseeks): partial K/M face bypass needs four carriers. Related to appendix item 2 (packet reads), not a duplicate of any row.
- **#687** (cbethin): certifies a single-read relocation neighbourhood in one K-triangle of the #622 word. Related to O2, not a duplicate.
