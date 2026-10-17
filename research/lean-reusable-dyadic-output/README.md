# Executed reusable dyadic output

Four unchanged accepted Lean modules extend the executed dyadic adder through paid exponent copying, actual numerator extraction and paid sign separation. The fourteen-tape endpoint provides a marked low numerator word, its observed Boolean sign and a physically copied common-exponent word, with exact first halt and every-prefix represented-cell bounds.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the unchanged selected PR1094 context, author-checked by James Chang with OpenAI assistance. Historical context is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the five selected critical source blobs are identical at observed main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. These finite conditional execution results do not improve κ or supply the full selected multiplication theorem.

## Actual output construction

`CopiedExponentDyadicAddition` waits for the actual eleven-tape addition endpoint. The retained comparison flag selects the unchanged original exponent word representing the common exponent. One charged handoff invokes the accepted zero-padding copier with zero padding. Nine spectator tapes and three active tapes give twelve tapes in total. The old eleven-tape endpoint and finite fields are reconstructed exactly, and the fresh output is the literal marked common-exponent word with its head at the left marker.

If `e` is the common exponent word, the exact first-halt time is

`EncodedDyadicAddition.totalTime + 1 + 6*length e + 14`.

The extra every-prefix capacity is `length e + 2`, counting both markers. The copy operates on actual symbols; selecting the source view does not copy the word for free.

`ExtractedDyadicOutput` pays one handoff into the already accepted `MarkedBitDifference.extraction_exact` implementation, retaining its transitions unchanged. Eleven spectator tapes plus the active source/output tapes give thirteen tapes. The emitted numerator word includes its final sign bit. The old twelve-tape endpoint and finite fields are reconstructed exactly. If `q` is the actual sum-row list, the exact additional time is `1 + 6*length q + 16` and extra prefix capacity is `length q + 2`.

`MarkedSignedWordSplit` is an actual two-tape finite-symbol controller. Given a marked word `low ++ [sign]` and blank output, it delays each bit until the following symbol is inspected. A following data symbol causes a low bit to be written; the actual right marker identifies the final sign bit. It preserves the complete source, writes a marked low word, returns both heads to their left markers, clears its held-bit scratch and overwrites the previous observed sign. For `n = length low`, including n=0, exact first halt is `5*n + 10` and every-prefix represented cells are at most `2*n + 5`.

`ReusableDyadicOutput` pays one handoff from the actual extracted numerator into that splitter. Twelve spectator tapes and two active tapes give fourteen tapes. All thirteen preceding tapes and finite fields are reconstructed exactly at the endpoint. Its final additional time is `1 + 5*length lowWord + 10`; extra prefix capacity is `length lowWord + 2`.

Thus, writing `B` for the accepted eleven-tape bound, the complete every-prefix bound is

`B + (length e + 2) + (length q + 2) + (length lowWord + 2)`.

The complete exact time is the accepted eleven-tape time plus the three charged handoffs and the three displayed scan costs. The underlying exponent-difference-to-unary computation remains numeric-gap-dependent. No bit-width-only or shared root-uniform cost is inferred.

## Reusable semantic endpoint

The source uses `Cell.value = numerator / 2^fractionalBits`. The proved endpoint exposes actual marked low bits, an actual observed sign field and actual marked common-exponent bits. Decoding these fields gives exactly the sum of the two supplied dyadic input values. The low/sign representation uses `signedValue(low,sign) = decode(low) - bit(sign)*2^length(low)`.

Proof observations such as `lowWord`, `signBit` and `commonWord` describe the derived endpoint. They do not appear as uncharged whole-word operations in the transition. The added held-bit/sign registers may begin dirty and are overwritten; arbitrary old scratch values are not reversibly restored.

## Initial and remaining obligations

Four physically encoded marked input words, input signs, finite registers, independent work tapes and fresh output tapes are supplied. Initial encoding/allocation, packed-store acquisition and writeback, physical caller transport, selected global precision and a full multiplication runtime remain separate. This packet makes the result reusable in the stated tape alphabet; it does not install it into an occupied caller slot.

The newer accepted `FixedGridReference` direction proves unbounded integer fixed-Q simulation with exact HALVE parity, including Q=P+1 for selected rows1→2. The separately accepted MarkedSignedHalf and FixedGridHalf now supply a parity-qualified same-width physical half and its local fixed-Q value link. Physical fixed-grid initialization, complete SCALE/caller composition and a uniform charge remain open. The variable-exponent execution here does not implement those requirements for free.

## Acceptance, predecessors and reproduction

`ACCEPTANCE.json` binds 32 complete standard-only axiom probes and eight full printed types to the exact four source hashes. All four successful roots are diagnostic-free. Original failed predecessors and exact proof repairs remain preserved. No accepted source was edited or replayed for publication.

Substantial generic finite-machine, framing and charged-caller suppliers already exist in PR2235. PR2411 supplies further actual mapped copying, counted seek and marked return. This packet reuses the earlier concrete counted copy and extraction machinery and exposes its specific low/sign/exponent endpoint and local bounds. No generic-copy novelty, priority or global absence claim is made. Mapped copying that overwrites whole destination symbols does not itself establish preservation of an occupied companion track inside that same symbol.

James Chang with OpenAI assistance, Apache-2.0. Preserve original headers and predecessor credits. Exact public PR2426, PR1947, PR1899, PR1869 and PR1840 primitives, together with the earlier reference arithmetic/store/hosting foundations, are reused. Public LemmaG/LemmaA and PrefixNorm import aliases retain DreamingOfClouds and Gareth Davidson (@bitplane) attribution and only the documented import substitutions.

The four new sources total 66,529 bytes. `PUBLIC_SOURCE_MANIFEST.json` pins the complete 31-module research closure, with 27 immutable public/import-derived prerequisites and exact topological order. `REPRODUCTION.md` uses an already prepared Lean 4.21.0/Mathlib installation, bounded serial compilation and preserved per-module logs. Avoid loading conflicting original and alias namespaces together.
