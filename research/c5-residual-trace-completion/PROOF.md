# Cost 20 on the four remaining physical C5 cores

This completes the four local obligations left by PR3268 and PR3271.
It extends thakrarsagar's weighted-rank and equality-trace method in PR3256.
The new ingredient is a weighted cover using every forced singleton and
nonadjacent pair block, with physical coefficients specific to these cores.

## Exact object

The pinned PR2782 recipes supply 112 scalar labels in F2^9 and a partition
into 56 two-port planes. Each plane has binary Gram matrix I2. The four
ordered cycles below are checked against those actual labels. Adjacent
planes are orthogonal; other distinct planes are nonorthogonal.

A strict fitting matrix K over Q, R or C has ten scalar coordinates, two
per plane. Its diagonal is one. Its off-diagonal entries inside a plane
and between nonadjacent planes vanish. Entries between adjacent planes
are unrestricted. In an arbitrary finite decomposition

    K = sum_t u_t v_t^T,

transpose is ordinary transpose, including over C. Factors, signs,
denominators and term count are unrestricted. Delete zero factors and
absorb scalar coefficients into one factor. If A_t and B_t are their
sets of touched planes, a term costs the binary pairing rank c(A_t,B_t)
between the COMPLETE two-port planes of A_t and B_t. Touching one scalar
port charges both plane labels. Zero-cost nonzero terms are allowed.

**Theorem.** Every such decomposition costs at least 20 on each of
`(3,10,4,6,13)`, `(3,10,12,23,13)`, `(6,13,23,54,26)` and
`(14,24,47,18,55)`. Five explicit terms attain 20 on each.

This is a scalar local theorem. It does not add floors across overlapping
cores, price a native program, admit a supplier or improve kappa.

## Weighted rank cover

Use the ten blocks in this fixed order:

    {0}, {1}, {2}, {3}, {4}, {0,2}, {0,3}, {1,3}, {1,4}, {2,4}.

Their forced principal matrices are I2 or I4, of ranks r_H=2|H|. Put
b_H(A,B)=1 if both A and B meet H, and zero otherwise. If n_H is the
sum of these hits over terms, restriction to H gives a decomposition
of I_(r_H) into n_H rank-one matrices. Therefore n_H>=r_H.

The following integer weights have common denominator six. Their order
is the block order above, in the stated physical cyclic orientation.

| Physical cycle | Integer weights | Sum w_H r_H |
|---|---|---|
| 3,10,4,6,13 | 4,8,2,4,6,4,2,4,0,6 | 112 |
| 3,10,12,23,13 | 4,6,2,4,4,4,2,4,2,6 | 112 |
| 6,13,23,54,26 | 6,3,3,3,3,3,3,3,6,3 | 108 |
| 14,24,47,18,55 | 2,8,4,6,4,4,6,0,4,2 | 112 |

All 1,024 ordered support pairs per core satisfy the exact inequality

    d(A,B) = 6c(A,B) - sum_H w_H b_H(A,B) >= 0.

These finite premises are checked with the actual rectangular binary
matrices. A graph isomorphism alone does not supply them. RESULT.json
retains the ordered tariff-table hashes. A numerical LP suggested the
weights; neither an optimizer nor floating point is used in replay.

For total integer cost C, let x_H=n_H-r_H>=0 and D=sum_t d(A_t,B_t).
Then

    6C - sum_H w_H r_H = sum_H w_H x_H + D.

Thus C>=19 on three cores and C>=18 on the third. To prove C>=20,
it suffices to exclude cost19 on all four and cost18 on the third.
Their slack budgets on the left are respectively 2 or 6, and zero.

## Trace equations at rank equality

If exactly r rank-one matrices sum to I_r, assemble their columns into
square U,V. Then UV^T=I_r implies V^TU=I_r. Each term's restricted trace
is consequently one. No positivity or conjugation is used.

For term t, write z_i=u_(t,i)^T v_(t,i) on plane i. If i is absent from
A_t intersect B_t, z_i=0. If n_H=r_H, every term must satisfy

    sum_(i in H) z_i = b_H(A_t,B_t).

These equations have integer coefficients. Their consistency over Q is
equivalent to consistency over R or C by Gaussian elimination. They
are necessary conditions; consistency does not imply factor existence.
A block with excess imposes no individual trace equation.

For positive-weight blocks, enumerate all nonnegative excess vectors
with sum w_H x_H at most the slack budget, and set D to the remaining
slack. For a zero-weight block, ignore its actual excess and impose NO
trace equation. Its hit count is only capped at r_H. This weakening
contains every real decomposition, including those with arbitrarily
many hits on that block. In particular a capped count of r_H must not
be confused with true rank equality.

The enumeration gives 3, 4, 48 and 3 cases across the four cores, 58 total.
For each case retain every support pair whose trace system is consistent
and whose defect fits its budget. Reuse of a support pair is allowed.

## Complete finite count certificate

A retained term increments ten block-hit coordinates and one defect
coordinate. Positive-weight hit coordinates and defect are bounded by
the case's exact target. Zero-weight hit coordinates are capped at r_H.
Replay checks that every zero-cost support pair has zero hits in ALL ten
blocks and zero defect. It therefore has zero count image and can be
removed from this analysis regardless of multiplicity or coefficients.
Every paid profile advances a bounded coordinate.

Starting at zero, close under addition of every retained profile, with
repetition. The finite state box has size at most

    (D+1) product_H (target_H+1).

The implementation enforces an upper bound of six million states per case
and exhausts its queue within that bound. It reaches 5,327 states across
all 58 cases. No case reaches its required target. A separate dense-rank,
integer-elimination implementation groups transitions by actual total
cost and obtains identical profile/state counts and unreachable targets.
Thus no finite fitting decomposition has C<20.

An actual cost19 support multiset on the first core passes every principal
rank count. It consists of mask pairs `(14,14)`, `(25,9)`, `(28,7)`,
`(31,16)` and `(31,19)`, of costs `5,3,3,2,6`. All singleton/pair hits
are exactly their required ranks. It fails the trace constraints.
The rejecting control also checks that removing trace filtering restores
reachability. Counts alone would not prove this theorem.

## Sharpness

For cyclic i=0,...,4 let w_i=e_(i,1)+e_(i+1 mod5,0). The five terms
w_i w_i^T partition the ten scalar coordinates, have diagonal one, and
introduce off-diagonal entries only between adjacent orthogonal planes.
Every constrained scalar entry fits. Each term touches two orthogonal
nondegenerate planes and has complete-plane tariff four. Total cost is20.
The primary checker verifies all constrained entries and tariffs. The
separate checker uses ten scalar singleton terms, each charged the full
plane tariff two, giving an independent cost20 upper bound.

## Dependencies and limits

The four-core proof is self-contained after the pinned recipe/matching
bytes and elementary characteristic-zero linear algebra. Pending PR3268
and PR3271 identify the missing cores and retain method/source credit;
no pending executable or unavailable Git object is needed by fresh CI.
Their other-core results are not replayed or silently admitted here.
Together those pending claims cover more cores, but no global112-port
floor follows by addition across overlaps.

Native realization, restoration, precision, hosting, all-size compilation,
the full consumer invoice and multiplication theorem remain outside scope.
Selected cold replay, Lean, Docker, human review and proof-kernel review
were not run. The finite checks establish the written proof's premises,
not a formal verification of integer multiplication.
