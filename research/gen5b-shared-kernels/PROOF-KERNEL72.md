# Shared-donor kernel validation (separate from frozen final12)

## Verified candidate

Pinned source: PR299 commit `5f6bd3fbc0e6796dd31263cef1f06dc968186f64`.
The larger candidate uses the line groups `(6,7)`, `(16,17)`, `(2,3)`, dropping
only pivot relations 10859 and 10861 from the first group. It has 72 pivots,
93 distinct donors,165 helper roles and 473 setup/restore shear pairs.
All three individual groups and both proposed disjoint unions were checked.
No source program was imported or executed.

Every role is plain, not reused, not removed by the sink stage, not a member
of the frozen kernel stage, not an endpoint in the 904 descent changes, and
not touched by final12 and not an old restored endpoint. Any restoration-donor
uses are included in the chronological audit (none occur for these witnesses). All new helper endpoints
remain FULL. Each group uses the common entrance line E=span(e_i-e_j).
Its Gram entry for 9 I-J is 18, so it is nondegenerate over Q and every retained
prime q > 2^80. Exact rational containment checks place E inside every member's
first required frame and check each subsequent old chronological frame step.
The 72-pivot union uses 663 distinct old frame containments.

## Scalar identity on arbitrary independent dirty inputs

This is a compositional proof at the bit F2 interface, not a claim that the
entire parity-filtered decoder is an integer identity. Let Q be the actual
prefix through all initial plain dirty compensation reads, but before source
injections or any new member's other use. Let S be the old remaining word.
The inherited complete decoder is U=SQ: target += source, all source/dirty
coordinates fixed.

Let K=sum e_d e_p^T over every new donor/pivot incidence and A=I+K.
Pivot and donor sets are disjoint, hence K²=0, A^-1=A in F2, and all individual
setup shears commute, even with a donor shared by several pivots.
All new members remain unchanged in Q except for their target compensation
columns. Write R for that response matrix. The independently reconstructed
integer adjoint, reduced modulo 2, verifies R_p=sum_d R_d for each pivot.
If Q' is Q with precisely the pivot compensation reads omitted, this gives
A Q'=Q A. Therefore the proposed complete word is

    A^-1 S A Q' = A^-1 S Q A = A^-1 U A = U.

The final equality holds because U touches only source-to-target entries,
whereas A touches only dirty helper entries. This proves every source,
target and dirty column, in both directions, on arbitrary entry values.
The executable checker compares the corresponding full 18,954-column formal
matrices. Its old remainder is the inherited decoder composed with Q^-1;
it does not pretend to be a new replay of every old physical record.
Omitting a setup or a restoration, or corrupting one response relation,
is rejected by regression controls.

## Literal common prefix

The independent signed-adjoint reconstruction agrees with all 1,720 existing
kernel cut-read triples. The plain odd-read block has 648,088 ADDs; its last
read is `[3503,16719,-1]` at base record 648087. The target-prefix setup cut is
696719, later than this block. Existing kernel setups occur inside this block
and use disjoint helper support. New setups can therefore be inserted at the
structural boundary immediately before the first source injection. Removing
new pivot reads does not require shifting any inherited indexed transform:
apply the new stage after the inherited transforms, using that structural
boundary. All target operations already before this boundary merely read
unmodified helper columns or use disjoint frozen kernel helpers.

The source witness is `kernel-witness.json` in this package; `check_shared_kernel.py` independently derives the
same response and physical-role map. The common cut is semantic (before first
source injection), rather than reusing an invalid post-transformation record
number.

## Paid moves, including donor sharing

Each new pivot starts at E instead of ZERO, so its first old rank-d MOVE is
replaced by rank d-1. Each distinct donor first moves ZERO→E once, performs all
its same-E setup shears, then moves E→its old first frame, rank d-1. A donor
used 21 times still pays that rank 1 entrance exactly once; its 21 scalar ADDs
are all retained and counted. At the end every member is at FULL, so all 473
inverse shears are legal at FULL and require no additional MOVE.
The new setup matrices commute, so either exact reverse ordering or the
source's family ordering is valid; the emitted specification uses reversal.

Measured local delta:

    rank 1:+93, rank 2:+144, rank 3:-144, rank 4:+19, rank 5:-17, rank 6:-2.

Its paid rank mass drops by 72. Residual family demand changes by
`rank 24:-72, rank 23:+72`. Bank assignment and exact pricing are separate
certificates; the path checker does not infer them from volume alone.

## Conservative scalar prefix bound

`check_scalar_bounds.py` independently replays all source/helper updates in
both directions, including the final12 suffix and all frozen kernel shears.
All 14 terminal-sink writes are redirected to their actual target pivots;
removed sink reads, deliveries and cleanup updates are absent. At each extra
shear it uses the actual previously propagated
nonnegative row weight, not a unit-cost scalar approximation.

For an upper bound, it restores every omitted target-compression read and
every newly removed pivot compensation read. It includes the two target-prefix
batches AND the seven sink setup/restore batches. Their combined directed
source-to-destination target graph has 681 edges and 908 vertices and is checked
acyclic. Each edge has weight equal to its total number of ADD occurrences,
two per setup/restore pair. Applying those weighted edges in topological order
to all accumulated nonnegative target increments dominates any chronological
placement of those ADDs: it counts every directed path with the product of
its edge multiplicities, including mixed prefix-to-sink paths. This proof works
in both execution directions. Target values never feed sources or helpers.
The monotonicity of every cancellation-free ADD majorant also bounds all
intermediate values, not only the final vectors.

Old and new uncompressed majorants are compared, with only the new setup and
restoration shears inserted. Their difference is nonnegative. The maximum
added forward majorant is 80662; the inverse one is 1334317. Adding these to
the inherited bounds 77985 and 2475558 yields

    F_new <=158647, B_new <=3809875.
    64 F_new^3 B_new^2 =3709343221562739318443143000000 <2^104.

This closes the retained payload-size cap conditional on the inherited old
majorant bounds. The checker is conservative about compressed target paths;
it does not claim to reproduce a new full physical record hash.

## Role-resolved integration with final12

The unified bank checker reconstructs the original 15,427 helper roles, applies
all old kernel entrances, 434 retained early restorations, twelve new final12
endpoints, and the 72 additional rank-one kernel entrances. The seven sinks
remain removed. New kernel membership is checked disjoint from the affected
final12 helpers and the inherited kernel and descent selections.

The residual rank changes relative to final12 are rank 24:-72 and rank 23:+72.
The combined inventory has 1,646 rank-23 residuals and 11,401 rank-24 residuals;
its total residual rank is 322,862 per replica. The explicit width-120 pattern
`(23,23,23,23,24,4)` absorbs each group of four new rank-23 residuals. The
remaining pure patterns are adjusted with exact integer counts.

All 925,620 role/replica occurrences in a stage are assigned without collision
or omission to explicit bank and block addresses. Five stages use disjoint
bank namespaces. All 161,431 banks per stage are full, attaining the volume
lower bound. Total bank stock is 807,155; with 422,400 data families, literal
stock is 1,229,555. The compact address table is reproducibly generated rather
than duplicated in the repository.

The independently reproduced moment/assembly certificate uses the measured
kernel histogram and final12 chronological delta, while the unified finite
bill charges all 473 setup and 473 restoration shears. Removed pivot reads
are not subtracted from that conservative scalar bill. The corrected
sink-aware payload bound is supplied separately by `check_scalar_bounds.py`.
The line charts, first-frame splits, changed final12 charts and retained
normalizer allowance are checked by the chart modules.

## Evidence boundary

The changed prefix is proved compositionally over F2 using the inherited
complete decoder as a hypothesis. The checker is not a newly executed
complete upstream physical program. All unchanged PR299 and final12 compiler,
routing, prime, reconstruction, complex-supplier and analytic contracts remain
inherited. No unconditional multiplication theorem, exhaustive priority claim,
or optimality claim is asserted. The separate PR300 case, when selected, uses
its explicit additional data pin and verified non-overlap certificate.
