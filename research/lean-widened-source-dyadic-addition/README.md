# Paid exponent widening and half-source dyadic addition

Three unchanged accepted Lean modules execute a binary exponent increment, handle actual overflow by extending an independent marked work tape, and feed the resulting exponent into the fourteen-tape reusable dyadic adder. The final value is the first input plus one half of the second input. Exact first halt and every-prefix represented-cell bounds retain the actual possibly increased exponent width and numeric exponent-gap cost.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the unchanged selected PR1094 context, author-checked by James Chang with OpenAI assistance. Historical context is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; the five selected critical source blobs are identical at observed main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2. This finite conditional execution does not improve κ or establish the selected all-size multiplication runtime.

## Counted physical increment

`PaidBinaryIncrement` first runs the unchanged accepted marked fixed-width counter. A charged finite branch either halts with the incremented word or enters the extension scan. On overflow, actual transitions scan to the right marker, overwrite it with a high one bit, write the new right marker in the adjacent blank cell and return to the left marker. No runtime list append or unit-cost Nat increment supplies that bit.

For an input word `xs` of width n, the exact first-halt time is

`MarkedBinaryIncrement.totalTime xs + 1 + (if overflow then 2*n+5 else 0)`.

The proved bound is `4*n+9`; every-prefix represented cells are at most `n+3`. The output value is exactly `value(xs)+1`, and its length is `n+1` on overflow and n otherwise. The empty word is covered: the actual overflow extension creates the one-bit representation of one.

The tape is an independent marked working tape with blank exterior. Extending into that blank cell does not establish an in-place update of a packed slot whose right neighbor might be occupied. The working word and old overflow flag are overwritten; no arbitrary scratch restoration or input encoder is claimed.

## Capacity-checked predecessor

`IncrementedSourceDyadicAddition` uses the accepted fixed-width increment and one real overflow branch before the reusable adder. Its successful endpoint explicitly requires

`value yp + 1 < 2^(length yp)`.

If the actual increment reports overflow, the controller halts with that modular counter state retained. Successful first halt and output semantics are not asserted for the rejected path. The other thirteen tapes remain spectators during increment, and the handoff passes actual tape fields into the existing adder without decoding or allocating a word.

Its successful exact time is

`MarkedBinaryIncrement.totalTime yp + 1 + ReusableDyadicOutput.totalTime xp (incremented yp) xs ys sx sy er ar`.

The prefix bound is the maximum of the actual initial represented-cell count `length xp+length yp+length xs+length ys+8` and the accepted adder/output bound evaluated on the incremented exponent word.

## Widened fourteen-tape endpoint

`WidenedSourceDyadicAddition` reuses that physical frame and handoff, replacing the fixed-width preparation by the paid widening increment. Its actual switch consumes the resulting output tape. Therefore the successful endpoint has no exponent-capacity premise, while the independent-work-tape/blank-exterior entrance remains explicit.

Write `yp' = PaidBinaryIncrement.outputWord yp`. Exact first halt is

`PaidBinaryIncrement.totalTime yp + 1 + ReusableDyadicOutput.totalTime xp yp' xs ys sx sy er ar`.

It is bounded by `4*length yp+10` plus that same adder time. The latter still charges numeric-gap-dependent unary production. Increasing the exponent may change the gap and hence the actual later cost; the bound is evaluated at the real widened word.

The complete prefix-cell bound is

`max (length xp+length yp+length xs+length ys+9) (additionBound xp yp xs ys sx sy er ar)`.

Here `additionBound` is exactly the prior fourteen-tape bound evaluated using `yp'`: the eleven-tape adder bound plus marker-inclusive copied-exponent, extracted-numerator and separated-low-output lengths. The extra one cell in the first term pays possible overflow extension.

With `Cell.value = numerator / 2^fractionalBits`, incrementing the second exponent from p to p+1 divides its value by two without changing its signed numerator. The actual reusable output decodes to

`inputValue(xp,xs,sx) + inputValue(yp,ys,sy)/2`.

This is half-source addition. Any negative coefficient requires the appropriate separately established sign/negation input; it is not silently included in the statement.

## Boundaries, acceptance and reuse

Physical marked words, input signs, initial registers, blank work/output tapes and the independent exponent tape's blank exterior are supplied. The source-exponent work copy is changed in place. Preserving an original packed source requires the separate paid acquisition/caller interface. No selected store allocation, occupied-slot writeback, physical input encoding, arbitrary dirty-state inverse or global uniform multiplication charge is supplied here.

The newer fixed-grid direction separately has accepted semantic simulation and a parity-qualified same-width physical half with a local fixed-Q value link. Fixed-grid initialization, the complete selected caller/schedule and its uniform charge remain separate. The variable-exponent widening strategy here does not implement the fixed-grid caller for free.

`ACCEPTANCE.json` records 26 complete standard-only axiom probes and nine full printed types for the exact three source hashes. All successful roots are diagnostic-free; original failed predecessors and exact proof repairs remain preserved. No source rewriting or accepted compiler replay was done for publication.

The fixed-width counter and its arithmetic predecessors are existing public work, reused through PR2005 and the unchanged public RippleCounter source. The reusable output/addition providers are imported unchanged. Substantial generic machine, framing and caller infrastructure already exists in PR2235; PR2411 supplies further physical copy/seek/return APIs. This packet's scope is its concrete occupied-working-word overflow extension and half-source caller endpoint, with no generic novelty or priority claim.

James Chang with OpenAI assistance, Apache-2.0. Preserve the unchanged RippleCounter and all other predecessor headers/credits, including documented import-only provider adaptations. The three new sources total 40,825 bytes. The manifest lists the complete 38-module research closure with 35 immutable public/import-derived prerequisites and an exact compile order. Reproduction uses an already prepared Lean4.21.0/Mathlib installation, bounded serial compilation and per-module logs; conflicting alias namespaces must not be loaded together.
