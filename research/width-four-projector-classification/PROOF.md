# Complete action classification at width four

## Scope and result

Work over F2 in a fixed coordinate space V = F2^4. For a matrix P, let
off(P) be P with its diagonal set to zero. Let H be a three-dimensional
subspace of the twelve-dimensional off-diagonal matrix space. Its unit
graph has an edge {i,j} if E_ij or E_ji belongs to H. Suppose that this
graph has matching number one.

The complete pool C(H) consists of all rank-one idempotents P with
off(P) in H minus {0}. Require that the sum of their images is V and
that their patterns span H. Two pools are equivalent if a single element
of GL(4,2) conjugates one unordered pool to the other.

There are exactly **386 equivalence classes**. Of these, **40 are
irreducible**. The two actions from PR7749 and PR7707 have class labels
C347 and C384. They are two of the 22 irreducible classes with four pool
members. Twelve further irreducible classes have five members, and six
have six members.

| Pool size | Reducible classes | Irreducible classes |
| --- | ---: | ---: |
| 4 | 125 | 22 |
| 5 | 148 | 12 |
| 6 | 59 | 6 |
| 7 | 12 | 0 |
| 10 | 2 | 0 |

This is an exhaustive finite classification at ambient width four. It
does not classify embeddings in larger coordinate spaces. The general
matching bound permits joint image five for reducible actions at these
parameters, so this package does not call all width-four actions global
maximizers. No paid word, supplier or new kappa follows from this census.

## Coverage of pattern spaces

A matching-one graph has an edge. A permutation of the four coordinates
can map a present directed unit to E_01. It is therefore sufficient to
enumerate all H that contain E_01. In the code, compact off-diagonal bits
follow row order, with diagonal positions omitted. Thus E_01 has code 1.

The quotient by its span has dimension eleven. Each two-space in this
quotient has a unique reduced basis with highest pivots p < q. Write

```text
a = 2^p + low,                  0 <= low < 2^p,
b = 2^q + lower bits,           0 <= lower bits < 2^q,
bit p of b = 0.
```

These ranges give each two-space once. Their total is the binary Gaussian
coefficient `(2047 * 2046) / 6 = 698027`. Lift a and b by shifting their
bits one place and adjoin the unit 1. This gives all anchored three-spaces
once. For each space, the program constructs its complete pool and tests
the matching, image and pattern dimensions. Exactly 2,070 spaces pass.

Every nonzero rank-one binary matrix is uniquely x y^T with x,y nonzero.
It is idempotent exactly when y^T x = 1. There are 15 choices for x and
eight covectors for each x, hence 120 projectors. The four coordinate
projectors have zero pattern and do not enter a pool. No pool member is
selected or omitted by a search heuristic.

The stated pattern-span requirement does not omit a full-image pool from
an ambient three-space with matching number one. If its actual pattern
span had dimension k <= 2, its unit matching number would be at most one.
The retained matching bound `2n <= 3k + nu` would give `8 <= 7`. The
checker nevertheless tests the actual pattern span directly.

## A different enumeration

The second path reads all 65,536 four-by-four binary matrices as four
rows. Rank one means that there is exactly one distinct nonzero row.
Direct matrix multiplication tests idempotence. This gives the same 120
projectors without using the factor-pair inventory.

For each pair of distinct realized patterns a,b, form span(E_01,a,b).
When its dimension is three, reconstruct the complete matrix pool. Test
its image by its columns, and test the graph and actual pattern span.
Every qualifying H occurs: extend E_01 to a basis of H with two elements
of its spanning set of realized patterns. Thus this second enumeration
is complete, although it has repetitions. Its full dictionary of pattern
spaces and matrix pools equals the first dictionary, entry for entry.

## Simultaneous conjugacy

Each qualifying pool has a basis of four of its image vectors. For each
ordered image basis B, transform every factor pair by

```text
x_new = B^(-1) x,       y_new^T = y^T B.
```

Encode a transformed pair as `16*x_new + y_new`. Sort the pool and take
the least tuple over all ordered image bases. This tuple is a complete
conjugacy invariant. A conjugacy carries the set of ordered image bases
bijectively to the corresponding set for the other pool. Conversely,
equal tuples give an explicit change of basis between the pools. This
argument uses the uniqueness of binary rank-one factor pairs.

The certificate gives a class and an image basis for every one of the
2,070 spaces. A separate row-matrix calculation checks each conjugacy
witness. Canonical tuples can contain diagonal projectors, since arbitrary
conjugacy does not preserve diagonal deletion. The certificate also gives
an original qualifying pattern space and pool for each class. These are
the representatives to use when the coordinate pattern contract matters.

For a further check, the matrix path examines all 65,536 binary matrices
and retains exactly 20,160 invertible matrices. Gaussian row operations
compute their inverses; both inverse products are checked. For each of
the 386 representative pools, the code computes every conjugate by direct
matrix multiplication and takes its least tuple in a fixed matrix order.
All 386 minima differ. The stabilizer count and orbit size are retained,
with their product equal to 20,160. This proves that the partition has no
false split; the explicit witnesses prove that it has no false merge.

## Irreducibility

The matrix path constructs all 67 subspaces of F2^4 by spans of subsets
of its fifteen nonzero vectors. It tests every vector of every subspace
under every member of each representative pool. A class is irreducible
exactly when it has no invariant subspace of dimension one, two or three.
The certificate gives the count in each dimension. Forty classes pass.

The source verifier from PR7749 runs unchanged. Both predecessor pools
also occur literally in the anchored census. They have distinct complete
conjugacy invariants, so the new result includes the earlier trace-pair
separation without using that weaker invariant as a classification test.

## Evidence and limits

The finite coverage arguments above, two complete enumeration paths,
explicit witnesses and full-group comparison establish the stated scope.
The JSON certificate contains every qualifying anchored space, every
class representative and every orbit and invariant-subspace count. The
verifier reconstructs the certificate rather than trusting its totals.

The paths share the mathematical definitions and fixed width. They do not
constitute independent human review or formal-kernel acceptance. Larger
ambient embeddings, paid group-algebra words, integral exponent relations,
native realization, dirty-register restoration and a complete recursive
bill remain open. All five framework assumptions remain unchanged.
