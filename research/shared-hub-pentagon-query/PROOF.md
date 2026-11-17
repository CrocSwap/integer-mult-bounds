# Two pentagons with a shared hub need nine two-coordinate queries

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let G have vertices 0,...,8 and the two cycles

```text
0--1--2--3--4--0
0--5--6--7--8--0.
```

Over any field F, let M be an 18-by-18 matrix with 2-by-2 blocks indexed by
G. Require M_ii=I_2 and M_ij=0 for distinct nonadjacent i,j. Blocks at the
edges are unrestricted, including different matrices in the two directions.
Then the exact minimum of rank_F(M) is nine.

Equivalently, nine is the smallest field-coordinate dimension of a linear
query factorization M=AB satisfying this complete ordered-block contract.
This is a statement about algebraic query dimension. It does not count native
calls, physical COPY operations, arbitrary-input restoration or recursive cost.

## Lower bound

The independent set S={1,3,5,7} has identity principal submatrix I_8.
Consequently rank(M)>=8. Suppose for a contradiction that rank(M)=8, and
write M=AB with A having eight columns and B eight rows. Write A_i for the
two-row block of A and B_i for the two-column block of B, and U_i=im(B_i).

Since M[S,S]=I_8, the four U_s for s in S form a direct decomposition of the
eight-dimensional query space. The four A_s are its coordinate projections,
after identifying each U_s with F^2 using B_s. In these coordinates, the
ordered zeros M_sj=0 imply that B_j has no component in U_s whenever s,j
are distinct nonneighbors. In particular,

```text
U_4 is contained in U_3,
U_2 is contained in U_1 + U_3,
U_8 is contained in U_7,
U_6 is contained in U_5 + U_7.
```

Every B_i has rank two because A_i B_i=I_2. It follows that U_4=U_3 and
U_8=U_7. Since 2 and 4 are nonadjacent, A_2 B_4=0, so A_2 kills U_3.
Its restriction to U_2 is invertible. Therefore the projection of U_2 onto
U_1 along U_3 is injective. Both spaces have dimension two, so that
projection is surjective.

The hub decoder A_0 kills U_3 because 0 and 3 are nonadjacent, and kills
U_2 because 0 and 2 are nonadjacent. For every u in U_1, surjectivity gives
a v in U_2 with v=u+w for some w in U_3. Hence

```text
A_0 u = A_0 v - A_0 w = 0.
```

Thus A_0 kills U_1. The same argument on 6,8 shows that A_0 kills U_5.
It already kills U_7, since 0 and 7 are nonadjacent. It therefore kills
U_1+U_3+U_5+U_7, which is the entire query space. This contradicts
A_0 B_0=I_2. Rank eight is impossible, proving rank(M)>=9.

All steps use dimensions, invertibility and the specified ordered zeros.
They apply in every characteristic and do not assume symmetric, commuting
or invertible edge blocks. The independent-set argument alone gives only
eight; the two terminal saturation steps supply the extra dimension.

## Attainment

Write the two input coordinates at vertex i as x_(i,0),x_(i,1), and encode
coordinate (i,a) as the integer 2i+a. Form the following nine unordered pairs:

```text
(0,2), (3,4), (5,6), (7,8), (9,1),
(10,12), (11,13), (14,16), (15,17).
```

Every integer 0,...,17 occurs exactly once. Each pair joins coordinates
belonging to adjacent vertices. Query the sum of the two coordinates of
each pair. To recover one coordinate, its receiver subtracts the paired
coordinate, which its read mask permits.

More explicitly, let B have nine rows and eighteen columns, with one row
equal to the indicator of each pair, and set A=B^T. Then M=AB has I_2 in
every diagonal block and zero blocks at every nonedge. The columns of A
associated with different pairs have disjoint supports, so A has rank
nine. The same is true of the rows of B. Each pair contributes the rank-one
block [[1,1],[1,1]] on its two coordinates, including in characteristic two.
Thus rank(M)=9 over every field, as required.

Independent invertible changes of the two coordinates at each vertex give
L M L^-1. They preserve identity diagonals, the complete zero mask and
rank nine. They need not preserve symmetry or make the allowed blocks
commute. These transformations give the noncommuting finite fixtures.

## What this settles

For this shared-hub two-coordinate mask, arbitrary directed block coding
cannot improve on the nine-coordinate edge-pairing construction. The graph
is triangle-free and has overlapping odd cycles. Sharing a hub therefore
does not by itself provide a block-coding saving beyond coordinate pairing
in this two-pentagon example.

The lower argument is written here rather than inferred from a finite
matrix census. The verifier checks the supplied construction, literal
decoding and the local saturated-branch identities used in that argument.
It does not exhaust all fitting matrices and does not prove the universal
claim by enumeration. Larger payloads and other shared-cycle topologies
remain open within this package.
