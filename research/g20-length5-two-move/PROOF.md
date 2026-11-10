# Two moved corrections do not emit on length-5 G20 intervals

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

The constructor of `construct.py` deletes the two outer gates and writes
each contact immediately followed by its correction, both on one chosen
frame. The contact-frame word uses the contact's published frame. This is
the model of PR #6664.

## Domain

The census takes every interval with exactly five contacts. There are 133
such intervals. The same scan finds 331, 250 and 119 intervals at 2, 3 and 4
contacts, which are PR #6664's published totals, and 1,384 intervals of
length at least 5, which is PR #6923's published total. Length 5 is 133 of
those 1,384. The other 1,251 intervals have length at least 6 and are outside
this census. The scan also records 86 intervals of length exactly 6; they are
counted and not searched.

For each length-5 interval the census takes every pair `i < j` of its five
corrections, every frame `f_i` of the route table other than contact `i`'s
frame, and every frame `f_j` other than contact `j`'s frame. The other three
corrections stay on their contact frames. The two new frames may be equal.
The table has 636 frames, so each pair contributes `635 × 635` assignments.

| Contacts | Intervals | Pairs | Assignments |
|---:|---:|---:|---:|
| 5 | 133 | 1,330 | 536,289,250 |

`133 × 10 × 635 × 635 = 536,289,250`. The domain is finite, and the verifier
checks that the rejection classes below add up to this product.

The least interval in scalar-position order is the declared first case. Its
outer gates are the scalar records at indexes 1,119 and 8,918, both
`ADD(572, 22)`, on frames 1 and 24. It has the same 10 pairs and 4,032,250
assignments as every other length-5 interval. Its classes are reported
separately below, and they are included in the totals.

## Scalar endpoint

For a contact `C` with correction `R` and outer gate `G`, `G C G = C R`, and
`R` commutes with `C`. Noncontacts commute with `G`, and `G^2 = I`, so the
rewrite preserves the scalar map. A frame is not an operand, so moving frames
leaves that map unchanged. The verifier checks the endpoint on the published
word, on all 133 contact-frame skeletons, and on one two-move skeleton of
each interval (corrections 0 and 1 moved to the least other catalogue frame).
The expected final row is `e_i` on public roles, plus `e_(i-111)` for
`111 ≤ i < 222`, and zero on owned roles.

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

## Why the classes are exhaustive

The emitter is a left-to-right machine that stops at the first missing route.
Write the rewritten word as

`P · (C_i R_i at f_i) · M · (C_j R_j at f_j) · T`,

where `P` is the prefix before contact `i`, `M` the records between
correction `i` and contact `j` (other contacts on their contact frames), and
`T` the rest. `P` is the same for every `f_i, f_j`. `P` and `M` depend on
`f_i` and not on `f_j`. The machine state after a prefix is a function of
that prefix. Every assignment therefore falls into exactly one of these
classes, tested in order:

| Class | Rejection point | Assignments |
|---|---|---:|
| `prefix_fail` | inside `P` | 86,290,150 |
| `first_meet` | inside `C_i R_i` at `f_i` | 332,300,580 |
| `middle_fail` | inside `M` | 116,497,735 |
| `second_meet` | inside `C_j R_j` at `f_j` | 1,196,454 |
| `tail_missing` | inside `T` or the final return | 4,331 |
| emitted | none | 0 |

Each class except "emitted" is a rejection of the full word, because the
machine reaches it before reading any later record. The verifier computes the
state after `P` once per contact, resumes from there for each `f_i`, and
replays `T` for each of the 4,331 words that pass both meetings. It asserts
that the six classes partition all 536,289,250 assignments. Every tail
rejection observed during that replay is `missing_edge`.

No assignment emits, so no paid histogram changes and no rewritten word
lowers `Σ n_r r^t` on `(0, 1)`.

## The first length-5 interval

On interval `1,119..8,918` the same partition is

| Class | Assignments |
|---|---:|
| `prefix_fail` | 2,419,350 |
| `first_meet` | 1,612,900 |
| later classes | 0 |
| total | 4,032,250 |

Six of its ten correction pairs miss a route before the first moved contact.
The other four pairs reach that contact, and every alternate frame misses a
route inside the moved meeting. The second correction is never tried. This
is the one-interval census named as the first step. The table above is the
same machine run on the other 132 length-5 intervals as well.

## Controls

- **Cold tail replays.** Each of the 4,331 words that reach `T` is rebuilt
  from the published scalar program and emitted from the start. Each misses
  an edge.
- **Cold prefix samples.** The first 25 recorded assignments in each of
  `prefix_fail`, `first_meet`, `middle_fail` and `second_meet` are rebuilt
  and emitted from the start. All 100 miss an edge.
- **Enumerator lock.** Lengths 2, 3 and 4 reproduce PR #6664's 331, 250 and
  119 intervals. Length at least 5 reproduces PR #6923's 1,384 intervals.
- **Positive emission control.** One published length-5 one-move assignment
  from PR #6923 is replayed on this emitter and is not part of the two-move
  count: scalar positions `7,337..10,919`, correction 2, contact
  `ADD(340, 670)` on frame 506, moved frame 123. It emits with histogram
  difference `3 H2 − H4`, which is a strict loss on `(0, 1)` by the splitting
  `H4 = H2 + H2`. The two-move census itself has no emission to which that
  test applies.
- **Sign-classifier fixture.** `2 H1 − H2` is a strict loss. `H1 − 2 H2 + H3`
  is left unsigned. The classifier is not used to sign a two-move histogram,
  because no two-move word emits.

## What remains outside this census

The census moves exactly two corrections, on intervals of exactly five
contacts, on the published one-edge route table. A missing edge is a
rejection on this table. Intervals of length at least 6, three or more moved
corrections, and any added route are separate finite questions. They are
stated in the package README. Ordinary admission, the 18-call caller,
adjoint columns, moduli 101 and 10201, and the selected frontier are
untouched. The selected conditional exponent remains `781451/250000000`.
