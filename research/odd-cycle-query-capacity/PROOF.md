# Every unequal odd-cycle query mask

JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0. Credit Tekalign
PR3362's C5 proof/interface, Nick Petalas PR4909's bipartite interface, and
classical finite linear-programming duality and capacitated matching methods.
No literature-priority claim is made for odd-cycle coding or matching.

## Contract and exact answer

Let n=2k+1, k>=2, and d_i be any nonnegative integers, S=sum d_i. Over any
field F take an S by S fitting matrix M with M_ii=I_(d_i), and M_ij=0 for
distinct nonadjacent vertices of C_n. The two allowed ordered blocks at every
edge are arbitrary rectangular matrices. They need not be symmetric, invertible,
commuting, or simultaneously diagonalizable. A zero-width block is empty.
Let alpha be the largest sum of d_i on an independent vertex set. Then

    min rank(M) = max(alpha, ceil(S/2)).                 (1)

For linear query factorizations M=AB this is the exact minimum intermediate
field-coordinate dimension. It is not a native call count, physical COPY cost,
Gaussian rank, admitted supplier, or multiplication exponent. No assertion is
made about nonlinear encoders, changed zero masks, or a physical embedding of
these cycles inside the P112 geometry.

## Lower bound for arbitrary directed blocks

Factor M=AB through r=rank(M) dimensions. Let B_i be its i-th column block,
A_i its i-th row block, and U_i=im B_i. Because A_i B_i=I, B_i is injective,
dim U_i=d_i, and A_i is injective on U_i. Because both ordered forbidden blocks
are zero, A_i annihilates the sum of all nonneighbor U_j. Thus

    U_i intersect sum_(j nonadjacent to i, j!=i) U_j = 0. (2)

For every independent set the U_i form a direct sum, by applying A_i to a
putative relation. Therefore r>=alpha.

Put t_i=dim(U_i intersect U_(i+1)). The two subspaces U_i intersect U_(i-1)
and U_i intersect U_(i+1) lie in U_i and have zero intersection: i-1 and i+1
are nonadjacent when n>=5. Hence

    t_(i-1)+t_i <= d_i;  2 sum_i t_i <= S.               (3)

For each i take J_i={i,i+1,i+3,i+5,...,i+2k-1} modulo n. The subgraph on
J_i consists of exactly the edge {i,i+1} and k-1 isolated vertices. Applying
each isolated A_j kills all the other subspaces. Their sum is therefore direct
with U_i+U_(i+1), so

    r >= sum_(j in J_i) d_j - t_i.

Every vertex lies in exactly k+1 of these n rotated sets. Sum the inequalities
and use (3):

    n r >= (k+1) S - sum_i t_i >= (k+1/2) S = n S/2.

Integer dimensions give r>=ceil(S/2), in every characteristic. This proves the
entire lower bound, including arbitrary noncommuting payload blocks. Finite
matrix tests are corroboration of this argument rather than its justification.

## Exact integral sharing

An edge count x_i>=0 reserves x_i distinct coordinates at both endpoints.
Private count p_i=d_i-x_(i-1)-x_i must be nonnegative. One shared coordinate
uses the rank-one all-ones two-by-two block; one private coordinate uses a
scalar identity. These disjoint groups fit the full ordered zero mask over every
field and have rank sum_i(x_i+p_i)=S-sum_i x_i.

For completeness the needed cycle matching fact is proved here. Consider the
finite LP max sum_i x_i with x_i>=0 and x_(i-1)+x_i<=d_i. Its dual is min
sum_i d_i y_i with y_i>=0 and y_i+y_(i+1)>=1. Truncating y_i at one preserves
feasibility and cannot increase the objective. An extreme dual point is either
an integral vertex cover or all y_i=1/2. Indeed a proper component of fractional
vertices connected by active edge equalities is a path, whose alternating
plus/minus perturbation preserves all active equalities for a sufficiently small
amount; an endpoint cannot be pinned by an adjacent integral value without
becoming integral itself. Such a path is not extreme. If the component is the
whole odd cycle, its alternating equations force all values to one half.
Finite LP strong duality therefore gives the fractional optimum

    min(S-alpha, S/2).                                 (4)

Here integral covers have minimum weight S-alpha because their complements
are independent sets. To pass to integers, choose an extreme optimal primal
point. Any positive-support component that is a proper path has integer edge
values: a full-rank active system is solved from a zero edge/end or a tight
endpoint constraint and then successively along integer vertex capacities.
Equivalently the path incidence matrix has every nonsingular square minor
0 or +/-1 by removing a leaf. Fractionality can consequently occur only when
all n edges are positive and every vertex constraint is tight. The cyclic
system x_(i-1)+x_i=d_i has determinant two; any fractional solution has all
x_i integer-plus-one-half. Round x_0,x_2,...,x_(n-1) down and the intervening
edges up. Every vertex keeps its total except vertex 0, whose total drops by
one. Nonnegativity remains valid, and the objective loses exactly one half.
Thus the maximum *integral* sharing is

    min(S-alpha, floor(S/2)).                          (5)

When (4) is integer, the fractional extreme case cannot be optimal: the sum of
an odd number of half-integers is a noninteger. This also covers zero widths
and zero total. Equations (5) and the channel construction attain (1).
The LP argument is a classical matching method, not a new general LP theorem.

## Compressed deterministic construction

The implementation does not call an LP solver or expand d_i coordinates.
Fix the closing edge x_(n-1)=t with 0<=t<=D=min(d_0,d_(n-1)). The remaining
capacities on endpoints are reduced by t. A path maximum matching is obtained
by saturating the leftmost remaining edge as far as possible and continuing.
An exchange proves this greedy rule: if an optimum uses fewer copies at the
left edge, an unused copy at its right endpoint can be taken directly, or one
copy on the next edge can be moved left without reducing the number of edges.
After fixing the left edge repeat on the shorter path.

Let g(t)=t+the optimum path sharing. The capacitated path matching/cover dual
is integral, either by the leaf argument above or ordinary weighted bipartite
matching duality. Thus for integer t it equals the minimum of the path-cover
affine functions

    cover_weight + t*(1 - number_of_endpoints_in_cover).

Those slopes are -1,0,1. The same LP expression on real t is concave, so g on
integers is discretely concave. Binary search for the first index satisfying
g(t)>=g(t+1) finds a maximum, including an arbitrary long flat plateau and
D=0. It uses at most 2 ceil(log2(D+1))+1 greedy path evaluations; each takes
O(n) integer operations and O(n) compressed integers. The maximum arithmetic
operand bit length is O(log(S+1)); source/target coordinate expansion and any
physical index/bit-operation costs are separate. `validate` checks every
coverage equation and exact answer, and emits a weighted independent witness using linear-space backpointer
reconstruction, without quadratic prefix-tuple copying.

## Discriminating cases and stop

Seven width-two vertices need seven query coordinates, rather than twice the
scalar optimum four. For d=(2,1,2,1,2,1,1), alpha=6 exceeds S/2=5; the actual
answer is six. For seven unit vertices alpha=3 but ceil(S/2)=4. Both terms
are essential. The C5 predecessor is recovered exactly, not claimed again.

The proof closes this cycle-mask dimension contract. It does not fund copying,
dirty compensation/restoration, owner access, source coefficient preparation,
frames, hosting, stock, finite precision, physical tapes, compiler or outer
transfer. A new physical construction needs those contracts before another
implementation campaign. No selected frontier is changed.
