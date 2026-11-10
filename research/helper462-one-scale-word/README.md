# One-scale zero-swap word for the helper-462 matcher

**Constructive witness, plus a scoped integer-coefficient proof. No new κ.**
The selected record stays `781451/250000000`.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **refined**.

Handoff comment
[19137812](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137812)
leaves the literal stock/role/route generator open. Finding
[19492596](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19492596)
and fork draft PR 150 answer one letter-count piece of that handoff: the pinned
helper-462 matcher has a zero-swap word with 7 scales and 27 shears, and at
least one scale is necessary because `det(S) = -16`. This package takes the
remaining one-scale question from that finding's open remainder and from PR 150's
second open question. It does not rebuild the 7-scale word, price inherited P2
tariffs, or search for a word with fewer than 27 shears at two or more scales.

`current-priorities.md` on this base still quotes the older selected value from
PR #5599. The verifier reads `certificates/selected-result.json`. That record is
`781451/250000000`. This package does not edit it.

## Alphabet

Rows are numbered `0..7`. A letter is one of:

- a shear `row_a += c * row_b` with `a ≠ b` and `c ∈ Q`;
- a single-coordinate scale `row_a *= c` with `c ∈ Q \ {0}`;
- an axis swap of two rows.

A word is applied to `I` from the first letter through the last. Shears
contribute determinant 1, a swap contributes `-1`, and a scale by `c`
contributes `c`. For every word,

`(product of the scale coefficients) * (-1)^{number of swaps} = det(product)`.

The pinned matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`. The same file's
24 elementary factors multiply to `S` and use 5 swaps, 5 scales and 14 shears.
That published word is rechecked as a source control. Its five swaps stay a
valid schedule.

## Witness

`det(S) = -16`. Let `D` be the diagonal matrix that scales row 0 by `-16` and
fixes the other rows. Then `W = D^{-1} S` has determinant 1. The elimination
below writes `W` as 53 rational shears. Appending the scale by `-16` on row 0
therefore multiplies to `S`.

The frozen letters are `WORD.json`. Counts: **0 swaps, 1 scale, 53 shears**.
The scale is the last letter, on row 0, with coefficient `-16`. Every shear
coefficient lies in `Z[1/2]`; the denominators that occur are `1, 2, 4, 16`.
The same elimination with the final scale placed on any other single row also
multiplies to `S`, again with 53 shears. Those eight schedules are explicit
words. Fifty-three is the length of this elimination, not a minimum.

The witness is checked by exact rational arithmetic in two multiplications:
successive row operations, and the product of the corresponding elementary
matrices. Dropping any one of the 54 letters, changing the scale to `-8` or
`+16`, or adding 1 to the first shear coefficient misses `S`.

The determinant identity is a proof for every word in this alphabet: a
zero-swap word has scale-product `-16`, so it uses at least one scale, and a
single scale must have coefficient `-16`. The word above shows that one scale
is also sufficient. The minimum number of scale letters in a zero-swap word is
therefore exactly one. That minimum is not a statement about shear length.

### Balanced scale

For `u ∈ Q \ {0}` and two distinct rows `(R, S)`, the shears

1. `R := R - (1/u) S`
2. `S := S + (u - 1) R`
3. `R := R + S`
4. `S := S + (1/u - 1) R`

replace `(R, S)` by `(u R, S/u)`. The verifier checks this identity on
`2, -16, 1/2, 3/7, -1`. Expanding step 2 gives
`S = (u-1)R_old + S_old/u`, and step 3 then collapses the first row to `u R_old`.
Step 4 cancels the `(u-1) R_old` term against `(1/u - 1) u R_old`.

### Signed exchange

The three shears `R := R + S`, `S := S - R`, `R := R + S` send `(R, S)` to
`(S, -R)`. No swap letter is used. The determinant of this `2×2` action is 1.

### Elimination

Start from a matrix of determinant 1. For each column `k` from `0` through `6`:

- If the pivot is `0`, signed-exchange row `k` with the first later nonzero row
  in that column. The processed columns `0..k-1` are already zero on every row
  `≥ k`, so the exchange stays inside the trailing block.
- If the pivot `p` is not `1`, apply the balanced scale on rows `(k, k+1)` with
  unit `1/p`. Row `k` is multiplied by `1/p` and row `k+1` by `p`, so the pivot
  becomes `1`.
- Clear strictly below the pivot by shears.

After column `k-1`, the leading `k×k` block is upper triangular with unit
diagonal, hence determinant 1, and the block under it is zero. The whole
determinant is 1, so the trailing minor has determinant 1 and its first column
is not zero. The last diagonal entry is that final `1×1` minor, so it equals 1
and needs no scale. Back-substitution from column `7` down to column `0` clears
above each pivot. Reversing the reduction and negating each coefficient is a
shear word for the determinant-1 matrix.

Controls: the identity reduces to the empty word, and `diag(2, 1/2, 1, …, 1)`
reduces to shears only.

## Integer coefficients are impossible

This is a proof under stated hypotheses. It is not a proof that every larger
alphabet fails, and it is not a census of rational words.

**Hypotheses.** Zero axis swaps, exactly one scale, and every shear coefficient
an ordinary integer. The determinant identity forces that scale coefficient to
be `-16`. The matrix of the word is therefore `E1 * D_i * E2`, where `D_i`
scales coordinate `i` by `-16` and fixes the others, and `E1, E2` are products
of integer elementary shears. Each shear is invertible over `Z`, so left or
right multiplication by it preserves the gcd `Δ_6` of the `6×6` minors.

`D_i` has at least six diagonal entries equal to `1`. The corresponding `6×6`
minor is `I_6`, so `Δ_6(D_i) = 1`. The verifier checks the case `i = 0` on rows
and columns `1..6`.

`S` has rank `5` over `F_2`, by the following reduction. Entries of `S` mod 2:

```
row 0: 0 0 0 0 1 0 0 0
row 1: 0 0 1 1 0 1 0 0
row 2: 0 0 1 1 0 1 0 0
row 3: 0 0 0 0 0 0 1 0
row 4: 0 0 1 0 0 0 0 1
row 5: 0 0 0 1 0 0 0 0
row 6: 0 0 0 1 0 0 0 0
row 7: 0 0 1 0 0 0 0 1
```

Rows `2, 6, 7` repeat rows `1, 5, 4`. Columns `0` and `1` are identically zero.
On the five remaining rows, add row 5 into row 1 and then the new row 1 into
row 4. The leading ones sit in columns `4, 3, 6, 2, 5`, all different, so these
five rows are independent and the rank is exactly 5. Every six rows are
dependent over `F_2`, every `6×6` minor is even, and `Δ_6(S)` is even. It
cannot equal `Δ_6(D_i)`.

So no integer-shear, zero-swap, one-scale word multiplies to `S`. The dyadic
witness above uses a denominator `16`, which is consistent with this
obstruction: the witness is not an integer word.

## Minor census

Separately, every `k×k` minor is enumerated. There are `C(8,k)^2` of them for
each `k`, and the loops have no early exit. Exact Gaussian elimination produces
the determinantal divisors

`Δ = (1, 1, 1, 1, 1, 2, 4, 16)`.

The invariant factors are `Δ_k / Δ_{k-1}` with `Δ_0 = 1`:

`(1, 1, 1, 1, 1, 2, 2, 4)`.

Each divides the next, and the product is `16 = |det(S)|`. This is an exhaustive
finite census of minors. It is not a census of words. The impossibility proof
above uses only that `Δ_6(S)` is even; the census records the exact value `2`.

The single scale `diag(-16, 1, …, 1)` has `F_2`-rank 7, so the rank test does
not reject every matrix of determinant `-16`.

## What this does not say

Fifty-three shears is the length of this elimination. A zero-swap word with at
least two scales and fewer than 27 shears was not searched. Inherited P2
tariffs were not evaluated, so no completed ordinary bill is claimed. No owner,
ROW, fallback, tape, precision, or physical generator is emitted. No supplier
is admitted. The selected frontier is unchanged.

## Reproduce

From the repository root, Python 3.12.3, standard library only:

```sh
python3 -B research/helper462-one-scale-word/verify.py
python3 -I -B research/helper462-one-scale-word/verify.py
python3 -O -B research/helper462-one-scale-word/verify.py
python3 -B scripts/research_package.py --package research/helper462-one-scale-word
```

Expected first-line token: `PASS_HELPER462_ONE_SCALE_WORD`.

No Lean, Docker, or selected cold replay was run.

## Open next questions

1. What is the minimal number of shears in a zero-swap word that uses exactly
   one scale? The elimination above has length 53 on every coordinate. A shorter
   one-scale word would still be an upper bound unless the search is exhaustive.
   Keeping the scale count at one separates this question from a search at two
   or more scales.
2. Is there a zero-swap word whose scale coefficients multiply to `-16`, with
   at least two scales and fewer than 27 shears? The 7-scale schedule has 27
   shears and this witness has 53. Neither schedule answers that question, and
   this package does not search it.
3. With the inherited P2 tariffs, does any legal word beat the published pair on
   the completed ordinary bill? Letter counts do not determine that bill. This
   package records no tariff.

## Credit

The matcher and the five-swap elimination are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957), using
the helper-462 witness of ai-nanachi #4760/#4814. The zero-swap 7-scale,
27-shear schedule and the determinant lower bound of one scale are finding
19492596 / fork draft PR 150. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Apache-2.0.
