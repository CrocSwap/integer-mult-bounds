# A fixed quadratic space misses the rank-15 P120 pattern

Claim type: finite certificate with a scoped algebraic proof. The main result
is a restriction on one column space, not an unrestricted minimum-rank theorem.

Let V be the ascending list of integers v with 0 <= v < 512 and binary weight
3 or 7. It has 120 elements. Write x_i(v) for bit i of v, with bits numbered
0 through 8. Two vertices are orthogonal when their binary dot product is zero.
A legal one-block pattern has nonzero diagonal entries and zeros at every
ordered orthogonal pair. Symmetry is not required.

## The fixed space

For every field K of characteristic three, let U_K be the space of functions
on V spanned over K by these 36 functions:

```text
x_i + x_8 - 1,       0 <= i < 8,
x_i x_j + 1 - x_8,  0 <= i < j < 8.
```

Use this displayed order, with pairs ordered lexicographically. Let F be their
120 by 36 evaluation matrix. This is the fixed quadratic space specified by
the nine coefficient relations in unpaidmoon's #7087, expressed without the
redundant coefficient coordinates. Indeed, if the free coefficients are a_i
and b_ij for indices below 8, then

```text
a_8 = sum_i a_i - sum_(i<j) b_ij,
c = -a_8,
b_i8 = 0.
```

Thus c+a_8=0 and sum_i a_i+2a_8+2 sum_(i<j) b_ij=0 over characteristic three,
exactly the declared relations. The omitted b_78 coefficient is zero here.
The uniqueness minors below also prove that the 36 evaluation functions are
independent. The result uses this explicitly defined space, irrespective of
other representations or conventions.

## The obstruction

**Theorem.** Over every field K of characteristic three, every legal P120
pattern whose columns lie in U_K has rank at least 16. In particular, no such
pattern has rank 15.

**Proof.** Scale each column by the inverse of its diagonal entry. This preserves
rank, membership in the linear space U_K, and forced zeros, and makes the
diagonal one.

For a vertex v, coefficients z in K^36 of a normalized legal column must satisfy

```text
F[u,:] z = 0   for every u orthogonal to v,
F[v,:] z = 1.
```

`FACTOR.json` lists 16 vertices v and, for each, a coefficient vector z_v
satisfying these equations. For each v it also lists 36 allowed equation rows.
The 36 by 36 matrix of those rows has nonzero determinant in F3. Hence the
coefficient solution is unique over F3 and over every K of characteristic three.
The latter assertion follows because the same determinant is a nonzero prime-
subfield element of K. Therefore every normalized legal matrix with columns
in U_K contains all 16 displayed columns F z_v at the indicated vertices.

The artifact supplies 16 row indices for these columns. Their 16 by 16 minor
has determinant one in F3 and therefore in K. The mandatory columns are
independent, so every such matrix has rank at least 16. QED.

Only these 16 columns are needed. No classification of all rigid columns or
all legal patterns is claimed. The exact checks cover 912 legal-column
equations, 16 uniqueness determinants and the independence determinant.

## A rank-31 construction in the same space

The artifact also supplies A in F3^(120 x 31) and B in F3^(31 x 120). The checker
computes M=AB and verifies its 120 unit diagonal entries and all 6,720 ordered
orthogonal entries. It also supplies C in F3^(36 x 31); all 3,720 entries of
A=FC are checked. Consequently every column of M lies in the same fixed space.

The checker evaluates nonzero 31 by 31 minors of A and B and their corresponding
product minor in M. Their determinants are 1, 2 and 2. Hence M has rank at least
31, while the factorization gives rank at most 31. It has rank exactly 31, and
scalar extension preserves the certificate over every characteristic-three K.

This point was obtained by intersecting the legal affine column fibers in the
span of #7087's rank-32 construction with a common hyperplane. A fiber c+N meets
ker(L) precisely when L is nonzero on N or L(c)=0. This follows by cancelling
L(c) with a direction in N, or by observing that the functional is constant on
the fiber. Only the resulting point is claimed; unsuccessful search candidates
prove no lower bound. The delivered factors are the complete construction,
and checking them requires no predecessor code, Git or network.

## Consequence for the next construction

Accepting the existing clique construction in unpaidmoon's #7014, P120 has a
rank-15 legal pattern over every field. Its result is cited, not replayed here.
The new theorem shows that this rank cannot be attained with every column in
U_K. Thus a rank-15 construction must leave this particular quadratic space.
The bounds established here inside U_K are 16 <= minimum rank <= 31. Neither
endpoint is claimed optimal in that restricted problem.

The rank-31 point is not an improvement to the unrestricted window bound.
The initial broad upper-bound target was superseded by #7014; the published
scope is this fixed-space separation and its new rank-31 companion point.
The scope correction is recorded in the linked Discussion update.

## Remaining obligations

No optimal restricted rank, physical decoder, native word or recursive supplier
is constructed. Delivery, restoration, precision, stock, movement and a complete
caller are unpriced. No characteristic-zero identity follows from these finite-
characteristic factors. No new kappa or selected-frontier change is claimed.
Independent human and formal proof-kernel review are unclaimed.
