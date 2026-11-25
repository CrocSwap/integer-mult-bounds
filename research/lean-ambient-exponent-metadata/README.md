# Saved exponent cleanup and ambient marked XOR

Four unchanged accepted modules connect exact dyadic Cell restoration to exponent-metadata cleanup and the existing finite-symbol marked XOR execution, including arbitrary surrounding tape contents.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the source-matched selected PR1094 context. The original source context is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the selected-result, assembly, selected-source and two emitter blobs remain identical at 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. This package does not improve κ or prove the full selected multiplication theorem.

## Checked results

- `DyadicAddSavedExponent` retains the original target exponent and derives exact restoration of the original Cell from the actual aligned ADD output and unchanged source. Exact divisibility follows from the forward operation; no original target numerator or inverse equation is assumed. The half-source specialization matches the existing reference ADD.
- `DyadicAddExponentCleanup` defines exponent XOR and target restoration on a boundary state. XOR is involutive on every such state; saving starts from zero, and clearing requires the restored exponent match. The two-instruction cleanup restores an actual forward-image target and clears metadata while preserving the source and supplied post-ADD dirty accumulator. The reference-program join derives the required target/source values from the accepted ADD execution.
- `ExponentMetadataBitAdapter` interprets actual paired Boolean rows as the saved and current target exponents. Under explicit `Matches`, the accepted marked XOR scan implements the metadata toggle with exact first halt at 5*w+4 transitions and w+2 represented tape cells at every prefix. Equal restored exponent values force every target bit literally false, including leading zero slots; the source track is preserved.
- `FramedExponentMetadata` lifts that interpretation and literal clearing endpoint to arbitrary ambient lists. The strict observer remains on a supplied local segment witness. Both spectator lists are preserved, with the left list in the zipper's stored reverse order. The inherited framing theorem counts both ambient contexts in addition to the local marked cells.

`ACCEPTANCE.json` binds eighteen complete axiom probes and seven full printed types to the exact source hashes. All four accepted roots are diagnostic-free. Historical preparation labels remain in the unchanged source; the source-bound acceptance summary records their later successful checks.

## Scope and remaining interfaces

The restore/cleanup definitions use unbounded Int/Nat reference operations. Only the exponent XOR has the stated finite-symbol execution refinement here. The actual scan starts with a supplied marked paired word and false Boolean scratch. Width selection, physical bit encoding, pairing, marker installation, segment location and allocation are not free operations supplied by these theorems. Other BoundaryState fields remain semantic parameters. Preserving the post-ADD accumulator is not restoration of the accumulator before that ADD. Selected physical execution, arbitrary dirty-scratch recovery, global precision and uniform recursive bit cost remain separate.

## Reuse and attribution

James Chang with OpenAI assistance, Apache-2.0. Preserve the existing Cell/alignment, selected emitter and routing credits, DreamingOfClouds' LemmaG/LemmaA attribution, and Gareth Davidson (@bitplane) with OpenAI Codex assistance for PrefixNorm. Reuse immutable public PR1840 XOR, PR1921 framing, PR2025 arithmetic and PR2370 aligned ADD, with their credited predecessors. Related PR590/612/878 Boolean-register interfaces concern scalar target translation and finite boundary data; they do not provide these Cell-exponent restoration or marked-tape metadata joins. No priority or global novelty claim is made.

The four shipped sources total 21,074 bytes. Eighteen public or deterministically import-derived prerequisites give a complete 22-module research closure of 169,546 bytes. `PUBLIC_SOURCE_MANIFEST.json` records exact pins and topological order. `REPRODUCTION.md` uses an already prepared Lean 4.21.0 / Mathlib installation; no prerequisite source is duplicated in this package. Do not load conflicting original and import-alias namespaces together.
