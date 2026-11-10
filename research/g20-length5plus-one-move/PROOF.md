# One moved correction at length 5 or more does not lower the G20 moment

## Object

The word is the emitted local scalar program in
`research/g20-conjugation-admission/WORD.json.gz`, the output of PR #5708.
Drop `Q` and `ZERO_Q`. What remains is 11,930 scalar records on 685 roles.
`ADD(a, b)` is the characteristic-2 update `x_a <- x_a + x_b`.

An interval from one `ADD(a, b)` to a later equal `ADD(a, b)` is an **A2
conjugation of length `L`** when the open interval contains no `ERASE` or
`INIT` of `a` or `b`, contains exactly `L` noncommuting `ADD` records, and
each of those records has an A2 correction:

- `ADD(b, s)` with `s ≠ a` contributes `ADD(a, s)`;
- `ADD(d, a)` with `d ≠ b` contributes `ADD(d, b)`.

`ADD(b, a)` has no correction of this form. The constructor deletes the two
outer gates and writes each contact immediately followed by its correction.
There are 1,384 such intervals with `L ≥ 5`, and 15,865 corrections in them.
This proof moves **exactly one** correction onto a different frame of the
published one-edge route table and leaves the others on their contact frames.

PR #6305 classifies every length of four or more while every correction stays
on its contact frame. PR #6337 moves one correction only for lengths one
through three. PR #6633 moves one correction at length four. PR #6664 moves
two corrections at lengths two through four. None of those statements covers
one moved frame at length five or more.

## Scalar endpoint

For a contact `C` with correction `R`, the elementary identity is
`G C G = C R`, and `R` commutes with `C`. Every noncontact commutes with the
outer gate `G`, and `G^2 = I`, so deleting the two outer gates and replacing
each contact by `C R` preserves the scalar map at every contact count. A
frame is not an operand. The same skeleton with one correction frame changed
has the same scalar map.

The verifier checks that map on the published word, on all 1,384 contact-frame
skeletons, and on every moved skeleton it replays. Each row is a 685-bit
mask, initially `e_i`. ADD is exact XOR. Only an owned role may be erased,
and INIT requires that role's row to be zero. The expected final row is zero
on owned roles. On every other role it is `e_i`, with the extra term
`e_(i-111)` for `111 ≤ i < 222`.

## Routes

`PATHS.json` has 2,369 routes and 636 frames. Every route is one edge of
integer rank 1 through 7. A live ADD, meaning its source row is nonzero,
routes its destination and then its source to its frame before the sum. A
missing edge rejects the word. A dead ADD is omitted and does not read its
frame. At the end every public role returns to its final frame, and every
owned role must be zero. The paid moment at exponent `t` is `Σ_r n_r r^t`.
The published word pays

```text
{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}.
```

## One-hop lemma

Fix one correction and write the contact and the correction on a frame `f`
other than the contact frame. The prefix before that contact is identical to
the contact-frame skeleton, so a missing edge in the prefix rejects every
choice of `f`. There are 6,114,415 such assignments.

If both events of the pair are live, the frames `f` that survive the pair are
the intersection of the one-edge reachable sets of the wires the pair must
move. Every other frame fails inside the pair: 3,272,780 assignments. The
verifier checks one rejected frame on every correction against an independent
replay of the two events, and checks that every surviving frame passes that
replay.

On the 949 corrections whose contact-frame pair already misses an edge, 112
alternate frames still pass the pair. The independent emitter replays all 112.
Every one misses a later edge.

Now suppose the contact-frame pair itself routes. After the pair, a wire is
**dirty** when its frame differs from the contact-frame skeleton. Row masks do
not depend on frames, and every later ADD target is unchanged. The next live
ADD, erasure, or final assignment that touches a dirty wire writes the same
target in both words, so the wire agrees with the contact-frame skeleton after
that one event. Dirtiness does not spread to a new wire.

Therefore the moved word fails unless three things happen:

- the pair routes at `f`;
- each dirty wire's one next route exists;
- every route that does not touch a still-dirty wire exists.

The contact-frame walk decides the third item up to its first missing edge.
If that edge belongs to a clean wire, the moved word fails there too: 179
assignments. If it belongs to a dirty wire's next route and the moved frame
has no edge, the moved word fails on that hop: 686,779 assignments. If the
moved frame passes the dirty hop that stopped the contact-frame walk, the
lemma does not finish the suffix. Two assignments are in that remainder. The
independent emitter replays both, and both miss a later edge.

If the contact-frame word routes all the way to the end and every dirty hop
exists, the moved word emits. The paid-histogram difference is local: the pair,
plus one hop for each dirty wire. Eight assignments emit. Their differences
from the published histogram are below.

## The eight emissions are strict losses

Write `Hr` for one paid job of rank `r`. For positive `a, b` and `0 < t < 1`,
`(a+b)^t < a^t + b^t`. Replacing a negative job of rank `R` by two or more
positive jobs whose ranks sum to `R`, and repeating, leaves a positive
remainder exactly when the shape is a strict loss on the whole interval.

| Scalar positions | Length | Moved frame | Shape | Split |
|---|---:|---:|---|---|
| 6,261–11,325, correction 7, gate `(523, 387)` | 13 | 77 | `5 H1 + H2` | already positive |
| 6,433–11,727, correction 7, gate `(551, 426)` | 14 | 96 | `5 H1 + H2` | already positive |
| 7,278–10,929, correction 6, gate `(385, 664)` | 9 | 91 | `H1 + 2 H3 − H4` | `H4 = H1 + H3`, remainder `H3` |
| 7,278–10,929, correction 6, gate `(385, 664)` | 9 | 155 | `3 H1 + 3 H2 − H3 − H4` | `H3 = H1 + H2`, `H4 = H2 + H2`, remainder `2 H1` |
| 7,278–10,929, correction 6, gate `(385, 664)` | 9 | 157 | `3 H1 + 3 H2 − H3 − H4` | same split |
| 7,318–10,917, correction 3, gate `(319, 672)` | 6 | 123 | `3 H2 − H4` | `H4 = H2 + H2`, remainder `H2` |
| 7,319–10,916, correction 3, gate `(233, 662)` | 6 | 123 | `3 H2 − H4` | same split |
| 7,337–10,919, correction 2, gate `(340, 670)` | 5 | 123 | `3 H2 − H4` | same split |

Positions are zero-based indexes in the scalar program, before the outer gates
are deleted. The independent emitter reproduces each shape, and each shape is
a strict loss on `(0, 1)`. None lowers `Σ n_r r^t`.

## Census

| Class | Assignments | Outcome |
|---|---:|---|
| Prefix already missing | 6,114,415 | missing edge |
| Pair rejects the new frame | 3,272,780 | missing edge |
| Dirty wire's next route missing | 686,779 | missing edge |
| Clean later route missing | 179 | missing edge |
| Contact-frame pair already missing, alternate frame replayed | 112 | missing edge |
| Lemma remainder, independently replayed | 2 | missing edge |
| Emitted | 8 | strict loss |
| Total | 10,074,275 | no saving |

`15,865 × 635 = 10,074,275`, one alternate catalogue frame for every correction.

As a control, the same fixed-frame enumerator recounts these 1,384 intervals
together with the 119 length-4 intervals. The totals are the published #6305
figures: 1,503 intervals, 1,450 missing routes, 14 unchanged histograms and 39
strict losses, with the same seven signed shapes. A separate control replays
every length-4 one-move assignment with the independent emitter and recovers
the #6633 totals: 302,260 assignments, 504 local survivors, all missing an
edge, and no emission. One prefix failure in each of the 28 lengths represented
here is also replayed and misses its edge.

## What this does not say

The screen does not move two corrections in one interval, does not add a
route, and does not change the word. A missing edge is a rejection on this
table, not a proof that another native path is impossible. The six neutral
one-step neighbors and the 645 common-frame expansions named in the #5708
README still have no executable search record in that package. Ordinary
admission, the 18-call caller, adjoint columns, moduli 101 and 10201, and the
selected frontier are untouched. The selected conditional exponent remains
`781451/250000000`.
