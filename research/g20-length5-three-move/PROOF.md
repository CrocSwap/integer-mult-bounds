# Three or more moved corrections do not emit on length-5 G20 intervals

## Object

The word is the emitted local scalar program in
`research/g20-conjugation-admission/WORD.json.gz`, the output of PR #5708.
Drop `Q` and `ZERO_Q`. What remains is 11,930 scalar records on 685 roles.
`ADD(a, b)` is the characteristic-2 update `x_a <- x_a + x_b`.

An A2 interval runs from one `ADD(a, b)` to a later equal `ADD(a, b)`. Its
open interior has no `ERASE` or `INIT` of `a` or `b`, and each of its
noncommuting `ADD` records (its contacts) has an A2 correction:

- `ADD(b, s)` with `s ≠ a` contributes `ADD(a, s)`;
- `ADD(d, a)` with `d ≠ b` contributes `ADD(d, b)`.

The constructor deletes the two outer gates and writes each contact
immediately followed by its correction, both on one chosen frame. The
contact-frame word uses the contact's published frame. This is the model of
PR #6664 and PR #6963.

## Domain

The census takes every interval with exactly five contacts. There are 133
such intervals. The same scan finds 331, 250 and 119 intervals at 2, 3 and 4
contacts, which are PR #6664's published totals, and 1,384 intervals of
length at least 5, which is PR #6923's published total. Length exactly 6
contributes 86 intervals. Those lengths are counted and not searched.

For each length-5 interval, move any set of three, four or five corrections
onto frames of the published route table other than those corrections'
contact frames. Every correction outside the set stays on its contact frame.
The chosen frames may be equal. The table has 636 frames, so each moved
correction has 635 legal frames.

| Moved corrections | Choices of index set | Assignments on one interval | Assignments |
|---:|---:|---:|---:|
| 3 | 10 | 2,560,478,750 | 340,543,673,750 |
| 4 | 5 | 812,952,003,125 | 108,122,616,415,625 |
| 5 | 1 | 103,244,904,396,875 | 13,731,572,354,784,375 |
| 3, 4 or 5 | 16 | 104,060,416,878,750 | 13,840,035,444,873,750 |

`133 × (10 × 635³ + 5 × 635⁴ + 635⁵) = 13,840,035,444,873,750`. The domain is
finite. The verifier recomputes it by enumerating the 16 masks and, separately,
by grouping those masks under their two earliest indexes. The two counts agree.

The least interval in scalar-position order is the declared first case. Its
outer gates are the scalar records at indexes 1,119 and 8,918, both
`ADD(572, 22)`, on frames 1 and 24. It has the same 104,060,416,878,750
three-or-more assignments as every other length-5 interval. None of its
two-move pairs reaches the tail, so every one of those assignments is an
early rejection in the case split below.

## Scalar endpoint

For a contact `C` with correction `R` and outer gate `G`, `G C G = C R`, and
`R` commutes with `C`. Noncontacts commute with `G`, and `G² = I`, so the
rewrite preserves the scalar map. A frame is not an operand, so moving frames
leaves that map unchanged. The verifier checks the endpoint on the published
word, on all 133 contact-frame skeletons, and on one two-move skeleton and
one three-move skeleton of each interval (the least other catalogue frame on
corrections 0 and 1, and on corrections 0, 1 and 2). The expected final row
is `e_i` on public roles, plus `e_(i-111)` for `111 ≤ i < 222`, and zero on
owned roles.

## Emitter

`PATHS.json` has 2,369 one-edge routes of integer rank 1 through 7 on 636
frames. A live ADD (nonzero source row) routes its destination and then its
source to the record's frame. A missing edge rejects the word. A dead ADD is
skipped. At the end each public role returns to its final frame and each
owned role must be zero. The paid moment at exponent `t` is `Σ_r n_r r^t`.
The published word pays

```text
{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}.
```

A word that misses a route has no paid histogram. It does not lower the
moment on `(0, 1)`.

## Case split

Number the five corrections `0, 1, 2, 3, 4` in word order. Every moved set
`M` with `|M| ≥ 3` has a unique pair of earliest indexes `i < j`. Every other
index in `M` is strictly greater than `j`, and every index strictly between
`i` and `j` stays on its contact frame. The later indexes therefore form a
nonempty subset of `{j+1, ..., 4}`.

Each of those later corrections is either left on its contact frame or sent
to one of the other 635 frames, except that the assignment which leaves all
of them on their contact frames is the two-move word and is outside this
domain. That is `636^(4-j) − 1` extensions of each two-move frame pair:

| Second earliest index `j` | Later slots | Extensions of one frame pair |
|---:|---:|---:|
| 1 | 3 | 257,259,455 |
| 2 | 2 | 404,495 |
| 3 | 1 | 635 |
| 4 | 0 | 0 |

There is no three-or-more set whose second earliest index is 4, because at
most one correction can precede it. Summing `635² × (636^(4-j) − 1)` over the
ten pairs `(i, j)` recovers the mask count above. The verifier checks that
identity before it reads the word.

Write a two-move word, with corrections `i` and `j` moved and every other
correction on its contact frame, as

`P · (C_i R_i at f_i) · M · (C_j R_j at f_j) · T`.

`T` contains every correction of index greater than `j`. Any three-or-more
word with the same earliest pair and the same frames `f_i, f_j` differs from
this word only at correction records of index greater than `j`. The emitter
is a left-to-right machine and stops at the first missing route. If the
two-move word is rejected at a record strictly before the first of those
later corrections, every extension is rejected at that same record, for the
same reason, because the two words agree through it.

## The two-move partition, recomputed

The verifier repeats the length-5 two-move census of PR #6963. Every
rejection it executes is `missing_edge`; any other reason raises. The classes
are the same partition of the 536,289,250 two-move assignments:

| Two-move class | Rejection point | Assignments |
|---|---|---:|
| `prefix_fail` | inside `P` | 86,290,150 |
| `first_meet` | inside `C_i R_i` at `f_i` | 332,300,580 |
| `middle_fail` | inside `M` | 116,497,735 |
| `second_meet` | inside `C_j R_j` at `f_j` | 1,196,454 |
| `tail_missing` | inside `T` or the final return | 4,331 |
| emitted | none | 0 |

The first four classes reject before `T`, hence before every later
correction. Each of their frame pairs therefore rejects all
`636^(4-j) − 1` extensions at the same missing edge.

## The 4,331 tails

The remaining two-move assignments are the 4,331 words that pass both moved
meetings and then miss an edge. Their second-earliest indexes are

| `j` | Tail words | Extensions each | Extensions |
|---:|---:|---:|---:|
| 1 | 4,305 | 257,259,455 | 1,107,501,953,775 |
| 2 | 7 | 404,495 | 2,831,465 |
| 3 | 19 | 635 | 12,065 |
| 4 | 0 | 0 | 0 |

On every one of these 4,331 words the missing edge lies strictly after the
second moved correction and strictly before the next correction. The distance
from the rejecting record to the next correction's contact is an integer in
`2, ..., 329`. The next correction is therefore unread. Moving any nonempty
set of later corrections, to any frames, leaves the rejecting record and the
machine state at that record unchanged.

The early and tail extensions are disjoint and cover every three-or-more
assignment:

| Class | Assignments | Outcome |
|---|---:|---|
| Earliest pair rejected before the tail | 13,838,927,940,076,445 | `missing_edge` at that record |
| Earliest pair among the 4,331 tails | 1,107,504,797,305 | `missing_edge` before the next correction |
| Emitted | 0 | — |
| Total | 13,840,035,444,873,750 | no paid histogram |

No assignment emits, so no paid histogram changes and no rewritten word
lowers `Σ n_r r^t` on `(0, 1)`.

## One tail, as a record

The first tail in scalar-position order has outer gates at scalar indexes
5,673 and 7,030, both `ADD(46, 56)`, on frames 1 and 506. Its earliest moved
corrections are indexes 1 and 2:

- correction 1, contact `ADD(56, 312)`, moves from frame 1 to frame 594,
  with correction `ADD(46, 312)`;
- correction 2, contact `ADD(173, 46)`, moves from frame 587 to frame 353,
  with correction `ADD(173, 56)`.

The rewritten word misses a route on the next record, `ADD(173, 312)` at its
published frame 587, at rewritten index 6,306. Correction 3 begins at
rewritten index 6,547. The verifier locks this tuple
`(5673, 7030, 1, 2, 594, 353, 6306, 6547)`.

## Controls

- **Cold two-move tails.** Each of the 4,331 tail words is rebuilt from the
  published scalar program and emitted from the start. Each misses an edge at
  the index recorded by the resumed census.
- **Cold one-further move.** For each of those words the next correction is
  also moved, to the least other catalogue frame, and the word is emitted
  from the start. It misses an edge at the same index.
- **Cold maximal move.** For one tail of each index `j ∈ {1, 2, 3}`, every
  later correction is moved to its least other catalogue frame. That word
  misses an edge at the same index. For `j = 1` this is a five-move word.
- **Cold early extensions.** The first 25 two-move samples in each early
  class that still have a later correction are extended by one move of that
  correction and emitted from the start. All 100 miss an edge at the same
  index as their two-move word. These samples are controls on the
  implementation. The case split above covers the assignments that are not
  replayed.
- **Enumerator lock.** Lengths 2, 3 and 4 reproduce PR #6664's 331, 250 and
  119 intervals. Length at least 5 reproduces PR #6923's 1,384 intervals.
  The two-move class counts reproduce PR #6963.
- **Positive emission control.** One published length-5 one-move assignment
  from PR #6923 is replayed on this emitter and is outside the three-or-more
  count: scalar positions `7,337..10,919`, correction 2, contact
  `ADD(340, 670)` on frame 506, moved frame 123. It emits with histogram
  difference `3 H2 − H4`, a strict loss on `(0, 1)` by the splitting
  `H4 = H2 + H2`. The three-or-more census itself has no emission.
- **Sign-classifier fixture.** `2 H1 − H2` is a strict loss.
  `H1 − 2 H2 + H3` is left unsigned. The classifier is not used to sign a
  three-or-more histogram, because no such word emits.

## Outside this census

The hypotheses are one word, one published one-edge route table, and A2
intervals of exactly five contacts, with three, four or five corrections
moved in the #6664 constructor. Under those hypotheses the census is
complete: the domain is finite, every assignment belongs to exactly one class
above, and the class sizes sum to the mask count.

A missing edge is a rejection on this route table. The result does not by
itself prove that some other route, some other word, or an interval of
another length emits and lowers the moment. Intervals of length 2, 3 or 4
with three or more moved corrections are the open question in
`research/g20-two-moved-corrections`. Two moved corrections at length at
least 6 are open question 1 of PR #6963. Three or more moved corrections at
length at least 6 are the open question of this package. One added route at
a missing edge stays with PR #6923's second question. Ordinary admission,
the 18-call caller, adjoint columns, moduli 101 and 10201, and the selected
frontier are untouched. The selected conditional exponent remains
`781451/250000000`.
