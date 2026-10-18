# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits (prior work this package stands on)

- **#446** (Theorem C; closed, not merged): the cost formula and exactness model, carried by the merged **#595** (FL C.6): the pairing model and the window table.
- **#717**: the provenance / manifest pattern (`checks/provenance.py` follows it) and the complex E8 decoders.
- **#1590** (`research/root-unit-decoder-lemmas`, merged): Lemma A (T ≤ 2), the lift identity Lemma B, ERR1. The Lean file formalises the rank argument behind Lemma B; the step-0 manifest check and the PASS/FAIL style of `verify.sh` follow that package.
- **#2111** (pending): the three-total model and lemmas, the sharp example `tied_min`, the configurations in `data/` (copies), `lib/kit.py`, `lib/satlib.py`, `c/enumall.c`. This package asks and answers a different question about the same objects and is self-contained; it does not depend on #2111 being merged.
- **#2031** (pending): the DRAT certificate of the D5 CNF of #1590, cited as context, not duplicated.
- **#2125** (pending): the T² threshold for root-unit decoders, the context for why characteristic 2 matters.
- Our own swarm working cards of 2026-10-14 (the `KPR4-T3` struct card: tracks on CR2, the map φ, jets, the jetfail search, and the Lean project), shipped verbatim in `evidence/PROOF-working-notes.md`.

## New in this package

`README.md`, `verify.sh`, `requirements.txt`, `MANIFEST.sha256`, `checks/*.py` (written for this package; they re-implement the checks of the working scripts in exact arithmetic with fixed seeds), `data/tied_min_B.json`, `data/cr2_realisations.json`, `scripts/make_data.py`, and `lean/`.

## Adapted from our earlier work

- `lib/kit.py`, `lib/satlib.py`, `c/enumall.c`, `data/*.json` (configurations): unchanged copies from #2111 (themselves from the working cards).
- `lib/cr2.py`, `gr.py`, `phi.py`, `gen.py`, `tangent.py`, `jet2.py`, `col.py` and `scripts/t*.py`, `tied_min_jet_cert.py`, `verify_cr2.py`: the working scripts of the struct card; only the import / data paths were changed (and `t4.py`, `t18.py`, `t22.py` write their output to the current directory).
- `data/jf0..2.json`, `data/tm_noncr2.json`: outputs of those scripts.
