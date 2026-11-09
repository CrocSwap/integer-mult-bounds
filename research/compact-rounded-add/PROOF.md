# Compact literal rounded ADD on the retained lifecycle ABI

Prepared for @CubeJerry with substantial OpenAI assistance. This is an
arithmetic/compiler-interface lemma, not a new kappa, a complete supplier,
or an unconditional multiplication theorem.

## 1. Exact proposition and dependency boundary

Fix a reduced rational a/b, b>0, and write b=2^d o with o odd. This package
supports o<=125. Let L=max(bitlength(|a|),bitlength(b)) and K=L+2. The
constructor `compile_compact(a/b)` emits a fixed finite flat table, before
runtime numerical inputs are supplied. Its four coded ports are ordered
(target, source, numerator work, staged-output work). It uses only the
unchanged executor's branch, write, unit move, goto, halt and reject rows.

For every positive even number R of components, every matching sequence of
positive signed widths w_i, every common grid 2^-F, and arbitrary independent
signed integers x_i,y_i in those widths, the service succeeds exactly when

    z_i = x_i + floor((a*y_i + floor(b/2))/b)

fits the original signed width for every i. On success it installs the z_i,
preserves the complete source and borrowed contexts, restores all local heads,
and erases the current and previously used private bodies. This quantifies
all widths and component/column multiplicities. No condition that a*y_i or
its rounded quotient separately fits the public width is imposed.

The four data tapes and any context tapes are physically distinct. Public
numeric bodies use canonical three-bit codes for little-endian two's-complement
bits 0/1 and delimiter 2, and end at an actual physical blank. Component
boundaries match. Public heads begin at their local origins. Work heads may
start anywhere from their origins through their contiguous old binary body
frontiers. No hidden old nonblank cells may lie after a blank frontier.
All bodies are behind protected local LEFT markers and ancestor backing.
Contexts are read-only binary bodies with confined starting heads. The
common grid, tape distinctness and canonical physical frontier are admission
premises; this table is not a universal decoder for arbitrary corrupt codes.

On detected shape, grammar or final-range failure, no public cell has yet
been written. Work and heads may remain dirty or displaced; there is no
failure cleanup or automatic public-head restoration claim. A subsequent
call may retire failed private work after its public heads are re-established.

The unchanged lifecycle implementation is public commit
`ab239cb6ee884e7a900dd9101c34448077fad0b0`,
`research/compiled-owned-bank-lifecycle/machine.py`. The immutable physical
fixture comes from rounded scalar commit
`6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57`. The exact scalar Builder is
`13193a22b1070a74a8580c5d3ea27470443f815a`. `DEPENDENCIES.json` pins every
vendored byte by origin commit/path, Git blob, SHA-256 and length. Only the
Builder is reused from the exact scalar constructor; runtime carries and
passes below are newly emitted. The proof does not assume a host arithmetic
callback for the payload or a modified executor.

The source witness is DreamingOfClouds' #6936 word at
`03626137d0bd57f09b0bf9597376183ce6fa9683`, Git blob
`d93e67ca7628bf5531ae6e369da4dd7b7907b88f`, SHA-256
`273e81f176f001684b1fa3eb857992bf58b54748004fcfe806b83adb48d2cc00`.
It has 71,144 events. The coefficient census contains 61,052 ADD events
and one COPY (`COPY,1485,770,1,115`), collectively 4,462 reduced coefficients, L<=24 and o<=125. The three actual constructed
source tokens are `(local, pc, original_event)` for pc 252, 1103, 2798,
with ordered target/source indices retained in `SOURCE.json`. All three
are ADD. The coefficient census does not install COPY or transfer its
caller zero-target contract from a generic ADD theorem.
This is a finite three-occurrence registry, not an installed full recursive
caller or construction of all 4,462 coefficient tables.

## 2. Widened Horner numerator, with cancellation retained

Consider one width W component. Put M=W+K, and let A=2^(W-1). The private
numerator begins at zero. Read the fixed coefficients' bits from most
significant to least significant, padding both to L bits. If beta_i is the
bit of b and alpha_i is the bit of |a| multiplied by sign(a), perform

    N <- 2N + beta_i*x + alpha_i*y.

After j passes, N=B_j*x+A_j*y, where B_j and A_j are the corresponding
binary prefixes. In particular 0<=B_j<=b, |A_j|<=|a|, and the signs of A_j
are consistent with a. Therefore every prefix satisfies

    |N| <= (b+|a|) A < 2^(W+L).

The final offset c=floor(b/2)<2^(L-1) gives

    |b*x+a*y+c| < 2^(W+L)+2^(L-1) < 2^(W+L+1)=2^(M-1)

for W>=1. Thus all prefixes and the offset result fit width M. K=L+2 is a
uniform sufficient extra width; the proof does not assert it is minimal.
For a=0 the same construction works. No separate same-width multiplication,
negation of a most-negative public input, or premature product-range guard
appears. This is why large terms that cancel remain admitted.

Each Horner pass is in place on N and uses a bounded finite carry k. For
old numerator bit n and public bits x_bit,y_bit set

    v = 2n + beta*x_bit + alpha*y_bit + k,
    z = v mod 2,     k' = floor(v/2).

The table writes z over n after reading n. The preceding old bits are no
longer needed: the recurrence carries exactly their contribution. Starting
at k=0, [-4,4] is closed because n,x_bit,y_bit are bits, beta in {0,1}, and
alpha in {-1,0,1}. This constant carry range is independent of the numerical
magnitude of a and b. Some constructed source tables use only [-2,2].

After W public bits, the public heads stay at their delimiters. Their last
bits sx,sy are retained in finite control and supplied for the K high
numerator positions. This is signed extension, including W=1 and a
most-negative source. Let sn be the old numerator's final bit and sz the
new final bit. Summing the bit recurrence with powers of two shows that
width-M signed arithmetic is exact precisely when

    k_M = 2sn + beta*sx + alpha*sy - sz.

Indeed, replacing unsigned values by signed values adds their sign times
2^M, and the telescoping carry contributes k_M*2^M. The guard is both
necessary and sufficient. The preceding range proof guarantees it on
admitted inputs at every Horner prefix. It is never a guard on a separate
public-width product.

A further in-place binary pass adds c. Its fixed coefficient bit index caps
at L, after which all offset bits are zero; M>=L+3. With v=n+c_bit+k and
z=v mod2, k'=floor(v/2), its signed terminal guard is k_M=sn-sz. Its carry
is bounded independently of a. The result is exactly N=b*x+a*y+c.

## 3. Two banks, markers and all rewinds

The numerator work tape contains a global logical marker 5, followed for
each component by logical marker 6, its M numerator bits, and delimiter 2.
The output work tape holds just W output bits and delimiter 2. Encoded
logical 6 is three nonblank physical bits and cannot prematurely stop
physical retirement. No third guide bank is allocated.

Initialization scans the matched public component, creates W zero bits,
then adds K zero high bits while the public heads stay at delimiters. To
return for another Horner pass, the table moves numerator left K times
from its delimiter, then repeatedly moves left across a numerator bit and
moves both public heads left once. Encountering marker 6 ends the rewind;
the numerator head moves right once. Thus all three heads are at their
current first bits, including W=1, and no head crosses its local origin.
K is fixed in the table. Each later Horner pass uses this same rewind.

The offset and residue passes do not move public heads. Their numerator-only
rewinds move left until marker 6 and then right. Neither this marker nor
any input-dependent length is examined by host code. At the quotient end,
all public heads are at their component delimiters and N at its delimiter;
advancing these heads and the output head starts the next component.
Finite parity/seen flags require a nonempty even component count.

After every component has passed its range checks, the heads are at the
field frontiers. A reverse numerator scan recognizes each delimiter 2,
moves the two public heads and output head left once over their delimiter,
skips K numerator high bits, and moves the other heads left once for each
of the W remaining bits. It ignores marker 6 and continues to the previous
component. The global marker 5 terminates this procedure exactly at all
public/output origins, leaving the numerator at its origin. This works
without a runtime width counter and permits different matching widths in
different components.

Only now does the output-to-target copy run. It copies coded bits and
delimiters to the target without changing the source. No branch before
this copy writes the target. Well-formed staged output has exactly the
public extent, so the target physical frontier is reached simultaneously.
The unchanged executor resets all data/context heads, and unchanged
`Controller.primitive` retires both private banks on successful return.

## 4. Signed residue, exact odd quotient and final admission

To divide the signed M-bit numerator, first compute its residue r modulo o.
For o>1, a least-significant-bit scan retains rho and power modulo o,
starting at 0 and 1. Each bit n contributes n*power; then power doubles.
At the terminal sign bit s, the unsigned value U differs from N by s*2^M.
The correct residue is therefore

    r = (rho - s*power) mod o = N mod o,  0<=r<o.

This correction is essential for negative N. There are at most O(o^2)
residue states; here o<=125 is an explicit scope restriction. For o=1,
r=0 and the residue traversal is omitted. This result is not a polynomial
in log o construction for arbitrary divisors.

Rewind to the first numerator bit and initialize k=-r. On each bit n set

    z = (n+k) mod2,    k'=(n+k-o*z)/2.

Since o is odd, the numerator is even, and the recurrence is exact. The
interval [-o,0] is closed, starting at -r. Thus the odd quotient controller
has only O(o) carry states and no a-sized states. If Z is its M output
bits interpreted unsigned, summing the recurrence gives

    o Z = N-r + (s-k_M) 2^M.

Consequently k_M=s-o*sz is exactly the signed quotient guard when sz is
the desired quotient sign. Since r is the correct residue and o>=1,
Q=(N-r)/o=floor(N/o) already fits signed width M.

The first d quotient bits are discarded, without moving public or output
heads. The next W bits are staged, advancing the two public heads over
W input positions. The remaining K-d quotient bits must all equal the
last staged sign bit sz, and the final carry must satisfy k_M=s-o*sz.
Since d<=L-1, K-d>=3; these counts remain valid even when W<d. They do
not assume the low discarded bits are zero. The high checks hold if and
only if floor(Q/2^d) fits width W: they are exactly the signed extension
criterion for the quotient's W surviving bits. The displayed telescoping
identity proves the final carry test's necessity and sufficiency, including
negative values and signed zero.

Finally write N=oQ+r. Then

    floor(N/(o*2^d)) = floor(Q/2^d),

because writing Q=2^d k+t with 0<=t<2^d gives
0<=o*t+r<o*2^d. This proof also covers negative Q; it uses mathematical
floor and Euclidean remainder, not truncation. Therefore the staged result
is floor((b*x+a*y+c)/b)=x+floor((a*y+c)/b). When b is even, a*y exactly
halfway between multiples rounds upward on both signs; when b is odd,
there is no half-integer tie for integer a*y. The implementation is total
nearest-up rounding subject only to final representability, rather than
checked exact division.

On the actual admitted inputs, each real-component error from exact
x_i+(a/b)y_i is at most one half of a grid unit. Thus the complete
Euclidean (equivalently complex-component) field error is at most
sqrt(R)*2^(-F-1). This is an actual-input primitive defect bound; it
does not itself propagate upstream ideal-input errors, assert format
admission of a whole caller, or transfer an existing source precision
invoice. The private extra width K<=26 matches the current coefficient
bit bound, without asserting that its repeated scans have already been
paid in another package.

## 5. Positive full primitive cost and retained backing

Let S=sum_i(w_i+1), R be the component count, and

    U = 1 + S + (K+1) R.

U is the numerator's logical body length; output length is S. Both work
bodies are binary physical codes of lengths 3U and 3S. Let A_N,A_O be
contiguous initial dirty physical body lengths, with initial work heads
within those bodies/frontiers. Let Q_c=sum(length(context)+1), allowing
confined initial context heads. Public heads start at origins.

Count each physical tape read/write/unit movement and each executed flat
row positively. An ordinary coded branch costs at most 11 including its
row (10 physical actions); a coded write costs 10; an ordinary coded unit
move costs 5; goto costs 1. No successful positive move is from a blank
frontier, because all such positions are first written or are already
nonblank. Blank tests cost less. Boundary states and the marker scans are
included in the following deliberately slack bounds:

| Phase | Tape actions plus rows, upper bound |
|---|---:|
| Allocate numerator zeros and markers | 128U |
| One complete Horner pass and its public/numerator rewind | 128U |
| Offset pass and numerator rewind | 128U |
| Residue pass and numerator rewind | 128U |
| Odd quotient, low discard and final high checks | 128U |
| Whole-field reverse marker scan and installation | 128U |
| Successful executor origin resets and two current-body retirements | 128U+16Q_c |

For example, a Horner ordinary position uses three coded reads, one write,
three moves and one goto, at most 59 actions/rows. Its rewind uses at most
27 per ordinary position. A high position plus its fixed rewind costs at
most 33; the finite boundary states fit the remaining margin per component,
whose numerator record has W+K+2>=6 positions. The quotient's ordinary
staged positions use at most 59, while drop/high positions use at most 17.
These counts include reverse traversal and no unmetered data access.

For `retire`, starting at displacement p<=A, the first origin scan costs
2p+3, the erase scan costs 3A+1, and its return costs 2A+3. Thus entry
retirement costs at most 7A+7 per old bank. After the service, the bodies
are contiguous and current lengths are at most 3U,3S. Origin scans and
exit retirement are covered above. The fixed entry/exit rows and constants
are absorbed because U>=1. A conservative combined bound is

    512 (L+8) U + 7(A_N+A_O) + 16Q_c.

This retains all L rereads, every marker, widening, copying, head return,
entry and exit erasure, finite control, and old dirty backing. On detected
failure before installation, execution is a prefix of these passes and
uses no more than the same bound, but omits success cleanup. The bound is
not identified with any earlier one-unit linear primitive tariff.

If H_N,H_O are already allocated historical private capacities, the new
private physical backing is bounded by

    max(H_N,3U) + max(H_O,3S),

not merely the currently nonblank bytes. Add the unchanged public/source,
context, ancestor and controller backing. Retirement turns old cells blank;
it does not reclaim or forget their historical capacity. Repeated calls
sum their positive costs and keep the maximum widths/extents of each bank.
No arbitrary workspace is silently restored by destruction: these two
roles are explicitly owned scratch authorized for retirement by the
retained primitive interface.

## 6. Finite construction size and actual source coverage

There are O(LK) Horner/high/reset states: carry and signs have constant
ranges, with fixed coefficient index and fixed high-bit count. Offset
states contribute O(L), residue states O(o^2), and quotient/drop/high states
O(Ko), since d<K. Marker scans and copy loops add only constant-size
families. Therefore the flat graph has O(LK+o^2+Ko) rows/states; binary
encoding of its addresses also costs the logarithm of the graph size.
Construction performs finite integer operations on fixed coefficients,
residues and labels; their positive bit cost, source authentication, source
census, token lookup/export and storage of the graph are separate setup
costs. None is declared free or part of a runtime payload callback.
For this fixed finite source class L<=24,K<=26,o<=125. This does not claim
an efficient uniform variable-divisor or variable-coefficient algorithm.

The three constructed witnesses are:

| Source pc | Coefficient | L,K,d,o | Rows / states |
|---|---|---|---:|
| 252 | -14729531/163840 | 24,26,15,5 | 100033 / 43280 |
| 1103 | -1379/250 | 11,13,1,125 | 187806 / 117382 |
| 2798 | 1085645/393216 | 21,23,17,3 | 76560 / 33066 |

The old generic direct-carry bound for pc252 would be
|a|+b+o+floor(b/2)=14,975,296. We do not instantiate that graph.
The new construction's Horner carry is bounded by 4 universally, and the
largest of these actual graphs is the deliberately retained o^2 residue
case. A larger constant number of bitwise passes is paid explicitly.
No full 4,462-table catalogue is materialized or claimed tested.

Literal executions verify respectively 100+Round(q*2)=-80 at W=8,
7+Round(q*2)=-4 at W=4, and -7+Round(q*3)=1 at W=4. Each separate rounded
product exceeds its public signed range; the combined ADD is valid.
The exact source tokens retain the original event's extra origin field.
The caller must still supply ordered distinct fields, common formats and
all recursive remappings. The fixture invokes the unchanged
`Controller.primitive` method with precisely its required attributes;
it does not pretend to execute the complete Controller constructor,
stack, source exporter or current caller.

## 7. Verification, novelty and remaining obligations

`verify.py` independently computes expected outputs with direct signed
integer floor, never replaying table carry transitions. Its 1,952 exhaustive
small-width pairs span five small coefficients and all three source
witnesses; additional endpoints cover W<d and most-negative inputs. All
these runs execute the immutable retained primitive and actual CodedPorts.
Transparent row counting observes immutable table lookup only. It receives
no payload values and does not affect transitions. Dirty long-to-short
history, late overflow, failed-work reuse, matched equal values on distinct
tapes, borrowed contexts and canonical shape errors are checked. Compiled
negative controls lose a leading coefficient bit, lose the negative sign,
round ties downward, omit signed residue correction, or omit high-range
checks. Each is detected. Finite coverage supports the implementation;
Sections 2-5 supply the all-size proof.

Binary Horner multiplication, signed carry arithmetic and long division
are classical. Canonical `upstream/build/sections/02-streams.tex`, blob
`088fceea1867abc76271d7efe7532b779fee9039`, already gives linear signed
stream arithmetic with guards and reversals. NickPetalas' #3094
`research/rank7-one-carry-scalars` uses one-carry Boolean/dyadic bank circuits;
`research/scalar-fused-dyadic` audits host rational normalization. These are
credited, not rediscovered as novel primitives. Our bounded overlap read
is recorded in `OVERLAP.md`; it is not a repository-wide novelty proof.

The new contribution is the explicit compact widened-numerator table,
its two-bank marker geometry and complete retained lifecycle join, its
cancellation-safe total signed rounding proof and positive costs, and
three source-bound current large-coefficient witnesses. The preceding
rounded scalar package already gives a generic direct-carry ADD existence
theorem and small fixtures; it explicitly leaves this numerical coefficient
explosion and source inventory open. #6937's total RDiv proposal is credited.
The present package does not install all remaining arithmetic services or
transfer any rounded native contract automatically.

Remaining: whole coefficient catalogue/export, source/format remapping,
all-column native services and error bounds, full recursive owned-history
accounting, a common physical supplier tariff, and outer analytic recovery.
The five inherited framework assumptions are not globally discharged.
No complete multiplication exponent changes and no selected certificate
is modified. In particular, the previous optimistic rounded-scan invoice
is not a cap available to this multi-pass implementation without a fresh
complete assembled cost proof.
