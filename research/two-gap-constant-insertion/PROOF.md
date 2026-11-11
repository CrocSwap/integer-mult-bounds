# Two constant insertions after the stage-0 paired-star gates

No new kappa. In the nine-gate diagonal word of PR #7027, place constant
matrices `R` and `S` in the two gaps immediately after stage-0 `I + x E_11`
and stage-0 `I + x E_22`. The coefficient of `e` equals the pure product `P`
for exactly `2^50` pairs `(R, S)` with entries in `F_2`. The same coefficient
is never `I`. The selected frontier stays 781451/250000000.

This is an identity in `F_2[x, y, z][e]/(e^2)`. The machine check multiplies
every matrix unit in both gaps. It does not enumerate the `2^50` solutions,
and it does not search other gap pairs.

## 1. The word and the two gaps

The ring is `F_2[x, y, z][e]/(e^2)` with `e` central. The ambient space has
eight coordinates: core indices `0, 1` and three leaves of dimension 2, on
indices `(2, 3)`, `(4, 5)` and `(6, 7)`. Stage `s` uses the indeterminate
`x_s`, written `x, y, z` for stages `0, 1, 2`. Its three diagonal gates are

```text
I + x_s E_11,  I + x_s E_22,  I + x_s (E_33 + E_44),
```

supported on the core plus leaf `s`. In coordinates that is the factor
`1 + x_s` on one or two indices and `1` elsewhere:

```text
stage 0: index 0; index 1; indices 2 and 3
stage 1: index 0; index 1; indices 4 and 5
stage 2: index 0; index 1; indices 6 and 7
```

The word is these nine gates in that order: stage 0, then stage 1, then
stage 2, and within a stage `E_11`, then `E_22`, then `E_33 + E_44`. All
nine gates are diagonal, so they commute, and the pure product `P` is
diagonal. Its entries are

```text
P_00 = P_11 = (1 + x)(1 + y)(1 + z),
P_22 = P_33 = 1 + x,
P_44 = P_55 = 1 + y,
P_66 = P_77 = 1 + z.
```

Each of these is nonzero and is not `1`.

The two insertions sit in adjacent gaps of this order. Write `G0` for the
first gate, `I + x E_11`, and `G1` for the second, `I + x E_22`. The word
under test is

```text
G0 (I + e R) G1 (I + e S) G2 ... G8,
```

with `R` and `S` matrices over `F_2`. Because `e^2 = 0` and `e` is central,
the coefficient of `e^0` is `P` for every `R` and `S`. The coefficient of
`e` is

```text
C = G0 R (G1 ... G8) + (G0 G1) S (G2 ... G8).
```

## 2. The entry formula

Let `L1` be the diagonal of `G0` and `Rgt1` the diagonal of `G1 ... G8`.
Let `L2` be the diagonal of `G0 G1` and `Rgt2` the diagonal of `G2 ... G8`.
Diagonal matrices multiply entrywise, so

```text
C_ij = L1_i R_ij Rgt1_j + L2_i S_ij Rgt2_j
     = a_ij R_ij + b_ij S_ij,
```

where `a_ij = L1_i Rgt1_j` and `b_ij = L2_i Rgt2_j`. Write `Later_j` for the
`j`-th diagonal entry of `G2 ... G8`. Then `G0` contributes `1 + x` only at
index `0`, and `G1` contributes `1 + x` only at index `1`, so

```text
a_ij = G0_i G1_j Later_j,
b_ij = G0_i G1_i Later_j.
```

Every factor `G0_i`, `G1_i` and `Later_j` is `1` or `1` plus one
indeterminate, hence nonzero in the integral domain `F_2[x, y, z]`.

On the diagonal, `G1_i` appears in both products, so `a_ii = b_ii = P_ii`.
Therefore

```text
C_ii = (R_ii + S_ii) P_ii.
```

## 3. When the coefficient equals the pure product

`P` is diagonal, so `C = P` asks for `C_ii = P_ii` and `C_ij = 0` whenever
`i ≠ j`.

On the diagonal, `(R_ii + S_ii) P_ii = P_ii`. Cancel the nonzero factor
`P_ii`. The diagonal condition is exactly

```text
R_ii + S_ii = 1  for every index i.
```

Off the diagonal, compare `a_ij` and `b_ij`.

If `i ≠ 1` and `j ≠ 1`, then `G1_i = G1_j = 1`, so `a_ij = b_ij`. That
common value is nonzero. The entry equation `a_ij R_ij + b_ij S_ij = 0`
becomes `R_ij + S_ij = 0`, so the two bits are equal. There are `42` such
positions: `64 - 8` off-diagonal pairs, minus the `7 + 7` pairs that meet
index `1`.

If `i = 1` and `j ≠ 1`, then `G0_1 = 1`, `G1_1 = 1 + x` and `G1_j = 1`, so

```text
a_1j = Later_j,  b_1j = (1 + x) Later_j.
```

Cancel `Later_j`. The equation is `R_1j + (1 + x) S_1j = 0` with both bits
in `{0, 1}`. The bit `S_1j = 1` forces `R_1j = 1 + x`, which is not a
constant. The only solution is `R_1j = S_1j = 0`.

If `j = 1` and `i ≠ 1`, then `G1_i = 1` and `G1_1 = 1 + x`, so

```text
a_i1 = (1 + x) G0_i Later_1,  b_i1 = G0_i Later_1.
```

Cancel `G0_i Later_1`. The equation is `(1 + x) R_i1 + S_i1 = 0`. The only
constant solution is `R_i1 = S_i1 = 0`.

These `14` positions are exactly the off-diagonal pairs with a row or a
column equal to `1`. Thus `C = P` if and only if

- `R_ii + S_ii = 1` for all eight indices,
- `R_ij = S_ij` for each of the `42` off-diagonal positions that miss index `1`,
- `R_ij = S_ij = 0` for each of the `14` off-diagonal positions that meet index `1`.

The free data are the eight diagonal bits of `R` and one bit for each of the
`42` matched positions. The count is `2^(8 + 42) = 2^50`.

The set contains degenerate pairs and pairs with both matrices nonzero.
`(R, S) = (I, 0)` and `(R, S) = (0, I)` both satisfy the conditions.
So does `R = I + E_02` and `S = E_02`: the diagonal sums to `1`, and the
only off-diagonal bit sits at `(0, 2)`, which misses index `1`, with equal
bits.

## 4. The coefficient is never the identity

For any constant pair, each diagonal entry `C_ii` is either `0` or `P_ii`.
Every `P_ii` differs from `1`, so `C` cannot equal `I`. This is the same
diagonal obstruction PR #7039 recorded for any finite number of constant
insertions. The two-gap calculation does not remove it.

## 5. What the checker establishes

`verify.py` rebuilds the nine diagonals, checks that their product is the
closed form above, and checks that `G1` is `1 + x` only at index `1`. It
computes both gap scales directly. It checks `a_ii = b_ii = P_ii`, checks
that the `42` matched off-diagonal scales are equal, and checks that each
blocked scale pair differs by the factor `1 + x` in the direction stated in
section 3. It multiplies all `64` matrix units in each of the two gaps and
checks that the resulting coefficient is the single scale predicted by the
entry formula. Matrix multiplication is bilinear, so every constant pair is
the sum of its units and has coefficient `a_ij R_ij + b_ij S_ij`.

The checker also evaluates the named witnesses `(I, 0)`, `(0, I)`, `(I, I)`
and `(I + E_02, E_02)`, and it rejects a blocked bit on both matrices. Those
are controls. The count `2^50` is the number of free bits in the solved
system, not a population that was listed.

## 6. Limits

The two gaps are these two adjacent slots in this gate order. Another pair
of the ten possible slots has a different scale ratio. Entries outside
`F_2`, including a polynomial value `1 + x` on a blocked position, are
outside the count. The non-idempotent factor `N` from PR #7027 is a
different stage-0 gate. This identity is at `g = 3`, `d = 2`. It does not
supply a word for `g = 13` or `g = 31`, and it does not change the selected
frontier.
