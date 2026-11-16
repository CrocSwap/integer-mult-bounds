# One added route does not save a dirty one-move failure

## Object

The word, the one-edge route table, and the length-at-least-5 one-move domain
are those of
`research/g20-length5plus-one-move`. That package moves exactly one A2
correction onto a different frame of the published table. It classifies
686,779 of the 10,074,275 assignments as **dirty failures**: the contact pair
routes, and the first missing edge is the next route of a wire whose frame
disagrees with the contact-frame skeleton.

This proof keeps that moved correction and the rest of the published table.
It adds one edge, the first missing pair `(origin, target)`, with an integer
rank in `{1, ..., 7}`. Every published route already has a rank in that range.
No second correction moves, and no second edge is added. The selected
conditional exponent stays `781451/250000000`.

A completed route walk has paid histogram `P`. Write `B` for the published
histogram `{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}`. The difference is
a **strict saving** on `(0, 1)` when `Σ_r (P_r − B_r) r^t < 0` for every
`t ∈ (0, 1)`. A word that still misses an edge has no paid histogram and is
not a saving. For `0 < t < 1` and integers `a, b ≥ 1`,

`(a + b)^t < a^t + b^t`,

and `x ↦ x^t` is strictly increasing on the positive reals. In particular
`r^t > 1^t = 1` for every integer `r > 1`.

## The domain is the #6923 dirty class

The verifier imports the pinned #6923 classifier and counts the assignments
it labels `dirty_fail`. The count is again 686,779. The length histogram of
those assignments is the `LENGTHS` table in `verify.py`, and it sums to
686,779. The first missing lookup recorded by that classifier is compared
with the first missing edge of an independent route walk of the same moved
word. All 686,779 pairs agree.

Those pairs form 22,709 ordered frame pairs. Sorted lines
`origin target count` have SHA-256

```text
8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494
```

The largest multiplicity is 1,841. Exactly 303 pairs attain it. Each runs
from a frame in `326..635`, excluding 507 and 519–524, into frame 1. Those
303 pairs account for `303 × 1,841 = 557,823` failures. Every one of the
686,779 first hops is a paying hop: the moved wire's row is nonzero, so any
completed walk charges the new edge at least once.

## Route walk

`paid_histogram` in the #6923 verifier is the published route rule. A live
`ADD` routes its destination and then its source from the wire's current frame
to the event frame. A missing edge rejects the word. A dead `ADD` is omitted.
At the end every public role returns to its final frame, and a nonzero owned
role rejects the word. Paying hops increment the histogram of their edge rank.

The census walk is that rule, with two stated changes.

- It resumes at the contact. The #6923 snapshot stores the rows and frames
  immediately before that contact. The prefix is identical to the
  contact-frame skeleton, and a dirty failure has already passed the prefix,
  so the first missing edge lies at or after the contact.
- The first missing pair is inserted and kept. A later hop that needs the
  same pair uses the inserted edge. A different missing pair still rejects
  the word.

The two patched events are the contact and its correction. Both remain `ADD`s,
and only their frame fields change, so the scalar endpoint is the endpoint
already checked for the one-move skeleton. Every emission is checked again
with `endpoint_ok`.

## Census

| Class | Assignments | Outcome |
|---|---:|---|
| A different edge is still missing | 686,386 | no histogram |
| The walk emits | 393 | strict loss at ranks 1..7 |
| Total | 686,779 | no saving |

The suffix walk is the enumerator for both classes. Every emission is also
rebuilt from the start of the word and replayed by `paid_histogram` at each
rank `1..7`. One still-rejected word in each of the 28 lengths represented
here is replayed the same way and still misses an edge. The eight #6923
emissions and the two repair assignments are replayed as controls and stay
outside this dirty class.

## The 393 emissions are strict losses

On an emission the inserted edge is used for `u ∈ {1, 2, 3}` paying hops.
Let `Q` be the histogram of every paying hop that is not that edge, and let
`P^(r)` be the histogram when the inserted edge has rank `r`. Then

`P^(r) = Q + u e_r`.

The independent replay checks this identity at every rank: the #6923
histogram with the edge present at rank `r` equals `Q` plus `u` jobs of rank
`r`. Comparing two such replays gives

`P^(r) − P^(1) = u (e_r − e_1)`

for each `r ∈ {2, ..., 7}`. Therefore, on `(0, 1)`,

`Σ (P^(r)_s − B_s) s^t = Σ (P^(1)_s − B_s) s^t + u (r^t − 1)`.

The second term is positive. A strict loss at rank 1 remains a strict loss
at every higher rank in `1..7`.

The rank-1 differences fall into the 52 shapes in `SHAPES`. Three of them are
settled by the monotonicity above, and the other 49 by the splitting
argument. The splitting search is the #6923 search: while a negative job of
rank `R` remains, find at least two positive jobs whose ranks sum to `R`,
replace them, and repeat. Each replacement strictly raises the moment. The
search stops with a positive remainder, so the original shape is a strict
loss. The search refuses a shape with more than twelve positive atoms, and
every split shape in this census passes it.

| Rank-1 shape | Assignments | Certificate |
|---|---:|---|
| `2 H2 − 2 H1` | 8 | `2(2^t − 1) > 0` |
| `5 H2 − H1` | 2 | `5·2^t − 1 > 4` |
| `H1 + H4 − H3` | 1 | `4^t > 3^t` |
| 49 other shapes | 382 | explicit split with a positive remainder |

`2 H2 − 2 H1 = 2(2^t − 1)` and `2^t > 1`. `5·2^t − 1 > 5 − 1 = 4`.
`H1 + H4 − H3 = 1 + 4^t − 3^t > 0` because `4^t > 3^t`. These are the 11
elementary assignments. The verifier rejects any shape that has neither an
elementary certificate nor a split.

## One explicit emission

The lexicographically first emission, in scalar-position order, is the
interval `5,760–6,924`. The outer gate is `ADD(89, 19)` and the interval has
13 corrections. Correction 6 is the contact `ADD(161, 89)` on frame 575,
with correction `ADD(161, 19)`. Moving that correction to frame 429 misses
the edge `(429, 575)`. Adding it produces one paying use. The other-edge
difference is `−H1 + 3 H2 − H4`, so the rank-1 difference is `3 H2 − H4`.
The split `H4 = H2 + H2` leaves `H2`, a strict loss. Ranks 2 through 7 add
the positive term `r^t − 1`.

## What this does not say

The screen adds one edge to one moved word. It does not add the second
missing edge of any of the 686,386 words that still fail, and it does not
move a second correction. A rejection on this enlarged table is not a proof
that another routing model is impossible. Ordinary admission, the 18-call
caller, adjoint columns, moduli 101 and 10201, and the selected frontier are
untouched.
