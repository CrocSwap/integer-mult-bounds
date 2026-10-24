# Support bounds for subspaces of the current E8 Gram code

Let R contain the 112 retained root lines as rows. The current Gram query
code is the row space of R^T. For any d-dimensional subspace of this code,
over Q, R or C, the union of its query supports has at least the following
number of ports:

| Dimension d | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Support lower bound | 53 | 76 | 92 | 100 | 106 | 109 | 111 | 112 |

These are lower bounds. Exact attainment at dimensions above one is not
claimed.

## Common zero roots and the finite chamber argument

First use a real coefficient subspace U in eight dimensions. Choose a
generic vector a in U: avoid each root hyperplane that does not contain U.
There are finitely many such hyperplanes. The roots orthogonal to a are
then exactly the roots orthogonal to every vector in U.

The saved eight simple roots are independent. Every full E8 root has an
integer expansion whose coefficients have one sign. Reflection in each
simple root permutes the 240 signed roots. These reflections therefore
generate a finite group: its permutation action is faithful because the
roots span all eight dimensions.

Let rho have dot product one with every simple root. Choose an image of a
in its finite orbit that maximizes its dot product with rho. A negative
dot product with a simple root would increase this value under reflection.
Thus the chosen image has nonnegative dot product with every simple root.
Let J be the simple roots with dot product zero.

A positive root is orthogonal to that image if and only if all its nonzero
simple coefficients are in J. These zero roots contain the simple roots
in J and lie in their span. Their span therefore has rank |J|. Reflection
preserves U's dimension, so |J| is at most 8-dim(U).

## The 256 exact subset counts

The checker tests every subset J of the eight simple roots. It counts all
120 root lines whose coefficient support is in J. It also checks that their
real span has rank |J|. The maximum counts at ranks zero through eight are

```text
0, 1, 3, 6, 12, 20, 36, 63, 120.
```

No root-system classification is used. The checker reconstructs every root
from its integer coefficients and checks all 1,920 simple reflection images.
For a query subspace of dimension d, at most the rank-(8-d) maximum can be
common zero lines among the full 120 ports. At most eight ports were removed.
The retained support therefore has at least 112 minus that maximum ports.
At d=1, the separately checked retained minimum support 53 is stronger than
this subtraction. This gives the displayed table.

## Complex subspaces and scope

For a complex coefficient subspace U of complex dimension d, let H be the
real span of the real and imaginary parts of a basis. Its complex span
contains U, so dim_R(H) is at least d. A real root is orthogonal to U if
and only if it is orthogonal to H. Apply the real argument to H. Rational
subspaces are already real subspaces. The map from coefficients to queries
is injective because R has rank eight.

Nonzero diagonal input scalings preserve every support union. Thus the same
table applies to the diagonally scaled Gram codes in the rank-eight fitting
rigidity theorem. A subspace of query rows outside those codes is not
covered. Such a larger space can use the table only for its intersection
with the Gram code. No physical circuit, cost reduction, or exponent gain
is claimed.
