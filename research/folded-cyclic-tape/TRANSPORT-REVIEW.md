# Independent review of the folded physical caller

Prepared for @CubeJerry with substantial OpenAI assistance by a separate
source-aware verifier. Apache-2.0. This is supporting verification for the
integrated folded caller, not a separate result or a kernel proof.

## Claim boundary

The folded-order bandwidth lemma is inherited from
CrocSwap/integer-mult-bounds#4879, and the physical banded solver and exact
word arithmetic are inherited from CrocSwap/integer-mult-bounds#3851 and
CrocSwap/integer-mult-bounds#3787. The new caller physically folds original
right-hand sides, calls that unchanged solver on already prepared folded
factor banks, and unfolds the protected return. It supports several
right-hand sides without an unpriced transpose or host permutation of
payloads. Neither a new folding lemma nor a complete periodic Gaussian
inverse is claimed by this interface alone.

The numerical validity of a particular folded factor bank is a separate
preparation proposition. This review checks the transport, composition,
ownership and complete movement invoice. Its exact diagonal fixtures do
not substitute for the independent Reference/Schur numerical checks.

## Universal transport argument

For n>=1 let pi(2j)=j and pi(2j+1)=n-1-j. The map enumerates each
original row exactly once. The physical fold first makes a complete
record reversal. Alternately consuming the next record of the original
and reversed tapes then emits pi in order. The original prefix has
ceil(n/2) records; the reversed prefix has floor(n/2). Their corresponding
original index sets are disjoint and exhaust the interval, including odd
n and n=1.

Unfold splits even and odd returned positions into two sequential tapes.
The first is the original ascending left half; the second is the
descending right half. Reversing the second and concatenating both
restores original order. In the singleton case the second half is empty;
the inherited reverse_records accepts the encoded zero length and
performs no payload move. No signed word is decoded or rounded by these
permutations.

Consequently the complete numerical operation is exactly
P^-1 * ChildSolve(P*x), with the child already supplied the factors for
P*A*P^-1. Permutation preserves the input infinity norm and adds zero
rounding error. The approximate child is not assumed linear; the formula
describes its actual rounded execution in a different record order.

The right-hand-side input head advances monotonically from one complete
n-record line to the next. The output head remains at its append frontier
between unfolded lines. Each line's six transport buffers and entire
child return are cleared before reuse. Thus r lines produce exactly rn
original-order output records, rather than overwriting or interleaving
earlier answers.

## Ownership and failure behavior

The wrapper has a finite pending flag independent of where the caller
moves the returned head. A new call is rejected while that flag is set,
even when the returned head stands on the trailing BLANK. `consume`
physically clears the complete protected body, erases its marker and
clears the flag. Double consumption rejects.

Borrowed origin tests must use physical delimiter inspection. The first
draft consulted the backend head integer; this was corrected to a paid
left move, LEFT read and right move. The fixed structural identity test
for external/distinct physical ports does not inspect numerical data.
The erased owned output origin instead follows from the closed/pending
ownership invariant and physical cleanup. No unmetered address value is
needed to control the actual computation.

The owner-role inventory must include the inherited word engine's
inactive descendants as well as its direct pool, output and canonical
tapes. The reviewer identified the missing descendant pools in the first
inventory and requested their inclusion in both alias admission and
retained-erasure checks. The expanded inventory is used by the final integrating replay.

If a later RHS is short, the already produced prefix is erased on failure.
If the child rejects a zero reciprocal, its own cleanup restores its
state and the parent clears its line buffers. A child return that has
already succeeded is separately tracked until fully unfolded and erased.
These paths preserve every borrowed body and restore its origin head.
The parent factory scope is suspended around the child call, as required
by the inherited ownership interface; this prevents child entry work
from acquiring parent scratch roles. The numerical reviewer identified
that separation requirement and it was incorporated before final replay.

## Complete time and retained-space invoice

Write r for the number of RHSs, n for the line length, b>=1 for the
supplied scalar half-bandwidth and W for signed record width. The fold,
unfold, parent line copies, reversals, input/output rewinds and all
transport/child-return erasures cost O(rnW) tape work. A tape reversal
first scans its complete extent and then uses local backward moves per
record; it does not seek from the origin for each output record.

The unchanged child reads both factor banks on every RHS. Its forward
and backward dot products use 2rnb scalar products of width W. Its
reciprocal products use rn products with width

    Wwide = 2W + ceil(log2(b+1)) + 2.

The bounded row windows and factor-bank traversal additionally cost
O(rn(b+1)W). Hence a complete generic online bound is

    O(rn [b*M(W) + M(W+log(b+1)) + (b+1)W]),

including the protected-return consumption, where M includes all
inherited word setup, numerical recovery and cleanup. One may simplify
to O(rn(b+1)M(W)) when the coefficient plan explicitly ensures
W>=ceil(log2(b+1)). An assertion of that simpler bound for arbitrary
descriptors would omit the child's wide reciprocal carrier.

The parent buffers require O(nW), the child buffers O((n+b)W), and the
word child O(W+log(b+1)) retained cells. The protected multi-RHS return
requires O(rnW). Add the borrowed factor banks O(n(b+1)W) and input
O(rnW) when describing the entire call. Retained blank backing is counted;
reusing an owner does not deallocate its historical maximum extents.
Erasure scans the present dense live prefix rather than that blank tail,
as established in the independent literal-runtime cleanup audit.

Coefficient/factor preparation is separate from this online invoice.
No claim of constant-price scalar multiplication or free source access
is used by this transport proof.

## Executed independent checks

`independent_physical.py` constructs diagonal original-order systems with
d_i=2^(i mod 3), prepares their exact dyadic folded factor pages, and
feeds distinct mixed-sign RHSs to the actual unchanged BandedSolve.
The independent expected relation is simply d_i*y_i=x_i in original
order. It does not call the author's folding function or stage oracle
to compute expected answers.

The eight calls have lengths 1,2,3,4,5,8,9,1 and respectively
3,2,2,3,2,2,3,1 RHSs. All 79 output records satisfy their exact original
equations. There are 237 successful actual scalar products, all in the
inherited finite base branch. The sequence ends in a small call after
larger retained buffers. Every borrowed body/head is preserved, and
every role in the supplied ownership inventory is blank at its origin
after consumption.

Controls check aliased descriptors, a displaced borrowed input head,
pending output with its head on BLANK, double consumption, a short later
RHS, a child failure on a zero reciprocal, and aliases to an inactive
twiddle descendant as either a payload or Count port. Normal and optimized
isolated Python runs pass. A static source check rejects direct
head/cells/meter attribute access in the new control source; this is a
scoped source check, not a runtime enforcement claim about all inherited
modules. Test observations of backend bytes and heads occur outside the
production calls.

The script is portable when retained beside folded_consumer.py. While
stored in this separate reviewer directory, pass the target package path
as its single argument. The JSON receipts record the actual source hash;
normal and optimized receipts for one source version agree except for
elapsed wall time. The updated descendant/suspended-scope version received
a targeted normal replay before integration; the current package registers
normal and optimized replay of that complete version.
