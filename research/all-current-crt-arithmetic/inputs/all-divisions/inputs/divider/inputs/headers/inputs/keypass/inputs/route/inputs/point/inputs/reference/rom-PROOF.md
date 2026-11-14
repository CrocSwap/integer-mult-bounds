# Executed control for a source-bound Beneš ROM producer

## Statement and assumptions

Fix integers h>=1, W>=h+3, N=2^h, 1<=s<=N and a nonempty ordered
list of m offsets, m>=1, each 0<=a_i<s. The source layer selector
satisfies 0<=j<2h-1. Inputs h,s,j are `L`, exactly W little-endian bits,
`R`; the offset tape is `L`, m repetitions of W little-endian bits followed
by `|`, then `R`. W is the physical width of h, not a decoded interpreter
argument. These are padded records; canonical minimum-length headers are not
claimed. Inputs are finite, start at their unique left markers, have no
trailing nonblank data, and occupy distinct physical tapes. Every private
and output tape is blank. There is a fixed number of tapes and a fixed
finite symbol alphabet.

`producer_program()` emits the same instruction tuple without any input
argument. On this domain it halts with all borrowed bytes preserved, every
head at its left origin, all private backing blank, and two owned outputs:

* `layers`: L, then for layer k=0,...,2h-2 the concatenation of the N bits of
  each offset's source network, in original list order, followed by `|`; R.
* `rom`: L, exactly the mN bits of selected layer j in that order; R.

The source is PR4100 `benes(rotation(N,s,a_i))`, with its deterministic
component orientations and its schedule 0,1,...,h-1,h-2,...,0. Duplicate
offsets remain separate rows. This is a uniform construction for the stated
encoded domain, with a finite exact calibration at the actual key caller.
It is not a complete CRT evaluator, an E(p,ell) comparison or a new kappa.

## Inherited result and changed implementation

ToikY's PR4192 at 519d811cc48693ad9969d6d7994bef3940167005 already gives the
heap-node arena layout, explicit DFS stack, deterministic-source refinement,
owned output and charged arena scans. Its simulator receives decoded h,p,
mirrors scalar control in Python integers, and `Arena.access` returns
`int(...,2)`. Its header/scalar bit lowering is a written theorem rather
than executed microcode. Those earlier results are credited premises, not
re-proved novelty here.

The new program uses those same five-field `(node,kind,layer,index,value)`
records and the same top-down, then bottom-up schedule. Each field has W
bits. We reverse the bits **within each word** relative to PR4192's big-endian
fixture; keys, record order, represented integers and Boolean root tables
are unchanged. W>=h+3 bounds all node/index/sentinel values, and kind<=4.
No cell-tariff equality with the predecessor is asserted for this different
literal instruction encoding.

The rotation permutation is generated directly into root P. For x<s,
start at x and perform a_i single increments with wrap at s; for x>=s,
keep x. Thus all padded wires are fixed. This uses encoded loops, not a
host-generated permutation or stored truth table.

## Primitive simulation invariant

Each scalar role is a fixed-width bit record. At the entrance and return of
`copy`, `clear`, `constant`, `inc`, `dec`, `double`, `half`, `equal`, `less`
and `zero`, all involved heads are zero. The definitions imply:

* `inc` and `dec` propagate one carry/borrow from low to high bits; overflow
  or underflow takes a rejecting halt. Valid control invariants exclude it.
* `double` shifts left with a one-bit carry; `half` shifts right and writes
  zero at the highest bit.
* Equality scans every bit. `less` replaces its flag at each differing bit,
  so the highest differing bit decides unsigned order.
* `copy` moves one bit at a time and returns both heads. All call sites use
  distinct source and destination roles.
* `repeat` and the two while macros re-evaluate their conditions on tapes.
  They are assembler macros only: their Python bodies run once to emit
  fixed instructions. Runtime bounds are never host loop counts.

All runtime register values are symbols from a fixed finite set. The only
machine instructions are one-cell read/write/move, finite-symbol assignment,
finite equality/not, a finite branch, a static jump and halt. PC/head/list
positions belong to the emulator configuration. They do not feed into a
machine operand. The interpreter watchdog is a verifier timeout, not an
accepting branch or a complexity proof.

`access` compares each of four key words against every record, reads or
writes the value on the unique match, scans to the end even after the match,
and returns all heads. Its found flag rejects missing/duplicate matches.
There is no decoded address or host-indexed record access. Arena storage is
built by the same encoded depth/node/kind/layer/index counters. The number of
records is J=N(h^2+3h+1); each contains five W-bit words.

## Complete source refinement

The padded rotation is a permutation. At a node with permutation P, the
source's two matchings are x xor 1 and INV[P[x] xor 1]. The program retains
that order. A newly reached vertex receives its color **before** being pushed
onto the shared stack. The stack top is a bit record; pop decrements it,
reads the slot, and restores its sentinel N before visiting neighbours.
Every vertex is pushed once and the top never exceeds the node size or N.
The pop/colour/ordered-push transition therefore agrees with the retained
source, including coincident neighbours and parallel matching edges.

First/last rows are color[x] xor parity(x) and color[INV[x]] xor parity(x).
The two child permutations use exactly node 2v+color[x], index floor(x/2),
value floor(P[x]/2). The source's perfect-matching argument makes each child
a permutation. Consequently the omitted redundant quadratic distinctness
scan is unnecessary for these **generated rotations** and their children;
this is not a compiler for arbitrary unvalidated supplied permutations.

The leaf case size2 writes P[0] twice. By induction, the top-down loop
constructs the same child data and endpoint rows as PR4192. The bottom-up
loop chooses child parity x and child index floor(x/2), copies its layer,
and adds one to the parent layer index. Thus every root table equals the
canonical source table, rather than merely realizing an equivalent network.

Each offset is compiled in a reused arena. Its full root network is appended
to an owned spool before the arena is erased. A final repeated sequential
scan transposes offset-major networks into layer-major output, iterating the original offset stream until its end marker, with no
numeric offset-count register or list-length capacity. This preserves
both list multiplicity and within-layer wire order. The selected row is
written simultaneously; it is never reconstructed from an oracle. The spool
and all scalar roles are then erased. Offsets, modulus, selector and h are
read-only throughout. This proves the stated success endpoint and ownership.

Malformed inputs may reject with dirty owned work or nonreturned heads;
there is no arbitrary-error rollback claim. Unbounded/nonterminated records,
aliased tape roles and initially dirty owned backing are outside the domain.

## A conservative complete instruction and storage bound

This proof prices the new primitive program, not host execution time.
Let A=N^2+2Nh^2+(37Nh-35N)/2 be PR4192's complete logical-access bound.
The new valid-rotation path has no more accesses: it replaces root input
copies with the same N puts and omits the redundant validation gets. Each
access takes fewer than 1000 W(J+1) primitive instructions. This follows by
expanding the four key-bit loops, value loop, marker rewinds and found test;
each loop iteration has fewer than 50 instructions and each return traverses
at most W or 5WJ cells. Each other scalar macro takes fewer than 100W
instructions, except initial repeated doubling (at most 100hW).

Arena creation/disposal uses O(WJ) instructions per offset. There are
O(A+J+N^2+Nh^2) scalar macro invocations per offset: the rotation loop has
at most N(s-1)<=N^2 iterations; source traversal loops are bounded by the
same tree/stack counts as the inherited access census. Transposition scans
mN(2h-1)^2 bits, with O(W) counter work per bit. Header, scalar-bank and
successful disposal costs are included. The deliberately loose explicit
upper bound

    T <= 10^6 W^2 (m+1) (N+1)^3 (h+1)^4

therefore dominates initialization, all scalar/control operations, every
arena scan, both serializations and all successful cleanup. It does not
charge borrowed payload initialization as free production; descriptor
construction is outside this interface. No comparison to E(p,ell) follows.

Peak represented cells are at most

    100(W+2) + 5WJ + mN(4h-1) + 10(h+1) + input_cells.

The 100 scalar-role allowance exceeds the fixed bank. Terms include the full
arena, spool mN(2h-1), complete layer output of the same size, selected ROM
mN, markers and separators. Spool/arena ownership is not productive credit.
The retained caller may reuse the ROM, but this bound does not amortize an
unproved number of future queries. Final output disposal is a separate
literal erase scan with its own observed instruction count.

## Actual consumer and remaining boundary

For h=3,s=5, offsets[0,2,4,0], the output is five 32-bit layers. Selected
layer index 2 is handed directly, as the same owned cell list, to the
unchanged #4795 Service with target bit position 2. ROM values remain 0 or 1. Its query ABI uses h_query=4,s_query=2 and
addresses the same flat 32-bit table as two rows of16; the producer used four
rows of8. The equality is of flat ordered cells, not an identification of
these different header parameters. The existing service observes the actual
current y at each of its three epochs. No query answer is supplied by the
verification oracle. The service returns the ROM unchanged; the new erase
program subsequently disposes of it and of the full layer output.

This joins one generated actual row to the existing fixed key port. A
variable-geometry key adapter, full descriptor production from current CRT
coordinates, all five repair layers, binary lowering of the whole new
symbol machine, full E allocation and outer/native/precision contracts are
not established. The retained supplied-ROM key proof remains its own premise.
