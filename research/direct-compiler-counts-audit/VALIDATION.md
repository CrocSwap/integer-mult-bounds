# Local verification receipt

Scientific scope froze at2026-11-05T21:05:20.015014UTC. No expected engine,
source adapter, actual controls, scientific source object, case, healthy or
control packet, or PROOF byte changed after that freeze. The final amendment
updates only README/TASK status and adds this validation note.

CPython3.12.14, macOS26.5.2 arm64, standard library, serial children and
OMP/BLAS/MKL/VECLIB/NUMEXPR threads1:

- All eight registered warning-strict normal/optimized commands passed through
  `scripts/research_package.py --package research/direct-compiler-counts-audit`.
  Metadata/pins also passed. The original formal-interface gate remains unmet;
  the helper correctly reports `outcome=partial`.
- 72 actual full-reference/typing/encoding/argument corruptions rejected;
  eight explicit healthy-reference controls passed. The initial external
  harness diagnostic mismatch is preserved and explained in CORRECTIONS.md.
  No verifier program or first packet was changed to repair that harness.
- At local commit`cbe4a86aff3d1a11c60c1fedf830b673f3a20ffa`, committed raw
  bytes/source-history checks passed for all30 package/input files. Canonical
  main`7c49fe32c55de02c2c873655c804b16e4c3fef0a` is the sole declared source
  history commit; no pending foreign commit is needed by a verifier.
- Official export and all11 declared inputs passed. Its31-member tar SHA256
  is`3bd8e66ad5189d2ed3f6f885763eac761e642201475b0a91e7694c7e76de5da6`.
  All eight commands then passed from that read-only, Git-free export with
  PATH=/nonexistent. All31 exported files remained byte-identical. This is an
  exact scientific-byte replay before the stated final metadata amendment;
  final committed/export/public byte receipts are recorded separately.

The complete healthy packet is1,930,712 bytes, SHA256
`da8b0953c9a94165de7e25fb00b793acc86c36a0eb73e0afb37146c65275aeb3`.
All3,480 exact vector entries and four complete summary records agree.
First primary/oracle/source runs took0.319/0.316/0.261seconds, each below38MB
peak RSS. The actual seven-control packet is3,058 bytes, SHA256
`dac54fc24ed2f0ca9edacb4bac90d9268be8655c331e4f0e752fee3d5c174354`;
its first took0.751seconds and52,592,640bytes peak RSS. Forecasts are not
measurements. No speedup, universal test coverage or native cost is inferred.

The frozen META-PIVOT-REVIEW contextual-hash warning is resolved by
CONTEXT-BYTE-CORRECTION.json: its earlier hashes bind retained extra-terminal-LF
text exports; PREDECESSOR-CONTEXT-PINS binds corrected raw canonical blobs.
Neither context version was executed. Scientific pins and firsts are unchanged.

Hosted CI and upstream publication are separate later observations, not
predicted successes here. No source `verify`, native census, literal executor,
selected cold suite, Lean, Docker, paid or heavy work ran. All five selected
assumptions and the physical/compiler/precision/tape/analytic/outer obligations
remain. Counts corroborate Dillon/PR4521 and the credited predecessors; the
new finite result concerns actual inline-guard fault coverage only.
