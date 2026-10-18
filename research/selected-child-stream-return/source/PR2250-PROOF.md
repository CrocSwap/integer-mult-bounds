# Sequential compact controls and selected monomial lifts

We implement the retained compact-control construction on complete record
streams and bind its tensor interpretation to the selected R480/T16 complex
supplier. We retain Douglas Colkitt's algebra, guard and repair method. The
new work supplies sequential payload execution, explicit keyed sorting and
cleanup, and a compiler for the actual Gaussian monomial catalogue.

## Contract

Let M complete addresses carry R-bit records, with V=MR. Address fields have
binary lengths and complete ranges. We permit arbitrary records and dirty
compact fields. Put A=ceil(log2(2V)); the fixed collection of field descriptors
has O(A) bits per entry. We assume a completed ordinary interchange of two
equal b-bit address chunks, with arbitrary spectators, restored local work
and time O(V b^tau), for a fixed 0<tau<=1. It may borrow internally; we grant
it no external row stock or ancestor access.

For f>=2, two wide slots have fK bits and selected positions rho+jK,
0<=j<f, 0<=rho<K. Put n=f-1 and B=2^G. Two complete nG-bit compact fields u,t
precede the slots; a third, b, follows them. Other complete fields can lie
between these fields. We implement the selected-bit XOR, for either source
order, while restoring u,t,b and every unselected bit. We also implement
the constant-source specialization, which toggles the selected target bits.
For f=1 we use an elementary one-bit operation.

The exact endpoint holds at every legal finite size. Before asymptotic
absorption we charge the compact interchanges, ordered rotations and repair
separately. In the retained parameter domain

    f<=p, A=O(p), G=4 ceil(log2 p)+6, K/log p -> infinity,
    R exceeds every fixed power of p,

we obtain O(V((f log p)^tau+1)) time on a fixed number of tapes. Constants
may depend on the fixed parameter family and monomial dimension. We claim
neither a practical cutoff nor a new exponent for multiplication.

## 1. Raw word and ordered rotations

For a target segment v, control bit z and dirty integer t, execute

    v <- v+2zt;
    t <- t+(v mod 2);
    v <- v+z(1-2t);
    t <- t-((v mod 2) XOR z).

Writing the initial parity as a, direct substitution gives final values
v+z(1-2a) and the original t. The retained packed construction applies this
identity to the n low selected positions and handles the highest separately.

For an earlier source, two target rotations use the packed offsets
sum_i 2z_i t_i 2^(rho+iK) and sum_i z_i(1-2t_i)2^(rho+iK).
To load or unload t, interchange it with the back field, rotate the back
field by packed selected target bits, and interchange back. The complete
word uses four compact interchanges and four rotations. A constant toggle
uses z_i=1 in the same word; it does not require f separate bit operations.

For a later source, run the earlier-source word controlled by the low bits
of u, load the selected source bits into u through the back field, run the
word again, then unload u. We use twelve interchanges and ten rotations.
Every rotation reads controls preceding its target. `Compact.operations`
records that chronology and `rotate` checks the physical ordering.

For a target range Q and suffix block length L, compute its offset a from
the unchanged prefix. Split the Q consecutive blocks at Q-a into two tapes.
Recompute the offset during merge and emit the second piece before the first.
The machine reads and writes each payload bit a bounded number of times,
then erases the pieces and restores their heads. This realizes modular
rotation for any offset, including wraparound. At most M fibres require
control preparation. Binary arithmetic and the packed sum take polynomial
time in A, so the rotation costs O(V+M A^C) for a fixed C.

We use the completed ordinary primitive only on equal compact fields of
width nG. The executable tests implement those calls by elementary digit
interchanges using four sequential buckets. The meter records their exact
widths and full logical volumes. That implementation proves the test
endpoints and has exponent tau=1; the faster stated bound uses the declared
ordinary contract. PR2234 offers a pending written construction with
tau=1-169711/100000000. Its review status remains separate.

## 2. Original sufficient guard

Write each low target segment as 2g_i+a_i. Use the retained good set:

    t_i < B-1,
    2B <= g_i < 2^(K-1)-2B,
    and, for a later source, u_i < B-1.

On this set, temporary loads do not carry into adjacent compact digits and
the target displacements stay inside their guarded segments. The four-step
identity therefore holds digitwise and restores the compact fields. The
ideal low-selected XOR T preserves the guard: it changes only the target
parities and fixes u,t. The raw modular word S is a bijection because each
rotation is independent of its target and each interchange is invertible.
Since S=T outside the bad set E, S also preserves E.

For complete ranges, the retained union bound is

    delta <= min(1, n(2*2^-G + 8*2^(G-K))).

For an earlier source one can omit one copy of 2^-G. We retain the common
bound and original predicate. The existing carry/guard papers give sharper
sets; we do not change or re-prove their refinements. Empty good sets at
small parameters cause no endpoint problem: the repair then handles the
whole stream.

## 3. Sequential exceptional repair

After S, enumerate current output addresses q in their physical order. For
each record, evaluate the same predicate E(q), writing one hole bit. Append
good records to a good stream. For a bad record compute

    k(q) = encode(T(S^-1(q)))

and append its full destination key (at most A bits) and complete R-bit payload to the bad
stream. Evaluate inverse offsets on the current inverse controls, with
the original modular field widths. Overflow on bad inputs is part of that
calculation. We never infer an integer identity there.

Sort the keyed bad records by stable binary radix passes. In pass j, scan
the current stream once, read its key into a control work area and append
the key and record to bucket zero or one according to key bit j. Concatenate
the two buckets and erase them. Start at the least significant bit. After
pass j, induction gives increasing order of the low j+1 key bits, with
stability inside equal keys. After all key bits the records have full key order.
The machine uses two bucket tapes; it does not allocate one tape per key
or invoke an arbitrary sorting primitive.

Scan the hole tape in original address order. At a zero hole bit, consume
the next good record. At a one bit, consume the next sorted bad key and
record. Require that key to equal the current address, then emit the record.
The map TS^-1 permutes E, so its keys are distinct and occupy precisely
those holes. Thus the replacement sends the record currently at q to
T(S^-1(q)), giving T on the original input. Good records retain their order
and value. Consume and erase the good, bad and hole tapes, then rewind the
output. Finally perform the omitted highest selected-bit operation.

The full scan, holes and reinsertion cost O(V), since R>=1. The nG-bit field
gives n<=log2 M<=A. Each inverse operation evaluates O(n) terms on O(A)-bit
integers, within an O(A^3) schoolbook bound. We include guard evaluation on
good records and reinsertion key decoding in the O(M A^3) arithmetic charge.
For each
of at most A radix passes we move at most delta M records of R+A bits, including
keys, rewinds and erasure. The repair therefore costs

    O(V + M A^3 + delta M A(R+A)).

`streams.stable_radix` and `compact.repair` implement these scans. Their
payload destinations are append-only. Dense random-address maps appear
only in the independent test oracles.

## 4. Time, work and locality

Take G=4 ceil(log2 p)+6. Eventually K>=G+4 ceil(log2 p)+10. With n<=p,
the preceding bound gives delta<=5/(128p^3). Since A=O(p) and R dominates
every fixed power of p,

    M A^C / V = A^C/R -> 0,
    delta M A(R+A)/V = delta A(1+A/R) = O(p^-2).

Hence all control preparation, repair and phase-independent scans cost
O(V), while the at most twelve compact interchanges cost O(V(nG)^tau).
The highest selected bit costs O(V). This proves the advertised bound.
For independent parameters outside this domain, keep the displayed
preparation and repair terms; the executable endpoint still holds.

We use a fixed number of stream, key, counter and arithmetic tapes. The
number of radix passes grows with A, but the tape count does not. Temporary
regions have their own origins and end markers. The algorithms visit only
those regions, erase the regions just written, and restore their heads.
An ordinary child must satisfy the same local return contract. The caller
does not inspect a buried ancestor or clear an ancestor's historical work
extent. The bounds are uniform in external parked contents and their offset.

The simulator's bulk transfer abbreviates consecutive bit transitions and
charges each read, write, move and erasure. Its meter is not host elapsed
time and does not count Python arithmetic as unit-cost machine arithmetic.
The polynomial terms above supply that separate charge.

## 5. Fixed Gaussian monomials on f columns

A retained recipe acts on one binary column by

    |x> -> i^(p0+q(x)) |Lx XOR b>,
    q(x)=sum_i alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j mod 4.

The raw recipe can store diagonal and lower-triangular entries of Q. The
retained `clifford_exact.qvalue` uses only its strict upper part; alpha
already specifies the diagonal contribution. We follow that convention.

Gaussian elimination over F2 expresses the fixed invertible L as a fixed
word of row additions. Replace a row swap by three row additions and
reverse the reduction word to obtain L. Each row addition on all f columns
uses the compact selected-bit XOR just proved. Repeat each set bit of b
through a constant-source compact toggle. Thus affine offsets repeat in
each column; they do not cancel when f is even.

Before the affine word, apply the phase

    f*p0 + sum_(j=0)^(f-1) q(x_j) mod 4.

Compute that exponent from address counters in polynomial time per record.
For each Gaussian coefficient, multiplication by i^k swaps its real and
imaginary blocks and negates the appropriate blocks. We use two coefficient
scratch tapes and a one-bit carry for two's-complement negation. Each
coefficient costs linear time in its bit width, and we erase the scratch
before advancing. On fixed-width modular encodings this is exact; for
Gaussian integers use the normal symmetric headroom so negation cannot
overflow. The phase adds no denominator or magnitude growth.

For the inverse monomial, undo the affine word in reverse order, then apply
the negative phase on the recovered input columns. Evaluating that polynomial
on output columns would generally be wrong. Composition gives the tensor
power of the specified unary monomial, with restored dirty controls.
Because its dimension and binary word are fixed, the complete monomial has
the same asymptotic bound as one compact operation.

## 6. Actual selected binding and the scalar distinction

The selected PR1094 archive binds the R480 local word, its Clifford catalogue
and DATA-PHASES recipes. It has m=73, 14,336 live families, 14,826 physical
slots and 144 calls. We compare both literal 24,767-event programs and their
hashes with the retained local archive. We use none of the nearby R492 words.

The new compiler checks all 3,474 distinct local monomials from child,
endpoint and residual-wrapper recipes. For each it exhausts all 512 local
columns, comparing the affine endpoint, inverse and phase with the retained
interpreter. This is 1,778,688 exact column checks. The generic proof covers
their arbitrary f-column lifts; finite enumeration alone does not do so.

A concrete selected use is child 7, frame 0 to 9, rank one, at events 9394
and 9396 in both orientations. We execute its right monomial on full Gaussian
records at f=1 and exercise a two-column physical compiler fixture separately.
Residual recipe `0:1000.right` has p0=2 and b=245. Two zero columns therefore
map to (245,245) with phase zero, rather than phase two.

Role-level scalar operations have a different rule. The first forward
SCALE coefficient -1/2 remains -1/2 at f=2. The literal `phase` events are
section markers, not Gaussian phases. Global bridge and signed-exchange
coefficients also remain fixed. Only a scalar constant inside a unary
Clifford recipe receives its tensor power.

For a common-frame scalar gate, linearity gives

    T^tensor-f(u+c v) = T^tensor-f u + c T^tensor-f v.

Thus an audited literal common-frame circuit can replace each unary frame
by its tensor lift and retain the original role-scalar word. We do not
tensor an equality of sums. A directed residual uses right_f, one contiguous
C^(r f) child, then left_f; residual wrappers use the actual inverse right
and left maps. Keep the independently supplied backward literal program.
Also retain the columnwise DATA-PHASES translations, including terminal X_q
and the final cover correction. This compiler lemma supplies their address
and unit-phase movement; it does not supply the completed C child itself.

## 7. Evidence and limits

The registered checks include complete small payload rectangles, early and
late source orders, constant toggles, the highest-offset boundary, physical
forward/inverse monomials, and controls for omitted repair, wrong inverse
keys and a missing tensor phase. A bounded mixed-guard fixture fixes nine
ignored source bits; the repair preserves that fibre.

An additional complete experiment uses 8,388,608 one-bit records: 6,291,456
exceptional records and 2,097,152 good records. The sequential repair performs
23 radix passes and agrees with the direct endpoint. In that experiment
we construct the raw S output and expected T output with address oracles;
we execute extraction, sorting and reinsertion through the tape routines.

We do not execute the entire selected complex supplier. Full caller/hosting
composition, recursive numerical precision, selected finite invoice admission
and analytic transfer remain separate. We leave the selected frontier
unchanged. We prepared the written proof and implementation with substantial
OpenAI Codex assistance; we claim no independent human or formal verification.
