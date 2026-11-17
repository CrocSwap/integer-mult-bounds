# Fuse negation into the marked-tape negative half

A fixed reversible table computes and reverses the negative stochastic half
in at most **`4W+1` local transitions per direction** for every signed width
`W >= 2`. The bound is attained at `x=0` with either resident coin value.
This is a scoped written proof with exact finite corroboration. It reduces
the `6W+2` worst case reported by ToikY's #6809 under the same six-glyph tape,
parity, coin and head-return contract. It uses 35 coin-expanded rows per
direction. [Prior negative-half construction and transition bound][negative]

## Contract

Write `x=2q+p` with `q=floor(x/2)` and `p` in `{0,1}`. For a resident
read-only coin `u`, zxv's #6092 convention gives

```text
S(n,2,u) = floor(n/2) + [u < n mod 2]
S(-x,2,u) = -q-pu = ~q + (1-pu)
```

Here `~q=-q-1` is the signed two's-complement complement. The work head
starts at the clean parity marker in `P0 b0 ... b_(W-2) S(b_(W-1))`, with
the value in little-endian order. The forward call writes `S(-x,2,u)` in
the same layout and retains `Pp`. The inverse restores the original
`x` and `P0`. Both heads return. The work interval is exactly `W+1` cells
including parity, plus one stationary coin cell on a second tape. The
table uses the glyphs `0,1,P0,P1,S0,S1` and no additional working cells.

The directional entry and return states are `F0/FH` and `I0/IH`. Each
row reads one work glyph and the stationary coin, writes one work glyph
and moves the work head by at most one cell. The table supplies each row
explicitly, with `*` expanding to the two coin values. The coin is read
only. All calls stay inside the declared interval, so arbitrary exterior
cells retain their contents. [Literal table](TABLE.txt)

## Forward proof

Follow #6801's marked right shift. Scan to the marked sign, store its
original bit in control and write the complementary sign bit. On the
leftward pass each interior cell receives the complement of the carried
bit from its right. Its original bit becomes the new carry. Thus the
pass writes `~q` across all `W` value cells. Upon reaching the parity
marker, the carried original low bit `p` is written into `Pp`.
[Positive marked-shift construction][positive]

When `e=1-pu` is one, the table ripples an increment through the low
ones of `~q`. It visits the first zero or the marked sign, whichever
comes first, flips that bit and returns over the zeros it just wrote.
When `e=0`, the parity write also halts. The result is
`~q+e=-q-pu`. Both `~q` and `~q+e` fit in signed width `W`, since
`-2^(W-2) <= q <= 2^(W-2)-1`. The ripple agrees with signed addition,
including the all-ones word becoming zero.

## Inverse proof

On a canonical inverse entrance `(y,Pp,u)`, the table uses the same
`e=1-pu`. When enabled, it decrements `y` modulo `2^W` and returns over
the ones it just wrote. At parity it puts `p` into control, clears
the marker to `P0` and starts a rightward shift. In state `IUc`, the
incoming bit `c` is the original bit to write in the current cell. The
complement of the scanned ordinary bit becomes the next carry. At
the marked sign, the table accepts only `S(1-c)` and writes `S(c)`.
The leftward return only moves the head.

The sign rule requires that the two highest bits of the recovered
`q` agree. That is exactly the signed range condition
`-2^(W-2) <= q <= 2^(W-2)-1` for reconstructing `x=2q+p`.
For an integer `y` at the inverse boundary, the candidate is
`q=-(y-e)-1=-y-pu`. The only signed wrap in computing `y-e` occurs
at signed minimum with `e=1`. The wrapped word is signed maximum,
whose two highest bits differ. Its complement still has unequal
highest bits, so the guard rejects, as required by the integer
range test. Thus the inverse halts successfully exactly on the forward
image, where it restores `x=-2y+p(1-2u)` and `P0`. Malformed tapes and
rollback of rejected inputs are outside the interface.

## Local reversibility and exact time

For each target state, all incoming transitions in the table have the same
move. At fixed coin, the written glyph identifies the source row for that
target state. For example, `FD0` and `FD1` each receive a marked sign
from the scan or one of two distinct ordinary bits from the shift.
Each `IU` state receives `P0` from its unique entry branch at that
coin or one of two distinct ordinary bits while shifting. Ripple turns
and return loops have distinct written glyphs, and the halting branches
write distinct parity glyphs at fixed coin. These finite conditions make
the microstep injective. The target state recovers the predecessor head
position and the written glyph recovers the row. The verifier checks both
conditions on every row.

The shift and parity handling cost `2W+1` transitions per direction.
For `e=1`, let `k` be the index of the first zero of `~q`, capped at
`W-1`, using `W-1` if every bit is one. The carry phase adds exactly
`2(k+1)` transitions. The inverse decrement turns at the same cell
because the forward increment replaces exactly those low ones by zeros
and flips the turning bit. The all-ones case turns at the sign in both
directions. Therefore the exact invoice on a valid pair is

| Condition | Transitions per direction |
| --- | ---: |
| `e=0` | `2W+1` |
| `e=1` | `2W+2k+3 <= 4W+1` |

At `x=0` the complement is all ones and `e=1` for either coin, so the
table reaches `4W+1` in both directions. Relative to #6809's exact
worst case this saves `2W+1` transitions. The comparison is between
the two tables' worst cases. Optimality among all machines remains open.

## Reproduction

Run from the repository root with CPython 3.12. The verifier reads the
new table, prints a generated result and writes no files.

```sh
python3.12 -I -W error -B research/fused-negative-half-tape/verify.py
python3.12 -I -O -W error -B research/fused-negative-half-tape/verify.py
python3.12 -B scripts/research_package.py --package research/fused-negative-half-tape
python3.12 -B scripts/check_research_commit.py --package research/fused-negative-half-tape --check-source-history
```

The direct verifier reports `PASS_FUSED_NEGATIVE_HALF_TAPE`. It checks
4,088 exhaustive round trips at widths 2 through 10, 240 translated
boundary round trips through width 4,096, and the full inverse boundary
through width eight (1,016 images and 1,016 nonimages). It also checks five
rejecting controls for coin polarity, the inverse sign guard, an exterior
head movement and both local reversibility conditions. These runs execute
only the new table. The universal quantifier comes from the shift, ripple
and range arguments above.

The verifier caps the table input at 4,096 ASCII characters and the
simulator at `4W+1` transitions for widths through 4,096. The exhaustive
test domains and mutation set are fixed. Python allocates bounded tape
copies and table entries dynamically for verification. These data
structures describe the experiment and are outside the proved work-tape
budget.

## Open next questions

Bind one reached negative half to the marked layout. Start by pinning one
caller site and its signed width, then charge marker setup, resident coin
delivery, parity ownership and the return-state handshake. The supplied
markers, nonbinary glyphs and stationary coin are premises of this local
model. Physical encoding, repeated-call sequencing, reached precision,
native MOVE and the complete supplier bill remain open. This result
establishes a local transition saving and makes no κ claim.

## Credit

This contribution was produced by Nick Petalas. Credit ToikY's #6809 for
the negative marked-tape baseline and its open transition-constant question,
Nick Petalas's #6801 for the positive marked shift and local tape model, and
zxv's #6092 and #6066 for the signed arithmetic and restoration contract.
JoyboyBrian's #6095, AAAmirinu's #6244, Nick Petalas's #6026, Ali Romman's
#5599 and the retained stochastic and native lineage supply context. Exact
canonical provenance is recorded in [SOURCES.json](SOURCES.json).
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

[negative]: https://github.com/CrocSwap/integer-mult-bounds/pull/6809
[positive]: https://github.com/CrocSwap/integer-mult-bounds/pull/6801
