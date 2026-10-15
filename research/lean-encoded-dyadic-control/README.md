# Executed variable-exponent dyadic addition and prefix storage

Three unchanged accepted Lean modules compose actual encoded exponent comparison/difference, unary control production, numerator padding and signed addition. The complete eleven-tape execution has a derived first halt, decoded dyadic-sum semantics and a whole-run prefix-cell bound.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the unchanged selected PR1094 context, author-checked by James Chang with OpenAI assistance. Historical context is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the five selected critical source blobs are identical at observed main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. These finite conditional execution results do not improve κ or supply the full selected multiplication theorem.

## Actual computation and cost

`EncodedExponentControl` runs the accepted physical pair builder on two arbitrary-width unsigned exponent words, with both signs false. The two extra zero columns are actually written. A charged switch enters the accepted compare/subtract/extract/binary-to-unary controller. Both original exponent words remain available. With `m = max(length xp, length yp)` and `d` the computed absolute numeric difference, its exact first-halt time is

`8*m + length xp + length yp + 24 + 1 + PairedDifferenceUnary.totalTime(rows xp yp, clearScratch er)`.

The proved bound is `d*(2*m+10) + 38*m + length xp + length yp + 122`. Its every-prefix represented-cell bound is `length xp + length yp + 2*m + d + 14`. Numeric difference is explicitly charged. A short binary word can describe a large unary gap, so this is not a bit-width-only linear-time claim.

`EncodedDyadicAddition` uses the convention `Cell.value = numerator / 2^fractionalBits`. Thus the smaller exponent receives the nonnegative numerator left shift. After actual exponent computation, two real marker write/move transitions construct the other operand's empty unary control, and one charged branch chooses the route. A retained Boolean selects the same physical control tapes on every delegated padding/addition step; no Nat comparison, subtraction, variable shift or whole-word copy is a unit-cost operation.

Write `dl`, `dr` for the derived shifts. The exact first halt is

`EncodedExponentControl.totalTime xp yp er + 3 + PaddedSignedAddition.totalTime dl xs dr ys`.

The output bits satisfy the decoded signed dyadic sum at exponent `max(decode xp, decode yp)`. That common exponent is a view of one unchanged original input word. This unit does not allocate or copy a fresh exponent result record.

`EncodedDyadicAdditionSpace` covers every actual run prefix, including both marker writes, the charged route switch and post-halt stuttering. With `a = dl + length xs`, `b = dr + length ys`, the full bound is

`length xp + length yp + 2*max(length xp,length yp) + 12 + 2*(a+b) + max(a,b) + 16`.

All eleven tapes, original words, consumed difference work, padding controls, padded numerators and sum are counted. Registers and sign fields are finite control data. Scratch may be cleared or overwritten; arbitrary prior scratch values are not reversibly restored.

## Initial and remaining obligations

Four marked binary words, their sign fields, independent blank work tapes and finite initial registers are supplied. Physical input encoding, allocation, packed-store acquisition/writeback, raw2's half-source preparation, external caller routing and fresh result-field construction remain separate. No shared root-uniform C(n+w), selected global precision or full multiplication runtime follows from these local bounds.

The newer accepted `FixedGridReference` direction supplies unbounded integer fixed-Q simulation, exact HALVE parity, and Q=P+1 for the selected rows1→2 reference. Physical fixed-grid encoding, executed right shifts and a uniform charge remain open. This variable-exponent implementation is a separate concrete supplier; it does not discharge the fixed-grid physical requirements for free.

## Acceptance, overlap and reuse

`ACCEPTANCE.json` binds 25 complete standard-only axiom probes and five full printed types to the exact three source hashes. The accepted runs retain one unnecessarySeqFocus style warning in `EncodedDyadicAddition`; the other two roots are diagnostic-free. Failed predecessors and exact proof repairs remain preserved. No accepted source was edited or replayed for publication.

PR2235 already provides substantial reusable finite-machine, framing and charged-caller infrastructure. PR2411 provides further actual map-copy, counted seek and marked-return suppliers. This packet's narrower result is its existing concrete zipper-alphabet composition, correct exponent-control routing, dyadic interpretation and complete local prefix count. No generic controller novelty, priority or global absence claim is made. The external end-to-end tiny-κ result is not a replacement for the selected contextual κ or its remaining physical suppliers.

James Chang with OpenAI assistance, Apache-2.0. Preserve all original source headers and predecessor credits. Exact public PR1840, PR1869, PR1899, PR1947, PR1985 and PR2025 dependencies are reused, together with the earlier reference-store/hosting foundations. Import-renamed public LemmaG/LemmaA and PrefixNorm retain DreamingOfClouds and Gareth Davidson (@bitplane) attribution; only the documented import substitutions are applied.

The three new sources total 41,587 bytes. `PUBLIC_SOURCE_MANIFEST.json` pins the complete 27-module research closure with 24 immutable public/import-derived prerequisites, and gives its exact topological order. `REPRODUCTION.md` uses an already prepared Lean4.21.0/Mathlib installation with bounded serial compilation and preserved logs. Do not load conflicting original and alias namespaces together.
