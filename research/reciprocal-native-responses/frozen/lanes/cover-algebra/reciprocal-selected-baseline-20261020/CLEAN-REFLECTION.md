# A clean reflection and its two hidden query families

This note uses the same actual R=I+U L as RECIPROCAL-CALLER.md.
Let S be the 32 special ports of the reciprocal model and let
O be the other 80 ports. Write Pi and J0 for their coordinate
projections. J0 is not the signed metric J.

The matrix P is the identity on O. Therefore the ordinary rows
of E=P R equal the ordinary rows of R. They have zero diagonal.
The selected set S is closed under the actual physical pair code.
These are the local response conditions for a possible clean
R service. They do not by themselves emit that service.

## Conditional local maps

Use x=(a,u) and y=(z,v), with selected coordinates first. The
clean forward map and its metric-converted inverse-adjoint are

```text
F_R(x,y)=(-z,(Rx)_O,(Rx)_S,v+(Rx)_O),
B_R(x,y)=(-z,(Rx)_O-v,(Rx)_S,v).
```

Selected wire exchange at both boundaries of B gives

```text
w=R(z,u),
Bswap_R(x,y)=(w_S,w_O-v,-a,v).
```

The input types are Qx and Z y, where

```text
Z=diag(Q_S,I_O).
```

The output types are FULL on X and selected Y, and Fq on ordinary
Y. Both selected input fields have the same Q type. Thus the
selected exchange is a valid wire exchange under this local
contract. The initial selected target is arbitrary.

The signed metric gives C=R, G=J^-1 in the clean metric formula
of RECIPROCAL-CALLER.md. No positive-definite metric is needed.
No helper is used as a new cache.

## A rank-48 residual

Let A=F_I and B=B_I. Then

```text
F_R=A diag(R,I),       B_R=B diag(R,I).
```

Since rank(R-I)=16, each source code differs from I by rank 16.
In the three-call product F_R2 B_R1 F_R0, transport each source
code through the invertible ideal factors. The result, after
removing A B A, is a product of three conjugates of diag(R_i,I).
Each difference has rank 16. The complete residual has rank
at most 48.

The same argument applies with the selected-conjugate Bswap.
No stage matrices have been commuted. This is an array-rank bound,
not a native invoice.

For the unpermuted B, the ideal product A B A is the signed swap
W on ordinary coordinates and -W on selected coordinates. For
Bswap, its ideal product is W on both sets. These selected signs
are scalar operations.

At the ideal endpoint, the ordinary Y q factor is converted to
the required Q by Q^2, a translation. Both selected output banks
need one positive Q line each. Thus the ideal terminal has 64
rank-one lines. This count excludes the nonidentity reflection
residual. With I entry, the 32 initial selected formation lines
are an additional cost.

## Exact hidden-output test

Use a triple with arbitrary routed R0,R1,R2. Set all final X
coordinates and all final selected Y coordinates to zero. Let
the final ordinary logical Y be h. Its physical field is Fq h.
Let i_O embed h into the full 112-coordinate vector.

Reverse the last forward map. Its coded source is reconstructed
from final selected Y and final ordinary X. Both are zero, so
the input X to that last call is zero. R2 drops out exactly.

For the unpermuted B, the remaining inverse is

```text
x_initial=R0 J0 R1 i_O h,
y_initial=(I-R1)i_O h.
```

For the selected-conjugate Bswap, it is

```text
x_initial=R0 R1 i_O h,
y_initial=J0(I-R1)i_O h.
```

In the second formula, the selected initial borrowed baseline
is zero. Thus Bswap removes the hidden selected borrowed row.
It does not remove the ordinary hidden observation.

For Bswap the difference from the ideal inverse factors as

```text
x_initial-i_O h
 =U1 L1 i_O h + U0 L0 R1 i_O h,
y_initial
 =-J0 U1 L1 i_O h.
```

Only two 16-row query families occur:

```text
L1 i_O h,       L0 R1 i_O h.
```

This gives a 32-array-rank bound for the hidden correction.
The two rows must not be identified across stages. They can be
formed freely after all ordinary holes are normalized, but that
normalization is a paid operation. This note supplies no cheaper
reader.

The unpermuted B also has a 32-row bound, from

```text
R0 J0 R1 i_O-i_O
 =U0 L0 i_O+R0 J0 U1 L1 i_O.
```

It has an additional selected borrowed response
`-Pi U1 L1 i_O h`. This is why retaining an old selected data
query by that orientation does not settle arbitrary borrowed
state restoration.

## Exact check

The checker uses the pinned physical 112-port R and three
different signed conjugations. It verifies all 224 two-bank
columns, both local inverse orders, both full inverse orders,
the two hidden formulas, and the 48/32 rank bounds.

The signed stage conjugations are an order regression, not an
actual D25 route replay. In this regression the complete residual
has rank 48 and the hidden correction has rank 32. The proof
above supplies the general bounds. It does not claim that these
regression ranks are actual routed lower bounds.

The native lane has a separate census for a possible clean R
word. The controller lane owns the physical joint decoder. This
note does not claim a complete native service, a returned code,
an admitted helper schedule, or a kappa improvement.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
