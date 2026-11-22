# Fixed-word second-slot screen

`pinned/ONE-RESIDUAL.json.gz` is the frozen 4+4→8 balanced-fusion graph prepared
by the companion investigation. Its SHA-256 is
`7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7`.
The checker independently executes its 39,605 instructions with 630-bit
input masks: all original charts and 3,433 private clear records remain,
629 outputs are exact, and output 130 has only input `x38` as an extra.
This packet does not itself prove that the graph is the admissible physical
supplier or compare the expanded graph to its native predecessor.

Run `python3.12 -I -B second_slot.py`. The verifier tests five already-paid MOVE
sites on this exact tape. At one site at a time, it allows the sent field
to be XORed with any linear combination of all preclock fields at the
same sender, including freely retained sender history. Every terminal
decoder may combine its entire received history for free. The subsequent
tape, clocks, destinations and all other moves are fixed. It checks every
one of the 630 required native output rows. Thus failure under these generous
side information allowances excludes any such source-local single-site
linear repair; it does not exclude changed histories, another contact,
coordinated paid recodings, changed endpoints, nonlinear strategies, or
different output locations.

| Field | Frozen index | Source → destination | Result |
|---:|---:|---|---|
| 2472 | 8635 | 380 → 544 | no solution; core includes chart-1 owner 22 |
| 2475 | 8647 | 381 → 544 | no solution; core includes chart-1 owner 275 |
| 2477 | 8655 | 382 → 544 | no solution; two conflicting parity equations |
| 3318 | 21258 | 91 → 544 | no solution; two conflicting parity equations |
| 3317 | 21254 | 0 → 91 | no solution under the same fixed-tape template |

These are the four literal chart-544 ingresses and the final 0→91 feeder.
`slot_solver.py FIELD --historical` emits each equation core and the
source registers or historical fields in that equation.

The separate `sponsor_solver.py` studies the tempting frozen index 11012
509→0 return of field 3150. It permits an arbitrary linear recoding from
all live and historical source fields, then asks whether `x38` can be
reconstructed from chart 0's complete live and retained state before its
0→91 send, while native output 111 remains linearly decodable from all
chart-525 history. Both requirements constrain the same source coefficient
parity for live fields 3149, 3150 and source `history-12`: the first
requires 1 and the second 0. The solver tests the other unaffected
terminal outputs as well, but those are not needed for this two-equation
contradiction. This does not rule out repairing chart 544 without first
reconstructing `x38` at chart 0, or changing subsequent paid contacts.

## Why the screen is exact for its template

Inject a formal marker at the selected paid field and replay the fixed
tape on complete input masks. After substituting a sender-local linear form
`q` for the marker, each observation at a chart is `b_j + a_j q`, where
`a_j` is 0 or 1. Let `H0` be the span of all `b_j` with `a_j=0` and all
`b_j+b_*` with `a_j=1`, for any marked observation `b_*`. A desired row
is linearly decodable exactly when it belongs to `H0` or
`b_*+q+H0`. Expressing `q` in the source's available-field basis converts
the latter condition to exact binary linear equations on its coefficients.
The program prints contradictory equations when that system is
inconsistent. `second_slot.py` validates the marked-history identity on 200
deterministic four-input examples against all 16 possible `q` values and
all 16 targets, including duplicates and zero observations.

These are locally generated checks, not an independent scientific review.
The hypothetical 4+4→8 price gain and the seven-placement invoice have
separate evidence; this packet establishes neither a complete operator
repair nor a new κ bound.
