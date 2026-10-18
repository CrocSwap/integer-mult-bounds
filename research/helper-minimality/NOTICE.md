# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## New in this package

`README.md`, `verify.sh`, `scripts/provenance.py` (adapted from #717), `SOURCES.json`, `requirements.txt`, `MANIFEST.sha256`, everything under `checks/` and
`cards/` (the swarm's card scripts, path edits only as listed in the README), `evidence/` (card notes, local paths removed) and the stored
pre-read pair table `inputs/derived/pairs.json.gz`.

## Vendored, unchanged (git blob ids in `SOURCES.json`, checked by `scripts/provenance.py`)

- **#799** (jeremykothe2), commit in `SOURCES.json`: `independent/audit_local.py` (the verifier AL), `code/audit_allcold.py`, `code/emit_allcold.py`, `construction/construct_gauge_xcentre.py` (line anchors of the cut hypothesis).
- **#635** (jeremykothe2): `hpe_emit_local.py` of the cold14 st2 code, taken from the copy on main (`research/complex-sw4-frame8/local/`); its sha256 equals the pin in #799 `construction/INPUTS.json`.
- Main at the base commit: `upstream/build/sections/03-motifs.tex` (spec schedule lines 78-83).

## Rebuilt words and derived inputs (not files of any PR)

The #656 canonical and layered words and the #799 X4 canonical and full words are rebuilt locally from the PRs' construction code and pinned by
the hashes the PRs publish (`SOURCES.json`, `derived`). `inputs/ledger_helpers.csv` is the #656 helper ledger (byte-identical modulo CRLF to
`research/format-limits-2` #717, `s3-4-census-gauges/evidence/C1/ledger_helpers.csv`).

## Results and constructions this package builds on (credit)

- **#717** (DreamingOfClouds, open) and **#595** (DreamingOfClouds, merged): the census of the helper sites (S1, S3, S4), the invoice and the format lemmas; rows F3-F5 of #717 record the value-side facts that the frame bounds here complement.
- **#656, #659, #664, #799** (jeremykothe2): the gauge44 layered and no-triangle lineage, entrance promotions and the X4 joint exchange whose words are analysed; **#645** (icekylinx): Gauge44; **#622, #623** (jeremykothe2): the K-triangle skeleton and the ck/jp8 providers; **#635** (jeremykothe2): the emitter and cold14 pipeline.
- **#741, #685** (chafreaky): the eight B-frame coalescences and the entrance promotions in #799's lineage.
- **#869, #870** (jeremykothe2): the eight block-0 hybrid deliveries (B2 cites card B169, not #869, for "legal only for 450..457") and the U8 owner-controller word (not analysed here).
- Lawler, Management Science 19(5):544-546 (1973), for the backward rule; Boyar and Find 2013 for the cancellation-free contrast.

## Overlap check with recent swarm PRs

- **#698** (thakrarsagar): the selected CK supplier's B-phase frames are optimal at fixed boundaries. Related to the frame lattice used here, but a different object: fixed gate order with exact end-of-B frames (CK B frames), against the order-free L2/L3 bounds here on helper copies.
- **#719**: rank-two obstruction for the 78 CK cleanup pairs. Related to the pair conflicts (L4) and to the multiset-changing merges of open problem 2; a different object (CK cleanup pairs, not helper copies), no row duplicated.
- **#705** (littleBro): determinant obstruction for rank-homogeneous register paths. Related to the cut/centre count (K1) only loosely: a different model (Clifford words) and a different argument.
- **#687** (cbethin) and **#683** (Mister-Meeseeks): a K-triangle relocation neighbourhood and a four-carrier bound for partial K/M face bypass. Different objects, no row duplicated.
- **#716** (thakrarsagar): R420 target pairs save XORs; not the same objects (the register ids 716..727 in row B1 are bridge registers, not PR numbers).
