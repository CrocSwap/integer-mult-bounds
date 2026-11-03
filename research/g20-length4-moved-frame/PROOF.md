# Length-4 G20 conjugations do not emit after one moved correction

## Object

The word is the emitted local scalar program in
`research/g20-conjugation-admission/WORD.json.gz`, the output of PR #5708.
Drop `Q` and `ZERO_Q`. What remains is 11,930 scalar records on 685 roles.
`ADD(a, b)` is the characteristic-2 update `x_a <- x_a + x_b`.

An interval from one `ADD(a, b)` to a later equal `ADD(a, b)` is an **A2
conjugation of length 4** when the open interval contains no `ERASE` or
`INIT` of `a` or `b`, contains exactly four noncommuting `ADD` records, and
each of those records has an A2 correction:

- `ADD(b, s)` with `s ≠ a` contributes `ADD(a, s)`;
- `ADD(d, a)` with `d ≠ b` contributes `ADD(d, b)`.

`ADD(b, a)` has no correction of this form. The constructor deletes the two
outer gates and writes each contact immediately followed by its correction.
On the contact-frame word every correction keeps the contact's published
frame. This proof moves **exactly one** of the four corrections onto a
different frame of the published one-edge route table and leaves the other
three on their contact frames.

There are 119 such intervals. PR #6305 already classifies every length of
four or more while every correction stays on its contact frame. PR #6337
moves one correction only for lengths one through three. Neither statement
covers a length-4 word with one moved frame.

## Scalar endpoint

For a contact `C` with correction `R`, the elementary identity is
`G C G = C R`, and `R` commutes with `C`. Every noncontact commutes with the
outer gate `G`, and `G^2 = I`, so deleting the two outer gates and replacing
each contact by `C R` preserves the scalar map at every contact count. A
frame is not an operand, so the same skeleton with one correction frame
changed has the same scalar map.

The verifier checks that map on the published word, on all 119 contact-frame
skeletons, and on every moved skeleton that passes the local meeting test.
Each row is a 685-bit mask, initially `e_i`. ADD is exact XOR. Only an owned
role may be erased, and INIT requires that role's row to be zero. The
expected final row is zero on owned roles. On every other role it is `e_i`,
with the extra term `e_(i-111)` for `111 ≤ i < 222`.

## Routes

`PATHS.json` has 2,369 routes and 636 frames. Every route is one edge of
integer rank 1 through 7. A live ADD, meaning its source row is nonzero,
routes its destination and then its source to its frame before the sum. A
missing edge rejects the word, including when the moved row is zero. A dead
ADD is omitted and does not read its frame. At the end every public role
returns to its final frame, and every owned role must be zero. The paid
moment at exponent `t` is `Σ_r n_r r^t`. The published word pays

```text
{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}.
```

## Why the meeting filter is exhaustive

Fix one correction and a candidate frame `f` other than its contact frame.
The snapshot is the row masks and wire frames immediately before that
contact on the contact-frame skeleton. Earlier corrections stay on their
contact frames, so this snapshot is the pre-contact state of the one-move
word. The contact and its correction are the next two ADD records, both at
`f`.

Every wire that the contact or the correction must move is therefore a wire
that has to reach `f` from its snapshot frame. Those wires' reachable frames
are the snapshot frame itself and the heads of the published edges out of
that frame. Any `f` outside the intersection fails on this pair, so the full
word fails. The verifier compares that intersection with an independent
two-event replay on all 635 other catalogue frames. The two tests agree on
every one of the 476 corrections: 301,756 frames fail the meeting, and 504
lie in the intersection.

## Census

| Domain | Count | Outcome |
|---|---:|---|
| Length-4 intervals | 119 | 118 missing routes, 1 unchanged histogram |
| Other catalogue frames | 302,260 | 301,756 fail the meeting, 504 miss a later edge |
| Emitted moved frames | 0 | no paid-moment change is defined |

The one contact-frame emission is the length-4 neutral word already named by
PR #6305: zero-based scalar positions 9,399 and 10,815, gate `ADD(560, 315)`.
Its histogram equals the published histogram, so it is not a saving. Every
moved assignment fails to emit. None lowers `Σ n_r r^t` on `(0, 1)`.

As a control, the same enumerator and emitter recount every length of four
or more at the contact frame. The totals are 1,503 intervals, 1,450 missing
routes, 14 unchanged histograms and 39 strict losses, with the same seven
signed shapes published by PR #6305. That recount is a consistency check. It
is not a new proof of the fixed-frame theorem.

## Sign control for those seven shapes

Write `Hr` for a job of rank `r`. A shape with every coefficient positive is
positive for `0 < t < 1`. Otherwise each negative job of rank `R` is replaced
by at least two positive jobs whose ranks sum to `R`. For positive `a, b`
and `0 < t < 1`, `(a+b)^t < a^t + b^t`, because
`(a/(a+b))^t > a/(a+b)` and the same holds for `b`. Iteration leaves a
nonnegative remainder, so the shape is a strict loss on the whole interval.
The seven shapes are `2H1 − H2`, `3H1 + 2H2`, `2H2 − H4`, `2H1 + H2 + H3`,
`H1 + 3H2`, `H1 + 2H2 − H5` and `H1 + H3 − H4`. The same rule rejects
`H1 − 2H2 + H3`. No moved length-4 word produces a shape, because none emits.

## What this does not say

The screen does not move two corrections in one interval, does not move a
frame at length five or more, and does not add a route. A missing edge is a
rejection on this table, not a proof that another native path is impossible.
The six neutral one-step neighbors and the 645 common-frame expansions named
in the #5708 README still have no executable search record in that package.
Ordinary admission, the 18-call caller, adjoint columns, moduli 101 and
10201, and the selected frontier are untouched. The selected conditional
exponent remains `781451/250000000`.
