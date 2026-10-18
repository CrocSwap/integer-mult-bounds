# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- **#446** (Theorem C, closed) and **#595** (merged): the cost formula and the pairing model; **#1590** (merged): exact decoders, Lemma A, Lemma B, ERR1 (E7 and E8 dyadic decoders with cost 49 and 72), and the pattern of `scripts/provenance.py` and `checks/expect.py` (both adapted from there); **#2111** (open): the T = 3 side (tied_min, the lift route), which this package does not repeat. #606, #1698 and #1830 are cited as context for the surrounding decoder discussion; nothing here depends on them.
- Our working card `KPR4-GAP` (2026-10-14): `c/kgap.c`, the searches and the numerical realisations; its notes are shipped verbatim in `evidence/`.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `requirements.txt`, `MANIFEST.sha256`, `lib/roots.py`, `lib/units.py` (pure-Python exact versions of the card's `units.py`/`kg.py` logic), `checks/units.py`, `checks/fano.py`, `scripts/search_e6.py`, `scripts/make_fano.py`, and the data files.

## Adapted from our earlier work

`c/kgap.c` (unchanged), `scripts/realize.py` (unchanged), `evidence/KPR4-GAP-NOTES.md` (verbatim).
