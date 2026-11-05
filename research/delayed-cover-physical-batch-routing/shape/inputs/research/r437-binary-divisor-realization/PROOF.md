# Explicit binary realization of the R437 quotient arithmetic

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0. Retained record,
Count, Word and R437 adapter sources keep their original attribution.

## 1. Exact scope and machine boundary

A natural is a canonical, nonempty, little-endian bit string between LEFT and
RIGHT, with a single zero digit for zero. All input heads start at the first
digit. Numerator and divisor are distinct. The positive divisor is borrowed;
the numerator is consumed in place into the quotient. Two distinct blank owned
roles receive the remainder and padded denominator. No payload integer is
read into host control. The only arithmetic variables in `divide` are bits,
a comparison sign, and a difference in {-2,-1,0,1}. Aliasing checks select from
four fixed roles; they are not numerical address computations.

The machine alphabet and Tape read/write/unit-step/rewind/clear operations are
those of the pinned `records.py`. Python cells/head/bytearray and meter counters
simulate a tape and external instrumentation. They are not unit-cost arbitrary
random access operations in this theorem. `binary.py` never reads cells, head,
lengths, or a numerical Word decoder. Rewind and normalization execute the
original unit movements. The constant-size `Natural` view allocates no Tape;
its methods can be inlined into the finite controller. Function calls and
fixed role selection have finite-control lowerings.

`scan` validates canonical input before any digit is overwritten. Zero divisor
and malformed canonical representation reject without overwriting payload bytes;
validation finally rewinds each inspected input to head1. The power constructor
also rejects any alias among its three roles before writing its initial one. This theorem
covers valid arithmetic success and those pre-mutation guard failures. It does
not promise rollback after allocation exhaustion or arbitrary primitive faults.
The borrowed input requirement is **head1**, not arbitrary starting heads.

This replaces one specific use of large host integers. It is not a full
physical refinement of Python, the catalogue compiler, AST loader, Word radix
validation, source setup or the complete R437 caller. These remain separate
paid obligations. The source constructor supplies encoded q, family count and
GL low-class size. Their mathematical identities and input acquisition are
premises; they are not treated as free work in a full caller. The high divisor
q^(d²), unlike those supplied inputs, is constructed by the binary algorithm
below and explicitly charged.

## 2. Division invariant and source equivalence

Let input have N bits and positive divisor D have b bits (b>=1). Copy D into
the denominator role, append one high zero, and initialize a remainder of b+1
zeros. These fixed-width scratch roles keep their extent throughout the input
loop. Before processing an input bit x, let r be the previously processed
prefix modulo D. Initially r=0. The left-shift ripple writes 2r+x into b+1
cells. Since 0<=r<D, 2r+x<2D<=2^(b+1), so the final carry is zero.

Scanning from low to high and replacing the comparison sign at every differing
bit leaves precisely the sign of the most significant difference. If 2r+x>=D,
one low-to-high borrow subtraction writes 2r+x-D and emits quotient bit1;
otherwise it leaves the remainder and emits bit0. The subtraction cannot
underflow, and the new remainder is again in [0,D). The numerator head visits
its original bits once from high to low. Previously written quotient bits are
never read as later input digits. This is the standard prefix invariant,
proved here for the literal direction and fixed padded representation.

On reaching LEFT, the original `Natural.normalize` methods remove redundant
high quotient and remainder zeros while retaining canonical zero. Denominator
scratch is completely erased and rewound. D's copied bytes are never modified;
its head is restored after the initial copy. Thus the final canonical quotient
and remainder agree exactly with the retained `Natural.divide_small`, whose
host remainder follows the identical recurrence. Equality includes normalized
RIGHT/BLANK bytes, not merely numerical value.

## 3. Binary construction of the high divisor

`multiply_into(A,B,C)` requires canonical borrowed A/B on distinct roles and
blank C. It starts C at zero and processes B from high to low. Each iteration
sets C:=2C and, if the bit is1, adds A using a bit carry. The carry in `add` is
at most1, and the sum digit temporary at most3. A shorter operand is represented
by its stationary RIGHT marker until the other operand finishes. Extensions
write one new RIGHT immediately, avoiding a scan through stale blank backing.
The invariant C=A*(processed prefix of B) proves the returned product, including
A=0 or B=0. Both borrowed heads return to1.

For fixed compiled dimension d, K=d² is a source parameter, not decoded input.
`power_into` starts at1 and applies this multiplication by the supplied radix
K times. Its loop can be unrolled in that fixed compiled source. Two accumulator
roles alternate; each old accumulator is erased before reuse. Induction gives
q^j after iteration j, hence exactly q^(d²). The implementation does not invoke
Python multiplication on q or the high divisor. It deliberately uses a simple
linear sequence rather than claiming the predecessor's square-and-multiply
work as already physically priced. This may be much slower; no speedup is
asserted. q is scanned and validated once. q>=2 is a source contract (the
standalone positivity validator also permits1, for which the identity holds).

The verified bridge imports the exact nested runtime `quotient` function from
`r437-batched-high-quotient/adapter.py`. Its AST is not changed. The compiler-side
host multiplication code is not executed by the candidate. Instead high_factor
is a fixed source-role tag referring to the binary-constructed high tape, and
a private Count subclass implements `divide_small` via the two scratch roles.
All three calls in that exact runtime body are consumed solely by `==0` guards;
the adapter checks this before compilation. Consequently returning the finite
zero/nonzero tag0/1 is observationally identical there, even though it is not
the original general-purpose integer-returning divide_small API. The complete
remainder exists on tape before the predicate scan and is then erased. No
caller outside this authenticated three-guard body receives the narrowed API.

The original sequence remains family division, GL low division, then one high
division for every radix digit after the first. The original positive-input,
nonempty quotient, q/d matching, exact-divisibility error strings, copy and
exception-close paths remain. The original encoded `radix_power` Word loop is
reused and credited; **its complete physical tariff is not proved here**.
For an inexact factor the remainder is scanned and erased before the original
guard raises, after which the original catch closes the owned quotient copy.
Borrowed fresh Count bytes/heads are unchanged.

## 4. Constructive cost and retained backing

A primitive unit is one tape read, write or unit head move, or one finite-state
transition. Let N=max(1,bit_length(input)), b=bit_length(D). The following loose
bounds cover the literal traversals, including the terminal test of each loop.
They do not use Python elapsed time or big-integer operation counts.

| Stage | Tape-action upper bound |
|---|---:|
| Canonical input/divisor validation | 8(N+b+4) |
| Padded denominator/remainder initialization and divisor rewind | 16(b+3) |
| Numerator positioning and final normalization | 24(N+3) |
| One bit: shift, comparisons, optional subtraction and every rewind | 64(b+2)+64 |
| Remainder normalization, denominator erasure and output erasure if requested | 32(N+b+4) |

For example a scan executes at most two reads, one write and one move per
visited digit, plus endpoint tests; a rewind has one read and one move per
returned cell. In the per-bit row the shift is one forward scan and rewind,
the comparison is one simultaneous forward scan and two rewinds, and the
subtraction is at most one simultaneous forward scan and two rewinds. Source
normalization visits every removed zero once with a bounded two-step erase;
it is linear even when the result is zero. These facts give the displayed
conservative constants directly from the source bodies.

Each finite-state test/update along these loops can be expanded into a fixed
number of transitions: all numerical temporaries range over the small sets
above. At most256(b+2) such transitions per input bit, and256(N+b+4) outside
the bit loop, suffice by counting the bounded statements/branches in the
listed scans and original normalization. Hence the following deliberately
larger bound covers **all** tape actions and finite control, as well as optional
owned output disposal:

`U_div(N,b) = 1024(N+1)(b+2) + 1024(N+b+4)`.

The checker independently counts actual record actions and requires them below
this bound; that finite check supports but does not replace the loop proof.
No numerical input is used for a lookup, array index, host division or shift
count in the candidate arithmetic. Numeric loop/head indices in Tape itself
are simulator coordinates, each change charged as a unit movement.

For multiplication with operand bit lengths A,B, product length is at most A+B.
Every processed multiplier bit needs one shift and at most one addition, both
linear in A+B plus endpoints. Positioning, normalization, borrow restoration
and complete owned-output disposal are also linear. The same conservative
finite-state accounting gives

`U_mul(A,B) = 1024(B+1)(A+B+4)`.

If supplied radix has B bits and K=d², the j-th input accumulator has at most
(j-1)B+1 bits. Include erasure of the preceding accumulator and the initial
radix scan. The **entire high-divisor construction, including optional final
disposal**, is bounded by

`U_power(B,K) = 16(B+2) + sum_{j=1..K}[1024(B+1)(jB+5)+8(jB+3)]`.

The multiplication bound already allows output disposal; the explicit erase
term conservatively also charges the alternating old role. No setup product
is omitted. Divisor import/compilation outside the supplied radix interface is
separate, not zero.

Visited cells include LEFT/RIGHT and the first blank reached during erasure.
Division uses at most N+3 cells on the in-place numerator, b+3 on the borrowed
divisor, and b+4 on each scratch role: at most N+3b+14 over these four roles.
This counts erased backing, because Tape.clear does not shrink storage.
Power uses at most B+3 radix cells and KB+4 on each accumulator, total
(2K+1)B+11. In the reusable adapter, retain both power roles and both division
scratch roles for its entire lifetime; do not discard the spare's previously
visited backing. Other supplied family/GL divisors and the original fresh
input/owned quotient copy are additional. Their own bit lengths must be included
when summing a complete invocation. The unchanged source radix Word arena and
all other caller stores are separate.

At #4987/#5025's N=1040413 and high divisor b=520192, this gives
`U_div = 554207929267200`. At B=127,K=4096, `U_power = 139683277391888`.
These are conservative **symbolic bound evaluations**, not executed physical
runs or an economical complete source bill. No huge payload or enormous
quadratic divisor replay is performed.

## 5. Evidence, omissions and next questions

The checker compares7936 small divisions with independently evaluated divmod
and the original Natural byte-level result; twelve wider cases cover up to256
input bits, equality, zero and long carries. Eighteen high-power cases check
both accumulator reuse and erased backing. The original complete quotient body
runs at actual binary Count/Word interfaces for q3,d2, GL2 size48, five families,
w1..3 and three residuals; this is a structural-context calibration, not the
production R437 catalogue. Source Word arithmetic is not swapped for integers.
Original factor-rejection guards, fresh input restoration, ring ownership and
workspace cleanup are checked. Five actual algorithm omissions reject.

Open next questions: charge the supplied source-constant compiler and complete
Context/Word radix paths; then integrate the encoded arithmetic into the full
admitted caller, retaining every payload, stock, native and physical lifetime
obligation. There is no complete supplier admission, kappa improvement, human
review or proof-kernel acceptance here.
