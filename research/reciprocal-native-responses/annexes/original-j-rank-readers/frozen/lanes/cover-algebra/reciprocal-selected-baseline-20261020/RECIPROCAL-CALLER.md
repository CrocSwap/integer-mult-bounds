# A reciprocal caller with a 48-row residual

The actual 112-port response has a factorization E=P R. The matrix P
is an involution on 32 ports. The matrix R is an involution with
rank(R-I)=16. A three-call caller can keep P as a common bank code
and leave only three rank-16 shear corrections.

This is an ordered caller theorem. The actual matrix is checked
independently. A new native word, stored query records, and a complete
terminal decoder are separate obligations. Rank 48 is not a native
cost of 48.

## Source and metric

The matrix source is

```text
oblique-native-20261017/signed-metric-reciprocal-20261020/
model-normal-v2/RESPONSE.json.gz
```

Its decompressed SHA256 is
`df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0`.
The root construction is in
`root/RECIPROCAL-RANK-TWO-20261020.md`.

Write the physical row and column factors as L and U. They satisfy

```text
R=I+U L,       L U=-2I16,       P^2=R^2=I,
E=P R,        E^-1=R P.
```

The source also supplies a real diagonal matrix J with

```text
P* J P=J,      R* J R=J,      E* J E=J.
```

Its diagonal entries are 1 on 80 ports, -1/2 on 16 ports, and -1/4
on 16 ports. Thus all metric scales and inverse scales are dyadic.
The order of the inverse formulas is

```text
E^-*=J E J^-1,       E^-1=J^-1 E* J.
```

Do not replace E by an involution. In general E^2 is not I.

Every nonidentity row or column of P lies in the same 32-port set S.
The physical P has 160 nonzero entries. It is not a monomial matrix.
Its accepted common-frame scalar word costs 728 real primitives.
This cost does not include global address views.

## A local P wrapper

Let D(A)=diag(A,A), and define

```text
L_A=[[I,0],[A,I]],       U_A=[[I,A],[0,I]].
```

Assume a raw forward service has response E. Apply P to the
current-I Y input. Apply P to the completed-FULL X output. The
result is

```text
F^P = [[P,0],[E,P]] = D(P) L_R.
```

For a raw backward response E^-1, the same input and output
wrappers give

```text
B^P = [[P,-P R],[0,P]] = D(P) U_-R.
```

There is also an exact conversion from the chronological
inverse-adjoint of the whole wrapped forward word:

```text
D(J^-1) (F^P)^-* D(J) = B^P.
```

This conversion uses only physical diagonal scales. It does not
commute a port-mixing code through a hole phase. The complete
inverse-adjoint must retain the complete helper and phase contract.

The current-I pre-Y and completed-FULL post-X placements use the
standard stage-view contract. Its source is
`bridge-access-20261017/general-stage-views-20261020/GENERAL-VIEWS.md`,
SHA256 `5da866eb2802e8a30ea77d2f88877b5005a2eb04632514c897a426e76277db2e`.
No wrapper is granted on a retired ordinary Y hole.

## Three different stages

Keep all stage labels. Set

```text
H=P1 P0,                     Ptot=P2 P1 P0,
Rhat0=R0,
Rhat1=P0^-1 R1 P0,
Rhat2=H^-1 R2 H.
```

Then

```text
F2^P B1^P F0^P
  =D(Ptot) L_Rhat2 U_-Rhat1 L_Rhat0.
```

This identity holds over an ordered operator ring. It uses no
commutation between stages.

Write K_i=Rhat_i-I. Each K_i has at most 16 array columns. Let

```text
W=L_I U_-I L_I=[[0,-I],[I,0]].
```

The normalized defect is

```text
T=W^-1 L_Rhat2 U_-Rhat1 L_Rhat0=A2 A1 A0,

A0=[[I,0],[K0,I]],
A1=[[I-K1,-K1],[K1,I+K1]],
A2=[[I,-K2],[0,I]].
```

Each A_i-I has square zero. For A1 this follows from the ordered
factorization

```text
A1-I=[-I;I] K1 [I,I],
```

because [I,I][-I;I]=0. Therefore

```text
rank(T-I) <= rank(K0)+rank(K1)+rank(K2) <=48.
```

For a payload field of dimension d, the bound is 48d. It is an
array-rank bound, not a count of scalar coordinates.

An exact inverse applies these operations in this order:

```text
X += K2 Y
q = K1(X+Y);  X += q;  Y -= q
Y -= K0 X.
```

The middle sum X+Y is unchanged by its two writes. A serial
implementation must use the complete query before either write
changes its required source.

## Three queries at actual source cuts

Factor the transported K_i as Uhat_i Lhat_i, where

```text
Uhat0=U0,        Lhat0=L0,
Uhat1=P0^-1 U1,  Lhat1=L1 P0,
Uhat2=H^-1 U2,   Lhat2=L2 H.
```

For arbitrary initial logical data x,y, define

```text
c0=L0 x,
t=y+R0 x,
c1=Lhat1 t,
w=x-Rhat1 t,
c2=Lhat2 w.
```

Direct substitution gives the output before Ptot:

```text
X=-y-U0 c0-Uhat1 c1,
Y= x-Uhat1 c1+Uhat2 c2.
```

Thus the normalized defect is also

```text
T(x,y)=(x-Uhat1 c1+Uhat2 c2,
        y+U0 c0+Uhat1 c1).
```

These records have three different literal read cuts:

| Record | Actual stored argument | Read cut |
| --- | --- | --- |
| c0 | native F0 source X=x | completed X, before post-P0 |
| c1 | B1 input Y=P0 t | current-I Y, before pre-P1 |
| c2 | native F2 source X=H w | completed X, before post-P2 |

The local rows at these cuts are L0,L1,L2. In particular, c1 is
L1 applied to the stored B1 input. It is not L1 applied to the
uncoded t. This distinction accounts for P0 without an extra old
query.

No read discards an arbitrary baseline. To retain these records,
one must specify either owned fields or a joint invertible code
with a decoder for every displaced baseline. The c1 record starts
at the current-I cut. Its later frame progress is not free.

## Physical endpoint and the 32-port code

Use the all-hole raw service contract. Let Q be the diagonal
positive input line operator and q=Q^-1. For arbitrary physical
inputs X0,Y0, the first logical source is x=q X0 and y=Y0.
This is a coordinate definition; it needs no formation gate.

Let F be the complete native Fourier progress and
Qhat=diag(Q,I). The retained signed terminal, including its
old Y Q^2 maps, gives

```text
output = diag(F,F) Qhat D(Ptot) T Qhat^-1 input.
```

Do not commute F with the routed code. A logical code A at this
boundary is implemented physically as F A F^-1.

Because each stage route is port-diagonal, it does not enlarge
the 32-port support of P. Hence Ptot is the identity outside S.
The conjugated Ptot code can be removed with the following
conditional complete-FULL recipe:

1. Apply q to the 32 affected X fields.
2. Apply Ptot^-1 to both banks through the completed stage views.
3. Apply Q to the same 32 X fields.

The line subtotal is 64 rank-one children. The scalar subtotal
for the six P words is 6*728=4,368 real primitives. The stage views,
helper host, precision, and line-child admission remain separate.
The operations do not remove T.

After this code removal, a saved-record decoder would add
Q(Uhat1 c1-Uhat2 c2) to X and subtract U0 c0+Uhat1 c1 from Y,
in the complete F frame. The X scatter still contains Q on its
output ports. The availability of three 16-row records alone
does not implement those scatters.

In particular, 3*1792+64 is only a native subtotal under a
compatible raw-service premise. No 96-child residual decoder is
claimed, and no supplier or kappa gain follows from this note.

## A separate signed clean interface

Suppose a completion C satisfies C J^-1 C*=G, with physical
diagonal dyadic units J,G. Suppose its ordinary rows have a legal
zero-diagonal native response and a clean selected exchange.
For x=(a,u), y=(z,v), its clean map is

```text
F_C(x,y)=(-z,(Cx)_R,(Cx)_P,v+(Cx)_R).
```

Since C^-*=G^-1 C J^-1, its exact metric conversion is

```text
D(G) F_C^-* diag(J,G^-1)
  =(-z,(Cx)_R-v,(Cx)_P,v).
```

Selected input/output exchange then gives

```text
w=C(z,u),
Bswap_C=(w_P,w_R-v,-a,v).
```

All added metric operations are diagonal field scales. This local
identity does not identify C_s and C_t at different stages.
The selected FULL and ordinary hole types must still be kept.
It does not change the all-hole reciprocal theorem above.

## Validation and limits

The checker independently reads the actual 112-port model. It
checks both inverse orders, the metric identities, the exact P
support, the U L factor, and the scalar P word. A regression uses
three different signed conjugations of these actual matrices. It
checks all 224 two-bank columns, the ordered factorization, both
inverse orders, and the three source-record formulas. These
signed conjugations test order; they are not the actual D25 routes.

The proof covers general routed operator coefficients. The native
stage-view theorem is an inherited premise. This checker does not
emit a raw service, allocate records, restore dirty record fields,
or certify a complete decoder.

The root lane supplied E=P R and its signed metric. The oblique
lane supplied the actual 112-port model and its scalar words.
The bridge lanes supply the stage-view contract and study native
record access. AI assistance was used.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
