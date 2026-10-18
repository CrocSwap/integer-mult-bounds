# Exact bounded neighborhood around the PR941 matching floor

This package studies the historical PR941 disjoint-helper-pair class around
the frozen PR915 target basis. Gareth Davidson (@bitplane) already proves
the arithmetic minimum of 11,948 complete ADDs, and supplies an admitted
11,949-ADD word. The three retained arithmetic optima fail the 192-bit
nine-stage guard. This contribution exhausts a precisely defined larger
finite neighborhood and finds that none of its 857 words closes that gap.
It does not prove that every arithmetic optimum fails.

## Fixed class and complete neighborhood

The pinned PR915 D consists of 306 target shears E, the direct middle matrix
R=EK, and literal reversed target shears. A directed pair (a,b) prepares
helper a += helper b, requiring column b of R to become column b XOR column a.
The helper operation is repeated in reverse order after target restoration.
Its complete gain is

    weight(R[:,b]) - weight(R[:,b] XOR R[:,a]) - 2.

Both paid helper gates are included. Pairwise disjointness makes gains
additive and the helpers' preparation/restoration commute. The generic
two-sided identity gives the same map on arbitrary targets and helpers.
The original source code and proof retain credit for this construction.

For each of the three frozen nominations, choose two distinct matching edges.
Keep every other directed edge exactly fixed. On the four distinct endpoints,
enumerate all three perfect pairings and both orientations of each new edge:
12 replacements. Keep precisely those whose two-edge gain equals the removed
two-edge gain. This includes retaining both pairs, reversing either one,
reversing both, and true alternating four-cycle exchanges. Deduplicate by the
entire sorted list of directed pairs. Because the old matching has at least
two edges, this also covers zero- and one-edge changes in this domain.

This definition fixes the support to vertices already matched in the chosen
two edges. It excludes using an unmatched vertex, changing three or more
edges, iterative closure, a new target basis, overlapping helper shears,
stars, a different phase-B word or global resynthesis. No other matching
search is inferred. Sorted ordering loses no word in the priced class:
disjoint helper gates commute, and all positive accumulated weights are
nondecreasing between copies, so a permutation of disjoint preparation or
restoration gates cannot change their maximum or downstream state.

The three nomination sizes are 199, 200 and 199. Thus the complete proposal
count is 12*(C(199,2)+C(200,2)+C(199,2))=711,624. The accepted distinct
neighborhood sizes are 285, 287 and 285, with no cross-seed duplicates:
857 complete words. These counts include the three old nominations.

## Arithmetic floor and actual guard values

The unchanged PR941 verifier checks its integer vertex/odd-set dual on all
96,141 unordered helper pairs. Its dual objective is twice 1,260, equal to
the gain of each nomination. The exact complete arithmetic floor remains
13,208-1,260=11,948 ADDs. No matching solver or new optimization theorem is
needed. Every retained replacement preserves this gain; the full word is
assembled with both helper wrappers and its price independently recounted.

All 857 words have 5,728 D ADDs and 11,948 total ADDs. The other 6,220 ADDs
and all non-D fields remain fixed. Every candidate's D action equals the
parent on all 661 independent input columns, represented simultaneously by
bit masks; this includes arbitrary dirty helper restoration. These finite
identities do not grant supplier admission.

Every complete literal stream contains the COPY/ERASE scatter lifetimes.
Forward and reverse cancellation-free values are recomputed with those
operations, including the reversal of COPY and ERASE roles. The original
macro evaluator agrees with the literal evaluator on every word. The two
guard values are exactly

    local = 64 F^3 B^2 < 2^104,
    nine  = 2^18 F^5 B^4 < 2^192.

All 857 local guards pass. All 857 nine-stage guards fail. The smallest
nine-stage value is attained by reversing two old orientations in nomination
2 (zero based), removing indices 51 and 102 and inserting directed pairs
(149,131) and (318,250). It has

    F = 72,467; B = 10,522,512;
    local = 2696743753697311832946628804608;
    nine = 6422720960971889698335381712362626086444383357876503052288;
    2^192 = 6277101735386680763835789423207666416102355444464034512896.

Thus even the best nine-stage value in this finite domain is too large.
The 102-bit local guard alone would accept it, demonstrating why it is
necessary to retain the complete nine-stage invoice expression. All recipes,
directed-pair digests and exact prices are in EXPECTED.json. Its best pair
list is included only as a boundary witness, not an admitted construction.

## Independent evidence and limits

The primary engine enumerates three pairings times four orientations, uses
integer masks for gains and dirty-column identities, and consumes the pinned
original builder and verifier for assembly, literal pricing and the dual.
The separate engine imports neither of those implementations nor the primary
engine. It enumerates all 24 permutations of four vertices, quotients by
swapping the two directed edges, uses set symmetric differences for gains,
and matches the complete candidate digest inventory. It reconstructs and
prices every literal word, checking 10,239,436 ADD records per direction,
plus the COPY/ERASE events. Its minima and every F/B guard value agree.
The literal stream rule follows the attributed PR941/PR926 convention;
implementation independence is not independent human review.

There is no new circuit, no new kappa, and no global impossibility result.
The PR941 precision-constrained optimum remains 11,948 or 11,949 outside
this exhausted neighborhood. Its inherited syntactic H2 and literal K
extraction remain false for helper-writing D words. Semantic D adoption,
changed whole-hosted emission, complete supplier invoices, common-label
realization, native 5/9/11-stage admission, compiler/precision/tape and
analytic obligations are unchanged. Native tools were not run.

Base abdc6a7002abdbcd9e21bfc5e1a795784deacfdf selected PR942/PR589; that
snapshot is historical context. During the round, upstream advanced to
ba82555c64e1879e4b7decce28186f208fcb8262 and selected PR1042 at
1672188119205421/10^18. This package keeps its fixed historical comparison
and makes no claim to reprice that newer selected construction.
