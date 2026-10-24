# A sharp coordinate bound for unitary centre codes

The actual sixteen centre readers need at least 24 complex output
coordinates in any Gaussian dyadic unitary code. The code can mix all
112 ports and can act on additional arbitrary borrowed fields. The
lower bound does not require the code to preserve the old blocks.

The bound is attained by an explicit unitary matrix. A separate new
native-support construction in the core lane also reaches 24. The
matrix bound does not give a lower bound for native cost. It does not
exclude a nonunitary code, odd denominators, or a different output
interface.

## A finite-field bound

Let A be an r by n matrix over Z[1/2]. Let p be an odd prime. Suppose
the reduction of A modulo p has row rank r. Let the reduction of
A A^T have rank s.

Suppose an orthogonal matrix U over Z[1/2] encodes the n real inputs.
Additional arbitrary borrowed inputs are permitted: append zero
columns to A and include those columns in U. Suppose all rows of A
can be recovered exactly from m coordinates of Ux, for every input x.
Then

```text
m >= 2r-s.
```

To prove this, write T=A U^T. Exact recovery from those m coordinates
means that T is supported on those coordinates. This follows even
if the proposed recovery coefficients are not declared dyadic:
the recovery matrix is unique because U is invertible, and it is T.

Reduce all entries modulo p. Orthogonality makes U invertible after
reduction. Thus the row space W of T has dimension r and

```text
T T^T = A A^T.
```

The radical R=W intersect W^perp of the restricted bilinear form
therefore has dimension r-s. The ambient form on F_p^m is
nondegenerate. It follows that R^perp has dimension m-(r-s).
Every vector in W is orthogonal to R. Hence

```text
r = dim(W) <= dim(R^perp) = m-r+s.
```

This proves the bound. The argument does not assume that the
restricted form on W is nondegenerate. That defect gives the
additional coordinates.

For a Gaussian dyadic unitary matrix, replace each complex entry
a+ib by its real two-by-two matrix. The result is a real dyadic
orthogonal matrix. This gives the same bound for complex fields
after the real coordinate count is divided by two.

## Application to the actual supplier

Let V contain the sixteen original centre readers. The pinned
physical matrix satisfies

```text
V V* = diag(12 I8, 8 I8).
```

The first eight rows are the signed six-mode readers after the
actual pair matrix H. The pair matrices satisfy H*H=2I. Thus each
of these rows has squared norm 12. The last eight rows are the
eight disjoint eight-port sums and have squared norm 8.

The reduction of V modulo 3 has row rank sixteen. Before the
invertible pair change, its sixteen nonzero rows have disjoint
block supports. The pair matrices have determinants that are
units modulo 3. The exact checker also verifies the rank directly.

In real coordinates, A has 32 rows. Its rank modulo 3 is 32, while
the rank of A A^T modulo 3 is 16. The theorem gives

```text
real output coordinates >= 2*32-16 = 48,
complex output fields >= 24.
```

The argument still applies when U mixes the large and small port
sets. It also applies when U acts on any number of additional
arbitrary borrowed fields and the readers ignore those inputs.
The initial contents of these fields must remain arbitrary for
this extension of the statement. No claim about a promise of zero
initial contents is needed.

There is an equivalent Hermitian proof over F9. The sixteen
complex rows have an eight-dimensional radical after reduction
modulo 3. Their containing coordinate space therefore needs
dimension at least sixteen plus eight.

## Exact attainment and native access

The independently checked 32-coordinate code uses sixteen
selected physical outputs on the large sector and sixteen on the
small sector. Keep its large 48-by-48 unitary block unchanged.
On each small eight-port clique, use

```text
C8 = ((1+i)/4) H8,
```

where H8 is the real Walsh matrix. Since H8 H8^T=8I, this matrix
is Gaussian dyadic and unitary. Its first output is
((1+i)/4) times the clique sum. The other seven outputs have
zero sum. All sixteen original readers are therefore available
from sixteen large outputs and eight small outputs.

The exact checker constructs this physical 112-by-112 matrix,
verifies both unitary product orders, and verifies the full
24-coordinate centre decoder. This proves that the matrix bound
is sharp.

This direct Walsh attainment has nonzero diagonal entries on
56 ordinary small outputs. It is not an admitted ordinary native
response. The core lane found a different completion that removes
these diagonal entries. It keeps one selected centre per small
clique, modifies the Haar basis with a dyadic reflection that
fixes the sum, and permutes the seven ordinary output rows.
That extension needs its own pinned scalar and native-support
review. It is not inferred from the Walsh construction.

## Why this changes the construction target

A unitary code C satisfies C^-*=C. Thus a native forward service
and its chronological inverse-adjoint can use the same code.
The prior one-coordinate normalized centre shear does not have
this property. A unitary completion can remove that algebraic
code mismatch.

The bound identifies the cheapest possible coordinate target
within this class. Twenty-four fields are necessary; thirty-two
are not forced by the required centre information. The current
native follow-through is to form the 24-coordinate code, use its
ordinary rows in the existing native transfer paths, and test
the full forward/backward caller.

The remaining obligations are the actual frame types, all
native transfers and phases, source access, arbitrary borrowed
state, the final decoder, recursive composition, and complete
cost. Neither unitarity nor the coordinate bound resolves these
obligations by itself. No supplier exponent or kappa improvement
is claimed here.

## Independent checks and credit

The root checker imports no producer arithmetic or replay code.
It uses sparse real matrices over Fraction. It checks the pinned
112-port unitary code, both adjoint products, all sixteen readers,
all ordinary-row equations, and both literal scalar words on
1280 arbitrary real columns. The words each cost 5460 real scalar
primitives. The 1056 outside real components are unchanged.
The largest component prefix one-norms are 16 and 28; the binary
denominator height is two.

It rejects one deleted ADD in each scalar word and one changed
adjoint entry. It also checks the modulo-3 ranks and the explicit
24-coordinate Walsh attainment. It does not replay a changed
native word or a routed caller.

The consumed code payload has decompressed SHA256
fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428.
The producer is
../lanes/new-core-transfer-20261017/low-displacement-20261020/
metric-completion-20261020/UNITARY-FREEZE.json, with SHA256
f48111c62d3da6541739419111411f939f8929a6864a71afc8a0251ae9adb8f6.

Run from the workspace:

```text
python3 work/centre-encoding-campaign-20261014/root/check_unitary_completion_review.py --out <new-json-file>
python3 -O work/centre-encoding-campaign-20261014/root/check_unitary_completion_review.py --out <another-new-json-file>
```

The root lane supplied the distributed unitary normalization,
the finite-field coordinate bound, and this independent matrix
engine. The core lane supplied the actual matching placement,
physical pair binding, native row support, and complete scalar
code. The controller and earlier native packets supplied the
actual centre readers and their supports. AI assistance was used
throughout.

No PR or publication is authorized. Before a future PR description,
read /Users/aliromman/Projects/IntegerMultiplicationBounds/
PR-DESCRIPTION-STANDARD.md.
