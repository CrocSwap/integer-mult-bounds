# A paid fixed-three-lane reversal

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and scope

For every n>=0 and B>=1, SOURCE contains n consecutive B-bit records and
BD contains the canonical least-significant-first positive binary encoding
of B. These are supplied ports, each with a left marker, head at its first
payload cell, and blank tail. OUTPUT and the work ports are blank after
their reliable left markers. Every port, including unused ports1,2,3,
starts with its head at its own origin+1. All15 ports are distinct.
Ports1,2,3 may contain arbitrary payload after their markers and are untouched.
The local alphabet is {0,1,blank,left}; the compiled instruction table is
independent of n and B. The interpreter's step counter and low/high water diagnostics are observers,
not control registers of the mathematical program. The interpreter executes
only single-cell reads,
writes, unit head moves and finite jumps. Its host step cap is a verifier
stop, not an input to the mathematical machine.

On a valid call OUTPUT contains the same records in reverse order, preserving
bit order within every record. SOURCE and BD retain their payloads. All heads
return to their own origin+1; all work cells are blank. Output is caller-owned;
its later disposal is a separate caller obligation, bounded by a linear scan
of its nB cells if requested. Inputs may be based at independently translated
origins. This is a valid-input service; malformed encodings can reject with
partially written work and displaced heads. There is no transactional failure
restoration claim.

This realizes the fixed-T=3 instance of Nick Petalas's PR5148 construction,
with the physical costs that its abstract stable-lane model leaves unpaid.
Credit Matarener's PR3825 pass obstruction, James Reed's PR3839 finite census,
and the retained PR5090 local instruction Builder/Tape semantics. No universal
multitape lower bound, full bit-free supplier gain, or selected-frontier update
follows.

## Local control and refinement

The retained unary routine copies BD to TEMP, decrements its canonical binary
value until zero, and appends one unit to B per decrement. It preserves BD,
erases TEMP, and returns both descriptor heads. The initial scan copies one
B-bit record at a time from SOURCE to DATA and appends one unit to N. A blank
SOURCE cell is accepted only at a record boundary. Thus N has length n and
DATA is the original record sequence. S starts at unary1.

At stage i, put s=3^i. The invariant is: DATA is partitioned into consecutive
original-index blocks of length s, with the final block possibly shorter;
each block is internally reversed, and blocks are in original order. Heads
start at their origins and every lane is empty. The coverage loop compares
N and S by local synchronous scans. If s>=n it terminates.

Otherwise split transfers consecutive chunks of at most s records cyclically
to lane0, lane1, lane2. Chunks remain ordered within each lane, so this is an
actual stable split. Each transferred source cell is erased. The unary S and
B tapes drive every chunk and record loop. No payload record is fabricated for
an absent position. After rewinding the empty DATA and populated lanes, merge
transfers one chunk from lane2, then lane1, then lane0 to DATA. Absent tail
chunks are skipped by reading their blank current cells. Every full group
becomes the reversal of the corresponding three original blocks. A final
one- or two-block group is also reversed because only its real lane chunks
are emitted. Each lane is consumed in its own stream order: the merge is stable.

Hence DATA has the same invariant with block size3s. The literal tripling
loop consumes S and writes three units to NEXT per unit, then consumes NEXT
back to S. Induction proves the invariant at every stage. The first s>=n
occurs after k=ceil(log_3 n) stages for n>=2, with k=0 for n=0,1. DATA is then
one reversed block. Final transfer consumes it into OUTPUT; fixed cleanup
scans erase N, S, B and all auxiliary cells and return the heads.

For n7, s1 gives records2,1,0,5,4,3,6, and s3 gives6,5,4,3,2,1,0,
exactly PR5148's first example. The digit-complement and block-reversal
constructions agree because complementing the next ternary digit reverses
the order of these three already-reversed subblocks, including the last
incomplete group.

## Complete local-action bound

Let L=floor(log_2 B)+1 and k as above. Count each table instruction, including
reads, jumps, writes and head moves, as one action. A conservative bound is

    T <= 256 ((n+1)(B+1)(k+1) + B(L+1) + 1).

This is a written upper bound, not a fitted measured slope. The following
summands account for the whole execution. A rewind over h payload positions
costs at most3h+5. A row copy/consume, including the B rewind, costs at most
16B+12. Unary conversion costs at most32B(L+1)+16L+32. Initial copy/counting,
source/data/N rewind, and final payload transfer are together at most
40nB+24n+32. At one nonterminal stage, the2n row transfers and chunk dispatch
cost at most40nB+48n+48; the lane/DATA rewinds cost at most12nB+40.
Coverage scans across the run cost at most12n(k+1)+16(k+1). Tripling and its
transfer cost at most48s+32 per stage. Since sum_{i<k}3^i=(3^k-1)/2<3n/2
for n>=2, all tripling costs are at most72n+32k. Final cleanup costs at most
16(B+n+3^k+L+1)+80; n0/1 uses3^k=1. These deliberately loose summands fit the
displayed bound (including B=1,n=0). In particular runtime width is paid;
there is no constant-time B-bit word operation or free lane interleaving.

## Retained backing, setup and output

The15 role objects and fixed419-instruction program are constant setup.
No tape is allocated during execution. If K0 counts already allocated tape
backing, newly visited storage is bounded by

    6nB + 7n + B + 2L + 60.

This conservatively counts SOURCE, DATA, OUTPUT and each of three lanes at
nB individually. It does not sum only simultaneously live lane payloads:
each lane can retain a different historical high-water mark. N costs n;
S and NEXT each reach3^k<3n for n>=2 (at most1 for n<=1); B costs B; BD and
TEMP cost L each. Markers, terminal blank visits and the n<=1 exception fit
the60 allowance. Thus retained backing is at most K0 plus this expression,
even though the dictionary simulator retains blank written cells after erasure.
This is a tape-cell statement, not a Python allocator-byte claim. Borrowed
input production, input descriptor production and later output disposal are
explicit caller costs, not hidden inside this service.

## Open next questions

A complete bit-free supplier must compose this reversal with its other
permutations and numerical consumers and pay their combined bank and costs.
First bind one actual supplier endpoint to the present record layout; pass
optimality alone does not establish a numerical gain. Heterogeneous runtime
lane capacities would require a separate fixed-bank encoding and scheduling
contract; this theorem fixes three lanes.
