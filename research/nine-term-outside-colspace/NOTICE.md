# Notice

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root).

## Credits

- This package closes one named residue of the author's #2338 (*Decoder floors are tight in the frontier format*, open, the parent): its open item "factors outside `col M`, `m ≥ 9`", sub-case (b) of the `m = 9` trichotomy.
  The model, notation and the results it uses (Theorem R, Theorem P, the support-propagation lemma, the reductions) are #2338's, which build on #2277 and #2639 (author's own) and on the merged swarm work cited below.
- **Cited from their PR statements, not re-derived:** **#1224** (joaqcoo): normal form of one-sided nine-term decoders, merge lemma, ratio classes; **#1180** (woklerx): the nine-term example outside `col M`;
  **#1633** (bbMisk): the excess-rank budget `s + t ≤ m − 8`; **#1213** (DavidAriasC): one coordinate component of the P112 masked decoders; **#1815** (jmbarrancoml) and **#1212** (burntout76): rigidity of rank-8 realisations
  (**not used** here); **#968**: the P104 unit. **Discussion 1267** (philippeVV): the nine-term co-star programme: **not covered by this package** (co-star decoders are case (c), see README).
- Tools: Python (standard library), `numpy`, `networkx`. No SAT solver.
- No file is copied from another contributor. `checks/lib.py, lib2.py, common2.py, frames.py, cert2.py, setup9.py, orbits.py, cliques.py, paircensus.py` are the author's own library / census files from the working cards behind #2338 / #2277 (paths edited only);
  `checks/cnt*.py, m9lib.py, aut104.py, ctl8.py, ctlb.py` are the author's working-card scripts (MASK9), paths edited only, plus the `ONLY_ORBITS` hook in `cnt.py` and `cnt104b.py`.
  `SOURCES.json` records the source hash of each.

## New in this package

`README.md`, `verify.sh`, `SOURCES.json`, `MANIFEST.sha256`, `checks/inputs_check.py, rank_formula_check.py, pairs_fast.py, mk_cnt_pkl.py, cmp_logs.py, log_counts.py, manifest_check.py, frames_data.py`, `data/` (frame definition; compact census output);
`evidence/logs` and `evidence/helper` (`*.log` renamed `*.log.txt`) are exports of the author's working cards (MASK9, Oct 15, 2026), copied (absolute paths stripped in three helper scripts), except the logs `orbits_*`, `cliques_*`, `aut104_P104` which are from this package's own fresh run.
