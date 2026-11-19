# The full four-qubit width-ten nullity

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Use the full Gaussian-dyadic four-qubit Clifford group G, natural
representation V of dimension sixteen, Pauli subgroup P and scalar
kernel Z of order four from
[PR #7766](https://github.com/CrocSwap/integer-mult-bounds/pull/7766).
Write S=G/P=Sp(8,2) and N=|G/Z|=12,128,668,876,800.
The projective Gram matrix at tensor width ten has

```text
exact nullity = 193,919,902,208,
exact rank    = 11,934,748,974,592.
```

There are fifteen absent irreducible modules: seven from the minus
quadratic orbit and eight from the plus orbit. Their full list is below.
This resolves the width-ten question left by
[PR #7770](https://github.com/CrocSwap/integer-mult-bounds/pull/7770).
The threshold T(4)=13 is unchanged. No physical supplier or new kappa
follows.

## 1. The actual modules use Bell-line extensions

The [source quotient calculation](https://github.com/petalas/integer-mult-bounds/blob/ff12ca358d601a21cd4b1f016b8a3a969ac44016/research/clifford-four-qubit-width-nine/README.md)
gives V^9=V tensor W9, where W9 is an honest S module of dimension
2^32. If s fixes a d-dimensional subspace in the natural binary
space E, its character is 2^(4d). Thus W9 is the permutation module
on four ordered vectors of E. Its complete 81-row decomposition has
twenty absent rows and is replayed unchanged.

At width ten,

```text
V^(tensor 10) = (V tensor V) tensor W9.
```

The Pauli weight lines in V tensor V are indexed by the 256 quadratic
refinements q of the symplectic form on E. The two S orbits have sizes
120 and 136. Their stabilizers are the full orthogonal groups H_minus
and H_plus, of orders 394,813,440 and 348,364,800. The CTblLib records
for these groups are named `O8-(2).2` and `O8+(2).2`.

For each q, let T_q be the preimage of H_q in G. The actual Bell line
has a one-dimensional T_q character eta_q extending its P character.
This is the extension constructed in the
[pinned source proof, Sections 2 and 4](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md).
Its signs and Gaussian phases are part of the representation.

For each ordinary irreducible H_q module rho, define

```text
pi_(q,rho) = Ind_(T_q)^G(eta_q tensor rho).
```

These are exactly the irreducible G modules in the central-character
sector z -> -1. Each is irreducible because its distinct P weight
spaces form one orbit, and its stabilizer acts irreducibly on one
weight space. Conversely, divide one weight-space action by eta_q
to obtain an H_q irreducible, then induce. This argument needs no
splitting of the projective Clifford extension.

The degree of pi is [S:H_q] dim(rho), and its multiplicity in V^10 is

```text
m_rho = < Res_(H_q) W9, rho >.
```

The actual eta_q cancels on both sides of this weight-space comparison.
It is not an assumption that the Bell line is trivial. These two
families exhaust the central-character sector, since their squared
degrees sum to

```text
120^2 |H_minus| + 136^2 |H_plus| = (120+136)|S| = N.
```

## 2. Authenticate the two complete restriction calculations

The exact CTblLib 1.3.11 archive supplies the three ordinary tables
and both `ALF` class fusions into S8(2). `EXTERNAL.json` pins the archive
and the three table members by SHA-256. The published tables and
form-stabilizer fusions are mathematical inputs, not reconstructions
from group multiplication.

The extractor reads all 81 S rows, 60 minus rows and 67 plus rows.
It expands every tensor row and every Galois row. All values lie in
the real quadratic field represented by (a+b t)/2 with t^2=17.
The checker derives t from the seventeenth-root quadratic period,
checks its square and conjugation, and checks that Galois power three
negates it. It does not copy a Galois row as if its entries were rational.
All 14,650 ordinary row inner products pass exactly.

The fusion is checked against the actual quadratic-form permutation
characters. For every S class C,

```text
Ind_(H_minus)^S(1)(C) = 1+chi_5(C),
Ind_(H_plus)^S(1)(C)  = 1+chi_6(C),
```

where the degrees are 119 and 135. The class sizes and centralizers
in the fusion give the left sides. The pinned source gives the right
sides. The same fusion sends each stabilizer class to its natural
fixed-space dimension d. The second row of each full orthogonal
table is exactly the Dickson sign (-1)^d, which is another source
convention check.

For an H row of degree e, let A_d sum |C| rho(C) over its classes with
fixed dimension d, for 1<=d<=7. The unique d=8 class is identity.
Subtracting the constant character removes d=0 classes and gives

```text
m_rho = [rho is trivial]
      + [e(2^32-1) + sum_(d=1)^7 A_d(2^(4d)-1)] / |H|.
```

Every result is an exact nonnegative integer. Independently, the
extractor computes all 10,287 coefficients in the restrictions of
the 81 S irreducibles to the 127 H irreducibles. Every coefficient is
an exact nonnegative integer. Combining them with the source W9
multiplicities gives exactly the same 127 values. Both the restricted
and induced degree sums agree.

The sparse restriction matrix and all projected rows are retained in
`STABILIZERS.json`. The optional archive command reconstructs this
entire file, including the complete ordinary inner-product and Galois
checks. Registered replay needs only the retained data; it repeats
both multiplicity formulas, fusion checks and independent orbit tests.

## 3. The fifteen absent modules

| Quadratic type | Stabilizer row | Stabilizer degree | Clifford degree |
| --- | --- | --- | --- |
| minus | 2 | 1 | 120 |
| minus | 4 | 34 | 4,080 |
| minus | 10 | 204 | 24,480 |
| minus | 14 | 357 | 42,840 |
| minus | 22 | 714 | 85,680 |
| minus | 28 | 1,071 | 128,520 |
| minus | 43 | 2,295 | 275,400 |
| plus | 4 | 28 | 3,808 |
| plus | 6 | 35 | 4,760 |
| plus | 14 | 175 | 23,800 |
| plus | 16 | 210 | 28,560 |
| plus | 21 | 350 | 47,600 |
| plus | 25 | 567 | 77,112 |
| plus | 44 | 1,400 | 190,400 |
| plus | 46 | 1,575 | 214,200 |

The row numbers refer to the published ordinary stabilizer tables,
not to the S8(2) table. Every unlisted stabilizer row occurs. The first
minus row in the table above is the Dickson module already proved
absent by the source. The plus Dickson row has multiplicity one,
which agrees with the source's separate signed calculation.

The two missing regular-block totals are

```text
minus: 102,154,809,600,
plus:   91,765,092,608,
total: 193,919,902,208.
```

A degree-e irreducible contributes e^2 to the regular block. The
projective Gram matrix represents the central-character-minus-one
ideal; a block has positive eigenvalue exactly when its module occurs
in the tensor power. Thus the total is its full nullity, and subtraction
from N gives the stated exact rank. No other central-character blocks
belong to this Gram matrix.

## 4. An independent quadratic-space count

The character norm of W9 restricted to H equals the number of H orbits
on eight ordered vectors. This number can be counted without either
character table. More generally, encode a tuple of length k by a map
from F2^k to a quadratic space of dimension 2n. Let its image have
dimension r and its induced alternating form have radical dimension t.
The kernel has [k choose r]_2 choices. On the quotient, the number of
alternating forms of radical dimension t is

```text
B(r,t) = [r choose t]_2 |GL(r-t,2)| / |Sp(r-t,2)|,
```

where r-t is even. If r+t>2n, no embedding exists. If r+t<2n, all 2^r
quadratic refinements embed. At equality, write r-t=2s and let epsilon
be +1 for plus type and -1 for minus type. The number that embed is

```text
(2^t-1) 2^(2s) + Z_epsilon(2s),
Z_epsilon(2s) = (2^(2s)+epsilon 2^s)/2,       s>0,
Z_plus(0)=1,                                Z_minus(0)=0.
```

Here is the embedding condition. If the quadratic form is nonzero on
the alternating radical, one nonsingular radical vector can be paired
with a dual vector whose value can change the ambient Arf type. Both
types are therefore possible. If the quadratic form is zero on the
radical, the dual pairs are hyperbolic. At equality no complement
remains, so the nondegenerate part must have the ambient type. Below
equality a positive even-dimensional complement can supply either
type. The counts Z_epsilon are the usual two Arf-type counts for a
fixed nondegenerate alternating form.

Two tuples with the same kernel and induced quadratic form are related
by an ambient isometry. This follows from
[Taylor's Witt extension theorem, Theorem 7.4](https://www.maths.usyd.edu.au/u/don/papers/gcg.pdf#page=65);
the ambient polar radical is zero. Consequently the orbit count is
obtained by summing the displayed terms over r,t, multiplied by
[k choose r]_2 B(r,t).

For n=4 and k=4 the counts are 2,294 and 2,295. For k=8 they are
78,491,573,017 and 84,713,186,558. These equal the two sums of squared
multiplicities. Separate class-histogram moments give the same values.
As a finite control, the checker enumerates all four orthogonal groups
in dimensions two and four, of orders 2, 6, 72 and 120. Their direct
Burnside counts agree with the formula for every tuple length zero
through eight.

## Evidence and limits

All twenty-three retained source files are authenticated. The unchanged
source verifier includes its literal Pauli/Bell actions and threshold
calculation. Changed fusion and projected-character controls fail for
the stated reasons. The archive replay also rejects a copied Galois
row. All registered, archive and source checks use exact arithmetic.

The argument depends on the published ordinary tables and class
fusions. Their hashes, character identities, dimensions and independent
orbit counts were checked; no full four-qubit group or Gram matrix was
materialized. The full three-qubit suite, selected cold replay, Lean
and Docker were not run. Conditioning, native realization and complete
caller pricing remain open. T(4)=13, all five framework assumptions
and the selected frontier remain unchanged. No independent human,
formal-kernel acceptance or global literature priority is claimed.
