# Native ADD countdown backing

The source is Jose Manuel / jmbarrancoml's PR2697 at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, exported byte for byte in
[sources](sources). PR2902 bounds native payload arrays and leaves these
non-payload arrays separate. This result supplies only the `Counter.tape`
component of that handoff.

## Domain and metric

Consider one successful, complete `stream.add_pass` with modulus M>=2,
positive spectator cardinalities U,G,S, and F=UM²GS payload bits. All source
words retain the same identity, width and value throughout the call. The three
spectator words have exactly one high zero margin. The native Ring's residue
arena has b=bit_length(M)+1 digit positions. The coefficient callback returns
the same canonical coefficient on split and merge, as required by ADD semantics.
Use the native Tape factory and unchanged Counter/Word methods.

Count `len(counter.tape.cells)` for distinct Counter objects reachable from the
active native execution. Include LEFT, RIGHT and blank retained entries. Include
pending constructor results before assignment replaces an old binding. Clearing
content does not shorten this length. No external observer, factory or callback
captures native frames, Counters or their arrays. This is a reference-lifetime
metric, independent of allocator capacity or garbage-collection latency.

Exclude borrowed spectator tapes, payload arrays, Natural tapes, all numerical
Word arenas and templates, callback/program/field records, outer caller counts
and Python object overhead. A total private-A bound still needs those categories.
The count below is not a complete native memory bound.

Let

```text
p = bit_length(U)+3
m = bit_length(G)+3
s = bit_length(S)+3
r = b+2 = bit_length(M)+3.
```

These are constructor backing lengths. A word with ell digit symbols before
RIGHT gives its Counter ell+2 cells. Normalization may erase leading zeros,
but its backing remains ell+2. Native decrement and close never increase it.
The coefficient-derived offset and leading words have the same fixed arena
width b even when their values are zero or one.

## Exact intrinsic maximum

The maximum of the native Counter component is

```text
C = p+r+m+max(m,r)          if S=1
C = p+r+m+max(m,r+2s)       if S>1.
```

This formula is uniform over the stated source domain. Its two possible
maximizing cuts are the next-middle constructor and the inner copy operation.
It is independent of the coefficient value and of the number of passes.

Each traversal retains `outer`, `sources` and `mid`, of lengths p,r,m. Closed
`sources` and `mid` remain in their local bindings until replacement or function
return. A new `sources` constructor can overlap its predecessor and the old
`mid`, with total p+2r+m. A new `mid` constructor overlaps its predecessor,
with total p+r+2m. M>=2 guarantees that a second x iteration reaches the latter
cut, even if U=G=1.

Every `copy_blocks` call has its `blocks` of length r, alongside p+r+m. If S=1,
`one_bit_suffix` takes the direct bit branch and creates no `bits` Counter.
Its maximum p+2r+m is attained by a leading-copy call at x=0, whose block
count is M>=2. This and p+r+2m give the first formula.

If S>1, `copy_blocks` constructs a `bits` Counter of length s for every block.
After closing it, the old `bits` remains bound while the next constructor runs.
Thus the exact copy maximum is p+2r+m+2s. At x=0 the offset is zero and leading
is M, for every coefficient. There are at least two leading blocks, so this
cut is attained even with one middle iteration and one outer iteration.
Together with p+r+2m this gives the second formula.

No other cut is larger. New `outer` has no predecessor in its traversal frame.
Pending `sources` is bounded by the copy maximum. A pending `mid` cannot coexist
with an active `copy_blocks` frame, because the previous call has returned.
Pending `bits` is already included. An `observe` argument aliases an existing
Counter; the native observer stores only integer traffic totals. Constructors
and decrement allocate no additional Counters. The first traversal frame ends
before the second starts, including its cleared bindings. Copy loops and their
constructor sequences exhaust every Counter allocation site in this source.

For U=G=S=1,M=3, C=18. For U=G=1,S=2,M=3, C=28. For U=1,G=4096,S=2,M=2,
the next-middle cut dominates and C=41. These are retained lengths, not the
number of nonblank symbols at those cuts.

## Callback phase and its necessary ownership condition

Both calls to `prepare_coefficient` occur before that traversal allocates
`outer`, `sources`, `mid` or any nested copy Counter. The preceding traversal's
frame has ended. If callback-private Counter backing is at most H and all such
backing becomes unreachable before the callback returns, the combined native
and callback Counter component is at most `max(C,H)`.

This is an upper bound if H is only an allowance. It is exact when a callback
attains H. The callback must also preserve the native configuration and avoid
capturing caller frames or native Counter references. Retained external state
cannot be dropped from a complete ledger.

A literal native counterexample uses U=G=S=1,M=3. Each coefficient callback
creates a 32-cell Counter, clears it, and retains its object in a captured list.
The two callback calls retain 64 cells together. The actual peak becomes
18+64=82, exceeding max(18,64)=64. Both coefficient results and the complete
ADD endpoint are correct. Clearing is insufficient to justify phase separation.
Capturing a completed traversal frame would likewise retain its closed native
bindings; the no-capture premise covers that separate way to escape ownership.

PR2902 supplies private payload maximum 2F+3. Therefore
`2F+3+max(C,H)` is a sufficient bound for this restricted union, under the
callback ownership condition. The component maxima need not coincide, so this
sum is not claimed sharp. Callback payload allocation must remain separately
excluded or separately bounded. None of this substitutes for PR2882's total A.

## Verification and remaining scope

The checker runs unchanged source methods. It wraps Counter construction with
a weak-reference observer and samples after each constructor returns. At that
instant the caller's previous binding still exists. Each Counter has its final
backing length then; subsequent decrement and clearing preserve length. The
census does not retain Counters or frames, and it checks that its weak references
are dead after an ordinary action returns. Its explicit inventory bound is
eight simultaneous Counters, including the deliberately escaping callback.

The 63 ordinary fixtures cover moduli 2,3,5, zero and nonzero coefficients,
unit and larger spectators, both formula branches, a 32,768-bit large-middle
case, and callback peaks above and below C. Each fixture checks the complete
ADD output against an independent integer-address permutation and verifies the
borrowed source and numerical live-slot baseline. One additional successful
native fixture supplies the 82-cell callback counterexample. Source/manifest,
domain, pending-`bits`, pending-`mid`, cleared-backing, weak-retention and typed
receipt controls reject the named invalid implications. The separate source
derivation and 162-fixture replay are recorded in VALIDATION.md.

Finite executions corroborate the source lifetime proof. They do not prove a
complete physical allocator, exception cleanup, full GL64 selected execution,
all-size caller transfer, supplier admission or a new multiplication exponent.
