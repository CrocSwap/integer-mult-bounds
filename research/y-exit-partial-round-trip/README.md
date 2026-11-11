# A restored partial Y-exit round trip does not lower the paid moment

**Scoped proof on one finite schedule. No new κ.** The selected value stays
`781451/250000000`.

On the pinned round-three centre word, with every emitted final chart kept,
a round trip of any nonempty set of the 112 rank-8 Y exits through frame 1
raises the exponent-1 paid moment by at least twice the number of exits.
When the emitted scalar, scale, and warp events stay on their recorded
charts, the paid histogram itself is forced, and the same round trip raises
the paid moment by exactly `2k` at every exponent in `(0, 1]`. Deleting a
helper transport cannot pay for that increase while the helper's final chart
stays. The selected frontier is unchanged.

The argument is in [PROOF.md](PROOF.md). The checker walks the emitted
events and replays one inserted round trip. It does not trust the counts
above as inputs.

## Scope and evidence

Catalogue card `complex-rank-shape-decoder`, priority revision 8, base
commit `17469fff78c22941280f04d39dc5a1faee09c840`. Scope status:
**changed**. The card asks whether a decoder or coframe change improves the
full signed moment. This package does not build that decoder. It answers the
first open question of
[research/y-exit-rank-lift-obstruction](../y-exit-rank-lift-obstruction):
whether moving only some Y exits, or also deleting helper calls, can clear
a paid moment while restoring every rank-8 Y exit. The reason is in
[TASK.json](TASK.json).

The all-112 round trip in that package costs 224 rank-1 children against an
optimistic centre credit of 64. That credit drops the centre roles off the
empty chart. The partial route was not priced. Here the endpoint keeps
every final chart, so the centre credit is not spent, and every nonempty
subset loses.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. The word and the retained emitter are live inputs.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/y-exit-partial-round-trip/verify.py
python3 -O -B research/y-exit-partial-round-trip/verify.py
python3 -B scripts/research_package.py --package research/y-exit-partial-round-trip --check-only
python3 -B scripts/research_package.py --package research/y-exit-partial-round-trip
```

The marker is `PASS_Y_EXIT_PARTIAL_ROUND_TRIP` with `y=112`,
`forced_transports=3298`, `rank_mass=5327`, and
`moment_increase_per_exit=2`.

The positive fixture inserts the frame-1 round trip on Y role 112 after its
last pinned event. The matrix matches the retained replay, and the histogram
gains two rank-1 children. Controls reject deleting one transport, a width-2
reading of the frame-1 gap, and the empty exit set. Not run: a physical
caller, Lean, Docker, and `make frontier6030-verify`.
`scripts/research_selected_baseline.py` is a binding check only.

## Open next questions

1. Can the one-way move of every Y exit onto frame 1 be accepted as an
   endpoint? The predecessor already shows a rank-mass gap of at least 48,
   and that move replaces each rank-8 exit by frame 1. The restored-exit
   argument here does not apply. The first step is the same comparison of
   one Y role's exit chart before and after the one-way transport.
2. Does a dimension-changing warp, outside the 240 same-dimension warps on
   this word, give an unpaid path from a Y exit to frame 1? No such warp is
   constructed here. The first step is one retained warp opcode whose source
   and destination charts differ in dimension, or a proof that the native
   alphabet forbids that pair.

## Credit

The word is Cao Yifan / intqwq, PR #4610. The emitter and the width law are
the retained centre extension. The all-Y obstruction and the open question
are `research/y-exit-rank-lift-obstruction`, which credits discussion #1166
comment 19133861, Chris R / Clear1nsight, for the 224-against-64 stop.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
