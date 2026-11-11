# A constant insertion beside the non-idempotent factor N

No new kappa. The selected frontier stays 363005817/100000000000.

PR #7027 exhibits a non-idempotent 4-by-4 matrix `N` over `F_2` whose gate
`I + x N` is the leading factor of a triple multiplying to `(1 + x) I_4`.
One matrix `R` is inserted immediately beside that gate, with `e` central and
`e^2 = 0`. The coefficient of `e` is never `I`. On the exhibited stage-0
triple, the same coefficient equals `(1 + x) I_4` if and only if `R = I_4`.

The evidence is split by class:

1. A proof, for every trailing matrix, that the right-hand insertion has
   `(0, 0)` entry in the principal ideal `(1 + x)`. The identity is therefore
   impossible for every matrix `R` with entries in `F_2[x, y, z]`.
2. A proof, by exact cancellation in that integral domain, that the exhibited
   stage-0 triple has coefficient `(1 + x) I_4` if and only if `R = I_4`, on
   either side.
3. An exhaustive finite census of the `65,536` constant 4-by-4 matrices, on
   both sides. The domain is finite, every bit pattern is visited once, and
   the count is the whole domain.
4. A proof that the same one insertion, read in the eight-dimensional word
   obtained by embedding the triple on stage 0, never has coefficient `I_8`.
   This is not a census of the `2^64` constant 8-by-8 matrices.

The diagonal entry formula of PR #7039 and PR #7103 is not used. `N` is not
diagonal, and the formula is false for this gate.

## 1. Hypotheses

The scalar ring is `F_2[x, y, z]`. It is an integral domain. The homomorphism
onto `F_2` given by `x ↦ 1`, `y ↦ 0`, `z ↦ 0` will be called evaluation at
`(1, 0, 0)`. The scalar `e` is central and `e^2 = 0`. A constant matrix has
entries in `F_2`. The coefficient of `e` is the degree-1 term in the quotient
by `e^2`.

The exhibited factor, copied from the bit rows in PR #7027, is

```text
N = [[1, 0, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],
B = E_22,
C = [[0, 0, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 1]].
```

Bit `c` of row `r` is the entry `(r, c)`, so these are the rows
`(1, 4, 0, 0)`, `(0, 2, 0, 0)` and `(0, 4, 4, 8)`. Then `N^2 = E_11`, so `N`
is not idempotent. The eight-dimensional coordinates are

```text
(core_0, core_1, leaf0_0, leaf0_1, leaf1_0, leaf1_1, leaf2_0, leaf2_1).
```

Stage `j` uses the core together with leaf `j`. Embedding a 4-by-4 matrix on
stage 0 writes it on coordinates `(0, 1, 2, 3)`.

## 2. The expansion

Row 0 of `N` is `(1, 0, 0, 0)`, so

```text
I + x N = [[1 + x, 0, 0, 0],
           [0,     1, x, 0],
           [0,     0, 1, 0],
           [0,     0, 0, 1]].
```

For an arbitrary matrix `M` of the same size,

```text
(I + x N)(I + e R) M = (I + x N) M + e (I + x N) R M.
```

The coefficient of `e` is `K = (I + x N) R M`. Its `(0, 0)` entry uses only
row 0 of `I + x N`:

```text
K_00 = (1 + x) (R M)_00.
```

The product `(R M)_00` lies in `F_2[x, y, z]`. Evaluation at `(1, 0, 0)`
sends `1 + x` to `0` and sends `1` to `1`, so `(1 + x) f = 1` has no
solution. Therefore `K` is not the identity.

The trailing factor `M` is arbitrary. It may be `I`, the exhibited product
`(I + x B)(I + x C)`, or the product of every later gate in the embedded
word below. No choice of those gates removes the factor `1 + x`.

The same row survives embedding. On coordinates `(0, 1, 2, 3)` the embedded
gate still has row 0 equal to `(1 + x)` times the first standard basis
covector. For every 8-by-8 trailing matrix, the coefficient of a right-hand
insertion therefore has `(0, 0)` entry in the ideal `(1 + x)`, and is not
`I_8`.

This is the expansion the question asks for. It does not depend on the
diagonal identity.

## 3. The exhibited stage-0 triple

Direct multiplication gives

```text
(I + x B)(I + x C) = [[1, 0, 0,       0    ],
                      [0, 1+x, x+x^2, 0    ],
                      [0, 0,   1+x,    0    ],
                      [0, 0,   0,      1+x  ]]
```

and `(I + x N)` times that matrix is `(1 + x) I_4`. Write `M` for the
displayed product.

**Left insertion.** The coefficient in `(I + e R)(I + x N) M` is
`(1 + x) R`, because `(I + x N) M = (1 + x) I_4`. The equation
`(1 + x) R = I_4` asks `(1 + x) R_00 = 1`, which section 2 forbids. The
equation `(1 + x) R = (1 + x) I_4` is `(1 + x)(R_ij - δ_ij) = 0`. The
multiplier is nonzero, so `R = I_4` is the only solution in
`F_2[x, y, z]`.

**Right insertion.** Let `Q = (I + x N) R` and `K = Q M`. The shapes above
give

```text
Q_0j = (1 + x) R_0j,
Q_1j = R_1j + x R_2j,
Q_2j = R_2j,
Q_3j = R_3j,
```

and then

```text
K_i0 = Q_i0,
K_i1 = (1 + x) Q_i1,
K_i2 = x(1 + x) Q_i1 + (1 + x) Q_i2,
K_i3 = (1 + x) Q_i3.
```

In entries, with `π = 1 + x`,

```text
K_00 = π R_00
K_10 = R_10 + x R_20
K_20 = R_20
K_30 = R_30
K_01 = π^2 R_01
K_11 = π R_11 + x π R_21
K_21 = π R_21
K_31 = π R_31
K_02 = x π^2 R_01 + π^2 R_02
K_12 = x π R_11 + x^2 π R_21 + π R_12 + x π R_22
K_22 = x π R_21 + π R_22
K_32 = x π R_31 + π R_32
K_03 = π^2 R_03
K_13 = π R_13 + x π R_23
K_23 = π R_23
K_33 = π R_33.
```

Every identity is an equality in `F_2[x, y, z]`, not a sample of monomials.
In characteristic two, `π^2 = 1 + x^2` and `x π = x + x^2`.

The identity `K = I_4` requires `K_00 = π R_00 = 1`, which is impossible.
The remaining fifteen entries are not needed for that conclusion.

The identity `K = π I_4` cancels in the following order. Each pivot is a
nonzero element of `F_2[x]`, and the ring is an integral domain, so the
quotient is unique in `F_2[x, y, z]`.

```text
K_20 = R_20 = 0
K_30 = R_30 = 0
K_10 = R_10 + x R_20 = 0          so R_10 = 0
K_00 = π R_00 = π                 so R_00 = 1
K_21 = π R_21 = 0                 so R_21 = 0
K_31 = π R_31 = 0                 so R_31 = 0
K_11 = π R_11 + x π R_21 = π      so R_11 = 1
K_23 = π R_23 = 0                 so R_23 = 0
K_13 = π R_13 + x π R_23 = 0      so R_13 = 0
K_33 = π R_33 = π                 so R_33 = 1
K_01 = π^2 R_01 = 0               so R_01 = 0
K_03 = π^2 R_03 = 0               so R_03 = 0
K_02 = x π^2 R_01 + π^2 R_02 = 0  so R_02 = 0
K_22 = x π R_21 + π R_22 = π      so R_22 = 1
K_32 = x π R_31 + π R_32 = 0      so R_32 = 0
K_12 = x π R_11 + x^2 π R_21 + π R_12 + x π R_22 = 0
```

The last equation reduces to `π R_12 = 0` after the earlier values are
substituted, because the two copies of `x π` cancel. Thus `R_12 = 0`. Every
entry has been determined, and `R = I_4`.

The same calculation shows where the diagonal identity stops applying.
That identity would require `K_11 = π R_11`. The formula here is
`K_11 = π R_11 + x π R_21`. The matrix unit `E_21` has `K_11 = x π`, which
is not zero. PR #7039 records that its diagonal argument does not cover this
factor. The `(0, 0)` entry is a different computation, using row 0 of `N`
rather than diagonality of every gate.

The left-hand and right-hand statements are the two readings of "beside".
The right-hand expansion is the one the question names first. Both use the
same factor `N` and the same two remaining stage-0 gates.

Any other middle matrix `B'` with `C' = I + N + B'` and
`(I + x N)(I + x B')(I + x C') = (1 + x) I_4` has the same two obstructions
to coefficient `I_4`: the right-hand `(0, 0)` entry is covered by section 2
for every trailing matrix, and the left-hand coefficient is `(1 + x) R`
because the pure product is `(1 + x) I_4`. This package does not recount the
128 middle matrices of PR #7027. It also does not classify, for a
non-exhibited companion, the solutions of coefficient `(1 + x) I_4`.

## 4. The constant census

A constant 4-by-4 matrix is an integer from `0` through `65,535`, with row
`r` stored in bits `4r` through `4r + 3`. Each of the `2^16` matrices occurs
once. Nothing stops early.

On the right of `N`, and on the left, the number of these matrices whose
coefficient equals `I_4` is `0`. The number whose coefficient equals
`(1 + x) I_4` is `1`, and that matrix is `I_4`, on each side.

The zero matrix has coefficient `0`. The matrix `I_4 + E_01` does not have
coefficient `(1 + x) I_4`. Those are controls. The census agrees with
sections 2 and 3 on the constant subdomain. It is not a substitute for the
polynomial argument, and the polynomial argument is not a sampling of the
census. The degree checks in `verify.py` exercise the division routine; they
are not a degree cutoff in the theorem.

## 5. The embedded three-stage word

Replace the three diagonal stage-0 gates of the nine-gate word by the
embedded factors `N`, `B` and `C`, in that order, and keep the six diagonal
gates of stages 1 and 2. Stage 1 multiplies by `1 + y` on coordinate `0`,
then on coordinate `1`, then on coordinates `4` and `5`. Stage 2 does the
same with `1 + z` on coordinates `0`, `1`, `6` and `7`.

The stage-0 product is `I + x E_0`. The full pure product `P` is therefore
the same diagonal operator as in the nine-gate word:

```text
P_00 = P_11 = (1 + x)(1 + y)(1 + z),
P_22 = P_33 = 1 + x,
P_44 = P_55 = 1 + y,
P_66 = P_77 = 1 + z.
```

**Right insertion, immediately after the embedded `I + x N`.** Section 2
already excludes coefficient `I_8`. For this particular tail, column 0 is
`(1 + y)(1 + z)` times the first basis vector, so the general formula
specialises to

```text
K_00 = (1 + x)(1 + y)(1 + z) R_00.
```

Evaluation at `(1, 0, 0)` sends the right-hand side to `0`. The same
conclusion holds for a polynomial entry `R_00`, not only for a bit.

**Left insertion, with `N` first.** The coefficient is `R P`. Since `P` is
diagonal, `K_00 = R_00 P_00`, and `P_00` is the same nonunit. The coefficient
is not `I_8`.

Both statements are bilinear, so they are checked on the 64 matrix units and
then extended by the ring action. A sum of two units is checked directly as a
control. This unit check is not an enumeration of `M_8(F_2)`.

The pure-product equation `K = P` is not solved. Its column 0 is. On the
right, that column is

```text
K_00 = (1 + x)(1 + y)(1 + z) R_00,
K_10 = (1 + y)(1 + z) (R_10 + x R_20),
K_20 = (1 + y)(1 + z) R_20,
K_30 = (1 + y)(1 + z) R_30,
K_i0 = (1 + y)(1 + z) R_i0    for i = 4, 5, 6, 7.
```

`P` has `(1 + x)(1 + y)(1 + z)` in position `(0, 0)` and zeros below it.
Cancelling the nonzero factor `1 + y + z + y z` forces `R_00 = 1`,
`R_20 = 0`, hence `R_10 = 0`, and `R_i0 = 0` for every `i > 0`. Column 0 of
`R` is the first standard basis vector. The other seven columns are open.

## 6. Limits

The selected record remains `363005817/100000000000`. No native caller,
compiler bill, or thin map is constructed. Profiles `g = 13` and `g = 31`
are not considered. PR #6956 is not rerun.

The result is not the two-gap classification of PR #7103, and it is not the
polynomial count of PR #7191. Those papers insert constants or linear
polynomials into the diagonal word. The factor here is `N`.

A matrix over the rational function field is outside the statement. The
scalar matrix `(1/(1 + x)) I_4` satisfies `(1 + x) R = I_4` in that larger
ring, which is why the obstruction is that `1 + x` is not a unit. It is not
a solution in `F_2[x, y, z]`.

`current-priorities.md` at this base can still print an older decimal. The
live selected record is `363005817/100000000000`, from
`certificates/selected-result.json`. This package uses that record and edits
neither file. PR #7027, PR #7039 and PR #7103 name the previous fraction
`781451/250000000`; that is not the frontier this package is measured
against, and this package does not move either value.

## Credit

The paired-star contract, the operator `T`, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617. The
T-commuting projector obstruction is PR #6956. The factor `N`, the triple,
and the embedding convention are PR #7027, head
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`. The diagonal obstruction for the
idempotent gates, and the statement that it does not cover `N`, are PR
#7039, head `e4ddcd2fde8c46b7e528e8806ab72d9bf7690978`. The question answered
here is open question 3 of PR #7103, which is the same non-idempotent slot
already named as question 2 of PR #7039. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Independent human review and a
proof-assistant proof are unclaimed. Apache-2.0.
