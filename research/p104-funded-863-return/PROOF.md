# Funded return of public helper 863

The source is the complete, authenticated P104 word of [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
at `ed090b57ed88f8859e5ff4643645099e6ba856ea`. All clocks in
[WITNESS.json](WITNESS.json) are zero-based indices in that word; a correction
at a clock runs before the original event, except that the paid split's
correction runs between its two transports.

In normalized coordinates, a MOVE changes the chart and leaves the field's
coefficient row unchanged. The source helper 863 has input chart 3 and reaches
chart 240 before its final lift to chart 127. It is a source only after that
lift, and its return value is its original arbitrary input `x₈₆₃`.
The candidate omits the lift at 58031 and all four later reads of this helper.
Its return chart is now 240. Two successive owned lifetimes on label 1568
cache `x₈₆₃`: at the entrance in chart 3, then at clock 37753 in chart 240.
The second capture is taken from the actual corrected prefix. Neither cache
moves, and each is cleared in its birth chart. The other public input and
output contracts, including all 104 main and hosted boundaries, are retained.

The literal witness gives sixteen corrections from these caches. Fifteen
use an existing coframe. For the sixteenth, the paid rank-six transport
of role 1355 from chart 739 to 127 is factored through chart 240, of rank four,
into rank-one and rank-five transports. This is the only added intermediate
contact, and both legs are charged. At the level of normalized scalar rows,
the corrections replace the suffix response of the four removed reads. An
exact rational comparison checks every output for every public basis input,
and checks the actual COPY precondition. It also checks that no owned output
is left. The other native engine uses a separate all-input adjoint; the
physical catalogue checks phase, chart action and finite compiler binding.
This is not an inference from a modular search.

Write `H_r = r^(1−C)`. Relative to #7277, the productive changes are
`T4 +1, T9 −1`. The original rank-five lift of 863 is removed, and the
donor split adds rank one and rank five while removing rank six. Thus the
net paid changes are `P1 +1, P6 −1`, and the gain per native call is
`H4 + H6 − H9 − H1`. This is strictly positive for `0 < C < 1` by
strict concavity: the pairs `(4,6)` and `(1,9)` have the same sum and
the first is less spread out. Paid and productive rank mass each fall by five per
native call. The exact signed #7113 caller makes 17 such calls; the complete
rank surplus stays at 1,424, with 22,461 productive positions, 110,536 paid
positions and no empty-root credit. These counts include the entire caller,
not just the edited routes. Both directed price engines check the old bill,
the new bill and strict gain.

The candidate word has 76,461 events and 1,501 public fields. Its 72 owned
lifetimes, peak 50 and 68 labels are included in the native and precision
bills. Owned ascent mass is still 56. The fresh exact common grid remains
1,125 / F25. The application replay verifies the unchanged literal signed
caller on the new native word and checks the full physical catalogue,
ordinary and precision bounds, fixed tape prices and outer predicates.
See the four registered receipts for the exact numbers and controls.

The five framework assumptions from the selected proof are retained:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
and `analytic_recovery`. This is a finite, source-aware verification of one
conditional supplier and application. Independent human and formal review,
maintainer selection and a materialized multiplier remain open. No selected
record is changed.
