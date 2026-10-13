# Packed Clifford representation bridge and one historical CK child

This package proves a phase-sensitive representation bridge between nine little-endian Boolean coordinates and packed addresses `Fin 512`. Its final theorem, `CurrentMain.Current5996CKPackedRecipe.packed_canonical_child`, identifies the explicit packed circuit for one historical CK-HPE child with its canonical operator for every complex payload.

The selected directed record is catalog ordinal 0, key `0 → 2`, rank 1, with ordered descriptors `[] → [459]`, at construction commit `5996f9043c27bafa90b23e1c937de92a738f1a76`. `SELECTED_RECORD.json` records every serialized monomial field and the exact catalog/canonical identities. The theorem executes the right monomial, the Gaussian gate, and then the left monomial. Each monomial follows diagonal → permutation → XOR offset → stored global phase.

## What is proved

- Symbolic packed parity and matrix action agree with the nine-coordinate decoder; both inverse equations remain explicit in the generic matrix interface.
- The strict-upper quadratic form, modulo-four exponent, input/preimage phase coordinate and full stored global phase are preserved.
- The packed `cg(1, true)` gate agrees with the exact Gaussian operator with coefficients `(1+i)/2` and `(1-i)/2`.
- The monomial and Gaussian bridges compose with the accepted source-bound `[459]` canonical identity. The final equality holds for arbitrary payloads, not only the zero state.

These results establish one local operator supplier. Typed event streams, pre-A execution, physical execution, full-work state, residual/endpoint adapters, complete recipe coverage and the all-size multiplication theorem remain outside this package.

## Historical construction context and κ

The explicit author-checked historical value is **κ = 16127213726553 / 10000000000000000 = 0.0016127213726553**. It was read exactly from the pinned construction's `certificates/selected-result.json` and native assembly receipt; see `KAPPA_CONTEXT.json`. It is a conditional construction context, not a bound derived by these Lean modules. No newer selected construction is asserted here.

## Sources and attribution

The dependency closure contains 20 sources: seven unchanged public PR581 dependencies and thirteen included sources. The latter include an unchanged, attributed copy of PR593's `HyperplaneEnd/Clifford.lean`, imported as `PR593Clifford`. Its generic circuit and packed-check algebra belongs to Jeremy Kothe and Claude Opus 5.5 (Anthropic), in omp. The local representation adapters and selected-record proofs retain all inherited PR509, PR513, PR581 and finite-source attribution in `NOTICE.md` and `DEPENDENCIES.json`.

`MANIFEST.json` fixes the exact source order and 125 complete axiom probes: 58 retained public probes and 67 probes in the thirteen included sources. `ACCEPTED_CHECKS.json` records immutable prior output identities. Public and research receipt/log identities are kept distinct. `REPRODUCTION.json` is the single authoritative record for the package replay and its measurements.

The pinned environment is Lean 4.21.0 and Mathlib commit `308445d7985027f538e281e18df29ca16ede2ba3`. The runtime inventory references the public PR528 base of 2,213 pairs and PR581 extension of 156, plus a disjoint 294-pair extension, for 2,663 source/object pairs. No generated objects or caches are included.

## Offline retained-prefix reproduction

Use a successful public build of the exact PR581 package, with its two retained PR528 outputs, and the installed Lean 4.21.0 / Mathlib308445 distribution. The checker retains all seven public source/object/receipt/log records and compiles only the thirteen included sources in manifest order. The included PR593 source is reproduced as part of this bridge; its upstream attribution remains explicit.

```sh
python3 check.py --lean /path/to/lean-4.21.0-linux/bin/lean \
  --mathlib-root /path/to/mathlib4 \
  --base-runtime-manifest /path/to/lean-complete-bank-endpoint/EXTERNAL_OBJECTS.json \
  --reused-runtime-extension /path/to/lean-selected-child009/EXTERNAL_OBJECTS_EXTENSION.json \
  --prefix-package /path/to/lean-selected-child009 \
  --prefix-build /path/to/successful-pr581-build \
  --build-dir /path/to/fresh-packed-bridge-build
```

The immutable runtime references are PR528's 2,213 rows and PR581's disjoint 156-row extension. The included 294-row extension completes the exact 2,663-pair union. Source and object bytes, raw import lists, complete local import order and first object matches are checked again. No dependency installation, download, runtime rebuild or scientific supplier generation is performed.

The output directory must be absent. `--guard-only` checks inputs and output absence without compiling. `--require-observed-prefix` additionally requires the exact recorded predecessor result and receipt hashes. Portable predecessor receipts may differ in timestamps while retaining the exact source/object/log hashes and complete probes. Retained raw logs are checked byte-for-byte; the prefix validator performs no warning-path normalization.

The optional `--slot-service /path/to/lean_check.py` uses an independently reviewed local FIFO service, which is an executable trust boundary. The recorded reproduction uses its pinned shared service, one serial owner client and a two-slot global limit. Every fresh root retains a 60-second/4-GiB hard limit and a 45-second/3.5-GiB review limit. Compiler failure, a review threshold or preservation failure stops the sequence and preserves earlier successful outputs. Receipts distinguish compiler time, FIFO wait, post-slot guards and post-compiler guards.

The thirteen fresh roots print 67 ordered axiom records; the seven retained roots supply 58, for 125 total. Public object bytes and complete probes are compared with the accepted references. Raw fresh logs and their hashes are retained; any path-only warning difference requires an explicit bounded comparison rather than a changed proof source. Public reproduction status is recorded only in REPRODUCTION.json. This command does not discharge the event-stream, entry-execution, physical realization or all-size assumptions described above, and does not adopt a later selected source or a later kappa value.
