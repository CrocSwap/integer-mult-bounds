# One other off-diagonal block cancels the after-stage-0 leaf

This note answers open question 1 of PR #7097 for one named matrix. The
field has characteristic 2. No new kappa is claimed. The selected frontier
stays `363005817/100000000000` from `certificates/selected-result.json`.

The evidence class is a proof. The matrix identities are multiplications
of explicit 0-1 matrices. The leaf-block identity is the same closed form
at every invertible specialization. The GF(4) word in `verify.py` checks
that the implemented schedule matches the identity. It is not a search,
and it is not an exhaustive census of legal blocks.

## 1. The matrix

Let the block size be 16, with coordinates `0, ..., 15`. Write

```text
A  = diag(I_8, 0_8),    A' = I+A,
B  = E_{0,8} + E_{8,0},
C  = E_{0,0} + E_{8,0} + E_{8,8},
C' = E_{0,0} + E_{0,8} + E_{8,8}.
```

`E_{i,j}` is the matrix unit with a 1 in row `i` and column `j`. The named
pair from PR #7097 is `B_0 = E_{0,8} + E_{9,2}`. These two matrices differ
in positions `(8,0)` and `(9,2)`.

`A` is the coordinate projection onto `0, ..., 7`, so `A^2 = A` and
`A A' = A' A = 0`. The only nonzero columns of `B` are `B e_0 = e_8` and
`B e_8 = e_0`. Therefore

```text
(AB+BA) e_0 = A e_8 + B e_0 = e_8,
(AB+BA) e_8 = A e_0 = e_0,
```

and both sides vanish on every other basis vector. The same two columns
give `A'B+BA' = B`, because `A' e_8 = e_8` and `A' e_0 = 0`. Thus `B` is
a nonzero legal off-diagonal block for this fixed `A`: the paired-star
halves

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']]
```

satisfy `AB+BA = B` and `A'B+BA' = B`. `B` has rank 2. The nine columns

```text
(A+B) e_0 = e_0+e_8,  (A+B) e_j = e_j (1 ≤ j ≤ 7),  (A+B) e_8 = e_0
```

span `{e_0, ..., e_8}` and the remaining columns are zero, so `A+B` has
rank 9. The same count on `e_0, e_8, ..., e_15` gives `rank(A'+B) = 9`.
A solution of `(A+B)X = B` is therefore not unique. One solution is enough.

## 2. Theorem

Over every field of characteristic 2,

```text
(A+B) C = B,    (A'+B) C' = B.
```

`C'` does not solve the first equation, and `C` does not solve the second.
The zero matrix solves neither.

Proof. The nonzero columns are

```text
C e_0 = e_0+e_8,   C e_8 = e_8,
C' e_0 = e_0,      C' e_8 = e_0+e_8.
```

Hence

```text
(A+B) C e_0 = (e_0+e_8) + e_0 = e_8 = B e_0,
(A+B) C e_8 = e_0 = B e_8,
(A'+B) C' e_0 = e_8 = B e_0,
(A'+B) C' e_8 = e_8 + (e_0+e_8) = e_0 = B e_8.
```

Every other column on both sides is zero. The same expansions with the
two witnesses exchanged, or with the zero matrix, leave a column `e_0` or
`e_8` unmatched. Over `Z` the same product `(A+B)C` has a 2 in position
`(0,0)`, so the characteristic is part of the statement. The entries lie
in `{0,1}` and the only sum that cancels is `1+1`, so the identity over
`F_2` transfers to every field of characteristic 2 along the unique ring
map.

## 3. The named pair still fails

This section is the obstruction already proved for `B_0` in PR #7097. It
is recorded so the new witness is visibly a different matrix, not a change
to that proof.

The columns of `A+B_0` are `e_0, e_1, e_2+e_9, e_3, ..., e_7, e_0`, and
then zeros. The functional `φ(v) = v_2+v_9` vanishes on each of them.
Column 2 of `B_0` is `e_9` and `φ(e_9) = 1`, so no matrix `X` satisfies
`(A+B_0)X = B_0`. The columns of `A'+B_0` span the vectors whose
coordinates `0` and `8` agree and whose coordinates `1, ..., 7` are zero.
The functional `ψ(v) = v_0+v_8` vanishes on that space, while column 8 of
`B_0` is `e_0` and `ψ(e_0) = 1`. Both functionals use only these 0-1
columns, so neither equation has a solution over any field of
characteristic 2.

## 4. Half relations used for the leaf block

The relations `A^2 = A`, `AA' = 0`, and `AB+BA = B` give, on one
core-plus-leaf support,

```text
(A+B)^2 + B^2 = A+B,
(A+B)B + B(A+B) = B.
```

The first is `A + (AB+BA) + B^2 + B^2`. The second is `AB+BA`. Thus
`P^2 = P`, and the same calculation with `A'` gives `(P')^2 = P'`.
Also `P+P' = I` on that support, because `A+A' = I` and `B+B = 0`.
The cross term is

```text
(A+B)(A'+B) + B^2 = AB + BA' = AB + B + BA = B+B = 0,
```

and `(A+B)B + B(A'+B)` is the same expression. Thus `PP' = P'P = 0`.
For the queries, `(A'+B)A + BA = 0` and `A(A'+B) + AB = 0`, so
`P'R = RP' = 0`. Exchanging `A` and `A'` gives `PR' = R'P = 0`.

Let `x = D+1` with `D` invertible. Then

```text
(I+x P')(I+x P) = I + x I = D I
```

on the stage support, in either half order. The inverse of one half
`L = I+x Q` is `I+(x/D) Q`, because `Q^2 = Q` and

```text
x + x/D + x^2/D = x(D+1+x)/D = x(x+x)/D = 0.
```

Either half fixes the other half's query: `(I+x P') R = R`.

## 5. Corollary: the leaf-0 ← leaf-1 block

Use the after-stage-0 split of PR #7097. One half of stage 0 stands
first, the constant sum `K+M` stands between the halves, the other half
stands second, and `M` is added again after stage 0. Every later stage is
an adjacent pair with no further thin map. `K` is zero on diagonal blocks
and on leaf/leaf blocks, and it is `I` on each core/leaf pair. `M` is
zero except for a block `C_•` from leaf 1 into leaf 0 and a block `E`
from leaf 0 into leaf 1. The second half has diagonal factor
`A_Q ∈ {A, A'}`.

**Corollary.** For every invertible specialization,

```text
S_{leaf 0 ← leaf 1} = D_1^{-1} (D_0+1) (B + (A_Q+B) C_•).
```

In particular the block is zero when `A_Q = A` and `C_• = C`, and when
`A_Q = A'` and `C_• = C'`. The block `E` does not appear. This is one
matrix `B` and one block of `S`. It does not say that `S = I`.

Proof. Write `x = D_0+1` and let `L = I+x Q` be the second half, acting
on the core and on leaf 0. A vector `u` supported on leaf 1 is fixed by
`L^{-1}`. The first half's query is supported on the core and on leaf 0,
so it sends `u` to zero; conjugation by `L` keeps that zero. The same
holds for the second half's own query. Thus neither stage-0 query meets
this block.

`K u` is the same vector `u` placed on the core. Section 4 sends a core
vector `c` to the leaf-0 vector `x B c`, so this term contributes
`x B u`. The forward part of `M` contributes `C_• u` on leaf 0. Applying
`L` multiplies that leaf-0 vector by `I+x(A_Q+B)`. Adding the after-gap
copy of `M` contributes another `C_• u`. In characteristic 2 the two
copies of `C_• u` cancel, and the `M` contribution that remains is
`x(A_Q+B) C_• u`. The block `E` reads leaf 0 and writes leaf 1, so it
does not read `u`. Before the later stages the block is therefore

```text
x (B + (A_Q+B) C_•).
```

A completed later stage on leaf `t` replaces the state `S` by
`U S U^{-1} + T`. Here `U` is `D_t I` on the core and on leaf `t` and is
`I` on every other leaf, and `T = R+R'` is supported on the core and on
leaf `t`. The cross relations of section 4 give the query-fixing step, and
the product of the halves is `U` on that support. For `t = 1`, `U` scales
the input leaf by `D_1^{-1}` and fixes leaf 0, so the block is multiplied
by `D_1^{-1}`. For `t ≥ 2`, `U` fixes both leaf 0 and leaf 1, and `T` does
not meet the block, so the block is unchanged. `U` is scalar on each
summand of the core/leaf decomposition, so it does not move a core/leaf
block into a leaf/leaf position.

Substituting either exhibited solution makes the parenthesis zero. The
scalar `D_1^{-1}(D_0+1)` may be anything invertible or zero; the matrix
block is still zero.

## 6. What the checker establishes

`verify.py` raises unless all of the following hold.

- The products in sections 1 and 2, the separation from `B_0`, both
  swapped-witness failures, and the zero-matrix failure.
- Rank 2 for `B` and rank 9 for `A+B` and for `A'+B`.
- The integer product `(A+B)C` has a 2 in position `(0,0)`.
- The two functionals of section 3.
- Idempotence, `PP' = P'P = 0`, `P+P' = I` on the stage support, and both
  query cross relations, for this `B`.
- On the core and leaves 0, 1, and one spectator leaf, the after-stage-0
  word of section 5, at both values `D_j ∈ {t, t+1}` in
  `F_4 = F_2[t]/(t^2+t+1)`, in both choices of the second stage-0 half,
  and with the later pairs run together either as A then A' or as A' then
  A: the matching `C_•` makes the final
  leaf-0 ← leaf-1 block zero; the empty correction reproduces
  `D_1^{-1}(D_0+1) B`, which is nonzero; the witness for the other half
  leaves that block nonzero; a nonzero `E = E_{3,4}` does not change it.
  With `E = 0` and the matching `C_•`, the opposite block leaf 1 ← leaf 0
  is nonzero at those same points.

One spectator leaf is the pattern of every later stage in the proof. The
checker does not allocate all thirteen leaves. The closed form already
covers every invertible tuple, so the two field values are agreement
checks, not an interpolation.

## 7. What this does not prove

- It names one legal `B`. It does not classify the legal blocks
  `[[0, Q], [R, 0]]`.
- The cancelled block is leaf 0 ← leaf 1. At the tested points with
  `E = 0`, the opposite block is nonzero. No claim is made that every `E`
  fails, and `S = I` is not claimed.
- The solution `C` is one matrix. Section 1 records that `A+B` has rank 9,
  so it is not the only solution.
- Stage 0 remains first. The schedule is the after-stage-0 split, not the
  stage-0-not-first schedule of PR #7096.
- The rank-16 coordinate witness asked in question 2 of PR #7097 is
  untouched, as are the g = 31 profiles.
- Native transport, frames, and the selected frontier are untouched.

## 8. Credit

The paired-star contract and the chronological rank floor are from PR
#5747 (Ali Romman), with the predecessor statements in PR #5673, PR
#5631, and PR #5617. The local form used here is the one in
`research/coupled31-chronology/PROOF.md`. The internal gap is PR #7026.
The after-stage-0 formula and the named obstruction for
`B_0 = E_{0,8}+E_{9,2}` are PR #7097. This note supplies a different
legal block and the two matrices `C` and `C'`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human review and a proof-assistant proof are unclaimed.
