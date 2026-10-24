# Raw selected subsets with a dyadic borrowed block

## Result and scope

The raw physical selected swap extends from one eight-port centre minor to
any selected subset S. The borrowed-input block of the resulting completed
X bank is a unit if and only if an explicit eight-dimensional matrix is a
unit. This criterion applies to the actual clean-J backward local.

For a union of k complete orthogonal centre minors, the criterion is that
`k-13` is a nonzero signed power of two. Among `1 <= k <= 14`, the admitted
values are 5, 9, 11, 12, and 14. The first admitted case uses forty selected
ports. It needs no new native child. Each selected Y field contains its
original selected X input in the full frame.

A scalar circuit on completed X makes the five-minor borrowed block exactly
`diag(Q_S^-1,-I_U)`. The circuit uses no scratch array and no native child.
This removes the odd-prime obstruction of the one-minor raw local. It does
not prove a complete global controller or a free final decoder. In
particular, an inverse Q on borrowed selected data is an operator, not a
free scalar coefficient.

Five is minimal among unions of complete eight-port minors. No claim of
minimum cardinality among arbitrary selected subsets is made.

## General subset theorem

Use the exact matrices of the centre-free core:

```text
J = I - K R,
K = R^T/4,
R K = 14 I_8.
```

Let S be any subset of the 112 ports, and let U be its complement. Set

```text
H_U = I_U - K_U R_U,
T_S = I_8 - R_U K_U = R_S K_S - 13 I_8.
```

All coefficient rings below contain the dyadic rationals. They can also
contain the exact native array operators. The two matrices H_U and T_S
are units at the same time. Their inverses then satisfy

```text
H_U^-1 = I_U + K_U T_S^-1 R_U,
T_S^-1 = I_8 + R_U H_U^-1 K_U.
```

Expand both products to verify these identities. For example,
`(I-KR)(I+K(I-RK)^-1R)=I`. The products are ordered. No Q operator is moved
through K or R.

Write input data as `x=(a,u)` and `y=(b,v)`. The physical input fields are
`X_p=Q_p x_p` and `Y_p=y_p`. The core output fields are `X_p=F x'_p` and
`Y_p=F Q_p^-1 y'_p`. Swap physical X and Y at each p in S, then run the
unchanged clean-J backward core. The exact logical map is

```text
X_S = Q_S^-1 b - (I_S-K_S R_S) Q_S a + K_S R_U v,
X_U = u + K_U R_S Q_S a - H_U v,
Y_S = Q_S a,
Y_U = v.
```

To prove the map, the physical swap gives logical input
`x_pre=(Q_S^-1 b,u)` and `y_pre=(Q_S a,v)`. Substitute these values into
`X=x_pre-J y_pre`, `Y=y_pre`.

The native Q operators and F are linear combinations of the same spatial
translations. Thus they commute. The physical selected output is
`F Q_S^-1 Q_S a=F a`. This is the original selected input in the full
frame.

The map from borrowed y to completed X is

```text
M_S = [ Q_S^-1    K_S R_U ]
      [    0        -H_U  ].
```

The diagonal Q block is a unit. An upper block elimination therefore
reduces M_S to `diag(Q_S^-1,-H_U)`. Thus M_S is a unit if and only if T_S
is a unit. This is an operator-ring statement. It does not need a
commutative determinant for the Q blocks.

For the finite array realization, H_U is a scalar matrix tensored with the
identity on each spatial array. A failed scalar rank condition therefore
means missing array channels, not just a single scalar coefficient.

## Complete-minor classification

A complete minor A has eight ports and `R_A K_A=I_8`. The checker gives a
partition of the actual 112 ports into fourteen such minors. Its first five
minors are the five used by the prior protected five-minor logger.

If S is a union of k minors, then

```text
R_U K_U = (14-k) I_8,
T_S = (k-13) I_8,
H_U^-1 = I_U + K_U R_U/(k-13).
```

For k below 14, U contains a complete minor. Thus K_U is injective and R_U
is surjective over the dyadic coefficient ring and over every field of odd
characteristic. The centre image has eigenvalue `k-13` under H_U. The
kernel of R_U has eigenvalue one.

| k | k-13 | Result over dyadic coefficients |
|---:|---:|---|
| 1 | -12 | Fails modulo 3 |
| 2 | -11 | Fails modulo 11 |
| 3 | -10 | Fails modulo 5 |
| 4 | -9 | Fails modulo 3 |
| 5 | -8 | Unit |
| 6 | -7 | Fails modulo 7 |
| 7 | -6 | Fails modulo 3 |
| 8 | -5 | Fails modulo 5 |
| 9 | -4 | Unit |
| 10 | -3 | Fails modulo 3 |
| 11 | -2 | Unit |
| 12 | -1 | Unit |
| 13 | 0 | Singular over the rationals |
| 14 | 1 | U is empty; unit |

If an odd prime divides k-13, the eight columns of K_U are independent
kernel channels modulo that prime. Conversely, `H_U w=0` implies
`w=K_U R_U w`. The kernel is contained in the image of K_U. Its exact
nullity is therefore eight array channels. Each Q remains a unit modulo
an odd prime: its exact Gaussian dyadic kernel and its inverse reduce to
mutual inverses. For primes without a square root of minus one, use the
quadratic field extension.

This proves a restriction on the stated raw local and on controllers that
must invert this borrowed block. It does not exclude a controller that
reads additional ordinary Y information, changes its borrowed encoding,
or uses a different local map.

## A circuit for H and its inverse

Suppose U contains a complete pivot minor A, and put W=U minus A. Define

```text
L = K_A R_W,
M = K_W R_A,
d = k-13.
```

For a union of k selected minors, `L M = -d I_8`. Let
`T(a,w)=(a+Lw,w)`. Direct multiplication gives

```text
H_U = T^-1 [ d I_8   0 ] T.
           [  -M    I_W]
```

The following operations implement H_U:

```text
a += L w
w -= M a
a *= d
a -= L w.
```

The inverse circuit is

```text
a += L w
a *= 1/d
w += M a
a -= L w.
```

For an admitted k, each SCALE is a signed power of two. All ADD
coefficients are dyadic. These are reversible operations on the actual
arrays. There is no zero-state assumption, private query record, or new
native call. The checker runs both inverse orders on every array column.

For k=5, use the forty selected ports in the receipt and the retained pivot
minor `[4,11,12,17,90,97,99,104]`. Then d=-8. The inverse circuit has scalar
cost 7744 under the existing scalar invoice.

## A diagonal borrowed block for five minors

After the raw local, apply H_U^-1 to completed X_U. Then add
`K_S R_U X_U` to completed X_S. Put

```text
c = R_S Q_S a + R_U u.
```

The result is

```text
X_S = Q_S^-1 b - Q_S a - K_S c/8,
X_U = u - v - K_U c/8,
Y_S = Q_S a,
Y_U = v.
```

For example, `R_U H_U^-1 = -R_U/8`. Substitute this identity into the
selected upper map to obtain the displayed formula. All selected Q
operators remain next to their own inputs.

The upper map can use the live pivot query in the inverse circuit. After
`a += Lw` and `a *= -1/8`, the pivot holds
`K_A R_U H_U^-1 original_X_U`. At that point, add `K_S R_A a` to X_S, then
finish the inverse circuit. The scatter has 160 nonzero ADDs and scalar
cost 1600. The fused completed-X circuit has scalar cost 9344. This
factorization was also derived in the new-core transfer lane.

The old-core local invoice is:

| Operation | Scalar cost | Added native mass |
|---|---:|---:|
| Retained clean core | 202138 | 5522 total |
| Forty physical swaps | 1040 | 0 |
| Fused completed-X map | 9344 | 0 |
| Complete local | 212522 | 0 beyond the core |

The response of X to `z=(Q_S a,u)` is
`diag(-I_S,I_U)+K R/d`. Its eight-dimensional determinant factor is
`(1-k)/d`. At k=5 this is one half, so this response matrix is also a
dyadic unit. This observation concerns completed-X scalar algebra. It
does not make a mixed-frame input change free.

## Exact check and remaining work

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/check_raw_minor_subsets.py
```

The final status is

```text
PASS_RAW_MINOR_SUBSET_UNITS
```

The checker pins the clean core, interface, canonical word, and ordered
operator utility. It checks the fourteen actual minors, all fourteen raw
local variants on all 712 formal input columns, every selected physical
output, the exact scalar H factorizations and both inverse orders, the
odd-prime kernel witnesses, and both forms of the five-minor completed-X
map. It also checks three negative controls.

All 480 logical helper values return under the inherited native endpoint
and wrapper contract. The eight owned private arrays return to zero. The
new boundaries do not touch any helper. The full physical core proof is
inherited; this is not a new unframed physical identity test on helper
arrays.

The complete global controller, final decoding of Q-coded selected data,
actual owner views and phases, and the full recursive invoice remain open.
The result gives no new complete kappa value. It supplies a zero-new-native
local mechanism that removes the one-minor odd-prime restoration barrier.

The first five minors and the source inverse use the protected five-minor
logger and controller work. The raw selected operator convention uses the
raw backward and forward locals in this lane. The coordinated campaign
identified the complete-minor escape and the fused pivot scatter. This
work was produced with AI assistance. Source pins and the literal packet
hash are in `RAW-MINOR-SUBSETS.json`.
