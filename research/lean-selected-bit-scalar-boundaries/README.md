# Selected bit scalar boundaries

Author-checked selected conditional context: **κ = 1517760977820331/1000000000000000000 = 0.001517760977820331**, from `certificates/selected-result.json` at selected main `f19cb621be2caf3a7291a37c343c1c55afe935e0`. The exact bit supplier is PR493 head `c3a9a436b84fe44fdc223a5784d84736d1c2d3c7`. This package does not prove a complete multiplier or κ theorem.

## Historical source context on the publication base

The checked construction remains the historical `f19cb621be2caf3a7291a37c343c1c55afe935e0` selection above. Main commit `9449300d19da876995e63d0022406cbe998ef4d3` now selects a different construction, with conditional κ = 1584931111785787/1000000000000000000 = 0.001584931111785787. It preserves the prior selected record byte-for-byte at `certificates/checkpoints/direct531.json` (SHA-256 `0bca96caf2da6fe14c3f69b0560b6185de1c8238d2b361dec8e9786c91f585ed`). These 489-helper proofs are not a certificate of the newer 480-helper instance. Their original source, κ context and measured Lean reproduction are unchanged.

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

## Offline reproduction

The eight sources use only the official Lean 4.21.0 core library. No Mathlib checkout, predecessor Lean package, supplier execution or network download is needed by the checker. The supplied checker requires Linux with `/proc` for its measured memory limits; the Lean source statements are portable.

Provide the exact extracted `lean-4.21.0-linux` distribution. `OFFICIAL_CORE_MANIFEST.json` pins its binary and all 317 source/object pairs, with toolchain-relative `src/lean` and `lib/lean` paths. The checker verifies byte identities, import order and the exact reachable core closure before compiling, and verifies preservation again afterward.

Run `python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean --build-dir /new/empty/build-directory`. The build directory must not exist. An optional `--slot-service /path/to/existing_slot_service.py` uses an existing FIFO `acquire()` service without changing Lean inputs.

All eight included roots are compiled fresh in manifest order; zero public outputs are retained. Each command uses `-s 65536 -j 1`, a 60-second wall limit and 4 GiB address-space limit. The checker stops after the first failure or a measured check above 45 seconds or 3.5 GiB. All 50 complete axiom probes must match the manifest and use only the standard `propext`, `Classical.choice` and `Quot.sound` axioms. Source copies, objects, raw logs and receipts are preserved in the isolated build directory. Only `REPLAY_SUMMARY.json` owns the public reproduction status.
