# Paid positioned track acquisition and return

Seven unchanged accepted Lean modules compose an actual three-tape read of one selected paired track from a supplied finite packed store, returning its data and control heads to home. The chosen bits are copied to a separately supplied empty tape. The complete store and both original paired tracks survive.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the unchanged selected PR1094 context, author-checked by James Chang with OpenAI assistance. The original source context is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the five selected critical source blobs remain identical at observed main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. These finite supplied-store results do not improve κ or establish the full selected multiplication theorem.

## Checked endpoint

Let `pre`, `selected`, `post` describe the ordered store, `p = pre.length`, and `w = selected.rows.length`. The actual controller performs positional access, one charged handoff, source-preserving track extraction, one charged handoff, and physical return to global home. Its first halt is exactly

`2 * capacity(pre) + 4*p + 6*w + 26` transitions.

The original represented entrance volume is `V = capacity(pre ++ selected :: post) + p + 2`, including every packed delimiter and the marked unary control. The output is initially empty. `entrance_resources` derives actual endpoint and first halt with time at most `7*V` and, for every run prefix including terminal stuttering, at most `2*V` represented tape cells. The copied output includes its paid left/right markers. Zero-width blocks and position zero are covered.

The complete data store, both selected source tracks, all other blocks, the unary control tape and the carried Boolean scratch are preserved. The seven extraction registers finish clear; arbitrary old register values are not restored. The track selector is a fixed Boolean program parameter. Tape-cell volume counts represented zipper cells; finite control and register fields remain separate fixed fields.

## Module roles

- `PairedTrackExtraction` specializes the accepted marked-difference extraction phase to a chosen Boolean track of the existing paired alphabet. It derives `6*w+16` transitions, first halt, exact output and `2*w+4` prefix cells from actual steps.
- `PairedTrackExtractionFraming` derives confinement and step/run compatibility with arbitrary surrounding source lists, then exact framed output and full-context storage. The left list is stored in reverse zipper order. Output remains a distinct empty-at-entry tape.
- `PackedMetadataSlots` supplies ordered structural lookup with explicit before/selected/after focus, missing-key failure, unique-key ownership, complete packing/capacity, and the existing metadata XOR/update refinement. Keys are logical labels, absent from the physical alphabet. Semantic first-match update and unique physical ownership are distinct facts.
- `PositionalMetadataAccess` traverses actual L/data/R symbols using one supplied unary tick per preceding block. Exact first halt is `capacity(pre)+2*p+4`; the control head rewinds while the data head reaches the selected left marker. All symbols and arbitrary carried scratch survive.
- `PositionalMetadataReturn` traverses those blocks in reverse physical order, returning data and unary heads home at the same exact cost. It reads finite symbols without a numeric seek or hidden boundary sensor.
- `PaidPairedTrackAcquisition` composes the three actual machines with two charged transitions, and binds executable `locate` success to the reached focus and copied word.
- `PaidPairedAcquisitionResources` derives the complete prefix bound and original-entrance `7V` time / `2V` space invoice without adding an execution premise.

`ACCEPTANCE.json` binds 43 complete axiom probes and 12 full printed types to exact source hashes. All use only standard Lean axioms. Two harmless `unnecessarySeqFocus` style warnings in `PackedMetadataSlots` are retained verbatim; the other six roots have no diagnostics. The historical “Uncompiled candidate” label in `PositionalMetadataReturn` is preserved. Its exact source subsequently passed and has an independent accepted terminal, as the source-bound summary records.

## Explicit caller obligations

The initial marked packed store, unary positional tape, distinct empty output tape, fixed track choice and valid ordered layout are supplied. Structural key lookup is not a paid runtime key search. Key-to-position binding, unary preparation, physical field encoding, initial store construction/allocation, source refresh and subsequent output writeback remain separate obligations. A malformed entrance gets no success theorem merely because transitions are total. No uniform recursive bit-cost, selected precision, arbitrary dirty-register recovery or full multiplier theorem is claimed.

## Reuse and attribution

James Chang with OpenAI assistance, Apache-2.0; preserve all source headers and prerequisite attribution. The actual extractor reuses public PR1947 marked-difference extraction and PR1840/1869/1899 marked tape and arithmetic foundations. Packed metadata reuses PR2403 ambient exponent metadata, PR1921 XOR framing, and the exact reference arithmetic/store/routing chain. Import-renamed public LemmaG/LemmaA and PrefixNorm retain DreamingOfClouds and Gareth Davidson (@bitplane) credits and unchanged proof bodies.

PR2235 provides substantial generic finite-head machine, framing, charged-caller and serializer infrastructure. Its inspected serializer consumes a compiler-stack input into a blank-origin output. This package's endpoint is a source-preserving selected track of an occupied paired store, with actual positional access and return. The model/ABI distinction is explicit; no priority or generic framing novelty claim is made.


The later [PR2411 framework](https://github.com/CrocSwap/integer-mult-bounds/pull/2411), at immutable provider commit `7415d773d14212c68b523979aaac6db9dc0ba542`, also supplies general components that overlap this work: [GuardedMapCopy.copy_hoare](https://github.com/platypii/integer-mult-bounds-lean/blob/7415d773d14212c68b523979aaac6db9dc0ba542/IntegerMultBounds/Machine/GuardedMapCopy.lean#L52) preserves an occupied source and the destination outside the written interval while applying a fixed symbol map in exactly the word length; [CountedSeek](https://github.com/platypii/integer-mult-bounds-lean/blob/7415d773d14212c68b523979aaac6db9dc0ba542/IntegerMultBounds/Machine/CountedSeek.lean#L212) supplies payload-preserving forward/backward movement with an immutable binary descriptor and clean local clock, bounded by `5*distance + 7*descriptor.length + 16`; [MarkedReturn.return_hoare](https://github.com/platypii/integer-mult-bounds-lean/blob/7415d773d14212c68b523979aaac6db9dc0ba542/IntegerMultBounds/Machine/MarkedReturn.lean#L104) restores a marked word's origin in `length+2` transitions. Those are reusable generic suppliers, not missing primitives. The present accepted endpoint remains specific to the existing paired-symbol/zipper model, a unary count of variable-width blocks, its two charged handoffs, exact home/output states and original represented-volume `7V/2V` theorem. The bounded comparison found no exact combined endpoint substitution; reuse in the other finite-alphabet absolute-tape model still needs an explicit representation/position/interface bridge. No generic copy/seek/return novelty or global absence claim is made.

Seven shipped sources total 85,710 bytes. Twenty-seven immutable public or deterministic import-derived prerequisites give a complete 34-module research closure of 355,239 bytes. No public prerequisite is recopied. `PUBLIC_SOURCE_MANIFEST.json` records exact identities and topological order. Use `REPRODUCTION.md` with an already prepared Lean 4.21.0 / Mathlib installation, and avoid loading conflicting original and alias namespaces together.
