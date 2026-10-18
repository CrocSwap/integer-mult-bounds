# A separate value-stack allowance

The scientific source is unchanged Jose Manuel/jmbarrancoml PR2697,
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, authenticated through the
[PR2758 exports](../selected-continuation-storage/SNAPSHOT.json).
This proof refines PR2758's retained-array allowance. Its live-symbol bound,
stack grammar, successful arithmetic and source contracts remain predecessor
results. This is a written source argument, not a formal-kernel proof.

## Quantified contract

Fix a successfully initialized Callback, a valid coordinate, ancestor depth
`h >= 0`, and fixed index/residue digit lengths `I,R >= 2`. Assume a successful
`Callback.weight` execution satisfying the pinned source's chronological,
unit-denominator and fixed-word preconditions. Both stacks are private, empty,
with all four heads at one on entry. Observers do not mutate them. Their arrays
are the only four arrays counted here. Input programs, fields, numerical Words,
Python metadata, physical placement and other caller objects are excluded.

Write

```text
A = 2I + 4
B = R + 3
T = max(A,B)
F(h) = (h+1)T + hB.
```

In order pending main, pending reverse, values main, values reverse, define

```text
c(0) = (A+1, A, B+1, B)
c(h) = (F(h)+1, T, (h+1)B+1, B),  h >= 1.
```

For fresh arrays, each retained length is at most its coordinate of c.
For arbitrary erased, restored-head entry arrays with lengths `K_0,...,K_3`,
the coordinate bounds are `max(K_j,c_j)`. This includes warm history explicitly;
an aggregate entry bound alone is insufficient to infer the coordinate bounds.
Repeated successful calls with identical h,I,R keep the same coordinate bounds.

Thus for fresh arrays, or earlier successful calls bounded coordinatewise,

```text
retained backing at h=0 = 2A + 2B + 2
retained backing at h>=1 <= F(h) + (h+1)B + T + B + 2.
```

The latter improves PR2758's `2F(h)+T+B+2` by `(h+1)T-B` cells.
The depth-zero formula is exact even if B>A. For h>=1 the stated improvement
is strictly positive. All counts include the four LEFT cells and erased tails.
They describe lengths of Tape.cells, not bytearray allocator capacity or heap
memory. No claim of caller success follows from this successful-call contract.

## Value main stack invariant

Every record pushed onto `values` by `weight` has tag RETURN and exactly B
symbols. Let k RETURN records precede the active request, and let its remaining
ancestor depth be d. Evaluation of that request adds at most d+1 records above
those k throughout its execution, including partial stack instructions.

At depth zero, the root VALUE is removed from pending before one RETURN is
pushed. CONSTANT and UNIT also finish by pushing one RETURN. GOOD leaves one
MULTIPLY on pending and evaluates a child of depth at most d-1. It adds at most
d records. MULTIPLY pops that result before pushing its replacement, so it
cannot increase the maximum beyond k+d+1.

For PAIR, the first child executes above k existing returns and adds at most
d records. It finishes with one additional return. The second child executes
above k+1 and adds at most d records, for at most k+d+1. Two CONSTANT children
instead reach k+2, which fits since d>=1. At combination PAIR pops both results
before pushing one replacement. Mixed children and unit resets only reduce the
remaining depth. These are the literal push/pop orders in
[controller.py](../selected-continuation-storage/vendor/controller.py).

Apply the induction with k=0,d=h. The value main stack has at most h+1 complete
RETURN records and its partial push never exceeds the extent of the completed
record. Each pop overwrites existing cells and moves its main head backwards.
Its maximum written address is therefore at most `(h+1)B`, and its array length
at most `(h+1)B+1`. The +1 counts LEFT.

## The other arrays and statement interiors

PR2758 proves the combined live-symbol bound F(h), including partial pushes
and Stack.pop's copy-before-erase interior. In particular pending main has at
most F(h) contiguous symbols, so its array length is at most F(h)+1.

A pending record has length A or B. Stack.pop first erases RECORD_END, then
copies exactly the other L-1 symbols into reverse. Hence pending reverse writes
at most T-1 positions above LEFT and has length at most T. Values contains only
RETURN, so its reverse has length at most B. At h=0 pending receives only the
initial VALUE; its two lengths are A+1 and A, even when B>A.

Tape.write extends an array only through the address it writes. Erasure and
rewind never shorten an array, and do not extend it beyond these maxima. The
bounds thus hold at every write, including transient reversal. Arrays have no
constructor replacement overlap in this category: the same four Tape objects
are retained throughout weight. Arbitrary warm lengths are carried through by
the coordinatewise maximum with K. At successful return all non-LEFT content
is erased and heads restored; retained lengths remain.

## Sharpness boundary

If A>=B, a successful complete depth-h binary trace with two real ancestor
requests per PAIR reaches every coordinate maximum. The first descent has
h PAIR records and h+1 VALUE records on pending, reaching F(h). A leaf on the
last descent coexists with h completed first-sibling results on values,
reaching h+1 RETURNs. Popping a VALUE reaches A cells of pending reverse;
popping a RETURN reaches B cells of values reverse. The retained arrays
preserve all these maxima even though they occur at different cuts.
Their final total is exactly `(h+2)A+(2h+2)B+2`.

This is conditional grammar sharpness. A fixed word length need not admit
arbitrarily deep numerical extents, and the finite fixtures are not assertions
of selected-catalogue membership. The literal GL64 depth-two fixture has
I=20,R=3,A=44,B=6, and reaches lengths `(145,44,19,6)`. Their sum is 214.
PR2758 already observed 214; this contribution supplies the directional
all-depth proof that makes that observation attain a certified upper bound,
rather than its previous allowance 340.

For B>A and h>=1 the bound is conservative. For example the binary synthetic
h=2,I=14,R=32 trace reaches 343 below the new allowance 352. No general
optimality result is claimed in that regime.

## Consequence and unresolved work

This replaces one continuation backing component in a successful coefficient
call. It neither lowers the unchanged live-symbol bound nor changes executed
operations. It does not join numerical arenas, retained forms, program/field
arrays, native counters or suspended parent callers. A complete private reserve
must account for those objects at common cuts, then prove physical reuse,
movement, recursive grants and the outer contract. The selected frontier and
supplier admission remain unchanged.
