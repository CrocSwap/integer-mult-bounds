# Idempotent triples after one rank-1 matrix other than E_11

No new kappa. The selected frontier stays 781451/250000000.

Let A be the rank-1 idempotent in M_4(F_2) with rows (1, 1, 0, 0). An ordered
triple of idempotent matrices (A, B, C) satisfies

```text
(I + x A)(I + x B)(I + x C) = I + x I_4
```

if and only if A B = B A = 0 and C = I + A + B. There are exactly 58 such
triples. The same equivalence holds for every idempotent first factor in
M_n(F_2), any n. That general equivalence is a coefficient proof. The count
58 for this A, and the statement that the 802-by-802 scan has no further
solution, are proved by the kernel bijection below and are also the output
of an exhaustive finite census. The census was not run for the other rank-1
matrices. Their count is the same bijection, which uses only that the first
factor is a rank-1 idempotent on a 4-dimensional space.

The evidence classes are separate.

1. A proof of the coefficient equivalence for every idempotent triple over
   F_2, of the bijection with idempotents of the kernel, and of the counts
   58 and 177.
2. An exhaustive finite census of the 65,536 matrices in M_4(F_2), of all
   802-by-802 idempotent pairs after this A, of the subspaces used in the
   counts, and of the 512 endomorphisms of the 3-dimensional kernel.
3. Two explicit triples, one of them multiplied by hand below, and one
   witness whose third factor is not idempotent. These witnesses are not a
   classification by themselves.

This is not a truncated search. It does not change the selected frontier,
and it does not rerun the E_11 census or the T-commutant valuation identity
of PR #7027.

## 1. Hypotheses

Matrices are written as row bit-masks. Bit c of row r is the entry (r, c).
The named matrix and the two witnesses used below are

```text
A     = (1, 1, 0, 0) = [[1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
E_33  = (0, 0, 4, 0)
S     = (3, 0, 0, 0)
```

A gate is I + x M with M constant and x an indeterminate. The product is
ordered. The target I + x I_4 is the diagonal matrix with 1 + x in every
diagonal entry. In characteristic two, (1 + x)^2 = 1 + x^2 and
(1 + x)^4 = 1 + x^4.

The stage-0 copy of a 4-by-4 matrix sits on coordinates

```text
(core_0, core_1, leaf0_0, leaf0_1)
```

of the eight-dimensional paired-star space and is zero elsewhere. This is
the coordinate order of `research/paired-star-three-full-calls`. E_0 is the
identity on those four coordinates and zero on the other four.

## 2. The coefficient equivalence

Let A, B, C be matrices of the same size over F_2, not yet assumed
idempotent. Expanding the ordered product gives

```text
(I + x A)(I + x B) = I + x (A + B) + x^2 A B,
(I + x A)(I + x B)(I + x C)
    = I + x (A + B + C) + x^2 (A B + (A + B) C) + x^3 A B C.
```

The linear coefficient equals I if and only if C = I + A + B. Thus every
matrix solution, idempotent or not, has its third factor forced.

Now assume A and B are idempotent, and set C = I + A + B. Then

```text
(A + B)^2 = A + B + A B + B A,
(A + B) C = (A + B) + (A + B)^2 = A B + B A,
```

The quadratic coefficient is A B + (A + B) C, hence
A B + (A B + B A) = B A. The cubic coefficient is

```text
A B C = A B (I + A + B) = A B A,
```

because B^2 = B cancels the two copies of A B. Associativity gives
A B A = A (B A), so B A = 0 already forces the cubic coefficient to vanish.
Therefore, for idempotent A and B,

```text
(I + x A)(I + x B)(I + x (I + A + B)) = I + x I
```

if and only if B A = 0.

It remains to impose idempotence of C. With A and B idempotent,

```text
C^2 = (I + A + B)^2 = I + A + B + A B + B A = C + A B + B A,
```

so C is idempotent if and only if A B = B A. Combined with B A = 0, this
is A B = B A = 0.

Conversely, if A and B are idempotent, A B = B A = 0, and C = I + A + B,
the same two displays give C^2 = C and

```text
(I + x A)(I + x B) = I + x (A + B),
(I + x (A + B))(I + x C) = I + x (A + B + C) = I + x I,
```

because (A + B) C = (A + B) + (A + B)^2 = 0. This direction does not use
the ambient dimension. The three cross relations with C are then forced:

```text
A C = A (I + A + B) = 0,    C A = (I + A + B) A = 0,
B C = B (I + A + B) = 0,    C B = (I + A + B) B = 0.
```

So A, B, C are pairwise orthogonal idempotents summing to I. For any order
P, Q, R of such a triple, P Q = 0 and (P + Q) R = 0, and the same two-line
expansion gives (I + x P)(I + x Q)(I + x R) = I + x I.

**Theorem.** Let A, B, C be idempotent matrices in M_n(F_2). The ordered
product (I + x A)(I + x B)(I + x C) equals I + x I if and only if
A B = B A = 0 and C = I + A + B. Every one of the six orders then equals
I + x I.

The idempotence hypotheses are necessary for this equivalence. Section 4
gives 119 idempotent matrices B for the named A such that B A = 0 but
A B is not zero. For each of them the gate product with third factor
I + A + B is the target, and that third factor is not idempotent.

Characteristic two is necessary for the cancellations A + A = 0 and
(A + B) + (A + B) = 0. The theorem is not claimed over a field of odd
characteristic.

## 3. The named rank-1 matrix

The named rows give A e_0 = e_0 + e_1 and A e_j = 0 for j = 1, 2, 3. Thus
A^2 = A, the image is the line spanned by v = e_0 + e_1, and the kernel is
the coordinate hyperplane x_0 = 0. These subspaces meet only at 0. Every
vector is x_0 v plus a kernel vector, so F_2^4 = im(A) ⊕ ker(A). The rank
is 1. This matrix is not E_11 = (1, 0, 0, 0).

**Lemma.** Let P be any rank-1 idempotent on a finite-dimensional vector
space, so the space is im(P) ⊕ ker(P). Restriction is a bijection from
the idempotent endomorphisms B with P B = B P = 0 to the idempotent
endomorphisms of ker(P). The inverse extends a kernel endomorphism by zero
on im(P).

If B^2 = B and P B = B P = 0, then im(B) sits in ker(P) and im(P) sits in
ker(B), so B preserves the kernel and vanishes on the image. Conversely,
the extension B(u + w) = Q w is idempotent when Q is, its image lies in
the kernel, and it vanishes on the image. Both compositions with P are
therefore zero, and Q is the restriction of B.

For the named A the kernel is 3-dimensional. The idempotent endomorphisms
of F_2^3 are counted by image and kernel. Every idempotent is the
projection onto its image along its kernel, those subspaces meet only at
0 and span the space, and the pair (image, kernel) is unique. So each
idempotent is counted once.

F_2^3 has (8 - 1)/(2 - 1) = 7 lines. An ordered pair of linearly
independent vectors can be chosen in 7 · 6 = 42 ways, and each plane
contains 3 · 2 = 6 such pairs, so there are 7 planes. The planes containing
a fixed line are the lines of the quotient F_2^2, and that quotient has
(4 - 1)/(2 - 1) = 3 lines. A fixed line therefore has 7 - 3 = 4
complementary planes, and there are 7 · 4 = 28 rank-1 idempotents. A
plane likewise has 4 complementary lines, giving 28 rank-2 idempotents.
Ranks 0 and 3 contribute the zero map and the identity. The total is

```text
28 + 28 + 1 + 1 = 58.
```

The lemma therefore supplies exactly 58 idempotent matrices B orthogonal
to the named A, and exactly 58 idempotent triples (A, B, C) with
C = I + A + B. Any other 3-dimensional space over F_2 has a basis, and
that basis identifies its endomorphisms with the matrices just counted,
so it also has 58 idempotent endomorphisms. The lemma uses only rank 1.
The same count therefore holds for every rank-1 idempotent in M_4(F_2).
This package multiplies out only the named first factor. The other 119
rank-1 matrices were not scanned.

On the kernel coordinates (x_1, x_2, x_3), the extension by zero has equal
first and second columns, because e_0 = v + e_1 and the extension kills v.
The identity of the kernel extends to I + A = (0, 3, 4, 8). The projection
onto the kernel line spanned by e_2 extends to E_33.

## 4. One-sided annihilation

The product identity of Section 2 asks only for B A = 0 when the third
factor is allowed to be non-idempotent. For the named A, B A = 0 means
B v = 0.

Every idempotent is the projection onto its image along its kernel, so
the idempotents killing v are exactly the projections whose kernel
contains v. A k-dimensional subspace containing v corresponds to a
(k - 1)-dimensional subspace of F_2^4 / span{v} ≅ F_2^3. Those quotient
counts are 1, 7, 7, 1 for dimensions 0, 1, 2, 3, hence the kernels
containing v have dimensions 1, 2, 3, 4 in the same numbers 1, 7, 7, 1.

A fixed subspace K of dimension k has 2^{k(4-k)} complements. One
complement L_0 exists. Every other complement is the graph of a unique
linear map L_0 → K, and every linear map arises once, so the count is
the order of that Hom space. The resulting projections are

| dim ker | kernels containing v | complements | projections |
|---:|---:|---:|---:|
| 4 | 1 | 1 | 1 |
| 3 | 7 | 8 | 56 |
| 2 | 7 | 16 | 112 |
| 1 | 1 | 8 | 8 |

The sum is 1 + 56 + 112 + 8 = 177. Exactly 58 of these projections also
satisfy A B = 0, by Section 3. The other 177 - 58 = 119 idempotent
matrices B satisfy B A = 0 and A B ≠ 0. For each of those 119, the third
factor I + A + B reproduces the target gate and is not idempotent.

One explicit witness is S = (3, 0, 0, 0). Its image is span{e_0}, so
A S sends e_0 to v and is not zero. Also S v = S e_0 + S e_1 = 0, and
S^2 = S. The third factor (3, 3, 4, 8) fails to be idempotent. This
witness is outside the 58.

## 5. The exhaustive census

Every completeness statement below enumerates a set that has a product
structure of known cardinality, or enumerates every bit pattern in a
vector space of dimension at most 16. There is no early stop and no
sampled order.

**Idempotents of M_4(F_2).** A matrix is a 16-bit integer, with row r in
bits 4r through 4r+3. As that integer runs from 0 through 65535, each
matrix occurs once. The idempotents are the matrices M with M^2 = M.
There are 802. Their ranks are 1, 120, 560, 120, 1 for ranks 0 through 4.
For each of them the Gaussian rank equals the base-2 logarithm of the
number of vectors in the image. The named matrix and E_11 both occur.

**Pairs after the named matrix.** All 802 · 802 = 643204 ordered
idempotent pairs (B, C) were multiplied on the right of I + x A. Exactly
58 products equal I + x I_4. Each of those 58 has A B = B A = 0 and
C = I + A + B, and the 58 middle factors are exactly the 58 orthogonal
idempotents. The theorem already excludes any other idempotent pair. The
scan is the independent finite check that the reductions agree with the
gate product for this fixed first factor.

**Kernel and one-sided constructions.** All 512 endomorphisms of F_2^3
were tested for idempotence, and all subspaces of F_2^3 and of F_2^4 were
read off by testing every subset for closure. The projection construction
of Sections 3 and 4 reproduces the 58 kernel idempotents and the 177
matrices killing v. The zero-on-image extensions of the 58 kernel
idempotents are exactly the orthogonal matrices found by the pair scan.
Every idempotent B orthogonal to A was checked to satisfy the coefficient
identities: the linear coefficient is I, the quadratic coefficient equals
B A, the cubic coefficient equals A B A, and C^2 + C equals A B + B A.

**Stage-0 embeddings.** Each of the 58 triples was placed on the first
four coordinates of the eight-dimensional space. Because the factors are
block diagonal, with I_4 on the complementary leaf coordinates, the
product is I + x E_0. Removing the third factor of the exhibited triple
changes that product. The nine-factor three-stage word is not rebuilt.

## 6. Explicit triples

Take B = 0 and C = I + A = (0, 3, 4, 8). Both are idempotent, and the
products with A are zero. The gates are

```text
I + x A = [[1+x, 0,   0, 0],
           [x,   1,   0, 0],
           [0,   0,   1, 0],
           [0,   0,   0, 1]]

I + x C = [[1, 0,   0,   0  ],
           [x, 1+x, 0,   0  ],
           [0, 0,   1+x, 0  ],
           [0, 0,   0,   1+x]]
```

The middle factor is I. The first row of the product is (1 + x, 0, 0, 0).
The second row is x times the first row of I + x C plus the second row,
which is (x, 0, 0, 0) + (x, 1 + x, 0, 0) = (0, 1 + x, 0, 0). The last two
rows are already (0, 0, 1 + x, 0) and (0, 0, 0, 1 + x). The product is
I + x I_4. The ranks are 1, 0 and 3.

The second exhibited triple uses the kernel line spanned by e_2:

```text
B = E_33 = (0, 0, 4, 0),    C = (0, 3, 0, 8).
```

The ranks are 1, 1 and 2. All six orders multiply to I + x I_4. The
ordered triple (A, A, A) does not, and neither does (A, E_33, E_33).

The one-sided witness S of Section 4 multiplies to the target only after
the non-idempotent third factor (3, 3, 4, 8). It is not one of the 58.

## 7. Limits

The selected record remains 781451/250000000. No native caller, compiler
bill, or thin map is constructed. Profiles g = 13, q = 8 and g = 31,
q = 26 are not considered. No constant matrix R is inserted, and the
coefficient of e in a pure word is not changed. The E_11 pair census and
the even-valuation identity for the T-commutant are not rerun.

The 802-by-802 census classifies ordered idempotent triples whose first
factor is this named matrix. The coefficient theorem extends the
equivalence to every idempotent first factor, and the kernel count
extends the number 58 to every rank-1 idempotent in M_4(F_2). Those two
extensions are proofs. They are not a second census, and a census of one
matrix does not by itself prove them. Non-idempotent middle factors are
outside both statements. A failed search is not part of the argument.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package
uses that record and edits neither file.

## Credit

The question answered here is open question 2 of PR #7027, package
`research/paired-star-valuation-one-factor`, head
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`. That package classified the
E_11 slice and proved that orthogonal idempotents multiply to I + x I.
The paired-star coordinates and the operator E_0 are from PR #5747
(Ali Romman), as recorded in `research/paired-star-three-full-calls` and
`research/coupled31-chronology`. The T-commuting projector obstruction
that led to PR #7027 is PR #6956. Prepared by unpaidmoon with substantial
Cursor Grok assistance. Independent human review and a proof-assistant
proof are unclaimed. Apache-2.0.
