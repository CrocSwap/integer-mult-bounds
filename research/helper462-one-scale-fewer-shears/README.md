# Fewer shears in a one-scale zero-swap word for helper-462

**Constructive witness, plus one finite census and a rank lower bound. No new κ.**
The selected record stays `781451/250000000`.

The pinned helper-462 matcher has a zero-swap word with exactly one scale, of
coefficient `-16`, and **29 shears**. The merged elimination in PR #6954 uses
53 shears on the same alphabet and the same scale. Twenty-nine is strictly
shorter. It is the minimum inside the column-ordered repair family defined
below. The rank argument gives a lower bound of 8 for every one-scale
zero-swap word. The integers from 9 through 28 are open.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status: **refined**.

This package answers open question 1 of merged PR #6954 and of finding
[19507194](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507194).
The requested first step was to keep one scale of coefficient `-16` and replace
one balanced-scale block by a shorter shear identity. The witness replaces
every balanced-scale block, and every signed exchange, by a one-shear pivot
repair.

Existence of some one-scale word is already the theorem of #6954. The
two-scale word with 25 shears is open PR #7012 and uses eleven scales. The P2
ordinary-bill comparison is merged PR #6950. This package does not rebuild
those results and does not change the selected frontier.

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
`-16`. Both facts are the determinant identity; #6954 already recorded them.

## Moving the scale does not change the shear count

Let `D` be the diagonal matrix that scales one fixed row by `-16` and fixes
the others. For an elementary shear `E` that adds `c` times row `source` into
row `target`,

`D E D^{-1}` is the shear with coefficient `c * d_target / d_source`.

Conjugation by `D` or by `D^{-1}` therefore sends shear words to shear words
of the same length. Suppose a zero-swap one-scale word has matrix product
`B D A`, with `A` and `B` shear products (`A` is applied first). Then

`B D A = D (D^{-1} B D) A`.

The parenthesized factor is a shear word as long as `B`. The right-hand side
has the scale last, and its shear product equals `D^{-1} S`. It is enough to
bound words whose scale is the last letter.

The verifier also runs the opposite direction on the witness. Starting from
the scale-last word, it moves the scale to the front and to the position
after 10 shears by replacing each later shear `E` with `D E D^{-1}`. Each
moved word still multiplies to `S` and still has 29 shears. Putting the scale
back at the end recovers a scale-last word for `S`.

## The 29-shear word

Let `W = D^{-1} S` with the scale on row 0, so `det(W) = 1`. The witness is
the shear word for `W` followed by the scale. The frozen letters are
`WORD.json`. Counts: **0 swaps, 1 scale, 29 shears**. The scale is the last
letter, on row 0, with coefficient `-16`. Shear denominators are
`1, 2, 4, 8, 16`.

Both the successive row operations and the product of the elementary matrices
equal `S`. Dropping any one of the 30 letters, replacing the scale by `-8` or
`+16`, or adding 1 to the first shear coefficient misses `S`.

### What changed relative to the 53-shear elimination

On `W`, the merged elimination uses 15 exchange shears (five signed exchanges),
28 balanced-scale shears (seven blocks of four), 4 clears below pivots and 6
back-substitutions. The four-shear block is the identity

1. `R += -(1/u) S`
2. `S += (u - 1) R`
3. `R += S`
4. `S += (1/u - 1) R`

which replaces `(R, S)` by `(u R, S/u)`. The verifier checks it on
`2, -16, 1/2, 3/7, -1`.

The shorter elimination keeps pivot rows `0..7` and column order `0..6`. When
the pivot `p` is not 1, and some strictly lower row has a nonzero entry `a` in
that column, one shear

`pivot_row += ((1 - p) / a) * helper_row`

makes the pivot 1. The canonical branch always takes the first such helper.
On this `W` every non-unit pivot has such a helper, including the pivots that
are 0. Columns 0 and 1 of `W` each contain a single entry 2, in rows 5 and 6.
Row 0 is 0 in column 0, and the first shear imports row 5 into row 0.

The resulting counts are 6 one-shear normalizations, 10 clears and 13
back-substitutions. No signed exchange and no balanced-scale block remains.
`6 + 10 + 13 = 29`.

### The empty column-order probe

A probe that enumerated all `8!` column orders returned no word. It pivoted
only on a row that was already nonzero, and it asked for a second nonzero in
that column before changing an entry that was not 1. It also discarded a
residual row permutation unless that permutation was already the identity.
Columns 0 and 1 of `W` are single entries equal to 2, so that second-nonzero
rule has no move on either column. The 29-shear word is the other rule: it
writes into a row whose current entry is 0. The empty return is that filter.
It is not a census of column orders and it is not a lower bound.

## Census of the repair family

The family is finite, and the verifier expands it completely except for one
monotone discard. At column `k`, the pivot row is `k`.

- If the pivot is 1, clear strictly below it.
- If the pivot is not 1, each strictly lower row with a nonzero in the column
  is one legal one-shear normalization.
- If the pivot is nonzero, each strictly lower row is also one legal 4-shear
  balanced scale, using the identity above.
- After the pivot equals 1, clear every nonzero strictly below it.
- Then clear strictly above the unit diagonal.

A partial branch is discarded only when the shears already chosen are at least
as many as a completed word. Later steps add shears, so a discarded branch
does not contain a shorter completed word. The search starts with no
incumbent. The minimum length in this family is **29** when the scale sits on
any row except row 2, where the minimum is 30. The witness attains 29 for row
0. This is an exhaustive finite census of this family. It is a census of these
elimination choices, and the set of all rational shear words is a larger set.

## Rank lower bound

For any matrices, `rank(XY - I) = rank(X(Y - I) + (X - I))` is at most
`rank(Y - I) + rank(X - I)`. An elementary shear `E` has `rank(E - I) = 1`.
A product of `k` shears therefore satisfies `rank(W - I) ≤ k`.

By the scale-moving lemma, every zero-swap one-scale word has the same shear
count as a word for `D^{-1} S` with the scale last. For every scale row,
`rank(D^{-1} S - I) = 8`. Every zero-swap one-scale word therefore uses at
least **8** shears. The verifier also checks the subadditivity on one explicit
pair of shears, and checks that `diag(2, 1/2)` has rank distance 2 from `I`
while the balanced scale realizes it in four shears.

Eight is a proved lower bound under these hypotheses: zero swaps, exactly one
scale, and elementary rational shears. It leaves 9 through 28 open. The
29-shear word is an upper bound. A failed search outside the family would not
close that gap.

## What this does not say

No owner, ROW, fallback, tape, precision, or physical generator is emitted.
No supplier is admitted. No P2 ordinary bill is computed. The selected
frontier is unchanged. Integer shear coefficients remain impossible by the
argument in #6954; this word uses the denominator 16, so it sits outside that
integer hypothesis.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/helper462-one-scale-fewer-shears/verify.py
python3 -I -B research/helper462-one-scale-fewer-shears/verify.py
python3 -O -B research/helper462-one-scale-fewer-shears/verify.py
python3 -B scripts/research_package.py --package research/helper462-one-scale-fewer-shears
```

Checks use an explicit failure function, so the proof controls stay active
under `-O`. Expected first-line token:
`PASS_HELPER462_ONE_SCALE_FEWER_SHEARS`.

No Lean, Docker, or selected cold replay was run.

## Open next questions

1. Is there a zero-swap word with exactly one scale of coefficient `-16` and
   fewer than 29 shears? The repair-family census stops at column order
   `0..7` with the pivot row equal to the column index. The rank bound is 8,
   so the integers 9 through 28 are open. A shorter explicit word would still
   be an upper bound. Rational coefficients make the set of words of length
   at most 28 infinite, so closing the gap needs a different invariant or a
   finite coefficient bound.
2. Can the rank lower bound of 8 be raised under the same hypotheses? One
   shear has rank distance 1 from `I`, and subadditivity is sharp enough to
   reach 8 on this matrix. A stronger bound has to use more than
   `rank(W - I)`.

## Credit

The matcher and the five-swap elimination are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957), using
the helper-462 witness of ai-nanachi #4760/#4814. The 53-shear one-scale word,
the determinant identity, and the integer-coefficient obstruction are PR
#6954. The 7-scale 27-shear schedule is PR #6947. The 25-shear word in open
PR #7012 uses eleven scales and is a different question. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
