# Component-local reference stores

At the author-checked source context κ = 836330098538459/500000000000000000 = 0.001672660197076918, this package proves generic component-store prefix masks and exact read/halve/negate/write reference memory semantics. The results are parameterized by finite coordinate types, arbitrary initial payloads and duplicate-free schedules. They are a reusable reference implementation step; selected physical address/order, rounding, scratch restoration and bit-time remain separate. They do not prove the full selected multiplier theorem or change κ.

## What is proved

A chronological update reads its own current coordinate. With no duplicate slots, that read equals the coordinate's original value, even when operators on other coordinates are arbitrary. Every prefix therefore has the exact mixture of untouched and updated real/imaginary components. Complete traversal gives the endpoint.

The reference SCALE(-1/2) operation explicitly reads one slot, halves its accumulator, negates it, then writes that slot. Its memory equation is derived from these four operations. The accumulator is allowed to start arbitrary and remains dirty afterward. This is a real-number reference semantics, with no unit-cost bit-arithmetic claim.

The package contains two new scientific modules and one reused generic namespace slice. A fourth store-chain module is derived from an immutable public prerequisite; the existing Stream is also fetched rather than copied. ACCEPTANCE.json records twelve actual standard-axiom probes, four full type readbacks, the two unprobed but compiled prerequisite roots, and one harmless unused-instance warning. Exact accepted bytes are preserved despite historical uncompiled-proposal comments.

## Attribution and reuse

James Chang with OpenAI assistance, Apache-2.0, for the component-store and explicit reference-operation refinements. IndependentEntryUpdates preserves the unchanged generic namespace body of the earlier Current799EntryFold work; it is prerequisite reuse, not a new theorem claim. No historical 728-register application is included.

FreshScalarPrefixNorm is Gareth Davidson (@bitplane)'s PR1309 PrefixNorm with only its Stream import renamed. Its header, definitions and proofs are unchanged. Underlying Lemma G stream/conjugation credits are preserved. The exact import transformation and immutable sources are in PUBLIC_SOURCE_MANIFEST.json. Do not combine the original and renamed modules in one environment because their namespaces coincide.

Related source: https://github.com/CrocSwap/integer-mult-bounds/pull/1309

See REPRODUCTION.md for the exact five-module source closure. Original failure diagnostics and complete private checking records remain preserved; they are not part of the public payload.
