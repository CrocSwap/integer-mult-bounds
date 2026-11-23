# Independent review: sequential decoder bookkeeping

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. This is separate model-assisted review, not independent human
or formal-kernel acceptance.

**Decision: accept the scoped sequential-bookkeeping implication** at
COST-PROOF.md SHA256
`ff44f670b01ebb6748a0f5879d2fc83c1bc1950c9f15cb0a14743d86f7634ea8`
and the implementation pins in FROZEN-INPUTS.json. The inputs are a supplied
encoded calendar and the exact fixed chart library. Native service bodies,
service-side slot dispatch, complete Receiver/numerical state and generation
of the Plan/calendar/library remain external. No selected assumption is
removed and no new kappa is accepted.

## Review method and exact source boundary

I read the sequential proof, table/register/controller implementations,
the original representation proof, codec and source bindings, and the
literal original `Plan.decode`, `Plan.run` and `axes` definitions. The
original scientific-freeze and source-manifest hashes are checked, as are
all 17 retained source SHA256s and every supplied Git blob identity.
This review uses those authenticated retained exports; it does not claim
a new remote archive or canonical-history audit.

`independent.py` never imports or runs either author checker. It compiles
the implementation bytes directly, bypassing bytecode caches. Expectations
come from four separate constructions: integer arithmetic for registers;
a dictionary and independently parsed bit image for tables; literal source
Plan methods with a newly written native-service fixture for callbacks;
and exact integer formulas for the complete cost/space inequalities.
An independent tape shadow tracks every head move, read, write, erased
region and historical endpoint. The code under test does not supply those
expected values or positions.

## 1. Streaming tables and actual access

The corrected `Table.reset(records,count=...)` consumes records once in
source order and does not collect a generator into a B-record host list.
Each row/live/pending table has two reusable physical roles. A replacement
streams old records into the other role, patches the count by paid head
movement, clears the old role and swaps role labels. A get keeps its result
while continuing the complete scan; the current-record and result buffers
are both included in the proof. A pop performs both its get and delete.

Sorted dictionary keys preserve key associations. They do not authorize
sorting a Job's axes, port order or zero-retirement order. No indexed host
lookup is used as the proposed physical table operation. The audit shadow
confirms that observed movement is a sequence of one-cell changes and
that metered cell actions equal reads plus writes plus moves. An unpriced
head-jump mutation fails this independent position invariant.

Erasure resets logical initialized length, while each fixed role's old
historical endpoint remains. The two-role history sum survives swapping,
clearing and subsequent shorter writes. The checker retains its own shadow
memory after the implementation drops its host list, and verifies that
the previously initialized region was overwritten. A mutation that resets
the historical peak on clear is rejected.

The immutable input-row image is separately charged. Every decode copies
all B rows from it into a new working table. That image survives return to
the caller; the next nonoverlapping handoff may replace it. Nested calls
need their own frames. Calendar copying occurs once per complete run and
all rounds reread it. These details avoid treating source input, warm
history or repeated initialization as free.

## 2. Registers and Job transformations

The register witness uses binary reads/writes and explicit head movement.
Addition/subtraction propagate carry/borrow from low to high bits. For a
legal nonoverflowing multiplication, every positive partial sum is at most
the final product, so the stated output width suffices. Restoring division
maintains the prefix remainder: before processing the next bit, it is less
than the already read prefix bound as well as the divisor. Therefore its
next shift fits the full numerator width, even for a large divisor. The
final quotient/remainder match Euclidean division. The code rejects invalid
aliasing, zero divisors and overflowing operations where required.

For L=2w, at most L squared bit-pair visits, each with at most L carry
visits and O(L) movement, give the fourth-power multiplication bound.
Division is cheaper under the same envelope. Marked loop positions and
their resets are charged in that envelope. The generous
R=2^20(2w+1)^4 covers finite dispatch and binary symbol encoding; it is not
a measurement of Python execution. Fixed register roles can be scanned
within a constant bank; no absolute global recursion-depth address must
fit w.

The local Job bound D=2^32(N+1)^4 is also conservative. There are 595 fixed
candidate bases, at most 61N lifted operations and at most N axes.
Restarting scans to compare candidates/axes and preserve selected order
is covered by the displayed fourth power. The coefficient check is exact:
595*61^2=2,213,995, and multiplying by 2^10 remains below 2^32. Coefficients
have fixed signed fields; their comparison does not introduce a growing
rational-arithmetic oracle. A common expanded basis and a current candidate
use O(Nh) bits, so the 1024Nh bridge is ample for this streamed refinement.

The earlier meter using N squared was corrected before acceptance. All
four implementation adapter charges now use D (or (z+1)D for a live record
with z zeros). Replacing the fourth power by a square is rejected by the
independent per-Job charge check.

## 3. Exact callback chronology and continuations

The original source branches and the sequential implementation agree:
pending loans are popped at the same ordered port, external guards use
the same group/round arithmetic, zero ports preserve exemplar axes, and
native entry receives the same ordered Job values and columns. The free
slot search scans the live table; only the mapping from that slot to a
resident service body is outside the decoder boundary.

A paid callback retains the complete Job, identifier/serial/size/selected
values and loop position while processing one-axis leaves. Consequently
it can continue with the next axis and retain the correct ordered prefix.
A close performs the final resume before retiring its zeros in source
order. The supplied native service contract relates these callback states;
the bookkeeping theorem does not serialize its generator or restoration
state.

I extracted the original Plan methods independently and supplied a separate
nested calendar with a pending loan, child return, zero ports and external
guards. The mock service constructs nontrivial typed bases independently
from the retained fixed words and issues deliberately nonmonotone axes.
Complete source and sequential traces agree across three Plan.run cases,
24 decodes and their warm repeats. Omitting rounds or reversing a pending
prefix changes the trace and is rejected. Testing complete Plan.run matters:
the source performs ceil(B/source_width)*N^2 decodes, including every group,
round, calendar replay and row initialization.

## 4. Clock and historical-space argument

The proof's K includes both images of all three tables, one immutable row
image, the event tape, separately bounded record/transfer buffers, the
fixed library and register/framing allowance. The exact independent
substitution uses 512w+2048 for the latter: 256 register roles of up to
2w bits, followed by the separate framing reserve. An earlier reviewer
script used 256w+256; that transcription was corrected and both modes
rerun before this review freeze. Uniform per-role maxima
are added; a maximum simultaneous live total is not substituted. Its
leading row term is BNh. Live/pending terms have fixed coefficients at
N^84 h; the event term is O(N^88 h); buffers/library are smaller. For
N=2^h, h>=3000, the displayed comparisons give K<11BNh and encoded
S=2K<22BNh<32BNh, with S<N^96.

All actual local metadata values fit w=128h. Intermediate arithmetic fits
the stated 2w scratch. There is no running-step counter of size B N^350:
the source stops through nested bounded loops. A recursive suspension uses
local frame positions and head marks; parent handoff/return is charged to
the parent, while the child's own bookkeeping remains in its own bill.

The inequalities D<N^5 and R<N^16, together with S<N^96, imply
Q=64S(D+128)(R+32)<N^128. The event ledger has fewer than
M=64(C+PN+N^2+N+1)<N^128 augmented sweeps. Counting an adapter per bit,+rather than per Job, safely pays variable zero lists and repeated decoding
within the deliberately slow free-slot scans. The calendar has fewer than
N^90 events. Thus one decode costs less than 2N^346 including entry/exit
work, and at most B N^2 decodes plus the driver yield

    T < 2 B N^348 + B N^200 < B N^350 < B N^512.

The exponential comparison is effective, not asymptotic shorthand.
At N0=2^16, N0^512<2^(3N0)<9^N0. For all N>=N0, the binomial bound
and geometric series give (1+1/N)^512<2<9. Integer induction therefore
gives N^512<=9^N, and the retained physical volume W/B>=9^N yields T<W.
I checked all numeric component inequalities exactly at four production
heights; their universal validity follows from these power/ratio arguments.

This cost can be larger than a retained fast per-operation tariff. Its
absorption into the whole presented volume proves only this local service
boundary's invoice. Setup, native dispatch and native bodies are still
added to any complete caller accounting.

## 5. Required implementation/representation distinctions

Two clarifications were requested and incorporated into the accepted proof.
The bounded Python `event_reader` first packs source tuples and materializes
whole byte/bit images. Those host objects are a diagnostic input adapter.
The claimed physical algorithm starts with the already encoded supplied
calendar and stream-copies it, with only its current record buffered. The
Python adapter's memory or instructions are not certified by K or the clock.

Similarly, `Controller.call` builds a decoded host port list before calling
the Python service. The proved physical refinement expands and transfers
one Job at a time. The native service owns any complete expanded port list
that it needs to retain; its storage remains in the excluded service bill.
The decoder pays expansions/transfers and keeps its compressed port tokens
on charged tapes. This distinction prevents P expanded bases from being
silently charged as one current Job.

The accepted result is consequently a source-equivalent streamed refinement
with bounded reference witnesses. It is not a claim that the complete Python
controller already has the stated memory consumption or physical clock.
No native dispatch dictionary, hidden service coroutine or setup producer
has been made free by the proof.

## 6. Executed independent evidence and reproduction

Normal and optimized receipts are byte-identical. They cover:

- 360 randomized table insert/replace/delete operations at three widths,
  with independent sorted-bit parsing and 1,587,776 audited cell actions;
- 1,959 register value checks, exhaustive input pairs through four bits
  plus boundary cases at eight and seventeen bits; the largest observed
  arithmetic macro uses 6,834 cell actions;
- three original-source Plan.run comparisons, 24 complete decodes,
  352 source-service actions and three warm repeats;
- exact storage, register, event, sweep and complete-clock inequalities at
  h=3000,3001,4096,10000, plus the exact N0=2^16 exponential base;
- seven controls rejecting omitted rounds, reversed pending order,
  quadratic adapter undercharging, unpriced head relocation, lost historical
  peaks, failure to subtract an exact divisor and source corruption.

The first six controls mutate actual execution/accounting behavior. The
last checks the fixed source-hash discriminator. Universal conclusions use
the inspected algorithms and written inequalities, not extrapolation from
these finite tests. Native numerical action is deliberately abstract in
the newly written service fixture.

With standard-library CPython 3.12:

```sh
python3 -I -B review/independent.py --package PATH_TO_DECODER_PACKAGE
python3 -I -O -B review/independent.py --package PATH_TO_DECODER_PACKAGE
```

The directory supplied to `--package` contains the original representation
files, `sources/`, and the `sequential/` appendix. The review may be stored
elsewhere; it uses no current working-directory dependency. Acceptance pins
and receipt hashes are in FROZEN-INPUTS.json and REVIEW-RECEIPT.json.

The remaining work is concrete: generate the Plan/calendar/library under
a complete setup invoice, implement service-side slot dispatch, account
for resident native restoration/register state and whole Receiver headers,
then join those costs to the actual enclosing numerical/stopping contract.
This review does not assert those obligations are satisfied.
