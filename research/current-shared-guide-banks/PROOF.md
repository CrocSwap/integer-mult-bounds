# One shared physical ruler for native reset banks

## Statement and boundary

Let N and W be positive integers. Set L = N(2W+3). Let B be a positive
bank count. Each data bank has exactly L payload cells, one left guard and
one right guard. Banks occupy consecutive, disjoint intervals on tape 6.
The reset schedule is fixed before N and W are supplied. Every requested
slot k satisfies 1 <= k < B. Slot 0 can remain parked.

The program has seven tapes and the seven-symbol alphabet of the retained
machine. It uses only local branch, write, unit move, fixed goto, halt and
reject instructions. Tape 0 and tape 1 contain canonical positive binary N
and W, with heads at cell 1. Tapes 2, 3 and 4 have blank owned work windows,
with heads at 0. Tape 5 has an owned window of L+2 cells with arbitrary old
symbols. Tape 6 has the B data banks. Its head and the guide head start at 0.
All cells outside these owned windows are borrowed and remain unchanged.

The program produces one guide, executes every requested INIT or CLEAR,
returns all heads after every service, clears each address counter, and
retires the guide. It preserves both binary inputs, all data guards and
all unselected banks. INIT writes the exact source zero record. CLEAR
writes blank to the selected payload. No guide copy is stored at a data
bank. These claims hold for every admitted N, W and initial data payload.

The guide producer, reset consumer and guide retirement program are exact
copies from PR #7667. Their proof is retained in `guide-source/PROOF.md`.
The binary counter and machine are unchanged current-main inputs from
PR #6719. The new mechanism is the physical ruler traversal and its link
to the complete fixed reset schedule. The source and copy pins are in
`SOURCES.json` and `VENDORED.json`.

## Traversal invariant

At a service boundary, the guide head and data head are at 0. The three
work tapes are blank. The guide is the exact length-L source guide.

The finite control writes the fixed positive slot number k in canonical
binary on tape 4. The retained binary-to-unary program writes k UNIT cells
on tape 3. Tape 2 is its scratch tape. The binary descriptor is part of
the finite program; no host operation supplies a runtime tape address.

For each unary UNIT, the outward loop scans all L+2 guide cells. It moves
the data head once for each cell, including both guide markers. It then
returns the guide head to 0 while the data head remains fixed. After j
iterations, the data head is at j(L+2), the guide head is at 0, and the
unary head is at j+1. Induction gives the left guard of bank k after k
iterations. The counter head then returns to its first UNIT.

The linked source consumer starts at this guard. It uses the guide to
write the selected payload and returns both heads to their starting
positions. Its guide reads do not change the guide. Each reverse ruler
iteration moves the data head left by L+2 and returns the guide head to
0. After k iterations the data head is at 0. The counter erasers then
clear all binary and unary cells, both boundaries, and the scratch left
marker. All work heads return to 0.

Every data move lies between 0 and the selected bank's right guard. The
selector never reads data symbols, so parked contents cannot change its
path. Only the consumer writes data. Its write positions are exactly the
selected payload. Thus arbitrary parked values, all guards and the
borrowed exterior remain unchanged. The complete emitted service blocks
contain no guide write instruction. This proves guide preservation at
every instruction, as well as at service boundaries.

The linker resolves every finite control destination before execution.
It replaces an internal HALT with one fixed GOTO. Both cost one
instruction. Its final retirement retains HALT. No runtime callback,
array lookup or host address operation is available to the program.

## Exact instruction bill

Write ell(x) = bitlength(x) and pop(x) = popcount(x). The retained counter
has the exact cost

```text
c(x) = 24x - 7pop(x) + 15ell(x) + 12.
```

A single ruler crossing costs 7L+10 instructions. The unary control adds
three instructions per crossing. The final counter return costs 3k+4.
Thus one traversal of k banks costs k(7L+16)+4.

The fixed binary descriptor write and return cost 5ell(k)+6. The two work
markers cost 4. Counter conversion costs c(k). The unary eraser costs
7k+8. The binary descriptor eraser costs 7ell(k)+8. The scratch marker
retirement costs 2. Both traversals and the source reset cost are included
in the resulting service bill:

```text
T_service(k,L) = (14k+9)L + c(k) + 39k + 12ell(k) + 47.
T_produce(N,W) = c(N) + c(W) + 22NW + 36N + 7W + 36.
T_retire(L) = 7L+10.
T_total = T_produce + sum_over_services(T_service) + T_retire.
```

These are physical microinstruction counts. Control construction and
loading have a separate positive finite charge. The stored table has
fixed size, reported in `RESULT.json`, independent of N and W. Input
production, data-array allocation and numerical child work are not part
of this reset theorem. Their costs remain obligations; they are not zero.

## Complete retained capacity

Let K be the largest requested slot. Define ellN, ellW and ellK as the
three bit lengths. The required owned spans on tapes 0 through 6 are:

```text
ellN+2
ellW+2
max(ellN,ellW,ellK)+2
max(N,K)+2
max(W,ellK)+2
L+2
B(L+2)
```

The maxima retain work used by guide production and by every later
address counter. All B data banks remain charged, including banks that
the current service does not visit. Their total is

```text
(B+1)(L+2) + ellN + ellW + max(ellN,ellW,ellK)
            + max(N,K) + max(W,ellK) + 10.
```

If a tape has an older retained span H_i, charge max(H_i,s_i) for that
tape. This theorem does not release backing storage or clear arbitrary
old work outside the admitted windows.

## Current source instance and comparison

The pinned PR #7663 word has SHA256
`f95eabd1734c7a74f58428cb12f261a81032bef01aed78c8147a4e4f90636939`.
Its literal native plan has 234 child lifetimes. Retain 234 parent banks
and 234 child banks. Child ordinal j uses slot 234+j. Each child has one
INIT and one CLEAR. Sort these 468 events by their source clocks. An
independent reverse scan checks the complete lifetime census.

The sum of all service costs is exactly

```text
2300688L + 10458512.
```

Add guide production and retirement from the preceding formulas. This
bill is larger than the two-head local selection bill in PR #7666. The
shared guide trades travel for storage. No speed gain is claimed.

For N=W=1, L=5 and B=468, retained capacity is 3780 cells. The preceding
pair of complete guide/data arrays has 6552 cells. For N=512 and W=1,
L=2560, retained capacity is 1202130 cells, versus 2398032 cells for those
two arrays. The removed guide copies contribute 1196454 cells; the new
control spans add 552 cells. The net difference is 1195902 cells. This
comparison uses the same finite cell representation. It is not a change
to a global bit tariff or a complete multiplication bound.

The 468-event execution uses N=W=1. A second execution uses the complete
N=512 view and the last child bank. Both have an independent dense
execution of the emitted instructions. Six additional shapes check
counter and record boundaries. Fault controls alter actual instructions
for slot stride, travel direction, guide writes, return and cleanup.
Finite executions support the stated invariants; the induction above
supplies the all-size argument.

## Composition limit

The retained plan belongs to one RAW native word. It is not the full
compiled parent/child inventory. Numerical operations between reset
services must preserve the guide and all parked banks, restore the data
head to the agreed boundary, and return the work tapes blank. This
package does not implement those operations or charge their runtime.
Root descriptors, native adapters, cross-depth ownership, old work,
common whole-algorithm pricing and outer recovery remain open. The five
selected assumptions remain. No new kappa is claimed.
