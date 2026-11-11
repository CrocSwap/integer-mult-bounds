# Constant insertions after stage-2 E_22 and the stage-2 leaf

No new kappa. In the nine-gate diagonal word of PR #7027, place constant
matrices `R` and `S` in the gap after stage-2 `E_22` and the gap after the
stage-2 leaf gate. Over `F_2`, the coefficient of `e` equals the pure
product `P` for exactly `2^40` pairs. The matched positions are the
off-diagonal pairs inside `{6, 7}` and inside `{0, 1, 2, 3, 4, 5}`. Every
such coefficient has diagonal entries in `{0, P_ii}`, and each `P_ii`
differs from `1`, so the coefficient is never `I`. The selected frontier
stays `363005817/100000000000`.

This is an identity in `F_2[x, y, z][e]/(e^2)`. It is not a listing of the
`2^40` pairs. The count does not agree with PR #7287, and the level sets
do not: `(1, 4)` is blocked there and free here, while `(1, 6)` is free
there and blocked here. It is not a kappa improvement.

## 1. Hypotheses

The ring is `F_2[x, y, z][e]/(e^2)` with `e` central. The space has eight
coordinates

```text
(0, 1, 2, 3, 4, 5, 6, 7)
 = (core_0, core_1, leaf0_0, leaf0_1, leaf1_0, leaf1_1, leaf2_0, leaf2_1).
```

The historical labels `E_11` and `E_22` are the stage gates on coordinates
`0` and `1`. A witness written `E_{i,j}` below uses these same coordinates:
a one in row `i`, column `j`.

Stage `s` uses the indeterminate `x_s`, written `x, y, z` for stages
`0, 1, 2`. Its three diagonal gates, in order, are

```text
I + x_s E_11,    I + x_s E_22,    I + x_s (leaf of stage s),
```

supported on coordinate `0`, coordinate `1`, and the two coordinates of
leaf `s`. The word is stage 0, then stage 1, then stage 2. All nine gates
are diagonal, so they commute. Their product `P` is diagonal, with entries

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

Number the gates `G0, ..., G8` in the order above. Stage-2 `E_22` is `G7`.
The stage-2 leaf gate is `G8`, supported on coordinates `6` and `7`. The
word under test is

```text
G0 G1 G2 G3 G4 G5 G6 G7 (I + e R) G8 (I + e S).
```

There is no gate after `G8`. The factor to the right of `S` is the empty
product, which is `I`. PR #7287 inserts after `G4` and `G6` instead. These
are different slots: the only gate strictly between the insertions here is
`G8`, the stage-2 leaf.

Because `e^2 = 0` and `e` is central, the coefficient of `e^0` is `P` for
every `R` and `S`. Write

```text
L = G0 G1 G2 G3 G4 G5 G6 G7,    M = G8,    T = I.
```

The coefficient of `e` is

```text
C = L R (M T) + (L M) S T = L R M + (L M) S.
```

There is no `R S` term. On coordinates, the diagonals are

```text
L = diag((1+x)(1+y)(1+z), (1+x)(1+y)(1+z), 1+x, 1+x, 1+y, 1+y, 1, 1),
M = diag(1, 1, 1, 1, 1, 1, 1+z, 1+z),
T = diag(1, 1, 1, 1, 1, 1, 1, 1).
```

Every entry of `L`, `M` and `T` is `1` or a product of terms `1` plus one
indeterminate, hence nonzero in the integral domain `F_2[x, y, z]`. The
entries `L_66 = L_77 = 1` are the empty products on coordinates `6` and
`7`: no earlier gate meets the stage-2 leaf. The product `L M T` is the
closed form of `P`.

## 3. The entry formula

Diagonal matrices act by scaling rows and columns. For `i, j` in `0..7`,

```text
C_ij = L_i (M_j T_j) R_ij + (L_i M_i) T_j S_ij
     = c_ij (M_j R_ij + M_i S_ij),
```

where `c_ij = L_i T_j = L_i` is nonzero. Therefore `C_ij` depends only on
the pair `(R_ij, S_ij)`. Matrix multiplication is bilinear, so a constant
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

The middle diagonal takes two values,

```text
M_6 = M_7 = 1+z,
M_0 = M_1 = M_2 = M_3 = M_4 = M_5 = 1.
```

Their sum is nonzero:

```text
1 + (1+z) = z.
```

For bits `r, s` in `{0, 1}` the linear combination `M_j r + M_i s` is
`0`, `M_j`, `M_i`, or `M_i + M_j`.

- If `M_i = M_j`, the combination is `M_i (r + s)`. It vanishes if and
  only if `r = s`. Both bits may be `0`, or both may be `1`.
- If `M_i ≠ M_j`, each of `M_i`, `M_j` and `M_i + M_j` is nonzero, so the
  only solution is `r = s = 0`.

The level sets of `M` are `{6, 7}` and `{0, 1, 2, 3, 4, 5}`. The
off-diagonal positions inside a level set are

```text
{6, 7}:                 (6, 7), (7, 6)                         2 positions,
{0, 1, 2, 3, 4, 5}:     6 · 5 ordered pairs                   30 positions.
```

That is `32` positions. The other `56 - 32 = 24` off-diagonal positions
are forced to `0` in both matrices. The free data are the eight diagonal
bits of `R`, with `S_ii = 1 + R_ii`, and one bit on each of the `32`
matched positions, copied into both matrices. The count is

```text
2^(8 + 32) = 2^40.
```

The same count is the product of the per-position solution counts:
`2` choices on each of `40` positions and `1` choice on each of the other
`24`. The product equals the number of matrix pairs because each entry
pair `(R_ij, S_ij)` appears in only one equation.

The solution set contains `(I, 0)` and `(0, I)`. It also contains pairs
with both matrices nonzero. Two examples, with `E_{i,j}` the coordinate
unit named above, are

```text
R = I + E_{6,7},    S = E_{6,7},
R = I + E_{0,1},    S = E_{0,1}.
```

Coordinates `6` and `7` lie in the level set of `1+z`. Coordinates `0`
and `1` lie in the level set of `1`. The pair
`R = I + E_{6,7} + E_{7,6}`, `S = E_{6,7} + E_{7,6}` is a third solution:
the two off-diagonal equations do not interact.

PR #7287 has count `2^30` and middle diagonal
`diag(1+z, 1, 1, 1, 1+y, 1+y, 1, 1)`. Its level sets are `{0}`, `{4, 5}`
and `{1, 2, 3, 6, 7}`. Position `(1, 6)` is inside that last level set and
outside every level set here, so a constant `1` at `(1, 6)` solves the
earlier equation and misses this one. Position `(1, 4)` is the opposite
case: both coordinates have middle value `1` here, while PR #7287 gives
them the distinct values `1` and `1+y`. The two solution sets are not
equal.

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
`G7` and `G8`. It checks that their matrix product is the closed form of
`P`, that `L`, `M` and `T` are the diagonals displayed in section 2, and
that `L M T = P`. It checks that the empty product after `S` is `I`. For
all `64` positions it checks

```text
a_ij = c_ij M_j,    b_ij = c_ij M_i,    c_ij ≠ 0,
```

and that `a_ij = b_ij` if and only if `M_i = M_j`. It multiplies all `64`
matrix units in each gap, including the empty suffix, and checks that the
resulting coefficient is that single scale. It then solves all four
constant bit pairs at all `64` positions and checks that the solution sets
are exactly the ones in section 4. The witnesses of section 4 are
multiplied directly, and the blocked position `(1, 6)`, an unequal matched
bit, and a mixed matched-plus-blocked pair are rejected.

The position `(1, 4)` is blocked in the PR #7287 pair and free here. The
position `(1, 6)` is free there and blocked here. The solution count
`32 + 8` is not that package's `22 + 8`.

## 7. Limits

The hypotheses are the two named slots, constant `F_2` entries, the nine
diagonal gates in this order, and the empty product after the leaf. A
polynomial entry such as `R_{0,6} = 1+z` and `S_{0,6} = 1` satisfies the
single blocked equation at `(0, 6)` and is outside this count. The gap
after stage-2 `E_11` and the gap after stage-2 `E_22` has its own middle
diagonal, the single gate `G7`. PR #7287 classifies the pair after
stage-1 `E_22` and stage-2 `E_11`. PR #7215 classifies the pair after
stage-0 `E_22` and stage-1 `E_11`. PR #7191 classifies polynomial entries
in the two stage-0 gaps of PR #7103. Neither classifies this pair. The
non-idempotent factor `N` of PR #7027 is a different stage-0 gate. This
identity is at `g = 3`, `d = 2`. It does not supply a word for `g = 13` or
`g = 31`, and it does not change the selected frontier.

Evidence class: a proof of the entry formula and of the constant solution
set, with the scalar equations solved exhaustively on a domain of four bit
pairs. It is not a heuristic search, and it is not an enumeration of the
`2^40` matrices.
