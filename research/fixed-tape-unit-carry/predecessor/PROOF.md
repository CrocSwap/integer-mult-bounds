# A literal fixed-tape ordered shear at every extent

## Statement and exact boundary

For each direction `s ∈ {−1,+1}`, one fixed finite-control machine accepts four
positive canonical LSB-first binary integers `P,Q,G,S` and an arbitrary Boolean
stream in lexicographic `(p,x,g,y,z)` order, with

```
0 <= p < P,  0 <= x,y < Q,  0 <= g < G,  0 <= z < S.
V = P Q² G S.
```

It returns an owned output stream whose bit originally at `(p,x,g,y,z)` is at
`(p,x,g,(y+s*x) mod Q,z)`. The source and four binary descriptors are unchanged.
All temporary payload, unary counters and conversion work are erased, including
their installed markers. Every input head returns to its first encoded cell;
every scratch head returns to its original blank origin. The output starts
blank at its origin and finishes marked, with its head at its first bit.
Additional tapes are untouched. The program and physical tape count are
independent of `P,Q,G,S`, including arbitrarily long spectator dimensions `P,G,S`.
No ordinary-swap oracle, variable-size machine state or precomputed operation
trace is provided to the running controller.

This is a physical implementation of one already-known ordered-affine operation.
It is not a new algebraic routing lemma. In the exact selected source
`research/selected-bit-stream-routes/qadic_streams.py`, this is `add_high` with
`c=s`, zero carry, `before=P`, `middle=G`, `suffix=S`, `high=Q` and
`reversed_fields=False`. For `Q=1`, both functions are the identity on values;
the new machine still returns an independently owned output. The ordinary
interchange oracle in that predecessor is not invoked in this specialization.

The source's `rotate_fibers` explains the split/merge method; its README states
that the payload meter omits Python arithmetic, erasure and some head returns.
The contribution here is the literal finite controller and its complete
physical accounting. Generic ordered-affine routing, fixed arithmetic and
fixed-tape stream arguments retain their upstream authorship. The source
identities and review boundary are pinned in SOURCES.json.

## Machine model and finite compilation

`machine.py` defines the finite instruction forms: branch on one scanned symbol,
write one symbol at one head, move one head by ±1, jump to a fixed instruction,
halt, and reject. Only fixed tape numbers and finite instruction labels appear
in the compiled program. A branch has one destination for each listed alphabet
symbol and a fixed default. No instruction reads an integer head index, stream
length, simulation counter, Python list, callback or arithmetic expression.

Each instruction is directly one transition of a conventional multitape
machine: unused heads stay still, unchanged symbols are copied through, and a
branch's observed symbol determines the next finite state. A jump is a stay
transition. There is no RAM simulation or `log V` overhead. The interpreter's
integer coordinates, sparse maps, step limit and resource statistics describe
the external simulation; the program has no instruction that observes them.
The separate dense interpreter reads the serialized table and implements the
same local transitions without importing the producer.

The assembler runs before the input exists. It resolves a finite set of labels
and expands fixed macros. `build_program(inverse=False)` and
`build_program(inverse=True)` each produce **531 instructions on fourteen
tapes**, over the fixed seven-symbol alphabet
`BLANK, LEFT, RIGHT, ZERO, ONE, UNIT, MARK`. The last symbol is reserved and not
used on a valid execution. The only assembler parameter is this Boolean choice;
it does not accept runtime dimensions. TABLE.json contains the entire compiled
programs and is compared exactly to regeneration. Table size is independent of
the largest fixture or any theorem parameter.

Input descriptors and payload are supplied as standard marked strings, with
heads at their first cell. This is the input encoding, not free computation of
unary counts or a routing trace. Scratch tapes begin blank at the specified
origin. The machine installs and removes its own work markers. Valid-input
correctness assumes the declared payload has exactly V bits; incomplete streams,
noncanonical descriptors and occupied work cells are rejection controls, not
proof that the machine recognizes every malformed global input before writing.

## Binary descriptor preparation

The finite setup macro copies each canonical positive binary descriptor to a
single reusable work tape. A finite state remembers the last input bit and
requires that it is one at the right delimiter; this rejects zero, an empty
word and a redundant high zero. The original input is then rewound unchanged.

The work copy is decremented in place, with one unary mark appended per positive
countdown value. A borrow scans low zeroes, turns them into ones, and clears the
first one. When that one was the most significant bit, the right delimiter
moves left. At a power of two, the remaining low bits are all one; consequently
the representation stays canonical. At one, the final delimiter is erased and
the macro ends. A full zero test is never performed per iteration.

Let `L=bit_length(N)` and `pop(N)` be the number of ones. Across `N` decrements,

```
sum_{k=1}^N v2(k) = N − pop(N).
```

For the emitted instruction schedule the exact cost, excluding caller marker
installation and the final halt, is

```
c(N) = 24N − 7 pop(N) + 15L + 12 <= 44N.      (1)
```

To derive it, the initial copy and two rewinds cost `12L+10`; borrow/decrement
paths cost `7 sum v2(k)+14N+3(L−1)`; final cleanup and unary rewind add `3N+5`.
The resulting unary word has N marks followed by a right delimiter, and the
conversion work is empty. These are counts of the actual emitted branch,
write, move and jump instructions, not fitted timing coefficients. Finite
counter tests independently exercise power-of-two shrink boundaries and the
exact formula.

Thus preparing all four extents costs at most
`44(P+Q+G+S) <= 176V`: indeed `L<=N` and `pop(N)>=1` give
`c(N)<=39N+5<=44N`. This estimate holds for all positive extents, including
huge `P`, `G` or `S`. No spectator logarithm is multiplied into each payload
bit. The unary input expansion consumes space linear in V and is part of the
construction, not an assumed external descriptor service.

## Ordered split and merge

For fixed `(p,x,g)`, the target fibre consists of Q consecutive blocks of S
bits. In the forward direction, append its first `Q−x` blocks to A and its
last x blocks to B. Do this for every prefix in its original order. Rewind
A and B. For each identical prefix, emit x blocks from B and then `Q−x`
blocks from A. Each piece keeps its internal bit order.

An old target coordinate `y<Q−x` appears at `y+x`. An old coordinate
`y>=Q−x` appears at `y+x−Q`. Both are `(y+x) mod Q`. Each bucket holds
its successive prefix pieces in precisely the order used to consume them;
there is no random access or cross-prefix mixing. This argument holds for
arbitrary bit values, not merely for the tested payloads.

The inverse splits after x blocks and emits the second piece first. Its
output coordinate is `(y−x) mod Q`. Therefore the two machines are mutual
inverses on stream values. The source-preserving ownership convention means
that a caller must release an unwanted copy; that release is a separately
linear scan, not a claim that duplicated source storage disappears for free.

Two unary tracks encode the lengths `L=Q−x` and `R=x`. Their heads are at their
right delimiters between fibres. Initially they contain Q and zero marks.
After all G fibres for one x, the controller deletes one mark from L and adds
one to R, using their current end positions. It detects the final x iteration
by the LEFT marker immediately before the new, empty L delimiter. It then
transfers the Q marks back from R to L, restoring `(Q,0)` for the next p.
Every old delimiter beyond the new end is erased during these transfers.
Thus no numeric x value or comparison of head positions is needed.

P, G and S are separate unary loops. Their positions and limits are physical
tape data. The L/R tracks control the two pieces in both complete phases;
empty halves at x=0 and Q=1 take the same delimiter branches. There is no
division or host-language runtime counter.

Loop induction gives the prefix invariant: before each fibre, source and
bucket heads identify its next unconsumed piece, the P/G positions and L/R
lengths encode the current prefix, and all unary delimiters are intact. Before
each record, the S track is rewound; the inner loop then copies exactly S bits
and stops at its right delimiter. The L/R and G delimiter branches advance the
next enclosing position. The finite reset paths reestablish this invariant
for the next fibre and, after the final prefix, leave every bucket consumed.

## Full physical cost and workspace

All instructions, including branches and fixed jumps, are charged. A rewind
from relative head position h costs exactly `3h` transitions. A record copy
with an S-track initially at its right delimiter costs
`(11+consume)S+4`, where `consume` is zero during gathering and one during
emission. The very first record instead starts with the S head at one, saving
exactly `3S`. The remaining length-loop overhead for a segment of l records is
`6l+4`. These facts follow directly by counting the emitted instruction paths;
both bit values have paths of equal length.

The two complete phases have this exact ledger:

| Part | Transitions, summed over both phases |
| --- | ---: |
| Record copies and S rewinds | `23V + 8P Q²G − 3S` |
| L/R segment-loop overhead | `12P Q²G + 16PQG` |
| G rewinds and G-loop overhead | `12PQG + 8PQ − 3G` |
| P rewinds and P delimiter tests | `5P + 8` |
| L/R unit transfers, resets and enclosing advances | `42PQ + 10P` |

Their sum is

```
23V + 20P Q²G + 28PQG + 50PQ + 15P − 3S − 3G + 8.
```

Marker installation, initial L traversal, full-source and bucket checks,
bucket rewinds, output termination, final source/output rewinds, scratch
erasure and halt cost a further
`13V + 4(P+G+S) + 7Q + 96`. Adding the four conversions gives the exact
all-input running time, in either direction:

```
T = c(P)+c(Q)+c(G)+c(S) + 36V + 20P Q²G + 28PQG
    + 50PQ + 19P + 7Q + G + S + 104
  <= 442V.                                                   (2)
```

Every positive monomial and extent in (2) is at most V, as is one. Equation
(1) bounds the conversion sum by `176V`. Summing the displayed coefficients
therefore proves (2), with equality at `P=Q=G=S=1`, where the machine takes
442 transitions. This is an exact instruction-count argument, not an
empirical extrapolation. In particular, an arbitrarily large P or G does not
create a `log P` or `log G` charge per payload bit.

For space, count every cell between the origin and the furthest visited
position on each physical tape, even after its contents are erased. Put
`ell_N=bit_length(N)`. The fourteen tapes have these full-execution spans:

| Tapes | Total visited span |
| --- | ---: |
| Preserved source and owned output | `2V+4` |
| A and B split streams | `V+4` |
| Unary P, G and S | `P+G+S+6` |
| Unary L and R | `2Q+4` |
| Reused binary conversion work | `max ell_N+2` |
| Four preserved binary descriptors | `sum ell_N+8` |

Thus the total is exactly

```
3V + P+G+S+2Q + max ell_N + sum ell_N + 28 <= 41V.            (3)
```

No head visits a position below its own origin. The elementary inequalities
`ell_N<=N<=V` prove the last bound; equality again holds at the smallest
instance. The same bound covers every execution prefix, including blanked
but still visited bucket regions. Fourteen heads and the fixed finite control
are constant additional machine resources. Translating any tape's origin
changes neither (2) nor (3).

The source remains owned by the caller; the output is a distinct owned stream.
Gathering stores at most V bucket bits. Emission erases each consumed bit
immediately after writing it, so the total number of nonblank payload cells
on source, output and buckets is at most `2V+1`, including that single-copy
transition. This sharper observation is not substituted for the visited-span
bound. The final cleanup visits every unary/split tail through its origin,
erases its marker and leaves its head at that origin. The conversion tape was
already empty except for its marker and is cleaned in the same manner. Source
and descriptor markers remain unchanged; the marked output is rewound to its
first bit. No data-dependent collection of tapes, parked stack or allocator
is part of this operation.

## What remains open

This theorem discharges physical unit ordered shears, including arbitrary
spectator sizes, a source-preserving inverse, setup and scratch cleanup. It
leaves nonzero/data-dependent carries, rational scaling, reversed-field
interchange, complete selected owner routing, recursive role allocation,
ordinary leaf/bootstrap substitution and the stronger H2 time recurrence
outside its scope. It does not change any child histogram, selected κ,
precision assumption, complex supplier or analytic transfer theorem.

A fixed integer multiple of the unit shear follows by finitely many passes,
with its coefficient-dependent constant and intermediate copies charged.
This observation does not make a runtime-sized coefficient or rational
denominator free. No complete such caller is supplied here.

The all-size claims above rest on the algorithmic loop and step-count proofs.
The independently interpreted finite executions, source comparisons and
mutation controls provide implementation evidence, not a proof-assistant
verification of that induction or of the multiplication theorem.

Credit: the upstream ordered-affine stream lemma and Jose Manuel's selected
stream reduction supply the method and interface. The fixed controller and
checks are new work for David Arias with substantial OpenAI Codex assistance.
New work is Apache-2.0.
