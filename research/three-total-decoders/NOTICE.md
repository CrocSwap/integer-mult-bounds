# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits (prior work this package stands on)

- **#446** (Theorem C; closed, not merged): the cost formula and exactness model; **#595** (FL C.6): the pairing model and the window table; **#717**: the provenance/manifest pattern of `scripts/provenance.py` and the complex E8 decoders; **#1590** (`research/root-unit-decoder-lemmas`, merged): Lemma A (T ≤ 2), the lift identity Lemma B, ERR1, the D5 CNF; `checks/expect.py` and `scripts/provenance.py` are adapted from that package. **#2031** (pending): the DRAT certificate of the D5 CNF, cited, not duplicated.
- Swarm work used, all from our own working cards of 2026-10-13/14: the second-prover card `KPR4-T3/PROOF.md` (L1–L8, Theorem P), the `fprime` card (Theorems M1, U, MCC, tied_min, SCC/Peel), fleet workers S1 (matroid route, TU-signability, gadget, aff14), S2 (F2S exchange route, PP, 4095 sub-configurations), S3 (adversary search), and the `g1` card (joint signability, counterexamples, Hesse runs). Their notes are shipped verbatim in `evidence/`.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `requirements.txt`, `MANIFEST.sha256`, `c/brutetu.c`, `lib/kit.py`, `lib/satlib.py`, `scripts/make_lifts.py` (adapted from the g1 card's `exactlift.py`), `data/lifts_nojoint.json`, `checks/*.py` (written for this package; they re-implement the checks of the working cards in exact arithmetic with fixed seeds), and the selection of data.

## Adapted from our earlier work

- `c/enumall.c`, `c/tusign.c`, `c/mas.c`: unchanged from the g1 and fprime cards. `c/jsign.c`: the g1 card's program with an added option that prints the solving signing.
- `lib/hesse.py`: the arithmetic and sampler of `g1/hesse.py` with the module-level search loop removed. `lib/satlib.py`: from `fprime/enumB.py` and `fprime/costsat2.py`.
- `data/`: configurations and certificates copied from the cards; `data/gad_nonTS_minimiser.json` is one entry of the card's list of 23552 gadget minimisers.
- `evidence/`: verbatim snapshots (snapshot of 2026-10-14 14:32; the status header of `g1-PROOF.md` predates its §11–14).
