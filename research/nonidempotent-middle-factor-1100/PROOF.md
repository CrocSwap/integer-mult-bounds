# Middle factors after rows (1, 1, 0, 0)

No new kappa. The selected frontier stays `363005817/100000000000`.

Let A be the rank-1 idempotent in M_4(F_2) with rows (1, 1, 0, 0). For an
arbitrary matrix B, set C = I + A + B. This note proves which B satisfy

```text
(I + x A)(I + x B)(I + x C) = I + x I_4,
```

and records the exhaustive count. There are exactly 296 such matrices. They
fall into three families on the splitting F_2^4 = im(A) ⊕ ker(A):

| Family | Size | B | C | Annihilation |
|---:|---:|---|---|---|
| 1 | 58 | idempotent | idempotent | A B = B A = 0 |
| 2 | 119 | idempotent | not idempotent | B A = 0 and A B ≠ 0 |
| 3 | 119 | not idempotent | idempotent | A B = 0 and B A ≠ 0 |

Families 1 and 2 are the 177 idempotent middle factors already counted by
PR #7040. Family 3 is the new set: 119 non-idempotent middle factors. No
solution has both B and C non-idempotent. The zero matrix is the unique
rank-0 solution, and exactly eight solutions satisfy B^2 = 0.

The evidence classes are separate.

1. A coefficient proof, valid for every idempotent first factor in any
   M_n(F_2), that the displayed product equals I + x I if and only if
   B C = 0. The count 296 is not part of that lemma and is not claimed for
   any first factor other than the named matrix.
2. A block proof that, for this named A, B C = 0 if and only if B lies in
   one of the three families, together with the subspace counts 58, 119
   and 119.
3. An exhaustive finite census of all 65,536 matrices in M_4(F_2). The
   census multiplies the three gates for every 16-bit pattern and checks
   that the accepted set is exactly the set built from the three families.

The census has no early stop and no sampled order. It is not a heuristic
search. It does not rerun the 802-by-802 idempotent-pair census of #7040,
and it does not rebuild the nine-factor paired-star word.

## 1. Hypotheses

Matrices are written as row bit-masks. Bit c of row r is the entry (r, c).
The matrices used below are

```text
A        = (1, 1, 0, 0) = [[1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
P = I+A  = (0, 3, 4, 8)
W        = (0, 1, 0, 0)
S        = (3, 0, 0, 0)
E        = (4, 5, 0, 0)
```

A gate is I + x M with M constant and x an indeterminate. The product is
ordered and the coefficients lie in M_4(F_2). The target I + x I_4 has
1 + x on the diagonal and 0 off the diagonal. Characteristic two is used
for every cancellation A + A = 0. The statement is not claimed in odd
characteristic.

The named rows give A e_0 = e_0 + e_1 and A e_j = 0 for j = 1, 2, 3. Thus
A^2 = A, the image L is the line spanned by v = e_0 + e_1, and the kernel
K is the coordinate hyperplane x_0 = 0. These subspaces meet only at 0, and
P = I + A is the projection onto K along L: P v = 0 and P acts as the
identity on K. In particular P^2 = P and A P = P A = 0.

## 2. The coefficient criterion

Let A be idempotent in M_n(F_2), any n, and let B be arbitrary. The ordered
expansion is

```text
(I + x A)(I + x B) = I + x (A + B) + x^2 A B,
(I + x A)(I + x B)(I + x C)
    = I + x (A + B + C) + x^2 (A B + (A + B) C) + x^3 A B C.
```

The linear coefficient equals I if and only if C = I + A + B. For that
forced third factor, A + B + C = I in characteristic two, and the quadratic
coefficient collapses as follows:

```text
A B + (A + B)(I + A + B)
    = A B + (A + B)(I + A) + (A + B) B
    = A B + A + A^2 + B + B A + A B + B^2
    = B + B A + B^2
    = B (I + A + B)
    = B C.
```

The two copies of A B cancel, and A + A^2 = 0 because A is idempotent. The
cubic coefficient is A B C = A (B C). Therefore both higher coefficients
vanish if and only if B C = 0.

**Lemma.** Let A be an idempotent matrix over F_2 and let B be any matrix
of the same size. The product (I + x A)(I + x B)(I + x (I + A + B)) equals
I + x I if and only if B (I + A + B) = 0.

The lemma uses idempotence of A and characteristic two. It does not use the
dimension, the rank, or idempotence of B. Applied to the named matrix, the
gate identity holds exactly when B (B + P) = 0, or equivalently B^2 = B P.

## 3. Blocks on the image and the kernel

Every vector of F_2^4 is uniquely ℓ v + k with ℓ in F_2 and k in K. Every
matrix B therefore has unique blocks α in F_2, g in K, φ in the dual of K,
and δ in End(K), determined by

```text
B(ℓ v + k) = (α ℓ + φ(k)) v + (ℓ g + δ(k)).
```

There are 2 · 8 · 8 · 512 = 65,536 such tuples, so the correspondence is a
bijection. In these blocks P(ℓ v + k) = k, and

```text
B P(ℓ v + k) = φ(k) v + δ(k),
B^2(ℓ v + k) = (α ℓ + α φ(k) + ℓ φ(g) + φ(δ(k))) v
             + (ℓ (α g + δ(g)) + φ(k) g + δ^2(k)).
```

Equating B^2 = B P for every ℓ and k is equivalent to the four conditions

```text
α = φ(g),
φ ∘ δ = (α + 1) φ,
(δ + α I) g = 0,
δ(δ + I) = g ⊗ φ.
```

Here (g ⊗ φ)(k) = φ(k) g. Thus, for this A, the gate identity holds if and
only if these four equations hold.

## 4. Both off-diagonal blocks cannot be nonzero

The third block equation says δ g = α g. Apply φ:

```text
φ(δ g) = α φ(g) = α,
```

since α = φ(g) lies in F_2 and α^2 = α. The second equation at the vector
g gives the other evaluation φ(δ g) = (α + 1) φ(g) = 0. Hence α = 0. Every
solution therefore has

```text
α = 0,    φ(g) = 0,    δ g = 0,    φ ∘ δ = φ,
δ(δ + I) = g ⊗ φ.
```

Suppose g and φ are both nonzero. Choose h with φ(h) = 1 and set w = δ h.
Then φ(w) = φ(δ h) = φ(h) = 1, and

```text
(δ + I) w = (δ^2 + δ) h = (g ⊗ φ)(h) = g.
```

Apply δ(δ + I) to w. The left side is (g ⊗ φ)(w) = g, which is nonzero.
The right side is δ g = 0. This contradiction shows that no solution has
both g and φ nonzero.

Consequently δ(δ + I) = 0, so δ is idempotent, and the remaining conditions
are δ g = 0 and φ ∘ δ = φ. For an idempotent endomorphism, δ + I is the
projection onto ker(δ) along im(δ), so φ ∘ δ = φ if and only if
ker(δ) ⊆ ker(φ). The solutions are therefore exactly the triples below.

**Family 1.** g = 0, φ = 0, and δ^2 = δ. Then B(ℓ v + k) = δ(k).

**Family 2.** g = 0, φ ≠ 0, δ^2 = δ, and ker(δ) ⊆ ker(φ).

**Family 3.** φ = 0, g ≠ 0, δ^2 = δ, and g ∈ ker(δ). The condition
ker(δ) ⊆ ker(φ) is automatic because ker(φ) = K.

These three sets of block tuples are disjoint because their pairs (g, φ)
are disjoint, and different block tuples are different matrices.

## 5. Idempotence, annihilation, and rank

Write C = P + B.

In family 1, B(ℓ v + k) = δ(k) and δ^2 = δ, so B^2 = B. Also
C(ℓ v + k) = k + δ(k), and a second application returns the same vector
because δ(δ + I) = 0. Thus C is idempotent. The image of B lies in K, so
A B = 0. Also B v = 0, so B A = 0.

In family 2, B(ℓ v + k) = φ(k) v + δ(k). The identity φ ∘ δ = φ gives
B^2 = B, so B is idempotent. Then B v = 0, hence B A = 0. Since φ ≠ 0, the
image of B is not contained in K, so A B ≠ 0. The same expansion gives

```text
C(ℓ v + k) = φ(k) v + (k + δ(k)),
C^2(ℓ v + k) = k + δ(k).
```

These differ whenever φ(k) = 1, so C is not idempotent.

In family 3, B(ℓ v + k) = ℓ g + δ(k). Then B^2(ℓ v + k) = δ(k). Because
g ≠ 0, B^2 ≠ B. The image of B lies in K, so A B = 0. Also B v = g ≠ 0, so
B A ≠ 0. And

```text
C(ℓ v + k) = ℓ g + k + δ(k)
```

is fixed by a second application: δ g = 0 and δ^2 = δ cancel the extra
terms. Thus C is idempotent.

Combining this with the lemma, every solution has either B or C
idempotent, and the 58 solutions in family 1 are the only ones for which
both are idempotent. The 177 idempotent middle factors are families 1 and
2. They are exactly the solutions with B A = 0. This agrees with the count
177 in #7040. The 802-by-802 ordered pair census of that package is not
repeated here; the idempotent slice is recomputed from the block families
and from the 65,536-matrix scan.

The rank formulas follow from the same expressions. In families 1 and 2,
ker(B) has dimension 1 + dim ker(δ), so rank(B) = rank(δ). In family 3,
g lies in ker(δ) and, because δ is idempotent, ker(δ) meets im(δ) only at
0. Therefore ℓ g + δ(k) = 0 if and only if ℓ = 0 and δ(k) = 0, and
rank(B) = 1 + rank(δ).

Finally, B^2 = 0 forces the following. Family 2 consists of idempotents,
so only the zero matrix there could be nilpotent, and the zero matrix is
in family 1. Family 1 gives B^2 = 0 only for δ = 0, hence only for B = 0.
Family 3 gives B^2(ℓ v + k) = δ(k), so δ = 0, and then each of the seven
nonzero vectors g contributes one rank-1 matrix with B(ℓ v + k) = ℓ g.
Exactly eight solutions satisfy B^2 = 0.

## 6. The counts

F_2^3 has (8 − 1)/(2 − 1) = 7 lines and (7 · 6)/(3 · 2) = 7 planes. A fixed
line lies in the 3 planes corresponding to the lines of the quotient
F_2^2, so it has 7 − 3 = 4 complementary planes. A plane likewise has
7 − 3 = 4 complementary lines. An idempotent endomorphism is the
projection onto its image along its kernel, and that pair of complementary
subspaces is unique. The resulting counts are

```text
rank 0: 1,    rank 1: 7 · 4 = 28,    rank 2: 7 · 4 = 28,    rank 3: 1.
```

The total is 58. Family 1 therefore contains 58 matrices. Their ranks are
the ranks of δ, namely 1, 28, 28, 1 in ranks 0 through 3.

For a nonzero linear form φ, the kernel Π = ker(φ) is a plane. The
idempotents with ker(δ) ⊆ Π are the identity, the 3 · 4 = 12 projections
whose kernel is a line of Π, and the 4 projections whose kernel is Π.
That is 1 + 12 + 4 = 17 endomorphisms. Seven nonzero forms give
7 · 17 = 119 matrices in family 2. By rank of δ, and hence by rank of B,
these are 7 of rank 3, 84 of rank 2, and 28 of rank 1.

For a nonzero vector g, the idempotents with g ∈ ker(δ) are the zero map,
the 4 projections whose kernel is the line spanned by g, and the
3 · 4 = 12 projections whose kernel is a plane through g. Again 17. Seven
nonzero vectors give 119 matrices in family 3. By rank of δ they are 7 of
rank 0, 84 of rank 1, and 28 of rank 2. The rank formula of Section 5
turns those into 7 matrices of rank 1, 84 of rank 2, and 28 of rank 3.

Adding the three families,

```text
58 + 119 + 119 = 296,
```

and the ranks of B are

```text
rank 0: 1,
rank 1: 28 + 28 + 7 = 63,
rank 2: 28 + 84 + 84 = 196,
rank 3: 1 + 7 + 28 = 36,
rank 4: 0.
```

Different block tuples give different matrices, so there is no collapse
between a form counted twice or a vector counted twice.

## 7. The exhaustive census

Every matrix in M_4(F_2) is a 16-bit integer, with row r stored in bits
4r through 4r + 3. As that integer runs from 0 through 65,535, each matrix
occurs once. There is no early exit. For each integer the verifier sets
C = I + A + B, multiplies the three gates in F_2[x], and separately tests
B(B + P) = 0. The two tests agree on all 65,536 matrices. Exactly 296
products equal I + x I_4.

The same run extracts blocks for every matrix, rebuilds every one of the
65,536 block tuples, and checks that the two maps are inverse bijections.
It then builds the three families from the 512 endomorphisms of F_2^3 and
from the 256 subsets used to enumerate subspaces. The constructed set has
296 distinct matrices and equals the set accepted by the gate product.
The scanned family counts are 58, 119 and 119. The idempotent slices have
size 177, their overlap has size 58, and no accepted matrix has both
factors non-idempotent.

The accepted integers, written in ascending decimal order with one integer
per line and a trailing newline, have SHA256

```text
07a59d5644b30bf5c78ec67fd58bdee01cc1048fc5dc20ea574fffe3e4ec5659
```

That fingerprint is a label of this census, not a substitute for the scan.

## 8. Two solutions and one excluded matrix

The zero matrix is the family-1 point with δ = 0. Its third factor is P,
and (I + x A)(I + x P) = I + x I because A P = 0 and A + P = I.

The family-3 witness W = (0, 1, 0, 0) has g = e_1, φ = 0 and δ = 0. It
sends e_0 to e_1 and kills e_1, e_2 and e_3, so W^2 = 0 and W is not
idempotent. Its third factor is

```text
C = I + A + W = (0, 2, 4, 8) = diag(0, 1, 1, 1),
```

which is idempotent. The gates multiply as follows. First

```text
I + x A = [[1+x, 0, 0, 0], [x, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
I + x W = [[1, 0, 0, 0], [x, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
(I + x A)(I + x W)
    = [[1+x, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]].
```

The row-1 cancellation is x + x = 0. Then I + x C = diag(1, 1+x, 1+x, 1+x),
and the product is diag(1+x, 1+x, 1+x, 1+x) = I + x I_4.

The family-2 witness S = (3, 0, 0, 0) is the idempotent matrix used in
#7040. Its third factor (3, 3, 4, 8) is not idempotent, and the gate
product is still the target. This witness lies in the 119, not in the 58.

The matrix E = (4, 5, 0, 0) is the excluded block tuple g = e_1,
φ(e_2) = 1 and δ = 0. Both off-diagonal blocks are nonzero, so Section 4
excludes it. The gate product with third factor I + A + E is not the
target. One rejected matrix is not the classification; it is a failure
control for the excluded shape. The one-bit neighbor of W obtained by
setting the (0, 0) entry, which is A itself, is likewise rejected.

## 9. Scope

The count 296 and the three families are statements about this named
matrix only. The coefficient lemma applies to every idempotent first
factor, but the block count uses dim ker(A) = 3 and the named splitting.
No other rank-1 matrix was scanned. The nine-factor paired-star word is
not rebuilt, and a family-3 factorization is not claimed to be a legal
word factor. The reversed order (I + x B)(I + x A)(I + x C) is a different
equation and is not classified here.
