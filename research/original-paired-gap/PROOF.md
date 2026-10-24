# A paired gap from a monomial square

## General typed theorem

Let Q be an invertible operator on data fields. Assume that `S=Q^2`
and its inverse have legal monomial implementations with known costs.
Let F_data and F_mode be the productive output operators. Assume

```text
F_data Q = Q F_data,
F_mode R = R F_data,
F_data K = K F_mode.
```

R and K have legal coefficient operations at the stated endpoints.
Assume an admitted raw interface with input frames `(Q,I,I)` and output
frames `(F_data,F_data Q^-1,F_mode)` on `(x,y,u)`. Its two logical maps are

```text
F_core: x'=x, y'=y+(I-KR)x-Ku, u'=-u-2Rx.
B_core: x'=x-(I+KR)y-8Ku, y'=y, u'=-u-Ry/4.
```

The raw words accept arbitrary data, modes, and ordinary borrowed
helpers. They restore each ordinary helper in its stated output frame.
The theorem does not construct such a raw interface for an unspecified Q.

Use two replicas of this interface in the same chart. Extend Q, F, R,
and K by the replica identity. On the data fields define

```text
A = [[0,I],[S^-1,0]],     A^-1 = [[0,S],[I,0]],
T = Q A = [[0,Q],[Q^-1,0]].
```

Direct multiplication gives

```text
AQ=QA,    T^2=I,    SA=A^-1,
Q^-1 S A = S A Q^-1 = T.
```

These identities use only invertibility of Q. They do not use `Q^4=I`.
A acts on data fields. It need not act on the centre index, and it must
not move through R or K. F commutes with A because it commutes with Q.

The F/R/K hypotheses are necessary for the displayed physical protocol.
For example, a physical output operation `u += R X` has logical
coefficient `F_mode^-1 R F_data`. Legal monomial access to R alone does
not identify that coefficient with R. With `Q=I`, F a Hadamard, and
`R=diag(1,-1)`, it is the bit exchange matrix instead. The exact control
in `verify_algebra.py` uses an unnormalized Hadamard and its rational
inverse; the conjugation is the same. A protocol with conjugated output
coefficients requires separate legal access to those coefficients.

## Ordered forward and backward words

Start with arbitrary mode content z. Before both forward cores, apply
the physical graph `u -= R A X`. The source is Qx, so the logical
mode input is `u=z-RTx`. After both cores, first apply `u += R X`.
The frame intertwiners give

```text
v=-z-R(I-T)x,
y_1=y+x+Kv.
```

Then apply the physical graph `Y += A K U`. The logical addition is

```text
(F_data Q^-1)^-1 A K F_mode v = T K v.
```

Thus, with `G=R(I-T)` and `H=(I+T)K`, the forward map is

```text
x'=x,    v=-z-Gx,    y'=y+x+Hv.
```

Its inverse reads `x=x'`, `z=-v-Gx`, and `y=y'-x-Hv`.

Before both backward cores, apply these physical graphs in this order:

```text
X -= 8 S A K z,
u -= R Y/8.
```

The first graph must read the old mode z. Its logical source change is
`-8Q^-1 SAKz=-8TKz`. The second graph gives `u=z-Ry/8`. Substitution
in the raw backward word gives

```text
x_1=x-y-8(I+T)Kz,
u_1=-z-Ry/8,
y_1=y.
```

After both cores, apply `u += R S A Y/8`. Its logical coefficient is
`R S A Q^-1/8=RT/8`, using the frame intertwiners. Therefore

```text
x'=x-y-8Hz,    y'=y,    v=-z-Gy/8.
```

Its inverse reads `y=y'`, `z=-v-Gy/8`, and `x=x'+y+8Hz`.
These are algebraic inverses. This proof does not give free native
access to their boundary terms. The forward and backward words are not
claimed to be mutual inverses.

Only monomial access to S and its inverse is added to the coefficient
graphs. Restore every changed source or target view after its ADD group.
The monomial implementation and its complete cost remain explicit
hypotheses. The theorem permits arbitrary well-typed R and K; it does
not assume they commute with Q or impose a scalar value on RK.

## All-stage consequence

Suppose the actual stage charts transport their phases to one global Q,
and hence one global T. For any legal invertible mode gauges N_s, write

```text
G_s=N_s^-1 R_s(I-T),
H_t=(I+T)K_t N_t.
```

For every s and t,

```text
G_s H_t = N_s^-1 R_s(I-T)(I+T)K_t N_t = 0.
```

No relation between the centre images at the two stages is required.
For well-typed mode maps C_i, the residual terms
`M_i=H_(s_i) C_i G_(t_i)` satisfy `M_i M_j=0`. It follows that any
finite ordered product of `I+M_i` equals `I+sum_i M_i`, with inverse
`I-sum_i M_i`.

An intervening data map B is permitted when it commutes with T; then
`G_s B H_t=0`. An arbitrary port-mixing map need not have this property.
Unrelated stage operators T_s do not give the zero product either.
Equal per-port scalar bank operations on both replicas do commute with
T. This algebraic consequence does not prove that every proposed
controller operation has legal access or satisfies the hypotheses.

The general test uses ordered words and only adjacent Q inverse
cancellation. The exact example `Q=[[0,1],[i,0]]` has `Q^2=iI`, a unit
monomial, but `Q^4=-I`. It checks the distinction from the native
order-four specialization. The proof above establishes the general
statement; the example alone does not.

## The fixed original-complex instance

The original source provides 112 ports, eight centre rows R, and
`K=R^T/4`, with `RR^T=56I`. Each replica has 704 persistent fields.
The mode carriers are

```text
225, 226, 229, 232, 241, 242, 257, 258.
```

The full-mode core is pinned by decompressed SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
It has the raw maps above, restores the 472 ordinary helper contents,
and retains the old 5,056 native events. The mode basis changes are
pointwise scalar operations in the common input and output frames.
The exact common-frame lift and complete helper contract are inherited
from the pinned source and full-mode review. The local replay checks
the complete scalar maps, frame ledger, and native-event identity.

Each original positive line is

```text
C_p=((1+i)I+(1-i)X_p)/2.
```

Its exact square is the translation X_p, with no scalar phase. For
positive tensor depth lambda, take `Q_p=C_p^tensor(lambda)`. Then
`S_p=Q_p^2` translates each tensor coordinate by p and `S_p^-1=S_p`.
The two replicas are paired once at each tensor depth. This is not a
tensor power of a map with two replicas.

The actual full frame F is a product of commuting line operators, so it
commutes with Q and S. R and K are scalar matrices on field indices and
therefore intertwine the copies of F. The generalized A reduces to
`[[0,I],[S,0]]`. The literal physical graphs are

| Graph | Replica 0 | Replica 1 |
| --- | --- | --- |
| F input mode | u0 -= R X1 | u1 -= R S X0 |
| F output mode | u0 += R X0 | u1 += R X1 |
| F output target | Y0 += K u1 | Y1 += S K u0 |
| B input target | X0 -= 8 S K z1 | X1 -= 8 K z0 |
| B input mode | u0 -= R Y0/8 | u1 -= R Y1/8 |
| B output mode | u0 += R S Y1/8 | u1 += R Y0/8 |

Each translated source or target is translated before and after its
ADD group. Both input graphs precede both cores, and both output graphs
follow both cores. The complete wrapper is pinned by decompressed
SHA-256 `42aeb0902d8b2330f9050718c6d949993111a9fd898acad599ec867bb63a2b20`.

The native checker evaluates all 112 reviewed line recipes on all
512 spatial basis columns, including their scalar phase. The paired
scalar replay uses free ordered port lines with only the relation
`C_p^4=I`; it does not commute different port symbols through R or K.
It checks all 1,408 independent inputs, all helpers, arbitrary modes,
and both inverse orders. Since the exact line relations hold for each
tensor power, the same formal calculation proves every positive depth.

## Actual routes and matching replicas

At cover owner d, the port phase is the tensor power of `C_(dp)`.
An actual affine route is

```text
M(g,delta) f(d,z) = f(dg,z+d delta),    gp=p.
```

The translated native line at the source owner uses direction `dgp=dp`.
Address translations commute. Thus the complete affine route commutes
with the port phase, including the scalar phase, at every tensor depth.
The same route on both replicas commutes with A and T.

The source-bound checker reconstructs all nine routes for all 112 ports
from the original DATA-PHASES ledger. It verifies direction fixation,
the exact entry and exit translations, and each route inverse. The
direct reconstruction was also compared with every matrix in the prior
doubled geometry. That geometry is not a runtime dependency.

This proof requires matching replica views. A diagonal pair of different
views need not commute with the replica exchange. Nor does a common
port map A define a common action on the eight modes. In particular,
no terminal mode transport identity such as `QH=H A^-1` follows here.

## Cost and construction boundary

The literal wrapper has 2,688 physical ADDs and 448 translations in
each orientation. Its extra scalar allowances are 25,088 forward and
34,048 backward. Each full-mode core has allowance 204,418, so the
pair totals are 433,924 and 442,884. Two unchanged core profiles have
native rank mass 11,044 and 10,112 native events. There is no added
native child. The replay computes these values from the literal word.

The actual unit monomial maps have infinity norm one, while
`norm_inf(R)=56` and `norm_inf(K)=1`. The forward prefix has bound
`1+56=57`. Its suffix first updates the mode and then the target, so
the bound is `1+1*(1+56)=58`. The backward bounds are
`max(1+8,1+56/8)=9` and `1+56/8=8`.

These are wrapper bounds only. The scalar allowance excludes native
child implementation, native wrapper and address-map execution,
owner access, mode histories, displaced-owner backfills, the final
decoder, storage, precision, and recursive assembly. General monomial
implementations have their own costs and norms.

The local theorem assumes a legal pair schedule. A separate accepted
owner result is included as archival applicability evidence. The replay
does not rerun that schedule or its one-shot histories. Complete-cover
sweeps, protected active roles, and restored ordinary helper jobs are
required for that composition. The local `(I,F)` mode endpoint does
not by itself give a persistent nine-call mode path.

All-stage annihilation removes a feedback obstruction. It does not
implement the final odd-phase H/G operations, restore every arbitrary
mode in a complete controller, or give a complete supplier. Full global
closure remains unproved, and there is no kappa change.

The [general source proof](evidence/MONOMIAL-SQUARE-PROOF.md), its
[independent review](evidence/MONOMIAL-SQUARE-REVIEW.md), and the
[native review](evidence/NATIVE-REVIEW.md) state the inherited premises.
Source credit and substantial AI assistance are recorded in [NOTICE.md](NOTICE.md).
