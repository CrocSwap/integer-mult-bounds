# Consume canonical switch bits from an actual current CRT lease

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Uniform literal point-consumption adapter; bounded actual source/payload
composition. **No new kappa.** All five foundational assumptions remain.

## 1. Exact source boundary and new claim

Nick Petalas's #7504 supplies the canonical padded-rotation formulas. The
literal predicate B4 at CubeJerry commit
`56335a406469fad85e88ff72820d506d8bea6f63` implements those formulas with
2096 instructions on fourteen fixed tapes. Its original explicit boundary
supplies encoded h,s,a,j,x and receives one owned Boolean. This package
implements the physical preparation and consumption needed at the actual
encoded CRT payload caller, with current data read from that caller.

The caller is #7388 at `d6f4a69202ad0bba4a915f4d4f3eaba1fe431c86`,
`research/encoded-crt-leaf-payload`. Its retained frontends and writer are
from #7352 at `8c0e55c9ba25ff2c8199b01539a4d56ae71a1473`. Their source
symbol routines, numerical result lease, source commit, payload format and
literal radix consumer remain the exact pinned code. The new path replaces
the owned ROM/layer stream and row scans by the direct point adapter. It
does not replace numerical offsets with a host CRT calculation.

The default adapter emits one fixed 2500-instruction graph on twenty tapes.
The frozen B4 graph is embedded instruction for instruction, with a fixed
symbol renaming. The adapter itself contains no runtime numeric register,
data-dependent Python loop, decoded parameter or query callback. The outer
source/row controller retains its existing symbol-action semantics. Its
complete measurement is a cost vector, not a claim that the whole controller
has been compiled into one literal bit program.

## 2. Uniform physical adapter theorem

Fix integers h>=1, p>=h+1, 1<=s<=2^h, 0<=a<s, 0<=j<=2h-2,
0<=x<2^h and 1<=k<=h. All encodings below are least-significant-bit first.
The six external roles are:

| Role | Complete live framing and entry head |
|---|---|
|14: height|`L`, exactly p bits representing h, `R`; head at `L`|
|15: modulus|`L`, p bits representing s, `R`; head at `L`|
|16: offset|`L`, p bits representing a, `|R`; head at `L`|
|17: current row|`L`, p bits representing j, `R`; head at `L`|
|18: current mutable wire|`L`, exactly h bits representing x, `R`; head at `L`|
|19: target capability|`L`, exactly h unary ones, `R`; head at the kth one|

In particular, **the encoded height equals the unary width**. These are
matching semantic descriptors, not merely syntactically valid digit strings.
All twenty physical owners are distinct. The fourteen internal owners are
blank on the granted windows and start at position zero. Their earlier
historical backing remains charged. Every live frame has its unique origin
and exact declared endpoint; arbitrary opaque cells beyond those live frames
are preserved. The theorem supplies physical placement and access, rather
than deriving them from an abstract owner label.

Let b be bit x of row j of the exact deterministic source network
`benes(rotation(2^h,s,a))`. On success the adapter changes the physical wire
value to `x xor (b * 2^(k-1))`. Every other external byte is unchanged, all
five framed-word heads return to their origins, and the target head returns
to the same kth physical cell. All fourteen internal histories are blank
within their granted windows and all internal heads return to zero. The
Boolean produced by B4 is physically read, used and retired inside this
invocation; no external observer supplies or selects its value.

For the actual row-layer interpretation also require
`k-1 = min(j,2h-2-j)`. Under that condition this endpoint is precisely the
source's jth switch layer. An arbitrary valid k gives the stated bit-toggle
primitive, not necessarily that network layer. The caller's encoded control
in Section 5 establishes this target/row relationship at every invocation.

This theorem includes s=1,a=0, h=1, zero offsets, and s=2^h. The retained
numerical CRT producer imposes the stronger s>1 condition, so unit modulus
is not an admitted actual caller example. Its explicit rejection is kept.

## 3. Preparation, literal embedding and cleanup

The adapter first checks the fourteen blank origins, five source origins
and the selected unary cell. It replaces that selected `1` with `|` and
returns the width head to `L`. This unique temporary marker records an
actual physical position. It then installs six owned input/output guards.

It copies all p height bits and physically erases the high zero suffix.
The remaining owned height is the canonical positive binary encoding of h.
The old source height and all its high padding are preserved. Historical
capacity p is retained even though only bit_length(h) digits remain live.

For s,a,j it scans the unary width, counting both its ordinary `1` cells
and its one temporary marker as one cell. It copies h digits, then one
additional digit, and checks every omitted source digit is zero. It checks
the actual `R` or `|R` boundary and rewinds both heads. For the current wire
it copies exactly h bits, checks `R`, and appends a high zero. Thus all four
unsigned B4 fields have exactly h+1 bits. Bounds on s,a,j,x ensure that no
nonzero significant digit was discarded. This also retains the high bit
when s=2^h. The height/width consistency premise makes every B4 length exact.

B4's alphabet is renamed once at compile time: 0 and 1 become `0` and `1`,
blank becomes `_`, LEFT becomes `L`, and END becomes `|`. The additional
external `R` symbol is never present in an admitted B4 body. Its unused
branches go to B4's rejecting cleanup. B4's exact fourteen ports are
unchanged, numbered 0 through 13; the six caller roles are 14
through 19. No public marker undergoes a runtime conversion. Every embedded
read, write, unit move, jump and halt corresponds to one original instruction;
the final halt transfers to the appropriate local continuation.

Successful B4 returns all its heads to their first body cells and erases
its eight private guards/bodies, leaving the six owned input/output guards.
The adapter reads its actual output bit. It walks width and address together
to the temporary marker, writes the old address bit xor that Boolean, restores
the unary `1`, and rewinds the address. The width head stays at its original
target cell. The two possible Boolean outcomes are finite control states.

Finally it erases each of the six input/output bodies by a full forward
scan, returns through the cleared cells, and erases its guard. It moves the
eight already blank private heads one cell left. Every owned head is again
zero. Trailing height padding was already erased during preparation; all
other granted tails were blank and remain so. No old high-water capacity
is refunded by that retirement.

Whenever preparation completes with matching height and width, B4 domain rejection restores
the target mark and clears owned copies without changing the wire. Bad origins,
dirty private grants, missing/interior markers, incorrect lengths or inconsistent
height/width are outside the success theorem. No arbitrary malformed-input
rollback or uniform malformed-height resource bound is claimed. Some bounded
malformed cases are tested; those checks do not enlarge the stated domain.

## 4. Complete point time and history

Count one emitted R/W/M/J/H instruction as one fixed-alphabet transition.
Every M moves one head by one physical cell. A fixed binary encoding of this
six-symbol alphabet changes these counts by an absolute constant; no common
one-for-one tariff with the separate outer source controller is inferred.

Write ell=bit_length(h). The following counts are exact on every valid
successful invocation, independent of the Boolean answer:

| New part | Instructions |
|---|---:|
|Entry checks, mark, width rewind, six guards|`34+3k`|
|Full p-bit height copy, trim, both returns|`12p-ell+10`|
|Modulus and row copies, each|`6p+10h+22`|
|Offset copy, including its extra separator|`6p+10h+27`|
|Current-wire copy and appended high zero|`16h+22`|
|Eight private heads to B4 body origins|`8`|
|Read actual Boolean, seek/toggle/restore target|`7k+6`|
|Erase six owned fields/guards, eight returns, halt|`7ell+28h+110`|

For example, each ordinary width-guided digit costs seven instructions;
each discarded high zero costs three. An origin return from cell t costs
3t+1. The offset has an extra move/check plus three extra return instructions.
Height trimming charges four instructions per discarded high zero. Cleanup
of an n-bit owned input from its first body cell costs 7n+11. The six input
lengths sum to ell+4h+5; eight additional moves and the final halt account
for the last table entry. These identities follow by exhausting the emitted
loops, not by fitting finite observations.

The complete new overhead is therefore exactly

`A(p,h,k) = 30p+74h+6ell+10k+261`.

Since ell<=h and k<=h, `A <= 128(p+h+3)`. The embedded successful B4 count
is unchanged, including its final halt/continuation instruction. Its proved
bound yields the complete uniform result

`T_point <= 1024(h+3)^2 + 128(p+h+3)`.

All header reads, allocation writes, copies, temporary marking, movement,
Boolean use, cleanup and returns are included. There is no omitted helper
work inside this point boundary.

The copied height alone may visit p+2 cells. Compared with B4's fourteen
role history, its extra high zero suffix adds at most p cells. Its other
copied inputs and their guards lie in B4's already charged intervals. The
six borrowed roles stay within their supplied live frames. Thus a convenient
complete increment is

`K_after <= K_entry + p + 16(h+4)`.

This is a historical backing bound; repeated invocations take actual unions
and keep all larger earlier extents. Active owned space is O(p+h) fixed-alphabet
cells. All fourteen owners are reused after return; no fresh owner is created
per row, wire or query. Source/payload/window acquisition and transport into
this physical ABI are outside this local boundary and remain in the caller bill.

## 5. Paid current-row control and actual source access

The retained `emit_headers` walks the current encoded axis prefix and actual
source records while a numerical result lease is live. It obtains the unary
right width from source symbols, constructs the height by paid increments,
copies the right modulus and pads with the actual precision guide. It copies
the offset from the actual result stream with `copy_numeric_field`. The source,
result, axis, half and precision heads return. No test oracle contributes a
number to these headers.

This construction binds the height value to the same unary width used by
the point adapter. The current row field begins as p zeros. The physical
address for each payload is copied from the encoded position counter, then
updated in place by every point call. The predicate consequently reads the
current wire on every row, rather than the original input wire.

For forward routing, the row counter starts at zero. The unary target head
starts on its first cell, moves to the right endpoint, then back to the
left origin. For inverse routing, the controller scans all width marks after
the first and performs two paid increments per mark. This constructs 2h-2
without decoding h. It subsequently decrements that row counter. The target
head follows the same palindromic path in both directions. For h=1 the first
query is followed immediately by the endpoint/origin return.

Induct on query number i. Before query i, the target position is
`min(i,2h-2-i)`, and the row is i forward or 2h-2-i inverse. Hence the
point theorem's target/row condition holds in both directions. Each emitted
Boolean is applied to the current address. Termination follows from the
physical target cursor reaching `L` after exactly 2h-1 calls. Counter capacity
is sufficient because p>=h+1. Every increment/decrement and head traversal
is charged. The row field is physically zeroed again before return.

The existing physical position counter enumerates exactly 2^h positions.
For each, the caller walks the actual opaque payload, computes its destination
in the address tape, and writes that destination into its allocated MSB-first
key cells. It never decodes a key or copies a replacement payload tape. The
retained stable radix program then executes h passes, preserves all opaque
payload bits, and restores key orientation, buckets, control bits and heads.

Every canonical switch layer is an involution. Reversing their order yields
the inverse permutation. This isolated leaf leaves its left source child
unchanged; the actual inverse numerical lease therefore supplies the same
offset. Source staging and commit retain #7352's order: stage while the lease
is live, retire the numerical lease, then commit the source. The full original
physical source, payload and key encodings return after both directions.

This is a row-control correctness argument under the displayed interfaces,
plus actual finite source joins. It is not emitted binary control for the
entire balanced source iterator or a new all-node CRT implementation.

## 6. Full workload bill and fair ROM comparison

Set N=2^h, R=2h-1 and Q=NR. The source fixture's geometry comes from its
physical records. Let C_source(dir) be the retained complete source/lease/
staging/retirement bill, including every skipped lease. Let L be the actual
source extent. Real source/payload/window acquisition, placement and any
additional transport contribute A_acquire, not zero.

Header construction uses O(L+hp+p) symbol actions: every source record and
precision digit is read, and each of h height increments scans p bits.
Row-counter construction, updates and zeroing use O(Qp+Nhp) symbol actions.
Physical index/key scans and adapter retirement contribute O(N(h+1)+p+h).
The complete point graph executes Q times. The retained h-pass literal
radix theorem supplies

`T_radix <= h * (7740*(N*(12h+8)+10)+144)`.

The accounted workload consists of A_acquire, C_source(dir), all these
symbol-action terms, Q complete point invocations, the h-pass bit consumer,
and any actual continuation. There is no unpriced ROM, row oracle, source
lookup, key serialization, payload copy, output disposal or head return.
These components retain their own execution models. A common literal tariff
for the outer controller and source producer remains open.

The original #7388 baseline was freshly executed from its exact retained
files in both directions. Its complete receipts equal its published
RESULT.json byte-for-value. For its exact h=2,p=5 four-tag workload:

| Cost component | Old forward | New forward | Old inverse | New inverse |
|---|---:|---:|---:|---:|
|Encoded source/numerical symbol actions|113295|113295|372489|372489|
|Outer adapter symbol actions|3481|1294|3817|1602|
|Owned ROM producer instructions|2363816|0|2363816|0|
|Complete direct point instructions|0|21910|0|21910|
|Payload adapter bit actions|1694|1694|1694|1694|
|Literal radix instructions|43162|43162|43162|43162|

The new point count includes 14898 inherited B4 instructions and 7012 new
adapter instructions, over twelve invocations. Its read/write/move actions
are subtracted from outer adapter actions to avoid double counting. They
are not added again to its complete instruction count. Old row scans stay
in the original outer category. This is a complete measured vector on the
common boundary, not a sum of incompatible tariffs or a multiplication gain.

The retained ROM proof bounds one offset by
`10^6 p^2 * 2*(N+1)^3*(h+1)^4`, before caller row scans and final disposal.
Its produced table can be retained and reused when a later caller proves
the corresponding lifetime. Direct queries repeat work. Comparing upper
bounds establishes no all-workload gain, and no unproved number of ROM
reuses is assumed. The result here is the actual source/consumer connection
and its full local costs.

Each direction acquires 100 actual symbol owners: the retained 79 numerical
roles and 21 adapter roles, including fourteen point work tapes. Forward
and inverse symbol histories are 873 and 1253 cells. Both fresh inventories
stay retained: 200 owners and 2126 cells, plus the common 57-cell source.
Payload extent remains 183 bits. Each direction retains its 208-bit bucket
extent and 144-bit radix-register inventory. The inherited radix driver
keeps separate emulator register inventories for its two passes; those are
charged rather than silently identified. Erased bucket cells keep their
historical extents. No source or payload backing object is replaced.

## 7. Executed evidence and negative controls

The primary verifier checks all 1566 canonical network entries through h=3
against the original deterministic Beneš compiler, all 544 offset/address
entries for h=5,s=17,j=6, and a 2049-bit padded-precision case with earlier
blank histories retained. Every point checks the mathematical answer,
physical target, full borrowed bytes/heads, private retirement, exact new
instruction identity, historical envelope and write roles.

Five actual source/payload round trips cover the exact #7388 fixture, a
current-wire-sensitive left-modulus2/right-modulus3 variant, zero offset,
an invalid left coordinate, and a padded right coordinate. The latter still
moves valid payload positions although its padded source coordinate does
not change. Invalidity uses the retained local numerical convention; it is
not promoted to a global identity rule.

The modulus-three variant matters: the original modulus-two involution
does not expose all row-order or stale-wire errors. The negative stale-wire
table reads the original encoded position from an extra test-only role
during input copying, while still consuming at the real mutable address.
It returns cleanly but gives the wrong direct CRT placement. A stale offset
and forward row order during the inverse are also detected. In the latter
case source coordinates return correctly while the physical payload does
not, so source-only restoration would be insufficient.

Point controls cover bad modulus/offset/row values, one bounded height/width
disagreement, wrong source/target heads, a dirty private origin, owner alias
and an output-consumption mutation. Suppressing a true Boolean returns with
cleanup but fails the oracle. Aliasing is rejected at the explicit binding
check, not an invented in-machine address-identity instruction. Malformed
cases outside the theorem have no universal failure cleanup/resource claim.

Unit modulus is valid for the point theorem but the retained source rejects
it with `CRT modulus exceeds one`. This source admission control is recorded
instead of claiming unavailable caller coverage. Exact pins and receipts
are retained. Normal and optimized executions are registered separately.

## 8. Remaining obligations and attribution

The caller still supplies its encoded source, physical payload frame, private
grants and geometry admission. Common literal lowering and a complete tariff
for the balanced source controller, all right-axis fibers and target order,
full CRT composition, stock allocation and the outer multiplication recurrence
remain open. #7390's two-target path was inspected but is not included here.
No selected supplier, certificate or kappa is changed; none of the five
foundational assumptions is declared discharged.

Credit @CubeJerry, Nick Petalas #7504, the literal B4 predicate and independent
review, CubeJerry #7388/#7352 for the source/payload lineage, Ali Romman #5625
for fixtures/lifecycle, and JoyboyBrian's encoded numerical, ROM, key and
radix packages, including #5092, #5496 and #5015. Source notices and Apache
license are retained. The new work is the literal representation/consumption
adapter, exact costs and actual current caller substitution. Substantial
OpenAI assistance was used; model-assisted checks are not human review or
proof-kernel acceptance.
