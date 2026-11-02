# Exact restored tours through one mask layer

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Boundary and charged alphabet

Fix n>=1 and 0<=k<=n. There is one borrowed anchor A, source rows
B_1,...,B_n, and arbitrary target rows X_(S,j). Every row is an arbitrary
element of F_2^L, for any L>=1. There is at least one target for each
k-element subset S of {1,...,n}; its multiplicity r_S is a positive integer.
The required map is

    X_(S,j) <- X_(S,j) + A + sum_(i in S) B_i.

All source rows, including A, must return to their exact input values.
Let R=sum_S r_S and N=binomial(n,k).

The permitted word toggles A by one unchanged B_i and writes each target
exactly once by adding the current A. No other mixing or workspace is
allowed. Every toggle and every write costs one row ADD. Intermediate
anchor masks and repeated visits are unrestricted. In particular the
anchor is arbitrary dirty data, not a zero-initialized accumulator.

The target identities are quantified over all input rows. Thus a write
to X_(S,j) must occur when A's source mask is exactly S. Equality at a
particular numerical input would not suffice. The independent coefficient
of A stays one throughout the permitted word.

## Theorem

For 1<=k<=n, the minimum number of anchor toggles is

    T(n,k) = 2 binomial(n,k) + 2k - 2.

The minimum complete row-ADD count in this alphabet is R+T(n,k).
For k=0 the corresponding counts are zero toggles and R writes.
No optimum over unrestricted CNOT circuits is claimed.

The application to every k>=3 is the new part of the fixed-weight-layer
tariff here. The k=2 specialization, including unequal positive prices,
is already covered by Nick Petalas / PR4899. The k=1 and k=n endpoint
cases are elementary and included to state the uniform formula.

## Lower bound, including arbitrary repeated visits

View the anchor mask as a vertex of the n-cube. Each toggle crosses one
cube edge. The word is a walk starting and ending at the empty mask and
visiting all N required masks.

Order the required masks by their first visits, S_1,...,S_N. The part of
the walk up to S_1 has length at least k. Each disjoint segment from the
first visit to S_i to the first visit to S_(i+1) has length at least two,
since distinct masks of the same weight have Hamming distance at least
two. The remaining segment from the first visit to S_N to the final empty
mask has length at least k. These segments partition the entire walk.
Consequently its length is at least

    k + 2(N-1) + k = 2N+2k-2.

The argument permits every off-layer excursion, every repeated mask and
any ordering of target writes. The exactly R target writes add R to the
bound. For k=0, the unmodified anchor already has the required parity.

## An attaining fixed-weight listing

For completeness the classical reflected Gray construction is proved here.
Let G(n,k) be the binary reflected Gray list on n bits, with all entries
of weights other than k deleted. In integer notation the unfiltered list
is i XOR floor(i/2), for i=0,...,2^n-1. Its reflected definition gives

    G(n,k) = G(n-1,k), then 2^(n-1) + reverse(G(n-1,k-1)),

where out-of-range lists are empty. For k=0 or k=n there is a single
entry. The recurrence lists every weight-k mask exactly once.

For 1<=k<=n its first entry is 2^k-1 and its last entry is
2^(n-1)+2^(k-1)-1. This follows by induction from the two blocks;
the singleton k=n case has the same endpoints.

For 1<=k<n, adjacent entries inside either block differ in exactly two
bits by induction. At the junction, when k=1 the masks are 2^(n-2)
and 2^(n-1), so they differ in two bits. For 2<=k<n, the junction masks
are

    2^(n-2) + 2^(k-1) - 1,
    2^(n-1) + 2^(n-2) + 2^(k-2) - 1.

The second removes bit k-2 and adds bit n-1 relative to the first.
They also differ in exactly two bits. This proves the adjacency assertion
in all cases, including k=n-1, where the first block is a singleton.

Start at the empty mask, toggle its k coordinates to reach the first
listing entry, and write its designated targets. Move between consecutive
listing entries by their two differing coordinates, writing the targets
at each entry. Finally toggle the k coordinates of the last entry to
restore A. Each B_i is unchanged and each target receives exactly its
specified parity. The transition count is k+2(N-1)+k, attaining the lower
bound. The order of the two toggles within an exchange is immaterial.

## One complete improvement fixture

For n=5, k=3 and one target per mask, N=R=10. The new exact tour needs
24 anchor toggles and ten target writes, or 34 row ADDs. Applying the
four required source rows directly to each target needs 40 row ADDs.
The six-ADD reduction includes anchor preparation and full restoration.
At width L this is 34L versus 40L bit XORs. It does not include tape-head
movement, which is absent from the declared model.

## Scope and credit

Cinna Davis / PR2271 supplied the borrowed-source multi-mask contract,
its square example and the explicit higher-dimensional tour question.
The reflected Gray listing and cube distances are classical. The new
contribution is their exact restored fixed-weight-layer tariff and its
arbitrary-dirty row-circuit realization in this contract, beyond the
previously covered pair layer. Ali Romman / PR5372 treats a separate
all-nonempty-mask, paid clean-row contract. Those scientific verifiers
are neither imported nor replayed here.

The finite replay corroborates the theorem on its declared bounded
domains; the universal quantifiers rest on this written proof. A physical
caller, native frames and implementation, ownership/hosting, routing,
precision, recursive pricing and a complete supplier remain open.
No selected framework assumption or complete multiplication theorem is
proved. Independent human and formal proof-kernel review are unclaimed.
