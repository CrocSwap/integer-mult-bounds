# Proof map and scope

The two accepted packets address different obligations. The future bridge
proves a native access component and an ordered controller identity.
Partner retirement proves local algebra and principal-unit conditions.
Neither packet supplies a complete new supplier.

## Future D73 bridge

The [access proof](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/ACCESS.md)
and [independent review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/REVIEW.md)
use the actual eight selected ports and 104 ordinary ports. The actual
minor gives `R_A^T R_A=4I`. For `B=R_A^-1 R_U`, there are 416 nonzero
coefficients, each a signed half, with 52 per selected row. The bridge
adds the following map from a distinct source bank to a target bank:

```text
c U_t = c D_t^-1 [[0,-B],[0,I]] D_t,       c in {-1,1}.
```

First add each ordinary source to its same-port ordinary target. Then
align 104 ordinary sources and eight selected targets, apply the 416
half ADDs, and undo the 112 views. Selected source fields are not read.
No input needs to be zero, and no source is discarded.

For a port chart `[q,b_1,...,b_8]`, the route rho_t exchanges the eight
b axes with the coordinates of the future block E_t. Put
`beta_j=(weight(b_j)-1)/2 mod 2`. The future-Y translation after the
route is `q+lift_t(beta)`. For completed level h<t, the complete
quadratic phase becomes the common phase on `E_1+...+E_h+E_t`.
For h>=t, the X translation is `sum beta_j*b_j+lift_t(beta)` and
preserves the completed X frame. The independent check compares every
coefficient modulo four, including the constant. These equalities
tensor to every positive width.

The physical view A and logical content route D have different roles:
`A_(q,t) T_(q,h)=F_common D_(q,t)`. Relabeling a frame does not execute
the view. The checker binds the exact translations to the actual DATA
adapters and checks the two bank maps on all 224 arbitrary input columns.

All 96 Y cuts and 48 descending X cuts are derived from the actual event
order across 16 replicas. Every update has 104 distinct source families
and 112 distinct target families, with no source-target alias. Each
cover route is a bijection. Both views finish within the update. The
ledger covers all 69,120 helper jobs and 7,526 idle suffixes. Its mixed
policy retains all 512 selected FULL exceptions. Selected source fields
with the extra line are not read, and each selected target is still in
the required earlier phase.

One update costs `104*8+416*10=4,992` real scalar primitives and 224
affine maps. Its largest intermediate row one-norm is 27, with at most
one added binary denominator bit. These are component quantities. A
changed local word still needs its own content, frame, phase, and
arbitrary-helper proof.

## Arbitrary matched controller coefficients

The [general bridge proof](frozen/work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/GENERAL-BRIDGES.md)
uses units A_i, G_i, C and arbitrary linear maps P_i, W_i, T_i, V.
Put U_i=I-P_i and E_i=G_i A_i. The local B map and its inverse are

```text
B_i(x,y) = (U_i A_i x-y, y+P_i A_i x),
B_i^-1(w,v) = (A_i^-1(w+v), U_i v-P_i w).
```

No idempotence is needed here. Use the exact ordered preparation, plus-Y
bridge W, forward call, subtraction, minus-Y bridge T, and idle-X reset
in the source proof. The final descending X tail must use the same W.
For `z_i=sum_(j>=i) (-1)^(j-i) x_j`, the endpoint is

```text
Y_i = E_i x_i,             X_i = -y_i + (H x)_i,
(H x)_0 = C^-1 (U_0 A_0-V) z_0,
(H x)_i = U_i A_i z_i + W_(i-1) A_(i-1) z_(i-1)
          - T_(i-1) E_(i-1) x_(i-1),       i>0.
```

The descending tail cancels the preceding active Y input before that
X value is changed. Its remaining terms use P_i+U_i=I in their original
order. This proves the formula for every positive pair count.

If P_i is idempotent, the two independent suffix variables show that
later query preservation holds if and only if

```text
P_i W_(i-1)=0,             P_i T_(i-1)=0,       i>0.
```

No relation between consecutive projections is required. Pair zero
instead needs `P_0 C^-1(U_0 A_0-V)=0`. In the signed specialization the
proof uses only the same-stage relation `B_s D_s=13I`; it does not
commute graphs at different stages. Query preservation still does not
provide the original selected X suffixes needed by the response formula.
The first code and complete decoder remain separate obligations.

## Ordered partner retirement

The [partner proof](frozen/work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partner-retirement-20261018/PARTNER-RETIREMENT.md)
and its [independent review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/partner-retirement-review-20261018/REVIEW.md)
use disjoint selected sets S and T, each of size eight in the actual
packet. Let U be the complement of S and V the complement of T.
The intrinsic line at port p is Q_p, with inverse q_p. Graph entries
retain their stage, source, target, and operator order.

For arbitrary physical input `(Qh,d)`, the exact prefix and exchanges
give `z_S=d_S`, `z_U=h_U+d_U`, and

```text
Y_T = z_T,                 Y_V = q_V (J_t z)_V,
X_V = hat_h_V,             X_T = h_T + q_T (J_t w)_T,
hat_h_S = Q_S h_S,         hat_h_U = h_U,
w_T = z_T,                w_V = hat_h_V.
```

These cancellations need no inverse of J_t. Reversible ordinary
preparation needs J_t[V,V] to be a unit. The weaker preceding-stage
hypotheses are

```text
h_S = p_S + q_S b,         d_S = Q_S a,
h_U = p_U-v,              d_U = v,
p_U = H_s^-1 (u-D_s Q_S a),
```

where H_s is a unit and p_S is any data-only linear function. Then
`z_S=Q_S a` and `z_U=p_U`, so all 112 borrowed coefficients vanish
from Y. No relation between J_s and J_t is needed for that cancellation.

Let K_s have identity rows on S and rows `[D_s,H_s]` on U. Let R_t
have identity rows on T and rows of J_t on V. The physical Y code is

```text
E = diag(I_T,q_V) R_t K_s^-1 diag(Q_S,I_U).
```

It is a unit when H_s and J_t[V,V] are units. J_s, J_t, their selected
principal blocks, and the original selected data coefficient need not
be units. The full ordinary blocks in the actual current chart each
have size 104 and determinant 2^60. Their dyadic inverses pass in both
orders. The 40-port large-component determinant is 1/16; the separate
64-port block supplies determinant 2^64. The full gauge must be kept.

Put `D=diag(I_S,-I_U)` and `N=P_T q_T J_t[T,V] P_V`. Disjoint row and
column supports give N^2=0. The borrowed coefficient in X is therefore

```text
G_b = (I+N)D,              G_b^-1 = D(I-N).
```

For any X data coefficient C, the complete local map
`X=Cx+G_b y, Y=Ex` is a unit:

```text
x = E^-1 Y,               y = G_b^-1 (X-C E^-1 Y).
```

This does not remove a separate global controller requirement on C.
The optional eight-query correction acts on the full state. It cannot
be priced as only an inverse of the borrowed coefficient.

The initial selected ADD is a raw physical common-address operation.
Its fields have different logical frames. Q remains in the operator
coefficient; no inverse Q is executed by normalization notation. The
retained [boundary model](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/RAW-SELECTED-BACKWARD.md)
states that convention. This annex does not replay its native emitter.

## Endpoint and implementation limits

The physical retired code E is not FULL x. The direct FULL-data route
uses 104 normalization lines and eight final lines: 112. To reach the
required hole qx endpoint instead, the last powers are q_S^2 on S and
q_U on U. Thus the direct route uses 104 normalization lines, 104
demotion lines, and eight even-line monomial maps. The 208-line count
is not a lower bound on every decoder and is not a global construction.

The sixteen-line prefix count excludes its sixteen ADDs, the complete
ordinary gauge, routes, phases, and helper obligations. The separate
partner-F16 literal emission is not independently admitted here. Formal
operator tokens do not prove physical inter-stage access. The native
implementation must transport each block inverse consistently and bind
the same-port Q views before using the retired-code formula. Complete
finite precision, scalar and array-map cost, storage, recursive hosting,
and supplier admission remain open. No kappa improvement is claimed.
