# Literal allocation and retirement for the current CRT Word inventory

## Claim, source and boundary

The scientific base is canonical `CrocSwap/integer-mult-bounds` commit
`e54523517d0f03e58352e647c403a5af3e525a57`. The immediate source interface is
[CrocSwap/integer-mult-bounds#7596](https://github.com/CrocSwap/integer-mult-bounds/pull/7596)
at `CubeJerry/integer-mult-bounds` commit
`ee6005fe241ab947e511fe9f6d86f5f4fa58478b`. Its exact retained `Word` implementation,
current producer, eager Entry and arithmetic binder are vendored without edits
under `inputs/`; `SOURCES.json` gives the original paths and hashes.

The original current producer is JoyboyBrian's
[CrocSwap/integer-mult-bounds#5053](https://github.com/CrocSwap/integer-mult-bounds/pull/5053).
The entry and persistent ownership lineage includes
[#5219](https://github.com/CrocSwap/integer-mult-bounds/pull/5219),
[#5353](https://github.com/CrocSwap/integer-mult-bounds/pull/5353) and
[#5505](https://github.com/CrocSwap/integer-mult-bounds/pull/5505).
The arithmetic provider and its numerical admission are credited premises.
This package does not reprove CRT numerical correctness or its 32-live-word bound.

**Theorem (one eager current Entry).** For every positive precision `P >= 4`,
the fixed program emitted by `lifecycle.py` implements the exact LIFO reserve,
zero allocation, live-word copy, successful owned-word erase/release, and live
membership interfaces described below. It uses a fixed finite alphabet and
130,936 fixed `R/W/M/J/H` locations on 68 fixed physical roles, independently
of `P`, numerical values, trace length and incoming historical capacities.
It preserves protected owners and the template, restores every successful
working head, retires both selectors, and retains every physical role's actual
historical backing. Its exact instruction counts are in §5.

Consequently these services can replace the supplied Word lifecycle and
reservation methods at the exact #7596 per-Entry boundary. This is a local
service substitution. The current numerical source, higher control, entry
production, physical bank grants and numerical admission remain premises.
The registered actual-source replay uses retained raw `Unsigned` arithmetic
with the new lifecycle. It does **not** execute the entire 1,304,162-location
#7596 arithmetic graph joined to this graph; that join is justified by matching
the two reservation contracts, not presented as an executed full caller.

No selected certificate changes. All five foundational assumptions remain.
There is no complete multiplication theorem or new kappa in this package.

## 1. Fixed physical representation

There are 64 numerical roles, numbered 0 through 63. Roles 0 through 7 are
protected. The current Entry supplies 56 owned roles, numbered 8 through 63,
and one separate template. Every numerical role keeps its actual physical
identity throughout the lifetime. Equal values do not merge owners.

A completed `P`-bit Word has `L` at cell 0, binary digits at cells 1 through
`P`, `R` at cell `P+1`, and head at 1. The template has the same framing and
all-zero digits. An inactive owned Word has `L` at cell 0 and blank cells
1 through its complete historical end, with head 1. The Entry has already
provided the backed interval through `P+1`. No graph instruction allocates
a physical Word, extends an input-sized alphabet, decodes `P`, or jumps to
a computed tape position.

Protected guard contents can be arbitrary and are never erased. A protected
Word used as a COPY operand must separately satisfy the completed-Word input
contract. The exact current producer treats its eight arbitrary dirty guards
as protected, unused guards, so no binary-body premise is added to them.

The free stack is one additional physical tape. A live stack is

```
L  [six bits of bottom slot] ... [six bits of top slot]  R  blank ...
```

Slot codes are little-endian. Its entries are distinct elements of
`{8,...,63}`. At a boundary its head is 0, and cells after its terminal `R`
are blank throughout the 338-cell grant. The live numerical slots are
exactly the complement of the stack. Thus all protected slots are live.
There is no second host live set or host free stack in the graph.

Two separate eight-cell selectors encode `L`, six little-endian slot bits,
and `R`. They are blank at successful public boundaries and have head 0.
The source selector is populated by a paid fixed setter before COPY, FREE
or IS_LIVE. Output reservation populates the output selector internally.
No two selector owners alias, even if their encoded values happen to agree.

The local numbering is 0..63 numerical, 64 template, 65 stack, and 66/67
selectors. For the #7596 arithmetic union, preserve numerical roles 0..63,
map the lifecycle selectors to two of that graph's four existing selector
roles, and place the template and new stack on distinct additional roles.
The union has 70 roles, including the already existing Entry template.
The other arithmetic selectors stay blank and untouched during lifecycle
work. This is a compatible physical renaming, not permission to overlap
two simultaneously live tapes.

`INIT` is used only at the original eager Entry boundary: guards 0..7 live,
all 56 owned Words inactive, and the template supplied. It initializes the
stack to `(63,62,...,8)`, whose top is 8, exactly matching the Entry's
`list(reversed(range(8,64)))`. It clears the three fixed metadata grants
with paid writes. Arbitrary dirty acquisition or restoration of borrowed
metadata is not claimed: these grants are owned workspace. INIT must not
be used to discard outstanding numerical outputs.

## 2. Stack and ownership invariants

### Exact pop

The pop routine scans from `L` to the stack's terminal `R`, using unit
moves. An empty stack has `L R`; TAKE returns EXHAUSTED before changing it.
For a nonempty stack, it erases the old `R` and reads the top record backward.
The six decoded bits are retained in one of 64 finite control alternatives.
Each visited bit is erased. The routine writes a new `R` at the former first
bit of the removed record, returns to `L`, and writes the returned slot into
the output selector through fixed states.

Backward reading encounters bits 5,4,...,0. After `j` reads the finite
state stores the corresponding `j`-bit prefix of the numerical slot code;
the transition `v -> 2v+bit` is compiled into the finite graph. It is not
runtime wide arithmetic. The final state names exactly the former top slot.
Under the stack invariant that slot is owned, inactive, distinct from all
live operands, and has a blank body. Pop removes just that final record,
preserving the order and bytes of every earlier record.

TAKE returns the finite halt tag `ALLOC_s` with that physical owner still
blank. This is the reservation interface needed by the existing arithmetic
graph, which itself writes all result digits and `R`. The temporarily
reserved owner is live but not yet a completed Word. It cannot be passed to
COPY or FREE until its promised numerical producer has completed it. The
arithmetic contract already requires that completion before returning.

### Physical membership

The membership routine compares every six-bit stack record with the source
selector, retaining only the one-bit prefix-equality flag. It restores the
selector after each comparison. It returns FREE on the first matching record,
or LIVE when it reaches the terminal `R` without a match. Uniqueness of stack
entries and the complement convention prove the result. It scans physical
bits; its answer does not come from a Python set or from an encoded value
passed to the executor.

COPY requires LIVE. FREE first rejects the eight protected codes, then
requires LIVE. Consequently COPY's newly popped output cannot alias its
input, and FREE cannot release a guard or an already-free owner.
These facts are independent of the numerical values held in the Words.

### Exact push after erasure

For FREE, membership leaves the stack head at its terminal `R`. After the
body erasure proved below, the routine overwrites that marker with the six
source-selector bits in order, writes a new terminal `R`, restores the stack
head, and erases the selector. Thus the just-freed slot becomes exactly the
new top. Because that owned slot was live, at most 55 entries preceded it;
the new terminal marker lies within the 338-cell grant. The slot was absent
before insertion, so uniqueness and the complement invariant persist.

By induction over any finite successful trace, the graph therefore represents
the same ordered free stack and live partition as the corresponding abstract
LIFO reserve/release trace. This is an all-traces invariant, not an extrapolation
of the tested 360-operation example.

## 3. Word bodies and selectors

ZERO pops an inactive owner and traverses the retained zero template and
that owner together. Before each digit write it checks that the destination
cell is blank. It copies a zero, moves both heads once, and eventually copies
the template's terminal `R` into a checked blank. Five finite progress states
distinguish 0,1,2,3 and at least 4 digits, so termination at `R` requires the
admitted minimum width. Both heads return by scanning left to `L`, then moving
once to cell 1. The result is exactly a completed zero Word on the popped owner.

COPY performs the same sequential traversal using a live source Word. Each
source bit is kept only in the two finite bit alternatives before being
written to the checked blank output cell. Because both source and template
belong to the admitted current precision, source and output have `P` digits.
The source is never written. Its `R` determines the output extent; there is no
runtime integer-width argument. The source and output heads both return to 1.

FREE checks the source's `L` guard and scans its complete binary body. Each
digit, and finally `R`, is overwritten with blank. Only after that numerical
erasure does the routine push the owner onto the free stack. It then returns
the numerical head to 1 and retires the source selector. In particular there
is no interval in a successful operation during which a still-dirty body is
advertised as available for a subsequent call.

Each selector retirement reads and erases its `L`, six bits and `R`, then
returns its head to 0. Returned `ALLOC_s` tags are fixed halt states. A source
adapter may use them to select the already-existing object representing
physical role `s`; that selection does not allocate a new tape or decode an
input-sized integer.

All other numerical owners are untouched. The template is read-only. Every
numeric access is within `[0,P+1]`; no active-body operation touches an older
tail. FREE returns the complete owned history to blank except for its retained
`L` marker because the initial inactive tail was blank, the numerical and
lifecycle providers never write outside the current extent, and erasure clears
every active body cell. If an external party supplied a dirty older tail, this
full-history blankness conclusion would not follow: arbitrary dirty tails are
outside the inactive-owner contract. They cannot be silently erased or credited
as free storage.

### Metadata retirement

CLOSE requires no outstanding owned numerical Word. Under the invariant,
the stack then has all 56 owned slots exactly once, in its actual current order.
CLOSE validates and erases `L`, exactly 336 bit cells, and `R`, and returns its
head to 0. Both selectors must already be blank. Thus all new metadata bodies
are blank. It does not erase numerical `L` markers or retire the template;
the original Entry.close performs those existing paid actions. Metadata
retirement and numerical owner retirement are separate, both charged services.

Malformed entries may halt after partial work, and neither the graph theorem
nor the source adapter promises failure rollback. The semantic rejection
controls are not a universal malformed-input cleanup theorem.

## 4. Source substitution and the #7596 seam

The retained `Arena.zero`, `Arena.copy`, `Arena.free` methods have exactly the
success effects established above. `Arena.literal` writes a compiled constant
after calling zero, and `free_many` calls free on its supplied finite argument
list. Neither needs a new allocation mechanism. The current producer uses
`arena.live` only for finite protected/retirement control; it never directly
reads `arena.available`.

`source_binding.Owner` installs the three new methods on that same Arena
object, keeping all original Word and backing identities. Its `.live` view
obtains membership through actual paid IS_LIVE runs. Iteration ranges over
the fixed 64 handle codes and issues those queries; it does not inspect the
physical stack through a host decoder. Host `.available` access raises an
error. The higher numerical source and its finite loop/return control remain
retained; they have not been compiled by this adapter.

For a successful admitted source trace, induction at each lifecycle call
therefore gives the same numerical values, complete Word framing and returned
source semantics. The guards remain live. The source's credited live-stock
bound supplies enough inactive owners, so the new allocations cannot introduce
an exhaustion absent from the abstract admitted run. Direct record and raw
arithmetic operations are unchanged in this substitution theorem.

Source finally blocks enumerate a finite live set and free disjoint owners.
Their order can change the ordered free stack. The proof compares the actual
request order, or uses the weak slot bijection already proved in #7596 when
comparing a different set-enumeration order. That bijection is a proof relation
between numerical owner names. It does not permute physical histories or
transport old backing for free. Histories are always charged to actual roles.

The exact #7596 `reserve_simple` returns no owner for comparison, and pops
one owner for ADD/SUBTRACT. Its inherited `reserve` pops two distinct owners
for division, with distinct live inputs. `arithmetic_binding` overrides just
these two methods: it obtains both operand live tests physically, then issues
zero, one or two TAKE calls. The resulting output handles, complete blank
output bodies and unchanged input heads satisfy the unchanged arithmetic graph's
entry contract. Equal input handles remain legal for simple operations, including
the current source's aliased doubling. Two-output division retains its distinct
input requirement. No new alias is introduced by allocation.

This establishes the local composition implication. It does not provide a
complete iterator wrapper that attaches/retires the service across every changing
Entry, nor does the present replay materialize the full combined arithmetic
program. The source adapter's finite object-to-role checks are typed-interface
checks; the universal machine statement starts from fixed distinct physical
roles. General acquisition, wrapper production and higher controller lowering
remain separate obligations.

## 5. Exact instructions and full local invoice

Count every emitted instruction, including reads, writes, unit moves, jumps,
finite control, head returns and halt. Let `m` be the number of free records
at the call entrance, and `k` the one-based position of a found record from
the bottom. Source setters are separate paid calls of exactly 31 instructions.

| Entry | Exact successful instruction count | Domain |
|---|---:|---|
| INIT | 2,744 | Fresh eager Entry; three metadata grants |
| TAKE | `36m+155` | `1 <= m <= 56` |
| ZERO | `165P+36m+417` | `1 <= m <= 56`, `P >= 4` |
| COPY | `287P+97m+676` | Live completed source; `1 <= m <= 56` |
| FREE | `160P+61m+409` | Live owned completed source; `0 <= m <= 55` |
| IS_LIVE, absent from stack | `61m+90` | `0 <= m <= 56` |
| IS_LIVE, found in stack | `61k+89` | `1 <= k <= m <= 56` |
| CLOSE | 1,395 | All 56 owned roles inactive |

Here is a direct derivation rather than a fit to execution measurements.
The six-bit decoder costs 30 instructions. A dispatched numeric read costs
31; a dispatched write or move costs 32. Clearing a selector costs 30, and
checking one inactive selector costs 22. A stack rewind from cell `6m+1`
costs `18m+4`. A complete membership scan with no match costs `43m+3` before
rewind and retirement; a match at record `k` costs `43k+2`.

Pop including its output-selector construction costs `36m+50`. TAKE adds
two inactive-selector checks (44), output decode/retirement (60), and halt (1),
giving its table entry. ZERO adds a body of `165P+262` relative to TAKE:
the forward traversal costs `98P`; both rewinds cost `67P+98`; guards,
initial/final tests and jumps contribute the remaining fixed terms.

COPY's fixed metadata path is `97m+109`. Its body, including both guards,
both complete rewinds and the transfer to return, costs `287P+476`:
`159P` in the forward digit loop and `128P` in the two numeric rewinds.
The two-selector return costs 91, giving the displayed COPY total.

FREE's entry and membership cost `43m+55`. Its guard/digit/rewind work costs
`160P+254`: the forward digit loop costs `96P`, and rewind costs `64P+95`.
The push, stack return, selector retirement and halt cost `18m+100`.
These sums give its exact count. The liveness counts follow by adding its
inactive selector check, initial decode, membership, stack rewind and source
retirement. INIT and CLOSE are fixed unrolled scans with the stated totals.

These counts depend on data only through which legal finite branch is taken;
the relevant equal/unequal and zero/one branches have equal instruction lengths.
They therefore hold for every admitted `P`, every legal stack permutation,
and every numerical content. The bounded verifier corroborates the formulas
through `P=257`, all free-stack lengths and every handle; it is not their proof.

Including the source setter where needed, every individual successful local
service costs at most `287P+6139` for `P>=4`. This is an explicit full local
bound, not a bound on the source producer, its physical acquisition, or its
other primitives. For a trace, sum each actual call at its actual precision.
INIT and CLOSE are charged once per actual metadata lifetime, not once per
mathematical object whose name happens to be reused.

For a #7596 reservation with `m` free slots, two paid live queries cost
`122m+242`. Adding zero, one or two TAKE calls gives respectively

```
comparison reservation: 122m + 242 <= 7074,
one-result reservation: 158m + 397 <= 9245,
two-result reservation: 194m + 516 <= 11380.
```

The second TAKE sees `m-1`. Existing arithmetic setters, arithmetic instructions,
scope/return control and source iteration remain additional. The old binder's
coarse metadata receipt should not be treated as the exact new receipt.

For the Word services, the old successful zero/copy/free action bill contains
at least `P+1` body writes. Thus each replacement has cost at most
`1515` times those old lifecycle symbol actions when `P>=4`, using
`287P+6139 <= 1515(P+1)`. This constant simulation can preserve the existing
source-polynomial exponent for that component. It does not turn every remaining
source service into literal instructions, supply an accelerated recursive tariff,
or improve a multiplication exponent. Paid finite live queries and reserve
calls must still be added at their actual source call counts.

## 6. Historical storage and source reuse

Let `H_s` denote the previously retained number of cells of physical numerical
role `s`, including its left marker. A call at precision `P` retains at most
`max(H_s,P+2)` cells on each accessed role; in this eager-entry implementation
that entire required interval is supplied before the call. The same formula
applies to the retained template. The stack and selector contributions are
`max(H_stack,338)` and `max(H_selector,8)` for each selector. The total is
the sum of these **per-role** maxima, plus unchanged external owners. The
maximum of complete standalone totals is not a substitute for this sum.

Within a lifetime, all operations stay inside those intervals and use only
the same owners. Across completed lifetimes of different precision, use the
maximum precision actually assigned to each physical role. Clearing a body
or metadata does not refund history, and a later shorter call cannot reset
the charge. Arbitrarily larger previous backing remains in the bill even
when it is not traversed by a current-body operation.

If the caller requires a full-history sweep or transfer beyond the current
extent, its actual traversal cost remains additional. This package's claim
is preservation of the already-blank inactive tails and exact same-owner
retirement, not a free construction of blank capacity from dirty external stock.

## 7. Verification scope and remaining obligations

The primary suite checks 4,544 primitive packets: four precisions, every
positive free-stack length for TAKE/ZERO/COPY, every allowed free-stack length
for FREE, and every finite handle at every free-stack length for liveness.
Separate chronology uses seed 20261120 for 360 legal COPY/FREE operations on
noninitial stack orders with 2,049 cells retained on each numerical owner.
Exact pinned producer replay covers three current source invocations, including
two left records and two right records in separate cases. Original lifecycle
methods are unavailable during these positive producer/consumer runs. All
borrowed guards, owner identities, heads and historical tails are checked.

Controls reject protected release, duplicate release, copying an inactive owner,
short words/templates, dirty outputs, malformed handles, premature close and
exhaustion. A returning wrong-owner mutation restores every head and selector
but is rejected by the independent owner oracle. `RESULT.json` records exact
domains and instructions; no random search over unreported inputs is claimed.

The independent graph, cost and reservation-seam review is recorded in
REVIEW.md with separately implemented execution checks. The retained
peak_live diagnostic is not updated by this adapter and cannot supply a new
live-stock proof; the original stock theorem remains an explicit premise.
The replay interpreter's counters, watchdog, visited-interval observations,
`Owner.operations` log and inherited allocation meter are erased from the
claimed machine. None chooses an owner, changes a graph branch, supplies a
symbol or guides a head. The source controller remains explicit retained
control; its finite typed-Word lookup selects among 64 pre-existing objects.
No length-growing verifier log is counted as constant-space machine metadata.

The known remaining integration work is the full #7596 arithmetic join,
the changing-Entry attachment and retirement wrapper, higher numerical control,
input/framing acquisition, the original output-record/row/radix interfaces,
and their common physical tariff. All five selected framework assumptions are
retained. AI-assisted finite replay and written review are neither human peer
review nor a formal proof-kernel acceptance.
