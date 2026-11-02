# Cursor meter for one parent-packet blank-return

No new κ. The selected conditional exponent stays `781451/250000000`.

## Machine

The packet tape is `Tape` in
`research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/records.py`.
The alphabet constants in the sibling `words.py` are `ZERO, ONE, LEFT, RIGHT, BLANK = 0, 1, 2, 3, 4`.
A fresh tape has `cells = [LEFT]` and `head = 1`. `read` at `head >= len(cells)` returns `BLANK` and does not extend the tape. `append` reads a `BLANK`, writes one symbol and steps right. `rewind` steps left until it reads `LEFT`, then steps right once. `clear` is

```text
rewind
while read() != BLANK:
    write(BLANK)
    step(+1)
rewind
```

After `n` appends the tape is `cells = [LEFT] + payload` of length `n + 1`, and the head sits at `n + 1`. Both payload symbols `0` and `1` differ from `LEFT` and from `BLANK`, so the scan length does not depend on the bit.

## Call that erases a completed packet

In `packet_engine.py` the success path, after `copy_bits` has consumed a packet, is

```text
current.read() == BLANK
current.rewind()
current.clear()
```

The comparison read is the completeness check. It leaves the head on the trailing blank and is not part of the erasure meter below. `directory.rewind()` on the same source line is a different tape. The blank-return traced here is the following `rewind` and `clear` on `current`.

`changed.clear()` and `local.clear()` in the same loop are not this call. Their heads depend on `action`, which this note does not price. The failure-path `current.clear()` at the generator's `finally` is likewise not this call: it has no preceding rewind.

## Meter from the trailing blank

Write `R(h)` for `rewind` starting at head `h`, and `C` for `clear` starting at head `1` on a tape whose payload cells are exactly positions `1..n`.

**Rewind from `h = n + 1`.** One left step lands on cell `n`. The loop then reads cells `n, ..., 1` and steps left, then reads `LEFT` at cell `0` and steps right onto cell `1`. That is `n + 1` reads, `0` writes and `n + 2` moves. The `n = 0` case is the same arithmetic: the head is already at `1`, the left step lands on `LEFT`, and the loop body does not run.

**Clear from head `1`.** Its opening rewind costs `1` read and `2` moves and returns to head `1`. The loop then reads, blanks and steps through cells `1..n`, and one further read sees the virtual blank at `n + 1`. That is `n + 1` reads, `n` writes and `n` moves. The closing rewind is the rewind already counted, from head `n + 1`: `n + 1` reads and `n + 2` moves. Adding these gives

```text
reads  = 2n + 3
writes = n
moves  = 2n + 4
```

and restores head `1` with `cells = [LEFT] + [BLANK] * n`.

**Sum, the success-path blank-return.**

```text
reads  = (n + 1) + (2n + 3) = 3n + 4
writes = n
moves  = (n + 2) + (2n + 4) = 3n + 6
```

The success-path rewind, the blanking scan and `clear`'s closing rewind each walk every payload cell. None of them jumps. `clear` also opens with its own rewind. On this call the head is already on cell `1`, so that rewind only steps onto `LEFT` and back. It does not walk the payload a fourth time. Its `1` read and `2` moves are included in the `2n + 3` and `2n + 4` figures above.

## Parent length

`PHYSICAL.md` states the unexecuted parent geometry

```text
B = 2,  G = 3 * 3^124,  S = 2,  U = 9475,
n = U * B * G * S * 3^4 = 9475 * 12 * 3^128.
```

The same product is `972 * 9475 * 3^124`, because the executed fibre is `2 * 3 * 2 * 3^4 = 972` and the two omitted factors are the `9475` unused rows and the `124` atom coordinates inside `G`. Those coordinates are a factor of `n`, not a side path. Each of the three walks above steps across them.

Substituting this `n` is the cursor invoice of one success-path blank-return of a single packet of that length. It is not an execution of the parent: the published child bridge allocates the `972`-bit fibre and does not allocate this tape. The model is the predecessor's one-payload comparison, with the executed `Tape` operations in place of the one-visit lower bound.

Under that bound the parent write count was only `≥ n` and the executed packet's write count was only `≤ 972`. The machine meets both bounds exactly, and only as write counts. The parent move count `3n + 6` is strictly larger than `n` for this `n`. The same call on the executed fibre has writes `972` and moves `3 * 972 + 6 = 2922`, which is not the parent invoice.

A model that blanks only one executed fibre, or that divides `n` by `3^124` before counting, is a different machine. `clear` writes once per stored payload cell.

## What this does not sign

Gather, routing, parking, checkpointing, table setup and the reverse-row coefficient stay unpriced. `BILL.md`'s `G`, `C` and `F` terms are not set to zero. Splitting the parent into `9475` separate tapes would replace one sentinel pair by `9475` sentinel pairs; that layout is not the packet engine's one `current` tape, and it is not claimed here. No carrier admission and no selected-frontier change follows.
