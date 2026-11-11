# The g=13 internal-gap block stays nonzero when stage 0 is not first

This is a proof for one family of schedules. It is not a census of opening
orders, and it is not a claim that every interleaved word fails.

No new kappa is claimed. The selected frontier stays
`781451/250000000 = 0.003125804`.

The assigned reading is the schedule that completes stage 1, opens stage 0
around the same five maps, and evaluates the block from leaf 2 into leaf 0
at a point with `D_1 ≠ 1`. That block equals the stage-0-first expression
`(D_0+1) D_2^{-1} B`. It is nonzero whenever `B ≠ 0` and `D_0 ≠ 1`. The
nontrivial value of `D_1` does not appear in the normalized coefficient.

## 1. Contract

Use the paired-star contract in `research/coupled31-chronology/PROOF.md` at
base `17469fff78c22941280f04d39dc5a1faee09c840`. The field has characteristic
2. The core and each of the `g` leaves have dimension `d = 2q`. Stage `j`
has two orthogonal projectors. On its core and leaf they have the legal
shape

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']],
```

with `A' = I+A`, `A^2 = A`, and `AB+BA = B`. The same relation holds for
`A'`, because `A'B+BA' = AB+BA`. A full call is `(I+x P)(I+e R)` with
`x = D+1` and `e^2 = 0`. Thin calls are `I+e Z` with `Z` constant. The
variables `D_j` are independent and invertible. The target is `(I+e I)`
times the product of `(I+x_j E_j)`, where `E_j` is the identity on the
core and on leaf `j`.

The normalized coefficient `S` is the left factor in `(I+e S)` times the
pure product. A full call replaces `S` by `(I+x Q) S (I+x Q)^{-1} + R_Q`.
This agrees with the literal call because each query commutes with its own
half and is annihilated by the other half, so conjugating `R_Q` does not
change it. A thin call adds `Z`. The endpoint requires `S = I`. The
inverse factor is `y = x/D = 1+D^{-1}`, since `x+y+xy = 0`.

Block `S_{a,b}` maps leaf or core `b` into `a`.

## 2. The schedules

Number the leaves `0` through `g-1`. Fix a set `P` of stages, with
`0 ∉ P` and `P` a proper subset of `{1,...,g-1}`. The word does all of
the following, and nothing else.

- For each stage in `P`, in any order, apply both halves as an adjacent
  pair. Either half of that pair may come first. No thin map stands
  between those halves.
- Apply one half of stage 0, then every constant thin map, then the other
  half of stage 0. Either half of stage 0 may come first.
- For each remaining stage, in any order, apply both halves as an adjacent
  pair, with either half order.

Call `P` the prefix and the complement the tail. The assigned schedule is
`P = {1}`. The empty prefix is the first-stage internal gap of open PR
#7026. This note records that case as the predecessor and claims the
nonempty prefixes.

A stage `t` in the tail is a tail leaf. Its block into leaf 0 is the block
read below. For `P = {1}` the assigned tail leaf is leaf 2.

## 3. An adjacent pair is a scalar conjugation plus `T`

On one stage's core and leaf, `A'A = AA' = 0` and

```text
A'B+BA = (I+A)B+BA = B+(AB+BA) = 0.
```

The off-diagonal blocks of `P'P` are `A'B+BA` and `BA+A'B`, and the
diagonal blocks reduce to the same expression. Thus `P'P = PP' = 0` and
`P+P' = E`, the identity on that core and leaf. Therefore

```text
(I+x P')(I+x P) = (I+x P)(I+x P') = I+x E
```

on that support and the identity elsewhere. In characteristic 2,
`I+x E = D I` on the support. Call this scalar operator `U`: it multiplies
the core and that leaf by `D` and fixes every other leaf. The same
cancellation gives `P'R = RP' = 0` and `PR' = R'P = 0`, so each half
conjugates the other half's query to itself. Starting from `S`, either
order of the two halves replaces `S` by

```text
U S U^{-1} + T,    T = R+R' = [[I, I], [I, I]]
```

on that core and leaf. Leaf-to-leaf blocks of `T` are zero. `T` does not
depend on `D` or on the half order.

## 4. Setting every `D_j = 1` forces one sum

At `D_j = 1` every `x_j` is 0, so every conjugation is the identity,
whatever the order is. Each stage contributes `T_j`, and

```text
S = sum_j T_j + sum Z.
```

The sum of the queries has `I` on the core diagonal `g` times, `I` on each
leaf diagonal, and `I` on each core/leaf off-diagonal pair. For odd `g` the
core diagonal is `I`. The endpoint `S = I` therefore forces the thin sum
`Z` to be the matrix `K` which is `I` on every core/leaf off-diagonal pair
and zero on every diagonal and every leaf/leaf block. Every block is
fixed. There is no other constant solution of the `D_j = 1` equation.

## 5. A tail leaf misses the prefix

Let `t` be a tail leaf, and let the thin sum be `K`. The argument does not
use which nonempty proper set `P` avoids `t`, or the order inside `P`.

`T_s` and `U_s` for `s ≠ t` do not write into row `t` or column `t`: `T_s`
is supported on the core and leaf `s`, and `U_s` multiplies those two
blocks without mixing leaves. By induction from `S = 0`, row `t` and
column `t` stay zero through every prefix stage.

The first half of stage 0 is supported on the core and leaf 0, and its
query has the same support. Conjugation by that half preserves the zero
row and the zero column. Adding `K` then sets

```text
S_{core, leaf t} = I,    S_{leaf t, core} = I,
```

and leaves every leaf-to-leaf block in that row and column equal to zero.

The second half has off-diagonal block `B` whether it is `P` or `P'`. On
a vector supported on leaf `t`, its inverse acts as the identity, `K` sends
the vector to the core, and the half sends a core vector `c` to `(x B) c`
on leaf 0. Thus, immediately after stage 0,

```text
S_{leaf 0, leaf t} = (D_0+1) B.
```

In the other direction, the inverse sends a vector on leaf 0 to `(y B)`
times that vector on the core, plus a leaf-0 component. Only the core
component meets row `t`, through `S_{leaf t, core} = I`, and the half fixes
leaf `t`. Thus

```text
S_{leaf t, leaf 0} = y B = (D_0+1) D_0^{-1} B.
```

The second query does not meet leaf `t`.

Each tail stage `k ≠ t` conjugates by a scalar operator that fixes leaf 0
and leaf `t`, then adds a query with no leaf-to-leaf block. Stage `t`
multiplies column `t` by `D_t^{-1}` and row `t` by `D_t`. No later scalar
operator mixes the core into leaf 0, so the query of stage `t` cannot fill
these blocks. The final blocks are

```text
S_{leaf 0, leaf t} = (D_0+1) D_t^{-1} B,
S_{leaf t, leaf 0} = D_t (D_0+1) D_0^{-1} B.
```

In particular this holds for `P = {1}` and `t = 2`, which is the assigned
reading. The same two expressions are the stage-0-first blocks. The prefix
does not change them.

## 6. The single prefix leaf is unscaled, and `D_1` drops out

Now take `P = {1}` only. Stage 1 is applied to `S = 0`, so both halves add
their queries and the conjugation does nothing. The state is `T_1` for
every invertible `D_1` and either half order. No later call reads `D_1`.
The final normalized coefficient is therefore independent of `D_1`. The
pure product still depends on `D_1`.

It remains to see the leaf-1 blocks. Let the first half of stage 0 have
diagonal projector `A` and off-diagonal block `B`, and write `x = D_0+1`.
Its inverse fixes leaf 1. On a vector supported there, `T_1` produces that
vector on the core and on leaf 1. The first half sends the core vector to
`(I+x(A+B))` on the core and to `(x B)` on leaf 0, and it fixes leaf 1.
Adding `K` replaces the core block `I+x(A+B)` by `x(A+B)`, because `K`
contributes `I` there and the characteristic is 2. The leaf-0 block stays
`x B`.

The second half has diagonal projector `A' = I+A`. It fixes leaf 1, so the
block into leaf 0 is

```text
x^2 B(A+B) + x B + x^2 (A'+B) B.
```

The coefficient of `x^2` is `BA + A'B = BA + B + AB = B + (AB+BA) = 0`.
The block is `x B`. If the halves of stage 0 are exchanged, the same
calculation with `A` and `A'` swapped has coefficient
`BA' + AB = B + BA + AB = 0`.

For the opposite block, the second inverse sends a leaf-0 vector to
`(y B)` on the core. The first-half calculation leaves
`S_{leaf 1, core} = y(A+B)` and `S_{leaf 1, leaf 0} = y B` after `K` is
added. The leaf-1 output is

```text
y^2 (A+B)B + y B + y^2 B(A'+B),
```

and `(A+B)B + B(A'+B) = AB + BA' = 0` by the same relation. The block is
`y B`. Exchanging the halves again gives `A'B + BA = 0`.

No tail stage multiplies leaf 0 or leaf 1. The final blocks are

```text
S_{leaf 0, leaf 1} = (D_0+1) B,
S_{leaf 1, leaf 0} = (D_0+1) D_0^{-1} B.
```

The stage-0-first formula would still divide the first of these by `D_1`.
That factor is absent here. At every point with `D_1 ≠ 1` the two matrices
differ, and both are nonzero when `B ≠ 0` and `D_0 ≠ 1`.

This leaf-1 calculation uses that the state entering stage 0 is exactly
`T_1`. It is not claimed for a prefix of two or more stages.

## 7. Theorem

Let `g` be odd and at least 3, and let `B` be nonzero. Let `P` be a
nonempty proper subset of `{1,...,g-1}`. In every schedule of section 2
with that prefix, no constant thin maps meet the endpoint. Every half
order and every order of the prefix and of the tail are included.

Indeed section 4 forces the thin sum to be `K`, the complement of a proper
subset contains a tail leaf `t`, and section 5 then gives a leaf-to-leaf
block equal to a nonzero scalar times `B` at every specialization with
`D_0 ≠ 1`. The normalized coefficient is not `I`.

In particular this holds for `P = {1}` at `g = 13` and `q = 8`, with tail
leaf 2. Five rank-8 maps can sum to `K`, so the obstruction is not that
the `D_j = 1` equation is impossible at rank `q`. Index the `d = 16`
coordinates by `0, ..., 15`. The five bundles

```text
(0,1,2,3), (0,1,4,5), (0,1,6,7), (8,9,10,11), (12,13,14,15)
```

each contain four coordinates. Coordinates 0 and 1 lie in three bundles
and every other coordinate lies in one, so the sum of the five bundle maps
is `K`. Each bundle has rank 8. Their total rank is 40.

The chronological floor in `research/coupled31-chronology/PROOF.md` is
`4q + 2 ceil((g-2)/3)`. At these parameters it equals 40. These five maps
meet that number and still fail. This note does not re-prove the floor.
The adjacent-halves count is a different schedule: it does not apply once
a thin map stands between the halves, and it is not used here.

The pure product is still the target. Thin maps contribute the identity,
and each completed stage contributes `I+x_j E_j`. On the core,

```text
x_a + x_b + x_a x_b = D_a D_b + 1,
```

so `I+(x_a+x_b+x_a x_b)I = D_a D_b I`. The core factor is the product of
the `D_j`, leaf `j` is multiplied by `D_j`, and the factors commute. The
failure is only the coefficient of `e`.

At the assigned point `D = (2,3,4,...,14)`, one has `D_1 = 3 ≠ 1` and
`D_0 = 2 ≠ 1`. Over `GF(16)` with polynomial `x^4+x+1`, the tail scalar
`(D_0+1) D_2^{-1}` equals 4, so the block from leaf 2 into leaf 0 equals
`4B`. Replacing `D_1` by 1 leaves `S` unchanged. The block does not vanish.

The same five maps with stage 0 first have the same leaf-2 block and a
different leaf-1 block, namely `(D_0+1) D_1^{-1} B`. Moving stage 1 in
front of the gap does not remove the miss. It changes the leaf-1 block to
`(D_0+1) B`, which is still nonzero.

## 8. What the checker establishes

`verify.py` evaluates the normalized coefficient over `GF(16)`. It raises
unless all of the following hold.

- The exhibited `(A, B)` is legal and the two stage projectors do not
  commute. The same frame with `B = 0` is legal. `B` is nonzero in the
  first frame and zero in the second.
- The five bundles have rank 8, odd coordinate coverage, and sum to `K`.
  The sum of the ranks is 40, and `K` has rank 32.
- On a `g = 3`, `q = 1` word with prefix `{1}` and thin sum `K`, the fast
  updater agrees with the dual-number coefficient. The leaf-2 block matches
  section 5.
- At `g = 13`, `q = 8`, for prefix `{1}` and both orders of stage 0, the
  five maps give `S = I` when every `D_j = 1`. At

```text
(2,3,4,5,6,7,8,9,10,11,12,13,14)
(6,10,3,5,7,9,11,13,14,2,4,8,12)
```

the pure product is the target, `S` is not `I`, both leaf-2 blocks equal
section 5, and both leaf-1 blocks equal section 6. Those scalars are
nonzero because `D_0 ≠ 1`. Both points have `D_1 ≠ 1`. Replacing `D_1` by
1 preserves `S` and changes the pure product. Exchanging the halves of
stage 1 preserves `S`.

- The same five maps with the empty prefix, which is the stage-0-first
  word, produce the same leaf-2 block and a different leaf-1 block at the
  first point. That comparison separates the two schedules. It is not a
  second proof of the empty-prefix theorem.
- Prefix `{1,3}` and prefix `{3,1}`, at the first point and one half
  order, keep the pure product, miss the endpoint, and produce the
  section 5 block on leaf 2. This is one corroboration of a two-stage
  prefix. It is not a census of subsets.
- With `B = 0` and prefix `{1}`, the leaf-2 block is zero. The factor `B`
  is necessary for this obstruction. The commuting-projector count already
  excludes five maps for every order when the projectors commute. That
  count is not re-proved here.

The field points check the updater against the block identities. The
identities themselves are sections 3 through 7. One nonzero specialization
shows that a matrix polynomial is not identically zero; the argument here
is the equality, valid at every invertible specialization.

## 9. What this does not prove

- A prefix that contains every stage `1` through `g-1` leaves no tail
  leaf. Section 5 does not apply, and section 6 does not extend to several
  prefix leaves. That schedule is open.
- For two or more prefix stages, the block from an earlier prefix leaf
  into leaf 0 is not identified. Section 6 uses a single prefix.
- A thin map in any gap other than the interior of stage 0, including one
  map after stage 0, is outside the word. So is a full call between the
  halves of stage 0.
- Nested or crossed stage intervals are outside the word.
- The same shape at `g = 31`, `q = 26` is a different profile.
- The empty prefix is the schedule of open PR #7026. Agreement of the
  leaf-2 block with that schedule is a comparison, not a new proof of it.
- No exhaustive or sampled search of prefixes, projectors, or field
  elements was run. A single nonzero reading is not a theorem for every
  opening order; the orders in section 2 are the ones the identities
  cover. Absence of a search is not nonexistence of every interleaved word.
- The `g = 3` finite censuses do not lift, and they are not inputs.
- Native transport, frames, and the selected frontier are untouched.

When `B = 0` the tail block is zero, so this certificate does not fire.
That hypothesis is the commuting case.

## 10. Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), with the predecessor statements
in PR #5673, PR #5631, and PR #5617. The adjacent-halves count that leaves
an internal gap open is the open PR #7010 argument. The stage-0-first
internal gap at `g = 13`, `q = 8`, including the five bundles and the
leaf-to-leaf formula for an empty prefix, is the open PR #7026 argument.
This note answers the second open question of that PR: the same leaf-2
block when stage 0 is not first.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
