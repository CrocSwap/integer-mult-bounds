# The new G20 input does not free a same-frame paid query

## Statement

Let `W` be the emitted word in `research/g20-helper-split/WORD.json.gz`.
Field `684` is the independent input added by the rank-4/rank-4 split:
it is born at frame `508` and ends at frame `0`. Execution is the forward
`F2` replay of that package. `ADD d, s, f` replaces the row of `d` by the
sum of the rows of `d` and `s`, and both fields are at frame `f`. A paid
`Q` moves a nonzero row to a new frame. `ZERO_Q` is the same move on the
zero row and is unpaid.

A same-frame identity may use field `684` when the queried row lies in the
span of the other fields currently at that frame and at least one solution
contains `684`. The identity zeros the queried field by those `ADD`s,
replaces the paid query by `ZERO_Q`, and is source-compatible only when
the original row can be restored from fields already at the destination
before the next read. On `W` there are exactly four such queries. Each
destination window has one other field, that field's row is different,
and the cancelled program for field `27` changes `109` endpoint rows.
The selected conditional value stays `781451/250000000`.

## The four queries

While field `684` shares a frame with a paid query, the bank-span test
returns four events. Witnesses are one particular solution and the kernel.

| Event | Field | Rank | Destination | Particular witness | Kernel vector |
|---:|---:|---:|---:|---|---|
| 14884 | 35 | 2 | 159 | `27, 466, 665` | `19, 27, 465, 466, 684` |
| 14888 | 19 | 2 | 152 | `661` | `27, 465, 466, 661, 684` |
| 14893 | 74 | 2 | 160 | `664` | `27, 465, 466, 661, 684` |
| 14895 | 27 | 2 | 156 | `465, 466, 661, 684` | empty |

The symmetric difference of the particular witness with the kernel vector
is the other solution. Field `27` has one solution, and that solution
contains `684`.

At event `14895` the rows are

```text
row(27)  = e_27
row(465) = e_465
row(466) = e_27 + e_465 + e_684
row(661) = e_19
row(684) = e_19 + e_684
```

Their sum is `e_27`. Dropping `684` leaves `e_27 + e_684`, so the free
move is illegal. The four `ADD`s followed by `ZERO_Q` are frame-legal and
leave `2845` paid queries, with the rank-2 count `1341` instead of `1342`.
The final row of field `27` is `0` instead of `e_27`, and `108` further
endpoint rows differ.

## Destination windows

The next read of each queried field is an `ADD` that consumes it:

| Field | Read | Frame | Other occupant |
|---:|---:|---:|---|
| 19 | 15087 | 152 | 208 |
| 27 | 15103 | 156 | 200 |
| 35 | 15181 | 159 | 154 |
| 74 | 15197 | 160 | 146 |

From the query through that read, the destination frame never holds more
than one field besides the queried field. The span of those rows does not
contain the cancelled value. Every witness listed above is outside that
window, so the `ADD`s that built the relation cannot be run there.

## Predecessor

On `research/g20-helper-split/prior/WORD.json.gz` the same field-`27`
query from frame `508` to frame `156` is event `14888`. Its bank has one
solution, the witness `{466}`, and the kernel is empty. The next read is
event `15096`, again with only field `200` beside it, and that window does
not restore `e_27`. The emitted split keeps the paid count at `2846` and
replaces this twin by the four-field witness that uses field `684`.

## Boundary

The check is this identity class on these two pinned words. It does not
rerun native moduli, the eighteen-call invoice, ordinary admission, or a
search that inserts new routes for the witnesses.
