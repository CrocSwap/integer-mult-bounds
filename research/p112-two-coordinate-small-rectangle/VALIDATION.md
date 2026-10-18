# Validation receipt

Run locally on 2026-10-13T23:36:05.353741+00:00, Linux x86_64,
Python `3.12.3`, standard library only. One verification
process at a time; no third-party packages, native builds, GPU, or Lean.

## Passing checks

- Task first working example:
  `python3 -B research/complex-decoder-field-extension-seed44/verify.py`.
  Final status `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44`, p=0..24,
  examples=3, attaining=25, pairing=14400, controls=7. Orientation only.
- `python3 -B scripts/research_package.py --package research/p112-two-coordinate-small-rectangle`.
  Metadata, historical provenance and live pins pass. Both registered exact
  checkers pass: 140 strata, 71,540 functionals, 700 support pairings, nine
  Gaussian-rational fixtures, nine primary and nine separate-checker controls.
  Local observed elapsed time about 3.9 seconds; this is not a benchmark claim.
- Both checker commands with `python3 -I -O -B` pass, so their checks remain
  active with Python assertions disabled. About 4.8 seconds total locally.
- `python3 -B scripts/research_package.py --package research/p112-two-coordinate-small-rectangle --check-only`
  passes again after the final task/overlap documentation update.
- Pinned geometry, model proof and selected-result working bytes match the
  base. Only this new package is included in the contribution.

Normal verification compares the complete deterministic receipt and does not
rewrite it. The receipt was generated to fresh paths and separately checked
before installation. The second checker derives the root/dual-code geometry
without importing the primary checker or the predecessor geometry.

## Exact claims checked and limits

The finite premise is erasure distance 12 without extra conditions, and
free-compatible erasure distance 24. Exact boundary witnesses lose span at
12 and 24 deletions; the first has no common odd neighbor, and the second
has neighbor {0}. Neither boundary is a decoder gain or a sharp decoder
threshold. The quantified GL(3,C) implication is a written linear-algebra
proof in README.md, not a finite sampling claim or proof-assistant result.

No full selected cold replay, physical word, owner/frame admission, restoration,
precision/tape, all-size/compiler, analytic transfer or bit-interface theorem
was run or discharged. Supports outside the two stated domains, more mixed
coordinates, other punctures and shared-copy accounting remain open. Hosted
CI, maintainer acceptance and independent human review remain unperformed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0.
