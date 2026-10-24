# Three calls with two unit response types

This packet extends the five-code one-pair controller. The backward
native response need not be the inverse of a forward response. It is
sufficient that each local response is a unit and that its required
scalar code is available in its own common-frame chart.

The native local maps are

```text
F0(x,y) = (x,y+E0 x),
B1(x,y) = (x-G1 y,y),
F2(x,y) = (x,y+E2 x).
```

E0, G1, and E2 are arbitrary units. They can be noncommuting routed
operators. No transpose or involution relation is needed for the
ordered content identity.

## The five code operations

Execute this word:

| Step | Operation | Required cut |
| --- | --- | --- |
| 1 | F0 | Native word |
| 2 | X <- E0 X | Completed X at stage 0 |
| 3 | Y <- G1^-1 Y | Current Y entrance at stage 1 |
| 4 | B1 | Native word |
| 5 | X <- G1^-1 X | Completed X at stage 1 |
| 6 | Y <- E2 Y | Current Y entrance at stage 2 |
| 7 | F2 | Native word |
| 8 | X <- G1 X | Completed X at stage 2 |

The successive states are

```text
after step 2: (E0 x, y+E0 x),
after step 4: (-y, G1^-1(y+E0 x)),
after step 5: (-G1^-1 y, G1^-1(y+E0 x)),
after step 7: (-G1^-1 y, E2 G1^-1 E0 x),
after step 8: (-y, E2 G1^-1 E0 x).
```

Each cancellation uses adjacent inverse factors. There is no old-stage
Y code or future-stage completed-X code. The last operation uses a
past-stage code on completed X.

The exact closure condition for this word is

```text
E2 G1^-1 E0 = I.
```

Thus a native transpose pair, with G1=E1^T in its routed chart, gives
T=E2 E1^-T E0. There is no need to first synthesize a native shear by
E1^-1. This conclusion does require an in-place scalar circuit for
G1^-1 at its own chart. A determinant statement alone is not such a
circuit or a cost certificate.

The five scalar cuts are the same cuts as those in
[the matched one-pair packet](../one-pair-current-codes-20261018/ONE-PAIR.md).
That packet pins the current matched native word. The present theorem
does not replace its source with an unproved native word.

## Physical boundary

Keep Q as the port-diagonal positive intrinsic line, and let q=Q^-1.
The physical entrance is W=diag(Q,I). The preterminal frame is
F diag(I,q). The retained signed terminal is

```text
A = [[0,Q^2],[-I,0]].
```

In the common-F coordinate chart, the complete map is

```text
A diag(I,q) [[0,-I],[T,0]] W^-1 = diag(Q T Q^-1,I),
T = E2 G1^-1 E0.
```

No response is moved through Q. An exact terminal decoder must remove
Q T Q^-1, or a new outer-operation contract must consume that code.
The direct decoder applies Q^-1, then E2^-1, then G1, then E0^-1,
then Q. Its two line passes remain 224 rank-one children on 112 fields.
This theorem does not reduce that bill.

## A small unit code for the new response search

Let J3 be the three-by-three all-ones matrix. The matrix C=I-J3 has
zero diagonal and determinant -2. Its inverse is I-J3/2. Both matrices
are dyadic units. The following in-place circuit implements C on three
arbitrary input fields a,b,c:

```text
a += b
a += c
b -= a
c -= a
a *= -2
a -= b
a -= c
```

The output is (-b0-c0,-a0-c0,-a0-b0). Reverse these operations to apply
C^-1. Each direction has six unit ADDs and one signed factor-two scale.
The existing scalar tariff charges 52 real primitives per direction.
No accumulator, private field, or initial zero is used.

Six-mode blocks diag(C,C), one for each of eight vertices, therefore
need 16 such code circuits. Their total is 832 real primitives before
the physical pair-code conjugacy and cover views. This is only the
scalar code cost. The native zero-diagonal response, its other 64
ports, phase recipes, and complete one-pair bill are separate work.

In a single common chart with E0=G1=E2=C, the residual is C, not C^3.
With different routed charts it remains E2 G1^-1 E0. The common-chart
identity does not remove the routed or intrinsic-line code.

## Verification

The checker uses an ordered free group for the native response and Q
symbols. It checks the complete content map, the physical boundary,
the direct inverse, and deletion of each of the five code operations.
It separately checks both orders of the three-field scalar inverse on
all three input columns. It imports no producer.

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/one-pair-general-units-20261018/check_general_units.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/one-pair-general-units-20261018/check_general_units.py
```

Both runs must report PASS_ONE_PAIR_GENERAL_UNITS and emit the same
receipt. No new native word, owner schedule, terminal implementation,
precision bound, or kappa improvement is claimed.
