# Exact acquisition by quotient superspaces

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Let K be a finite field of order q. Let v_1,...,v_n be vectors with
nonnegative real acquisition costs a_i. Acquiring a subset S permits free
linear reconstruction from its span. Let V=span(v_i), let U be a specified
target subspace of V, and put c=dim(V)-dim(U). Costs are charged once per
acquired index. Zero vectors, duplicates, zero costs, an empty query pool
and U=0 are allowed.

For every R<=V/U, let W_R be its inverse image under the quotient map, let
E_R={i : v_i in W_R}, and let T_R=span(v_i : i in E_R). Compute a cheapest
basis B_R from the indices E_R for T_R. Discard R if U is not contained
in T_R. Then

    OPT(U) = min_R sum_{i in B_R} a_i,

over the retained candidates. There are exactly

    N_q(c) = sum_{k=0}^c product_{j=0}^{k-1} (q^c-q^j)/(q^k-q^j)

candidates. The number of weighted-basis problems depends only on target
codimension. The empty product is one. For q=2 and c=0,1,2,3,4 the counts
are 1,2,5,16,67. The executable covers q=2 and c<=4.

This is an exact algorithm for additive acquisition. The finite-field
restriction concerns bounded enumeration. The underlying reduction holds
over any field if all superspaces can be considered. No polynomial bound
in c, physical reconstruction cost or new multiplication exponent is asserted.

## Proof of the reduction

Every retained B_R spans U, so its acquisition is feasible and OPT(U) is at
most its cost. Conversely, let S be an optimal feasible acquisition and put
W=span(v_i : i in S). Since U<=W<=V, W is the inverse image of exactly one
quotient subspace R. All indices of S belong to E_R. Therefore T_R=W:
inclusion in W follows from eligibility, while the reverse inclusion follows
from S. Remove dependent vectors from S to obtain a basis of W. Nonnegative
costs ensure removal cannot increase cost. A cheapest basis B_R consequently
costs at most S. That candidate is retained and attains OPT(U). Finiteness
of the index set supplies an optimum, including at zero cost. There is always
a retained candidate at W=V.

The basis need not have rank dim(U). Paying for extra independent directions
can be cheaper than buying queries entirely in U. It is also unnecessary
that eligible queries span the entire W_R. The algorithm uses their actual
span T_R and explicitly checks target coverage.

## Counting and constructing quotient spaces

The number of ordered independent k-tuples in K^c is product_j(q^c-q^j).
Each k-dimensional subspace has exactly product_j(q^k-q^j) ordered bases.
Division and summation prove N_q(c), the classical Gaussian binomial count.

The constructor starts with the zero subspace and repeatedly adjoins every
vector outside each current subspace. Every extension increases rank, and
canonical reduced bases identify repetitions. Induction on rank proves
completeness. The checker uses a different enumeration: choose all pivot
positions, assign every permitted free entry in reduced row echelon form,
then enumerate the resulting vector set. Unique reduced forms prove that
it lists every quotient subspace exactly once. Both enumerations terminate
after c rank layers. A third finite corroboration scans all vector subsets
and tests closure under XOR for c<=4.

To construct the quotient map, extend a basis of U to a basis of V and take
the coordinate forms of the added elements. The checker accepts any c forms
that vanish on U and map V onto K^c. Rank-nullity makes their kernel on V
exactly U, so they parameterize the same complete superspace family. No
favorable choice of quotient coordinates is assumed.

## Checkable candidate optimality

The binary certificate gives selected indices and dual forms d_j with
d_j(v_i)=delta_ji on selected vectors. This proves independence. For every
eligible v, the checker computes coordinates d_j(v), reconstructs v, and
checks that every used selected index has price at most the price of v.
The coordinates prove full eligible coverage and the absence of an improving
single-element basis exchange.

That exchange condition implies global cheapest-basis optimality. At every
strict price threshold, all cheaper eligible vectors are spanned by cheaper
selected vectors. Thus the selected cheap prefix has the full rank of the
eligible cheap prefix. Every other basis contains at most that many cheap
vectors. Summing these rank inequalities over the finite distinct prices,
or pairing sorted basis prices, proves that every other basis costs at least
as much. This is classical weighted linear-matroid greedy optimality,
inherited from Ali Romman's PR5791 contract rather than a new matroid theorem.

If a candidate cannot span U, its certificate supplies one target vector and
a linear functional that is one there and zero on every eligible query.
No eligible acquisition can obtain that target. Otherwise the checker
reconstructs every target from the selected basis. After checking all
quotient spaces, it checks the reported minimum. The certificate checker
does not rerun global subset optimization.

## First strict improvement and an interior necessity example

For queries (1,2,3), prices (3,2,2), and target U=span(1) in F2^2, a cheapest
whole-span basis buys 2 and 3 for four units. Both are needed to reconstruct
the target in that basis. The new optimizer buys query 1 for three units.
Here c=1, so only U and V are considered.

For queries (1,2,3,4,7), prices (8,2,2,1,2), and target span(1) in F2^3,
queries entirely in U cost eight. A cheapest whole-span basis costs five.
The intermediate superspace span(1,2) has a four-unit basis (2,3), and four
is optimal. Every query costs at least one; the sole one-unit vector is 4,
and neither it nor any price-two vector is the target. A subset cheaper than
four cannot span 1: XOR with the sole one-unit vector 4 sends the
price-two vectors 2,3,7 to 6,7,3. This shows why considering only U and V is insufficient
once c=2. No predecessor numerical result is used for either example.

## Attribution and scope

Ali Romman / PR5791 supplies whole-span acquisition, the partial-target
question and its exchange certificate contract. Nick Petalas / PR5878 gives
the earlier sharp c+1 guarantee for pruning a cheapest whole-span basis.
The new step is the exact quotient-superspace reduction with a complete
bounded optimizer and certificate. Quotient spaces, rank-nullity, Gaussian
binomial counting and weighted matroid selection are classical tools.
No literature-wide priority for enumerative optimization is claimed.

This does not price XOR reconstruction, physical delivery, restoration,
phase realization, storage or native legality. A source-to-query adapter,
complete signed supplier invoice and all-size caller remain separate proof
obligations. Independent human and formal proof-kernel review are unclaimed.
