# An eight-port signed response with dyadic principal pivots

The signed component response has a local interface that the unsigned
complete-minor response does not have. Its selected and ordinary
principal blocks are both dyadic units with eight selected ports. The
full response can still have an odd determinant.

The ordinary gauge also has an implementation that uses ordinary data
fields as its centre registers. Those fields have arbitrary input values.
No new centre bank is needed for this algebraic factorization.

## Signed pivot theorem

Let `R=Z[1/2]`. Let `K` be an `r` by `n` matrix over `R`, and let
`Lambda` be a diagonal `r` by `r` matrix with entries `1` or `-1`.
Let `G` be a symmetric signed permutation matrix. Let `lambda` be a
positive power of two. Define

`J = G - K^T Lambda K/lambda`.

Select `r` ports `S` such that `G_SS=0`. Let `T=G(S)` be their physical
partner ports. Then `T` is disjoint from `S`; it also has `r` ports.
Let `W` contain the other ports. The matrix `G` pairs `S` with `T` and
acts as a signed permutation `G_W` on `W`.

Suppose both square matrices `K_S` and `K_T` are dyadic units. Then
the two principal blocks `L=J_SS` and `H=J_UU`, where `U=T union W`,
are dyadic units. In particular,

`L = -K_S^T Lambda K_S/lambda`.

The ordinary block has the factorization

```text
H = [ I                 0 ]
    [ K_W^T K_T^-T      I ]
    diag(-K_T^T Lambda K_T/lambda, G_W)
    [ I    K_T^-1 K_W ]
    [ 0    I           ].
```

Multiplication gives each block of `G_UU-K_U^T Lambda K_U/lambda`.
The outer two factors are shears. Every diagonal factor is a dyadic
unit. This proves the claim without division by the odd determinant
of the full response.

If the additional relation `G K^T=K^T Lambda` holds, it suffices to
assume that `K_S` is a dyadic unit. The rows indexed by `S` give
`G_ST K_T^T = K_S^T Lambda`, so `K_T` is also a dyadic unit.

## Centre information carried in ordinary data fields

Write the ordinary input as `(t,w)`. The factorization has this shorter
ordered word:

```text
1. t <- K_T t
2. t <- t + K_W w
3. t <- -Lambda t/lambda
4. w <- G_W w
5. w <- w + K_W^T t
6. t <- K_T^T t
```

Its outputs are

```text
t_out = -K_T^T Lambda(K_T t_in + K_W w_in)/lambda,
w_out = G_W w_in - K_W^T Lambda(K_T t_in + K_W w_in)/lambda.
```

These are exactly the rows of `H`. Every step is invertible over `R`.
Reversing the steps gives `H^-1`. The `r` fields `t` are data fields,
not zero work fields. Their initial values enter the query and their
final values are the required `H` outputs. No value is erased.

All steps require a common physical frame. The theorem does not give
access to a retired source bank or permit fields with different frames
to be added. A literal implementation must price the two small unit
maps, both shears, the diagonal scale, and the signed permutation.

## Why the two principal units give an invertible data interface

Write a general response in selected and ordinary blocks as

`J = [[L,B],[D,H]]`.

The retained raw backward formula, with selected physical input `z`,
ordinary data input `u`, selected borrowed input `b`, and ordinary
borrowed input `v`, is

```text
X_S = q b - L z - B v,
X_U = u - D z - H v.
```

Keep the line operator `q` in its written position. First apply `H^-1`
to ordinary X, then subtract `B` times that updated ordinary X from
selected X. The borrowed response is `diag(q,-I)`. The data response is

```text
A = [ -L+B H^-1 D     -B H^-1 ]
    [ -H^-1 D          H^-1   ].
```

If `L` and `H` are dyadic units, then so is `A`, with

```text
A^-1 = [ -L^-1      -L^-1 B        ]
       [ -D L^-1    H-D L^-1 B     ],

det(A) = (-1)^|S| det(L)/det(H).
```

Both products can be checked without any commutation assumption. One
factorization of `A` is

`upper(-B) diag(-L,H^-1) lower(-D)`.

Thus the selected and ordinary principal units are sufficient. The
full response `J` need not be a dyadic unit. This is the exact place
where the signed response can avoid the earlier one-minor data kernel.
The local formula does not by itself give a routed controller or terminal
decoder.

## Actual eight-centre instance

The source is the pinned pair geometry in the preceding structured-centre
review. Its eight vertex mode spaces have orthogonal projectors `P_v`
of rank six. Their sum is the identity on the 48-port block. Each centre
row `K_v` lies in its vertex space, and `K K^T=12I_8`.

Take signs `alpha=(1,-1,1,-1,1,-1,1,-1)`, put
`Lambda=diag(alpha)`, and set `G=sum_v alpha_v P_v`. The actual pair
geometry makes `G` a symmetric signed permutation. It satisfies
`G K^T=K^T Lambda`. The signed response is

`J_alpha = G - K^T Lambda K/2 = G(I-K^T K/2)`.

Use

```text
S = [0,7,15,36,42,46,79,89],
T = [27,57,53,111,105,20,94,72].
```

The order on `T` follows the partners of the displayed order on `S`.
Exact calculation from the pair columns gives

```text
det(K_S) = det(K_T) = -4,
det(J_alpha,SS) = det(J_alpha,UU) = 1/16,
det(J_alpha) = 5^8,
det(A) = 1.
```

Every row of `K_W` has eight signed unit entries. The six-step word
therefore forms the eight centre values in eight existing ordinary
fields. The independent 40-column expansion equals the actual ordinary
principal block. The other 64 ports of the native response are a separate
Hadamard block and need their own gauge.

For a second determinant proof, use

`J_alpha^-1 = G - K^T Lambda K/10`.

Since `G_SS=0`, its selected block is `J_alpha,SS/5`. The complementary
minor identity then gives equal selected and ordinary determinants in
this 48-port instance. This identity concerns the block of 48 ports;
the complete 112-port response has the additional Hadamard determinant.

## A graph construction for more signed pivot sets

Each physical pair of ports belongs to one edge of the eight-vertex
pair graph. The two pair modes at its endpoints are orthogonal and have
norm squared two. If the endpoint signs `alpha` differ, `G` swaps the
two physical ports, with a possible sign. If the signs agree, `G` is
diagonal on that physical pair.

Choose a cycle cover using only edges whose endpoint signs differ.
Choose one physical port from each selected edge. Then `G_SS=0`, and
`K_S` is a signed incidence matrix of the cycle cover. Each column has
two signed unit entries. In a cycle of length `ell`, its determinant
is the sum of the two matching terms. It is either zero or `2` or `-2`.
Choosing the other physical port of one edge changes the relative sign
of those two terms. Thus each cycle can be made nonsingular. With `c`
cycles, `det(K_S)=+/-2^c`, which is a dyadic unit.

The selected edges cross the sign partition, so these cycles are even.
In the actual sign pattern, the cross-edge graph is `K_4,4` minus a
perfect matching. The displayed selection consists of two nonsingular
four-cycles. This explains its determinant of magnitude four and gives
a family of signed eight-port pivot sets, rather than a numerical
accident at one set.

For this fixed sign pattern, the cross-edge graph has nine cycle covers:
six single eight-cycles and three pairs of four-cycles. Each cycle gives
one independent parity condition on its port choices. The resulting
number of nonsingular selected sets is

`6 * 2^7 + 3 * 2^6 = 960`.

The checker enumerates all eight-edge covers and all port choices within
each cover. A separate peer check derives the same nine covers from the
complements of the graph's perfect matchings. This is exhaustive within
the stated cycle-cover construction. It is not an enumeration of all
eight-port subsets of the 48-port block.

## The sharp selection size in the component-sign family

The sign family retains the eight eigenvalues whose magnitude is five.
Thus its determinant on 48 ports is `5^8`, for every component sign
choice. The displayed inverse formula puts every inverse entry in
`(1/5) Z[1/2]`. For a selected set of size `s`, the determinant of its
principal inverse block lies in `5^-s Z[1/2]`. Jacobi's identity gives

`det(J_UU) in 5^(8-s) Z[1/2]`.

For `s<8`, this cannot be a dyadic unit, including when it is zero.
Therefore a dyadic ordinary inverse requires at least eight selected
ports throughout this component-sign family. The signed pivot sets
attain the bound. The same argument applies with the separate dyadic
Hadamard block present. It concerns the selection size, not the rank
of a native centre capture or the number of native children.

This graph theorem gives an algebraic construction from the stated pair
geometry. An emitted native response is still required for the chosen
component signs. A complete supplier also needs the selected physical
exchange, all frame transitions, source access, restoration, recursive
width, and total cost.

This is AI-assisted research. It uses the controller-followthrough
signed response, the oblique-native pair geometry, and the earlier
raw backward interface. The six-step ordinary factor was derived in
bridge-review and independently checked by controller-followthrough.
The sharp selection-size bound was independently derived in
budget-geometry and checked here from the inverse and determinant.
