# A constant insertion beside the valuation-1 factor

No new kappa. The selected frontier stays 781451/250000000.

The nine diagonal gates recorded in PR #7027 multiply to the pure operator
`product_j (I + x_j E_j)`. One constant matrix `R` may be inserted beside the
stage-0 factor `I + x E_11`. The pure product does not move. The coefficient
of `e` is never the identity. The coupled31 operator `(I + e I)` times that
pure product is a different equation, and for this one slot it holds exactly
when `R = I`.

The evidence is split by class:

1. A proof, using that `F_2[x, y, z]` is an integral domain, for every matrix
   whose entries lie in that polynomial ring.
2. An exhaustive finite census of the 65,536 constant 4-by-4 matrices on the
   stage-0 block, and of their 65,536 embeddings into the eight-dimensional
   space. The census domain is finite, every element is visited, and the
   count is the whole domain.

The proof covers every constant 8-by-8 matrix. Those `2^64` matrices are not
enumerated. A failed search is not an ingredient.

## 1. Hypotheses

Keep the idempotent triple and the coordinate convention of PR #7027. The
stage-0 block is four-dimensional over `F_2`, with

```text
A = E_11,    B = E_22,    C = E_33 + E_44.
```

These are orthogonal idempotents, and `(I + x A)(I + x B)(I + x C) = I + x I_4`.
`E_11` is the projector onto the first coordinate. The eight-dimensional
space has coordinates

```text
(core_0, core_1, leaf0_0, leaf0_1, leaf1_0, leaf1_1, leaf2_0, leaf2_1).
```

Stage `j` uses the core together with leaf `j`. The nine gates are the three
idempotents on each stage, in stage order `0, 1, 2` and, within a stage,
`E_11`, `E_22`, then `E_33 + E_44`. Each gate is diagonal. Their product `P`
is diagonal, with

```text
(1 + x)(1 + y)(1 + z)    on the core,
1 + x                    on leaf 0,
1 + y                    on leaf 1,
1 + z                    on leaf 2.
```

That is `product_j (I + x_j E_j)`. The scalar `e` satisfies `e^2 = 0` and is
central. A constant matrix has entries in `F_2`. A polynomial matrix has
entries in `F_2[x, y, z]`. One insertion is the adjacent factor `I + e R`,
on the left or on the right of the embedded gate `I + x E_11`.

The coefficient of `e` means the matrix of the degree-1 term in
`F_2[x, y, z][e] / (e^2)`. The identity `I` is the constant identity matrix.
The coupled31 target from `research/coupled31-chronology/PROOF.md` is
`(I + e I) P`, whose coefficient of `e` is `P`, not `I`.

## 2. The stage-0 expansion

On the four-dimensional block,

```text
(I + x E_11)(I + e R) = I + x E_11 + e (I + x E_11) R.
```

The coefficient of `e` is `(I + x E_11) R`. Its first row is `(1 + x)` times
the first row of `R`. The identity has first row `(1, 0, 0, 0)`, so the
`(0, 0)` entry would be `(1 + x) R_00 = 1`. In `F_2[x]` the polynomial `1 + x`
is not a unit, and `R_00` would have to be its inverse. No polynomial, and
in particular no constant, satisfies that equation. The left insertion
`(I + e R)(I + x E_11)` has the same obstruction in column 0.

The other two stage gates do not remove it. They are the identity on the
first coordinate, so in

```text
(I + x E_11)(I + e R)(I + x E_22)(I + x C)
```

the `(0, 0)` entry of the coefficient is still `(1 + x) R_00`. The local
pure product is `(1 + x) I_4`. For a constant `R`, that local equation holds
on either side of `E_11` exactly for `R = I_4`. The same count holds for the
left side, where the coefficient is `R (I + x I_4)`.

This local identity does not decide the eight-dimensional word. The gates of
the other stages still scale the entries. Embedding `I_4` by zeros off the
stage-0 coordinates is a different matrix from `I_8`.

## 3. The diagonal identity

Let the nine gates be `G_0, ..., G_8`, with `G_0 = I + x E_11`, and write
`P = G_0 ... G_8`. Every `G_s` is diagonal, and `F_2[x, y, z]` is an integral
domain. For a polynomial matrix `R` placed immediately on the right of `G_0`,

```text
G_0 (I + e R) G_1 ... G_8 = P + e (G_0 R G_1 ... G_8).
```

The left and right factors are diagonal, so the coefficient `C` has

```text
C_ij = L_i R_ij Rgt_j,
```

where `L_i` is the product of the diagonal entries to the left of the slot,
including `G_0`, and `Rgt_j` is the product of those to the right. Both are
nonzero, because each gate diagonal is `1` or `1` plus one variable. On the
diagonal, `L_i Rgt_i = P_ii`. The left-hand slot has the same shape with the
factors of `G_0` moved into `Rgt`. Reordering the nine diagonal gates only
repartitions the same nonzero factors, so the diagonal identity `C_ii = R_ii P_ii`
is independent of the order and of the side.

Each `P_ii` is one of `(1 + x)(1 + y)(1 + z)`, `1 + x`, `1 + y`, and `1 + z`.
None of them is the constant `1`.

## 4. The coefficient is never `I`

Suppose `C = I`. Then `R_ii P_ii = 1` and, for `i ≠ j`, `L_i R_ij Rgt_j = 0`.
The off-diagonal multiplier is nonzero, so `R_ij = 0`. The diagonal equation
asks a nonunit to divide `1`. There is no solution in `F_2[x, y, z]`, hence
none in `F_2`.

The same diagonal reading applies to any finite number of constant insertions
among these nine gates. The contribution of an inserted constant matrix `R`
at any gap has diagonal `R_ii P_ii`, because the gates on its two sides still
multiply to `P_ii`. A sum of such terms is `c_i P_ii` with `c_i` in `F_2`.
That product is `0` or `P_ii`, never the constant `1`. Two copies of the
identity cancel in characteristic two and leave the coefficient zero. This
does not use a search over pairs of gaps.

## 5. The endpoint operator is exactly `R = I`

The coupled31 target is `(I + e I) P = P + e P`. For one insertion beside
`E_11`, this asks `C = P`, so `R_ii P_ii = P_ii` and `L_i R_ij Rgt_j = 0`
off the diagonal. The integral domain forces `R_ii = 1` and `R_ij = 0`. Thus
`R = I` is the only polynomial solution, on either side, and it is constant.
The resulting word is exactly the endpoint operator.

That decides this one insertion beside this one factor. It does not produce
a word whose factors commute with `T`, and it does not touch the three-call
obstruction in PR #6956. The unsplit call `E_j` is a different pure factor.
Profiles `g = 13` and `g = 31` are not considered.

`R = I` does not make the coefficient equal to `I`. At `x = 1`, `y = z = 0`,
the core entry of `P` evaluates to `0`, while the identity evaluates to `1`.

A matrix supported on the stage-0 block is zero on coordinates `4, 5, 6, 7`.
Diagonal gates cannot move an off-diagonal entry onto the diagonal, so those
four diagonal entries of `C` stay `0`. Both `I` and `P` are nonzero there, so
no stage-supported matrix solves either equation. The local solution `I_4`
embeds as one of those matrices and fails globally for that reason.

## 6. The finite censuses

Every completeness statement below enumerates a product domain of known
cardinality. Nothing stops early.

**Local constant matrices.** A 4-by-4 matrix over `F_2` is an integer from
`0` through `65,535`, with row `r` stored in bits `4r` through `4r + 3`.
Each matrix occurs once. On either side of `E_11` in the three-gate stage
word, zero of these matrices give coefficient `I_4`, and exactly one gives
coefficient `(1 + x) I_4`. That one matrix is `I_4`. The two-factor expansion
`(I + x E_11)(I + e R)`, and the opposite order, likewise gives coefficient
`I_4` for none of the `65,536` matrices. The 16 matrix units were multiplied
directly and agree with the row-and-column scaling.

**Stage-supported embeddings.** The same `65,536` matrices are written onto
coordinates `(0, 1, 2, 3)` and extended by zero. This is every constant
matrix supported on the stage-0 block. On either side of the embedded
`E_11` in the exhibited nine-gate order, zero of them give coefficient `I_8`
and zero give coefficient `P`. The scaling formula used for that loop was
checked by a direct product against all 64 matrix units of `M_8(F_2)`, on
both sides. The coefficient map is linear: the product for `E_00 + E_12`
equals the sum of the two unit products. Every block-supported matrix is the
sum of a subset of those units, so the formula is the product on the whole
domain, not a sample of it.

The same unit check was repeated with the nine gates reversed. There `E_11`
stands at the other end of the word, and `R = I` again has coefficient `P`.

## 7. Limits

The selected record remains `781451/250000000`. No native caller, compiler
bill, or thin-map rank is constructed. The non-idempotent leading factor of
PR #7027 is not diagonal, so Sections 3 through 5 do not apply to it. Two or
more constant insertions can still be asked for the endpoint equation
`C = P`: the diagonal obstruction kills only `C = I`, and off-diagonal scales
depend on the gap. Entries in the rational function field are outside the
polynomial statement. PR #6956 is not rerun.

`current-priorities.md` at this base still prints the older decimal
`0.00310045`. The live selected record is `781451/250000000`. This package
uses that record and edits neither file.

## Credit

The paired-star contract, the operator `T`, and the pure target are from PR
#5747 (Ali Romman), including PR #5673, PR #5631, and PR #5617, as recorded
in `research/coupled31-chronology`. The T-commuting projector obstruction is
PR #6956, `research/paired-star-three-full-calls`. The valuation-1 triple and
the open insertion question are PR #7027, head
`1ba2ac5adfe58fbe9dba34d50d4e5d30633ce3d0`. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Independent human review and a
proof-assistant proof are unclaimed. Apache-2.0.
