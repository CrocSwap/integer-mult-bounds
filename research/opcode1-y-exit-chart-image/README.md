# Opcode 1's dimension-8 images of the Y exits

**Exhaustive finite census on one recorded opcode. The selected κ stays
`363005817/100000000000`.**

On the pinned round-three centre word, opcode 1 is the linear automorphism
with columns `(1, 2, 4, 8, 64, 19, 104, 197, 325)`. The 112 Y-exit charts are
frames 142 through 253. Each image under opcode 1 has dimension 8. Comparing
those images with all 162 recorded dimension-8 charts gives a partition:

- 4 images equal the source chart.
- 24 images equal a different Y-exit chart.
- 11 images equal a recorded dimension-8 chart that is not a Y exit and is
  not a role start or final chart.
- 73 images, including role 112's frame 142, equal no recorded dimension-8
  chart.

The pairs are the certificate lines in [PROOF.md](PROOF.md). The checker
recomputes the spans and accepts the certificate only when the two agree.
A chart-image hit is not an emitted warp and not a paid-moment change.

## Scope and evidence

Catalogue card `complex-rank-shape-decoder`, priority revision 8, base
commit `e54523517d0f03e58352e647c403a5af3e525a57`. Scope status:
**changed**. The card asks whether a decoder or coframe change improves the
full signed moment. This package does not build that decoder and does not
price an itinerary. It answers the first open question of PR #7219, which
PR #7219 leaves unrun after proving that opcode 1 preserves dimension.
The reason is in [TASK.json](TASK.json).

Evidence class: an exhaustive finite census. The domain is the 112 Y-exit
charts and the 162 recorded dimension-8 charts. Both sets are finite, both
are visited, and a recorded chart of any other dimension has a span of a
different size, so it cannot equal an 8-dimensional image. This is not a
heuristic search and not a proof about any other warp alphabet.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance at the base commit. Full Git history is needed to
resolve them. The word, the contact-graph model, and the retained emitter
are live inputs.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/opcode1-y-exit-chart-image/verify.py
python3 -O -B research/opcode1-y-exit-chart-image/verify.py
python3 -I -W error -B research/opcode1-y-exit-chart-image/verify.py
python3 -B scripts/research_package.py --package research/opcode1-y-exit-chart-image --check-only
python3 -B scripts/research_package.py --package research/opcode1-y-exit-chart-image
```

The marker is `PASS_OPCODE1_Y_EXIT_CHART_IMAGE` with `y_exits=112`,
`recorded_dim8_charts=162`, `fixed=4`, `y_to_y=24`, `non_y=11`,
`unrecorded=73`, and `role112_chart=142`.

The positive fixture is the mutual pair of frames 146 and 147. Controls
reject a zeroed column of opcode 1, a 111-exit sample as a stand-in for the
census, the claim that role 112 lands on frame 143, and the claim that
frame 146 is fixed. Not run: `model.build` on the full contact graph, the
inverse opcode `-1`, a physical caller, Lean, Docker, and
`make frontier7000-verify`. `scripts/research_selected_baseline.py` is a
binding check only.

## Open next questions

1. Does any of the 24 Y-to-Y chart images occur as a warp event that leaves
   the paid transport count unchanged? A hit of the chart-image law is not
   yet a walk. The first step is the mutual pair of frames 146 and 147.
   Nothing in this census edits the word, so the paid moment is untouched.
2. Which of these 112 charts does the inverse opcode `-1` carry onto a
   recorded dimension-8 chart? The inverse is a different signed map, and
   this census does not evaluate it.

## Credit

The word is Cao Yifan / intqwq, PR #4610. The span and the chart-image law
are the contact-graph model, which credits PR #4672, PR #4654, PR #4610, and
the PR #4470 lineage. The Y-exit indexing follows
`research/y-exit-rank-lift-obstruction`, which credits discussion #1166
comment 19133861, Chris R / Clear1nsight. The question is the first open
question of PR #7219, whose dimension lemma is the predecessor and is not
reopened here. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0. No independent human review or proof-kernel check
is claimed.
