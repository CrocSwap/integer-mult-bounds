# A route-compatible response with a dyadic centre code

The current shared-root route divides the 112 ports into three
classes. The class label r_p is the first vector r in the ordered
root space with q_p dot r=1. The order is

```text
0,30,45,51,75,85,102,120,384,414,429,435,459,469,486,504.
```

The actual classes have 64, 32, and 16 ports, with labels 30, 45,
and 75. The 64 small ports split equally between classes 30 and 45.
The 48 large ports split into 32 in class 30 and 16 in class 75.

The rank-sixteen response does not preserve these classes. Each of
its eight small cliques contains four ports from each of the two
small classes. Each large six-mode block contains four modes in
class 30 and two in class 75. A change of construction is required.

## The response

Every actual two-port pair code stays within a route class. Apply
the same pair-code matrix H as in the rank-sixteen construction.
At each large vertex, replace the six-mode block by two blocks:

```text
I_4 - d_4 d_4^T,      I_2 - d_2 d_2^T.
```

The groups are the four and two modes with the same route label.
Retain their original signs. Split each small eight-clique into its
two four-port route classes, and use I_4-11^T on each part.

There are eight large four-mode blocks, eight large two-mode blocks,
and sixteen small four-port blocks. These 32 blocks partition all
112 mode labels. If M is their direct sum, set

```text
E = H^-1 M H.
```

The full physical E has zero diagonal. Each nonzero entry E_pt
connects ports with r_p=r_t. Also,

```text
rank(E-I) = 32,
det(E) = 3^24.
```

Each block inverse is I-dd^T/(k-1), where k is two or four.
Thus the full response is a rational unit, and its only odd inverse
denominator is three. The complete inverse is checked in both
orders. The old selected-eight principal block is singular. This
packet uses empty selection: the ordinary response is the entire
112 by 112 unit.

The source graph cannot keep rank sixteen by choosing another
monochromatic eight-clique cover. All 64 maximal eight-cliques have
four ports from each small route class. The largest monochromatic
clique in the actual graph has size four. This is an exact check
against the independently reviewed complete maximal-clique list.
It is a restriction of this clique construction, not a lower bound
for all possible native responses.

## Two in-place centre codes

Apply the actual H pair code. In each signed block choose its first
mode as a pivot. The sum-and-difference code multiplies coordinates
by their signs, subtracts the pivot from every other coordinate,
multiplies the pivot by the block size, and adds all complement
coordinates to it. The pivot then holds the old signed sum.

This code C and its literal inverse each cost 1,870 old real scalar
units. They use no owned field, no new field, no native child, and
no odd division. The maximum prefix row one-norm is 8 forward and
4 backward. The inverse needs at most three extra binary
fractional bits.

The exact diagonal form is

```text
C E C^-1 = diag(-3 I_24, -I_8, I_80),
```

with the diagonal entries placed at the actual pivot ports listed
in the payload. The 32 centre coordinates occupy existing data
fields. The other 80 fields retain independent complement data.

A second code uses a rank-one reflection on each four-mode block.
For its sign vector d, let p be the pivot and let

```text
s = d - 2 d_p e_p,
S = I - s s^T/2.
```

Then S squared is I, rank(S-I)=1, and S d=2 d_p e_p.
Thus S diagonalizes I-dd^T with centre multiplier -3.
Its exact no-scratch word is

```text
x_i += d_i d_p x_p        for all i other than p
x_p *= -2
x_p += d_i d_p x_i        for all i other than p
x_p /= 2
x_i -= d_i d_p x_p        for all i other than p.
```

It costs 78 old units per four-mode block. The two-mode blocks use
the preceding pivot code. Including H, this second complete code
and its inverse each cost 2,486 units. They are dyadic and use no
additional field or native child. Their forward and inverse prefix
row one-norms are 8 and 4. Their maximum binary heights are one
and two.

The reflection code has a smaller block displacement rank. The
pivot code has a smaller scalar invoice. No decoder advantage for
the reflection code is claimed without its physical caller.

## Route and phase scope

Both complete physical codes preserve the route labels. Therefore
they commute with every field-diagonal spatial operator of the
form diag(A_(r_p)). This follows entry by entry: every nonzero
scalar coefficient connects two copies of the same A_r.

For the unshifted shared-root D11 stages, put e=511, v_p=e+r_p,
and u_(s,p)=v_p+e_(8+s), for s=1,2. The actual route has columns

```text
kappa_(s,p)(e_j) = e_j + (u_(s,p))_j u_(s,p).
```

The advance is P_kappa inverse F9 P_kappa; stage zero is F9.
If two route labels agree, their complete column lists, permutation
operators, and ordered advance operators agree. This includes
their phase, since they are the same ordered circuit. Thus the
commutation applies to these actual unshifted advances, rather
than to a nominal label alone. Added field-dependent address views
or phase corrections still require their own checks. Route
preservation does not permit Q to move through C.

For either code the current entry word C Q^2 is literal: it has
112 explicit input translations followed by the scalar code.
The spatial interpreter retains the ordered translation labels.
The formal transported code q C q, with q=Q^-1, has the same
diagonal response because the centre multipliers are scalar.
This fact does not supply a raw-output decoder or a free transition
to a subsequent input code.

The relative q-difference spaces have dimension one for the eight
two-mode blocks and dimension three for the other 24 blocks.
Only the eight two-mode spaces lie inside the common root space.
Thus a common-root gauge cost cannot be inferred from route
preservation. It requires the actual native and endpoint operators.

## Complete raw native word

The large sector uses the pinned cyclic pair flags. It changes only
the scalar transfer coefficients. The small sector uses the exact
sixteen four-cliques and their cyclic flags. Every nonzero ADD has
equal source and target frames.

The local map is

```text
F(x,y,h) = (x, y+E x, h),
B(x,y,h) = (x-E^T y, y, h).
```

The input convention is X=Qx, Y=y. The output convention is
X=F9 x' and Y=F9 Q^-1 y'. The native invoice in either direction is

```text
944 H1 + 48 H3 + 64 H5 + 64 H6,
1120 native children, native mass 1792,
4312 old real scalar primitives, 224 endpoint adapters.
```

The native prefix row one-norm is 14 in either direction.
All 640 input columns are independent. The 416 fields outside
the data banks remain unchanged. They receive no productive
advance in this word.

The emitter checks 297 fresh native operators, including their
global phases. It reuses 752 operators only after exact ordered
frame comparison with the frozen reviewed sources. The 224
endpoint adapters have the same exact endpoint frames as those
sources. Both complete provider words are serialized, read back,
and replayed. Removal of a nonzero transfer is rejected.

## Evidence

`emit_model.py` pins the pair geometry, root space, clique list,
and rank-sixteen predecessor. It checks the response and inverse,
both capture codes, all 640 columns, literal inverse orders,
route preservation, and the spatial entry code.

`emit_native.py` binds the exact model hash and emits both complete
native directions. Normal and optimized runs must give identical
payloads and receipts. The model and native freezes are separate
from a common-root gauge extension and independent review.

The construction builds on the root's route-compatible split,
the controller's common-root geometry, the independent cyclic
flags, and the native rank-sixteen word. The four-mode reflection
uses the root's rank-one capture formula. AI assistance was used.
This packet does not claim a complete supplier or kappa bound.
No publication is authorized.
