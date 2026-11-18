# Rank-exact factors over dyadic Hamilton quaternions

## 1. Statement and meaning

Let `K=Q+Qi+Qj+Qk` be the Hamilton quaternion division ring, with
`i^2=j^2=k^2=-1` and `ij=k=-ji`. Let `L=Z+Zi+Zj+Zk`, and put
`D=L[1/2]`. For a nonempty finite `m` by `n` matrix `A` over `D`, define
its inner rank over `D` as the smallest `q` for which `A=C B`, with `C`
of size `m` by `q` and `B` of size `q` by `n`, both over `D`.

**Theorem.** The inner rank of every such `A` equals its rank `r` over `K`.
There is a terminating exact algorithm for attaining factors. If `2^s A`
has integral coordinates, with `s>=0`, the factors can satisfy

```text
A = C B,
C in Mat_(m,r)(O),       2^s B in Mat_(r,n)(O),
O = Z^4 union (Z+1/2)^4.
```

Thus each coordinate of `C` has denominator at most two, and each coordinate
of `B` has denominator dividing `2^(s+1)`. Matrix size and rank do not add
denominator bits to this bound. Rank zero has the usual empty-middle
factorization. The result concerns all finite sizes and coefficients in
this specified ring, not all rational quaternion entries or all orders.

Here `O` is the classical Hurwitz order. Its Euclidean arithmetic is not
new. This proof applies that arithmetic to the open general-response
question in Nick Petalas's PR7745 and to RQ10 in Dugongue's atlas PR5803.
The atlas's split dyadic case R07 uses integer Smith reduction; this
nonsplit Hamilton component uses Hurwitz row reduction instead. See
`CREDITS.md` for exact sources and the classical reference.

The theorem provides coefficient factors, not a physical query program.
It does not bound coefficient magnitudes or compilation time in the input
bit length. Reached-grid halving, storage, movement, ordinary coefficient
words, dirty restoration and the complete caller bill remain open. There
is no new kappa or selected-frontier change.

## 2. The order and a norm-decreasing division

Write `omega=(1+i+j+k)/2`. Then `O` has integer basis `1,i,j,omega`, since
`k=2omega-1-i-j`. This basis describes exactly the two coordinate cosets in
Section 1. Its nontrivial products are as follows; products with one are
unchanged.

| Left / right | `i` | `j` | `omega` |
| --- | --- | --- | --- |
| `i` | `-1` | `-1-i-j+2omega` | `-1-j+omega` |
| `j` | `1+i+j-2omega` | `-1` | `i+j-omega` |
| `omega` | `i+j-omega` | `-1-i+omega` | `-1+omega` |

The table and bilinearity prove closure under multiplication. Conjugation
preserves `O`. For `a=(a0,a1,a2,a3)`, its norm `N(a)=sum ai^2` is central,
positive on nonzero `a`, and multiplicative. The identity
`a conjugate(a)=N(a)` proves the inverse formula in `K`. The norm of a
Hurwitz integer is an integer: this is immediate for integral coordinates;
for four coordinates `zi+1/2`, the norm is `sum(zi^2+zi)+1`.

For any rational quaternion `x`, round it in two ways: to the nearest point
of `Z^4`, and to the nearest point of `(Z+1/2)^4`. Choose the closer result
`q`, breaking equal-distance ties toward the integer lattice. Both are in
`O`. To bound the distance, let `ui` be the absolute residual from the
integer choice. Then `0<=ui<=1/2`, and the corresponding half-lattice
residual has absolute value `1/2-ui`. Hence

```text
sum_i [ui^2 + (1/2-ui)^2] <= 1,
N(x-q) <= 1/2.
```

This includes ties and signed coordinates. The bound is attained at, for
example, `(1/2,1/2,0,0)`. It is the classical Hurwitz covering bound.

Given `a,b` in `O` with `b!=0`, choose this `q` for `x=a b^(-1)` and set
`c=a-qb`. The multiplication order is essential. Closure gives `c` in `O`,
and norm multiplicativity gives

```text
N(c) = N((a b^(-1)-q)b) <= N(b)/2 < N(b).
```

Computing the rational inverse for this offline rounding decision can use
odd denominators. The returned quotient `q` and remainder `c` are Hurwitz
integers. The claim excludes odd denominators from the emitted factors and
ordinary coefficient dictionary, not from all compiler arithmetic.

## 3. Left row reduction and the inverse certificate

First consider a matrix `M` over `O`. Start with `E=M` and `U=V=I_m`.
Maintain

```text
U M = E,       U V = V U = I_m.
```

Process columns from left to right, with the next pivot row `p`. If every
entry of the current column in rows `p..m-1` is zero, skip that column.
Otherwise swap a nonzero entry into row `p`. A row swap in `E` and `U`
requires the same column swap in `V`.

For each nonzero lower entry `a=E[i,col]` and pivot `b=E[p,col]`, use the
division in Section 2. Perform these operations:

```text
E[i,*] <- E[i,*] - q E[p,*]
U[i,*] <- U[i,*] - q U[p,*]
V[*,p] <- V[*,p] + V[*,i] q
```

The last multiplication is on the right. These are inverse elementary
matrix operations: if `T` has `-q` in position `(i,p)` and ones on its
diagonal, then `T^(-1)` has `q` in that position because `i!=p`. The updates
are `E<-TE`, `U<-TU`, and `V<-VT^(-1)`. They preserve both invariant
identities and keep every matrix entry in `O`.

If the remainder is nonzero, swap rows `i` and `p`; the new pivot norm is
at most half the old norm. If it is zero, that lower entry has been cleared.
Nonzero pivot norms are positive integers. Thus only finitely many nonzero
remainders can occur at a fixed pivot. A zero remainder reduces the number
of nonzero lower entries. The column therefore terminates. Earlier pivot
columns stay zero in all active rows, so later operations preserve them.
There are finitely many columns. The whole algorithm terminates.

At return, the first `r` rows of `E` have strictly increasing pivot columns
with nonzero pivots. Every later row is zero. The selected pivot minor is
upper triangular with nonzero diagonal, so it is invertible over `K` by
back substitution, with multiplication order preserved. Thus `E` has rank
`r` over `K`. Since `U` is invertible over `O`, `M` has the same rank.

Let `C` be the first `r` columns of `V`, and let `B0` be the first `r` rows
of `E`. The invariant gives `M=V E=C B0`, with both factors over `O`. No
pivot is divided out of the emitted matrix. In particular, a nonunit pivot
does not force its inverse into a returned factor.

## 4. Dyadic factors and the matching lower bound

For a given dyadic input `A`, choose a common `2^s` that clears all its
coordinate denominators. Then `M=2^s A` is in `L`, hence in `O`. Apply
Section 3 and set `B=2^(-s) B0`. The scale is central. This proves `A=C B`
and the stated denominator bounds. It also proves that all factors lie in
`D`, since `O` is contained in `D` and `O[1/2]=D`.

Conversely, any factorization through `q` dyadic quaternion columns remains
a factorization over the division ring `K`. Its image is contained in the
right `K`-span of those `q` columns. Therefore `rank_K(A)<=q`. The construction
uses `q=r`, so the lower bound is attained. This establishes exact inner
rank, not only an upper bound.

This does not contradict PR7745's integral counterexample. There the
coefficient ring is the smaller Lipschitz order `L`. It need not contain a
norm-decreasing Euclidean quotient. For `a=1+j`, `b=1+i`, the exact left
quotient is `(1-i+j+k)/2`, in `O` but not in `L`. Coordinatewise integer
rounding leaves a remainder with the same norm as `b`; the integer-only
reduction has no strict progress at that step.

On PR7745's exact response, this implementation returns

```text
C = [1, (1-i+j+k)/2]^T,
B = [1+i, i+k].
```

These multiply to the original matrix `[[1+i,i+k],[1+j,i+j]]`. This is a
rank-one dyadic factorization. The source supplies its separate proof that
no rank-one Lipschitz factorization exists; that obstruction is retained
and replayed, not claimed as a new result here.

## 5. Relation to query channels

Under the atlas's faithful even/odd operator split, its R03 theorem makes
any `q`-query word factor the full odd response through `q` ordinary-algebra
rows, including with feedback. Its R04 construction implements any explicit
factorization when the required ordinary coefficient words and query
commutation contract are supplied. For the full ordinary ring `D`, the
coefficient-existence part of that interface therefore has minimum channel
count `rank_K(A)`.

Each fixed quaternion coefficient in the returned factors has a finite
formal word made from signed lane permutations, additions and dyadic halves.
That existence statement does not make a half exact on an actual reached
integer grid, place a query bank, preserve a physical borrowed field or
price cleanup. A smaller physical dictionary can again have a larger inner
rank. The theorem is about the full stated ring and complete response;
it does not authorize deleting unobserved outputs or changing a caller.

## 6. Evidence and limits

The exact checker replays all operation transcripts with Nick Petalas's
separate multiplication formula. It checks `UM=E`, both inverse identities,
`VE=M`, echelon pivots, returned products and both denominator bounds. A
separate rational Gaussian elimination computes the rank of the `4m` by
`4n` left-regular block matrix. That rank is four times the quaternion rank,
so it checks the factor width without using the Euclidean reducer.

The retained receipt covers 625 matrices from the complete five-letter
`2x2` alphabet `{0,1,i,j,omega}`, 35 constructed rectangular cases of all
possible ranks for ten shapes, five dense rectangular cases, and four
explicit witnesses. In total it covers 669 matrices and 947 Euclidean
divisions, with ranks zero through five. The 4,096-point eighth-grid check
corroborates the sharp rounding bound. Sixteen Hamilton basis products and
sixteen Hurwitz basis products check signs and order closure.

Eight malformed/order-domain inputs reject. Three changed operation/factor
certificates reject. A reversed quotient order fails the norm bound, and
integer-only rounding detects the source stagnation. The original source's
eight basis responses, sixteen parity classes and twenty-four norm-two
divisors replay unchanged. These are finite checks of the all-size written
proof, not an exhaustive enumeration of all matrices or formal acceptance.

No coefficient-height bound, compiler bit-complexity bound, live physical
query, reached-grid realization, ownership restoration or complete supplier
invoice is supplied. Historical full suites, selected cold replay, Lean and
Docker were not run. All five framework assumptions remain. Prepared by
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
