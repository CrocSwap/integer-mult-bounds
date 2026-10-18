# A physical ordered shear with unit carry

## Quantified contract

Fix a direction e in {-1,+1}. One fixed finite program accepts positive canonical
LSB-first binary descriptors P,Q,G,S and an arbitrary Boolean source of volume
V=P Q² G S, in lexicographic order (p,x,g,y,z). Its owned output moves the source
bit at that coordinate to

```
(p, x, g, (y + e(x+1)) mod Q, z).
```

The source and descriptors start as marked strings with heads at their first
symbols. The output and all eight scratch tapes start entirely blank, at their
own origins. The fourteen roles are distinct. Input strings have exactly their
declared lengths. Origins may differ independently between tapes.

The program preserves every input symbol, returns each input head, and leaves
the output marked with its head on the first bit. Every scratch tape is wholly
blank and its head returns to its own origin. Additional unaddressed tapes remain
untouched. These are valid-input, successful-execution guarantees, not a general
exception-safety or malformed-input recognition theorem.

Each direction uses 552 instructions, fourteen tapes, and the seven-symbol
alphabet retained from David Arias's PR2776. Instructions are local symbol
branches/writes, unit head moves, fixed jumps, halt, and reject. Neither assembly
nor the running program receives an unmetered runtime callback, computed address,
host integer loop, ordinary-swap oracle, or input-dependent transition table.

For c(N)=24N-7 popcount(N)+15 bit_length(N)+12, the exact transition count is

```
T = c(P)+c(Q)+c(G)+c(S) + 36V + 20P Q²G + 28PQG
    + 50PQ + 19P + 7Q + G + S + 111 <= 449V.
```

The exact sum of visited spans, including erased cells and preserved inputs, is

```
3V + P+G+S+2Q + max(bit_length(P),bit_length(Q),bit_length(G),bit_length(S))
   + bit_length(P)+bit_length(Q)+bit_length(G)+bit_length(S)+28 <= 41V.
```

Both displayed uniform bounds attain equality at P=Q=G=S=1. This means that these
coefficients are sharp for this program and this all-input linear majorant. It
is not an optimality statement about other machines or encodings.

## Inherited components and the exact change

The byte-pinned PR2776 machine, counter converter, split/merge macros, and cleanup
macros remain unchanged in predecessor/. Its proof supplies the binary-to-unary
invariant and the exact conversion cost c(N), including canonical shrink at
powers of two and the final decrement. All code and that proof remain available
for review. The new argument below checks the changed phase and its composition
with those retained components; it is not an independent formalization of them.

The predecessor starts its split lengths (L,R) at (Q,0), visits Q pairs
(Q-x,x), and resets after the final transfer. The new program makes one initial
unit transfer, giving (Q-1,1). At the boundary after each fibre group, it checks
whether L is zero *before* transferring. For L>0 it transfers one unit and
continues. For L=0 it resets (0,Q) to (Q,0), transfers one unit, and advances p.
The same phase serves gathering and emission.

## All-size phase and endpoint argument

At the start of the group for x, the invariant is

```
L=Q-1-x, R=x+1, 0 <= x < Q, L+R=Q.
```

The descriptor conversion and initial transfer establish it at x=0 because Q
is positive. For x<Q-1, L is positive. The next transfer gives the pair for x+1
without changing the total. At x=Q-1, L=0 and R=Q. The zero branch performs the
complete reset and one transfer, establishing the initial pair for the next p.

Thus every phase visits exactly Q groups per p, including Q=1. No numeric x
counter or head-index comparison occurs in the finite controller.

For each (p,x,g), the forward gather appends L blocks of S bits to A and R
blocks to B. The matching emit consumes R blocks from B followed by L blocks
from A. A source block y<L moves to y+R; a block y>=L moves to y-L.

Both equal
(y+x+1) mod Q. The pieces remain consecutive within their buckets. Both phases
visit p, x, and g in the same order, so no prefix consumes another prefix's piece.

In the inverse program, gathering takes R then L blocks, while emission takes
L then R. A block y<R moves to y+L; a block y>=R moves to y-R. Both equal
(y-x-1) mod Q. The two coordinate permutations are mutual inverses. Their
ownership contract preserves the source and creates a distinct output; a caller
that discards an input copy must separately pay its erasure.

At x=Q-1, R=Q and L=0. The whole fibre passes through one bucket, with identity
endpoint. Empty-segment branches work unchanged. This also handles the only
fibre when Q=1; there is still an independently owned output.

For all bits, the two copying paths have equal length and never branch on a
global payload property. The argument therefore applies to arbitrary Boolean
payloads, not just basis vectors or the test patterns.

## Ownership, cleanup, and complete cost

Static inspection finds no write instruction on the source or descriptor roles.
Input/output rewinds use their retained markers. The bucket scans consume every
piece and erase each consumed bit. Unary reset erases each former delimiter.

The last reset and transfer leave (Q-1,1), with all nonblank cells at or left of
their heads. The unchanged backward erasers therefore clear both lengths and
their markers completely, including their older tails. The remaining cleanup
contracts follow from the retained macros with unchanged entry invariants.

Here is a path-count comparison with the source proof, not a fitted coefficient.
There are Q-1 positive boundary branches and one zero branch per p per phase.
Each positive branch performs one unit transfer. The zero branch performs one
Q-unit reset followed by one unit transfer. Thus there are still Q unit transfers
and one complete reset. Moving the zero test before the transfer only reorders
the same unit operations.

The final branch moves its transfer after the reset.
The emitted table contains another copy of the seven-instruction transfer macro
in each phase, but a runtime path executes exactly the old number of transfers.

Each fibre still copies Q records in gathering and Q in emission. Both length
heads start at their right markers, and the sum of their rewind distances depends
only on L+R=Q. The first actual record retains the same S-head saving, even when
the first segment is empty. P/G/S loop counts and descriptor conversions do not
change. Combined bucket length remains V, so their termination, rewinds, erasure,
and visited-span sums do not depend on the changed division between A and B.
Final L/R cleanup distances also have the same sum Q+2.

The only additional executed operation is the initial seven-instruction transfer.
Adding seven to the predecessor's exact ledger gives the displayed T. This
comparison counts preparation, preserved-source access, all copies, markers,
restoration, erasure, branches, jumps, and halt. There is no recursive child,
frame change, or external assembly operation inside this kernel. Allocation of
these roles in a larger caller remains a separate premise and cost.

The space invoice also remains unchanged. L initially visits its Q-unit extent
during conversion and seeking; R reaches Q units in each phase. A and B together
hold V payload cells, and both retain their marker spans even for an empty bucket.
All other tape extents match the predecessor. These facts give the displayed
span sum, including cells that later become blank.

Finally, c(N)<=44N for N>=1, and each positive monomial in the displayed ledger
is at most V. Hence T<=449V and span<=41V. At the smallest input, direct
substitution gives 449 and 41. Translating any origin changes no local step,
marker relation, or span width, so both identities hold for independent origins.

## Binding to the existing bit interface

The frozen qadic_streams.py add_high specialization has high=Q, before=P,
middle=G, suffix=S, reversed_fields=False, coefficient e and constant carry e.
Its affine endpoint is exactly y+e*x+e modulo Q. No rational scaling or completed
interchange call occurs. For Q=1 it returns the input object; our kernel has the
same value endpoint and also creates the declared owned output.

This is an actual nonzero low-digit carry case, not an invented offset. For any
odd radix q>=3, low_x=q-1 and low_y=1 with coefficient +1 give new low_y=0 and
carry +1. Applying coefficient -1 to low_x=q-1, low_y=0 gives new low_y=1 and
carry -1. The implementation tests these source routines at three radices and
two widths. This does not assert that every such low-coordinate pair occurs at
a selected GL64 caller site or that the tests execute a complete source catalogue.

## Independent validation and limits

The coordinate model unpacks each output ordinal and gathers its unique input
preimage. It does not share the split traversal, unary counters, or compiler.
The inherited separate dense interpreter executes only serialized local
instructions; a sparse interpreter supplies an additional whole-bank check.
Exact predecessor comparisons use the same input shapes, payloads, and origins.

Mutation controls include a correct zero-carry endpoint, reversed orientation,
missing initial/reset carry, retained scratch, missing rewind, changed payload,
and nonlocal movement. A cost-only control returns every endpoint correctly but
adds two unit moves. Saved receipts record executions, not independent truths.

The all-size theorem rests on the above invariant and path count with the retained
counter lemmas. Finite tests corroborate the implementation. There is no external
human review, proof-assistant verification, full selected payload replay, complete
physical caller, H2 discharge, supplier admission, or new multiplication exponent.
Arbitrary fixed carries, runtime-sized carries, rational scaling, reverse field
order, and physical role allocation remain outside this claim.
