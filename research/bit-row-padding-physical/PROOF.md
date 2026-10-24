# Complete-fibre compatible-row padding on fifteen fixed tapes

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
The compatible-row semantics are Jose Manuel's PR2786, and the wider strict
volume criterion and bounded Count adapter are Nick Petalas's PR3503. This
package does not claim either arithmetic fact as new.

## Contract and machine

Let P,R,S,B be positive integers with S<=R, V=PRB, and
R'=S ceil(R/S), Delta=R'-R. Input is an arbitrary binary function serialized
in lexicographic [P][R][B] order. B is the COMPLETE body/spectator fibre,
including the other high field and any supplied intermediate coordinates.
P contains all preceding complete coordinates. No coordinates are silently
dropped or replaced by one representative bit.

The source and four descriptors are borrowed. Descriptors are canonical
least-significant-first binary words (last digit1). Each tape has a unique
left marker followed by its finite word, then blanks. Every head initially
points one cell right of its own marker; origins can differ independently.
Nine work/call tapes begin blank; a distinct final output tape begins blank.
These are fifteen physically distinct tapes, not fifteen aliases of a bank.
A fixed physical tape is the ownership identity; distinctness is an input
ABI premise, not an uncharged pointer comparison. The Python simulator checks
identity at construction and resumption to reject aliased representations;
that structural validation is not an extra physical routing instruction.

The controller creates the padded word [P][R'][B], inserting Delta complete
zero rows AFTER the R genuine rows of EACH prefix. It exposes this tape and
a canonical binary R' at CALL. The callee borrows padded input, row count and
all original borrowed state, returns a distinct owned tape [P][R'][B], restores
all borrowed contents/heads, and closes its own scratch. The private P,R,S,B,Delta and temporary control
tapes are not exposed to the callee and must remain untouched. Its completed endpoint
preserves each row ordinal and permutes inside that row. Consequently padded
rows are again zero. More generally an explicitly proved zero-preserving
rowwise endpoint can satisfy the same adapter contract.

The controller then copies genuine rows, checks and discards all added row
bits, rejects wrong returned lengths, and clears all nine owned work/call
tapes. Final output is a distinct owned [P][R][B] tape. Borrowed source,
descriptors and their backing/heads are unchanged. All heads are at their
own local first cell and all owned visited cells except fixed left markers
and final output are blank.

The callee's row semantics and source preservation are premises. Local
zero checks do NOT establish them. A returned all-zero word can pass the
shape checks while destroying genuine data; the verifier intentionally
exhibits this. Test snapshots/oracles are not executable semantic admission.
The callee itself, its time/space/precision and native admission are excluded
from the adapter theorem. If the callee violates the contract, local malformed
return guards may reject; successful semantic correctness is not promised.
For canonical marked tapes, data/extent/length/padding-zero failures enter a
fixed cleanup epilogue: all owned work and partial output are erased, and
original borrowed heads rewind without changing their bytes. Post-CALL head
guard failure instead quarantines state: a violating callee may have moved
a head left of its marker, so a one-direction rewind is not a valid recovery
argument. Foreign alphabet symbols or misplaced left markers also quarantine.
No recovery of bytes maliciously changed by a callee, arbitrary exception
unwinding or drop-in replacement of Python try/finally is claimed. On invalid
inputs the valid-volume bound is not asserted; cleanup pays the actual finite
word lengths it scans. Canonical positive descriptors/valid callee are the
success theorem domain.

## Fixed control and positive-width invariant

machine.py emits one constant table, without input arguments. Its only
instructions are local read-and-branch, one-cell write, unit move, fixed jump,
CALL and DONE. Each references at most one fixed tape. The alphabet is
{0,1,left,blank}; one local instruction is one transition for this model.
The simulator's counters/dictionaries and visited-cell observation are a
representation of this machine, not runtime arithmetic instructions.
No instruction decodes extents, addresses a nonlocal cell, slices data,
multiplies, divides, allocates tapes or chooses an input-dependent unbounded control program.
Static labels and assembly resolve once, independently of P,R,S,B.

Four descriptor passes copy bits to one reusable temporary binary tape.
The finite copy state remembers only the last bit, so empty/zero/noncanonical
positive descriptors reject. Each descriptor is rewound and preserved.
The temporary is decremented to zero, emitting one unary1 per decrement.
A decrement flips low zeros to ones, clears the next one and, if that one
was the highest digit, removes it. It rewinds only the digits just crossed.
Thus the temporary remains canonical or empty, and yields exactly n unary
ones for descriptor n. There is no4096-bit or other width capacity.

Planning first scans unary R and S together, rejecting S>R, then rewinds.
It consumes all R row marks and cyclically traverses S group marks. At each
consumed mark it increments a canonical binary R' counter. If R ends on a
group boundary, Delta is empty. Otherwise it drains the remaining group,
appending one Delta mark and incrementing R' once per mark. Exactly
S ceil(R/S) positions are counted. This is a paid sequential implementation
of round-up, not a host division.

At every prefix the first row loop processes exactly R rows and the second
exactly Delta rows. For every row the unary B counter advances once per bit
and rewinds at its right end. Padding copies genuine bits and writes literal
zeros on additional rows; restriction copies genuine bits and requires every
additional source bit to be0. The prefix counter advances once per complete
pair of loops. End-of-word guards enforce the exact supplied volume. All
counter rewinds and payload head moves are actual local instructions.

At CALL the original source, descriptors, padded source and R' are all
rewound. After return, the machine locally steps left and reads the unique
left marker on each exposed tape, then steps right. This checks returned
head positions; it does not compare borrowed contents. Restoration of those
contents remains the callee premise. Restriction then runs only AFTER CALL.

## Uniform costs, including setup

Every positive extent is at most V: P,R,B<=PRB and S<=R. Also
Delta<R and R'<2R. Binary descriptor length ell(n)<=n. The following bounds
count local instructions in the fixed table, excluding the callee.

For n consecutive binary decrements, let z(t) be the number of low zero
digits in the positive value t. Each digit position j is crossed in the
borrow chain only when 2^j divides t. Hence
sum(t=1..n) z(t) = sum(j>=1) floor(n/2^j) < n.
The total number of changed/crossed digits is <2n. Rewinding follows only
those crossed digits plus at most two boundary cells: it never scans the
original full descriptor width on each decrement. Copy, rewind, trim and
unary-output overhead are bounded by60n+40 instructions, directly allowing
eight instructions per borrow/return edge and all fixed tests. Four
conversions therefore cost at most240V+160.

For increments1..r, the number of carried low ones sums to less than r.
Counting writes, local branch/goto, carry moves and rewind gives at most
16r+8 instructions. Group planning includes the cover comparison, all group
rewinds, remaining-row and group tests, Delta writes, and counter increments.
Every group rewind is charged to its consumed marks; total consumed group
marks is R'<2R. A conservative bound is80R+80<=80V+80.

For one transform, every processed genuine/added cell has at most ten
instructions in the bit loop. B rewinds cost at most3(B+2) per row; row and
prefix guards/rewinds cost at most a further twenty per row plus twenty per
prefix. Since B,R>=1 and processed row count is PR'<2PR,80V+80 bounds a
transform including source/output rewinds and terminal guards. The two
transforms therefore cost at most160V+160.

Nine owned tapes are cleared by one forward erase scan and one backward
rewind, at most eight instructions per cell plus fixed boundary overhead.
Their maximum occupied lengths total at most
P+R+S+B+Delta+max(ell(P),ell(R),ell(S),ell(B))+ell(R')+2V+2V < 11V+2.
Thus100V+200 is a conservative cleanup bound; the eight post-CALL local
boundary checks cost24. Summing these deliberately loose allocations is
less than2048V+2048 transitions for all V>=1. This bounds the actual table,
not the host Python interpreter's elapsed time.

For space, all four unary extents and Delta total at most5V; the two binary
work/count extents total at most2V+1. Original source, padded source,
returned source and final output occupy at most6V altogether. Borrowed
descriptors have total length at most4V. Include all fifteen fixed markers,
the blank cells observed at right boundaries and any one-cell guard/rewind
overrun: fewer than64V+64 distinct visited cells on all tapes suffice.
The callee must deliver a returned word of length PR'B and must charge its
own other scratch separately. No global-origin span is counted: independent
tape origins are translation-invariant.

These bounds need not be optimal. They prove supplied-width linear movement
and preparation with fixed tape/control resources. For the T=10Nf sequential
matcher lifetimes, the adapter charge is the SUM of these per-call bounds
at their actual complete volumes. It cannot replace the2T raw bodies,
3T body additive maps or T older high-part swaps. Physical P3 constants,
precision, the full native body and outer admission remain separate.

## Actual source boundary and discriminator

#4989's generator uses the borrowed branch exactly when2k<e=w-1. For
f1,q5,w4,k1,S3, e3>2 and R=q^k=5. It schedules
inner_borrow, row_pad, body_sub, raw_reverse_swap, body_add,
raw_reverse_swap, body_rsub, inner_return, row_unpad, older_high_swap.
This adapter supplies the padding/restriction interface around that completed
inner body; it does NOT implement that body. The source owners462 and461
remain distinct; the latter is a complete spectator encoded in the fibre.

At P2,B6, sixty genuine bits become seventy-two padded bits. Twelve actual
zeros are written in two six-bit rows. The old addressed interpreter's
zeros=[0]*(total-size) is valid row metadata, but is not this physical bit
allocation; no predecessor bug is asserted. All sixty individual dirty basis
inputs and an all-one translated-origin fixture test the complete fibre,
together with boundary cases around binary carries. A synthetic completed
rowwise reversal witnesses the adapter composition only.

The conditional proof applies at arbitrary positive extents, including the
actual much larger body/spectator product. P2,B6 is a discriminating interface
fixture, not an execution of the full GL64 cover. Small q5 is source scheduling
calibration, not proof of the source's large-prime admissibility bound.
