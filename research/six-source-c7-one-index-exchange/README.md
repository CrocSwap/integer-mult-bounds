# One off-diagonal pair does not finish the six-source c=7 weight-3 count

**Scoped exchange obstruction. No new κ.** In the unchanged unsigned dirty
connector, let a floor word on six sources in characteristic 7 call each
source seven times. Suppose exactly one index `s` in `4..22` fails to make
`q_s + q_{45-s}` a weight-3 mask. Adding the early pair `(0, 3)` and any one
pair off `s + t = 45` still leaves at least one of the `C(6, 3) = 20`
weight-3 masks unrealized. The cover has size at most 19, and the literal
word below attains 19.

This does not decide whether a six-source depth-two block exists at `c = 7`.
Masks of every weight other than 3, two or more off-diagonal pairs, and two
or more failed diagonal indices stay open. The selected conditional κ is
unchanged.

## Inherited interface

A floor word has length 42. `q_t` counts the first `t` letters, so `q_0 = 0`
and `q_42 = (7, 7, 7, 7, 7, 7)`. A pair `(s, t)` with `0 ≤ s ≤ t ≤ 41`
realizes a weight-3 mask when every coordinate of `q_s + q_t` lies in
`{0, 1, 7, 8, 14}` and exactly three lie in `{1, 8}`. The coordinate sum is
then `s + t = 3 + 7λ`. The two tight diagonals are `λ = 0` and `λ = 6`,
that is `s + t ∈ {3, 45}`. On `s + t = 3` the only possible slot is `(0, 3)`.
On `s + t = 45` the slots are `(s, 45 - s)` for `s = 4..22`, nineteen of
them. Together with `(0, 3)` that is twenty slots, one per mask.

The diagonal equality case, in which all nineteen middle slots are weight-3
realizations, is empty. That is the inherited result of fork PR 156 and
upstream PR #6941, from the centre fact in discussion comment 19384981: every
weight-3 centre freezes a coordinate at 14, and the allowed step
`S(s+1) = S(s) + e_{w_s} - e_{w_{44-s}}` cannot move a 14. This package
rechecks the centre count (300 realizations, all with a 14) and does not
repeat the induction down to `q_4`.

## Only the centre can be the one failed index

Write `S(s) = q_s + q_{45-s}`. The partner of `s = 4` is one final letter, so
a direct count shows that every weight-3 value of `S(4)` is a permutation of
`(8, 8, 8, 7, 7, 7)`. There are 120 such count states and no others. Inside
`{0, 1, 7, 8, 14}`, a coordinate changes by `+1` only from 0 or 7 and by `-1`
only from 1 or 8. In particular 14 never moves, and the only weight-3 vectors
of sum 45 with no 14 are the twenty permutations of `(8, 8, 8, 7, 7, 7)`.

Thus if `S(4)` is weight 3, every later weight-3 diagonal vector connected to
it by these steps stays free of 14. Two steps of size at most 1, starting
from `{7, 8}`, stay inside `{5, ..., 10}`.

- If the failed index is `s* = 4`, then `S(5), ..., S(22)` are weight 3. The
  centre therefore has a 14, and that 14 is still present at `S(5)`. But
  `q_5` sums to 5, so it has no coordinate 7 and `S(5)` has no 14.
- If `5 ≤ s* ≤ 21`, then `S(4)` is the free type above and `S(s* - 1)` is
  still free of 14. The next weight-3 vector `S(s* + 1)` is at most two
  steps away, so it also has no 14. The centre is weight 3, so its frozen 14
  would already be present at `S(s* + 1)`.

The only remaining possibility is that `s* = 22` and `S(4), ..., S(21)` are
all of free type. At `s = 21` every source has suffix count 3. The three
non-mask sources occupy positions 21, 22 and 23 once each, and no in-type
step remains. Every such chain fails at the centre, and the first 24 letters
contain each source four times.

## Where an off-diagonal pair can sit

There are 108 pairs with `s + t` equal to one of
`10, 17, 24, 31, 38, 52, 59, 66, 73, 80` and `0 ≤ s ≤ t ≤ 41`. The count
bounds on a one-failure chain kill 82 of them: a coordinate is too small to
be 0 or 1, or too large to be 14, and the only remaining allowed values are
`{7, 8}`, whose three-and-three sum is 45 rather than the off-diagonal sum.
The same bound leaves `(33, 33)` and the 25 pairs whose both indices lie in
`4..21`.

On those 25 pairs the free-type chain is an exact layered graph, including
stays. The jointly realized weight-3 sums are only these:

| pair | realizations | mask of the sum |
|---|---:|---|
| `(12, 12)` | 20 | the diagonal mask already at `s = 12` |
| `(11, 13)` | 180 | new, while both diagonal masks are equal |
| `(10, 14)` | 180 | new, while both diagonal masks are equal |
| `(9, 15)` | 20 | the complement of the common diagonal mask |

An equal pair of diagonal indices is a repeated mask among the 18 indices
`4..21`, so that image has size at most 17. The repeated read `(12, 12)`
does not add a mask.

The remaining slot `(33, 33)` is a block: positions `33..41` are three copies
of one triple and positions `24..32` are three copies of the complement.
Every free-type chain with that suffix repeats a mask on `s = 4..12`, so
those nine indices contribute at most 8 masks and the diagonal image has
size at most 17. The checker finds that 8 is tight and that such chains
exist; the block is not being ruled out, only prevented from finishing the
count by itself.

## The cover

The eighteen indices `4..21` realize at most 18 masks. The early pair `(0, 3)`
adds at most one. One off-diagonal pair adds a mask outside that image only
in the equal-endpoint cases or at `(33, 33)`, and in every one of those cases
the image already has size at most 17. Therefore

`17 + 1 + 1 = 19`

and, when the off-diagonal mask is already on the diagonal,

`18 + 1 = 19`.

At most 19 of the 20 weight-3 masks are realized. The word

```text
023514103524310254054123145203452034213150
```

attains 19: its diagonal image has 18 masks, `(0, 3)` supplies `(0, 2, 3)`,
no off-diagonal pair is weight 3, and `(1, 3, 5)` is missing. A one-letter
mutation of this word is rejected. The ceiling is sharp, and it is not 18.

## What remains open

A word whose diagonal image has size 18 has no off-diagonal weight-3 mask
outside that image, so further off-diagonal pairs do not help on that word.
A word that does realize a new off-diagonal mask has diagonal image at most
17. Two such masks, together with `(0, 3)`, could in principle reach 20.
This package does not decide that larger exchange, and it does not search
masks of any weight other than 3. Characteristic 7 therefore remains the
smallest open characteristic for a six-source depth-two block. No supplier,
consumer, or selected frontier changes. The selected conditional κ remains
`781451/250000000` in `certificates/selected-result.json`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c7-one-index-exchange/verify.py
python3.12 -I -O -W error -B research/six-source-c7-one-index-exchange/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c7-one-index-exchange --check-only
```

The marker is `PASS_SIX_SOURCE_C7_ONE_INDEX_EXCHANGE only_failure=22 centres_with_14=300/300 free_vectors=20 slots_blocked=82 graph_slots=25 block_slots=1 graph_internal=20 graph_novel=380 block33_max_distinct=8 cover_at_most=19 witness_cover=19 missing=(1,3,5) census=12/12:20,11/13:180,10/14:180,9/15:20 controls=6`.

The six controls are the inherited centre count, the move table that keeps 14
fixed, the two-step and short-prefix bounds that stop a 14 from appearing
before the centre, the absence of an in-type step at `s = 21`, the witness
chain matching those steps, and the rejected one-letter mutation. No SAT
solver, Lean, or Docker replay is used.

## Open next questions

1. Can two off-diagonal weight-3 pairs finish the count when the diagonal
   image has size at most 17? *Why:* one new pair plus `(0, 3)` stops at 19,
   while two new pairs have room to reach 20. On an image of size 18 there
   is nothing for them to add. *First step:* keep the centre as the only
   failed index and ask whether the `(9, 15)` complement and one other new
   pair from `(10, 14)`, `(11, 13)`, or `(33, 33)` can be new at the same
   time and disjoint from `(0, 3)`. *Blocked by:* those pairs constrain the
   same suffix, and this package does not enumerate their joint realizations.
2. Which non-weight-3 masks does the witness above miss? *Why:* a depth-two
   block needs every nonzero mask, so a completed weight-3 count would still
   not be a block. *First step:* evaluate `q_s + q_t` on this one word for
   weights other than 3 and list the missing masks. *Blocked by:* the state
   graph here tracks only weight-3 diagonal sums; it is not an unrestricted
   search, and the `c = 5` / `c = 6` human-proof question is a different
   remainder.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR #4231, PR #4248, PR #6107), with the Ross Richardson PR #934 / PR #943
lineage. JosieElliston's PR #6141 leaves `c = 7` open. Nick Petalas's handoff
on 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
isolates the tight diagonal and asks for an exchange. The empty equality case
is upstream PR #6941 / fork PR 156, discussion comment 19493159; its centre
fact is rechecked here and its induction is not repeated. zxv's PR #6057 and
JosieElliston's PR #6061 supply the `c ≥ 8` words. queelius's open PR #6216
is a `c = 5` certificate only.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
