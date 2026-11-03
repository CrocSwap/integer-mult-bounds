# An attaining lift of the fixed seven-source projection

## Contract

A singleton word has coordinates in {0,...,7}. Starting at zero in F2^8,
coordinate j toggles bit j. Its prefix states are taken immediately before
each call. A restored word ends at zero. It is universal when every element
of F2^8 is the difference of two prefix states.

Let Q be the fixed projected state set of Nicholas Stone's PR5430 word

    341236425430103051216402.

The predecessor proves that every universal lift projecting exactly onto Q
has at least 35 distinct states. Consequently a closed singleton path with
that projection has at least 36 calls: it has at most one prefix state per
call and its length is even. This lower bound is a cited theorem, not a
claim independently re-established here. Its exact retained source is pinned
as provenance in SOURCES.json. No predecessor scientific verifier is replayed.

## Construction and optimality

Use the new word

    374717236747275473071030571727164702.

It has length 36. Deleting coordinate 7 gives exactly the predecessor's
24-call word. Its coordinate counts are

    (4,4,4,4,4,2,2,12).

All counts are even, so the final state is zero. The 36 prefix states are
distinct; their low seven bits project onto exactly Q. Twelve projected
states are visited in both layers, and twelve in one layer.

The exact finite certificate is the word itself. For each mask d in F2^8,
`interval_table` constructs positions 0 <= i <= j <= 36 whose literal
coordinate parities on [i,j) are d. All 256 masks occur. Thus the XOR of the
two prefix states at i,j is d. A terminal position j=36 can be replaced by
position zero because the word is closed. Conversely, prefix-pair difference
enumeration directly covers all 256 masks; the two algorithms agree without
using the predecessor's lift criterion or matching enumeration.

This proves a universal restored lift of length 36. Together with the cited
lower bound, the exact minimum is 36 among all closed singleton paths whose
projected prefix-state set is Q. In particular it is also the minimum among
words formed only by inserting coordinate 7 into this literal parent word.
The wider fixed-state-set minimum follows because the upper construction is
in that class and the predecessor lower bound covers the entire class.

## Arbitrary dirty payloads

For any nonnegative payload width b, let h,x_0,...,x_7 be arbitrary independent
b-bit vectors. Leave every x_j unchanged and update the accumulator by
h <- h XOR x_j for each coordinate j in the word. At cut t its value is
h_initial XOR the sum of sources with the prefix parity at t. This invariant
follows by induction on the 36 calls, with all arithmetic over F2.

Every source appears an even number of times, so the accumulator returns to
its initial dirty value. For the certified interval [i,j), XORing the two
accumulator values cancels that initial dirt and yields precisely the target
source parity d. This is a scoped algebraic interpretation of the word.
Obtaining, storing and comparing these two observations is not free physical
work. No simultaneous production of all targets is asserted.

The literal scalar oracle executes all 512 assignments to eight sources and
one dirty accumulator, checking all 256 recovery intervals on each assignment.
It corroborates the invariant and interval implementation. The proof above
extends coordinatewise to arbitrary b; the enumeration alone does not claim
a physical multi-stream caller.

## Scope

This is a finite construction with a scoped optimality corollary using PR5430.
It neither classifies seven-source parents nor improves the global eight-source
optimum. Other projected sets can have shorter lifts, including the credited
32-call construction. COPY/ERASE costs, observation retention, frame legality,
source access, native calls, storage, precision, tapes, supplier/compiler
admission and the multiplication theorem are outside the result. Independent
human and formal proof-kernel review are unclaimed.
