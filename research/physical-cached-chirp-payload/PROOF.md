# Physical cached chirp payload pass

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The cached suffix identity, rounding argument and table-travel mechanism are
inherited from CrocSwap/integer-mult-bounds#4325 and #5987. The new result is
their encoded physical consumer, actual word products, polynomial payload
binding and complete ownership invoice. **No new κ.**

## 1. Source and quantified interface

Fix d>=1, dyadic t_i=2^ell_i>=2, with t0=max_i t_i, and odd slopes s_i.
Put T=product_i t_i and r=t0. The exact source is #4100 PROOF's phase

    a_i(x)=exp(-pi i s_i x^2/t_i),     a(x)=product_i a_i(x_i).

That source already chooses largest axis0 as the innermost coordinate and
packs its r coefficients into a polynomial record. No transpose is supplied.
Distinct-prime production and the outer CRT/Fourier caller are outside scope.

Let h=2^-f, with f>=0, actual payload modulus<=R, R>=1, and
W>=f+ceil(log2(R+1))+2, W>=max ell_i. Each coefficient is a consecutive pair
of W-bit two's-complement real/imaginary words on the h grid. A polynomial
record is exactly r such pairs; the remaining axes index consecutive records.
The returned layout is identical. An opaque Kronecker product integer is
not this coefficient-field ABI.

The borrowed tables contain grid pairs A_i(x), where A_i(0)=1,
|A_i(x)|<=1 and |A_i(x)-a_i(x)|<=e_tab. These are **certified prepared-input
premises**, not online authentication of arbitrary coefficient pages.
Table generation, certification and serialization are paid separately.
Certified inward approximations are permitted; exact transcendental grid-cell
separation is unnecessary. The serializer checks integer unit-disk inequalities,
sizes and zero entries. SOURCE.md supplies the actual numerical producer.

The caller performs one chirp or conjugate-chirp multiplication, preserves
borrowed bodies/origins, erases scratch and protects its return until consume.
It reuses the unchanged authenticated #3787/#3851 scalar-word cohort and its
hypotheses. No convolution, full transform, supplier admission, outer integer
assembly or discharge of all five selected assumptions is claimed.

## 2. Physical roles and initialization

`run(payload,shape,tables,width,precision,conjugate=False)` has three borrowed
data tapes, two distinct Count tapes and a finite conjugation boolean. No d,
T, radix or address is decoded into host control. Shape concatenates ell_i
zero bits and AXIS_END per axis. Each table page is PAGE_BEGIN, t_i complex
records, PAGE_END. All tags belong to a fixed finite alphabet.

Initialization reads each shape field into an encoded Count; checks positive
ell_i<=W and ell_i<=ell0; and scans exactly 2^ell_i complex records. It checks
each zero entry as one, all remaining body cells as binary, and exact catalogue
endpoints. Nonzero phase semantics come from preparation, not this structural
scan. The shape is copied to one counter tape. Another tape stores pi0,...,pi_d
as complex words, initially all one. Two temporary Signed values carry a suffix.
A fixed pool supplies other temporaries; one fixed FftWord supplies products.
There is no per-axis tape or variable host array during execution.

## 3. Universal stream invariant

Before processing x, the input head is at its coefficient, the counter holds
x in little-endian fields, and the cache obeys

    pi_d=1,  pi_k=trunc_h(A_k(x_k)*pi_(k+1)), k=d-1,...,0.   (1)

The table head is just after the current axis0 entry. Initialization restores
it just after entry0; A_i(0)=1 makes (1) exact at the initial point.

Increment resets overflowed lower fields. If it stops in axis j, higher axes
are unchanged. Cache/table heads advance one adjacent axis per overflow. For
j=0 the next table entry is already under the head. For j>0, read_field copies
x_j to a Count and a counted scan advances x_j records from page j's start.
The axis number is never decoded.

Read adjacent pi_(j+1), then recompute pi_j,...,pi0 in descending axis order.
Backward separator scans find the previous table's entry0 and counter field;
each lower changed digit is zero. The new suffix stays in two Signed values.
All changed instances of (1) are restored; higher instances remain valid.
Thus every cache equals a fresh rounded suffix chain at that coordinate,
regardless of how many records preceded it. Full overflow requires complete
catalogue and payload endpoints. Exactly T coefficients are processed, in
axis0-packed polynomial order, without a payload gather or per-record d scan.

## 4. Actual arithmetic and error

Arithmetic.complex_product executes four word products ac,bd,ad,bc and forms
(ac-bd,ad+bc) exactly. Only the two completed components are truncated by f;
individual products are not rounded early. Raw signed words have O(W) bits,
including the 2W-bit products and a sum carry, and are kept until rescaling.

Every suffix remains in the unit disk: exact products multiply moduli and
componentwise truncation toward zero cannot increase modulus. The final
payload result has modulus<=R and fits the stated carrier. Conjugating its
phase negates the imaginary Signed word exactly without changing the schedule.

Cache replacement first encodes the complete new pair in short scratch,
checking headroom before modifying the cache. It then clears exactly that
slot, copies the checked word and clears scratch. Thus ordinary external-data
validation cannot strand later cache entries behind an interior blank.
Asynchronous interruption halfway through a write is not a recovery contract.

For suffix error E_k against the exact unit-phase product,
E_k<=E_(k+1)+e_tab+sqrt(2)h. The final-axis multiplication by pi_d=1 is grid
exact. Consequently

    E_0 <= d e_tab+(d-1)sqrt(2)h,
    |output-a(x)u| <= R[d e_tab+(d-1)sqrt(2)h]+sqrt(2)h.     (2)

The conjugate case has the same bound. Component-l1 error is at most sqrt(2)
times the displayed error. Inward tables with each component error<=2h give

    component-l1 output error <= 2[R(3d-1)+1]h.             (3)

Exact component truncation permits the sharper inherited e_tab<=sqrt(2)h.
These bounds concern the actual supplied dyadic input. Earlier input error is
its caller's obligation. There is no accumulation in T: invariant (1) always
contains at most d table approximations and d-1 nontrivial grid truncations.

## 5. Exact product count

Let L_k=product_(i<k)t_i. Slot k is updated exactly T/L_k-1 times because
its initial value is known exactly. Thus

    U=sum_(k=0)^(d-1)(T/L_k-1)<2T,
    scalar products =4(T+U)<12T.                           (4)

Sentinel products are counted even when arithmetically redundant. All use
the single unchanged scalar owner at width W. Let M(W) denote that owner's
complete cost under its inherited contract.

## 6. Complete movement and encoded-control bill

After initialization, table entry visits are exactly the inherited #5987
largest-axis-first walk. Page tags add O(1) actions per crossed page. Our
additional full validation/rewind and final overflowing scan/rewind cost
O(W sum_i t_i+d). Since sum_i t_i<=T for d>=2 (and equality for d=1), these
are O(TW). We do not assert the old exact constant seven for this newly
framed, validated implementation. Every forward/backward page traversal and
final borrowed-head restoration is included.

Here is an explicit bound for the potentially hidden address arithmetic.
When a carry stops at j>=1, x_j ranges from1 to t_j-1, each value occurring
T/L_(j+1) times. With M=t0>=t_j and L_j>=M*2^(j-1),

    sum_over_carries x_j
      = (T/2) sum_(j>=1)(t_j-1)/L_j < T.                   (5)

Count.product(digit,entry_bits) scans log(W+1) multiplier digits, with
operand/result lengths O(log(x_j+1)+log(W+1)). Its schoolbook cost is
O(log(W+1)[log(x_j+1)+log(W+1)])=O((x_j+1)W). There are fewer than2T visited
fields and (5) bounds the sum of x_j, so all such products cost O(TW).
The initialization's extent products are similarly absorbed by t_i W.

read_field copies and normalizes at most ell_j<=W bits. It runs once at a
higher-axis carry stop, not once per changed suffix factor. previous_field
crosses at most one adjacent ell_i-bit field per cache update. Counter
increments, their local returns and adjacent cache moves therefore cost
O(W sum_k T/L_k)=O(TW). No full counter rewind occurs per coefficient.
Short cache-word replacement, complete component additions/truncations and
borrowed/owned cleanup are linear in the cells scanned. The inherited encoded
indices/Counter operations use amortized ripple updates; they do not perform
a full-length comparison at every bit. Initial cache filling is O(dW).

Including final output consumption, a conservative complete envelope is

    O(T M(W)+TW+d^2W+table manufacture/serialization).      (6)

The zero-entry initialization is already O(dW); the displayed d^2W permits
the predecessor's more general cache-initialization bound. Under the frozen
M(W)=O(W log^2(W+2)) invoice, the online part is
O(TW log^2(W+2)+d^2W). Thus this physical pass has the required power-zero,
polylogarithmic cost at #4100's layout without adopting its complete theorem.

## 7. Ownership, retained space and setup

The fixed inventory contains the scratch pool, counter, cache, output and all
active/inactive scalar-word descendants. All five external roles are mutually
distinct and outside that inventory. Origins use paid local delimiter checks.
Construction is sealed during invocation; Count/Signed objects refer to fixed
reusable physical pool roles. Host diagnostic counters are observers only:
removing them changes no branch, tape action or returned bit.

A pending flag protects the output even when its head has moved to the final
blank. consume erases body and marker before reuse. Ordinary validation
failures close all temporaries, clear owned prefixes and restore borrowed
heads. Concurrent mutation of borrowed data or private child tapes is outside
the contract. The physical fixtures check successful and failed cleanup.

Current storage, including input, prepared tables and protected return, is

    O(TW + W sum_i t_i + dW + scalar-owner backing).         (7)

Counter shape uses sum_i(ell_i+1) cells and the cache d+1 complex words.
The frozen word proof gives O(W) storage at this scalar width, including its
stack and twiddle workspaces. On reuse every role's largest prior allocation
is still retained and charged, including word descendants, the long output,
cache and counter. Blank retained tails do not disappear from the space bill.
The inherited Tape.clear stops at the current first blank; it does not rescan
historical empty tails. A grow/shrink fixture requires equal current action
counts with fresh and previously widened owners, while retaining their
different backing volumes.

EncodedChirpTables performs input-independent integer validation and physical
serialization. A conservative validation/serialization tariff is
O((sum_i t_i)W^2+sum_i ell_i+d log^2(W+1)); page storage is in (7).
Certified phase manufacture adds SOURCE.md's explicit per-entry work and
retained interval-cache history. Multiple retained preparations sum their
storage. No numerical receipt, free table oracle or silently discarded source
cache substitutes for that bill.

## 8. Evidence boundary and remaining obligations

Finite executions check every bit against a separate original-coordinate
rounded chain, including unequal axes, all-binary carries, d=1, conjugation,
zero rounded factors and signed complex payload. Actual scalar calls agree
with (4). Malformed payload/page/shape, external/owned aliases and moved output
controls test the ABI. A wider prior call is followed by a narrow one with
identical live action counts to a fresh narrow owner and larger retained space.

Source-aware independent review and source-table certificates complement the
trace. Neither is a human acceptance or proof-kernel claim. Finite fixtures
exercise the word engine's base branch; universal arithmetic uses its pinned
all-size contract. Full convolution/FFT assembly, production prime existence,
outer supplier/CRT/recovery integration and a stronger complete multiplication
bound are not established here.

The conservative d^2W term is absorbed by TW: d^2 <= (9/8)2^d <= (9/8)T
for integer d>=1. The online consequence is O(TW log^2(W+2)).
Reported action deltas cover a checked transaction: run, literal output read,
rejected pending call and consume. They are not bare-run transition counts.
Finite-alphabet actions differ by a fixed encoding factor from binary steps.
