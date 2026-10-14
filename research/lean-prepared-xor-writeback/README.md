# Prepared XOR write-back to an existing marked block

Two checked Lean 4.21 modules implement target-only writes and connect them to the actual paid prepared-XOR pipeline.

- `MarkedTrackWriteback`: an explicit finite-symbol two-tape scan copies the source target bits into an existing equal-width marked destination, preserving its other track and the complete source tape. Both heads return and scratch clears. Its exact first halt is 7n+9 and every prefix uses at most 2n+4 represented cells.
- `PreparedXorWriteback`: the actual PR488 preparation, backward pairing and marked XOR feed that write machine through one charged control transition. Four original/work tapes remain explicit spectators. The existing destination has length max(len xs,len ys). The genuine first halt is at most 25n+34; with actual six-tape entrance volume V=max(1,len xs)+max(1,len ys)+len dst+4, time is at most 25V and every prefix uses at most 73V cells.

The destination target becomes the computed XOR word; its other track stays literal old data. These statements require the supplied marked destination capacity and isolated block layout. Matching input words to ambient Cell/exponent fields, physical slot access, address allocation, arbitrary ambient framing and width changes remain separate. Old destination target bits and dirty scratch are overwritten or cleared, not restored. Represented finite-alphabet cells are not an uncharged integer encoding.

The ten immutable prerequisites are reused from PR488, PR1840 and PR1921 rather than copied into this package. See MANIFEST.json for exact public heads, source blobs and hashes, and REPRODUCE.md for prospective commands. The twelve complete axiom probes use only the standard Lean axioms; four complete printed types retain the actual capacity premises. Both new modules are diagnostic-free. No reproduction was run merely to prepare this package.

James Chang, with OpenAI assistance; Apache-2.0. Author-checked conditional context: kappa=836330098538459/500000000000000000=0.001672660197076918. This package proves no new selected exponent or full multiplication result. Historical PR488 retains its distinct original context. No new XOR algebra, first-copy, global-novelty or optimality claim is made.
