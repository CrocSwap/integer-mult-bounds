# A joint numerical and countdown backing bound for native ADD

This is a source-lifetime proof for the unchanged `stream.add_pass` of Jose
Manuel/jmbarrancoml's PR2697, head
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. It joins two existing categories
at actual callback and traversal cuts. PR2831 supplies the numerical Arena
high-water invariant. Nick Petalas's PR2905, head
`119f74dfe6ff97d8d692a32ed02d6597220dd479`, supplies the native Counter
formula, and PR2916, head `639a340f6d514bbea984923da4df495b1dae42ac`,
separates callback count scratch from traversal count scratch. Those component
results are credited here, not claimed again as new work.

## Domain and metric

Fix any admitted modulus M>1 and positive before, middle and suffix values
U,G,S. The three borrowed count tapes have exactly one high zero margin,
so their digit widths are bit_length(value)+1. The Ring modulus has its
required high zero margin and residue digit width b_R=bit_length(M)+1.
The distinct index arena has fixed width b_I>=2. Arenas enter in the canonical
reachable partition state of PR2831: live and duplicate-free available slots
partition `words`, with properly erased free slots and fixed Word extents.

Count all retained `Word.cells` arrays in both arenas, including erased slots
and their permanent templates. Count distinct strongly reachable count-tape
arrays, including LEFT, delimiters, erased tails and pending Counter constructors.
Aliases count once. These two kinds of arrays are disjoint. Exclude payload
arrays, program/field/continuation records, Python container/object overhead,
temporary host buffers, allocation tables, physical placement and movement.
This is a backing-category component, not total private A or machine space.

Let K be entry count-tape backing, including the prepared U,G,S tapes and
any preexisting callback count state. Its array lengths stay unchanged.
Let H_R,H_I be entry allocated slot counts `len(arena.words)`, and L_R,L_I
be all live entry slots, including the modulus, Ring one, callback operands,
unrelated residents and any suspended caller state. Templates are additional.

Both sequential coefficient callbacks return the same canonical coefficient.
Each preserves entry numerical ownership, bytes and heads, and returns exactly
one new owned residue Word. Its peak additional live slots, including that
result, are at most J_R in the residue arena and J_I in the index arena.
It uses no unaccounted numerical arrays or arenas. It adds at most H_C
count-tape cells simultaneously, including pending constructors, and releases
all of them before returning. No callback, observer or other external code
captures native count tapes, arrays, owners or frames. Clearing an escaped
array does not satisfy release. Private callback count backing cannot become
new entry state between traversals.

Assume successful sequential execution, the other source arithmetic and complete
fibre contracts, sufficient capacity, and no mutation of arena bookkeeping or
array lengths outside the source operations. This statement does not infer
capacity sufficiency from successful-run bounds or establish a legal callback.
Use the source's default `payload_factory=Tape`. A custom factory could allocate
numerical Words or count arrays before either traversal and invalidate this
inventory. Payload tapes created by the default factory allocate neither category.
The allowances J_R>=1, J_I>=0 and H_C>=0 are finite integers.

## Statement

Define the native Counter widths and maximum:

```text
p = bit_length(U)+3
m = bit_length(G)+3
s = bit_length(S)+3
r = b_R+2
C = p+r+m+max(m, r)       if S=1
C = p+r+m+max(m, r+2s)    if S>1

B_R = max(H_R, L_R+max(J_R,6))
B_I = max(H_I, L_I+J_I)
N = (B_R+1)(b_R+2) + (B_I+1)(b_I+2)
```

Throughout both traversals, combined numerical-array and count-tape backing is

```text
at most K + N + max(C,H_C).
```

The numerical term N remains charged during native countdown work even if its
largest demand arose inside a completed callback. In general, replacing this
sum by a maximum of the separate callback and native live-content bills is false.

## Proof at common chronological cuts

Each traversal first calls `prepare_coefficient`. No native Counter exists
at that point. The previous traversal's frame has returned before the second
callback starts. Callback count backing therefore adds at most H_C to K.
The callback numerical slot peaks are bounded by L_R+J_R and L_I+J_I.

After callback return, its count scratch is unreachable, but its returned
coefficient remains one owned residue Word. The native loop then allocates x,
bringing the excess to two Words. Multiplication allocates at most four more,
including its returned offset, so the excess is at most six. At return from
multiplication only coefficient, x and offset remain. `subtract_exact` allocates
one leading Word. Native copy/countdown work therefore retains four excess
residue Words. It allocates no index Words. Offset and leading are freed per
source iteration, x per outer iteration and coefficient per traversal. Thus
entry live sets are restored before the second callback, and neither traversal
accumulates numerical live slots from the previous one.

The primitive multiply bound is PR2759's four-Word bound. Source inspection
also gives it directly: persistent scan and result coexist with at most two
addition temporaries, and the old result is freed before the next digit.
Canonical operands, fixed extent and high-bit margin remain its hypotheses.

PR2831's allocation induction gives retained slots equal to the maximum of
entry allocated slots and every completed live-slot demand. `free` erases
without shrinking the slot array. `zero` reuses an available slot first and
extends `words` only when every old slot is live. The demands just enumerated
are bounded by B_R and B_I. Every Word array has b+2 cells, and each arena
owns one permanent template. Hence total numerical backing is at most N.
Neither free nor callback return lowers that bound. A pending new Word array
before `words.append` fits the completed successful allocation's bound;
no count array is created during its initialization or erasure. This covers
interior allocation cuts as well as completed calls.

For completeness, the native Counter inventory is p+r+m for outer, source
and middle Counters. Replacing the middle Counter overlaps its cleared old
binding, adding m. A copy uses one block Counter, adding r; when S>1,
replacing a suffix Counter overlaps its cleared predecessor, adding 2s.
The two alternatives occur at different cuts, giving C. M>=2 guarantees
a leading copy of at least two blocks at x=0, so the copy overlap is reached.
The middle replacement is also reached through the repeated source loop.
Closed local bindings stay charged until replacement or frame return.

Native count backing is consequently K+C, with no callback-private count
scratch remaining. The first traversal frame returns before the second starts.
Taking max(C,H_C) across count phases, while retaining N across both, proves
the joint bound. This is not an assumption that independently computed
live-content maxima occur together.

## Attainment and invalid alternatives

Take M=5, U=G=S=1, b_R=4 and b_I=16. Entry has three live residue Words:
modulus, Ring one and the callback's borrowed operand two. There are no
live or allocated index slots. The callbacks compute inverse(2)=3 through
the unchanged Ring algorithm. PR2759's ten additional Words are attained,
giving thirteen allocated slots which remain after scratch erasure.

The numerical arrays then occupy N=14*6+18=102 cells. The three borrowed
marginal count tapes occupy K=12. Native countdowns attain C=20, at a cut
where numerical arrays still occupy 102. Thus combined backing is exactly
134. At that cut only seven residue Words are live, so the numerical live
arrays including both templates occupy 66 cells. The largest simultaneous
live-content bill across the whole action is 114, attained in the callback.
Using it as backing therefore misses 20 cells. A 133-cell total quota rejects
the actual native execution; 134 passes.

Warming the residue arena to 32 slots and the index arena to sixteen, then
freeing those Words before entry, changes backing to 536 with the same
114 live-content peak. This rejects forgetting historical slot extents.
Allocating ten temporary index Words during the callback instead yields
314 combined cells. Their blank slots coexist with native countdowns too.

A separate callback uses two 34-cell Counters and releases them before return.
Their borrowed source Count adds 34 cells to K, so K=46 and H_C=68.
The released case reaches 216, within K+N+max(C,H_C). Retaining the two
cleared Tape objects after each callback leaves 136 cells reachable by the
second traversal. The complete ADD permutation still succeeds, but backing
reaches 304, violating the released-case bound of 216. This is a counterexample
to dropping the no-capture premise, not a defect in the native algorithm.

## Evidence and boundary

The replay authenticates all source bytes and Git blobs before executing
the five unchanged source modules. The count observer uses weak references
and samples creation and every write, including pending constructor bindings.
Numerical samples sum actual array lengths after allocations; the source
argument above covers pending Word interiors. Fixed module bindings and
instrumented methods are restored in finally blocks, including quota failure.

Forty-one successful fixtures cover every input basis position of the 25-bit
minimal fibre, both suffix branches, repeated outer/middle extents, M=3,5,9,
borrowed residents, aliased extents, warm slots and both callback categories.
Each checks the complete output against an independent integer-address ADD
permutation, entry numerical bytes/ownership, restored heads and count release.
The captured callback is an additional successful negative example.

The quantified result depends on the written lifetime proof and callback/source
contracts. The finite fixtures alone do not establish them universally.
Extent preparation and its numerical/count overlap are outside this entry
boundary. Complete selected coefficients, GL64 payload, physical lowering,
exception safety, total private A, recursive/outer reserve and supplier admission
remain unproved here. No new kappa or formal-kernel result is claimed.
