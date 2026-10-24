# Optimal ordering of a one-arc circular Schur complement

Let n >= 3, 1 <= w <= floor(n/2), and let a nonempty proper contiguous arc
of the n-cycle be eliminated. Write M >= 1 for the surviving count. Label
the surviving path by 0,...,M-1 in its inherited cyclic orientation.
Half-bandwidth in an order p is max |p(i)-p(j)| over nonzero off-diagonal
entries, with value zero for a singleton.

**Theorem.** For any matrix supported on the circular radius-w band, if
the eliminated principal block is invertible, its Schur complement admits a
simultaneous row/column order of half-bandwidth at most min(M-1,2w).
For the full negative host H=I-E, where E has zero diagonal, strictly positive
entries at every circular distance 1,...,w, zero entries outside the band,
and every row sum is less than one, this is the exact minimum over all orders.
Equal off-diagonal magnitudes are unnecessary.

The new result is the optimal ordering and its matching lower bound. The
negative-sign/no-cancellation argument is credited to James Reed / jwr404's
[PR #4289](https://github.com/CrocSwap/integer-mult-bounds/pull/4289), following
[#4286](https://github.com/CrocSwap/integer-mult-bounds/pull/4286).
Those packages leave survivor reordering open. This theorem makes no claim
about the physical price of the permutation or the Gaussian caller's order.

## 1. Identify the survivor support graph

Put B={0,...,min(w,M)-1} union {max(0,M-w),...,M-1}.
The survivors touching the eliminated arc are exactly B. A path from a
survivor to the arc first crosses one of the two surviving endpoints, so
the minimum circular distance to the arc is min(i+1,M-i).

For an arbitrary band-supported matrix, the Schur update can couple only
pairs in B. An original coupling between i<j either has j-i <= w along the
surviving path, or its shorter route crosses the eliminated arc. In the
latter case both endpoints touch that arc and hence belong to B. Thus the
Schur support is contained in the graph G_(M,w) whose edges are

    i < j and [j-i <= w or {i,j} subset B].

For the full negative host, the eliminated block is I-E_A. Its inverse is
sum_(k>=0) E_A^k. All terms are nonnegative, and every entry is positive:
the arc is connected by the strictly positive nearest-neighbor entries.
Therefore each pair in B receives a strictly negative Schur update. Every
original in-band edge is strictly negative and cannot cancel this update.
Edges with j-i <= w are original edges. Hence this host's support is exactly
G_(M,w). This uses the predecessor's sign argument as a premise and derives
the explicit path-plus-end-clique graph needed for the new ordering theorem.

## 2. A folded order attains the upper bound

Use the vertex order

    0, M-1, 1, M-2, 2, M-3, ...

with the middle vertex written only once. If p(i) is its zero-based position,

    p(i)=2i                   if i < ceil(M/2),
    p(i)=2(M-1-i)+1           otherwise.

Consecutive surviving-path vertices have position differences at most two,
including the central pair. Summing these adjacent differences gives
|p(i)-p(j)| <= 2|i-j|. Every path-power edge therefore spans at most 2w.

If M >= 2w, B occupies exactly the first 2w positions of this order, so its
clique spans at most 2w-1. If M < 2w, B is the entire graph and every edge
spans at most M-1. These bounds prove min(M-1,2w) for all edges. A simultaneous
permutation changes entries' locations only, so it preserves this support
bound for arbitrary coefficients and any cancellations.

## 3. No order improves the constant on the full negative host

In any linear vertex order of half-bandwidth b, the first vertex has degree
at most b. Thus b is at least the graph's minimum degree.

If M <= 2w, B contains every vertex, so G_(M,w) is complete and its minimum
degree is M-1.

If M >= 2w+1, B consists of two disjoint w-vertex strips. A vertex outside B
has exactly 2w path-power neighbors. A vertex in B has 2w-1 other clique
vertices and at least one neighbor outside B: vertex w for the left strip,
or vertex M-w-1 for the right strip. Its degree is therefore at least 2w.
There is at least one vertex outside B, so the minimum degree is exactly 2w.
The folded upper bound and this degree lower bound coincide.

For example, M=9 and w=2 give exact minimum four, while the inherited linear
survivor order has bandwidth eight. The same graph shows that the linear
separated-carve constant 2w-1 cannot replace 2w in this circular problem.
This is an optimal reordering result, not a disagreement with the
predecessor's bandwidth measured in circular distance.

## Scope

The proof covers all sizes in the stated matrix class. Finite checks only
corroborate the graph identification and ordering; they are not a proof of
these quantifiers. An arbitrary invertible arc block gives the upper bound;
full negative support and the row-sum condition give the sharp lower bound.
Zero or signed couplings can have smaller minima. Multiple eliminated arcs
can join different support components and are outside this theorem. Row/column
routing costs, ownership, inverse norms, rounded arithmetic, tape layout,
compiler/hosting, supplier admission and a new kappa are unclaimed. No
independent human or formal proof-kernel review is claimed. No literature
priority is claimed for folding a path or the minimum-degree bandwidth bound.
