# Exact ordinary tensor error of a square-zero border

This contribution is produced by Nick Petalas. Apache-2.0.

## Statement and scope

All norms below are Euclidean operator norms on finite-dimensional complex
spaces. Let `D` be unitary, let `N^2=0`, and put

```text
C(e) = D (I + e N),       sigma = ||N||,       a = |e| sigma.
```

For every positive integer `k`, both errors

```text
||C(e)^(tensor k) - D^(tensor k)||,
||(C(e)^(-T))^(tensor k) - (D^(-T))^(tensor k)||
```

equal `F_k(a)`. Define the `(k+1)` by `(k+1)` real matrix `B_k(a)` by

```text
B[i,j] = a^(j-i) sqrt(binomial(j,i) binomial(k-i,j-i))   if 0 <= i < j <= k,
B[i,j] = 0                                             otherwise.
```

The exact spectral formula is

```text
F_k(a) = ||B_k(a)||.
```

Thus the error can be determined by a matrix of size `k+1`, independently
of the original dimension or rank of `N`. This is an exact finite spectral
formula, not a radical expression for its largest singular value. The case
`a=0` is zero throughout.

Write `gamma_k = sqrt(floor((k+1)^2/4))`. For every `a>=0`,

```text
max(a gamma_k, (1+a/2)^k - 1) <= F_k(a)
F_k(a) <= a gamma_k + ((1+a)^k - 1 - k a) <= (1+a)^k - 1.
```

In particular, the sharp first-order coefficient is

```text
lim_(a -> 0+) F_k(a)/a = gamma_k.
```

These are statements about ordinary tensor powers of completed matrices.
They do not identify the repository's chronological supplier product with
such a tensor power. No native invoice or multiplication exponent changes.

## 1. Reduce an arbitrary square-zero matrix to its largest shear

Since `im(N)` is contained in `ker(N)`, the orthogonal decomposition
`ker(N) + ker(N)^perp` writes `N` as a single off-diagonal block. Applying
the singular-value decomposition to that block gives mutually orthogonal
two-dimensional blocks

```text
[[0, sigma_j], [0, 0]],
```

and zero blocks. Each `sigma_j` is nonnegative and their maximum is `sigma`.
Unitary diagonal changes remove the phase of `e`. Therefore `I+eN` is
unitarily similar to a direct sum of shears `J(b)=[[1,b],[0,1]]`, with
`0<=b<=a`, and identity blocks. A block with `b=a` is present if `a>0`.

Its `k`th tensor power is the direct sum of tensor products of these
blocks. After subtracting identity, every such block has nonnegative
entries. Increasing any shear parameter increases entries. For real
nonnegative matrices, entrywise domination implies norm domination:
`|Mv| <= M|v| <= L|v|` when `0<=M<=L`, hence `||M||<=||L||`.
An identity block can be embedded into a two-dimensional zero-parameter
shear. Consequently the maximum is attained by `J(a)^(tensor k)-I`.

Left multiplication by the unitary `D^(tensor k)` does not change the
forward error. Also

```text
C(e)^(-T) = D^(-T) (I - e N^T).
```

Here `D^(-T)` is unitary, `(N^T)^2=0`, and `||N^T||=sigma`. The same
reduction proves equality of the two orientation errors. The analogous
inverse error has the same value as well, by right unitary multiplication.

## 2. Reduce the largest shear tensor to its symmetric subspace

Index the standard basis of `(C^2)^(tensor k)` by subsets of `{1,...,k}`.
For `M=J(a)^(tensor k)-I`,

```text
M[S,T] = a^(|T|-|S|) if S is a proper subset of T, and 0 otherwise.
```

Suppose `a>0`. The empty-set column is zero. On all nonempty columns,
`M^T M` is strictly positive, since their shared empty-set row contributes
`a^(|S|+|T|)>0`. The elementary positive-matrix eigenvector theorem gives a
unique positive unit eigenvector for its largest eigenvalue. Permutations
of the `k` coordinates commute with `M^T M`, so uniqueness makes that
eigenvector permutation invariant. It is constant on each subset level.
Thus the largest right singular vector belongs to the symmetric subspace.

Use the orthonormal level vectors which have value
`binomial(k,j)^(-1/2)` on subsets of size `j`, and zero elsewhere. For
a fixed size-`i` subset there are `binomial(k-i,j-i)` supersets of size `j`.
The matrix entry from level `j` to level `i<j` is therefore

```text
a^(j-i) binomial(k-i,j-i) sqrt(binomial(k,i)/binomial(k,j))
  = a^(j-i) sqrt(binomial(j,i) binomial(k-i,j-i)).
```

This is `B_k(a)`. The symmetric subspace is invariant under `M`, and a
largest right singular vector lies there, proving the exact formula.

The finite verifier avoids square roots. In constant-on-level coordinates
it uses `A[i,j]=binomial(k-i,j-i)a^(j-i)` with weight
`W[i,i]=binomial(k,i)`. Its Gram operator is `W^(-1) A^T W A`, similar to
`B^T B`, and has rational entries for rational `a`.

## 3. Sharp coefficient and global bounds

The coefficient of `a` in `B_k(a)` has only its first superdiagonal
nonzero, with entries `sqrt((i+1)(k-i))`. Its singular norm is the maximum
of those entries. Maximizing the integer product gives `gamma_k`.
All remaining entries of `B_k(a)` are nonnegative, so entrywise norm
monotonicity gives the lower bound `a gamma_k`.

Expand `J(a)^(tensor k)-I` by nonempty sets of tensor positions. The
sum of the one-position terms has norm `a gamma_k`. Each product on
`r` positions has norm `a^r`, and there are `binomial(k,r)` such products.
The triangle inequality bounds the remainder by
`(1+a)^k-1-ka`. This proves the sharper upper bound and the first-order
limit. Since `gamma_k<=k`, the simpler upper bound follows.

For the second lower bound use the unit vector `v=(1,1)/sqrt(2)` in
each tensor factor. Its matrix coefficient for `J(a)` is `1+a/2`.
Taking its product matrix coefficient gives `(1+a/2)^k-1`.

For illustration, `F_1(a)=a`, whereas

```text
F_2(a) = a/2 * (sqrt(a^2+8)+a) > sqrt(2) a     for a>0.
```

The strict inequality matters: the sharp first-order expression is not
an exact nonzero-parameter error formula.

## 4. A necessary precision budget, with a sufficient choice two bits away

Let `0<delta<=1` be the allowed operator error and `sigma>0`.
Necessarily `|e| sigma gamma_k <= delta`. The explicit sufficient choice

```text
|e| sigma <= delta/(2k)
```

works in both orientations. Indeed, with `x=ka<=delta/2<1`,

```text
(1+a)^k-1 <= sum_(r>=1) x^r = x/(1-x) <= delta.
```

For a dyadic parameter `e=2^(-p)`, `p` a nonnegative integer, this gives

```text
necessary p >= max(0, ceil(log2(sigma gamma_k/delta))),
sufficient p  = max(0, ceil(log2(2k sigma/delta))).
```

The sufficient integer is at most two larger than the necessary lower
bound, because `2k/gamma_k<4`. In particular, the required parameter
precision grows as `log2(k)+log2(sigma/delta)+O(1)` when that quantity is
positive. Choosing a fixed nonzero parameter cannot maintain a fixed
error as `k` grows, already by the product-vector lower bound.

This pays only for endpoint approximation. It does not bound the large
coefficients of a singular scalar wrapper, errors inserted inside paid
calls, intermediate magnitudes, owned restoration, storage, movement or
the cost of producing this parameter. Those are separate obligations in
PR4623's global approximation question.

## Credit and limits

Dillon Amburgey's PR4623 poses the global approximation problem and gives
the finite linear-circuit error contract. Its distinction between ordinary
tensor endpoints and chronological supplier substitution is retained here.
Credit Cinna Davis, Jacob Alan Sussman, zxv and the retained native, caller,
compiler and precision lineage. Singular-value decomposition, symmetry on
the Boolean lattice and the positive-matrix eigenvector theorem are
classical. No literature-priority claim is made for those tools.

The new result is the exact square-zero tensor-error reduction, its sharp
all-k first-order constant and the resulting two-orientation precision
screen. The written proof is universal within these hypotheses; the
verifier supplies separate finite exact corroboration. No human or formal
proof-kernel acceptance, physical supplier or complete multiplication
theorem is claimed.
