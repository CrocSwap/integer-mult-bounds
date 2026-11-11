# No retained warp opcode changes dimension

**Scoped proof on one recorded alphabet. The selected κ stays
`363005817/100000000000`.**

On the pinned round-three centre word, the recorded warp alphabet is the 72
maps in `canonical["warps"]` together with the inverses `model.inv` retains.
Each map is a linear automorphism of `GF(2)^9`. Under the native chart-image
law, an automorphism admits only equal-dimension chart pairs. Opcode 1, the
named example, joins frame 292 to frame 293, both of dimension 4. No retained
opcode admits a warp from a dimension-8 Y exit onto the dimension-9 frame 1.
A finite product of retained opcodes preserves dimension as well.

The argument is in [PROOF.md](PROOF.md). The checker recomputes the census
and the chart images. It does not trust the counts above as inputs.

## Scope and evidence

Catalogue card `complex-rank-shape-decoder`, priority revision 8, base
commit `e54523517d0f03e58352e647c403a5af3e525a57`. Scope status:
**changed**. The card asks whether a decoder or coframe change improves the
full signed moment. This package does not build that decoder. It answers the
second open question of PR #7102, on the same #4610 round-three word. The
reason is in [TASK.json](TASK.json).

Evidence class: a proof that every bijective linear map preserves subspace
dimension, together with an exhaustive census of the 72 recorded maps. The
240 emitted warps are a second exhaustive census, recomputed from the event
list. PR #7102 already records that those 240 preserve dimension. The recount
splits them into 72 endpoint uses, at dimensions 4 and 5, and 168 other uses,
at dimensions 0, 1, and 9. The Y-exit prohibition is the lemma, because those
240 events never use a dimension-8 chart.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. The word, the retained emitter, and the contact-graph model are
live inputs.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/retained-warp-opcode-dimension/verify.py
python3 -O -B research/retained-warp-opcode-dimension/verify.py
python3 -I -W error -B research/retained-warp-opcode-dimension/verify.py
python3 -B scripts/research_package.py --package research/retained-warp-opcode-dimension --check-only
python3 -B scripts/research_package.py --package research/retained-warp-opcode-dimension
```

The marker is `PASS_RETAINED_WARP_OPCODE_DIMENSION` with `opcodes=72`,
`dimension_changing_opcodes=0`, `opcode_1=292->293 dim=4`,
`y_exit_to_frame1_admitted=0`, and `emitted_warps=240`.

The positive fixture is opcode 1: frames 292 and 293, dimension 4, with the
recorded columns and a chart-image match. Controls reject a column of opcode
1 zeroed out, a 71-opcode sublist, the pair (Y exit, frame 1) under opcode 1,
a same-dimension chart outside that image, a sample of ten emitted events as
a stand-in for the alphabet, and a width-0 reading of the one-dimension gap.
Not run: `model.build` on the full contact graph, a physical caller, Lean,
Docker, and `make frontier7000-verify`.
`scripts/research_selected_baseline.py` is a binding check only.

## Open next questions

1. Which dimension-8 charts, if any, does opcode 1 carry a Y-exit chart onto?
   The dimension lemma says the image has dimension 8, so the image is not
   frame 1. It can still equal another rank-8 chart. A warp onto that chart
   would move the exit with no paid transport, inside this alphabet. The
   first step is to map the exit basis of Y role 112 by opcode 1’s columns
   and test the image against the other 111 Y-exit spans. Nothing algebraic
   blocks that census; this package stops once unequal dimensions are
   excluded. The one-way acceptance of frame 1 as an endpoint is a different
   contract and is not this question.

## Credit

The word is Cao Yifan / intqwq, PR #4610. The emitter is the retained centre
extension. The chart-image law and `model.inv` are the contact-graph model,
which credits PR #4672, PR #4654, PR #4610, and the PR #4470 lineage. The
question is the second open question of PR #7102. The Y-exit geometry follows
the round-three indexing in `research/y-exit-rank-lift-obstruction`, which
credits discussion #1166 comment 19133861, Chris R / Clear1nsight.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
