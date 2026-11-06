# One physical tape for five padding counters

Scoped constructive proof, produced by Nick Petalas. Apache-2.0.

## Statement and entry contract

Let five positive cardinalities have canonical little-endian binary descriptors
for q_i-1, with the empty word for q_i=1. Put L_i=bit_length(q_i-1),
R_i=2^L_i, D=sum_i L_i, N=product_i R_i and M=product_i q_i.
Five immutable descriptor tapes, one owned counter tape, an immutable input
tape and a fresh output tape suffice for padding and restriction, with at most

```text
256N + 32D + 256
```

charged actions. All eight heads return to their entry positions, all D
counter bits return to zero, and all input and descriptor bytes survive.
The result is lexicographic zero padding of an M-bit rectangle to its N-bit
binary rectangle, or restriction of an arbitrary N-bit rectangle to its
M genuine positions. Discarded padding need not be zero.

Index coordinates from 0 through 4, fastest first. The shared counter tape is

```text
^ 0...0 $ ^ 0...0 $ ^ 0...0 $ ^ 0...0 $ ^ 0...0 $
    L_0       L_1       L_2       L_3       L_4
```

Spaces in this display are not cells. Consecutive blocks have adjacent `$^`
delimiters. The head starts at the first bit of block 0, or its `$` if empty.
Descriptor heads start at their first bit or `$`. Payload heads start at the
first data cell, immediately after `^`. The output has enough fresh owned
cells for its result and one ending delimiter. All origins may be translated
independently. Outside cells are protected. Work markers and widths are part
of the promised well-formed entry, not produced by this component.

The alphabet is `{0,1,^,$,_}`. The action model charges each symbol read,
symbol write and unit head move, one `emit` control action per payload row,
and one `advance` control action per visited coordinate. The fixed five phase
bits, selected descriptor role and control location are finite control.
There is no runtime decoded width, coordinate, cardinality or volume in
`machine.py`. This is the same primitive-action convention as PR6151, not a
claimed count of transitions in a separately compiled transition table.

## Local coordinate invariant

The two-phase countdown is the construction of Nick Petalas's PR6151. Its
local invariant is stated here to make the new shared-head composition clear.
At coordinate position x, the phase and counter are

```text
x < q:        genuine, q-1-x;
q <= x < R:  padding, R-1-x.
```

A fixed-width decrement reports underflow and restores its local starting
head. At genuine underflow, a sequential complement of q-1 loads R-q.
If nonzero, one decrement changes it to R-q-1 and enters the padding phase.
If zero, reload q-1 and carry immediately. At padding underflow, reload q-1
and carry. All local operations end at this same block's first bit.
The q=1 empty block carries on each visit; q=R never emits a padding position.

This package implements that same local countdown without importing or
running the predecessor. The new step is the shared physical head and its
complete transport bound. The predecessor's twelve-tape resource contract
and local algorithm retain their credit. They are not audit deliverables.

## Shared head and correctness

`next_block` scans right to `$` and makes two additional unit moves, ending
at the next block's first bit. `previous_block` crosses the current `^` and
the preceding `$`, then scans left to the preceding `^` and moves right once.
Neither operation reads or changes the next block's counter value. In
particular an empty block has the same entry position convention as before.

Initialization loads each block from its own descriptor, walking only to
adjacent blocks, then returns through four adjacent blocks to block 0.
Every payload iteration begins with the shared head at block 0. After emission,
advance the fastest coordinate. A carry walks to the next coordinate; a
noncarry stops the ascent. Return through exactly the already crossed blocks
to block 0. The all-five carry also returns before ending the payload loop.
Finally clear all five blocks with the same outward and return traversal.

The coordinate invariant and ordinary mixed-radix carry induction imply
exactly N payload visits, in the specified order, and an all-five carry at
the end. A row is genuine precisely when all five phases are genuine.
Padding consumes the next input bit only on genuine rows and emits zero
otherwise. Restriction consumes every padded row and emits its bit only on
genuine rows. This proves the two stated outputs, including arbitrary data
in discarded padding.

Moving between counter blocks changes only the physical head. It leaves
all counter values and phases unchanged. Consequently the carry induction
survives this serialization. At the final carry every counter is q_i-1 and
every phase is genuine. The clearing traversal restores every owned bit to
zero and the work head to block 0. All descriptor operations rewind locally;
payload heads rewind by marker scans. The output delimiter is written before
its rewind. No operation leaves the owned intervals, changes an immutable
tape or accesses a counter through another head. The construction therefore
has eight actual tapes, D work bits and ten unchanged work delimiters.

## Travel bound

Consider an adjacent pair whose earlier block has width L. The forward scan
uses L+1 reads and L+2 moves, costing 2L+3. The reverse uses L+1 reads and
L+4 moves, costing 2L+5. A complete crossing pair costs exactly 4L+8,
independent of the later block's width, value and phase.

For edge i, between blocks i-1 and i, let P_i=product_(h<i) R_h. During the
payload loop, an outward crossing occurs exactly when every faster coordinate
carries. There are exactly N/P_i such events, including the final carry.
Every outward crossing has one matching return. Thus the total travel is

```text
sum_(i=1)^4 (N/P_i)(4L_(i-1)+8).
```

For every integer L>=0, L+2 <= 2^(L+1), so 4L+8 <= 8*2^L. Since P_i contains
R_(i-1)=2^L_(i-1), each summand is at most 8N. Total scan travel is at most
32N. Singleton faster coordinates cause no problem: their L=0, R=1 edge
cost is exactly eight, already covered by the inequality.

Initialization and final clearing each traverse every edge out and back once.
Their combined additional travel is

```text
2 sum_(i=1)^4 (4L_(i-1)+8) <= 8D+64.
```

Wide slow counters therefore do not impose a width-dependent cost per row.
They are accessed only after complete faster cycles. No uncharged repositioning
or arithmetic division is used by the machine; N/P_i is an analysis count.

## Remaining action counts

For completeness, count the local primitives of this implementation. A load
costs 8L+8 and clearing costs 5L+4, including local rewinds. A positive
decrement that visits j+1 bits costs 5(j+1); underflow costs 5L+4.
For positive m, sum_(v=1)^m (1+nu_2(v)) <= 2m. The genuine countdown and,
if nonempty, the padding countdown therefore visit at most 2R+2L bits per
complete coordinate cycle. Two loads per cycle give the sufficient bound
10R+26L+16. For L>=1 this is at most 31R, using L<=R/2 and 16<=8R. For L=0
the exact empty cycle costs twenty. Hence 32R suffices in all cases.

Coordinate i completes N/(product_(h<=i) R_h) cycles, at most N/R_i.
All five local countdowns cost at most 160N. There are N emit actions and
at most 5N advance actions. Payload movement and endpoint handling, including
both rewinds, cost 4M+4N+8 <= 8N+8. Counter initialization and final clearing
cost 13D+60 apart from between-block travel. Adding everything gives

```text
160N + 6N + 8N+8 + 13D+60 + 32N + 8D+64
  = 206N + 21D + 132
  <= 256N + 32D + 256.
```

This is a uniform sufficient bound, not an optimal action count. The declared
bound is larger than PR6151's twelve-tape 192N+16D+80 bound. The improvement
is four fewer tapes while retaining linear complete movement and D work bits.

## Evidence, limits and code constraints

The standalone checker uses one shared Tape object and one shared head.
A separate host mixed-radix oracle determines the expected result. Tests cover
empty counters, all five placements of unequal widths, all distinct permutations
of a selected unequal shape, translated origins, immediate work reuse, both
scan directions, arbitrary discarded padding, immutability and complete cleanup.
Adjacent-block checks include widths through 257 and verify the exact 4L+8
identity. Rejection controls exercise primitive permissions, malformed fixtures,
capacity exhaustion and semantic mutants. These are finite corroboration.
The universal quantifiers rest on the written argument above.

All loops have finite bounds from the entry contract. Each local marker pass
crosses at most L_i+1 cells, each coordinate cycle has R_i visits, the main loop
has N iterations, and each carry/return loop has at most five/four iterations.
The checker enforces maximum padded volume 4096, coordinate cardinality 257,
width 257 for navigation, and a per-run action cap. No recursion occurs.
Functions are checked to stay within sixty lines. All correctness checks use
explicit exceptions and remain active under optimization. Fixed tape dispatch,
local module loading and three temporary mutation bindings are the only
indirect calls. Mutation bindings are restored in `finally`.

Python's managed allocations, arbitrary-precision instrumentation and host
fixture lists are reference-model deviations from allocation-free code.
Live fixture data is bounded by the enforced 4096-row capacity; cases run
sequentially. Python/library allocator internals are outside inspection.
Warning-strict normal and optimized execution plus syntax/function-size checks
are the supplied diagnostics. No separate lint/type tool is required or claimed.

Descriptors, delimited zero work, fresh output and allocation are inputs.
Malformed entries need not restore state. Descriptor production, completed
fast callee execution, ancestor parking, physical caller integration and the
complete supplier bill remain external. No minimum-tape theorem, compiled
transition table, formal kernel, independent human review, selected-assumption
discharge, new kappa or complete multiplication theorem is claimed.
