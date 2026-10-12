# Selected bit scalar boundaries

Author-checked selected conditional context: **κ = 1517760977820331/1000000000000000000 = 0.001517760977820331**, from `certificates/selected-result.json` at selected main `f19cb621be2caf3a7291a37c343c1c55afe935e0`. The exact bit supplier is PR493 head `c3a9a436b84fe44fdc223a5784d84736d1c2d3c7`. This package does not prove a complete multiplier or κ theorem.

## Checked boundaries

Eight unchanged Lean source files contain 50 complete public axiom probes:

- Decoder/domain and named start/final/retained boundaries for the selected 120 ports, 489 helpers, 729 original registers and 672 frame-table entries. These finite identifiers do not prove frame rank or physical geometry.
- Exact 240 B gates, 600 operand occurrences, 120 scatter rows and 568 retained-index occurrences.
- Sequential Boolean XOR interpretation of the ordered B tuples. Arbitrary source/helper bits are preserved; each target equals its original bit XOR a contribution independent of initial target bits. The contribution is not asserted to vanish.
- Exact retained-major 9 COPY + 568 ADD + 9 ERASE scalar slice on 730 registers. Original-register coordinates agree with direct retained-centre scatter. Arbitrary original source/helper bits are preserved. Incoming temporary register 729 is overwritten and its final value is false. Only the explicitly conditional `clean_temp_restored` theorem restores an initially false temporary; arbitrary dirty temporary restoration is not claimed.

## Still open

A/C cleanup and source restoration, D dirty-helper compensation, the complete scalar shear/operator, physical frame and entrance-state transport, COPY-space allocation/ERASE legality, and the full inherited all-size/κ theorem remain separate. No row-major permutation theorem or execution of an upstream Python/C++ supplier is inferred.

## Reproduction contract

`MANIFEST.json` lists all eight included modules in dependency order and every expected axiom probe. No local object is retained for a public replay. `OFFICIAL_CORE_MANIFEST.json` lists the complete 317-module `Init` source/object closure with paths relative to an extracted official **Lean 4.21.0** distribution. This closure needs no Mathlib or Batteries installation.

The exact central-checker invocation and offline runtime instructions accompany the package's reviewed checker. Reproduction uses fresh isolated outputs, exact source/core identities, bounded serial jobs, and stops at the first failure or resource review. Historical local evidence is immutable in `ACCEPTED_CHECKS.json`; the sole mutable reproduction outcome is `REPLAY_SUMMARY.json`.

`SOURCE_BINDING.json` identifies the repository's existing compressed supplier input and exact source projections. That input is not needed to compile the literal Lean data modules. `PROVENANCE.json`, `AUTHOR_CHECK.json`, `NOTICE`, `SUPPLIER_NOTICE.md` and `LICENSE` record source identity, the author-checked conditional context and attribution. The source supplier, historical work and accepted objects remain in their original locations.
