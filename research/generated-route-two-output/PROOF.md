# Produce both low digits and exact carries for generated binary routes

## 1. Statement, source and novelty

Fix the carried-word implementation in #8092 at
`6a3437d1cd94dc4e1792f4052511af6160120bf9`, based on canonical
`e54523517d0f03e58352e647c403a5af3e525a57`. Its source grammar carries
coordinate swaps, additions with 94 fixed dyadic coefficients, and scales
with 15 fixed signed dyadic units. All inverse instructions remain in
that alphabet. Exact source files and Git blobs are in `ORIGINS.json`;
`retained/PROOF.md` is the preceding generated-grammar proof.

For every finite right word W of dimension N generated from those retained admitted seeds
by the source grammar (not arbitrary caller-supplied `literal` or
`euclidean_seed` inputs), every odd integer
q >= 3, and every supplied canonical low matrix g0 with entries in [0,q),
the construction returns

    h0 = g0 S mod q in canonical representatives,
    C = (g0 S - h0)/q in Z[1/2]^(N by N),

where S is the exact rational right product of W. It reads every row and
preserves the supplied g0. No dense S or table of low matrices is needed
by this producer. Both outputs are computed, including the low digits
which the earlier G20 carry-only state machines deliberately did not emit.

The local two-pass producer has finite control independent of q and of
the high width w. For the actual alphabet, at most 54 quotient comparators
and a 388-bit product encoding of the first-pass logical state suffice
for each fixed elementary column type. A shared dispatcher additionally
stores a fixed finite opcode/coefficient tag; that tag is not included in
the 388-bit product bound.
Every elementary carry numerator is in [-54,54]. A second finite-state
pass emits the complete B-bit new low word, B=bit_length(q), including
leading zero padding; its signed arithmetic state lies in [-54,86]. The
388-bit quantity is an encoding upper bound, not minimality, a physical
workspace measurement or an assertion that the Python interpreter uses
388 bits.

For a whole word of length ell containing m nonswap instructions, one
common carry denominator has exponent at most 5m, and signed integer work
registers of at most 6m+5 bits suffice. These are source-alphabet bounds;
section 5 gives a more precise word-dependent bound. The producer has an
explicit sequential implementation with conservative bit cost

    O_source(N^2 (ell+1) [B+W+log(2N)]^2),

where W is the sufficient carry work width. Data space, including
materialized outputs but excluding the supplied input, is

    O(N^2(B+W)+ell log(2N)) bits.

The proof separately charges input/output access, arithmetic, temporary
low words and carry registers. It does not implement the payload
permutation, enumerate GL_N(F_q), or return a recursive payload owner.
The high width w does not occur in these producer inputs or bounds.

### What is already known

The carry cocycle, the formula for the two mathematical outputs, their
width-independent rational envelope, and a table-free evaluation of fixed
G20 words are already in Ali Romman's #5841. #6474 and #6503 construct
bounded-state quotient/carry producers for released eight-input columns
with denominators 1 and 4. #8092 supplies the exact larger alphabet,
generated complete-basis grammar and its separate routing invoice.

This contribution adds the second output stream, extends the local
producer to every actual elementary alphabet entry, and binds its
composition, live integer widths and paid access to the generated words.
The classical cocycle and floor recurrence are credited inputs. No first
discovery of table-free carries, no faster whole route and no new kappa
is claimed.

## 2. First pass: retain only bounded information

Fix a local column with p in {1,2} inputs, coefficients a_i in Z and
denominator D=2^s. For an addition by a/D the two coefficients are (D,a);
for a scale they are (a). For canonical inputs x_i in [0,q), put

    Z = sum_i a_i x_i,
    L = sum_i min(a_i,0), H = sum_i max(a_i,0), U = max(0,H-1).

Then L <= floor(Z/q) <= U. For each j=L+1,...,U, retain b_j=0
initially. On one least-significant-first input row with low bits e_i and
radix bit f, update

    b_j <- floor((b_j + sum_i a_i e_i - j f)/2).

After r rows this is exactly floor((Z_r-j q_r)/2^r), where the subscript
means the integer represented by the first r low bits. This is the floor
identity used in #6474; it follows by writing the old numerator as
2^r b_j plus its remainder in [0,2^r). At the complete input, b_j >= 0
if and only if Z >= j q. Therefore

    u = L + number of nonnegative b_j = floor(Z/q).

The invariant interval for b_j is

    [L-max(j,0), H-min(j,0)].

It contains zero. The per-row added quantity lies in that same interval,
so the averaging/floor update preserves it. All states are bounded by
the fixed column, even on invalid streams.

Also retain Z mod D and q mod D from the first s bit rows. A phase count
saturates at s; if input ends earlier, the absent high bits are zero, so
the stored residues are complete. Inversion of an odd residue modulo the
fixed 2^s is a finite precompiled table, not an unpriced inverse of a
growing integer. Define

    r = Z q^-1 mod D,
    c = u - ((u-r) mod D).

Then u-D+1 <= c <= u and Z-cq is divisible by D. Since
0 <= Z-uq < q, one has 0 <= Z-cq < Dq. Thus

    y = (Z-cq)/D in [0,q), and C_local = c/D.

This supplies the unique canonical y and exact localized carry, including
negative fractional carries. It never divides by q at runtime. The
sufficient envelope is L-D+1 <= c <= U.

For each input x_i, a separate two-state comparison
v_i <- floor((v_i+e_i-f)/2), starting at zero, ends at -1 exactly when
x_i<q. Require the first and last radix bits to be 1 and at least two
rows. These checks establish a canonical odd q>=3. Supplied bit channels
have equal length and synchronized end markers. A malformed input may
reject without rollback; valid input channels are read-only.

## 3. Second pass: emit the missing low output

Return the input heads and read the same channels again. Retain c and
initialize a=0. For each row set

    t = a + sum_i a_i e_i - c f,
    z = t mod 2 in {0,1}, a <- floor(t/2).

After B input rows, perform s further rows with all input bits zero.
Discard the first s output bits, checking each is zero, and emit every
remaining bit. Exactly B bits are emitted. The ordinary signed carry
invariant gives

    Z_r-c q_r = emitted_low_r + 2^r a.

The complete integer Z-cq is nonnegative, divisible by 2^s and smaller
than 2^s q < 2^(B+s). The discarded bits are therefore zero, the final
carry is zero, and the emitted B-bit word is y. The s zero rows are
essential: a high output bit may emerge after the input channels end.

For fixed c the signed state stays in

    [L-max(c,0), H-min(c,0)].

This contains zero and every per-row increment and is preserved by
floor division by two. It includes the zero-flush increments. No
numerator of bit length B is accumulated in the control.

The exact symbol census is 2(p+1)B input reads, B output writes,
(U-L)B quotient-state updates, pB input comparisons and s zero-flush
steps. Head return and temporary-data handling are additionally charged
in section 6. The interpreter's `Observer` holds unbounded diagnostic
counts external to the finite-state assertion. Its output tuple is data,
not control state.

## 4. Actual alphabet and generated source binding

The frozen `ALPHABET.json` contains 94 additions and 15 scales.
Substituting exact numerators and denominators in sections 2-3 gives the
54 comparator maximum, carry interval [-54,54], second-state interval
[-54,86], and sufficient first-state encoding of 388 bits.
`Column.state_bits` sums ceiling binary sizes of the declared comparator
intervals, then adds p input-comparison bits, two s-bit residues, a
saturated phase and three validation flags. This is an exact calculation
over the authenticated finite alphabet. The invariants prove validity
for unbounded input length.

Every addition has D<=32 and D+|a|<=55. Every scale has
max(D,|a|)<=16. The alphabet is closed under addition sign reversal and
scale inversion. A swap exchanges its low coordinates and carry
coordinates; it has no new local carry and is charged as access work.

The #8092 constructors only copy this alphabet, relabel coordinates,
reverse/invert words and concatenate them. Products, tensors, direct
sums, guards and complete placements use these same producers without a
new coefficient decision. The original common coupled-port descriptor
is retained on both roles. This producer does not authorize different
routes across a coupled scalar contact.

The 15-dimensional `actual_port/17` source word is also applied in its
complete 134-dimensional stage-one ambient: its first 15 coordinates
are the original head, seven central and first seven fresh axes; the
remaining 119 coordinates are spectators. Tests read and return every
coordinate of every row. Neither 134 nor the diagnostic primes replace
the completed carrier N or its large-prime inequality.

## 5. Fused carry registers without a dense generated matrix

The whole-word law is the credited #5841 cocycle. The following gives an
explicit common-denominator implementation and word-height bound.
For prefix W_j, maintain current low row l_j and signed integer vector
p_j with

    C_(W_j)(l_0) = p_j / 2^v_j.

Initially v=0 and p=0. A swap exchanges the corresponding entries. For
addition at target i from source k with coefficient a/2^s, let c be the
produced local carry numerator. Set v'=v+s and

    p'_i = 2^s p_i + a p_k + c 2^v,
    p'_h = 2^s p_h for h != i.

For a scale use p'_i=a p_i+c 2^v and the same other-coordinate rule.
The denominator exponent changes only after old numerators have been
read. This is C_new=C_old E+C_E(l_old) in right chronology. Unaffected
numerator registers must still be shifted when the denominator grows.

Let D_j be the product of denominator factors so far. For an addition
put A_j=D+|a|, for a scale A_j=max(D,|a|), and for a swap A_j=1. Define
P_j=product A_j. Then P_j>=D_j and the elementary maximum-coordinate
norm bounds give

    max_i |(l_0 S_j)_i| <= (q-1) P_j/D_j.

Since l_j is canonical, |p_(j,i)| < P_j+D_j <= 2P_j.
In dimension N, an elementary coefficient product or shifted old numerator
is smaller than 2P_(j+1) in magnitude. For an addition the joint partial
also obeys |D p_i+a p_k|<2P_j(D+|a|)=2P_(j+1), rather than summing
two separate worst-case bounds. The local carry term is smaller than
2P_(j+1), using |c|<D+|a| for an addition and |c|<D+|a|<=2A_j
for a scale. The intermediate sum is below 4P_(j+1); a conservative
allowance

    W = bit_length(P_m)+4 signed bits

covers all intermediates and outputs. Denominator shifts are charged;
no q-sized carry numerator is hidden in local finite control. For the
source alphabet v<=5m and P_m<=55^m, so W<=6m+5 suffices, including m=0.

At completion write h0=l_m, p_m and v. The outputs satisfy section 1
without constructing S. A caller needing residues modulo q^(w-1) must
separately reduce these dyadic records; that step is not executed here.
For w=1 the high ring is a singleton and needs no high arithmetic.

Reverse and invert the complete word, read the committed low row and
charge a separate inverse execution with its own width ledger. The
credited cocycle gives C_(S^-1)(h0)=-C_S(g0)S^-1. A stale entry low
row is not a valid inverse input.

## 6. Paid sequential access and cost boundary

For the elementary transducer, supply p read-only B-bit low channels,
a read-only canonical q channel and fresh output, with origins and
synchronized end markers. The first pass scans forward and returns all
input heads; the second emits the B-bit result and returns all heads.
The bounded carry can be emitted as a separate fixed-width record.
There are at most two forward and two return input traversals, one
output traversal and return, s<=5 flush steps and constant marker/packet
work. Every logical state transition expands into a fixed finite
Boolean controller because all state and coefficient ranges are fixed.
Compilation is a nonzero source constant; a huge transition table has
not been materialized or timed here.

For a supplied N-coordinate row in marked sequential B-bit records,
copy the row to working storage, scan to extract at most two inputs into
parallel temporary channels, run the transducer, rewrite the selected
working record, erase temporary channels and return their heads. Each
operation requires O(NB) bit access. Indices and word descriptors are
read and charged; a conservative binary counter/address implementation
adds at most a logarithmic factor, covered by the squared bound below.
The original g0 record is never overwritten.

At the same step, scan N signed W-bit numerator records. Shift each
by fixed s<=5, multiply at most one by fixed |a|<=32 using shift/add,
and perform at most two signed additions. The local c has magnitude
at most 54; its shifted contribution fits W bits. School arithmetic,
complete scans, initialization, writes, head returns and ordinary
destructive scratch retirement cost O(N[W+log(2N)]^2) per step.
This deliberately conservative bound does not treat integer arithmetic
or array indexing as one physical tape step.

For N rows and total word length ell the resulting local bit bound is
O_source(N^2(ell+1)[B+W+log(2N)]^2). Outputs occupy N^2B low bits and
N^2W numerator bits plus one exponent. Working rows/temporaries add
O(N(B+W)). Word/control storage contributes O(ell log(2N)) bits for the
fixed alphabet. Scratch retirement here is destructive overwrite; no
reversible erasure is inferred. A literal instruction graph with this
layout has not been emitted or benchmarked; the code specifies the
bounded-register transducer and arithmetic algorithm.

This access contract does not build a complete low-type permutation on
payload fibres. It produces address/carry descriptions for a supplied
low matrix. Selecting that matrix, transporting all high/spectator
payload, ordering destination low types, restoring a parent owner and
absorbing costs into a complete recursive caller remain separate.
Rowwise output production is not a replacement for the paid routing
service or `owned_erasure`.

## 7. Why a single input pass needs growing retained state

The source alphabet contains the coefficient-one shear x <- x+y. Even this primitive cannot
emit its canonical low output with bounded retained state in the following
one-pass model. This is a statement about output order and access, not a
general lower bound for physical routes.

Fix any odd q>=5, B=bit_length(q), and consider a deterministic producer
which reads x, y and q in synchronized least-significant-first bit rows.
It must emit the B-bit canonical representative of x+y modulo q, also
least-significant first, on a write-only append-only output. It cannot
reread input or revise/retrieve prior output. Every input-dependent datum,
including work tapes, accessible outputs, control and head positions,
belongs to its retained state. Public q and B may already be known.

At the cut after B-2 rows, at least 2^(B-2) distinguishable states are
necessary. Hence every binary encoding of those states needs at least
B-2 bits. To prove this, put K=2^(B-2) and write q=aK+r, where
a is 2 or 3 and, because q is odd, 1<=r<K. Take all K prefixes

    x_low=t, y_low=0, 0<=t<K.

One common continuation uses zero in both remaining high pieces and
produces the low output t. A second valid continuation is:

| Case | High piece of x | High piece of y |
| --- | ---: | ---: |
| a=3 | 2 | 2 |
| a=2 and t<r | 2 | 1 |
| a=2 and t>=r | 1 | 1 |

Thus x=t+K times its displayed high piece and y=K times its high piece.
Each lies in [0,q), and q<=x+y<2q. The resulting low output is x+y-q.
Since K is even and q odd, its first bit has parity opposite to t.
The two valid completions share the entire already-read prefix, so no
first output bit can have been emitted on any of these K prefixes.
All output histories at the cut are therefore the same empty history.

If two prefixes shared a retained state, their common zero continuation
would produce the same output. It instead must produce their two
distinct t values. There must be at least K different states. This is
the standard deterministic distinguishability argument, as used in
Nick Petalas's retained serialized-carry-cut work. That predecessor
asks for the carry only after reading all of x before y; this theorem
permits interleaved reads but requires the canonical low output in
append-only low-bit order. Neither theorem supersedes the other.

The proof includes every odd prime q>=5, not just a sparse radix family.
It does not prohibit bounded-state carry-only output, a second pass,
growing workspace, revised output, a different output order or additional
input-dependent external data. The two-pass construction above uses
the reread explicitly. It does not claim the least possible time or
state at any fixed radix.

## 8. Evidence, limitations and next question

`check.py` authenticates eight source files and tests all 109 local
column types against direct integer modular division. It covers odd
composite q as well as primes; primality belongs to the surrounding
cover, not this dyadic producer. Forty long streams include 4,097-bit
q. Generated examples use independent dense rational right products
for low outputs, carries and q^w reconstruction, including every
spectator in the 134-coordinate stage fixture.

Mutations remove the flush, truncate signed states, omit denominator
shifts, reverse chronology, drop a shear invisible at low precision and
reuse a stale cache. Source hashes and invalid-domain controls are
required. Normal and optimized modes use explicit exceptions. Separate
review must inspect the second-output induction and the whole-word
integer width argument without importing this producer.

The one-pass cut is independently enumerated for every odd q from 5
through 255: canonical domain, equal read prefix, opposite first-output
bit and all distinct common-continuation outputs are checked. An even-q
control records the parity hypothesis. These finite cases corroborate
the displayed all-q proof and are not a search-based impossibility claim.

No complete canonical assumption is removed. No production carrier,
physical payload route, entire recursive owner bank or rounded integer
multiplier is executed. Selected kappa stays conditional at
0.00363005817; the selected certificate is unchanged. The next useful
step is installation in one actual recursive owner bank with complete
fibre transport, original-owner return and disposal costs. A faster
complete route requires that construction and a renewed invoice.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Ali Romman for #5841, #6474, #6503 and #7828; #7840 and the selected
native lineage; #8092's dyadic/generated route authors and reviewers;
Nick Petalas for the serialized-carry-cut method and its precise scope;
and the retained ordered-affine/full-GL work. Classical finite-state
arithmetic, carries and cocycles remain credited. Independent human
and proof-kernel acceptance are not claimed.
