# Constant insertions after stage-0 E_22 and stage-1 E_11

No new kappa. In the nine-gate diagonal word of PR #7027, place constant
matrices `R` and `S` in the gap after stage-0 `E_22` and the gap after
stage-1 `E_11`. Over `F_2`, the coefficient of `e` equals the pure product
`P` for exactly `2^30` pairs. Every such coefficient has diagonal entries in
`{0, P_ii}`, and each `P_ii` differs from `1`, so the coefficient is never
`I`. The selected frontier stays `363005817/100000000000`.

This is an identity in `F_2[x, y, z][e]/(e^2)`. It is not a listing of the
`2^30` pairs, not the adjacent stage-0 classification of PR #7103, and not
a kappa improvement.

## 1. Hypotheses

The ring is `F_2[x, y, z][e]/(e^2)` with `e` central. The space has eight
coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7)
 = (core_0, core_1, leaf0_0, leaf0_1, leaf1_0, leaf1_1, leaf2_0, leaf2_1).
```

The historical labels `E_11` and `E_22` are the stage gates on coordinates
`0` and `1`. A witness written `E_{i,j}` below uses these same coordinates:
a one in row `i`, column `j`. That is the coordinate convention of the
`E_02` witness in PR #7103.

Stage `s` uses the indeterminate `x_s`, written `x, y, z` for stages
`0, 1, 2`. Its three diagonal gates, in order, are

```text
I + x_s E_11,    I + x_s E_22,    I + x_s (E_33 + E_44),
```

supported on coordinate `0`, coordinate `1`, and leaf `s`. The word is
stage 0, then stage 1, then stage 2. All nine gates are diagonal, so they
commute. Their product `P` is diagonal, with entries

```text
P_00 = P_11 = (1 + x)(1 + y)(1 + z),
P_22 = P_33 = 1 + x,
P_44 = P_55 = 1 + y,
P_66 = P_77 = 1 + z.
```

Each entry is nonzero and is not `1`. The two insertions are constant
matrices over `F_2`: entries in `{0, 1}`, with no positive degree. They
occupy only the two named gaps. The equation under test is that the
coefficient of `e` equals `P`.

## 2. The two slots

Number the gates `G0, ..., G8` in the order above. Stage-0 `E_22` is `G1`.
Stage-1 `E_11` is `G3`. The word under test is

```text
G0 G1 (I + e R) G2 G3 (I + e S) G4 G5 G6 G7 G8.
```

PR #7103 inserts after `G0` and `G1` instead. These are different slots:
the gates strictly between the insertions here are `G2` and `G3`, namely
the stage-0 leaf gate and stage-1 `E_11`.

Because `e^2 = 0` and `e` is central, the coefficient of `e^0` is `P` for
every `R` and `S`. Write

```text
L = G0 G1,    M = G2 G3,    T = G4 G5 G6 G7 G8.
```

The coefficient of `e` is

```text
C = L R (M T) + (L M) S T.
```

There is no `R S` term. On coordinates, the diagonals are

```text
L = diag(1+x, 1+x, 1, 1, 1, 1, 1, 1),
M = diag(1+y, 1, 1+x, 1+x, 1, 1, 1, 1),
T = diag(1+z, (1+y)(1+z), 1, 1, 1+y, 1+y, 1+z, 1+z).
```

Every entry of `L`, `M` and `T` is a product of terms `1` and `1` plus one
indeterminate, hence nonzero in the integral domain `F_2[x, y, z]`. The
product `L M T` is the closed form of `P`.

## 3. The entry formula

Diagonal matrices act by scaling rows and columns. For `i, j` in `0..7`,

```text
C_ij = L_i (M_j T_j) R_ij + (L_i M_i) T_j S_ij
     = c_ij (M_j R_ij + M_i S_ij),
```

where `c_ij = L_i T_j` is nonzero. Therefore `C_ij` depends only on the
pair `(R_ij, S_ij)`. Matrix multiplication is bilinear, so a constant
matrix, being the sum of its occupied units, has the entry stated by this
formula at every position.

`P` is diagonal, so `C = P` if and only if `C_ii = P_ii` and `C_ij = 0`
for `i ≠ j`. On the diagonal, `M_i` appears twice and
`c_ii M_i = P_ii`, so

```text
C_ii = (R_ii + S_ii) P_ii.
```

Cancel the nonzero factor `P_ii`. The diagonal condition is

```text
R_ii + S_ii = 1    for every coordinate i.
```

Off the diagonal, cancel the nonzero factor `c_ij`. The condition is

```text
M_j R_ij + M_i S_ij = 0.
```

## 4. Which constant pairs work

The middle diagonal takes three values,

```text
M_0 = 1+y,
M_2 = M_3 = 1+x,
M_1 = M_4 = M_5 = M_6 = M_7 = 1.
```

These values are pairwise distinct, and each sum of two distinct values is
nonzero:

```text
1 + (1+x) = x,
1 + (1+y) = y,
(1+x) + (1+y) = x + y.
```

For bits `r, s` in `{0, 1}` the linear combination `M_j r + M_i s` is
`0`, `M_j`, `M_i`, or `M_i + M_j`.

- If `M_i = M_j`, the combination is `M_i (r + s)`. It vanishes if and
  only if `r = s`. Both bits may be `0`, or both may be `1`.
- If `M_i ≠ M_j`, each of `M_i`, `M_j` and `M_i + M_j` is nonzero, so the
  only solution is `r = s = 0`.

The level sets of `M` are `{0}`, `{2, 3}` and `{1, 4, 5, 6, 7}`. The
off-diagonal positions inside a level set are

```text
{2, 3}:                 (2, 3), (3, 2)                         2 positions,
{1, 4, 5, 6, 7}:        5 · 4 ordered pairs                   20 positions,
{0}:                    no off-diagonal position               0 positions.
```

That is `22` positions. The other `56 - 22 = 34` off-diagonal positions
are forced to `0` in both matrices. The free data are the eight diagonal
bits of `R`, with `S_ii = 1 + R_ii`, and one bit on each of the `22`
matched positions, copied into both matrices. The count is

```text
2^(8 + 22) = 2^30.
```

The same count is the product of the per-position solution counts:
`2` choices on each of `30` positions and `1` choice on each of the other
`34`. The product equals the number of matrix pairs because each entry
pair `(R_ij, S_ij)` appears in only one equation.

The solution set contains `(I, 0)` and `(0, I)`. It also contains pairs
with both matrices nonzero. Two examples, with `E_{i,j}` the coordinate
unit named above, are

```text
R = I + E_{1,4},    S = E_{1,4},
R = I + E_{2,3},    S = E_{2,3}.
```

Coordinates `1` and `4` lie in the level set of `1`. Coordinates `2` and
`3` lie in the level set of `1+x`. The pair
`R = I + E_{1,4} + E_{4,1}`, `S = E_{1,4} + E_{4,1}` is a third solution:
the two off-diagonal equations do not interact.

## 5. The coefficient is never the identity

For any constant pair, and at every coordinate,

```text
C_ii = (R_ii + S_ii) P_ii
```

is either `0` or `P_ii`. Section 1 records that every `P_ii` differs from
`1`. Every diagonal entry of `C` therefore differs from `1`, so `C` is
never `I`. This is the diagonal obstruction PR #7039 recorded for any
finite number of constant insertions. These two gaps do not remove it.

## 6. What the checker establishes

`verify.py` rebuilds the nine diagonals and checks the literal supports of
`G0`, `G1`, `G2` and `G3`. It checks that their matrix product is the
closed form of `P`, that `M` is the diagonal displayed in section 2, and
that `L M T = P`. For all `64` positions it checks

```text
a_ij = c_ij M_j,    b_ij = c_ij M_i,    c_ij ≠ 0,
```

and that `a_ij = b_ij` if and only if `M_i = M_j`. It multiplies all `64`
matrix units in each gap and checks that the resulting coefficient is that
single scale. It then solves all four constant bit pairs at all `64`
positions and checks that the solution sets are exactly the ones in
section 4. The witnesses of section 4 are multiplied directly, and the
blocked position `(0, 2)`, an unequal matched bit, and a mixed
matched-plus-blocked pair are rejected.

The position `(0, 2)` is free in the PR #7103 pair and blocked here. The
position `(1, 4)` is blocked there, because it meets coordinate `1`, and
free here. The solution count `22 + 8` is not the count `42 + 8` of that
package. Those checks separate the two classifications.

## 7. Limits

The hypotheses are the two named slots, constant `F_2` entries, and the
nine diagonal gates in this order. A polynomial entry such as
`R_{0,1} = 1+y` and `S_{0,1} = 1` satisfies the single blocked equation at
`(0, 1)` and is outside this count. Another pair of the ten slots has its
own middle diagonal. PR #7191 classifies polynomial entries in the two
stage-0 gaps of PR #7103; it does not classify this pair. The
non-idempotent factor `N` of PR #7027 is a different stage-0 gate. This
identity is at `g = 3`, `d = 2`. It does not supply a word for `g = 13` or
`g = 31`, and it does not change the selected frontier.

Evidence class: a proof of the entry formula and of the constant solution
set, with the scalar equations solved exhaustively on a domain of four bit
pairs. It is not a heuristic search, and it is not an enumeration of the
`2^30` matrices.
