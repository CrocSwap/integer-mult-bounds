# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## New in this package

Everything: `README.md`, `verify.sh`, `scripts/provenance.py` (adapted from #717/#899/#1238), `SOURCES.json`, `requirements.txt`, `MANIFEST.sha256`, `checks/`, `lib/dyadic.py`, `evidence/`.

## Adapted from our earlier work (no third-party code)

- `lib/ade.py` and `lib/fx.py`: root-line generators and the per-side saving functional used by the ceiling comparison (taken from our earlier root-unit analysis, with the module-level statistics printout of `ade.py` removed).
- `sat/gen.py`: the SAT encoding generator of the D5 closure; the only edit is the module search path (it imported `ade` from an absolute path); the generated CNF is pinned by sha256.
- `checks/expect.py`: assertion helper of `verify.sh` (as in #1238).
- `checks/lemma_a.py` ports the table of the T <= 2 card (`tmax.py`) and adds the instance check.
- `evidence/`: the independent audit of the D5 encoding and the two solver logs, verbatim.
