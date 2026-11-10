# A valuation-1 factor outside the T-commutant

No new kappa. The selected frontier stays 781451/250000000.

Over F_2, every 4-by-4 matrix that commutes with the stage operator T has even
(1+x)-valuation. Valuation 1 is therefore impossible for a T-commuting
projector and for every other T-commuting matrix. Outside that commutant,
three explicit gates multiply to the stage target I + x I_4, with valuations
1, 1 and 2. The same diagonal gates, copied onto the three overlapping stage
blocks of the eight-dimensional paired-star space, multiply to the pure
operator product_j (I + x_j E_j).

The evidence is split by class:

1. A proof of the square-determinant identity on the T-commutant, and a proof
   that an orthogonal pair of idempotents multiplies to (1+x) I.
2. An exhaustive finite census of all 65,536 matrices in M_4(F_2), of all 256
   commutant matrices, of all 802-by-802 idempotent pairs after E_11, and of
   all 65,536 middle factors after one fixed non-idempotent matrix.
3. Two explicit triples, checked by direct multiplication. The censuses are
   not a search sample, and the explicit triples are not a classification of
   every triple in M_4(F_2)^3.

PR #6956 remains in force for nonzero T-commuting projectors. This note does
not rerun that 15,625-triple census.

## 1. Hypotheses

The stage block is four-dimensional over F_2. Write 2-by-2 blocks and set

```text
T = [[I, I], [I, I]],    S = [[I, 0], [I, I]].
```

A gate is I + x M with M constant and x an indeterminate. Its (1+x)-valuation
is the largest k such that (1+x)^k divides det(I + x M) in F_2[x]. The
polynomial det(I + x M) has constant term 1, so it is never zero and the
valuation is finite. In characteristic two, (1+x)^2 = 1 + x^2 and
(1+x)^4 = 1 + x^4, so the stage target I + x I_4 has determinant 1 + x^4 and
valuation 4.

The eight-dimensional space is a core of dimension 2 plus three leaves of
dimension 2, with coordinates

```text
(core_0, core_1, leaf0_0, leaf0_1, leaf1_0, leaf1_1, leaf2_0, leaf2_1).
```

Stage j uses coordinates (0, 1) together with leaf j. The operator E_j is the
identity on those four coordinates and zero elsewhere. This is the support
used in `research/paired-star-three-full-calls`. The pure target copied from
`research/coupled31-chronology/PROOF.md` is product_j (I + x_j E_j). The full
target there is (I + e I) times that product, with e^2 = 0. This package
builds no factor I + e R.

Matrices are stored as four row bit-masks. Bit c of row r is the entry (r, c).

## 2. The T-commutant has even valuation

Let M = [[W, X], [Y, Z]]. The products T M and M T agree exactly when Y = X
and Z = W, so every commutant matrix is uniquely

```text
M = [[W, X], [X, W]].
```

Set A = W + X and B = X. Then M = [[A + B, B], [B, A + B]]. A direct block
multiplication gives S^2 = I and

```text
S M S = [[A, B], [0, A]].
```

Conjugation by S preserves the determinant, and I + x S M S is block
triangular, so

```text
det(I + x M) = det(I + x A)^2.
```

The right-hand side is a square in F_2[x] and its constant term is 1, so the
(1+x)-valuation is even. In particular it is never 1. Idempotence was not
used. A T-commuting projector is the special case already bounded in PR #6956;
the same square also excludes every non-projector in the commutant.

The 2-by-2 polynomial det(I + x A) = 1 + tr(A) x + det(A) x^2 has degree at
most 2. Its valuation is exactly 1 only for the polynomial 1 + x, because
(1+x)^2 = 1 + x^2 already has valuation 2. Trace 1 and determinant 0 give
that polynomial. With diagonal entries a and a+1, the determinant reduces to
b c, so b c = 0: three choices for (b, c) and two choices for a, hence 6
blocks. The case det(I + x A) = (1+x)^2 forces trace 0 and determinant 1.
The diagonal entries are then equal to some a, and a + b c = 1. For a = 0
only (b, c) = (1, 1) works; for a = 1 the three pairs with b c = 0 work.
That is 4 blocks. The free block B contributes 16 matrices, giving
6 * 16 = 96 commutant matrices of valuation 2 and 4 * 16 = 64 of valuation 4.
The remaining 256 - 96 - 64 = 96 matrices have valuation 0.

`verify.py` multiplies all 256 pairs (W, X). Each matrix commutes with T,
S M S equals the triangular form, and the Leibniz determinant equals both the
determinant of the triangular gate and det(I + x A)^2. The histogram is

| Valuation | 0 | 1 | 2 | 3 | 4 |
|---:|---:|---:|---:|---:|---:|
| Matrices | 96 | 0 | 96 | 0 | 64 |

Exactly 26 of the 256 matrices are idempotent, the same projector count as
PR #6956. One of them is the rank-1 call diag(1, 0, 1, 0), with valuation 2.
The non-projector [[0, A], [A, 0]] for A = E_11 also has valuation 2, so
dropping idempotence inside the commutant does not produce valuation 1.

## 3. Orthogonal idempotents

Let A and B be idempotent matrices over F_2 with A B = B A = 0, and set
C = I + A + B. In characteristic two,

```text
(A + B)^2 = A^2 + B^2 = A + B,
C^2 = (I + A + B)^2 = I + A + B = C.
```

The cross terms with I cancel because each appears twice, and A B + B A = 0.
Therefore

```text
(I + x A)(I + x B) = I + x (A + B),
(I + x A)(I + x B)(I + x C) = I + x (A + B + C) = I + x I.
```

The quadratic term is (A + B) C = (A + B) + (A + B)^2 = 0. This identity does
not use the size 4. For an idempotent P, the polynomial t(t + 1) splits into
coprime factors over F_2, so F_2^n = ker(P) + ker(P + I) as a direct sum. On
the second summand P acts as I, and that summand is the image of P. In an
adapted basis, det(I + x P) = (1 + x)^{rank(P)}. The three valuations on an
orthogonal triple therefore add to the ambient dimension.

## 4. The explicit triples

The coordinate idempotents

```text
A = E_11,    B = E_22,    C = E_33 + E_44
```

are orthogonal, with ranks 1, 1 and 2. Their gates are the diagonal matrices
diag(1+x, 1, 1, 1), diag(1, 1+x, 1, 1) and diag(1, 1, 1+x, 1+x). The product
is (1+x) I_4 in every order. The valuations are 1, 1 and 2. None of the three
commutes with T: A T has first row (1, 0, 1, 0), while T A has first row
(1, 0, 0, 0).

A second triple uses a non-idempotent leading factor

```text
N = [[1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
B = E_22,
C = [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 1]].
```

Here N^2 = E_11, so N is not idempotent. The product
(I + x N)(I + x B) is

```text
[[1+x, 0,   0, 0],
 [0,   1+x, x, 0],
 [0,   0,   1, 0],
 [0,   0,   0, 1]].
```

Multiplying on the right by I + x C clears the off-diagonal x and multiplies
the last two diagonal entries by 1+x. The product is again (1+x) I_4.
Leibniz determinants give valuations 1, 1 and 2. The leading factor does not
commute with T: N T and T N differ in position (0, 2).

Three rank-1 idempotents E_11, E_22 and E_33 have valuations 1, 1 and 1. Their
gates multiply to diag(1+x, 1+x, 1+x, 1), whose determinant has valuation 3.
Valuation additivity alone, with three 1's, cannot hit the target valuation 4.
The rank-2 third factor in the first triple is what makes the sum 4, and the
matrix product is checked directly rather than inferred from the determinants.

## 5. Finite censuses

Every completeness statement below enumerates a set that has already been
given a product structure of known cardinality. There is no early stop, no
rank pruning, and no sampled order.

**All of M_4(F_2).** A matrix is a 16-bit integer, with row r stored in bits
4r through 4r+3. As that integer runs from 0 through 65535, each of the 2^16
matrices occurs once.
For every matrix the Leibniz and Laplace expansions of det(I + x M) agree, the
constant term is 1, and the valuation lies in {0, 1, 2, 3, 4}. The histogram is

| Valuation | 0 | 1 | 2 | 3 | 4 |
|---:|---:|---:|---:|---:|---:|
| Matrices | 20160 | 20160 | 13440 | 7680 | 4096 |

The five counts add to 65,536. Exactly 20,160 matrices have valuation 1, and
none of them lie in the 256-element commutant. Among the 802 idempotents, the
valuation equals the rank in every case. The rank counts are 1, 120, 560, 120
and 1 for ranks 0 through 4. The 120 rank-1 idempotents are the valuation-1
idempotents; the other 20,040 valuation-1 matrices are not idempotent.

**Idempotent triples with first factor E_11.** There are 802 idempotents.
All 802 by 802 ordered pairs (B, C) were multiplied after E_11. Exactly 58
products equal I + x I_4. Each of those 58 has B orthogonal to E_11,
C = I + E_11 + B, and B supported on coordinates 1, 2 and 3. The same scan
finds exactly 58 idempotents with that support. Each solution determines its
middle factor, that factor is kernel-supported, and the two counts are equal,
so every kernel-supported idempotent occurs exactly once. The solution set
and the support set therefore coincide.

Those 58 matrices are the idempotents of the coordinate 3-space ker(E_11).
On F_2^3 there are (8-1)/(2-1) = 7 lines and 7 planes. A fixed line lies in
(4-1)/(2-1) = 3 planes, so it has 4 complementary planes and there are
7 * 4 = 28 rank-1 projections. Rank 2 is the complement I + P, another 28,
and ranks 0 and 3 contribute one matrix each: 28 + 28 + 1 + 1 = 58. Each such
idempotent extends by zero on the image line of E_11 and is orthogonal to
E_11, so Section 3 supplies the matching gate product. The census shows that
no other idempotent pair (B, C) works for this fixed first factor.

This is a classification only for idempotent triples whose first factor is
E_11. It is not a census of M_4(F_2)^3, whose cardinality is 2^48.

**One non-idempotent slice.** Fix the leading factor N from Section 4. For
each of the 65,536 choices of a middle matrix B, set C = I + N + B. The
coefficients of x^2 and x^3 in (I + x N)(I + x B)(I + x C) vanish if and only
if the product equals I + x I_4. Exactly 128 middle matrices pass. In 3 of
those solutions B commutes with T. In none of them does C commute with T. The
leading factor N does not commute with T, so every solution in this slice
still uses a non-commuting factor. The exhibited middle matrix E_22 is one of
the 128. The count is the size of this slice, not the number of all
non-idempotent triples.

## 6. The pure three-stage word

Embed a 4-by-4 matrix on stage j by placing its entries on the four stage
coordinates and writing zero elsewhere. In a basis that lists those
coordinates first, the embedded gate is block diagonal, with the 4-by-4 gate
in the stage block and I_4 on the complement. A 4-by-4 product equal to
I + x I_4 therefore embeds as I + x E_j.

For the diagonal triple the same conclusion is visible on coordinates. Stage 0
contributes the factor 1+x on coordinates 0, 1, 2 and 3. Stage 1 contributes
1+y on coordinates 0, 1, 4 and 5. Stage 2 contributes 1+z on coordinates
0, 1, 6 and 7. The ordered product of the nine gates is diagonal, with

```text
(1+x)(1+y)(1+z)    on the core,
1+x                on leaf 0,
1+y                on leaf 1,
1+z                on leaf 2.
```

The operators E_j are diagonal in this basis and commute, so
product_j (I + x_j E_j) has the same diagonal. The two operators are equal.
The verifier compares the embedded word, the product of the three support
gates, and this diagonal matrix of monomials. It also embeds the
non-idempotent triple on stage 0 and checks that those three gates multiply
to I + x E_0. Removing the last diagonal factor changes the nine-factor word.

The coefficient of e in this word is zero: every factor is a pure gate
I + x_j P. The coupled31 target asks for an additional factor I + e I. That
coefficient is a later question. The factors do not commute with T, so the
word is outside the full-call hypothesis of PR #5747 and PR #6956. Those
results still say that a stage built from three nonzero T-commuting projectors
misses the pure target. The word here uses a different call shape.

## 7. Limits

The selected record remains 781451/250000000. No native caller, compiler bill,
or thin map is constructed. Profiles g = 13, q = 8 and g = 31, q = 26 are not
considered. The square identity is proved for this 4-by-4 T. The idempotent
classification fixes the first factor as E_11. The count 128 fixes the leading
factor N. A failed search is not part of the argument: every finite domain
named above is enumerated completely, and the general identities are proved
before the counts.

`current-priorities.md` at this base still prints the older decimal
0.00310045. The live selected record is 781451/250000000. This package uses
that record and edits neither file.

## Credit

The paired-star contract, the operator T, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617, as recorded in
`research/coupled31-chronology`. The T-commuting projector obstruction and the
open question answered here are PR #6956,
`research/paired-star-three-full-calls`. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Independent human review and a
proof-assistant proof are unclaimed. Apache-2.0.
