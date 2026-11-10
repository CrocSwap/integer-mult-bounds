# Resident doubling on one physical ribbon

This scoped circuit construction and traffic proof was produced by Nick Petalas.
The construction answers the same-ribbon SCALE question in Ali Romman's PR6530.
It does not supply a new complete caller bill or a new kappa.

## Contract

Fix a record width W >= 2 and a positive payload dimension D. One resident
complex field occupies 2D consecutive W-bit two's-complement records on a
single ribbon, in the predecessor's interleaved real/imaginary order. Each
signed component x satisfies -2^(W-2) <= x < 2^(W-2), the exact-doubling
no-overflow condition. The other resident ribbon is arbitrary. Both evacuated
owner slots are zero. All ribbon heads and the clean finite-control bits begin
at zero. The owner head may be anywhere legal.

The output doubles every component exactly, returns the active ribbon head
and control bits to zero, and leaves the other ribbon, all owner cells, the
owner head and the separate carry tape unchanged. The compiled schedule uses
one of the two available finite-control bits. It needs no new tape, clean
payload field, read from an evacuated owner, or field movement.

The written construction applies to every finite W and D. The supplied emitter
admits 2 <= W <= 64 and 1 <= D <= 64 to bound its materialized instruction list.
Finite tests cover the explicitly reported domains, not every admitted input.

## Bit map and exact inverse

Write a record as bits b_0,...,b_(W-1), least significant first. Swap adjacent
positions (W-2,W-1), then (W-3,W-2), down to (0,1). This is the left cyclic
rotation

    (b_(W-1), b_0, b_1, ..., b_(W-2)).

Each swap is the three CNOTs i->i+1, i+1->i, i->i+1. Finally apply CNOT
W-1->0. The resulting low bit is b_(W-1) XOR b_(W-2); every higher bit is
the previous lower bit. The no-overflow condition makes the top two input
bits equal. Consequently the new low bit is zero and this is exact signed
doubling. On arbitrary bit strings it remains an invertible linear map.
Reverse the full CNOT sequence to obtain its two-sided inverse.

The retained source SCALE 2 circuit performs the same cyclic rotation by
successive swaps with position zero, followed by the same sign-clearing
CNOT, separately in its two records. The new schedule changes the rotation
factorization to neighboring swaps and puts both records on one ribbon.
The source circuit, its arithmetic contract and its previous two-ribbon
control-cache result retain their predecessor credit. The verifier compares
the new map, the literal retained source route and a separate logical gate
interpreter on all 129 basis columns, including the source carry coordinate.
This is a dependency check for the new construction, not a new predecessor
audit or a claim to its original result.

For a CNOT c->t, read c into a zero control bit, seek t, read and conditionally
write t, seek c and read c again to clear the control bit. The target differs
from the control, so the second control read restores the control bit. The
operation is reversible for arbitrary data. All seeks expand to unit moves.
The schedule is fixed by W,D and the instruction pointer; no payload-dependent
head index, numeric cardinality oracle or hidden payload access is used.

## Exact new traffic

There are 3(W-1)+1 = 3W-2 CNOTs per record. Each costs three reads and one
write. For N = 2D records, reads are D(18W-12) and writes are D(6W-4).

In the first record, the adjacent swaps cost 8(W-1) moves, with W-2 initial
moves and W-2 moves between successive swaps. The final long CNOT costs
3(W-1). Thus the first record costs 13W-15 moves and ends at W-1. Every
subsequent record costs 13W-14 moves, because its first control is W-1
positions beyond the preceding exit. The final head return costs NW-1.
The total movement is N(14W-14)-2 = 28D(W-1)-2.

Adding reads, writes and moves gives

    new(W,D) = D(52W-44)-2.
    new(64,D) = 3284D-2.

The predecessor's retained width-64 SCALE 2 route costs 9840D before its
staging transfers. The new resident circuit therefore saves 6556D+2 even
against that local term alone. This is an operation count, not wall time.

## A complete comparison with identical entry and exit

Use the actual selected word's adjacent events 10481..10483, with zero-based
indices:

    ADD   256 <- 256 - (1/2)257
    SCALE 257 <- 2*257
    ADD   257 <- 257 + (3/2)256

Both named fields can be resident before SCALE and are needed again by the
following ADD. For the comparison fixture, field 256 occupies bank zero,
field 257 bank one, and the owner head is at the end of field 256. This is
a legal entry. We do not claim a patched full predecessor policy.

The old normalized path evicts both fields, executes the retained SCALE
staging/circuit, reacquires both fields into the same respective banks, and
returns the owner head to its entry. Try both eviction orders and both
acquisition orders. The other field's arbitrary data and all unrelated owner
cells are preserved. This supplies exactly the new path's physical endpoint.
The next ADD can bind its target/source tape arguments to those banks as in
PR6530. No physical bank swap is implied or free.

Here is the complete affine calculation for all D >= 1. Let L=128D. From
the end of field i to the start of field j the distance is
abs((j-i-1)L+1). Its affine coefficients are 128*abs(j-i-1) and +1 when
j-i-1 >= 0, or -1 otherwise. A whole-field clean transfer, including ribbon
rewind, costs 1152D-3 in addition to this seek. It performs six accesses per
bit and three traversals of L-1 cells.

The inherited SCALE staging costs its entrance seek plus
2688D-267, before the 9840D local circuit. To derive that staging term,
the source transfer reads/writes total 24WD. Its moves, excluding entrance
seek, are 3(2DW-1)+8(DW-1)+4(D-1)W = 18WD-11-4W.
This is the explicit increasing-record staging path, including all rewinds.
After reacquisition, returning from the end of field j to the end of field
256 costs abs(j-256)L. Every sign in these absolute values is fixed on
D >= 1, so these are affine proofs, rather than extrapolation from samples.

For eviction/acquisition orders 01/01, 01/10, 10/01, 10/10 the complete
costs are respectively

    17776D-280, 17776D-282, 17776D-278, 17776D-280.

The best stated normalized flush path costs 17776D-282. The resident circuit
costs 3284D-2, saving 14492D-280, positive for every D >= 1. At D=1 the
complete comparison is 17494 versus 3282, a saving of 14212 operations.
This is a minimum over those four explicit normalization paths only.
The verifier executes all four paths at D=1,2,3 with two payloads each,
checks their full tapes and heads, and matches the affine bills exactly.

## Limits and credit

Classical adjacent transpositions, CNOT swaps, reversible finite control and
two's-complement arithmetic retain their usual credit. The new contribution
is their charged same-ribbon SCALE implementation under this exact exclusive
owner contract. Ali Romman supplies PR6530's interface, open question and
comparison policy, PR6527's staging and PR6513/6511's scalar/tape lineage.
Credit Nick Petalas for the retained scalar circuits, Sagar Thakrar / PR3241
for metered tape work, DreamingOfClouds / PR6030 and all retained native,
owner, precision and compiler predecessors. Original source files and credit
lines are preserved in inputs.

Only SCALE 2 is implemented here. The full caller policy is not reoptimized;
native and reset flushes retain their original obligations. Uniform encoded-D
control, native semantics, precision/stock admission, complete supplier funding
and outer transfer remain open. No new kappa, selected-frontier change,
independent human acceptance or formal proof-kernel result is claimed.
