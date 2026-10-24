# Selected-centre unit criteria and the short normalization

This note collects the accepted algebra from the frozen source proofs.
It does not add a new search result. The native counts and source
bindings have the separate reviews in [REVIEW-INDEX.md](REVIEW-INDEX.md).

## Coefficient ring and endpoint order

Use the Gaussian dyadic ring `Z[i,1/2]`. The matrices below have real
dyadic entries. A real dyadic determinant is a unit in this ring exactly
when it is a nonzero signed power of two. Thus rational invertibility
alone is insufficient for a dyadic implementation.

Let R have eight rows and 112 columns. The actual source has
`R R^T=56I`, `K=R^T/4`, and `R K=14I`. A subscript S or U on R
restricts its columns; on K it restricts its rows. S and U partition
the ports. Let `J=I-KR`.

The physical input is `X_p=Q_p x_p`, `Y_p=y_p`. The physical output
is `X_p=F x'_p`, `Y_p=F Q_p^-1 y'_p`. The common F commutes with each
actual signed endpoint line. No rule moves Q through R, K, or a matrix
that mixes port coordinates. The proof and replay keep those products
in their stated order.

## Ordinary-block unit criterion

Define

```text
D = R_S K_S,
T = D - 13I = I - R_U K_U,
H = I_U - K_U R_U.
```

The determinant identity for rectangular products gives
`det(H)=det(T)`. Equivalently, direct multiplication gives

```text
H^-1 = I_U + K_U T^-1 R_U,
T^-1 = I_8 + R_U H^-1 K_U.
```

Thus H and T are units at the same time. The ordered inverse identities
also hold over an operator ring that contains the scalar matrices.

Write `x=(a,u)` and `y=(b,v)`. Exchange the physical X and Y fields at
the selected ports and run the clean backward core. Put `q=Q_S^-1`.
The exact logical result is

```text
X_S = q b - (I_S-K_S R_S) Q_S a + K_S R_U v,
X_U = u + K_U R_S Q_S a - H v,
Y_S = Q_S a,
Y_U = v.
```

The borrowed-Y block of X is upper triangular with diagonal blocks q
and `-H`. Its invertibility is therefore equivalent to that of T. This
does not require a determinant of the port-operator blocks.

## Full original-X response criterion

Suppose T is a unit. Apply H inverse to the completed ordinary X bank.
Then apply `X_S += K_S R_U X_U`, using the changed ordinary values.
Set `z=(Q_S a,u)` and `E=diag(-I_S,I_U)`. The complete X map is

```text
X = A z + B0 y,
A = E + K T^-1 R,
B0 = diag(q,-I_U).
```

Y retains the values in the preceding display. Since
`R E K=14I-2D`, define `W=I-D` and note that
`T+R E K=W`. The determinant identity and the ordered inverse formula
give

```text
det(A) = det(E) det(W) / det(T),
A^-1 = E - E K W^-1 R E.
```

Given invertible T, A is a unit exactly when W is a unit. The complete
two-bank word can still be a unit when A is singular. It can recover
information from Y that is absent from X alone.

For k complete orthogonal eight-port minors, `D=kI` and `T=(k-13)I`.
For `1<=k<=14`, T is a dyadic unit at `k=5,9,11,12,14`. The second
factor is `W=(1-k)I`. Both factors are dyadic units at `k=5,9`.
Thus the first such union contains five minors, or 40 ports. This is
a statement about unions of these complete minors.

## The actual 38-port witness

The selected ports are

```text
1,3,4,17,18,19,20,23,24,26,27,29,35,36,38,39,40,42,45,
60,63,66,69,74,75,77,78,84,86,88,97,99,104,105,107,108,109,111.
```

Let `G=R_S R_S^T`, let E_ij be an elementary eight-dimensional matrix,
and set

```text
V = E_02 + E_03 + E_14 + E_15,
L0 = I + V/4.
```

The selected source columns give

```text
G = 20I - 8(V+V^T) - 2VV^T,
52I-G = 32 L0 L0^T.
```

Since `V^2=0`, `L0^-1=I-V/4`, and `det(L0)=1`. Therefore
`T=-8 L0 L0^T` has a dyadic inverse and determinant `2^24`.

To check the second factor, split the two nonzero rows of V from the
other six coordinates. Its upper-right block B has `B B^T=2I_2`.
In this order,

```text
4I-G = [ -12 I2     8 B  ]
       [  8 B^T   -16 I6 ].
```

Eliminate the lower-right block. The remaining block is
`-12I2+4BB^T=-4I2`. Both pivots are dyadic units. Hence
`det(4I-G)=2^28`, `det(W)=2^12`, and `det(A)=2^-12`.
The independent root checker also constructs both full 112-dimensional
inverse identities and checks both orders. It rejects a wrong centre
constant and the omission of selected signs.

The native implementation first forms all eight current queries in
existing owned fields C0 through C7. It then applies the finite
eight-dimensional transform and scatters the result. Every query is
formed before the first data scatter. The complete review checks all
query lifetimes, frames, scalar operations, and arbitrary helper terms.
The reviewed complete word that appends A inverse costs 179,074 scalar
primitives and retains native mass 5,073.

The witness proves existence at 38. It does not prove a minimum or a
lower bound on native children. The fixed-A,T split-pair class has
different restrictions and is not the class of this witness.

## Short normalization for any selected principal unit

This section permits a different symmetric core response. Write

```text
J = [L B],
    [D H]
```

where L is the selected principal block. The raw backward word is

```text
X_S = q b - L Q_S a - B v,
X_U = u - D Q_S a - H v,
Y_S = Q_S a,
Y_U = v.
```

On `z=(Q_S a,u)`, the original-X coefficient and its inverse are

```text
C = [-L 0],       N = [-L^-1    0].
    [-D I]           [-D L^-1  I]
```

Thus the following suffix implements N at the completed common frame:

```text
X_S <- -L^-1 X_S
X_U <- X_U + D X_S
```

Its complete map is

```text
X_S = Q_S a - L^-1 q b + L^-1 B v,
X_U = u - D L^-1 q b - (H-D L^-1 B)v,
Y_S = Q_S a,
Y_U = v.
```

The order of the two steps is required. The suffix needs L inverse and
the lower shear, but not H inverse or J inverse.

When H is also invertible, let

```text
U_B = [I -B],     A = U_B diag(I,H^-1) C.
      [0  I]
```

The long normalization has suffix `A^-1 U_B diag(I,H^-1)`.
It equals `C^-1=N`. This proves equality on the entire X bank, including
all borrowed-Y terms. It also preserves the same Y bank.

## The reviewed structured words

The signed S8 source selects `[0,7,15,36,42,46,79,89]`. Its selected
block has `det(L)=1/16`. Its full ordinary block has `det(H)=2^60`.
Both inverses are dyadic. The full centre response has determinant
`5^8`; the short construction does not require its dyadic inverse.

The complete core costs 87,360 primitives, the selected physical
exchange costs 208, the selected inverse costs 192, and the lower
shear costs 1,440. The complete short normalized word therefore costs
89,200. The long word costs 99,472 and has the same complete map.
No boundary operation touches an owned or private field.

For the positive S24 response, the selected row Gram is `6I`, and
the short suffix has cost 1,608. Each row query uses six selected
fields. It scales the query by one quarter, scatters the signed value,
then recovers zero from the changed selected query. The latter query
is minus one half of the former query. Orthogonality keeps the other
row queries unchanged. The final selected negations give N.
The complete word costs `87,984+1,608=89,592` and equals the long
96,012-primitive word.

The independent reverse replay inserts zero observables before each
owned COPY and before the final reset. This checks query restoration
before reuse. It rejects a word that leaves a data-dependent residual
before CLEAR, even though that word has the same cleared endpoint.
It also rejects reversed suffix order and an incorrect movement of Q
through the borrowed-source matrix.

## Limits

The results establish exact scalar units and complete local interfaces
for the stated frozen sources. They leave routed-stage transport,
caller exterior phases, owner histories, child hosting, final decoding,
recursive precision, and complete supplier pricing open. They do not
prove a complete kappa improvement. Source generation and independent
review used separate AI-assisted calculations; no human or formal-kernel
review is claimed.
