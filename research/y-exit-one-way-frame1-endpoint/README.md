# The one-way Y-exit move onto frame 1 is not a retained endpoint

**Scoped proof on one finite schedule. No new κ.** The selected value stays
`363005817/100000000000`.

On the pinned round-three centre word, the retained endpoint is the emitted
final-chart tuple, with the eight centres on the empty chart. Frame 1 is the
unique dimension-9 chart. Every Y exit is a different dimension-8 chart
strictly inside it. Moving those exits onto frame 1, without the return,
leaves each moved role on frame 1, so the retained tuple rejects the move.
The linear rows do not change.

The contract that accepts the move replaces exactly those Y exits by frame 1
and keeps every other chart. That schedule raises the paid moment by exactly
one per moved exit at every exponent in `(0, 1]`. For all 112 exits the
increase is 112. The predecessor gap of at least 48 still prices the same
chart replacement together with an optimistic credit of 64 for deleting the
eight centre transports. Those transports stay on the accepting contract, and
deleting one of them fails the next add on the empty chart.

The restored-exit argument of open PR #7102 does not apply: this move does
not restore the rank-8 charts. No selected-frontier change is claimed.

The argument is in [PROOF.md](PROOF.md). The checker reads the pinned word
and replays the transports. It does not trust the counts above as inputs.

## Scope and evidence

Catalogue card `complex-rank-shape-decoder`, priority revision 8, base
commit `e54523517d0f03e58352e647c403a5af3e525a57`. Scope status:
**changed**. The card asks whether a decoder or coframe change improves the
full signed moment. This package does not build that decoder. It answers the
one-way frame-1 question left open by
[research/y-exit-rank-lift-obstruction](../y-exit-rank-lift-obstruction)
and by open PR #7102, on the #4610 round-three word. The reason is in
[TASK.json](TASK.json).

Evidence class: **scoped proof**, with an exhaustive census of the 112 Y
exit charts on this word. The census domain is the Y block
`[112, 224)`. It is not a search over schedules or over other words, and it
is not a proof that every other endpoint contract rejects the move. The
dimension-changing warp question left by PR #7102 is not taken. The 240
emitted warps preserve dimension, and no other warp is constructed.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. The word and the retained emitter are live inputs.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/y-exit-one-way-frame1-endpoint/verify.py
python3 -O -B research/y-exit-one-way-frame1-endpoint/verify.py
python3 -I -W error -B research/y-exit-one-way-frame1-endpoint/verify.py
python3 -B scripts/research_package.py --package research/y-exit-one-way-frame1-endpoint --check-only
python3 -B scripts/research_package.py --package research/y-exit-one-way-frame1-endpoint
```

The marker is `PASS_Y_EXIT_ONE_WAY_FRAME1_ENDPOINT` with
`role112_chart=142`, `changed_endpoint_moment_increase=112`, and
`predecessor_gap_at_least=48`.

The positive fixture moves Y role 112 from chart 142 onto frame 1 after its
last add. The retained tuple fails on that role alone, and the tuple that
rewrites role 112 to frame 1 matches the retained matrix with one extra
rank-1 child. The all-112 fixture does the same for every Y exit. Controls
reject a transport placed before the exit add, deletion of centre role 632's
transport, a width-2 reading of the frame-1 gap, and the claim that chart
142 is frame 1. Not run: a physical caller, Lean, Docker, and
`make frontier7000-verify`. `scripts/research_selected_baseline.py` is a
binding check only; it returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

## Open next questions

1. Can one changed helper final chart fund the frame-1 Y-exit endpoint while
   every centre still ends on chart 0? Frozen helper finals are already at
   their net variation, so they cannot pay for the 112 rank-1 children. A
   lower helper final would be a further endpoint change. First step: name
   one helper role, its emitted final chart, and one legal nested destination
   of lower dimension, then replay the scalar pins and compare the rank mass
   with 112. No such destination is constructed here.

## Credit

The word is Cao Yifan / intqwq, PR #4610. The emitter and the width law are
the retained centre extension. The all-Y obstruction, the gap of at least
48, and the open endpoint question are
`research/y-exit-rank-lift-obstruction` (PR #6927), which credits discussion
#1166 comment 19133861, Chris R / Clear1nsight, for the 224-against-64 stop.
Open PR #7102 prices the restored partial round trip and leaves this
endpoint question open.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
