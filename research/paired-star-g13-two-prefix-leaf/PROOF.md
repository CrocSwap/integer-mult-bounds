# The earlier prefix leaf still meets leaf 0 in `(D_0+1) B`

This is a proof for one family of schedules. It is the expansion asked by open
question 1 of open PR #7096. It is not a census of opening orders, and it is
not a claim that every interleaved word fails.

No new kappa is claimed. The selected frontier stays
`363005817/100000000000 = 0.00363005817`. This note does not edit that record.
`docs/research/current-priorities.md` at this base still prints the older
decimal 0.00310045; the live value is `certificates/selected-result.json`.

## 1. Answer

Take the paired-star schedule of PR #7096, section 2, with the prefix order
stage 1 then stage 3. Expand the leaf-1 column through both halves of stage
3, then through the first half of stage 0.

After stage 3 the core block of that column is `D_3 I`, the leaf-1 block is
`I`, and every other block of the column, including leaf 3, is zero. After
the first half of stage 0 the block from leaf 1 into leaf 0 is

```text
(D_0+1) D_3 B.
```

That polynomial is not `(D_0+1) B`. Substituting `D_3 = 1` makes the two
polynomials agree, so a field point with `D_3 = 1` cannot see the factor
this expansion isolates.

Put the constant thin sum `K` between the halves and apply the second half.
The factor `D_3` cancels, and the block is `(D_0+1) B`. Every later adjacent
stage fixes leaf 0 and leaf 1, so the block at the end of the word is still
`(D_0+1) B`. The same holds with the two stage-0 halves exchanged, and with
either half order inside stage 1 and inside stage 3.

The same letters with any distinct stages `s` then `r` in `{1,...,g-1}`
replace `D_3` by `D_r`. The final block from the earlier prefix leaf into
leaf 0 is still `(D_0+1) B`. The block from the later prefix leaf into leaf
0 is `(D_0+1) B` as well. When `B ≠ 0` and `D_0 ≠ 1` both are nonzero, so
the normalized coefficient is not `I`.

## 2. Contract and schedule

The field has characteristic 2. The core and each of the `g` leaves have
the same dimension. Stage `j` has the legal shape of
`research/coupled31-chronology/PROOF.md` on its core and leaf:

```text
P  = [[A+B, B], [B, A+B]],    R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],  R' = [[A', A'], [A', A']],
```

with `A' = I+A`, `A^2 = A`, and `AB+BA = B`. Then
`A'B+BA' = AB+BA`, so `A'` satisfies the same off-diagonal relation. A full
call on stage `j` is `(I+x_j Q)(I+e R_Q)` with `x_j = D_j+1`, `e^2 = 0`,
and `Q` equal to `P` or `P'`. The scalars `D_j` are independent and
invertible, and they commute with the matrices. Thin calls are `I+e Z` with
`Z` constant. The normalized coefficient `S` starts at 0. A full call
replaces it by

```text
(I+x Q) S (I+y Q) + R_Q,    y = 1+D^{-1} = x D^{-1},
```

and a thin call adds `Z`. The scalar identity `x+y+xy = 0` gives
`(I+x Q)(I+y Q) = I` once `Q^2 = Q`. The endpoint requires `S = I`.

`K` is the matrix with `I` on every core/leaf off-diagonal pair and zero on
every diagonal block and every leaf/leaf block. Block `S_{a,b}` maps `b`
into `a`.

The schedule completes two distinct stages `s` and `r`, in that order, each
as an adjacent pair of halves. Either half of a pair may come first, and no
thin map stands between those halves. It then applies one half of stage 0,
then a constant thin sum, then the other half of stage 0, then every
remaining stage as an adjacent pair. The assigned reading is `g = 13`,
`s = 1`, `r = 3`. The argument is written for those indices and then
renamed.

## 3. An adjacent pair is conjugation by `U` plus `T`

On one stage, `A'A = AA' = 0`. The block products below use
`A'B+BA = B+(AB+BA) = 0`.

```text
(A'+B)(A+B)+B^2 = A'A+A'B+BA = 0,
(A'+B)B+B(A+B) = A'B+BA = 0.
```

Thus `P'P = PP' = 0` and `P+P' = E`, the identity on that core and leaf.
The same calculation with `A` and `A'` exchanged gives the symmetric
products. In particular `P^2 = P` and `(P')^2 = P'`. Also

```text
(A'+B)A+BA = A'A = 0,    A(A'+B)+AB = AA' = 0,
```

so `P'R = RP' = 0`. Exchanging `A` and `A'` gives `PR' = R'P = 0`.
Therefore

```text
(I+x P')(I+x P) = I+x E.
```

On the support, `I+x I = D I` in characteristic 2. Off the support the
product is `I`. Call this operator `U`: it multiplies the core and that
leaf by `D` and fixes every other leaf. The two factors commute, so either
half order gives the same `U`. The inverse scalar is `y`, and
`I+y E` multiplies the support by `D^{-1}`.

Because `P'R = RP' = 0`,

```text
(I+x P') R (I+y P') = R.
```

Starting from `S`, the order `P` then `P'` therefore replaces `S` by
`U S U^{-1}+R+R'`. The other order gives the same `U` and the same sum of
queries. The leaf-to-leaf blocks of

```text
T = R+R' = [[I, I], [I, I]]
```

are zero. `T` does not depend on `D` or on the half order.

Applied to `S = 0`, the update is `T`. Stage 1, in either half order and
for every invertible `D_1`, therefore leaves exactly `T_1`.

## 4. The leaf-1 column through `U_3`

Start from `T_1`. For an input `w` on leaf 1, the image is `w` on the core
and `w` on leaf 1. Let the first half of stage 3 have diagonal projector
`G ∈ {A, A'}` and write `x_3 = D_3+1`, `G' = I+G`. Both choices of `G`
satisfy `GB+BG = B`. The inverse of this half fixes leaf 1, and its query
is supported on the core and leaf 3, so the query does not meet column
leaf 1. The image becomes

```text
core:   (I+x_3(G+B)) w,
leaf 3: x_3 B w,
leaf 1: w.
```

The second half uses the same `x_3` and the diagonal projector `G'`. It
also fixes leaf 1, and its query misses column leaf 1. The new core image is

```text
(I+x_3(G+B)) w + x_3(G'+B)(I+x_3(G+B)) w + x_3^2 B^2 w
= (I + x_3 I + x_3^2 ((G'+B)(G+B)+B^2)) w.
```

The coefficient of `x_3` is `(G+B)+(G'+B) = I`. The coefficient of `x_3^2`
is `G'G+G'B+BG`. Here `G'G = (I+G)G = 0` and
`G'B+BG = B+(GB+BG) = 0`. Since `1+x_3 = D_3`, the core block is `D_3 I`.
The new leaf-3 image is

```text
x_3 B w + x_3 B(I+x_3(G+B)) w + x_3^2 (G'+B) B w
= x_3^2 (BG+G'B) w = 0,
```

because `BG+G'B = B+(GB+BG) = 0`. Leaf 1 remains `I`. Every other leaf was
zero and stays zero.

So, through both halves of stage 3, the leaf-1 column is `D_3 I` on the
core, `I` on leaf 1, and zero elsewhere. This is the column of
`U_3 T_1 U_3^{-1}`: `U_3` multiplies the core row by `D_3` and does not
scale leaf 1, and `T_3` does not write column leaf 1. The explicit halves
are the expansion; the conjugation formula is the same result.

## 5. The first half of stage 0

Let the first half of stage 0 have diagonal projector `H ∈ {A, A'}` and
write `x = D_0+1`, `H' = I+H`. Its inverse fixes leaf 1. On the leaf-1
vector `w`, the column of section 4 contributes `D_3 w` on the core and
nothing on leaf 0. The half sends a core vector `c` to `(I+x(H+B)) c` on
the core and to `(x B) c` on leaf 0. Therefore, immediately after the first
half and before the thin sum,

```text
S_{leaf 0, leaf 1} = x D_3 B = (D_0+1) D_3 B,
S_{core, leaf 1}   = (I+x(H+B)) D_3,
S_{leaf 1, leaf 1} = I.
```

The query of this half is supported on the core and leaf 0, so it does not
change column leaf 1. The polynomial `(D_0+1) D_3 B` equals `(D_0+1) B`
for every invertible `D_3` only if `B = 0`. One specialization, including
any point with `D_3 = 1`, does not decide that equality.

## 6. The thin sum and the second half

Adding `K` leaves the leaf-0 block unchanged, because `K` has no
leaf-to-leaf entry, and replaces the core block by

```text
(I+x(H+B)) D_3 + I = (D_3+1) I + x D_3 (H+B).
```

The second half fixes leaf 1. Its inverse therefore does not mix another
column into this one. On the current image
`c = ((D_3+1) I + x D_3 (H+B)) w` and `ℓ = x D_3 B w`, the leaf-0 output is

```text
ℓ + x B c + x (H'+B) ℓ
= x D_3 B w + x(D_3+1) B w + x^2 D_3 (B(H+B)+(H'+B)B) w.
```

The coefficient of `x` is `D_3 B+(D_3+1) B = B`. The coefficient of `x^2`
is

```text
B(H+B)+(H'+B)B = BH+H'B = BH+B+HB = B+(HB+BH) = 0,
```

where `HB+BH = B` because `H` is `A` or `A'`. The leaf-0 block is `x B`.
Exchanging the halves exchanges `H` and `H'` and uses the same relation.
The second query does not meet column leaf 1.

If the thin sum is omitted, the same expansion has core image
`(I+x(H+B)) D_3 w` instead. The two copies of `x D_3 B` cancel and the
`x^2` coefficient is again zero, so the leaf-0 block is the zero matrix.
The sum `K` is what produces `(D_0+1) B`. The relation is also necessary
for this cancellation: it is the step `HB+BH = B`.

## 7. The end of the word

Each remaining stage `k ∉ {0,1,3}` replaces `S` by `U_k S U_k^{-1}+T_k`.
The scalar `U_k` fixes leaf 0 and leaf 1, and `T_k` has no leaf-to-leaf
block, so

```text
S_{leaf 0, leaf 1} = (D_0+1) B
```

at the end of the word. Stages 1 and 3 have already been used. The value
does not depend on `D_1` or `D_3`. The stage-0-first formula of PR #7026
would still multiply this block by `D_1^{-1}`. That factor is absent, for
the same reason it is absent in the single-prefix calculation of PR #7096,
section 6: stage 1 ran before the gap, on the zero state.

The later prefix leaf is the `Δ = 1` case of the same stage-0 arithmetic.
Before stage 3, column leaf 3 is zero: stage 1 writes only the core and
leaf 1, and conjugation by `U_1` preserves a zero column. Stage 3 therefore
contributes exactly `T_3` on that column, namely `I` on the core and `I` on
leaf 3. Nothing stands between stage 3 and stage 0. Section 6 with `D_3`
replaced by `1` gives

```text
S_{leaf 0, leaf 3} = (D_0+1) B
```

after the second half, and the tail preserves it. After the first half this
later-leaf block is already `(D_0+1) B`, not `(D_0+1) D_3 B`. The extra
factor belongs only to a leaf whose stage was followed by another prefix
stage.

## 8. Any ordered pair

Replace stage 1 by an arbitrary stage `s` and stage 3 by a different stage
`r`. The opening state is still zero, so stage `s` contributes `T_s`.
Stage `r` then multiplies the core block of column `s` by `D_r` and does
not scale leaf `s`. Sections 4 through 7 never use the numerical values 1
and 3 except as names for that earlier stage and that later stage. The
final blocks are

```text
S_{leaf 0, leaf s} = (D_0+1) B,
S_{leaf 0, leaf r} = (D_0+1) B.
```

Immediately after the first half of stage 0, the earlier one is
`(D_0+1) D_r B` and the later one is `(D_0+1) B`. Either half order may be
used in stage `s`, stage `r`, and stage 0.

This is the two-stage statement. It does not by itself treat a prefix of
three or more stages. A third stage completed after `r` would have to be
checked before `D_r` could be replaced by a product of several later
scalars. That longer column is open question 2 of PR #7096 and is not
proved here.

## 9. The opposite block, and the block between the prefix leaves

The same schedule determines the opposite direction. After section 4,
`U_3` has multiplied row leaf 1 of column core by `D_3^{-1}`, and `T_3`
does not write that row, so `S_{leaf 1, core} = D_3^{-1} I`. Column leaf 0
is still zero. The first half of stage 0 sends a leaf-0 vector `w` to
`y B w` on the core and to `(I+y(H+B)) w` on leaf 0. Row leaf 1 is fixed,
so

```text
S_{leaf 1, leaf 0} = y D_3^{-1} B
```

after the first half. Adding `K` does not change a leaf-to-leaf block, and
it adds `I` to `S_{leaf 1, core}`. The second inverse sends `w` to `y B w`
on the core and to `(I+y(H'+B)) w` on leaf 0. The leaf-1 output is

```text
(D_3^{-1}(I+y(H+B))+I)(y B) w + (y D_3^{-1} B)(I+y(H'+B)) w
= y B w + y^2 D_3^{-1} ((H+B)B+B(H'+B)) w.
```

The second coefficient is `HB+BH' = B+(HB+BH) = 0`. Thus

```text
S_{leaf 1, leaf 0} = y B = (D_0+1) D_0^{-1} B,
```

and the tail preserves it. The later leaf has entering row `I` rather than
`D_3^{-1} I`, which is the single-prefix opposite block, and the same
cancellation leaves `y B`.

The leaf-3 entry of the leaf-1 column is zero after section 4. Stage 0
fixes both leaf 1 and leaf 3, and every later stage is some `k` other than
1 and 3, so that entry stays zero. In the other direction, column leaf 3 is
zero before stage 3 and `T_3` does not write row leaf 1, so
`S_{leaf 1, leaf 3}` is zero after the prefix and stays zero for the same
reason. The two prefix leaves do not meet each other.

## 10. Constant thin maps still miss at `g = 13`

At every `D_j = 1`, every `x_j` is zero, so every conjugation is the
identity regardless of order. Then `S` is the sum of every `T_j` and the
thin sum. For odd `g` the core diagonal of the query sum is `I`, each leaf
diagonal is `I`, and each core/leaf pair is `I`. The endpoint `S = I`
forces the thin sum to be exactly `K`. There is no other constant solution.

Sections 6 and 7 then give a leaf-to-leaf block `(D_0+1) B`. If `B ≠ 0`
and `D_0 ≠ 1`, that block is nonzero, so `S ≠ I`. No constant thin sum
meets the endpoint on any two-stage prefix of this shape, in any half
order and any order of the two prefix stages or of the tail.

In particular this holds for `g = 13` and the prefix order stage 1 then
stage 3. The five bundles of PR #7026 and PR #7096,

```text
(0,1,2,3), (0,1,4,5), (0,1,6,7), (8,9,10,11), (12,13,14,15),
```

sum to `K` on `d = 16` coordinates: coordinates 0 and 1 lie in three
bundles and every other coordinate lies in one. Each bundle has rank 8.
Their total rank is 40, and `K` has rank 32. The chronological floor cited
by those notes is 40 at `q = 8`, so these maps meet that number and still
fail. This note does not re-prove the floor. The exhibited frame
`A = diag(I_8, 0)` and `B = E_{0,8}+E_{9,2}` is legal, does not commute,
and has `B ≠ 0`, so the block is nonzero whenever `D_0 ≠ 1`.

The pure product is not re-proved. The obstruction recorded here is the
coefficient of `e`.

## 11. What the checker establishes

`verify.py` uses Laurent polynomials over GF(2), not a field point. It
raises unless all of the following hold.

- Both stage projectors are idempotent and `(I+x P)(I+y P) = I` for the
  `q = 2` generic frame.
- For four legal frames, including the exhibited `q = 8` frame, a `q = 8`
  frame with `B^2 = I`, and a `q = 2` frame with `B^2 ≠ 0`, the leaf-1
  column through both halves of stage 3 is `D_3 I` on the core and zero on
  leaf 3. After the first half of stage 0 the leaf-0 block is
  `(D_0+1) D_3 B`. After `K` and the second half it is `(D_0+1) B`. Both
  half orders are included. Substituting `D_3 = 1` collapses the
  intermediate polynomial to the final one. Omitting `K` leaves the zero
  block. The opposite block is `y D_3^{-1} B` after the first half and
  `y B` after the second.
- The frames include both `B^2 = 0` and `B^2 ≠ 0`. The matrix `B = I` does
  not satisfy the relation, and the same closure does not produce
  `(D_0+1) B`. The zero off-diagonal block produces the zero leaf block.
- At `g = 5` and `q = 2`, for two legal frames, every ordered pair of
  distinct stages in `{1,2,3,4}`, and all eight combinations of the three
  half orders, the literal conjugated word matches section 8. That is 192
  words. The tail leaf that remains keeps the PR #7096 factor
  `(D_0+1) D_t^{-1}`, and the block between the two prefix leaves is zero.
  This is an exhaustive finite check of those words at that size. It is
  not a census of projectors, and it does not lift to `g = 13` by itself.
  The lift is sections 3 through 9.
- The five `g = 13` bundles have rank 8, sum to `K`, and have total rank
  40. The exhibited frame is legal, noncommuting, and has nonzero `B`.

The polynomial identities are sections 3 through 9. The 192 words check
that the literal schedule agrees with those identities. They are not an
interpolation.

## 12. What this does not prove

- A prefix of every stage `1` through `12` is not evaluated. Section 8
  stops at one later stage. Blocks between a prefix leaf and a nonzero
  leaf other than its partner are not identified, except the tail-into-leaf-0
  control reproduced at `g = 5`.
- A thin map outside the interior of stage 0, including a map after stage
  0, is outside the word. So is a full call between the halves of stage 0,
  and so is a split of stage `r` that leaves only one half before the gap.
- Nested or crossed stage intervals are outside the word.
- The same shape at `g = 31`, `q = 26` is a different profile.
- The tail-leaf formula is the theorem of open PR #7096. Agreement at
  `g = 5` is a control, not a new proof of that theorem.
- No search was run over projectors or over field elements. A single
  nonzero specialization is not this expansion. The `g = 5` enumeration
  does not extend to every `g = 13` prefix by counting; sections 4 through
  8 are the extension. Absence of a search is not nonexistence of every
  interleaved word.
- When `B = 0` the block is zero. The commuting-projector count is not
  re-proved here.
- Native transport, frames, and the selected frontier are untouched.

## 13. Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), with the predecessor statements
in PR #5673, PR #5631, and PR #5617. The adjacent-halves count is PR
#7010. The stage-0-first gap, the five bundles, and the factor
`D_t^{-1}` are PR #7026. The schedule, the single-prefix block
`(D_0+1) B`, and the question answered here are PR #7096. The after-stage-0
correction in PR #7097 is a different word.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
