# A finite binary certificate for the sharp Eisenstein scalar cost

## Claim and inherited model

Fix the 40 two-dimensional port planes in Q^8 from the pinned PR798 geometry.
Port i has the ordered integer generators r_i and Jr_i.
For a support R, let X_R be the rational span of its port planes.
For any rational row bases V_R and V_A, define

```
c(R,A) = rank_Q(V_R V_A^T)/2.
```

Let B be any binary 40-by-40 matrix with diagonal one and B_ij=0 for distinct nonorthogonal ports.
Allow arbitrary values at orthogonal pairs, with no symmetry requirement.
For every finite decomposition over F2,

```
B = sum_j 1_Rj 1_Aj^T,
C = sum_j c(R_j,A_j),
```

we independently certify C>=40, with equality from the known row-star decomposition.
Empty supports, arbitrary overlap, cancellation and any finite number of totals are allowed.
This is the scalar theorem of Jose Manuel / PR2017, not a new numerical bound.
Its physical interpretation still requires the additive pairing-charge premise.
We do not claim a supplier, a new kappa, a nonlinear-message theorem, or a complete multiplication theorem.

## Binary witness criterion

Let L be an 80-by-80 matrix over F2, with rows and columns grouped into two-bit port blocks.
For port sets R,A, let L[R,A] denote its entire corresponding block submatrix.
The following three properties suffice:

1. Every diagonal two-by-two block is I_2.
2. Every block at a distinct orthogonal port pair is zero.
3. For every pair of supports, rank_F2 L[R,A] <= 2c(R,A).

To see this, mask the block (i,j) of L by B_ij.
Properties 1 and 2, together with the fitting conditions on B, make the result I_80.
If D_R selects both coordinate rows at every port in R, distributivity gives

```
I_80 = sum_j D_Rj L D_Aj  over F2.
```

The j-th summand has rank rank_F2 L[R_j,A_j].
Rank subadditivity and property 3 yield

```
80 <= sum_j rank_F2 L[R_j,A_j] <= 2 sum_j c(R_j,A_j).
```

This proof uses binary matrix rank directly.
It does not use a Hermitian radical comparison, an extension-field rank routine, or a claim that ranks survive specialization unchanged.
The witness comes from PR2017, whose proof uses the related Hermitian reduction argument.
The new contribution is an independent finite certificate of the entire support-pair inequality and this direct binary proof route.

## The concrete witness

CERTIFICATE.json supplies all 80 integer-encoded bit rows of L.
For representatives r_i,r_j, set

```
u = <r_i,r_j>/4,
v = <r_i,Jr_j>/4,
a = (u-v) mod 2,
b = u mod 2,
L_ij = [[a,b],[b,a+b]]  over F2.
```

All input dot products here are divisible by four; the checker verifies this.
This is the binary regular representation of the normalized Eisenstein Gram value in PR2017.
Its denominator is three, which becomes one modulo two.
We credit that construction and do not claim a new reduction map.

The verifier checks every diagonal and orthogonal block directly against the pinned geometry.
The proof only needs the resulting finite matrix and its verified properties.
It does not require trusting the formula as a symbolic field homomorphism.
The full binary matrix has rank eight, but that fact alone does not establish property 3.

## Why the flat-pair check covers every support

A flat here is the set of all ports whose planes lie in one line-spanned rational subspace.
Given any support R, let F be its flat closure. Then X_R=X_F.
For A with closure G, the pairing charge is c(R,A)=c(F,G).
L[R,A] is a submatrix of L[F,G], so its rank cannot exceed the larger rank.
Consequently, checking

```
rank_F2 L[F,G] <= rank_Q(V_F V_G^T)
```

for every flat pair proves property 3 for every support pair.
This is a proof of coverage; we do not infer coverage from matching counts alone.

The coordinate generator verifies J^2+J+I=0.
The polynomial t^2+t+1 is irreducible over Q, so each port plane has no nonzero proper J-invariant rational subspace.
Every span of ports is J-invariant.
Adding a port therefore increases its rational dimension by either zero or two.
Every proper span has a basis of at most three port planes.

Our traversal enumerates every one-, two- and three-port generator set: 40+780+9880=10700 sets.
It adds the zero space and one full-rank four-port basis for Q^8.
Every proper span appears in that traversal, and Q^8 is the only rank-four span.
For each span, exact membership recovers its complete port closure.
Deduplication uses exact canonical spans, not sampled similarities.
The result has 772 flats, with ranks `{0:1, 1:40, 2:330, 3:400, 4:1}`.

The primary PR2017 verifier compares 209 boundary or sampled support blocks.
Our traversal and complete pair coverage do not use that sample list or its field arithmetic.
Both checks share the pinned coordinate generator as input.

## Why the prime computations are exact over Q

The independent implementation uses the prime p=2147483647.
It verifies primality by trial division and checks p>8^8.
Every original root row has squared Euclidean norm eight.

For the root matrices, Hadamard bounds each minor of size at most eight by `(sqrt(8))^8=4096`.
A nonzero integer minor cannot vanish modulo p.
Hence all generator ranks, membership decisions, and span equalities agree with rational arithmetic.
This also prevents modular deduplication from identifying different rational spans.

For a cross Gram matrix between original root-row bases, Cauchy–Binet and Cauchy–Schwarz give

```
|det(R A^T)| <= sqrt(det(R R^T) det(A A^T)) <= 8^k
```

for any selected k rows on each side.
Here k<=8, so every minor has absolute value at most 8^8=16777216<p.
The modular cross-Gram rank therefore equals its rational rank exactly.
This bound applies to original integer root rows.
The checker retains those rows as each flat's basis; it does not apply the bound to scaled rational echelon rows.

The binary side uses XOR elimination on the explicit 80-bit witness rows.
A row-space basis may be computed before selecting columns: projection is linear and preserves the span of projected rows.
Thus the small masked-basis computation has exactly the rank of the original block submatrix.

## Completed certificate

The verifier computes 298378 unordered rational flat-pair ranks.
It checks both binary orientations directly, covering all 595984 ordered flat pairs.
Rational transposition preserves rank; it does not need a second rational calculation.
Every binary bound passes.

The table uses normalized ranks: rational pairing rank divided by two, and binary block rank divided by two.
Counts refer to unordered pairs, including diagonal pairs.

| Pairing charge | Binary half-rank | Pairs |
|---:|---:|---:|
| 0 | 0 | 2057 |
| 1 | 1 | 43580 |
| 2 | 1 | 8010 |
| 2 | 2 | 171210 |
| 3 | 2 | 14940 |
| 3 | 3 | 58580 |
| 4 | 4 | 1 |

There are 22950 strict drops. Therefore replacing rank domination by rank equality would be false.
For example, use zero-based reader ports {3,4} and source ports {5,12}.
Their original rational cross Gram and binary block matrices are

```
Q = [[ 4,-4, 4,-4],       L = [[0,1,0,1],
     [ 0, 4, 0, 4],            [1,1,1,1],
     [ 4, 0,-4, 0],            [1,1,1,1],
     [-4, 4, 4,-4]]            [1,0,1,0]].
```

The integer determinant of Q is 1024, so its rank is four.
L has rank two. This corroborates the strict inequality on a concrete pair.
PR2017 correctly uses an inequality; this is not a correction to its proof.

For the upper bound, each row star contains its own port and only orthogonal ports.
Its rational cross pairing has rank two, hence cost one.
The 40 row stars recover any fitting matrix and give C=40.
The verifier checks the dense row-star witness and its masked identity.

## Controls, attribution and limits

The checker rejects diagonal corruption and a nonzero orthogonal block.
The alternative matrix I_80 passes the diagonal/zero pattern but fails pairing domination on the full pair.
This control separates the indispensable rank bound from the fitting identity.
The checker rejects an insufficient modulus and a halved rational pairing bill.
Source and certificate mutation checks exercise the stored-input bindings.
No check relies on Python assert statements.

The universal decomposition claim combines a finite certificate with the explicit coverage and rank-subadditivity arguments above.
It is not a proof-assistant certificate. Independent human review of this new package remains absent.
No selected frontier, physical pricing premise, or inherited multiplication assumption changes.

Jose Manuel / PR2017 supplies the sharp theorem and normalized Gram witness.
Jonathan Lam / PR798 supplies the pairing model, geometry and row-star upper bound.
Joel Pulikkan / GamingPuzzled / PR620 supplies the underlying order-three construction.
DreamingOfClouds / PR1590 supplies the predecessor same-field Schur-rank method credited by PR2017.
The new exhaustive checker and binary proof exposition use substantial OpenAI Codex assistance.
New work is Apache-2.0; predecessor files and notices remain unchanged.
