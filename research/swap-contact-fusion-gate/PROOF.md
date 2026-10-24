# A two-region retiming gate after carried-frame field swaps

This is a source-scoped abstract transport result, not a physical supplier
or a universal frame-optimization theorem. It uses the unchanged source at
PR4971 `0130b196145a43a7d305de41f49e56e8e8556378`, including the actual
forward and backward scalar words. Substantial OpenAI Codex assistance;
Apache-2.0. The original swap construction and endpoint proof are Dugongue's.

## The declared replacement class

Keep the scalar contact order, weighted field exchanges, signed native address
operators, source/target owners, start/end charts and all eight center queries.
Keep each center's copy/query/clear interface at its original charts. A field
exchange carries its chart. Between consecutive scalar contacts on each field
strand, fold all intervening signed native address maps into their actual
invertible binary map M. The strand contributes the containment constraint

    M F_u ⊆ F_v

and one price `(dim F_v - dim F_u)^t`, where `0<t<1`, whenever that
difference is positive. Zero differences cost zero. Here t=1-C in the
recursive moment. Grant every containing binary subspace, without imposing
additional native phase restrictions; this enlarges the candidate class.
Fixed scalar/tape/owner work is unchanged and has no negative refund.

The source graph's nodes are scalar ADD contacts and fixed start, final and
owned-center boundaries. A contact has one chart shared by both participating
fields. A SCALE is chart-independent, so it needs no new node. Each current
strand records its most recent contact and intervening binary map. An ADD
consumes two strands and creates two outgoing strands at one node. A center
copy creates a fixed node for its source and owned cell, retaining the source
strand; center queries and clear operations fix the owned-cell chart.

All physical warp events are first checked against their literal signed
G-columns. Arbitrarily changing an event's frame labels is not an allowed
operation. The zero-to-full mutation from the #4571/#4979 lineage is rejected.
This binary consistency check does not re-prove absolute Clifford phases.

A **region** is a connected component of graph edges that have identity
binary map and zero rank in the SOURCE schedule. Every node in one such
region has the same source chart. Its internal identity edges must remain
zero in the replacement class: one common chart is assigned to all nodes
of the region. A region containing any fixed boundary is fixed. At most two
other regions may change chart. All remaining region charts stay at their
source values. Thus splitting a region, opening one of its zero edges or
changing three regions is outside this theorem.

## Exhausting the chart choices

For one changed region, with the outside charts fixed, let

    L = sum of M F_u over incoming boundary edges,
    U = intersection of M^-1 F_v over outgoing boundary edges.

Every allowed common chart F satisfies L⊆F⊆U. Internal nonidentity edges
also require M F=F; these are checked separately. Each source orientation
has 768 free regions: 642 have dim U-dim L=0 and 126 have difference one.
There are therefore only one or two subspaces to consider per region.
The checker enumerates both and checks the complete affected-edge histogram.

For two adjacent free regions, remove BOTH from the outside chart constraints.
Construct separate outer intervals [L_a,U_a], [L_b,U_b]. Enumerate all subspaces
in each interval and check every internal and connecting edge literally.
To enumerate an interval, start with L and repeatedly adjoin every vector of
U outside the current span, retaining each resulting subspace once. Every
intermediate subspace of U/L has a basis, so this process reaches every one;
using only a chosen coordinate basis of U would be insufficient. The replay
checks a two-dimensional quotient fixture containing its noncoordinate line.
The source intervals all fit the enforced four-dimensional quotient bound.

For each of 1,474 adjacent free-region pairs per orientation, this gives
59,231 candidate assignments in total and 2,090 feasible assignments. Count
each affected strand edge once, including edges between the two regions.
The inequality certificates below settle every feasible assignment. The
specific forced-common-chart fusion is impossible for all 1,438 pairs: the
joint L is not contained in the joint U. Each saved witness supplies an
explicit vector in L outside U.

If two free regions are not adjacent, their affected-edge sets are disjoint,
and their feasibility constraints and price differences separate. The
one-region result therefore settles those pairs without enumerating them.

## Exact prices for every 0<t<1

For each feasible assignment, form sorted old and new lists of affected
nonnegative integer edge ranks, retaining zeros. First test that the old list
majorizes the new list, with equal total rank. Concavity of x^t on [0,∞)
then gives

    sum old_rank^t ≤ sum new_rank^t.

The remaining differences, NEW minus OLD price, have exactly three forms:

    A(t) = -1 + 3*2^t - 3*3^t + 4^t,
    B(t) = 12 - 8*2^t - 4*3^t + 4*4^t,
    D(t) = 12 - 9*2^t + 3^t - 3*4^t + 3*5^t.

They occur respectively 24, 6, 1 times in the one-region enumeration and
136, 58, 10 times in the adjacent-pair enumeration, in each orientation.
Every other feasible assignment has a majorization certificate. No floating
moment evaluation or sampled exponent grid is used in the certificate.

A is the third forward difference of x^t at x=1. Its integral representation
is the integral of `t(t-1)(t-2)*x^(t-3)` over a unit three-cube, so A>0
for 0<t<1.

Put `b(t)=B(t)/4=3-2*2^t-3^t+4^t`, l=log 2, and p=log_2 3.
Since `3^5<2^8`, p<8/5. For 0≤t≤1,

    b'''(t)/l^3 = 8*4^t-p^3*3^t-2*2^t
                 ≥ (8-p^3-2)*4^t > 0.

Thus b' is convex and lies below the chord joining its endpoint values.
Both are negative: b'(0)=-log 3 and b'(1)=log(16/27). Therefore b decreases
to b(1)=0, and B(t)≥0 on [0,1], strictly positive for t<1.

For D, put q=log_2 5. The integer inequality `2^23<5^10` gives q>23/10.
Ignoring a positive term and enlarging the negative terms gives

    D'''(t)/l^3 = 3*q^3*5^t + p^3*3^t - 24*4^t - 9*2^t
                ≥ (3*q^3-33)*5^t > 0.

The last sign follows from 23^3>11*10^3. Again D' is convex. Its endpoint
values are negative because

    D'(0) = log(375/32768) < 0,
    D'(1) = log(5^15*27/2^42) < 0.

Consequently D decreases to D(1)=0 and is nonnegative on [0,1]. All numerical
premises here are exact integer inequalities checked by the replay.

This proves that every declared one- or two-region replacement has local
recursive cost at least the source cost for every 0<t<1. Keeping all other
supplier terms fixed cannot turn it into a higher-saving invoice. No new
productive target, supplier admission, selected frontier or κ follows.

## What would change the question

The result permits different charts but keeps each source region intact and
changes at most two of them. It leaves larger simultaneous changes, splitting
a region with new paid transitions, frame descents, changed scalar dependencies,
earlier output access, changed center contracts, new native operators and new
owner resources open. Even a positive abstract graph improvement in a larger
class would still need exact phase-aware physical lowering, actual all-input
return, the full finite/tape bill, completion/compiler, BIT and outer transfer.
