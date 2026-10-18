# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- This package extends the author's #2338 (*Decoder floors are tight in the frontier format*, open) and its sibling #2724 (case (b)): it works on part of the `m = 9` case (c) of #2338's trichotomy, a single explicit family of rank-9 realisations.
  The model, notation and the results it uses (the dense `F2^9` label table, Theorem P, the exact rank formula, the reductions) are #2338's, which build on #2277 and #2639 (the author's own) and on the merged swarm work cited below.
- **Cited from their PR statements, not re-derived:** **#1212** (burntout76) and its extensions **#1389, #1399, #1419, #1425, #1616** (JosieElliston): rank-8 gauge rigidity (used only to state Lemma E); **#968**: the P104 unit and the 8-term floor;
  **#1224** (joaqcoo), **#1180** (woklerx), **#1320** (Hope7Happiness), **Discussion 1267** (philippeVV): the nine-term one-sided and co-star decoders (context for case (c); **not covered** here).
  **#2321, #2385, #2398, #2515** (other authors) treat one fixed rank-9 P112 completion under a COPY-power cost; not the A2 family.
- Tools: Python (standard library), `numpy`, `networkx`. No SAT solver, no CP-SAT in `verify.sh`.
- No file is copied from another contributor. `checks/lib.py, lib2.py, common2.py, frames.py, frames_data.py, cert2.py, setup9.py` and `checks/inputs_check.py, manifest_check.py` are the author's library and check files, copied unchanged from #2724; `checks/a2lib.py, a2fam.py, a2cert.py, spans.py, modrank.py, unitcensus.py, orbits.py, orbits104.py, opt3u.py`
  are the author's working-card scripts (A2COST, CONJB, HUNT-A2; Oct 15, 2026), with absolute paths removed and (for `a2lib.py`) two working files merged. `SOURCES.json` records the source hash of each.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `checks/floors.py, tie_check.py, exact_opt.py, pairtable.py, census_facts.py, units_check.py, log_counts.py`, `data/` (frames; the two tie decoders converted from pickles to JSON);
`evidence/logs` and `evidence/hunt-a2-scripts` are exports of the author's working cards (A2COST, HUNT-A2; Oct 15, 2026), copied (absolute paths stripped in the scripts; `*.log` renamed `*.log.txt`).
