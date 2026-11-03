# Two moved corrections do not emit in short G20 conjugations

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
the model of PR #6337 and PR #6633.

**Domain.** Every interval with exactly 2, 3 or 4 contacts; every pair
`i < j` of its contacts; every frame `f_i` of the route table other than
contact `i`'s frame, and every `f_j` other than contact `j`'s frame. The
other contacts stay on their contact frames.

| Contacts | Intervals | Pairs | Assignments |
|---:|---:|---:|---:|
| 2 | 331 | 331 | 133,467,475 |
| 3 | 250 | 750 | 302,418,750 |
| 4 | 119 | 714 | 287,902,650 |
| total | 700 | 1,795 | 723,788,875 |

Each pair contributes `635 × 635` assignments, since the table has 636
frames.

## Scalar endpoint

For a contact `C` with correction `R` and outer gate `G`, `G C G = C R`,
and `R` commutes with `C`. Noncontacts commute with `G`, and `G^2 = I`, so
the rewrite preserves the scalar map. A frame is not an operand, so moving
frames leaves that map unchanged. The verifier checks the endpoint on the
published word and on all 700 contact-frame skeletons. The expected final
row is `e_i` on public roles, plus `e_(i-111)` for `111 ≤ i < 222`, and zero
on owned roles.

## Emitter

`PATHS.json` has 2,369 one-edge routes of integer rank 1 through 7 on 636
frames. A live ADD (nonzero source row) routes its destination and then
its source to the record's frame. A missing edge rejects the word, also when
the moved row is zero. A dead ADD is skipped. At the end each public role
returns to its final frame and each owned role must be zero. The paid
moment at exponent `t` is `Σ_r n_r r^t`; the published word pays
`{1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}`.

## Why the prefix classes are exhaustive

The emitter is a left-to-right machine that stops at the first missing
route. Write the rewritten word as

`P · (C_i R_i at f_i) · M · (C_j R_j at f_j) · T`,

where `P` is the prefix before contact `i`, `M` the records between
correction `i` and contact `j` (other contacts on their contact frames), and
`T` the rest. `P` is the same for every `f_i, f_j`; `P` and `M` depend only on
`f_i`. The machine state after a prefix is a function of that prefix. So
every assignment falls into exactly one of these classes, tested in order:

| Class | Rejection point | Assignments |
|---|---|---:|
| `prefix_fail` | inside `P` | 80,241,775 |
| `first_meet` | inside `C_i R_i` at `f_i` | 607,824,540 |
| `middle_fail` | inside `M` | 35,467,290 |
| `second_meet` | inside `C_j R_j` at `f_j` | 255,171 |
| `tail_missing` | inside `T` or the final return | 99 |
| emitted | none | 0 |

Each class except "emitted" is a rejection of the full word, because the
machine reaches it before reading any later record. The verifier computes
the states after `P` once per interval, after `C_i R_i M` once per
`(i, f_i)`, and replays `T` in full for each of the 99 words that pass both
meetings. The six classes partition all 723,788,875 assignments; the
verifier asserts the sum.

No assignment emits, so no paid histogram changes and no rewritten word
lowers `Σ n_r r^t` on `(0, 1)`.

## Controls

- **From-scratch replays.** For each rejection class the first 25 recorded
  assignments are rebuilt as complete words and emitted from the start; all
  125 reject with `missing_edge`.
- **One-move census of PR #6337.** The same machine, run on the one-move
  domain at 1..3 contacts with that package's unchecked snapshot, finds
  28,149 frames that host the meeting and 26 emitted words, with shapes
  `H4` (2 words) and `5 H2 − 2 H4` (24 words). These are PR #6337's published
  totals. This shows that the emitter detects emissions in this model.
- **Sign classifier.** `2 H1 − H2` and both one-move shapes are strict
  losses by subadditivity; `H1 − 2 H2 + H3` is not called a loss.

## What this does not say

This census moves exactly two corrections. It does not move three or more,
does not move a frame at five or more contacts, and does not add a route. A
missing edge is a rejection on this table, not a proof that another native
path is impossible. Ordinary admission, the 18-call caller, adjoint columns,
moduli 101 and 10201, and the selected frontier are untouched. The selected
conditional exponent remains `781451/250000000`.
