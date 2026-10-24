# Exact scope of the retained results

The input is the actual eight-by-112 rational query matrix R at historical
source commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It satisfies
`R R^T = 56 I`. Its 112 labels q are distinct, nonzero, odd vectors in
`F_2^9`. Each column has four entries in `{1,-1}`. This package does not
replace these columns with the completed 120-root system.

## 1. Scalar-polynomial degree

Let `H_q = (X_q+Z_q)/sqrt(2)` and `Gamma_q = H_q tensor H_q` on the
doubled binary payload. A common scalar phase does not change the
conjugation used below. Define, for each positive integer lambda,

```text
A_lambda = (1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda).
```

Here r_q is the corresponding column of R. The root coefficient occurs
once. It is not raised to a tensor power.

Identify doubled payload vectors with Pauli matrices `X^b Z^a`. The
four-term expansion of conjugation by H_q gives

```text
|a,b> -> (-1)^(q dot a) |a,b>       if q dot (a+b) = 0,
|a,b> -> |a+q,b+q>                 if q dot (a+b) = 1.
```

Thus c=a+b is fixed. On the a coordinate in the block c=11, the port
operator is Z_q when `q dot c=0` and X_q otherwise. The resulting block
A has dimension 4,096 and entries in `Z[1/2]`.

The [retained certificate](frozen/work/centre-encoding-campaign-20261014/lanes/history-encoding/BELL-GRAM-DEGREE.json)
fixes integer vectors v,w by SHAKE256 seeds and gives 817 moments
`s_j=w^T A^j v` modulo 65,537. The 409-by-409 Hankel matrix
`H[i,j]=s_(i+j)` has determinant 2,984 modulo 65,537. The separate
[review](frozen/work/centre-encoding-campaign-20261014/lanes/interface-proof/BELL-GRAM-DEGREE-REVIEW.md)
derives R from the original word, builds the sparse integer matrix 4A,
and checks the same determinant by fraction-free elimination in the
prime field. It also checks every Bell sign and the common fixed vector.

This determinant belongs to `Z[1/2]`, and its reduction is nonzero,
so the determinant itself is nonzero. The first
409 Krylov vectors are therefore independent. No scalar polynomial of
degree below 409 annihilates A. The nonzero minor remains nonzero over
any characteristic-zero field extension.

The Bell identity vector is fixed by every Gamma_q. Tensor the certified
block with this vector in all remaining tensor slots. The restriction of
A_lambda to that invariant subspace is exactly A. The degree bound holds
at every positive lambda, including when the proposed polynomial depends
on lambda.

If `aI+bA_lambda` is invertible, `b != 0`, and
`q(A_lambda)=(aI+bA_lambda)^-1`, then
`(a+bt)q(t)-1` is a nonzero annihilating polynomial. It has degree at most
`degree(q)+1`. Therefore `degree(q) >= 408`.

The result does not give the exact minimal polynomial. It does not bound
rational expressions, matrix-valued encodings, general scalar ADD
circuits, or the native cost of a decoder.

## 2. The least scalar cache for diagonal updates

Let R be any complex matrix with finitely many columns. Let D_1,...,D_t
be diagonal matrices. Put two columns in the same fiber F when all D_j
have the same diagonal entries at those columns. Then the smallest row
space E that contains row(R) and satisfies `E D_j subset E` for every j
is

```text
E = direct_sum_F row(R restricted to F),
dim(E) = sum_F rank(R restricted to F).
```

Each summand has support only on F. This direct sum contains row(R) and
is invariant under every D_j. Conversely, choose a linear combination D
of the D_j whose diagonal values distinguish the finitely many fibers.
Such coefficients exist over C: a finite union of proper hyperplanes
does not fill the coefficient space. Polynomial interpolation in D gives
each fiber projector. Any invariant E that contains row(R) must contain
the projection of every row onto every fiber. The supports are disjoint,
so their dimensions add. A basis in each fiber attains the bound.

For the historical R, use sign characters `D_s[p,p]=(-1)^(q_p dot s)`.
For the ordered normal directions

```text
42, 7, 25, 52, 82, 127, 97, 76
```

the successive dimensions, including the empty family, are

```text
8, 15, 28, 44, 44, 56, 56, 56, 56.
```

The final fibers are fourteen eight-column groups of rank four. For the
first zero through nine coordinate characters the dimensions are

```text
8, 16, 31, 53, 85, 101, 112, 112, 112, 112.
```

Thus six specified coordinate characters already require all 112 source
directions in this cache model. The 56-row cache does not support the
full source-phase family. The exact rank histogram of the two-demand
stack `[R; R D_s]`, over all 512 sign characters, is two of rank eight,
sixteen of rank fifteen, and 494 of rank sixteen.

The original [phase-cache note](frozen/work/centre-encoding-campaign-20261014/lanes/native-encoding/PHASE-CACHE.md)
contains this argument and these counts. The package check independently
reconstructs the counts from R and the labels. It checks the row-basis
construction directly. This is a scalar representation result. It permits
redundant cache rows, but does not permit a source-dependent payload
operator before the cache unless the input contract is changed.

The related fixed-code graph theorem in
[PR #4750](https://github.com/CrocSwap/integer-mult-bounds/pull/4750)
tests whether one given code is invariant. The result here gives the
smallest invariant enlargement of a specified query space. The
[source-span theorem in PR #4720](https://github.com/CrocSwap/integer-mult-bounds/pull/4720)
uses a different payload-query grammar and independently gives 112 scalar
source directions. These earlier published results are not new claims
of this package. No universal novelty claim is made.
