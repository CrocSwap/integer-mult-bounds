# Executed validation

Research and source base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
The files consumed are SHA-256-pinned in `SOURCES.json`, including the original
PR589 word and immutable PR843 recipe. `EXPECTED.json` binds the candidate's
raw SHA-256, all integer columns, full local bills, exact positive bounds,
interface conclusions, search receipt and eleven mathematical controls.
`NATIVE.json` contains full deterministic native receipts for both words.

The following checks passed on Linux with the environment recorded in
`ENVIRONMENT.json`:

* The completed 12,000-trial search, with 22 reverse-dominated identity
  factorizations, one dead end, 11,977 cutoffs and the 21-gate winner.
* Integer unit columns and all 2,048 Boolean block inputs; source/helper dirt
  arbitrary; PR843's independent 26-gate comparison on the identical map.
* Both complete local words, unchanged 636-frame E8 geometry checker,
  all 661 input columns, H1-H5 and U/J/K/U-inverse conclusions.
* Exact exported scalar semantics, COPY/ERASE lifecycle, immutable copied
  sources, unchanged non-ADD bill and all register frame paths, complete
  positive growth and the retained 104-bit payload cap.
* Eleven local controls: omitted ADD, reversed block, reversed operands,
  noncommuting reorder, F2-invisible double ADD, self ADD, foreign register,
  stale cleanup, wrong frame, mutated copied source and omitted ERASE.
* Fresh C++ legality and 5/9/11-stage replay on both words: 883/1,327/1,549
  columns, 96 distinct omitted-bridge controls, and equivalent five-stage
  implementations agreeing field for field.
* Minimal relocated execution under `python -I -O -B`, and eleven package
  controls covering mathematical candidate corruption, false/missing receipt,
  omitted checker pin, changed/missing source, wrong source binding, duplicate
  JSON key, changed predecessor artifact, Boolean frame identifier and
  preservation of existing output contents.

Reproduction commands and expected markers are in `README.md`. No global
artifact regeneration, selected cold complex replay, `make verify`, Lean,
hosted supplier invoice or remote CI is represented by these receipts.
Timing is not a performance claim. The broader assumptions remain open.
