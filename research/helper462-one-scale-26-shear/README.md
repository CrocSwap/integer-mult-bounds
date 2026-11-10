# A 26-shear one-scale zero-swap word for helper-462

**Constructive witness, plus one polynomial identity. No new κ.**
The selected record stays `781451/250000000`.

The pinned helper-462 matcher has a zero-swap word with exactly one scale, of
coefficient `-16`, and **26 shears**. Open PR #7030 records 29 shears on this
alphabet and this scale. Merged PR #6954 records 53. Twenty-six is strictly
shorter than both. It is the length of this witness. The rank argument
rechecked below gives a lower bound of 8. The integers from 9 through 25 are
open.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status: **refined**.

This package answers open question 1 of open PR #7030 and of finding
[19514166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514166).
The requested step was to keep one scale of coefficient `-16` and replace one
block of the recorded 29-shear word by a shorter shear identity. The witness
keeps that scale. Its shear word is a different factorization of the same
matrix. Inside that factorization, one 4-shear block is replaced by the
3-shear signed exchange below. The column-ordered repair branch of #7030 is
recomputed and still has length 29, so the new word is shorter than that
branch.

Existence of some one-scale word is the theorem of #6954. The repair-family
minimum of 29, for column order `0..7` with the pivot row equal to the column
index, is the census of #7030. This package recomputes only the canonical
branch of that family. It does not rerun the census. The two-scale word with
25 shears is open PR #7012 and uses eleven scales. The P2 ordinary-bill
comparison is merged PR #6950. The rank-bound question left open by #7030 is
not taken here. This package does not change the selected frontier.

`current-priorities.md` on this base still quotes the older selected value
from PR #5599. The verifier reads `certificates/selected-result.json`.

## Alphabet

Rows are numbered `0..7`. A letter is one of:

- a shear `row_a += c * row_b` with `a ≠ b` and `c ∈ Q \ {0}`;
- a single-coordinate scale `row_a *= c` with `c ∈ Q \ {0, 1}`;
- an axis swap of two rows.

A word is applied to `I` from the first letter through the last. Shears
contribute determinant 1, a swap contributes `-1`, and a scale by `c`
contributes `c`. For every word,

`(product of the scale coefficients) * (-1)^{number of swaps} = det(product)`.

The matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`. Its published
24 elementary factors use 5 swaps, 5 scales and 14 shears. That word is
rechecked as a source control. `det(S) = -16`, so a zero-swap word has
scale-product `-16`. One scale is necessary, and that scale has coefficient
`-16`. Both facts are the determinant identity already recorded in #6954.

## The 26-shear word

Let `D` be the diagonal matrix that scales row 0 by `-16` and fixes the other
rows. Let `W = D^{-1} S`, so `det(W) = 1`. The frozen letters are `WORD.json`:
26 shears followed by the scale on row 0 with coefficient `-16`. Counts:
**0 swaps, 1 scale, 26 shears**. Shear denominators are `1, 2, 4, 8, 16`.

Both the successive row operations and the product of the elementary matrices
equal `S`. Dropping any one of the 27 letters, replacing the scale by `-8` or
`+16`, or adding 1 to the first shear coefficient misses `S`. Moving the scale
to the front, or to the position after 10 shears, by the conjugation
`D E D^{-1}` from #7030, keeps 26 shears and still multiplies to `S`.

### Opening block

The first four shears multiply to `diag(-1, 1, 1, 1, 1, 1, -1, 1)`. The same
matrix is the balanced scale of unit `-1` on rows `(0, 6)`:

1. `row_0 += row_6`
2. `row_6 += -2 row_0`
3. `row_0 += row_6`
4. `row_6 += -2 row_0`

The identity sends `(R, S)` to `(-R, -S)`. The verifier checks the general
balanced-scale identity on `2, -16, 1/2, 3/7, -1`, and checks that these four
shears have the same product as the frozen opening block. The remaining 22
shears carry that diagonal matrix to `W`.

### One block replaced by a shorter shear identity

Shears 18 through 20, counting from zero, are

1. `row_6 += row_3`
2. `row_3 += -row_6`
3. `row_6 += row_3`

On rows `(3, 6)` this sends `(R, S)` to `(-S, R)` and fixes every other row.
The four shears

1. `row_3 += -2 row_6`
2. `row_6 += row_3`
3. `row_3 += -row_6`
4. `row_6 += -row_3`

have the same product. Replacing the three shears by those four produces a
27-shear word for `W`, which the verifier also multiplies to `S` after the
scale. The frozen word is the shorter side of that equality.

In the reduction direction, the inverse of that 23-shear tail carries `W` to
the signed diagonal, and the inverse of the opening block carries the
diagonal to `I`. Those 23 shears were proposed by a best-first search over
shears that cancel one existing entry or set one diagonal entry to 1. That
search is a heuristic. It is not a census of rational shears, and it is not
a proof that 23 is the shortest cancellation path. The certificate is the
exact product of the frozen word.

## Two shears change at most one diagonal entry

This is a proof for every pair of elementary shears on these eight rows, and
for every rational coefficient.

Let `E_{ij}(c) = I + c e_{ij}` with `i ≠ j`. Then `e_{ij} e_{kl}` is zero
unless `j = k`, in which case it equals `e_{il}`. Hence

`(I + a E_{t1,s1})(I + b E_{t2,s2}) = I + a E_{t1,s1} + b E_{t2,s2} + ab E_{t1,s1} E_{t2,s2}`.

The first three terms contribute 1 on the diagonal. The last term contributes
to a diagonal entry only when `E_{t1,s1} E_{t2,s2} = E_{t1,t1}`, which
requires `s1 = t2` and `t1 = s2`. That term is `ab` on diagonal index `t1`
and zero on every other diagonal index. A product of two shears therefore has
at most one diagonal entry different from 1.

The verifier expands this product as a polynomial in `(a, b)` for every
ordered pair of the `8 × 7` positions. Each diagonal polynomial is the
constant 1, except for the reciprocal pairs, where it is `1 + ab` at exactly
one index.

Shears 7 through 10 of the frozen word multiply to a matrix whose diagonal
entries in rows 0 and 1 are both different from 1. That block is not a
product of two shears. The identity says nothing about three shears, and it
does not say that every 26-shear word is shortest.

## Comparison with the recorded eliminations

On this same `W`, the elimination of #6954 still uses 15 exchange shears, 28
balanced-scale shears, 4 clears and 6 back-substitutions: **53** shears. The
canonical branch of the #7030 repair, which normalizes each pivot from the
first strictly lower nonzero row and then clears, still uses 6
normalizations, 10 clears and 13 back-substitutions: **29** shears. Both
words are recomputed and both multiply to `S`. The frozen word is shorter
than each of them. Recomputing the canonical branch does not rerun the
repair-family census.

## Rank lower bound, rechecked

For any matrices, `rank(XY - I) ≤ rank(X - I) + rank(Y - I)`. An elementary
shear has rank distance 1 from `I`, so a product of `k` shears has rank
distance at most `k`. Conjugation by `D` preserves shear length, as recorded
in #7030, and every zero-swap one-scale word has the same shear count as a
shear word for `D^{-1} S`. For every scale row, `rank(D^{-1} S - I) = 8`.
Every such word uses at least **8** shears.

This is the bound already stated in #7030. It is rechecked here so the gap is
visible next to the new upper bound. It is not a stronger lower bound.
Lengths 9 through 25 stay open.

## What this does not say

Twenty-six is the length of the frozen word. The cancellation search that
proposed the longer prefix is not a census. No owner, ROW, fallback, tape,
precision, or physical generator is emitted. No supplier is admitted. No P2
ordinary bill is computed. The selected frontier is unchanged. Integer shear
coefficients remain impossible by the argument in #6954; this word uses the
denominator 16.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/helper462-one-scale-26-shear/verify.py
python3 -I -B research/helper462-one-scale-26-shear/verify.py
python3 -O -B research/helper462-one-scale-26-shear/verify.py
python3 -B scripts/research_package.py --package research/helper462-one-scale-26-shear
```

Checks use an explicit failure function, so the proof controls stay active
under `-O`. Expected first-line token:
`PASS_HELPER462_ONE_SCALE_26_SHEAR`.

No Lean, Docker, or selected cold replay was run.

## Open next questions

1. Is there a zero-swap word with exactly one scale of coefficient `-16` and
   fewer than 26 shears? The rank bound rechecked above is 8, so the integers
   9 through 25 are open. A shorter explicit word would still be an upper
   bound. Rational coefficients make the set of words of length at most 25
   infinite.
2. Can a third row shorten the opening balanced scale of unit `-1` on rows 0
   and 6? Those four shears multiply to a diagonal with two entries `-1`.
   Two shears cannot change both diagonal entries. A helper row might still
   shorten the word if that row is restored. Shears 7 through 10 are a
   separate block: they already use rows 0, 1 and 3, and the diagonal
   identity shows they are not two shears. Whether they are three shears is
   the smallest local question.

## Credit

The matcher and the five-swap elimination are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957), using
the helper-462 witness of ai-nanachi #4760/#4814. The 53-shear one-scale word,
the determinant identity, and the integer-coefficient obstruction are PR
#6954. The 29-shear word, the column-ordered repair, the scale-moving lemma,
and the rank lower bound of 8 are open PR #7030. The 7-scale 27-shear schedule
is PR #6947. The 25-shear word in open PR #7012 uses eleven scales and is a
different question. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0.
