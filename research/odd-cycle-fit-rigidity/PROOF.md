# Rigidity of minimum-rank width-two odd-cycle fits

produced by Nick Petalas. Apache-2.0.

## Statement

Let F be any field, n=2k+1 with k>=2, and let M be a 2n by 2n matrix
partitioned into two by two blocks indexed by Z/n. Require

    M_ii = I_2,
    M_ij = 0 when i and j are distinct and nonadjacent on C_n.

The two ordered blocks on each edge are arbitrary. They need not be
symmetric or commute. JoyboyBrian's PR5023 gives the minimum rank n for this
contract, as a special case of its unequal-width theorem. We use that rank
value as a cited predecessor result.

Define D on the two ports (i,left) and (i,right) of every vertex. Its diagonal
blocks are I_2. Its only off-diagonal nonzero entries are

    D[(i,right),(i+1,left)] = D[(i+1,left),(i,right)] = 1.

**Theorem.** If rank(M)=n, there are invertible two by two matrices L_i over
F such that, for L=diag(L_0,...,L_(n-1)),

    M = L D L^-1.

Conversely every such matrix fits the contract and has rank n. Thus all
minimum-rank fits form one orbit under independent changes of basis at the
vertices. This classifies the actual fitting matrices, not just the rank value
or one attaining construction. Ordinary transpose, never conjugate transpose,
is used in the argument.

## Adjacent intersection lines

Factor M=A B^T through F^n, with A and B of size 2n by n and full column
rank. Let U_i and W_i be the row spaces of their two-row blocks A_i and B_i.
The identity A_i B_i^T=I_2 makes both spaces two-dimensional and their mutual
coordinate-bilinear pairing perfect. Forbidden blocks make U_i orthogonal to
W_j whenever i and j are distinct nonneighbors.

For nonadjacent i,j, U_i intersect U_j is zero. A vector in the intersection
annihilates W_i by its membership in U_j, and perfect pairing on U_i forces
it to vanish. The same statement holds for the W spaces.

Fix an edge {i,i+1}. The k-1 vertices

    J = {i+3,i+5,...,i+2k-1}, with indices modulo n,

are independent and are nonadjacent to both endpoints. Their W_j form a direct
sum of dimension 2(k-1). Indeed, pairing a relation with U_j kills every other
summand and then perfect pairing kills its own summand. Both U_i and U_(i+1)
annihilate this direct sum. Therefore

    dim(U_i + U_(i+1)) <= n - 2(k-1) = 3,
    dim(U_i intersect U_(i+1)) >= 1.

Inside U_i the two intersections with its neighbors are disjoint, because
i-1 and i+1 are nonadjacent. Both have dimension at least one and U_i has
dimension two. Consequently, with H_i=U_i intersect U_(i+1),

    dim H_i = 1,
    U_i = H_(i-1) direct-sum H_i.                         (1)

This extends the C5 equality argument of Nick Petalas's PR3248. The independent
set J is the additional step for every longer odd cycle. Its use is also
consistent with the rotated one-edge-plus-isolates inequalities of PR5023.

## A dual edge basis and local similarity

Choose nonzero h_i in H_i. The row h_i annihilates W_j unless j is i or i+1.
For every other vertex j, at least one of those two endpoints is a nonneighbor
of j, which proves this assertion from the ordered zero blocks.

The n rows h_i are independent. In a relation sum c_i h_i=0, pairing with W_j
leaves only c_(j-1)h_(j-1)+c_j h_j. This vector lies in U_j and annihilates
W_j, so perfect pairing makes it zero. Equation (1) then makes both
coefficients zero. This holds for every j.

Let g_i be the dual row basis, h_i g_j^T=delta_ij. Each W_j annihilates all
h_i except its two incident edges, and has dimension two. Hence

    W_j = span(g_(j-1),g_j).

For invertible matrices L_i and T_i we can therefore write

    A_i = L_i [h_(i-1); h_i],
    B_i = T_i [g_(i-1); g_i].

The diagonal identity is L_i T_i^T=I_2, so T_i^T=L_i^-1. Pairing the displayed
dual edge bases gives exactly the block D_ij. Thus

    M_ij = L_i D_ij L_j^-1,

which proves the claimed block-diagonal similarity over every field.

## Spectral and local consequences

A permutation of ports writes D as n disjoint copies of the all-ones two by
two matrix J_2. Each copy has rank one over every field and J_2^2=2J_2.
This proves the converse, and also proves

    M^2 = 2 M,
    characteristic polynomial = x^n (x-2)^n.

If char(F) is not two, M is diagonalizable with eigenvalues zero and two, each
of multiplicity n. If char(F)=2, M is square-zero with rank n, so its Jordan
form consists of exactly n nilpotent blocks of size two. No eigenvalue or
Jordan claim requires F to be algebraically closed because these forms split
over F itself.

Every ordered edge block has rank one. At each vertex the two return maps

    P_i^- = M_(i,i-1) M_(i-1,i),
    P_i^+ = M_(i,i+1) M_(i+1,i)

are complementary rank-one idempotents. Products along two distinct consecutive
edges vanish, in either orientation. These are necessary structural conditions
on a proposed optimal fit. They do not impose symmetry in the original bases.

The normal form is constructive. Choose a nonzero vector ell_i in im(P_i^-),
and put r_i=M_(i,i+1) ell_(i+1). Then L_i=[ell_i,r_i] is invertible and gives
the displayed similarity. The canonical form proves this assertion directly:
ell_i is a nonzero multiple of its left basis vector, and r_i has exactly the
matching scale at the other end of edge i. Each edge can be normalized
independently; no cyclic scalar consistency condition remains.

## Hypotheses and limits

Odd length is essential for this rigidity. On any even cycle of length at
least six, put an I_2 block on each ordered edge of a perfect matching, zero
on all other edges and I_2 on the diagonal. Its rank is n, but its ordered
edge ranks alternate between two and zero. Local similarity preserves these
ranks, so it cannot be equivalent to D. The independent-set lower bound makes
this a minimum-rank even-cycle example.

The rank hypothesis is also essential. Replace one shared pair J_2 in D by
I_2. The odd-cycle mask still fits, its rank is n+1, and its nonzero identity
summands violate M^2=2M in every field. This is a boundary example, not an
error in the predecessor minimum-rank theorem.

The proof does not classify unequal widths, higher-rank fits or other masks.
It gives no physical basis-change routine, complete-plane binary pairing
tariff, native caller, dirty-state restoration or recursive bill. It changes
neither kappa nor the selected frontier. Finite verification corroborates the
written all-field argument; independent human and proof-kernel review remain
unclaimed.
