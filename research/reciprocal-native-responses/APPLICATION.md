# Ordered three-call response and conditional cleanup

This application uses the actual `E=P R` response, with `P^2=R^2=I`
and `R-I=U L` of rank 16. Its identities keep all stage orders.
The exact matrix regression uses three distinct signed conjugations
of the actual 112-port matrices. Those conjugations test order; they
are not a replay of the actual D25 routes.

## Wrapped local responses

Write `D(A)=diag(A,A)` and

```text
L_A=[[I,0],[A,I]],       U_A=[[I,A],[0,I]].
```

For a raw forward response `E`, apply `P` on the current-I Y input
and on the completed-FULL X output. For a raw backward response
`E^-1`, use the same wrapper positions. The resulting content maps are

```text
F^P=[[P,0],[E,P]]=D(P)L_R,
B^P=[[P,-P R],[0,P]]=D(P)U_-R.
```

These wrapper positions use the pinned
[stage-view premise](frozen/lanes/bridge-access-20261017/general-stage-views-20261020/GENERAL-VIEWS.md).
No port-mixing wrapper is granted on a retired ordinary Y hole.
The common-frame `P` word costs 728 real primitives. Its address
views are separate costs.

## Three distinct stages

Set

```text
H=P1 P0,             Ptot=P2 P1 P0,
Rhat0=R0,
Rhat1=P0^-1 R1 P0,
Rhat2=H^-1 R2 H.
```

Then

```text
F2^P B1^P F0^P=D(Ptot)L_Rhat2 U_-Rhat1 L_Rhat0.
```

Let `K_i=Rhat_i-I` and `W=L_I U_-I L_I=[[0,-I],[I,0]]`. The
normalized defect is

```text
T=W^-1 L_Rhat2 U_-Rhat1 L_Rhat0=A2 A1 A0,

A0=[[I,0],[K0,I]],
A1=[[I-K1,-K1],[K1,I+K1]],
A2=[[I,-K2],[0,I]].
```

Each `A_i-I` has square zero and rank at most 16 in array units.
For the middle term, use

```text
A1-I=[-I;I]K1[I,I],       [I,I][-I;I]=0.
```

Thus `rank(T-I)<=48` in array units, or at most `48d` over a payload
field of dimension `d`. The exact inverse is the following ordered
sequence:

```text
X += K2 Y
q = K1(X+Y);  X += q;  Y -= q
Y -= K0 X.
```

The middle sum remains unchanged by the two writes. A serial
implementation must retain its complete query before either write
changes a required source.

## Source records and literal read cuts

Let `Uhat_i,Lhat_i` be the transported factors of `K_i`. In particular,

```text
Uhat0=U0,       Lhat0=L0,
Uhat1=P0^-1 U1, Lhat1=L1 P0,
Uhat2=H^-1 U2,  Lhat2=L2 H.
```

For initial logical data `x,y`, put

```text
c0=L0 x,
t=y+R0 x,       c1=Lhat1 t,
w=x-Rhat1 t,   c2=Lhat2 w.
```

Before the `Ptot` code, the output is

```text
X=-y-U0 c0-Uhat1 c1,
Y= x-Uhat1 c1+Uhat2 c2.
```

The three local rows `L0,L1,L2` have different physical read cuts:

| Record | Stored argument | Read cut |
| --- | --- | --- |
| `c0` | F0 source `X=x` | completed X, before post-`P0` |
| `c1` | B1 input `Y=P0 t` | current-I Y, before pre-`P1` |
| `c2` | F2 source `X=H w` | completed X, before post-`P2` |

In particular, `c1=L1(P0 t)`, not `L1 t`. Retaining these records
requires owned fields or a joint invertible code with a decoder for
every displaced arbitrary baseline. Later frame progress is also a
paid operation.

## Conditional endpoint cleanup

For physical inputs `X0,Y0`, let `x=q X0`, `y=Y0`, with `q=Q^-1`.
This is a coordinate definition. The retained signed terminal gives

```text
output=diag(F,F) Qhat D(Ptot) T Qhat^-1 input,
Qhat=diag(Q,I).
```

No routed code is commuted through `F`. A logical code `A` at this
endpoint needs the physical implementation `F A F^-1`.

Since each stage route is port-diagonal, `Ptot` remains supported on
the same 32 ports. Conditional on admitted completed stage views,
remove this code as follows: apply `q` on those 32 X fields, apply
`Ptot^-1` to both banks through the views, then apply `Q` to those
32 X fields. The line subtotal is 64 rank-one children. The six `P`
words cost `6*728=4368` real primitives. This does not remove `T`.

Saved records would then give the content correction

```text
X += Q(Uhat1 c1-Uhat2 c2),
Y -= U0 c0+Uhat1 c1.
```

The `Q` on the X scatter remains. Three available 16-row records do
not implement the scatter. The number `3*1792+64=5440` is only a
native subtotal under compatible raw-service and view premises. It
is not the price of a complete decoder or supplier.

## Conditional clean-reflection variant

Let `S` be the same 32 special ports and `O` the other 80. Let `Pi`
and `J0` be their coordinate projections. Here `J0` is not the metric.
Because `P` is identity on `O`, the ordinary rows of `E` equal those
of `R` and have zero diagonal. The selected set is pair-closed.

These are local response conditions for a possible clean service.
No native cleanR32 service is emitted in this package. Under that
service premise, use coordinates `x=(a,u)`, `y=(z,v)` and maps

```text
F_R(x,y)=(-z,(Rx)_O,(Rx)_S,v+(Rx)_O),
B_R(x,y)=(-z,(Rx)_O-v,(Rx)_S,v).
```

Selected exchange at both boundaries of `B_R` gives, for `w=R(z,u)`,

```text
Bswap_R(x,y)=(w_S,w_O-v,-a,v).
```

The entry types are `Qx` and `diag(Q_S,I_O)y`. The exit types are
FULL on X and selected Y, and `Fq` on ordinary Y. The selected
exchange uses equal entry types. All target baselines are arbitrary.

Each source code `diag(R_i,I)` differs from identity by rank 16.
Transport through the invertible ideal stage maps gives a complete
residual rank at most 48, in the same array sense as above. The ideal
terminal has 64 positive rank-one lines; an identity entry requires
32 further selected formation lines. Both counts exclude the
nonidentity reflection residual.

For the hidden-output test, set final X and selected Y to zero and
let final ordinary logical Y be `h`. Write `i_O` for its inclusion
into the full coordinate space. Exact reversal gives

```text
unpermuted B:
  x_initial=R0 J0 R1 i_O h,
  y_initial=(I-R1)i_O h;

selected-conjugate Bswap:
  x_initial=R0 R1 i_O h,
  y_initial=J0(I-R1)i_O h.
```

The final `R2` drops out. For `Bswap`, the hidden correction depends
on two 16-row families, `L1 i_O h` and `L0 R1 i_O h`, so its rank
is at most 32 arrays. Its selected borrowed row vanishes, but its
ordinary hidden observation remains. Normalizing the ordinary holes
would permit those reads and has a separate cost.

The exact regression attains residual rank 48 and hidden rank 32.
These are regression ranks, not lower bounds for actual routed
implementations. No unallocated record, clean service, cheap hole
reader, returned code, or complete terminal follows from this algebra.
