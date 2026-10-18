# Heterogeneous rank volume and minimum-stage rigidity

Work over an arbitrary field F, with n a positive integer. The state space is the direct sum of two
n-dimensional banks. The paid operations are cross shears

```
U(K) = [[I,K],[0,I]],       L(K) = [[I,0],[K,I]],
```

with rank charge `r=rank(K)`. Between calls permit arbitrary invertible
block-diagonal bridges `diag(B,C)`. The required endpoint is an invertible
block-off-diagonal matrix `E=[[0,V],[W,0]]`; V and W are invertible. This is an
exchange up to invertible changes of coordinates inside each bank. The endpoint
is measured before any separately designated final exchange, as in PR743.

**Theorem.** If the paid call ranks are `r_1,...,r_m`, then

```
sum_i r_i >= 2n + max_i r_i.
```

This is a lower bound in the stated linear interface, not a claim that an
arbitrary rank profile satisfying it is realizable.

## Potential with one distinguished first call

For current matrix `M=[[A,B],[C,D]]`, let
`Phi(M)=rank(A)+rank(D)`. The initial identity has potential 2n, and the
required endpoint has potential zero. Left multiplication by an invertible
block-diagonal bridge preserves both diagonal ranks.

Left multiplication by U(K) changes only the first diagonal block, from A to
`A+KC`. Since `rank(KC)<=rank(K)`, the rank inequality gives
`Phi(U(K)M)>=Phi(M)-rank(K)`. A lower shear similarly changes D to `D+KB`
and lowers potential by at most its rank charge.

Before the first paid call, the matrix is block diagonal; B=C=0. That first
call therefore leaves both diagonal blocks unchanged. Consequently

`sum_{i != first} r_i >= 2n`.

This is the distinguished-first-call argument credited to 0xjohnnydev's PR743
and the archived campaign/controller lineage. The following rotation removes
the dependence on which call happens to be first.

## Chronological rotation

Write all gates, including bridges, in chronological order
`G_1,G_2,...,G_N`, so that `G_N ... G_2 G_1=E`. Move the first gate to the
end, conjugated by E. The chronological list becomes

`G_2,...,G_N, E G_1 E^-1`.

Its product is

```
(E G_1 E^-1) G_N ... G_2
 = E G_1 E^-1 (E G_1^-1)
 = E.
```

The endpoint is unchanged, not merely conjugate to the old endpoint. Moving
a gate without its endpoint conjugation is generally wrong; finite controls
reject that operation.

An invertible block-off-diagonal E conjugates block-diagonal bridges to
block-diagonal bridges. More explicitly,

```
E U(K) E^-1 = L(W K V^-1),
E L(K) E^-1 = U(V K W^-1).
```

Both displayed coefficient maps have rank rank(K). Thus every rotation stays
in the allowed interface and preserves every paid call's rank. Repeating this
operation until a chosen paid call is first makes the distinguished-first-call
inequality applicable with that chosen rank omitted. For every j,

`sum_i r_i-r_j >= 2n`.

Choosing j of maximum rank proves the theorem. No enumeration, characteristic
two identity or analytic approximation enters this argument.

## Corollary: every minimum-stage call has full rank

Let P and v be positive integers and `n=P*v`, let every call rank be at most v, and suppose the controller uses
exactly `m=2P+1` paid calls. Put `R=max r_i`. The theorem and rank cap imply

```
2Pv + R <= sum_i r_i <= (2P+1)R,
```

so R>=v and hence R=v. Now the sum is at least `(2P+1)v`, while every one of
the `2P+1` terms is at most v. Therefore **every r_i=v**.

The result rules out replacing a first, last or interior call by a strictly
lower-rank transfer while retaining the minimum stage count and this bridge
interface. Under an explicitly rank-proportional copied-information invoice,
that particular attempted cost reduction cannot help. Rank is not silently
identified with the repository's actual geometry-dependent copied-center
price: changes to the decoder, nonlinear messages, additional connector banks,
cross-bank bridges, partial exchanges or a different endpoint remain outside
this result.

## Finite evidence and its limits

The certificate studies n=2 over F2. It explicitly enumerates GL(4,F2), its
30 nonzero cross shears and all 604,800 directed transitions. Dijkstra uses
the actual ranks 1 or 2 as edge weights, checks every Bellman inequality, and
retains predecessor equality witnesses. The exact minimum rank volume over
arbitrary call counts is 5. The exact call-count layers through five calls
have exchange minima `[none,none,none,6,6,5]`. Positive rank costs and the
global rank minimum therefore give the complete Pareto set `(3,6),(5,5)`.

Free bridges do not invalidate this finite graph model. In a word, commute
each block-diagonal bridge to the left using conjugation; this changes a
cross-shear coefficient by invertible left/right multiplication and preserves
its rank. The accumulated left bridge changes an off-diagonal endpoint to
another off-diagonal endpoint. The finite search includes all 36 such endpoints.

A separate dense-matrix implementation performs unweighted BFS using only
the 18 rank-one cross shears. Every rank-two coefficient matrix is the sum of
its two nonzero rank-one column matrices; same-direction shears compose by
adding coefficients. The resulting two rank-one calls cost exactly two, so
rank-one BFS computes the same weighted distances. It independently matches
every distance label, not just the final minimum. Cyclic conjugation is also
checked over F2, F3 and F5 with nontrivial block-diagonal bridges.

These finite checks corroborate the written theorem and catch implementation
errors. They are not formal verification of the theorem over all fields or
of any multiplication supplier.
