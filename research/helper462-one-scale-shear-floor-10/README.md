# One-scale helper-462 words need 10 shears

**Proof that every one-scale zero-swap word has at least 10 elementary shears. No new κ.**
The selected record stays `363005817/100000000000`.

PR #7055 proved that the elementary rank-drop depth of each one-scale block is
at most 2, so the shear length is at least 9. PR #7125 exhibits a word of
length 21 and leaves 9 through 21 open. A search that returns no shorter word
is not a lower bound. This package closes the bottom of that interval: length
9 is impossible under the same hypotheses, so the lower bound is 10. Twenty-one
remains an upper bound. Ten is not shown to be sharp.

This is a proof. The length-9 shape is a finite case split. The remaining
obstruction is a finite set of rational pencils, one for each census matrix
and each coordinate position, and every rational coefficient is decided by a
generic depth together with the rational roots of explicit eliminants. It is
not a heuristic search, and it is not a census of the infinite set of words of
length 10 or more.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`e54523517d0f03e58352e647c403a5af3e525a57`. Scope status: **refined**.

The question is open question 1 of PR #7125, the request to raise the
rank-drop floor of #7055 from 9 to 10. The 21-shear word, the 26-shear word,
and the 29-shear word are not redone. The selected frontier is not changed.

`current-priorities.md` on this base may still quote an older selected value.
The verifier reads `certificates/selected-result.json`.

## Hypotheses

Rows are numbered `0..7`. A letter is a shear `row_a += c * row_b` with
`a ≠ b` and `c ∈ Q \ {0}`, a single-coordinate scale, or an axis swap. A word
is applied to `I` from the first letter through the last, by left
multiplication. The pinned matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`. Its determinant is
`-16`.

**Inherited hypotheses, as in #7030 and #7055.** Zero axis swaps and exactly
one scale. The determinant forces that scale to be `-16` on one row. Let `D`
be the corresponding diagonal matrix. Conjugation by `D` sends a shear to a
shear of the same length, with the coefficient multiplied by a ratio of
diagonal entries. It is enough to bound elementary factorizations of the eight
matrices `D^{-1} S`. Each of those matrices lies in `SL(8)` and has rank
distance 8 from `I`. The verifier checks the determinant, the special-linear
blocks, and the rank.

An elementary shear changes `rank(· - I)` by at most 1. Write `ρ` for that
rank and `δ` for the elementary rank-drop depth: the longest chain of left
multiplications by `I - c E_{ij}` that each drop the rank by exactly 1.
Depth is at most the rank, because each step decreases it. A product of `ρ`
shears has depth `ρ`, since the partial products realize a chain of that
length and the opposite inequality is general. This is the depth lemma of
#7055. The positive control here is the same eight-shear word used there: it
has rank 8 and depth 8, so the depth function does attain the rank on some
elementary words.

## The length-9 shape

Let `A = D^{-1} S`, so `ρ(A) = 8`. Suppose `A = T_9 ⋯ T_1` with each `T_k` an
elementary shear, and write `P_0 = I`, `P_k = T_k P_{k-1}`, `r_k = ρ(P_k)`.
Then `r_0 = 0`, `r_9 = 8`, and each step changes the rank by at most 1.

The sum of the nine changes is 8, and each change is in `{-1, 0, +1}`. If `p`,
`m`, and `z` count the increases, decreases, and stalls, then `p + m + z = 9`
and `p - m = 8`, so `2m + z = 1`. The only solution is `m = 0`, `z = 1`.
A length-9 word has exactly one rank-preserving shear and no rank-decreasing
shear.

The first shear takes `I` to a rank-1 matrix, so the stall is not first. Let
it occur at rank `t`. The suffix after the stall consists of `8 - t` shears,
each increasing the rank by 1, from a matrix `Q` of rank `t` up to `A`.
Peeling that suffix is a left rank-drop chain of length `8 - t`, so
`δ(A) ≥ 8 - t`. The census below has `δ(A) ≤ 2`, hence `t ∈ {6, 7, 8}`.
The matrix `Q` is reached by left peels from `A`, so it is one of the census
matrices of rank `t`.

The predecessor `P` of the stall satisfies `Q = T P` with `ρ(P) = ρ(Q) = t`
and with `P` a product of `t` rank-increasing shears from `I`. The depth lemma
gives `δ(P) = t`. Equivalently, `P = (I - c E_{ij}) Q` for some position and
some `c ∈ Q \ {0}`, the rank stays `t`, and the depth equals `t`. A chain of
`t` rank drops from such a `P` ends at `I`, and the suffix peels supply the
rest of the word. So a length-9 word exists if and only if some census matrix
of rank `t ∈ {6, 7, 8}` has a rank-preserving elementary shear whose result
has depth `t`.

## The pencil is finite

Fix a census matrix `Q` of rank `t` and a position `(i, j)`. For
`c ∈ Q` set

`P(c) = (I - c E_{ij}) Q`.

The gap `G(c) = P(c) - I` is affine of rank at most one in `c`: only row `i`
moves, and it moves by a fixed row of `Q`. Every minor is a polynomial in `c`.
Any minor larger than the generic rank is the zero polynomial, so a
specialization cannot raise the rank above the generic rank. Fraction-free
elimination pivots on entries that are not identically zero. At any `c` where
none of those pivot polynomials vanishes, the same pivots remain valid and the
rank equals the generic rank. The only candidates for a different rank are the
rational roots of those pivots.

- If the generic rank is below `t`, no coefficient preserves rank `t`.
- If the generic rank is above `t`, the only coefficients that can land on
  rank `t` are those pivot roots. Each is evaluated exactly.
- If the generic rank equals `t`, every coefficient outside the pivot roots
  preserves rank. A root of a pivot drops the rank and is not a stall. Depth
  on the preserving coefficients is the remaining point.

On that preserving set, the rank-drop edges are the positions where both
standard-basis memberships hold and the pairing of #7055 is nonzero. The
unique coefficient is the reciprocal of that pairing. Membership and the
pairing are rational functions, read off one elimination of `G(c)`. A vector
that lies in the image generically stays in the image wherever the rank keeps
its generic value. A vector that lies outside enters only at the roots of the
inconsistency numerators. Those roots, the poles of the peel coefficients, and
the same data for every generic child are an explicit finite set `E ⊂ Q`.

For `c ∉ E` the edge set is a subset of the generic edge set, and each child
is the specialization of the corresponding polynomial child. Depth is therefore
at most the generic depth. The walk that builds `E` also computes that generic
depth, and one rational sample outside `E` is required to reproduce it by the
numeric depth function. The two implementations are independent: integer
factorization of a specialized gap, against fraction-free elimination of the
polynomial gap. They must agree. Every rational root in `E` is then evaluated
by the numeric function, and only the coefficients that still have rank `t`
are kept. Matrix entries that appear in the walk have degree at most 2; the
verifier rejects a deeper entry.

Degree 1 contributes one root, the slope ratio. Degree 2 contributes a
rational root exactly when the discriminant is a perfect square, tested by an
exact integer square root. Degree 3 and higher uses the rational-root theorem.
The constant and leading coefficients are factored completely, and primality
of every factor below `2^64` is the deterministic Miller-Rabin test with the
Sinclair bases. A coefficient of degree 3 or more with more than 64 bits is a
hard failure, not a skipped root. On every scale row the highest degree of a
polynomial whose roots were required is 8, and the verifier rejects any other
degree. No such coefficient exceeded the 64-bit factor bound: a larger one
aborts the run.

The 3×3 control is the matrix reached by the shears `(0,1,-2)`, `(1,0,-2)`,
`(0,2,-2)`. It has rank 2 and depth 0. One elementary shear raises the depth
to 2 while keeping the rank. The same predicate that accepts every helper
census matrix rejects this one. The checker is not reporting "depth stays
small" because it cannot see a jump.

## Census and the bound

The verifier expands the whole rank-drop tree of each `D^{-1} S`. Every left
rank-drop shear is the unique cancelling coefficient of the #7055 pairing:
the target basis vector lies in the column space of the gap, the source basis
vector lies in the row space, and the pairing is nonzero. The census asks
that question for every ordered pair, by exact integer elimination. Every
reported peel is checked to drop the rank by 1, and the walk does not stop at
a preset rank. A missed edge would be a missed peel, so the depth bound is
the depth of this exhaustive tree. No branch reaches rank 5 or below, so the depth is at most 2
and the length-9 shape applies. Distinct matrices are fewer than the arrival
counts of #7055: rows 0, 1, 2, and 4 have 37 arrivals at rank 6 and 20
distinct matrices; row 5 has 4 arrivals and 2 distinct matrices. The edge
counts agree with #7055 either way.

| scale row | `det(W - I)` | depth | distinct ranks 8, 7, 6 | max preserving depth at those ranks |
| --- | --- | --- | --- | --- |
| 0, 1, 2, 4 | 1/2 | 2 | 1, 33, 20 | 3, 2, 1 |
| 5 | 1/2 | 2 | 1, 36, 2 | 3, 2, 1 |
| 3, 6 | 21/8 | 1 | 1, 38, 0 | 2, 1 |
| 7 | 19/4 | 1 | 1, 48, 0 | 2, 1 |

Every one of those depths is strictly below the rank of its matrix. No
rank-preserving shear of a census matrix has depth equal to the rank. Length
9 is impossible.

Combined with the subadditive bound and the depth lemma, the shear length is
at least 10. The 21-shear word of #7125 remains an upper bound and is not
reproved here. The integers 10 through 21 stay open. Nothing in this argument
changes the selected κ.

## What this does not say

Ten is not shown to be sharp. A length-10 word has either two stalls or one
descent and one stall, and that case split is not taken. The bound uses
elementary coordinate shears, zero swaps, and one scale. It does not say that
`D^{-1} S` fails to be a product of nine arbitrary transvections.

No owner, ROW, fallback, tape, precision, or physical generator is emitted.
No supplier is admitted. No P2 ordinary bill is computed.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/helper462-one-scale-shear-floor-10/verify.py
python3 -I -B research/helper462-one-scale-shear-floor-10/verify.py
python3 -O -B research/helper462-one-scale-shear-floor-10/verify.py
python3 -B scripts/research_package.py --package research/helper462-one-scale-shear-floor-10
```

Checks use an explicit failure function, so they stay active under `-O`.
The certificate uses four worker processes when the machine has them. On this
4-CPU machine the registered replay finished in 190.48 seconds, `python3 -O -B`
in 192.01 seconds, and `python3 -I -B` in 189.13 seconds. Expected last line
begins with `PASS_HELPER462_ONE_SCALE_SHEAR_FLOOR_10`.

No Lean, Docker, or selected cold replay was run.

## Open next questions

1. Is 10 sharp for a one-scale zero-swap elementary word in the pinned
   helper-462 matcher, or does a second obstruction force length at least 11?
   The certificate rules out length 9, and the upper bound is still the
   21-shear word of PR #7125, so 10 through 21 remain open. A word of length
   10 would show that 10 is sharp. The useful first step is to classify a
   length-10 rank profile: the changes sum to 8 over 10 steps, so either two
   shears preserve rank or one descent accompanies one stall. The same census
   is the place to look. It is blocked by the free coefficient of each
   non-dropping shear; the length-9 case split does not cover two stalls.

## Credit

The rank subadditivity bound of 8 and the one-scale reduction are from PR
#7030. The depth lemma, the pairing criterion, and the bound of 9 are from PR
#7055. The upper bound of 21 is the word in PR #7125; this package does not
recompute it. The census edge counts match #7055; the rank-6 column here
counts distinct matrices rather than arrivals.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
