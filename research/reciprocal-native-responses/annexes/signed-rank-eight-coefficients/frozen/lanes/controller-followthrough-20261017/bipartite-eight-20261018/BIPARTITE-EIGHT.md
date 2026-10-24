# Eight selected ports with dyadic inverse gauges

This packet changes the signs of four of the eight six-mode components
in the native 48-port response. The selected and ordinary principal
blocks are both dyadic units. Only eight ports are selected. The native
core has the same children as the preceding response. This result does
not yet give a complete supplier or a terminal decoder.

The earlier exclusion of all sets of at most nine ports applies to the
fixed positive component response. The response in this packet is
different. No conclusion of that exclusion is changed.

## The signed response

Use the exact pair columns and centre rows in the frozen
`../partial-orthogonal/SYMMETRIC-FAMILY.json`. Each vertex `v` has six
orthogonal signed pair columns of squared norm two. Let `P_v` be the
orthogonal projector onto their span. Let `K_v` be their sum, as a row.
The projectors are orthogonal and sum to the identity on 48 ports. Also,

```text
K K^T = 12 I_8,
P_v K_w^T = delta(v,w) K_w^T.
```

Put `alpha=(1,-1,1,-1,1,-1,1,-1)` and `D_alpha=diag(alpha)`. Define

```text
G = sum_v alpha_v P_v,
J = G - K^T D_alpha K / 2.
```

On each physical pair, the two component projectors are the sum and
difference projectors. Thus `G` is a signed permutation of physical
ports. If the signs at the two endpoints agree, it is a signed identity
on that pair. If they differ, it is a signed exchange. In particular,
`G^2=I` and `G K^T=K^T D_alpha`.

The inverse and determinant on this block are

```text
J^-1 = G - K^T D_alpha K / 10,
det(J) = 5^8.
```

These formulas follow on the six-dimensional range of each `P_v`.
There are five eigenvalues `alpha_v` and one eigenvalue `-5 alpha_v`.
The full response is not a dyadic unit. This is not needed for the
principal-block interface below.

The other 64 ports retain exactly the negative Hadamard response from
the preceding packet. Its square is `4I`. There is no coupling between
these 64 ports and the 48-port block.

## The eight selected ports

Select, in this order,

```text
S = [0, 7, 15, 36, 42, 46, 79, 89].
```

The corresponding selected graph is two unbalanced four-cycles, on
vertices `0,1,2,3` and `4,5,6,7`. Each edge crosses the sign partition.
Only one physical port from each of these eight pairs is selected.
Consequently `G_SS=0`. The square centre minor `K_S` has determinant
`-4` and is a dyadic unit.

Let `L=J_SS` and `H=J_UU`, where `U` contains the other 40 ports. Then

```text
L = -K_S^T D_alpha K_S / 2,
(J^-1)_SS = L/5,
det(L) = 1/16.
```

Jacobi's complementary principal-minor identity gives

```text
det(H) = det(J) det((J^-1)_SS) = det(L) = 1/16.
```

Both `L` and `H` have dyadic entries and dyadic-unit determinants. Their
inverses therefore have dyadic entries. The checker forms the complete
inverse matrices and checks both inverse orders exactly.

Eight is the minimum possible selection size within this sign family.
For any component signs, every entry of `J^-1` lies in
`(1/5) Z[1/2]`, and `det(J)` is a signed dyadic unit times `5^8`.
For a selected set of size `s<8`, Jacobi's identity therefore puts
`det(J_UU)` in `5^(8-s) Z[1/2]`. It cannot be a dyadic unit. This proof
does not constrain response families beyond the stated component signs.

## A scalar ordinary gauge with no extra storage

Let `T=G(S)` be the eight physical partners of `S`. Let `R` contain the
remaining 32 ordinary ports. The packet uses sorted physical port order
for both sets. Since `G` is an involution, it is zero on the `T,T` and
`T,R` blocks, and its `R,R` block `G_R` is a signed permutation.
The square matrix `K_T` is a dyadic unit.

The following six steps implement `H` on arbitrary ordinary data
`(t,r)`. In the middle of the word, the eight fields at `T` hold centre
coordinates. They are data fields, not additional clean workspace.

```text
t <- K_T t
t <- t + K_R r
t <- -D_alpha t/2
r <- G_R r
r <- r + K_R^T t
t <- K_T^T t
```

Expansion gives

```text
t_final = -K_T^T D_alpha (K_T t + K_R r)/2,
r_final = G_R r - K_R^T D_alpha (K_T t + K_R r)/2.
```

This is exactly `H`. Every factor is a dyadic unit. Reverse the steps
and invert each factor to obtain `H^-1`. The emitted word includes every
signed exchange. It uses no owned centre field and no native child.

## The data interface

Write the 48-port response in blocks as `J=[[L,B],[D,H]]`. The retained
selected exchange, raw backward core, ordinary `H^-1` gauge, and upper
subtraction of `B` give the data map

```text
A = [[-L + B H^-1 D, -B H^-1],
     [-H^-1 D,       H^-1]].
```

Its inverse and determinant are

```text
A^-1 = [[-L^-1,    -L^-1 B],
        [-D L^-1,  H - D L^-1 B]],
det(A) = (-1)^8 det(L)/det(H) = 1.
```

An explicit factorization is

```text
A = [[I,-B],[0,I]] diag(-L,H^-1) [[I,0],[-D,I]].
```

The checker emits these two shears, the eight-port factor `-L`, and the
ordinary inverse word. It also computes an independent exact elimination
of `A` over the dyadic ring. The two resulting maps agree on all input
columns. All four emitted gauges act as the identity on the separate
64-port block; its gauge is a separate physical-boundary obligation.

| Common-frame gauge | Real scalar primitives | Extra owned fields | Native children |
| --- | ---: | ---: | ---: |
| `H` | 1,648 | 0 | 0 |
| `H^-1` | 1,648 | 0 | 0 |
| `A` | 4,720 | 0 | 0 |
| `A^-1` | 4,720 | 0 | 0 |

For clarity about the selected phase, with logical input
`x=(a,u), y=(b,v)` and selected intrinsic operator `Q`, the corresponding
backward interface has data part `A(Qa,u)` and borrowed part `(Q^-1 b,-v)`.
The selected retired Y carries `Qa` in its logical hole representation.
This is physical completed `a`, not a free conversion of `Qa` to `a`.
The packet does not assume that `Q` commutes with `A`, `B`, or `D`.

## Native word and checks

Only scalar transfer coefficients in the pinned one-way core are changed.
All native child records remain byte-identical. The exact replay checks
both providers and both directions on all 640 independent input columns.
It checks restoration of all 408 arbitrary borrowed helper fields,
all 91 private zero buffers, and all eight owned C fields.

The core costs 87,360 real scalar primitives, has 3,507 native children,
and has native rank mass 5,073 in each direction. Full boundary gauges,
source access, inter-stage transport, decoder phases, and recursive
children must still be charged in a complete supplier.

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/bipartite-eight-20261018/check_bipartite_eight.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/bipartite-eight-20261018/check_bipartite_eight.py
```

Both commands must print `PASS_BIPARTITE_EIGHT_NATIVE_AND_GAUGES` and
produce byte-identical receipts and payloads. `FREEZE.json` records the
source, checker, proof, receipt, and native payload hashes.

This is AI-assisted research. It builds on the oblique-native interior
response, the controller lane's pair geometry and structured centre
response, and the new-core-transfer native replay. The bridge-review
lane supplied the six-step ordinary gauge and the general data-interface
inverse. The budget-geometry lane independently derived the sharp
eight-port lower bound for this sign family. This packet makes no kappa
or frontier claim.
