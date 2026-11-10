# Rank-drop depth for one-scale helper-462 words

**Proof that every one-scale zero-swap word has at least 9 shears. No new κ.**
The selected record stays `781451/250000000`.

The bound of 8 in open PR #7030 is the subadditive rank bound, and it meets
`rank(W - I) = 8` on the recorded matrix. The invariant here is different: the
elementary rank-drop depth. On the recorded 29-shear word that depth is 2.
The same census on every scale row has depth at most 2, so length 8 is
impossible and the lower bound is 9. Twenty-nine remains an upper bound
because that recorded word still multiplies to the matcher. The integers 9
through 28 stay open.

This is a proof. Its finite part is an exhaustive census of a finite tree.
It is not a heuristic search, and it is not a census of the infinite set of
rational words of length at least 9.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status: **refined**.

The question is open question 2 of PR #7030 and of the finding recorded with
that PR. Subadditivity of `rank(W - I)` cannot be the source of a stronger
bound, because it already equals 8 on this matrix. The shorter-word question,
open question 1 of the same PR, is not taken here.

`current-priorities.md` on this base still quotes the older selected value
from PR #5599. The verifier reads `certificates/selected-result.json`.

## Hypotheses

Rows are numbered `0..7`. A letter is one of:

- a shear `row_a += c * row_b` with `a ≠ b` and `c ∈ Q \ {0}`;
- a single-coordinate scale `row_a *= c` with `c ∈ Q \ {0, 1}`;
- an axis swap of two rows.

A word is applied to `I` from the first letter through the last, equivalently
by left multiplication. Shears have determinant 1, a swap has determinant
`-1`, and a scale by `c` has determinant `c`. The pinned matcher `S` is the
`matcher` field of `research/bit-completed-backend-api/science/RESULT.json`.
Its determinant is `-16`. The same file's 24 right-route factors multiply to
`S` and are rechecked as a source control.

**Inherited hypotheses.** Zero axis swaps and exactly one scale. The
determinant identity forces that scale to be `-16` on one row. Let `D` be the
corresponding diagonal matrix. For shear products `A` and `B`,

`B D A = D (D^{-1} B D) A`.

If `E = I + c E_{ij}` adds `c` times row `j` into row `i`, then

`D^{-1} E D = I + c (d_j / d_i) E_{ij}`.

Conjugation therefore sends shear words to shear words of the same length.
The right-hand side has the scale last, and its shear product is `D^{-1} S`.
It is enough to bound elementary factorizations of the eight matrices
`D^{-1} S`.

The verifier checks both directions on the recorded word. Moving the final
scale to the front, or to the position after 10 shears, replaces each shear
that lands to the left of `D` by `D E D^{-1}`, whose coefficient is
`c (d_i / d_j)`. Moving that scale back to the end uses `D^{-1} E D`. Each
moved word still multiplies to `S` and still has 29 shears, and the restored
shear block equals `D^{-1} S` for row 0.

## The recorded word

`WORD.json` is the scale-last word from PR #7030 at commit
`98238eeed3faca9f0a5f1d4060db5d5da524a192`. Counts: **0 swaps, 1 scale, 29
shears**. The scale is last, on row 0, with coefficient `-16`. Both the row
operations and the agreement of the shear block with `D^{-1} S` are checked.
Replacing the scale by `-8`, adding 1 to the first shear, or dropping the
first shear misses `S`.

Twenty-nine is an upper bound exhibited by this word. It is not a minimum,
and this package does not search for a shorter word.

## Rank subadditivity still gives 8

For any matrices, `rank(XY - I) = rank(X(Y - I) + (X - I))` is at most
`rank(Y - I) + rank(X - I)`. An elementary shear `E` has `rank(E - I) = 1`,
so a product of `k` shears has rank distance at most `k` from `I`.

For every scale row, `rank(D^{-1} S - I) = 8`. Every one-scale zero-swap word
therefore has at least 8 shears. The verifier checks the rank-1 calculation
on one shear. This is the bound already proved in #7030. It is sharp as a
statement about rank: the positive control below is a product of 8 shears
whose rank distance is 8. The matrix `D^{-1} S` meets the same rank, so a
stronger lower bound has to use something other than this rank.

## The rank-drop depth

Let `A ∈ SL(n, Q)`. A **left rank-drop step** is a triple `(i, j, c)` with
`i ≠ j` and `c ∈ Q \ {0}` such that

`B = (I - c E_{ij}) A` satisfies `rank(B - I) = rank(A - I) - 1`.

The **elementary rank-drop depth** `δ(A)` is the length of the longest chain
of such steps. Each step decreases the rank, so `δ(A) ≤ rank(A - I)`, and the
directed graph of steps is a finite tree once repeated matrices are not an
issue: depth is at most `n`.

### One coefficient per edge

Let `M` have rank `r ≥ 1`, and fix indices `i, j`. As a function of `c`,
every `r × r` minor of `M - c E_{ij}` is affine. Suppose two distinct values
of `c` both drop the rank. Every `r × r` minor vanishes at those two values,
hence is the zero polynomial, including at `c = 0`. That contradicts
`rank(M) = r`. So each ordered pair `(i, j)` admits at most one cancelling
coefficient.

The same conclusion has a closed form. Write `u = e_i` and `v = e_j`.

**Pairing criterion.** There exists `c` with `rank(M - c u v^T) = rank(M) - 1`
if and only if `u` lies in the column space of `M`, `v` lies in the row
space, and `y^T u ≠ 0` for a solution of `M^T y = v`. The scalar
`y^T u` does not depend on the choice of `y`: the difference of two solutions
lies in `ker(M^T) = im(M)^⊥` and `u` lies in `im(M)`. The unique coefficient
is `c = 1 / (y^T u)`.

One direction: if `M x = u` and `c (y^T u) = 1`, then
`(M - c u v^T) x = u - c u (v^T x) = u - c u (y^T u) = 0`. Here `x` is not in
`ker(M)` because `M x = u ≠ 0`. Nullity therefore increases. A rank-one
modification changes rank by at most 1, because
`im(M + u v^T) ⊆ im(M) + span(u)` and the same inclusion with the update
reversed gives the other inequality. Rank drops by exactly 1.

The other direction: if the rank drops at some `c`, the column space can lose
dimension only if `u` is already in it, and the same statement for the
transpose puts `v` in the row space. A vector `z` outside `ker(M)` with
`(M - c u v^T) z = 0` gives `M z = c (v^T z) u` with `v^T z ≠ 0`, so
`v^T x = 1/c` for `x = z / (c v^T z)`, and then `y^T u = v^T x = 1/c`.

The census enumerates edges by the minor test. That enumeration is complete
without the pairing formula: if the rank drops, every maximal minor vanishes,
and a nonconstant affine minor has only one root. A nonzero constant minor
never vanishes, so that edge has no coefficient. The pairing test is computed
on the same edges and must return the same coefficient. On a full-rank gap
that value is also the reciprocal of one entry of `(A - I)^{-1}`.

### Depth is an obstruction to a tight factorization

**Lemma.** If `A` is a product of `r = rank(A - I)` elementary shears, then
`δ(A) = r`.

Write `A = T_r ⋯ T_1` and `P_m = T_m ⋯ T_1`. Rank subadditivity gives
`rank(P_m - I) ≤ m`. The final rank is `r` after `r` steps, and each step
increases rank by at most 1, so `rank(P_m - I) = m` for every `m`. Peeling
`T_r`, then `T_{r-1}`, and so on, is a rank-drop chain of length `r`. The
opposite inequality `δ(A) ≤ r` holds for every matrix. Therefore a matrix
with `δ(A) < rank(A - I)` is not a product of `rank(A - I)` elementary
shears.

Combined with the subadditive bound, its elementary shear length is at least
`rank(A - I) + 1`.

## Census

For each scale row the verifier expands the whole tree of `D^{-1} S`. The
node and edge counts below are the census. A missing lower rank means that
count is zero. No branch reaches `I`.

| scale row | `det(W - I)` | depth | nodes at ranks 8, 7, 6 | edges out of ranks 8, 7 |
| --- | --- | --- | --- | --- |
| 0, 1, 2, 4 | 1/2 | 2 | 1, 33, 37 | 33, 37 |
| 5 | 1/2 | 2 | 1, 36, 4 | 36, 4 |
| 3, 6 | 21/8 | 1 | 1, 38, 0 | 38, 0 |
| 7 | 19/4 | 1 | 1, 48, 0 | 48, 0 |

The recorded word uses scale row 0, so the invariant evaluates to **depth 2**
on that word's shear matrix. Every row has depth at most 2, strictly below
8. Every one-scale zero-swap word therefore has at least **9** shears.

The tree is finite because each of the `8 · 7` edges has at most one
coefficient and the rank decreases at every step. The walk visits every node
those edges generate. That is the completeness argument for this census. It
does not enumerate words that contain a shear which fails to drop the rank.
Such a shear is exactly what a word of length 9 or more must contain, and its
coefficient is not fixed by the equation above.

## Controls that separate this invariant from rank

The eight shears

`(0,1,-1), (1,0,1/2), (2,3,1), (3,2,2), (4,5,1), (5,4,3), (6,7,3), (7,6,3)`,

applied in that order, multiply to a matrix in `SL(8)` of rank distance 8.
Both peel rules recover the word from the outside and finish at `I`. Rank
subadditivity is therefore attained by some elementary words. It is the
matrix `D^{-1} S`, not the inequality, that blocks length 8.

On `2 × 2` matrices, the balanced scale from #7030,

1. `R += -(1/u) S`
2. `S += (u - 1) R`
3. `R += S`
4. `S += (1/u - 1) R`,

sends the identity to `diag(2, 1/2)` when `u = 2`. That matrix has rank
distance 2 and **no** rank-drop step, so its depth is 0. Four shears realize
it. This is the same phenomenon on the example #7030 used to show that a
balanced scale can be longer than the rank distance. Depth sees that gap;
rank subadditivity does not.

## What this does not say

Nine is not shown to be sharp. A word of length 9 would have exactly one
shear that does not drop `rank(· - I)`, and this tree does not contain that
shear. The recorded word of length 29 is an upper bound, not a minimum.
Open question 1 of #7030, the search for a word with fewer than 29 shears,
is untouched.

No owner, ROW, fallback, tape, precision, or physical generator is emitted.
No supplier is admitted. No P2 ordinary bill is computed. Integer shear
coefficients remain impossible by the argument in #6954; the recorded word
uses the denominator 16. The selected frontier is unchanged.

The obstruction uses elementary, coordinate shears. It does not claim that
`D^{-1} S` fails to be a product of eight arbitrary transvections.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/helper462-one-scale-rank-drop/verify.py
python3 -I -B research/helper462-one-scale-rank-drop/verify.py
python3 -O -B research/helper462-one-scale-rank-drop/verify.py
python3 -B scripts/research_package.py --package research/helper462-one-scale-rank-drop
```

Checks use an explicit failure function, so they stay active under `-O`.
Expected first-line token: `PASS_HELPER462_ONE_SCALE_RANK_DROP`.

No Lean, Docker, or selected cold replay was run.

## Open next questions

1. Can the elementary shear lower bound be raised above 9 under the same
   zero-swap, one-scale hypotheses? Length 8 is impossible, and the recorded
   word has 29 shears, so 9 through 28 remain open. A non-dropping shear has
   a coefficient that the rank-drop equation does not fix, and the set of
   length-9 words over `Q` is infinite. The useful first step is to name an
   invariant that charges one shear which does not drop `rank(· - I)`, and
   to evaluate it on this same recorded word. An explicit word shorter than
   29 is open question 1 of #7030 and is not taken here.

## Credit

The matcher and the 24 right-route factors are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957),
using the helper-462 witness of ai-nanachi #4760/#4814. The determinant
identity, the integer-coefficient obstruction, and the balanced-scale
identity are PR #6954. The recorded 29-shear word, the scale-moving lemma,
and the rank lower bound of 8 are PR #7030. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0.
