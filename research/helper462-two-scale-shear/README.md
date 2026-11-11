# Two-scale zero-swap word for the helper-462 matcher

**Constructive witness. No new κ.** The selected record stays
`781451/250000000`.

There is a zero-swap word for the pinned helper-462 matcher with **at least
two scales** and **25 shears**. Twenty-five is the length of this word. It is
strictly smaller than the recorded 27-shear schedule. This package does not
claim that 25 is minimal, and it does not claim a minimum over words that are
allowed to use exactly one scale.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **refined**.

The assigned question is the shear-count remainder of Discussion #1166 comment
[19137812](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137812),
after open PR #6947. The search in this package is restricted to zero-swap
words with **at least two scales** and fewer than 27 shears.

Exactly-one-scale words are a separate question, answered by a separate open
PR (#6954) and not used here. The inherited P2 ordinary-bill comparison is
also separate (open PR #6950) and is not made here. `current-priorities.md` on
this base still quotes an older selected value from PR #5599. The verifier
reads `certificates/selected-result.json`, whose κ is `781451/250000000`.

## Alphabet and witness

Rows are numbered `0..7`. A letter is a shear `row a += c * row b` (`a ≠ b`,
`c ≠ 0`), a scale `row a *= c` (`c ∉ {0, 1}`), or a swap of two rows. A word is
applied to `I` from the first letter through the last. Shears have determinant
1, a swap contributes `-1`, and a scale by `c` contributes `c`.

The matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`. Its published
factorization uses 5 swaps, 5 scales and 14 shears, and `det(S) = -16`. For
every word in the alphabet,

`(product of the scale coefficients) * (-1)^{number of swaps} = det(product)`.

### Cleanup

Seven integer shears and five scales take `S` to the permutation matrix `P`
whose row `i` is the basis vector `e` at column

`LANDING = (4, 3, 5, 6, 7, 0, 1, 2)`.

Starting from `S`:

| step | letter | effect on the active rows |
| --- | --- | --- |
| 1 | `R2 -= R1` | `R2` becomes `2 e5` |
| 2 | `R2 *= 1/2` | `R2` becomes `e5` |
| 3 | `R1 += R2` | `R1` becomes `e2 + e3` |
| 4 | `R4 += R7` | `R4` becomes `2 e7` |
| 5 | `R4 *= 1/2` | `R4` becomes `e7` |
| 6 | `R7 -= R4` | `R7` becomes `-e2` |
| 7 | `R7 *= -1` | `R7` becomes `e2` |
| 8 | `R1 -= R7` | `R1` becomes `e3` |
| 9 | `R5 -= R1` | `R5` becomes `2 e0` |
| 10 | `R5 *= 1/2` | `R5` becomes `e0` |
| 11 | `R6 -= R1` | `R6` becomes `2 e1` |
| 12 | `R6 *= 1/2` | `R6` becomes `e1` |

Rows 0 and 3 are untouched and stay `e4` and `e6`. The resulting columns are
`LANDING`. As a map on rows, this permutation is the product of cycles
`(0 4 7 2 5)(1 3 6)`.

### Content exchange

For any two rows with contents `(A, B)`, the letters

1. `A += B`
2. `B -= A`
3. `A += B`
4. `B *= -1`

replace `(A, B)` by `(B, A)`. The first three letters alone produce `(B, -A)`;
the scale corrects the sign. The verifier checks the identity on a non-basis
pair and on every spectator row. Each exchange is 3 shears and one scale by
`-1`, and it uses no swap letter.

Sorting `P` into `I` by placing `e_i` into row `i` uses these six exchanges,
in order: `(0, 5)`, `(1, 6)`, `(2, 7)`, `(3, 6)`, `(4, 5)`, `(5, 7)`. That is
18 shears and 6 scales.

### The word

The reduction `R` above is 25 shears and 11 scales, and `R(S) = I`. Row
operations act by left multiplication, so the word for `S` is the reverse of
the letterwise inverse of `R`. Inverting a shear negates its coefficient.
Inverting a scale takes the reciprocal. Every forward shear coefficient is
therefore `±1`. The forward scales are seven copies of `-1` and four copies of
`2`, and their product is `-16`.

Counts of this word: **0 swaps, 11 scales, 25 shears**. Eleven is at least
two. Twenty-five is strictly less than 27. The same verifier recomputes the
elimination from PR #6947 and checks that it is a different word with 0 swaps,
7 scales and 27 shears, also multiplying to `S`. Both words sit in the
at-least-two-scale class. The new fact is the shorter shear count.

Checked controls: deleting the last letter misses `S`; adding 1 to that shear
coefficient misses `S`; replacing one scale by `2` with a scale by `4` misses
`S`; the empty word is `I`; a scale-free signature cannot equal `-16`.

## Overlap

Refreshed upstream `main` is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Open upstream titles for this matcher are PR #6947 (the 27-shear schedule),
PR #6954 (exactly one scale) and PR #6950 (the P2 ordinary bill). A cached
overlap search on 2026-11-10, using the phrases `fewer than 27`, `25 shears`
and `two-scale`, did not surface another word in this restricted class. That
cache is not a novelty certificate. This package does not edit the selected
record.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/helper462-two-scale-shear/verify.py
python3 -I -B research/helper462-two-scale-shear/verify.py
python3 -B scripts/research_package.py --package research/helper462-two-scale-shear
```

Expected first-line token: `PASS_HELPER462_TWO_SCALE_SHEAR`.

## Open next questions

1. Is there a zero-swap word for this same matcher, still with at least two
   scales, whose shear count is strictly less than 25? Twenty-five is one
   explicit upper bound in that class. First step: factor the landing
   permutation `(0 4 7 2 5)(1 3 6)` by scales and integer shears in fewer than
   18 shears, then prepend the inverse of the seven-shear cleanup. An
   incomplete search would not prove that 25 is minimal.
2. In this alphabet, with zero swaps, is the shear length of the landing
   permutation strictly less than 18? Eighteen of the twenty-five shears are
   the six exchanges. First step: keep the pinned landing matrix and factor
   only that permutation. This package does not prove that each exchange
   requires three shears once the exchanges are multiplied together.

## Credit

The matcher, the published five-swap elimination and `det(S) = -16` are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957), using
the helper-462 witness of ai-nanachi #4760/#4814. The 27-shear zero-swap
schedule used as the comparison control is the elimination recorded by open
PR #6947. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
