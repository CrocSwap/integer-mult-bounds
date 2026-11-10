# Whole-low-domain carry and low commit on the supplied complete-stream ABI

This is a source-bound fixed-tape component theorem. It does not admit the
selected multiplication supplier, implement a homogeneous high-coordinate
route, or prove the literal selected caller's presentation/reordering cost.
All source pins refer to canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`; the executable dependency list is
in SOURCES.json. Predecessor proofs of the decoder, rotation and low commit
are retained dependencies, not newly claimed results.

## 1. Quantifiers, source matrix and physical input

Before runtime, fix an integer s>=1, N=8s, D=N^2, and an odd prime q. From
the actual frame506 in the pinned #589 frame bank form

    S8 = [B^T | A^T] = transpose(frame['B'] + frame['A']).

Here A and B are the frame's two four-row rational bases. This is exactly
`generator.generate` in #4989, including its source-frame fingerprint, not
the transpose matcher or a choice of a different image/kernel basis. The
source's addressed factors act on row coordinates on the RIGHT. Its
`carry_shift` records visit every row-major cell before `low_type_commit`;
the positive direction uses S8 and the negative source direction reverses
and inverts its entire homogeneous factor word. Thus the two source matrices
for this theorem are

    A_source = S8 tensor I_s, or (S8 tensor I_s)^-1.

The symbol A_source here is distinct from the frame's kernel basis A. We
write it simply as M below. It is fixed before the input arrives. The
source inverse has denominator dividing four, so every odd q is compatible
with both source matrices. Choosing an enormous q needed by a future whole
supplier remains a separate task; no small fixture admits that supplier.

Let L be the lexicographically ordered complete list GL_N(F_q), T=|L|, and
b=ceil(log2 q). Runtime inputs are a positive canonical odd binary Q and a
positive canonical binary Z. The source specialization is Q=q^(w-1), w>=1;
the component also works for other odd Q. Put

    H = Q^D Z,  V = T H,  K = T D b,  ell = bit_length(Q).

The original owner is an arbitrary complete Boolean stream indexed in order
by

    (G0, H[0], ..., H[D-1], z),

where G0 runs through L, every high coordinate independently runs through
[Q], and z runs through the complete [Z]. This is precisely the full-array
layout specified by #5487's `bit-full-fiber-low-commit/PROOF.md`. Its source
and the Q,Z descriptors have LEFT/RIGHT markers and heads at their first
bits. The other declared private tapes are independently owned and wholly
blank, at independently chosen origins. Unused tapes may contain arbitrary
spectator data. These are a successful-execution interface; the machine
does not certify an unbounded blank tape by inspecting its first cell, and
invalid-input rejection need not undo an already modified owner.

N, s, q, D and T are compile-time constants. In particular s is NOT an
unbounded runtime column width hidden inside the asymptotic constant. The
finite compiler's fixed m*c embeddings in #4359 can use such a frozen s.
A distinct runtime column multiplicity can be included among complete
trailing coordinates inside Z only once this contiguous layout has been
supplied. Flattening that trailing tuple is a mathematical indexing identity;
this package does not supply or price a conversion from the literal selected
caller's different tape order. It is one fixed matcher stage, not the entire
astronomical compiled matcher list.

## 2. Exact target and the direction distinction

Reduce M modulo qQ using its rational denominators, all units. For canonical
G0 define

    pi_M(G0) = G0 M mod q, entrywise in {0,...,q-1},
    C_M(G0) = (G0 M_mod(qQ) - pi_M(G0))/q mod Q.

The numerator is divisible by q. The theorem is that the returned original
owner has push permutation

    B_M: (G0,H,z) -> (pi_M(G0), H+C_M(G0) mod Q, z).

Every payload bit participates, with no sparse-input or tagged-record
restriction. All external descriptor/spectator tapes and heads return,
and every private tape is blank again at its entry origin.

The source route with M^-1 uses freshly computed pi_(M^-1) and C_(M^-1).
The flag `inverse=True` means B_(M^-1). It does NOT mean the inverse of B_M.
Indeed B_M^-1 would first recover G0=pi_M^-1(G0') and subtract C_M(G0) from
the high coordinates. There is no reason that equals C_(M^-1)(G0').

The full matrix route has a separate homogeneous high action H -> H M.
Entrywise modular arithmetic gives

    (G0+qH) M = pi_M(G0) + q(H M + C_M(G0)) mod qQ.

Thus the correct full route is B_M AFTER that homogeneous action. Only those
complete routes for M and M^-1 are mutual inverses. Homogeneous execution,
including its earlier-target ordinary interchanges, is outside this theorem.
The emitted carry leaf uses its positive rotation in BOTH source directions;
the possibly negative carry is already represented modulo Q. Tests of the
negative leaf orientation are adversarial controls, not a full-route claim.

## 3. Source carry envelope and finite compilation

For one output column and one old low row, let w_j=4 M_jc, let
R=sum_j w_j g_j, let l=R/4 mod q be its canonical low digit, and put
k=(R-4l)/q. The exact carry is k/4 mod Q. Replacing the rational matrix by
its modular representative modulo qQ alters the divided numerator by a
multiple of Q, so this identity has the same modular meaning as §2. It
does not use a rational floor in place of modular reduction.

For S8, the entries are integers, the positive column sum is at most four,
and the negative column magnitude is at most one. The integer carry is in
[-1,3], so k belongs to {-4,0,4,8,12}. For S8^-1, the positive quarter-weight
sum is at most six and the negative quarter-weight magnitude is at most
four. Since 0<=g_j,l<q,

    -(negative_sum+4) < k < positive_sum

with the evident weak upper bound zero when the positive sum is zero.
Integrality gives -7<=k<=5. Tensoring adds zero coefficients and selects a
fixed lane; it does not add s nonzero terms. Thus the unchanged #5332 decoder's
[-7,12] domain covers every actual source column, every old low row and every
admissible q,Q.

`column_specs` selects at most eight contributing cache positions in each
row and pads the list with zero coefficients. The reduced N=2 verification
fixture additionally uses six explicitly written zero CONTROL digits after
its D real cached digits. These are owned control cells, not a dummy payload
coordinate. Actual N=8s uses C=D local cache digits, without that padding.
In general denote the local cache digit count by C. The generic fixture
compiler is admitted only if the unchanged decoder accepts every reachable
low aggregate; support<=8 and a coefficient norm bound alone are insufficient.

The unchanged #5487 type compiler enumerates all q^D candidate low matrices,
retains exactly the invertible ones, and computes the permutation pi_M by
right multiplication. This pre-input enumeration depends only on N,q,M.
It initializes the K-bit old cache in the same lexicographic order as the
payload blocks. No runtime lookup, division, host-selected carry or random
address instruction is introduced. Compilation may be enormous and is not
claimed practical. It is a finite explicit algorithm; its cost is not zero
and must be absorbed in a future fixed-program threshold before varying w.

## 4. Literal program and last-consumer invariant

The program uses D+26 tapes. Its instructions are only scanned-symbol
branches, writes of one alphabet symbol, unit head moves, fixed jumps,
halt and reject. The #5332 explicit-edge language is translated as in #6241:
one source move/write becomes that instruction and one fixed jump, all source
program-counter edges are relocated, and its five tape roles are injectively
mapped. The rotation's owner is mapped to the owned fiber tape, not the
parent owner. Linking replaces a component halt by a jump to its fixed
continuation; there are no runtime Python or semantic callbacks.

First the literal #5487 cache initializer writes the entire fixed old cache.
The machine reads the supplied Q descriptor. At Q=1 every high coordinate
has one value, so it goes directly to low commit. It still executes the low
permutation and full cache retirement. This is the already credited unit-ring
observation of #5985, applied at the whole-stage boundary.

For Q>=3, it converts Q into D unary counters and Z into a further unary
counter. Their nested loops write an H-unit fiber-length counter. A fixed
T-unit counter controls the complete low-type loop. None of H, Q^a or
Q^(D-a-1)Z is supplied by a host arithmetic call.

At the start of low block i the following invariant holds:

* The first i parent fibers have their complete high carry vectors applied;
  all remaining parent fibers equal their entry values. Low block order has
  not yet changed. The original owner head is at fiber i.
* The full K-bit old cache is unchanged, and its head is at the first digit
  of the same low type L[i]. All earlier cache reads remain available.
* The reusable payload and local cache tapes are blank, and the fixed extent
  counters are ready for the next complete fiber.

Copy exactly H bits to the owned marked fiber tape and return the parent
head by exactly H unit moves using the fiber counter. Copy this old type's
D b cache bits to the local raw-cache tape, preserving the full cache and
advancing its head to the next low block. Any fixture-only zero control digits
are explicitly written. The local cache has its required end marker.

For coordinate a=0,...,D-1, generate canonical binary descriptors

    P_a=Q^a,  S_a=Q^(D-a-1)Z.

The old cache is untouched while #5332 generates C_a+1 in owned descriptor
storage. #5849 then rotates the complete owned [P_a] x [Q] x [S_a] stream.
Hence it changes exactly high coordinate a, including a=0; no earlier axis,
dummy Q coordinate or OLD interchange is needed. The carry depends only on
the retained old low cache, not on any already changed high coordinate.
After each leaf, erase its offset descriptor, new-low scratch output and both
extent descriptors. The new-low scratch is owned control data; the canonical
low permutation was independently compiled from the same fixed source matrix,
so this scratch is not a new productive output or a borrowed input being lost.

After all D leaves, the whole local cache is still present. It is erased
only at this last-use boundary. Install the entire transformed H-bit payload
back into the same parent fiber, consuming and erasing the owned fiber and
both its markers. Advance the T counter. This proves the invariant for i+1.
In particular, the component does not invoke one leaf and infer the rest.

After T fibers, the owner and full-cache heads reach their exact right
markers. Return both, and erase every local extent counter and binary work
cell. The old global cache remains intact and is returned at its first bit.
Now invoke the actual #5487 low-commit program with its exact complete-stream
and full-cache ABI. It validates the full old cache, moves whole H-bit blocks
according to pi_M, installs the result into the original owner, and only then
erases that cache and all its own work. Its cache validation is an additional
last consumer, so early retirement immediately after a carry leaf is illegal.

Induction gives exactly B_M and the stated return/erasure contract. Every
copy preserves arbitrary bits, including correlations between fibers. The
argument applies to all complete inputs, not merely basis or random fixtures.

## 5. Paid extent arithmetic and rewinds

The runtime binary product generator is a nested unary traversal followed
by one literal binary increment at every leaf. This section bounds the actual
rewinds; no increment is treated as a free arithmetic operation.

For positive counter lengths n_1,...,n_k with product P, set
M_j=n_1...n_j and M_0=1. At level j there are M_j successful loop iterations
and M_(j-1) end tests. The branch, increment-of-that-unary-head and jump
contribute 3M_j+M_(j-1) transitions. Each complete rewind of a length n_j
counter costs 3(n_j+1), giving another
3M_j+3M_(j-1). Thus all loop control/rewinds at that level cost at most
6M_j+4M_(j-1)<=10P. All k levels cost at most 10kP.

Let r be the number of trailing one bits before a binary increment. The
emitted ripple and head return take at most 7r+10 transitions, including
growth through the right marker. Across P increments starting from zero,

    sum r = sum_(j>=1) floor(P/2^j) < P.

So the complete increments cost at most 17P. Marker initialization and
initial zero construction cost 12 more transitions. The generated binary
product therefore costs at most

    (10k+17)P + 12.

This remains valid for k=0, where the one leaf increments zero to one. It
does not introduce P log P. The predecessor binary-to-unary conversion,
including its rewinds and countdown cleanup, costs at most 44n for extent n.

For coordinate a, P_a and S_a use a and D-a nested counters, respectively.
Their complete construction is bounded by

    (10D+34)H + 24,

because P_a,S_a<=H. Each generated binary extent is retired by scanning its
actual binary digits to RIGHT and erasing back through LEFT. An ell-bit
marked word costs at most 7ell+7 for that operation. This scan explicitly
admits ZERO and ONE; the inherited unary-only seek is not used on a binary
descriptor.

## 6. Complete transition invoice

All terms below are positive, conservative all-parameter upper bounds for
the emitted program. Their sum is the `transitions` value in bounds.py.
The bill also covers Q=1, where most terms are deliberately unused allowance.

| Region | Transition bound |
|---|---:|
| Full old-cache initialization | 5K+16 |
| Unary extents, fiber length and T counter | 128(D+1)H+16T+32(D+1) |
| All fiber staging, installation and local-cache copies/erasure | T(64H+16Cb+64) |
| All D coordinate leaves on all T fibers | TD((32D+1024)H+256Cb+1024ell+8192) |
| Parent/cache return and carry-workspace erasure | 16V+16K+32(D+1)H+32T+64(D+1) |
| Existing complete low commit and its cleanup | 128(T+D+1)V+16K+16+128D |
| Remaining fixed links and Q test | 32 |

Here is a direct check of the noninherited entries. Preparing the fixed
marked work tapes costs 3(D+4). Conversion costs at most 44(DQ+Z). The H
generator costs at most (10D+15)H+4 by §5 and its final rewind. The T counter
costs 5T+4. These fit the displayed preparation row.

In one fiber, copy/stage costs at most 14H+11, the exact parent return costs
7H+4, and complete consumed installation costs 15H+11. Copying the local
cache, explicitly padding any zero control digits and later erasing it costs
at most 9Cb+2. The outer-loop branch/advance/jump adds three. Their sum fits
64H+16Cb+64. All rewinds and source/head positions are paid.

For one coordinate, the retained source frontend costs
F<=64Cb+256ell+2048. Its explicit-edge translation costs at most 2F+2.
The inherited generic rotation costs at most 393H. Its complete owned offset
eraser costs at most 8ell+8, and the b-bit new-low scratch costs 3b to erase
and return. §5 prices the two binary products; their two erasures cost at
most 14H+14. The three component-entry jumps are also charged. The sum is
at most

    (10D+441)H+128Cb+520ell+3b+4147,

which is below the coordinate row displayed in the table. This includes
the descriptor producer, its physical dispatch and all cleanup; no code or
carry is supplied by a runtime oracle.

Final source/cache rewinds cost 3V+3K+8. Erasing H,T, the D Q-counters and
the Z-counter costs at most 7H+7T+7(DQ+Z)+7(D+3). Binary-work removal and
the final jump add four. This is below the carry-workspace row. The last
commit row is exactly the retained #5487 complete bound, with its current
corrected cache charge. A source-preserving logical reindexing is never
substituted for this payload-moving commit.

For fixed N,q, H<=V, ell<=Q<=H, K=TDb<=DbV, and T is fixed. The complete
displayed invoice is therefore O_(N,q)(V). It does not improve an ordinary
backend exponent and cannot absorb the positive exponent gap between the
implemented older B1 and the selected #6030 tariff.

## 7. Visited cells and ownership

A safe complete bound, including cleared cells, markers and every initial
head position, is

    64(D+1)V + 8K + 512(D+1).

One way to verify this loose bound is to sum the retained 43H visited-cell
bound across the TD rotation calls, giving 43DV. The source frontends all
use the same fixed origins and lengths: their UNION is bounded by
2Cb+4ell+O(1), rather than growing with T or D. For N>=2, C<=D+6<=5D/2 and
T>=48, so this is bounded by K+4H+O(1). The two binary product descriptors
each visit at most H+O(1) cells at their fixed origins; the unary counters,
their converter work and the H counter contribute at most (D+5)H+O(D).
Staging adds the original V-bit owner, one H-bit fiber, the T counter, and
the old/local cache spans, all at fixed origins. These fit
(44D+20)V+3K+O(D). Adding the entire retained low-commit bound
(D+8)V+2K+64(D+1), even counting shared spans twice, remains below the
displayed allowance. The explicit 512(D+1) margin covers the finite markers,
initial heads, five-bit quarter scratch and all endpoint cells.

Every private tape is returned blank, not merely deallocated in host state.
The original owner remains its original physical tape. Unvisited preexisting
data on unrelated spectator tapes is preserved; it is not counted as newly
visited workspace. Distinct physical tape roles are part of the machine
model and are checked in the emitted remapping and finite fixtures.

## 8. Evidence, limitations and credit

The complete executed low domain is GL2(F3), with 48 types and four high
coordinates. Q=1 and Q=3, complete Z=1/2 payloads, both SOURCE matrix
directions and translated origins are checked against a separate direct
qQ modular push oracle. The retained sparse and separate dense local
interpreters check every returned cell/head, transition and visited interval.
The dense interpreter only receives the new fixed tape count as its schema
parameter; its opcode semantics are unchanged. Boundary checks inspect all
48 local-cache last-use points and the full old cache immediately before
commit. Exact source binding separately checks the actual frame506 matrix,
right-action direction, inverse and carry envelope. The full GL8 payload
is not executed, and no such execution is claimed.

The written invariants prove arbitrary payloads and unbounded runtime Q,Z;
finite execution is corroboration. No independent human or proof-kernel
acceptance is claimed. The actual selected caller's physical ROW presentation,
homogeneous high route, native/ordinary callbacks, recursive allocation and
P3/precision/outer assembly remain separate. No new kappa and no selected
record change follow.

Credit JoyboyBrian #4989/#5332/#5487 for the actual source schedule, physical
decoder and complete low commit; Ali Romman #5849 and David Arias #2776 for
the physical rotation and literal machine; AAAmirinu #6241 for the frontend
tape/PC translation; unpaidmoon #6296 for the cache boundary; Nick Petalas
#5985/#6467 for the unit-ring branch and identical-matrix shorter word.
#6474 gives a distinct logical interleaved G20 producer and is not imported
as a physical frame506 decoder. Retain #4957, #4760/#4814 and the full
ordinary/ROW/native predecessor lineage. New whole-domain construction,
extent loops, ownership join, proof and checks are by @CubeJerry with
substantial OpenAI Codex assistance. Apache-2.0.
