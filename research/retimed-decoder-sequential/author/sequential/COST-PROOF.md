# Sequential bookkeeping for the same decoder service boundary

## 1. New claim and inherited boundary

This is a supplement to the immutable `../PROOF.md`, not a replacement for
that representation theorem. It uses the same binary `Plan.decode` and
`Plan.run` from #8042 at `dfd25d553a843a946ca0b94130a5ff8943e98fdd`;
`../SOURCE-BINDINGS.json` pins the exact source, graph, caller and predecessor
owner/mass arguments. The canonical comparison remains
`e54523517d0f03e58352e647c403a5af3e525a57`, and #8091's predecessor remains
`b500f72bbcf9c03a7f7fd40b366eedd6d1dd285b`. All five selected assumptions and
the selected conditional kappa 0.00363005817 remain unchanged.

Let a successful production activation have h>=3000, N=2^h, B=N^92 and
complete input volume W bytes. Keep all legal-call, custody, callback-return
and numerical-source hypotheses of the original proof. In particular

    P=18906, q=104904, C=2N^83,
    sum_e count[e] < 2N^6, ticks=N^82, rounds=N^2,
    source_width>=1, width=B, W/B>=9^N.

For the **supplied immutable event tape** and exact charged chart library,
there is a sequential finite-alphabet realization of the decoder-side
bookkeeping for the entire literal `Plan.run` such that:

* the ordered callback sequence and every Job value agree with the source;
* all reads, writes, head movement, lookup, copying, local conversion,
  callback-request/reply metadata and retirement are charged;
* its sum of local historical role allowances remains below 32BNh bits;
* its total local bookkeeping cost satisfies

\[
 T_{\rm bookkeeping}<B N^{350}<B N^{512}\le B9^N\le W.\tag{1}
\]

A tape step here reads or writes one binary cell, changes finite control, or
moves a head by one cell; fixed-alphabet symbols are encoded by two bits.
The large exponent is deliberately conservative. It does not become a new
constant in the old multiplier tariff.

**The exclusions are substantive.** Generating the Plan, evaluating Measure,
producing the event sequence, and producing the exact common chart library
are setup tasks outside this theorem. Copying the supplied encoded event
sequence, rereading it, and storing it are inside. In bounded fixtures,
`event_reader` accepts source record tuples and calls `pack_records` and
`bit_image`; those complete host tuple/byte/bit-list images are diagnostic
input adapters. They are not asserted to fit the production K workspace,
and their Python construction is not an instruction trace. The physical
algorithm starts from the already encoded supplied calendar and stream-copies
it to the one charged event role, buffering only the current source record. The native service body,
leaf computation, zero allocation/erasure body, whole-Receiver fields and
outer numerical fields remain outside. They retain their own storage and
time charges. A bounded slot is a request address, not a free jump to a
native iterator. The service side must locate/resume that resident body and
pay its movement and state cost. This proof covers writing the request and
reading the reply at the decoder interface. A real integration must add the
service-side dispatch cost to the callback bill.

A recursive leaf's own bookkeeping is part of that leaf's bill, not silently
absorbed a second time by (1). We prove (1) per actual `Plan.run` activation.
No complete native controller, complete finite-tape multiplier, old fast
tariff, activation threshold, or new kappa is claimed.

## 2. Machine model and concrete sorted tables

Use a fixed number of sequential tapes, independent of h, with binary data,
blank and a frame delimiter. Encode these four symbols by two binary cells.
Each tape has a single head. A local cursor and record length use w=128h
bits. Moving to position i is a loop of individual left/right moves; it is
never a random-access operation. Registers have at most 2w bits and are
implemented by the binary algorithms in Section 5. Finite control stores
only a fixed instruction location and flags. The interpreter's unbounded
statistics counters and comparison traces are diagnostic output, not
resident decoder state or control needed to stop the machine.

Each of the row, live and pending tables has **two fixed reusable tape
roles**. A table is a w-bit record count followed by sorted records

    key : w, payload_bit_length : w, payload : payload_bit_length.

The row payload is its Job; the live payload is `(slot, zero_count, zeros)`;
the pending payload is its Job. Jobs use the exact ordered token format in
`../codec.py`, with maximum J=4w+1+Nh<2Nh bits. Only dictionary keys are
sorted. Job axes, ports and zero-retirement lists retain their source order.

The following algorithms completely specify the table operations.

1. **Walk.** Rewind to the local left boundary, read the count, then stream
   each key, length and payload. Only the current payload is buffered.
2. **Get.** Perform a complete walk. Copy the matching payload to a result
   buffer and continue the scan. No index or cached location is retained.
3. **Insert, replace or delete.** Clear the other tape, write a provisional
   zero count, and walk the old tape once. Copy each unmodified record in
   order. Insert the new record at its ordered position, replace an equal
   key, or omit the deleted key. Rewind the output and overwrite its count;
   return to the saved local end. Clear the old tape and swap the two role
   labels. The input record and current copied record are separate buffers.
4. **Pop.** Get, then delete. Both scans are paid.
5. **Initialize.** The input count is already known (B for rows, zero for
   the other two). Stream the input records in order; do not first collect
   them into a host dictionary or another B-record array.
6. **Retire.** Rewind, overwrite every currently initialized cell with zero,
   and rewind again. Its logical extent becomes zero. Its historical peak
   remains charged to the same physical role.

`tapes.py` implements these head motions and binary-cell accesses directly.
A Python list represents the cells only for reference execution; every
access to an arbitrary tape position must pass through `Tape.at`, which
moves one cell at a time. The current record/result buffers are bounded
working tapes in this realization, not uncharged lists. Their transformations
are lowered as specified in Sections 4-5. The source and reference objects
are not being identified with CPython memory or instruction counts.

The same six table roles are reset and reused for every group/round and
later warm invocation. Reconstructing the row table is still paid each time.
An additional immutable input-row tape retains the source rows, which the
caller still needs after Plan.run. It is not hidden in the input argument.
Each decode reads that tape sequentially to initialize its working row
table. The immutable input image survives the return to its caller. It is
retired only on the next nonoverlapping caller handoff or after that caller
has consumed it. A nested caller uses its own frame. The reference loads
the supplied logical input into this charged role; it does not infer an
additional free copy of the source rows. Similarly the event tape and
callback request/reply tapes are reused. Clearing
a table does not reset its historical peak. No chronological list of old
states or old event logs is needed by the machine.

## 3. Decoder transition and callback ledger

`controller.py` follows the source's three event branches. Equality of the
serialized values and the original proof's induction give the same source
observations; replacing a lookup by a full sequential scan changes only
cost. The following ledger includes operations that are easy to miss.

| Stage | Explicit work | Maximum multiplicity |
| --- | --- | --- |
| Run driver | Compute group count, compare/increment group and round, call decoder | ceil(B/source_width) <= B groups, exactly N^2 rounds per group |
| Decode entry | Clear/reset the three pairs of table roles, write every external row, reset event cursor | B Job records per decode, including later rounds |
| Event read | Read opcode and ident, then exactly the source-arity fields; buffer the current row | At most 3+4P scalar fields |
| Open, pending port | Full pending get and deletion/rewrite; preserve ordered port | At most P ports |
| Open, external port | Integer division/remainder, source guards, row lookup, ordered selection | At most P ports and N selected coordinates per port |
| Open, zero port | Row-zero lookup/selection, write zero request, read returned Job, append port and ordered zero list | At most P ports |
| Open, free slot | For candidate slots 0 through C-1, scan the whole live table; stop only at a missing slot | At most C complete scans; no occupied-slot set |
| Open, native | Write ordered ports and columns request; read service acknowledgement; insert live record | One request and one full live-table rewrite |
| Paid | Get live record; issue resume request with slot; read/check returned full Job | One get and one service request |
| Paid, leaves | Preserve full Job and source cursor; restore it, select axis k, write request, read return, advance k | Exactly size-selected <= N iterations |
| Paid, pending | Select the source prefix in order and insert serial/Job | At most one table rewrite |
| Close | Pop live record; issue final resume; check no extra Job; issue retire requests in original zero-list order | At most P retire requests, plus two live scans |
| Decode exit | Check table emptiness, clear all current table cells and scratch, rewind calendar | Fixed number of complete scans |
| Final run exit | Clear supplied calendar copy and request/reply scratch | Fixed number of complete scans |

A request writes an explicit w-bit opcode (zero=0, native=1, resume=2,
leaf=3, retire_zero=4), bounded service slot when relevant, argument
counts and the complete ordered Job token values. A reply writes a tag and
its complete Job value when present. Native entry includes its newly allocated slot in the request and can
consume the ports sequentially: the decoder expands one Job at a time, and any port list or
expanded copies retained by the body are service state. The bridge workspace
for the current expanded Job is charged below. The implementation writes
explicit request/reply tapes and retires them after each call. A callback
cannot be repeatedly reused without writing a fresh request.

In particular, `Controller.call` decodes the complete port list into host
Jobs before `action(*decoded)`. That host list is a correctness adapter,
not a literal fixed-tape memory implementation. In the physical refinement,
the decoder expands and transfers one Job at a time; the corresponding
expanded port list is allocated as service-owned input state. The decoder
pays each expansion and transfer, while that retained service input keeps
its explicitly excluded storage charge. No collection of P expanded bases
is hidden in the decoder scratch allowance.

The reference calls a resident Python service to obtain its logical reply;
that call is the external service boundary. It does not demonstrate constant
time native dispatch, and does not treat the `services` dictionary as free
controller storage. The native body's state and mapping from a slot to that
body are explicitly external obligations. All decoder-owned rows, live keys,
zero lists, pending Jobs, ports and continuations are represented on charged
tapes. The sole persistent reference dictionary holds the excluded service
bodies.

Current record buffering is real: a result found early in a get survives
while the walk scans a later record. Both buffers are counted. During a paid
leaf, the full original Job and k survive, so selecting or returning a leaf
does not discard the continuation. Raw source integer axes and paid typed
axes remain distinct. Exact chart tokens are expanded and re-encoded when
needed; no host identity cache is assumed.

## 4. Local transforms and historical storage

The complete finite source census in the original proof provides 595 exact
base words, at most 61 operations each, with signed coefficients needing
five numerator/denominator bits and an explicitly stored library of fewer
than 2^21 bits. A lifted basis has at most 61N operations. There is no variable
library of arbitrary callback objects.

A local Job transform can be carried out using scans as follows. Stream its
four headers and ordered coordinate list. For a typed Job, scan the fixed
library in order, derive a possible column multiplier from the word-length
ratio, and compare the literal lift coordinate by coordinate. The first
matching base gives the canonical token. To expand, stream that same lift.
To select positions, scan the saved Job from its beginning for each requested
position, preserving the selection order. To verify equal per-axis bases,
compare their complete values by repeated scans; the cost is paid even if
the reference shares equal tuples. Fixed rational coefficients are compared
by their stored signed integer numerator and denominator fields; no unbounded
precision arithmetic is introduced.

For concreteness, all of these operations, including rewinds of the current
Job/library buffers, fit the deliberately loose bound

\[
 D=2^{32}(N+1)^4                                             \tag{2}
\]

bounded-register macros per Job. This is an algorithmic bound, not a finite
measurement. There are at most N axes; a basis has at most 61N operations;
there are 595 candidate words. Even comparing every candidate against every
axis and restarting an operation scan for each comparison uses fewer than
595*61^2*(N+1)^4 elementary coordinate/field operations. The exact coefficient is
595*61^2=2,213,995<2^22. Each such operation uses fewer than 2^10 bounded
register/scan primitives (field copy, compare, bounded coordinate multiply,
loop update and rewind). Thus (2) is a strict upper bound. Streaming the
fixed library's fewer than 2^21 bits, token headers, and the empty/integer
cases also fits (2). A full input and one candidate expanded basis can be
held simultaneously; a conservative 1024Nh additional bits suffice. A whole live
record with z zero Jobs uses at most (z+1)D macros.

Let Ktab be the sum of the maximum logical extents of one tape from each
of the three table pairs:

\[
 K_{tab}=3w+B(2w+J)+C(4w+PJ)+qC(2w+J).                    \tag{3}
\]

This includes a count header per table, a key and length per record, and
slot/count fields in each live record. The inherited inclusive bounds
|live|<C and |pending|<=qC hold during opening and closing, not just between
paid events. Put

\[
 K_e=w+2N^{88}(5+4P+5q)w,
\]

and reserve

\[
 K_b=(10P+32)J+(16P+256)w+1024Nh.                             \tag{4}
\]

The ten P-sized scratch roles pay separately for the decoder's ordered ports
and zeros, current copied live record, retained lookup result, decoded zero
list, insert record, callback request and decoded request, reply conversion
and one spare record image. The extra thirty-two Jobs pay for the full paid
Job, selected/one-axis values, row/exemplar and encoding temporaries. The scalar
term pays the entire current event, callback lengths/tags, cursors and
local program state. These are separate uniform role bounds; their maxima
need not occur at the same instant. Use an additional 512w bits for 256 bounded register roles, including
arithmetic scratch, of up to 2w bits each; reserve 2048 more bits for the
fixed local framing metadata. The common library is separately charged.

Thus the sum of local logical historical allowances is bounded by

\[
 K=2K_{tab}+K_{rows}+K_e+K_b+2^{21}+512w+2048,
 \qquad K_{rows}=w+B(w+J).                       \tag{5}
\]

The immutable row tape pays one count, one length and each complete Job.
At h>=3000, J<2Nh, Ktab<3BNh, Krows<2BNh, Ke<BNh, Kb<BNh, and
2^21+512w+2048<BNh. These inequalities follow by division by BNh:
all non-row terms have a fixed coefficient times a negative power of N,
and the row coefficient is 1+O(1/N). For example the largest live/pending
powers are N^84 h, nine powers below BNh; the event term has four powers
of N of slack. Coefficients are fixed below 2^40. With N>=2^3000 they are
strict, and increasing h decreases every normalized correction because
(h+1)/h<2 while N doubles. Consequently K<11BNh. The binary symbol encoding
uses at most S=2K<22BNh<32BNh bits, and S<N^96. This proves the claimed
uniform **sum of per-role maxima**, including already cleared high-water
cells. It does not use a maximum instantaneous total in place of that sum.

Local offsets, record lengths, count values, source indices and coordinates
therefore fit w bits. Intermediate products use 2w bits. No run-wide step
counter is required; the much larger total running-time bound does not
invalidate the scalar-width proof.

## 5. Bitwise register lowering

A bounded-register macro is a copy, compare, addition, nonnegative
subtraction, shift, multiplication, quotient/remainder, or loop-control
update on at most 2w bits. Sign handling for the fixed coefficients uses a
separate sign bit. Fewer than 256 registers including scratch suffice for the fixed program.
A deliberately padded census assigns 64 to head/extent pairs for at most
32 data/scratch tape roles, 24 to table transactions, 32 to decoder clocks
and current record fields, 32 to Job/library selection cursors, and 64 to
arithmetic, marked-loop and continuation scratch: 216 in total. All are
reused after their local operation. Constants P and q are part of the fixed
program, and variable lists are streamed through these same cursors.
Variable lists are on the already charged tapes, not on an unbounded stack
of registers.

Here is a literal implementation, independent of a unit-cost RAM model.
Copy/compare stream the two registers. Addition and subtraction ripple carry
or borrow from low to high bits. Multiplication loops over the two input
bit positions and adds each set partial product with a ripple carry.
Division scans numerator bits from high to low, shifts a remainder register,
compares it with the divisor, and subtracts when possible. Any access to
bit j first moves the corresponding head to j by one-cell steps. Rewinding
or changing which fixed register is active also uses explicit movement.
The finite-tape version marks the current bit positions on a fixed scratch
track and advances those marks by scans; it does not recurse into an oracle
that updates arbitrary-precision loop counters in unit time. Each such mark
update or reset costs at most another full register scan, already covered
by the fourth-power envelope below.
The divisor is positive at each actual source division.

If L=2w, multiplication has at most L^2 bit-pair visits, at most L carry
visits per pair, and at most 8(L+1) binary-cell actions per carry visit.
Including the marked loop positions, its cost is below 256(L+1)^4. The division algorithm uses at most L iterations,
each with a shift, compare, subtract and bounded head resets, below
256(L+1)^4. All simpler macros fit the same fourth-power envelope. Encoding
symbols, dispatch among at most 256 register roles, and loop-cursor updates
are covered by the much larger allowance

\[
 R=2^{20}(2w+1)^4                                           \tag{6}
\]

binary tape steps per macro. `registers.py` supplies the direct bitwise
copy, compare, ripple, product and restoring-division witness. Its tests
check values and actual movements at bounded widths; the loop analysis
above is the all-width proof. The interpreter records table cell actions
separately from conservative register/adapter charges. Multiplying their
sum by R is an upper-bound receipt, not a measured native machine clock.

## 6. Transparent composition of the clock

For production h>=3000, w<N, D<N^5 and R<N^16. A complete augmented sweep
may read/copy/clear a whole local table or scratch role, decode or re-encode
every Job it visits, and restore its cursor. Each table contains at most S
bits and at most S nonempty fields/Jobs. Count all movements, scalar work,
current-record copies and adapter work using

\[
 Q=64S(D+128)(R+32)<N^{128}.                               \tag{7}
\]

This even charges a Job transform per bit instead of merely per Job. It
covers a full table get, a full rewrite with its header patch and old-tape
retirement, initialization of the B-row table, a scan of the chart library,
copying the supplied event tape, one callback's metadata transfer, and one
bounded current-record transformation. Multiple such operations are counted
separately below. There is no zero-cost hash lookup inside Q.

The branch ledger in Section 3 is bounded, per event, by

\[
 M=64(C+PN+N^2+N+1)<N^{128}                               \tag{8}
\]

augmented sweeps. The C term pays the intentionally slow free-slot scan;
the PN term pays all ordered port selections and their individual row or
pending lookups/copies; N^2 allows repeated coordinate scans; N pays all
paid leaf continuations and request/reply transfers; the constant and
factor 64 cover fixed reads, table rewrites and retirement. Whole live
zero lists decoded during free-slot scans are included in Q. Neither C
nor B is replaced by a constant.

The exact supplied calendar has

\[
 E=(q+2)N^{82}\sum_e count[e]<2(q+2)N^{88}<N^{90}            \tag{9}
\]

records. The sum counts each open, all q paid resumes, and each close.
Late-closing contexts do not generate an additional family of opens.
Hence the event work of one decode is less than N^90*N^128*N^128=N^346.
Entry/exit setup, including **all B external rows on every decode**, and
calendar positioning/retirement cost less than N^200 (fewer than 64 augmented
sweeps and simple loop/register overhead). The loose sum is less than
2N^346 steps per decode.

The actual `Plan.run` performs ceil(B/source_width)*N^2 decodes, at most
BN^2. This includes every group, every round, each repeated row initialization,
and each replay of the entire event tape. The outer loop's own arithmetic
is less than BN^200. Therefore

\[
 T_{bookkeeping}<2BN^{348}+BN^{200}<BN^{350}<BN^{512}.        \tag{10}
\]

The two extra exponents at the final comparison absorb the explicit sum,
not an omitted iteration. One can improve this gross bound substantially;
no such improvement is needed for this scoped conclusion.

The all-size cutoff for the last exponential comparison is explicit. For
N0=2^16,

\[
 9^{N0}>2^{3N0}>2^{8192}=N0^{512}.
\]

For every integer N>=N0, the binomial theorem and
binom(512,k)<=512^k give

\[
 (1+1/N)^{512}\le\sum_{k=0}^{512}(512/N)^k
 <\frac1{1-512/N}\le 2<9.
\]

Induction therefore proves N^512<=9^N for all N>=N0. The production cutoff
N>=2^3000 is far stronger. Combining this with the actual source geometry
W/B>=9^N proves (1) without floating-point estimates or an unevaluated
asymptotic constant.

## 7. Suspension, local positions and historical reuse

A recursive callback can suspend the decoder while its six table roles,
full paid Job, cursors and pending lists remain stored. Use LIFO tape frames
with explicit delimiters. Save only each head's position relative to its
current frame, then move to that frame's end before entering the child.
On return, erase the child's current initialized region, stop at its frame
marker, and restore the parent's saved relative positions. Entering and
restoring a parent frame costs at most a fixed number of parent-local
augmented sweeps, already covered by the callback term in M. The child's
own cleanup is in the child's own bill. No absolute global stack address
or recursion-depth integer is assumed to fit w bits.

Previously larger erased regions remain blank and historically charged.
A later smaller call reuses a prefix without seeking to the old farthest
cell merely to forget it. This is why logical retirement can be fast while
the sum of historical maxima remains the relevant space quantity. Applying
the original proof's same-stage shrink and fixed-stage history hypotheses
to this new below-32BNh realization retains its conditional additional
<2W and <4572 Xmax history allowances. Those are control additions; all
excluded service and whole-field role charges remain to be supplied.

## 8. Bounded evidence and remaining questions

`check_sequential.py` compares the unchanged source decoder with the
sequential table implementation on supplied calendars, compares a complete
multi-group/multi-round source `Plan.run`, verifies the immutable input rows
survive return, and repeats it using the same warm table roles. It checks current-record rewrites, insert/delete ordering,
physical lookup distance, preserved historical peaks, explicit distinction
between zero and retire action opcodes, and the fact that
omitting source rounds changes the callback trace. The source generator
fixtures deliberately exercise pending loans, delayed closes, external
source guards, selected prefixes and ordered zero retirement. The register
witness checks its literal binary arithmetic. All guards are explicit
exceptions and remain active under `python -O`.

These bounded runs test the implementation and reject specific shortcuts.
They do not create the universal clock theorem by extrapolation. Equations
(2)-(10), the original complete chart census, and the retained owner/source
hypotheses supply that theorem.

The next concrete tasks are: account for producing the event tape and Plan
without unbounded setup dictionaries; implement and price service-side
slot dispatch together with the actual native restoration/register state;
and compose the resulting local terms with whole-Receiver headers, actual
precision stopping control and the complete caller tariff. A successful
result here alone does not justify deleting any selected assumption.
