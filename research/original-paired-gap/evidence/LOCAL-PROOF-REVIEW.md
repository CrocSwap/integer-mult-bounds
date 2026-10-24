# Proof review of the original-complex paired gap

The proposed local operator identities are correct with the stated
physical order. They use the original complex line transform. No Walsh
retarget is required for these identities. This is a proof review of
the local algebra and routed zero-feedback theorem. It is not a replay
of the pending paired native packet or an owner-schedule admission.

Use two copies of the same local frame interface. Extend R and K by the
identity on the replica index. There are 112 data-port pairs and eight
mode pairs. The two copies must have matching input and output frame
operators. The complete raw cores are assumed to have the stated
arbitrary-data, arbitrary-mode, and arbitrary-helper contracts.

For each port, let Q_p be the lambda-fold tensor power of the original
native C_p. Put Q=diag_p(Q_p) on each replica and L=Q^2. The literal
identity C_p^2=X_p gives Q^4=I, L^2=I, and no scalar phase. Define

```text
A = [[0,I],[L,0]],
A^-1 = [[0,L],[I,0]],
T = Q A = [[0,Q],[Q^-1,0]].
```

Here Q on the left denotes its two-replica block diagonal extension.
Direct multiplication gives

```text
A Q = Q A,   A^2=L,   Q^2 A=A^-1,   T^2=I.
```

A is a replica exchange with a port-dependent simultaneous translation.
It is an exact monomial for every positive lambda. It generally cannot
move through R or K. In particular, A must not be applied as one common
two-by-two map to the eight mode pairs. The common full frame F commutes
with Q and L because all original complex line transforms are linear
combinations of commuting address translations. The same F on both
replicas therefore also commutes with A.

## Forward physical order

The input physical source is Qx and the input mode is arbitrary z.
The physical preload gives

```text
u = z - R A(Qx) = z - R T x.
```

The raw forward core has

```text
x_1=x,
y_1=y+(I-KR)x-Ku,
u_1=-u-2Rx.
```

At its output, X is Fx and the mode has frame F. The physical addition
`U += R X` thus gives

```text
v = -z - R(I-T)x,
y_1 = y+x+K v.
```

The physical Y frame is FQ^-1. The final physical correction
`Y += A K U` contributes

```text
(F Q^-1)^-1 A K F v = Q A K v = T K v.
```

Only the common F moved through K; A did not. Thus, with
`H=(I+T)K` and `G=R(I-T)`, the complete map is

```text
x'=x,   v=-z-Gx,   y'=y+x+H v.
```

Its inverse is `x=x'`, `z=-v-Gx`, `y=y'-x-Hv`. No mode is assumed
zero. The raw cores keep their ordinary helper contract.

## Backward physical order

First use the original mode z in the physical source update

```text
X -= 8 Q^2 A K z.
```

Since the input source frame is Q, this changes its logical value by
`-8 Q^-1 Q^2 A K z=-8T Kz`. Only after this update, set the mode to
`u=z-Ry/8`. The raw backward core gives

```text
x_1=(x-8TKz)-(I+KR)y-8K(z-Ry/8)
   =x-y-8(I+T)Kz,
u_1=-(z-Ry/8)-Ry/4=-z-Ry/8,
y_1=y.
```

Its physical Y is FQ^-1 y. The final physical update
`U += R Q^2 A Y/8` contributes

```text
F^-1 R Q^2 A F Q^-1 y/8 = R T y/8.
```

This uses `Q^2 A Q^-1=Q A=T`. It does not move A through R.
Consequently

```text
x'=x-y-8H z,   y'=y,   v=-z-Gy/8.
```

The inverse reads `y=y'`, `z=-v-Gy/8`, then `x=x'+y+8Hz`.
Using the updated mode in the first source correction would be a
different word. The displayed order is essential.

## A literal boundary lowering

The following monomial conjugations realize the physical formulas with
pointwise R/K ADDs. This is a possible lowering, not a replay or cost
certificate for the pending producer packet.

* Forward preload: apply A to X, subtract R X from the modes, then
  restore X by A inverse.
* Forward target correction: apply A inverse to Y, add K U to Y,
  then restore Y by A.
* Backward source correction: apply A to X, subtract 8Kz from X,
  then restore X by A inverse.
* Backward final query: apply A inverse to Y, add RY/8 to the modes,
  then restore Y by A.

Each orientation uses two such sandwiches on 112 port pairs, or 448
pair-monomial applications. A pair-monomial application includes its
replica exchange and its stated port translation. This count is not
an execution cost for the maps. The scalar-A Walsh protocol's 240-map
count must not be copied into this port-dependent construction.

## Actual routes and all-stage annihilation

At owner d the port operator is C_(d q_p) in each payload layer.
For an actual affine cover view,

```text
M(g,delta)f(d,z)=f(dg,z XOR d delta),
```

the two products M Q_p and Q_p M differ only by whether the native
line direction is d g q_p or d q_p. Every selected route fixes q_p,
so these are equal. The payload translation commutes with each native
line translation. Thus the commutation includes the complete phase
and holds in every tensor layer. Applying the same view to the two
replicas also commutes with A and T.

A small independent source check reconstructs the single-layer columns
from the pinned doubled DATA-PHASES payload. It verifies `g q_p=q_p`
for all 112 ports and all nine stages, or 1008 exact cases. No producer
or native compiler is imported for this check.

For actual routed data maps D_s, and any invertible mode coordinates
N_s, the factors are

```text
G_s = N_s^-1 R D_s (I-T),
H_t = (I+T) D_t^-1 K N_t.
```

For every s and t,

```text
G_s H_t
  = N_s^-1 R D_s (I-T)(I+T) D_t^-1 K N_t
  = 0.
```

No R/K commutation, equality of centre images, or special value of RK
is needed. Route commutation is needed to identify all local factors
with this one global T. If the two replicas use different views,
`diag(D_s,D_t)` need not commute with the replica exchange. That case
is not covered by this argument.

As a consequence, `N_i=H_(s_i) C_i G_(t_i)` satisfies `N_i N_j=0`
for arbitrary well-typed mode maps C_i. Hence
`product(I+N_i)=I+sum(N_i)` and its inverse is `I-sum(N_i)`.
An intervening data map B is allowed when it commutes with T, since
then `G_s B H_t=0`. This is an algebraic construction family, not a
proof that each operation in the proposed physical controller meets
that hypothesis.

## Scope and remaining obligations

The local theorem assumes two compatible core interfaces. It does not
prove that the selected asynchronous supplier calls have disjoint or
compatible physical roles. The paired input gates must precede both
cores, and the paired output gates must follow both. Shared helper
owners, mode frames, and intervening calls need a separate schedule.
The native and source-domain reviewers are checking those obligations.

The zero-feedback identity does not restore arbitrary modes by itself.
It also does not make boundary H or G access free. H and G still contain
the odd native factor Q or Q inverse. The physical conversions above
work at the specified Q/I/F/FQ^-1 endpoints; they are not automatically
available between two arbitrary full-frame fields. The final source
access, target access, restoration, map execution, storage, precision,
recursive children, and full supplier invoice remain separate.

The source raw-core contract and endpoint frames are inherited from the
pinned full-mode and phase-gap evidence. This note does not repeat a
full native kernel check, certify a paired program payload, admit the
global controller, or claim a kappa improvement. A separate OpenAI
Codex research worker made this proof review.
