# Literal linear factors of the selected Gaussian MOVE on all columns

**Scoped enabling lemma. No new kappa.** Prepared for Jerry Chen / @CubeJerry
with substantial OpenAI assistance. Apache-2.0. CNOT decompositions, unary
clocks and split/merge routing are credited predecessor methods; the new
contribution is the complete source-bound literal join on the shared encoded
boundary, with both directions, all columns, complete costs and ownership.

## 1. Exact selected source and scope

At canonical `e54523517d0f03e58352e647c403a5af3e525a57`, the current #7000 native
word has zero-based event 24472 `["MOVE",415,3,99,false]`. The before/after
frames are `[]` and `[239]`. Its retained compiler lowers the exact map as a
right monomial, one positive C coordinate, and a left monomial. Their binary
matrix rows, with row bits indexed by logical coordinate, are

- right: `(239,129,130,132,136,16,160,192,256)`;
- left: `(3,5,9,17,32,65,129,1,256)`.

The source binder recomputes the actual recipe from the pinned word/frames;
these are not taken from a historical event or guessed from an abstract
profile. SOURCES.json pins every retained byte and its commit/path. The
programs implement only these two linear parts. They do not include either
quadratic/linear/constant phase, the right offset, the central C, or the full
MOVE. In the source monomial, the address action is Gx, not G^T x or G^-1 x.

The predecessor distinction is precise. #3834 checks a controlled-block
identity on finite dimensions. #5188 supplies a complete literal interchange
on separate binary descriptors, with its larger complete descriptor-length
bill. The fixed-tape ordered/affine shear packages already provide literal
linear-volume modular-addition kernels; at Q=2 a unit shear is one CNOT. At
Q=2^f, modular addition is not independent XOR of the f bits. #6992 already
supplies the serial-column monomial identity and its conditional direct-leaf
bill; its movement/numeric service remains structured, and its O(fV) bound
uses explicit long-record/metadata absorption premises. The selected monomial
tape lift already supplies the fixed GF(2) record list under inherited
movement propositions. None of these algebraic or routing ideas is claimed
new here. OVERLAP.md records the bounded current overlap gate.

The scoped result here supplies actual local instructions for both selected
matrices, deriving every varying guide from the shared five-code header. It
does not assume long coefficient fields or an unpriced transpose service.

## 2. Encoded interface and universal endpoint

Fix either construction-time choice `side='right'` or `side='left'`.
`compile_linear(side)` emits its entire finite graph before an input is read.
It returns `(code, alphabet)` in the pinned Builder format. HEADER is tape 0,
DATA tape 1, and private roles are the distinct tapes 2 through 26. There are
27 tapes and four symbols `{blank,0,1,|}`. Only local scanned-symbol branches,
one-cell writes, unit moves, fixed jumps and halt execute. Runtime parameters
never specialize the graph or select a variable collection of tapes.

HEADER begins with five canonical positive Gamma codes `f,r,P,S,w`, in that
order. Any symbols after this exact prefix are opaque and preserved. Let E
be the prefix's length. This is the same packed input interface as the
published literal native phase package at
`172f4535ce8dcff79f626410af845f757c1563be`; a later caller can retain its sixth
cutoff code as opaque trailing data. This program itself neither reads nor
establishes a cutoff.

DATA is exactly the complete lexicographic array `[P] x [2^f]^9 x [S]`, with
r Gaussian coefficients per address, each represented by w real bits followed
by w imaginary bits, MSB first. Equivalently, the proof treats its entire
payload as arbitrary raw bits. The bit volume is

`V = 2wrPS * 2^(9f)`.

The physical flattening places coordinate zero before coordinates one through
eight; the final S position, coefficient index, component and component bit
are innermost. Logical coordinate i is the f-bit integer
`a_i=sum_j x_(j,i) 2^j`. Thus a column vector has its logical coordinate i at
bit i, even though the packed integer's most significant group is a0.

Both public heads start at their own origins, and DATA has a blank at offset
V. Supply private owners blank from relative position -1 through the
per-role caps proved below, with all public/private roles genuinely disjoint.
Opaque exteriors, nonzero or negative origins, and previously allocated but
blank historical backing are permitted. Blankness/disjointness are admission
premises; the controller does not infer them from a few endpoint reads.

For every such entry, the selected graph terminates with the bit block from
`(p,a0,...,a8,s)` at
`(p,b0,...,b8,s)`, where

`b_i = XOR_(k with G_ik=1) a_k`.

Every coefficient/component bit retains its order and value. HEADER, all
heads, every private body/guard and all opaque exteriors are restored. DATA
is its original owner. The common grid and every numerical value are merely
permuted, so even most-negative signed fields are admitted; no intermediate
arithmetic headroom condition is needed.

A finite short or excess DATA body is detected during the initial clone,
before any public write. An invalid locally scanned header/payload symbol
also rejects through a missing local branch. On such detected failures DATA
and HEADER remain intact. Private cleanup, head return and retry after
failure are not promised. The semantic theorem quantifies over the valid
encoded entry and full blank-window premises, not arbitrary malformed or
aliased storage.

## 3. Fixed GF(2) decomposition and temporal order

For each of the two fixed matrices, row elimination uses operations
`row_target ^= row_control`. A row swap is three such additions. The
elimination records operations e1,...,eg, so

`E_g ... E_1 G = I` and `G=E_1 ... E_g`.

Every elementary matrix is its own inverse. Applying the recorded operations
in reverse temporal order therefore sends a vector to G times that vector.
The compiler checks the final identity matrix and reverses the word. It uses
the shorter of two fixed elimination orders, increasing or decreasing pivot
index; no runtime parameter enters this choice. The resulting words have
19 gates for the right matrix and 27 for the left. MATRICES.json retains the
exact words and graph identities. Direct evaluation on all 512 one-column
addresses additionally checks these fixed finite matrix identities.

For a given column, the gates retain this matrix order. Gates on distinct
columns operate disjoint bits and commute. Therefore running all f columns
of the first gate, then all f of the second, and so on, has exactly the same
address action as applying the matrix separately to each column. This is a
standard tensor/commutation identity; it does not make the f loop free.
The actual f loop is emitted and physically counted below.

## 4. Header-derived geometry and both CNOT directions

For a fixed gate let h<l be its two logical coordinate indices, and let j be
the current column, starting at zero. The higher physical address bit is in
coordinate h and the lower is in coordinate l. The array has the exact form

`[A_j] x [2_high] x [M] x [2_low] x [B_j]`,

where the final factor is a raw bit chunk and

`A_j=P 2^((h+1)f-j-1)`,
`M=2^((l-h)f-1)`,
`B_j=2wrS 2^((8-l)f+j)`.

All exponents are nonnegative for f>=1, h<l and 0<=j<f. Direct cancellation
gives `4 A_j M B_j=V`. For example, below coordinate l's bit j there are
`(8-l)f+j` coordinate bits, followed by the complete S/r/component payload.
Above coordinate h's bit j there are `(h+1)f-j-1` coordinate bits, besides P.
This derives the geometry from the exact packed convention without a
runtime address or stride oracle.

Gamma codes are decoded by literal prefix-controlled unary doublings. An F
tape retains f marks. Initial PREFIX starts as P, doubles h+1 times per F
mark and is halved once; MIDDLE starts as one, doubles l-h times per F mark
and is halved once. BLOCK starts as `2wrS`, then doubles 8-l times per F mark.
All multiplications use explicit nested unary loops, copied/erased with paid
returns. The two initial halvings divide even values because their total
exponents before halving are at least one.

After column j, F advances once. If another mark remains, BLOCK doubles and
PREFIX halves. The latter is even because j<f-1. MIDDLE remains unchanged.
At the last column no update occurs; F is returned, the three guides are
cleared, and the next fixed gate derives its own geometry. VOLUME is separately
generated once from the five fields and controls the complete initial clone.
No geometry guide is supplied as a free extra input.

For each prefix, the program consumes its two `2MB` high-bit halves into
LEFT and RIGHT. At each middle position it takes four B-bit chunks in order
Q00,Q01,Q10,Q11. A high-control CNOT maps low to low xor high, so the output
chunk order is `[Q00,Q01,Q11,Q10]`. A low-control CNOT maps high to high xor
low, so it is `[Q00,Q11,Q10,Q01]`. These are the permutations `[0,1,3,2]` and
`[0,3,2,1]`, respectively. Both are explicitly compiled according to the gate's
control/target orientation; neither direction is replaced by a transpose.

The first two output chunks append to LOUT and the last two to ROUT. After
all M positions, these complete high halves are merged left then right into
the other whole-field bank. Each Q bank is erased and returned immediately
when emitted. LEFT/RIGHT and LOUT/ROUT are erased and returned before the next
prefix. Thus the same raw-bit order within every B chunk is preserved. An
induction over middle positions and prefixes proves one CNOT pass; induction
over F and then the fixed word proves the universal endpoint.

## 5. Whole-field staging, ownership and return

The initial generated VOLUME clock copies exactly V public bits into A,
records each DATA advance on DTRACE, checks the following blank and returns
DATA. HEADER has already been returned by its own trace. Both originals are
preserved during every gate/column pass.

One MODE bit selects A-to-B or B-to-A. Each pass destructively consumes its
source bank and appends a complete V-bit target. At the end it checks source
exhaustion, returns the blank source and complete target heads, then changes
MODE. The next pass therefore never overwrites unread input and starts on
blank reusable target storage. Splitting, chunk transport, merging, bank
returns and erasure are all actual local instructions.

Only after every gate and column succeeds does the final bank overwrite DATA,
while erasing that bank and recording the return trace. It writes precisely V
bits and returns to the original public head. Remaining guides and MODE are
cleared; every owned guard is erased and its head restored. Auxiliary banks,
comparison-free work tracks and header trace were already returned blank by
their local invariants. This proves public preservation before commit and the
complete successful lifecycle. No free owner replacement is used.

## 6. Complete uniform instruction price

Every instruction, including goto and halt, costs one. For n symbols a rewind
costs `3n+3`; unary clear costs `7n+4`; unary copy with fixed repetition t,
appended e marks and erasure flag z costs `(6+5t+z)n+5e+7`. Consequently
unary doubling costs `47n+18`, halving a positive even n costs `15n+14`,
and `product(left,right,target)` costs `11LR+10L+7`. These counts follow by
summing the literal loops, not from wall-time measurements.

A raw B-bit destructive copy costs `11B+4`, or `14B+7` including a target
rewind. Stream emission of n bits, including erasure and source return,
costs `9n+4`. Summing the entire CNOT-pass body gives:

| Complete operation | Instructions |
| --- | --- |
| One high-half load | `28MB+14M+7` |
| One prefix, both loads/chunks/merges/local returns | `208MB+78M+45` |
| One pass through the next-column/finished branch | `58V+78AM+48A+16` |
| Next-column doubling/halving/jump | `47B+15A+33` |

Here B>=2 on the packed Gaussian ABI, AM<=V/8, A<=V/8 and B<=V/4. Thus a
complete pass plus a possible update costs less than `128(V+1)`.

For completeness, the initial geometry of a fixed h,l gate costs exactly

`124A0+124M+47B0 -36P -24RSw +28RS+10R +180f+44`.

The three generated extents, all intermediate doubles and all loop resets
are included. Its positive terms are bounded by `512(V+1)` using
A0,M<=V/8, B0<=V/4, RS<=B0/2 and f<=V. Final per-gate guide return/clear is
`3f+7(A_final+M+B_final)+15`, bounded by `32(V+1)`. Therefore every one of
at most 27 fixed gates, including all its f actual passes, has the safe bound
`1024 f (V+1)`. This deliberately loose allowance absorbs fixed jumps and
all gate boundaries.

The first-five Gamma conversions cost O(f+r+P+S+w+E), since strict binary
prefix values sum to less than each decoded value. Each value is <=V. The
VOLUME preparation, whole source clone/return, final public commit/return,
all remaining guide erasures and guard initialization/disposal together
cost less than `8192(V+E+1)` by the same unary prices. For example VOLUME
construction is
`47V+28P+40PR+40PRS-24PRSw+168f+83`, the complete clone is `20V+11`, and
commit itself is `16V+7`, before the fixed selection/retirement instructions.
These explicit helper formulas keep repeated control work in the bill.

Combining the 27-gate bound with the overhead, and V>=1024f for positive
f,r,P,S,w, yields the uniform complete bound

`T <= 65536 (fV+E+1)`.

The right program has fewer fixed gates, but no improved asymptotic claim is
attached to that constant. Program construction is input independent. Actual
entry production/transport, old-codec conversion, arbitrary strided packing,
phases, offsets, the C leaf and any complete caller remain additional work.
This is an O(fV+E) direct-leaf tariff, not an O(V) unrestricted-f affine rate
or a faster nonleaf recurrence.

## 7. Historical backing and repeated use

Each private role visits an interval starting at its own relative -1 guard.
MODE has cap 1. HTRACE and LENGTH each have cap E. Every other private role
has cap at most V, including blank endpoints: two whole banks, DTRACE,
VOLUME/AUX/DOUBLE, five input guides, three gate guides, four half streams and
four chunk streams. Temporary pre-halving guides are <=V/2 and every chunk
is <=V/4. No role count or origin depends on the header values.

There are 22 volume-bounded roles, two header-bounded roles and MODE, so the
sum of new private intervals is at most `22V+2E+51`. Including both public
tapes adds at most `V+E+2`, giving `23V+3E+53`. Both are bounded by
`64(V+E+1)`. If K0 is the actual corresponding pre-entry historical backing,
the full history at any time is at most `K0+64(V+E+1)`.

Erasure does not reduce history. Repeated calls at fixed origins retain the
union of each individual role's intervals, or its per-role maximum span,
then sum over roles. A later smaller clean call scans only its new finite
bodies and keeps its own current-shape time bill; it does not scan an old
blank capacity. Changed origins require their actual absolute interval
unions and paid transport corridors. Supplied source/opaque storage remains
in K0; it is never reclassified as free by a new wrapper object.

## 8. Evidence, limitations and Open next questions

The author direct oracle computes each output coordinate by XOR of the
selected original coordinates according to the actual matrix rows. It does
not execute the CNOT word to obtain expected payloads. All 512 one-column
matrix addresses are checked. Complete physical f=1 fields exercise r, P, S
and w variation, translated origins, arbitrary bits, header/exterior/head
preservation and malformed-cardinality rejection.

A separate dense C++ interpreter executes both actual fixed m=9 graphs on
all 262,144 addresses of a complete f=2 field. Both direct-matrix outputs and
all lifecycle checks pass. It cross-checks f=1 step counts against the pinned
reference interpreter. Changing every gate to process only the first column
still produces a complete, cleanly retired field but fails the f=2 oracle.
Reversing all control directions and corrupting final commit bits are also
detected. No reduced dimension, sampled address set or short prefix is
substituted for these full f=2 runs. Reusable-history evidence and independent
root/peer evidence are retained separately. Finite executions corroborate the
universal loop, algebra and cost proof; they do not replace it.

The next concrete composition is the exact retained MOVE24472: bind both
phase recipes and right offset around these G maps and the positive all-f C
leaf, then prove numerical admission, layout, public failure semantics and
the entire bill. The five/six-code packed interface permits a literal join,
but this package does not execute it. A general source caller still needs a
paid bridge from its old coded/strided representation, actual occurrence
emission and owner lifecycle. Faster nonleaf suppliers, recursion cutoff and
precision admission, and the remaining foundational assumptions stay open.
No selected certificate or accepted complete multiplication bound changes.
