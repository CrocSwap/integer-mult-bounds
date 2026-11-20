# Independent review: literal CRT Word lifecycle

## Verdict and scope

**No blocking flaw found in the admitted successful-trace theorem.** The
ownership invariant, ordered LIFO stack behavior, erase-before-release order,
per-role historical-capacity account, and all eight displayed instruction
formulas agree with the generated program.

This review covers the concrete ZERO/COPY/FREE/IS_LIVE and TAKE/INIT/CLOSE
metadata seam. It does not establish CRT arithmetic correctness, the source's
32-live-word theorem, a full #7596 arithmetic join, the changing-Entry wrapper,
or the higher controller. It makes no kappa claim.

The candidate is research/literal-crt-word-lifecycle, on canonical
scientific base e54523517d0f03e58352e647c403a5af3e525a57. Its retained immediate
source is #7596 at ee6005fe241ab947e511fe9f6d86f5f4fa58478b.
READ-INPUTS.json records the reviewed bytes. The candidate compiler SHA-256 is
c276f6fcd7c431d3e5b777ae892a16f4b511192bfe13792cd2cdd72e80331b34.
The emitted 130,936-location graph SHA-256 is
48863284a4af10cdbb4d16cbecba07dfbadabc57ee8d21f635181acc7e0d0d73.

The checks import the candidate compiler as the object being reviewed, but do
not import its verifier or hardware interpreter. The reservation check imports
the candidate adapter against a separate port shim and the independent
interpreter. No giant predecessor graph is copied or executed.

## Independent ownership derivation

Let F be the ordered sequence of six-bit records on the stack, read bottom to
top. Its elements are distinct members of O={8,...,63}. At an ordinary
admitted boundary, the live set is exactly {0,...,63} minus set(F). Each free
owner has its original physical identity, L at cell 0, a blank suffix
throughout its supplied history, and head 1. A completed live word has exactly
P bits and terminal R at P+1, with P>=4.

After TAKE, a reserved blank owner is live but is not yet a completed word.
COPY and FREE require completed words; the promised numerical producer must
establish completion. Membership alone is not a framing or completion predicate.

### Pop

The scan reaches terminal R at 6m+1. The top record occupies cells 6m-5 through
6m. Reading it backward encounters bits 5 through 0, so the finite recurrence
v <- 2v+bit returns exactly its little-endian value. Replacing the first cell
of that record with R and blanking the other six old cells produces F[:-1].
Older records retain their bytes and order.

The popped slot was inactive and owned. It differs from every live input.
Its finite ALLOC_s halt tag therefore names the actual reserved owner; equal
numerical values are irrelevant.

### Membership and push

The equality flag is the conjunction of all six bit comparisons. The source
selector returns after each comparison. A match at record k leaves the stack
head at 6k+1; absence leaves it at 6m+1. The common rewind returns head 0.

Under uniqueness and the complement invariant, absence is exactly liveness.
COPY therefore cannot allocate its own source. Protected codes remain live;
FREE rejects them separately before touching a numerical body.

FREE's absence test leaves the stack at terminal R. The numeric loop then
erases every bit and R and restores head 1. Only after this does the first
stack write occur. At that point the full admitted inactive suffix is blank:
the old tail was blank, and the active prefix has just been erased. Writing
the six source bits forward and a new R appends exactly that owner to F.

The inserted owner was absent, preserving uniqueness. Since an owned live
slot exists at entry, m<=55, so the new terminal marker lies at most at cell
337. The 338-cell grant suffices.

These transition facts prove the ordered stack and owner invariant by
induction over every finite admitted successful trace. Replay corroborates
the transitions; the theorem is not an extrapolation from a finite trace.

### Word bodies and CLOSE

ZERO copies the template's P zeros and R to checked blank output cells.
COPY copies its completed source's P bits and R. The COPY premise must
include the same current P; the routine does not compare source length to
the template. It checks minimum width and terminates at the source R.

Both operations restore participating numerical heads to 1, never write the
source/template, and retire selectors on public success. CLOSE touches only
metadata and erases its exact frame under the fully-free invariant.

CLOSE does not independently revalidate uniqueness or every numerical body;
these are inductive premises. INIT requires the fresh eager-Entry boundary
and cannot discard outstanding words. Failure rollback is not claimed.

## Independent path-cost derivation

A selector decode costs 30: three entry instructions, six groups of three,
and nine exit instructions. A physical numeric read therefore costs 31; a
numeric write or move costs 32. All bit alternatives have equal lengths.

A blank-selector check costs 22. Setting a frame costs 30 plus its public
halt, hence 31. Clearing a frame costs 30. A metadata rewind from cell q costs
3q+1. A numeric word rewind from terminal R costs 64P+95; the template rewind
costs 3P+3.

For m stack records:

- Membership absent costs 43m+3 before rewind.
- Membership found at record k costs 43k+2 before rewind.
- Stack rewind from the end costs 18m+4.
- Pop including output-selector construction and transfer costs 36m+50.

For pop, the scan costs 18m+3; the nonempty test/transfer costs 6; six backward
reads and erasures cost 23; replacement R costs 1; rewind from 6m-5 costs
18m-14; output-selector construction/transfer costs 31. Sum: 36m+50.

| Call | Independent decomposition | Total |
|---|---|---|
| TAKE | 44 + pop + 30 + 30 + 1 | 36m+155 |
| ZERO | TAKE + 98P forward + 67P rewind terms + 262 fixed | 165P+36m+417 |
| COPY | (97m+109) metadata + (287P+476) body + 91 return | 287P+97m+676 |
| FREE | (43m+55) entry + (160P+254) erase/rewind + (18m+100) push/return | 160P+61m+409 |
| IS_LIVE absent | 22+30+(43m+3)+(18m+4)+30+1 | 61m+90 |
| IS_LIVE found | 22+30+(43k+2)+(18k+4)+30+1 | 61k+89 |

ZERO's fixed 262 includes both rewinds' fixed terms; they are not added twice.
COPY's forward loop costs 159 per bit and its rewinds cost 128P+190.
FREE's forward loop costs 96 per bit and its rewind costs 64P+95.

INIT clears lengths 338,8,8. Each clear-and-return of length E costs 3E-2,
so the clears cost 1,056. Stack framing, 336 record bits, rewind from cell 337,
and halt add 1,688, for exactly 2,744.
CLOSE costs 44 selector checks + 3 left-frame actions + 3*336 bit actions +
2 right-frame actions + 337 return moves + halt = 1,395.

Including setters, COPY at m=56 gives the worst service bound 287P+6139.
For P>=4 this is at most 1515(P+1). This compares only the lifecycle component
against its old body-write bill, not the whole retained caller.

Two actual live queries cost 2*(31+61m+90)=122m+242.
Adding zero, one, or two TAKE calls gives 122m+242, 158m+397, and 194m+516.
The second TAKE sees m-1. Equal simple-operation inputs are legal; division
retains its distinct-input premise.

## History and alias cases

Each physical numeric role retains max(H_s,P+2), separately summed by owner.
The template and metadata have corresponding maxima with P+2,338,8.
Renaming logical slots cannot move old physical backing or refund its charge.

The independent chronology gives numerical roles unequal initial histories
and runs complete lifetimes at P=41,4,17,6 without changing backing identity.
After the first expansion the numeric total remains 2,842 through all shorter
lifetimes.

An invalid dirty-tail witness demonstrates the boundary. Put a 1 beyond P+1
in an otherwise inactive owner: ZERO succeeds, and FREE later succeeds, while
that bit survives. This is consistent with the stated premise and refutes
a stronger arbitrary-history-cleaning claim. It is an exclusion witness,
not an admitted positive packet.

Physical disjointness is also a premise. The independent entry check rejects
two roles backed by the same list. The graph does not synthesize disjointness
from numerical values. Equal values on different owners are tested positively,
with all identities and unequal capacities retained.

## Retained backend versus #7596 composition

The registered actual-source replay retains raw Unsigned arithmetic with the
new lifecycle. It does not execute the 1,304,162-location #7596 arithmetic
graph joined to this graph.

The local composition implication is supported: the replaced reservations
require bound live inputs and return zero, one, or two fresh blank owners.
Physical IS_LIVE plus TAKE provide the same identities, blank bodies, input
preservation, and heads.

The independent adapter check forbids inherited reservation functions, uses
the independent interpreter, and exercises both replacement methods at
m in {0,1,2,17,55,56} for all feasible result counts. All 15 successful packets
have the exact invoice. Same-handle simple operands work; aliased division,
inactive inputs, and host free-stack access are rejected.

A materialized joint graph can preserve numeric roles 0..63, reuse two of
the four arithmetic selector roles, and add distinct template/stack roles.
This gives 70 local graph roles. The other arithmetic selectors remain blank
during lifecycle work. Such finite state/role renaming is a compatibility
argument; no joined caller or its full receipt is claimed here.

The adapter does not preserve every diagnostic meter field: allocate updates
allocations but not old peak_live. This is not a numerical or ownership
failure, because the package retains the source live-stock theorem as a
premise. The old meter must not be reused as a new live-stock proof.

## Reproducible evidence

Run from the repository root:

    python3 -I -B research/literal-crt-word-lifecycle/review/check_graph.py
    python3 -I -B research/literal-crt-word-lifecycle/review/check_reservation.py

The complete deterministic domains appear in RESULT.json and
RESERVATION-RESULT.json:

- All generated numeric dispatch instances, 64 selectors each, and all five
  symbols for reads: 15,872 complete macro paths.
- Weighted logical paths at P in {4,5,19,83}, every admissible free-stack
  length, and two explicit stack permutations.
- All 64 liveness handles at every length 0..56 under both permutations.
- Physical COPY at P in {4,33}, all source handles, patterns {0,5,10,15}
  repeated every four bits, with equal values on all live owners.
- Four physical lifetime traces, 96 seeded decisions each followed by full
  retirement; seed 7596; exact final orders and capacities recorded.
- 10,204 successful service packets plus 9,170 setters, totaling 28,926,016
  charged instructions in that ledger. Dispatch tests, INIT/CLOSE, and
  negative controls are additional runs outside that ledger.
- Fifteen reservation packets totaling 67,401 instructions, excluding their
  initialization and preparation.
- Protected/duplicate release, inactive COPY, empty TAKE, physical-alias
  premise, dirty-tail exclusion, wrong-owner return, and a semantically
  harmless extra paid jump that breaks the exact instruction invoice.

These checks support the all-traces derivation but are neither a formal
proof-kernel result nor a substitute for arithmetic, wrapper, stock,
acquisition, and higher-control obligations. All five selected assumptions
remain.


The root additionally reviewed the proof and integrated these checks with
package-relative paths and exact receipt comparisons. These packaging edits
do not alter the candidate graph or the independent arithmetic oracle.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
