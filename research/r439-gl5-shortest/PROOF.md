# Exact scope of the GL5 and one-pass certificates

## Metric certificate

Encode a five-by-five F2 matrix by five row masks in a 25-bit integer. Generator
`(d,s)`, with distinct labels in `0..4`, adds row s to row d. Each generator is
an involution costing one ADD; a SWAP is not free. The identity is the only
distance-zero matrix. A finite table supplies a distance and a last generator
for every reached matrix.

The independent checker verifies:

1. Each nonroot reached matrix has a valid predecessor with distance one less.
2. Every one of its 20 generator neighbours is reached and differs in distance
   by at most one.
3. Exactly `(32-1)(32-2)(32-4)(32-8)(32-16) = 9,999,360` matrices are reached;
   unreached entries have no predecessor.

Descending predecessors reach the unique identity, so every reached matrix is
invertible and has a word of the recorded length. The count equals |GL(5,2)|,
so all invertible matrices occur. Along any generator path from the identity,
the edge inequalities bound the terminal distance by that path's length.
The descending word attains this lower bound. Thus the distances are exact.
The graph checker does not run BFS, use a queue, or import search code. It
decodes row fields and rebuilds the changed field separately from the builder's
shift/XOR expression.

The verified distance histogram for lengths 0 through 12 is:

```text
1,20,260,2570,19680,117860,540470,1769710,
3571175,3225310,736540,15740,24
```

This is a finite certificate of a familiar CNOT metric, not a new group-theoretic
result. Its usefulness here is exact shortest lengths for the pinned windows.

## Window domain and exact bounded saving

Flatten PR1122 A in chronological order, retaining every elementary ADD and its
frame. The domain is all original contiguous intervals of length at most 12
with one common frame and exactly five distinct physical source/destination
wires. Labels are the increasing physical wire indices. Original length may
be smaller than five. There are 1,203 intervals and 986 maps; forward-start
enumeration and independent backward-end enumeration agree on the entire set.

For each interval i, let `l_i` be its old length and `d_i` the complete GL5
distance of its map. Any circuit on those same five wires without auxiliary
registers has at least `d_i` ADDs. It can therefore save at most
`g_i = l_i - d_i`. All 319 intervals with positive gain have a first shortest
witness using every participant. The verifier checks all 32 Boolean inputs of
each old/new pair, independently of row-mask composition. F2 linearity extends
this identity to arbitrary dirty payload vectors on those wires.

Choose pairwise disjoint original intervals only, substitute equivalent
same-frame circuits on the same five labelled wires, and leave all other A
operations fixed. The standard weighted interval recurrence bounds total A
savings by 80. A separate end-sorted/binary-search implementation agrees with
the builder's position-indexed recurrence. The chosen 59 intervals attain 80.
This upper bound includes every positive gain, not just a filtered feasible
subset: the verifier explicitly checks that every positive-gain shortest path
has full participation.

Every A destination is in z (outside the target block), so every saved A ADD
also saves exactly one ADD when literal C is rebuilt from the reversed
z-destination gates of A then B. All other sections are fixed. Consequently the
complete one-pass class has lower bound `10652 - 2*80 = 10492` ADDs. This
candidate attains it and passes the actual frame and precision checks. Thus it
is a minimum **within that exact class**, even allowing other representatives
of the same window maps. Physical restrictions cannot improve on the relaxed
GL5 lower bound, and the exhibited minimizer satisfies those restrictions.

This excludes overlapping rewrites, windows of more than 12 old ADDs, a new scan
of the rewritten word, different participant counts, different frames,
commutations across fixed operations, auxiliaries, changed D/B/scatter, free
permutations, and non-ADD gates. No optimum over those larger classes is claimed.
The independent lower bound also does not assert a minimum positive growth
bound or unique shortest circuit.

## Literal cleanup, frames and full precision

All five participants still visit their original common frame. Their per-wire
entry and exit frame paths therefore agree; interleaving visits of different
registers may differ. The native record comparison independently checks each
register's ordered MOVE sequence and all COPY/ERASE records. C is regenerated
literally, not replaced merely by an algebraically equivalent inverse. D, B,
scatter, initial/final frames, retained totals and geometry are byte-for-byte
equal as decoded objects to the parent.

For precision, replace every XOR by positive integer addition from initial
bound one. Explicit COPY opens a clean private row with the copied bound;
ERASE closes it. This bounds the absolute row sum of the signed integer lift
at every prefix, without assuming integer cancellation. The verifier executes
both chronological directions separately. Every selected replacement is
admitted only after recomputing the complete current A/C word with D/B/scatter,
and both strict inherited conditions hold:

```text
2^6 F^3 B^2 < 2^104
2^18 F^5 B^4 < 2^192
```

For the final candidate, `F=13667`, `B=3758418`. Exact upper bounds are
`2307861360443122886999501568` and
`24941709210337926871896158204497246778939630375927808` respectively, requiring
91 and 175 sufficient bits. The original 104/192-bit allocations are retained.
The nine-stage formula and bridge exponent are bound to pinned source ASTs.
The unchanged native 5/9/11-stage checkers also recalculate local signed bounds,
all formal columns, bridge and copy counts, and the paid rank histogram.

Set-valued replay covers all 661 arbitrary dirty formal input columns of both
full words, forward and reverse, with exact restoration and the intended
target update. The original owning checker checks geometry and interfaces.
Its inherited H2 and K-equals-D failures for semantic D are reported, not
disabled or promoted to a new interface lemma. These finite checks do not
establish an all-size algorithm, supplier adoption, a changed paid recursive
moment, or a new multiplication exponent.
