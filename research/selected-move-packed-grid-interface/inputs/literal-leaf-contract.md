# A literal positive C tensor leaf on the packed selected native field

## 1. Source-bound scope and exact ABI

At canonical `e54523517d0f03e58352e647c403a5af3e525a57`, the selected #7000
native word has zero-based event 24472 `["MOVE",415,3,99,false]`.
Recomputing its actual before/after Clifford frames and source lowering gives
rank one. The retained independent Gaussian interpreter confirms that the
positive central factor has columns `((1+i)/2,(1-i)/2)` and
`((1-i)/2,(1+i)/2)`. Thus it is exactly

`C = (1/2) [[1+i,1-i],[1-i,1+i]]`.

This is the same C as Jose Manuel's #3091 and the current coded leaf #6967.
It is not an unnormalized Walsh butterfly. Entrance/exit monomials are still
separate; this package does not execute the complete MOVE. Source pins and
credit are in SOURCES.json and NOTICE.md. Rank one is one selected coordinate
per column: for positive column width f the central operator is
`C^(tensor f)`, not a single C. Every f factor is implemented, low bit first.

The supplied packed ABI is the first-five-field interface of the literal
native phase package at CubeJerry commit
`172f4535ce8dcff79f626410af845f757c1563be`, extended by one cutoff field.
HEADER contains six positive canonical Gamma codes, in order:

`f, r, P, S, w, cutoff`.

Here r is coefficient multiplicity, not source Fourier rank. Let E be the
total length of these codes. DATA is the complete lexicographic array
`[P] x [2^f]^9 x [S]`, with r Gaussian coefficients per address. Each has
w signed two's-complement real bits followed by w signed imaginary bits,
MSB first. All coefficients share an arbitrary fixed common grid, unchanged
by this program. Write `N=P S r 2^(9f)` and `V=2Nw`.

Require `w>=2` and `f<=cutoff`; both are physically checked. DATA is exactly
V bits followed by a blank. HEADER may have opaque symbols after the sixth
code. Both public heads start at their origins. Supply 27 genuinely distinct
private tape owners, blank from one cell before each origin through the caps
in Section 6. Opaque exteriors are preserved on successful legal calls.
Origins may differ or be negative; the controller never decodes them.

This is an explicit packed boundary, not the full old #6967 ABI. That provider
uses a 23-value length/unary-prefix/LSB descriptor and three-bit coded LSB
component fields with delimiters. A caller must supply the exact semantic
packing, component orientation, delimiter and header bridge, with its full
cost and ownership contract. Reversing individual already packed components
is linear, but the old codec and arbitrary strided packing are not silently
implemented here. The first five new fields match the published phase ABI;
its opaque-tail contract permits preservation of the added cutoff code.

## 2. Universal accepting and failure contract

For every legal encoded entry, suppose each output component of every
executed C axis is integral on the common grid and lies in
`[-2^(w-1),2^(w-1)-1]`. Then the fixed graph replaces DATA by the exact positive
`C^(tensor f)` on all f bits of coordinate zero. All eight other coordinates,
prefixes, suffixes, coefficient indices and absolute phase are preserved.
HEADER, every head, private body/guard and opaque exterior is restored;
DATA remains its original owner.

At each executed scalar row the program rejects exactly a nonintegral half
or an out-of-range w-bit result. A finite missing or extra DATA bit is detected
by the header-derived clone before numerical execution. Width/cutoff failures
reject before the clone. These rejections precede every DATA write, so the
original public field/header remain intact. Missing local branches are
explicit reject endpoints in the reference interpreter. Failure-time private
retirement, head return and same-bank retry are not claimed. This is a weaker
failure lifecycle than structured #6967, not its full drop-in export.

The domain is a prefix condition: final tensor-image fit alone does not
establish it. A credited sufficient condition from #3091 and its Gaussian
reserve/norm predecessors is that input components are divisible by
`2^ceil(f/2)`, bounded by M, and `2^ceil(f/2) M <= 2^(w-1)-1`.
This supplies all integral signed prefixes. Those reserve/norm results are
inherited, not new claims here. A caller can instead prove its actual
correlated prefix conditions.

For a concrete obstruction to endpoint-only admission, the real f=2 fibre
`[1,0,0,1]` has final `C tensor C` image `[0,1,1,0]`. Its first low-bit-axis
pair `(1,0)` nevertheless produces nonintegral halves. The exact program
must reject it even though the final image is integral and fits at w=2.

## 3. Literal acquisition and generated geometry

`compile_leaf()` has no runtime arguments. Its 6,826-location graph uses 29
fixed tapes and `{blank,0,1,|}`, with only scanned-symbol branches, one-cell
writes, unit moves, fixed jumps and halt. Compile-time loops enumerate fixed
bit/carry possibilities, never input-sized code. Varying counts and geometry
stay on tapes.

The first five Gamma codes become unary guides by repeated `v -> 2v+b`
copies. Strict binary prefixes sum to less than the represented value, so
these conversions cost `O(f+r+P+S+w+E)=O(V+E)`. The first value's canonical
binary word and bit length are also copied. Cutoff is copied only in binary,
with a unary bit length. Comparing lengths and, only if equal, MSB words
checks `f<=cutoff`. An arbitrarily large represented cutoff thus costs O(E),
not its value. HTRACE records every public header advance and restores its
head without an origin oracle. All comparison words are retired afterwards.

For axis j, `0<=j<f`, the selected bit is bit j of coordinate a0. Its physical
halves have

`A_j=P 2^(f-1-j)` prefixes and `U_j=S r 2^(8f+j)` Gaussian coefficients

per half. Thus `2 A_j U_j=N`, including all spectator and coefficient fields.
The program constructs Sr marks, doubles that guide eight times per F mark,
and doubles the P guide f-1 times, obtaining U0 and A0. Before each subsequent
axis it doubles U and halves A by consuming mark pairs. Every halving is even:
`A_j=2 A_(j+1)` for j<f-1. F's head controls precisely f axes. No update occurs
after the last, and no stride is supplied by host arithmetic.

The source clone uses A0 prefixes, two halves each, U0 coefficients per half
and two w-bit components each. It therefore reads exactly V bits, detects
shortage at a required read and excess at the next cell, and restores DATA
through its paid trace. It does not copy an arbitrary malformed tail into
a finite private frame. All numerical work starts on the private clone.

## 4. Scalar C arithmetic and exact guards

For `a=ar+i ai`, `b=br+i bi`, the four numerator rows, ordered left real/imaginary
then right real/imaginary, are

`(+,-,+,+), (+,+,-,+), (+,+,+,-), (-,+,+,+)`

on `(ar,ai,br,bi)`, all divided by two. These are credited #3091 rows.
Four reusable MSB component buffers are scanned from their LSB ends. For a
fixed row epsilon and carry c, the program emits

`d=(c+sum epsilon_i x_i) mod 2`,
`c_next=floor((c+sum epsilon_i x_i)/2)`.

Each row has three plus signs and one minus, so the signed bit sum is in
`[-1,3]`, and carries `{-1,0,1,2}` are closed. All sixteen bit tuples for each
carry become fixed local branches. Negative division is floor division in
those compile-time constants, not truncation. Induction on processed bits
gives the usual exact low-digits plus carry invariant.

After w bits the four source heads are at their guards. Moving each forward
once returns it to the original MSB sign bit. Two more carry steps read those
sign bits. NUM therefore holds w+2 numerator bits, LSB first. For
`L=2^(w-1)`, the actual numerator lies in `[-4L+1,4L-3]`, within the w+2-bit
signed range. This identifies the modular result with the actual integer.

The lowest NUM bit must be zero. After erasing it, the highest extra bit
must equal the retained sign bit; this is exactly the condition that the
integer half fit w signed bits. The w retained bits are emitted backwards
to restore MSB order, erasing NUM. Thus both guards are necessary and
sufficient. No w-bit unhalved numerator is materialized; for example,
`C(3+3i,3+3i)` succeeds at w=3 although numerator six needs another bit.
Each source component returns to its origin and persists through all four
rows; then all four are explicitly cleared.

## 5. Full arrays, tensor order and public commit

Two fixed private field banks alternate through one MODE bit. For an axis,
each prefix consumes its two complete `2U_j w`-bit halves into LEFT and RIGHT.
Their U_j Gaussian pairs align on every spectator and coefficient index.
The scalar operation builds separate LOUT and ROUT streams, which are
appended in original half order to the other whole-field bank. All four
suffix streams are erased and their heads returned locally before another
prefix. There is no uncharged gather or scatter.

After the prefixes, the program checks exhaustion, returns both field heads,
flips MODE, restores PREFIX and advances F. Prefix induction proves the C
action on bit j. Axis induction proves the f-factor tensor. Distinct factors
commute algebraically, with no extra phase or scalar; the chosen low-bit
order nevertheless fixes the actual signed-prefix acceptance domain.

DATA remains the borrowed original during every axis. Only after all f
successes is the final private field committed to the same public owner,
while erasing that bank and building the return trace. DATA returns; all
remaining guides and guards are cleared. This proves normal retirement and
public failure atomicity under the explicit entry premises.

## 6. Complete time and retained historical backing

Every table instruction, including jumps and halt, costs one step. A local
rewind through n symbols costs `3n+3`; unary clear costs `7n+4`; unary copy
with fixed repetition t, appended e marks and source-erasure flag z costs
`(6+5t+z)n+5e+7`. Doubling through DOUBLE therefore costs `47n+18`.
The even unary halving loop costs `15n+14`. All movements and returns are
inside these prices.

The Gamma conversion prefix sums are bounded by their represented values.
All first-five parameters are <=V. Cutoff is handled by at most constantly
many scans of its encoded word/length, so the header guard has O(V+E) cost.
The geometric sums of all SUFFIX doublings before the first axis are less
than U0, apart from the O(8f) fixed per-double overhead; PREFIX's are less
than A0. Subsequent U doublings have total old length <U_(f-1), and subsequent
A halvings have total old length <2A0. Since all these counts and 9f are
bounded by V, even all geometry setup/updates together cost O(V+E).

For the numerical loop, direct instruction counting bounds one `c_component`
by `64w+128 <=128w` for w>=2: the initial width-guided seek, w digit transitions,
two sign extensions, parity/range scans, output emission and all returns are
included. Each ordinary digit uses at most thirteen instructions. The four
input loads plus clears cost at most `84w+44`. Four scalar rows, pair control
and component handling therefore cost at most 640w per pair. There are
N/2 pairs per complete axis. All half loads, stream merges, whole-field
returns, suffix/prefix loops and their resets are linear scans of V; their
loops have fixed depth and every range is nonempty. A conservative count
places a complete axis, including its geometry update when present, below
`8192(V+1)` instructions. The actual table has no per-bit scan of a full
descriptor or whole address word.

Separately, header/initial geometry/source clone and final commit/retirement
are each below `8192(V+E+1)`: the preceding exact unary-helper prices and
constant-many full scans give much smaller coefficients, and this allowance
also covers all fixed guard and branch instructions. Hence

`T <=8192[f(V+1)+2(V+E+1)] <=65536(fV+E+1)`.

The second inequality uses f,V>=1. This is a complete direct-leaf bill:
source access and return, geometry, every axis, copying, full staging,
installation and erasure are charged. It is not a faster nonleaf tariff.
The fixed program construction is input independent. Entry acquisition,
old-format conversion, source packing and transport to the entry heads are
supplied caller work and must be added where required.

For backing, put `U*=Sr 2^(9f-1)`, `A*=P 2^(f-1)`, and
`C*=max(A*,U*,f,r,P,S,w)`. Relative to its own origin, each private role visits
only `[-1,cap]`, including the guard and blank endpoint, with these caps:

| Role | cap |
| --- | --- |
| A, B, DTRACE | V on each role |
| MODE | 1 |
| HTRACE, LENGTH | E on each role |
| DOUBLE | C* |
| F, R, P, S, WIDTH | f,r,P,S,w respectively |
| FBIN, FLEN | ell(f) on each role |
| TBIN, TLEN | ell(cutoff) on each role |
| PREFIX, SUFFIX | A*, U* respectively |
| LEFT, RIGHT, LOUT, ROUT | `2w U*` on each role, using the maximum U* |
| AR, AI, BR, BI | w on each role |
| NUM | w+2 |

Every cap in the twenty volume-type roles is <=V, except NUM's harmless
additional two cells; six code-type roles are <=E, and MODE needs one cell.
Including 27 guards/endpoints, their total allowance is at most
`20V+6E+57 <=64(V+E+1)`. Here K0 counts the actual pre-entry historical
backing of the 27 private owners only. Their backing at every time is at most

`K0+64(V+E+1)`.

For a complete 29-owner history statement, include all public history in K0
and add at most `E+V+2` public head positions. The same loose envelope remains
valid, since `21V+7E+59 <=64(V+E+1)`. Supplied source/opaque entry backing is
included in actual K0; a test fixture's unpriced construction is not a theorem
about free caller acquisition.

Erasure never subtracts historical cells. All successful-call writes are
blank again at return; older tails are already blank from prior successes.
Thus a smaller clean call needs no scan of old capacity and retains its own
current-shape time bound. At fixed origins repeated calls use per-role maxima,
then sum. Under changing origins retain absolute per-role history unions and
the caller's paid transport corridors; do not replace them by maximum current
volume. Whole-tail blankness and genuinely distinct owned windows are entry
premises, not inferred from a few local reads or fresh wrapper identities.

## 7. Exact source transfer, evidence and unresolved interfaces

The selected native tensor convention packs coordinate i as
`a_i=sum_j x_(j,i) 2^j`. The central rank-one compiler factor acts on i=0 in
each column j. The identity of its two source columns, with denominator two,
therefore identifies the operator implemented above exactly, including phase
and normalization. The source binder checks the entire retained local recipe;
this does not claim that this package implements its two surrounding factors.

For a current coded caller, an admitted semantic bridge must identify these
actual bits, preserve the complete other coordinate/spectator/coefficient
fields, preserve the common grid and signed width, and supply the six values
above, including the actual cutoff. It must price real packing and coefficient
orientation. The generic #6967 domain contains shapes that are not already
this complete packed nine-coordinate tensor; those calls are not silently
included. A supplied view cannot make strided payload movement free.

The author checker uses a direct tensor-row Gaussian polynomial oracle,
not the executable butterfly/carry algorithm. It tests complete m=9,f=1
packets, endpoint values, coefficient/spectator multiplicities, both named
arithmetic failures, cardinality/width/cutoff failures and a 2049-bit threshold.
The separate C++ interpreter executes the same fixed 6,826-location table on
the complete actual m=9,f=2 array: 262,144 addresses, 2,621,440 bits, and
704,382,528 table instructions. Its output matches the independent direct
tensor formula, and every header/head/private/exterior check passes. It
cross-checks the original interpreter at f=1. A mutant that executes only
the first axis still retires correctly but fails the f=2 tensor oracle,
directly detecting rank-one/f=1 conflation. No reduced dimension substitutes
for that actual full-field f=2 execution.

Independent root/peer evidence is recorded separately in REVIEW.md. Finite
tests support, but do not replace, the universal graph invariants and cost
proof above. Open obligations remain: full old-codec and placement bridges,
failure retirement if required, entire source MOVE/caller composition,
global producer/cutoff/precision admission, nonleaf speed and the other
foundational assumptions. No selected certificate, new kappa or unconditional
integer-multiplication theorem is claimed.
