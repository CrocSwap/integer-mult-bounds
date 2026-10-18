# Exact enumeration of minimal two-flat covers

Let D be a finite set of vectors in a vector space. A cover is an ordered pair
(A,B) of linear subspaces with D contained in A union B, dim A <= c and dim B <= d.
Order pairs by componentwise inclusion. The desired output is every minimal
cover, represented by canonical bases. A nonminimal cover is unnecessary for the
s4z requirement interface: any later host pair that contains it also contains a
minimal cover below it. Such a minimal cover exists: every strict decrease of a covering pair decreases the nonnegative integer dim A + dim B. Conversely every emitted pair must actually cover D.
This is about a union of two subspaces, not their sum.

## Branch lemma

Begin at (0,0). If some x in D lies in neither current subspace, any extension
that covers D must put x in its first or its second subspace. Recurse to
(A+<x>,B) and (A,B+<x>) whenever the respective dimension bound permits it.
Both children are necessary; replacing this split by a choice is unsound.
If no x remains uncovered, the current pair is a cover.

Fix any target cover (U,V). Starting at (0,0), at every nonterminal node contained
in (U,V), the uncovered x belongs to U or V. At least one child therefore remains
contained in (U,V). That child respects the capacity bound. Each edge increases
dim A + dim B by exactly one, so the path terminates after at most c+d edges at a
cover contained in (U,V). If (U,V) is minimal, that terminal pair equals (U,V).
Thus every minimal cover is enumerated. Every terminal pair is an actual cover.
This argument covers arbitrary D and does not assume generic independence,
particular P112 directions, or completeness of the retained direction catalogue.

The binary tree has at most 2^(c+d+1)-1 nodes and 2^(c+d) leaves. In the measured
(c,d)=(4,5) domain this is at most 1,023 nodes and 512 leaves per residual mask.
The adapter permits capacities 0..6, so even the largest kernel tree has at most
8,191 nodes and 4,096 leaves. These are coarse bounds, not measured visit counts.
The old flat-generation routine's 60,000 intermediate-entry limit is not needed
by this branch tree. Output overflow still fails explicitly.

## Minimality lemma

For any cover (A,B), define

    A0 = span(D \ B),       B0 = span(D \ A).

Then (A,B) is minimal if and only if A0=A and B0=B.

Necessity: A0 is contained in A and (A0,B) still covers D. If A0 is strictly
smaller, it dominates (A,B); the same argument applies to B0.
Sufficiency: if a cover (A',B') is contained in (A,B), then
D\B is contained in D\B' and in A', hence A=A0 is contained in A'. Thus A'=A.
Similarly B'=B. There is no strictly smaller covering pair.

The implementation checks equality by rank: the residual span is already
contained in the current flat, so equal dimension is equivalent to equality.
This is not valid for arbitrary subspaces lacking the containment premise.
Terminal pairs failing either equality are discarded. Duplicates are harmless
and are removed by the unchanged downstream canonical-key set construction.
The sorted kernel harness also removes duplicates explicitly.

## Equivalence to the pinned enumerator

The predecessor enumerates every A spanned by a subset of D with dim A<=c, sets
B=span(D\A), and retains componentwise minimal pairs with dim B<=d. The lemma
shows that every minimal cover has exactly this form. Both methods therefore
produce the same minimal antichain. Consequently, for every proposed host pair
(U,V), both say that D can be covered inside (U,V) on exactly the same inputs.
No direction or option can be lost by replacing one minimal-antichain generator
with the other. The theorem is stronger than the finite differential replay.

Credit: DreamingOfClouds' pinned `s4z.c` already contains the uncovered-label
branch in `dfs4` for a Boolean feasibility test. This contribution extends that
existing approach to the expensive *all-options* routine, supplies the minimality
criterion, and checks equivalence and performance. It does not claim discovery
of a new general-purpose subspace-search principle.

## Scope and limitations

The installed adapter accepts only the original no-free-line model (`FREES=0`,
with no environment override), fixed bundled data, and the documented benchmark.
It does not certify free deletions, the whole outer orbit enumeration, the
completeness of data88, machine-integer real-rank arithmetic, RRC, or the K2
conjecture. Existing outer fixed-array bounds and scientific assumptions remain
inherited. The positive span-five control and sampled negative span-two outputs
are finite checks, not a proof that the entire (6,5,4,4) domain has no crack.
The copied-information cost of a decoder is unchanged. No new supplier or kappa
follows from faster enumeration.
