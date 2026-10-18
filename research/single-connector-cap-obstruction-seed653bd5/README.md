# One framed connector cannot reach the selected block's late ports

**Scoped recursive-interface obstruction; no new `kappa`.** In each of the 12
selected late blocks, the join of the eight read-only input frames is not
contained in any of the four retained rank-eight target caps. A single
monotone accumulator that reads all eight inputs must therefore force a
rank-nine target climb before it can deliver the last source contribution.
The target endpoint forbids that climb.

The obstruction is checked over the 12 selected-word blocks and 24 pinned
blocks from the PR1319 base/extra words: **36 blocks, 144 target-cap pairs**.
Every pair has `dim(span(F_1,...,F_8) + H_j) = 9`. The selected input join has
rank eight in blocks 592 and 696 and rank nine in the other ten blocks; none
of the four target caps contains it in either case.

This tests one added physical accumulator as the sole carrier for the eight
external `Qz` terms of the four-output correction. The retained helper route
may still carry `Ry` and dirty endpoint information, but cannot act as another
`Qz` carrier. It does not cover
multiple accumulators, direct input-to-target operations, target retiming, or
different endpoint caps. It is not a general connector lower bound, selected
supplier replacement, or exponent improvement.

The accepted selected record remains
`836330098538459/500000000000000000` (`0.001672660197076918`). The source record
is pinned by SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32` at base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Its review, source manifest,
assembly certificate and reproduction command are separately pinned in
`SOURCES.json`.

## Reproduce

From the repository root with Python 3.12 or later and no third-party
dependencies:

```sh
python3 -I -B research/single-connector-cap-obstruction-seed653bd5/verify.py
python3 -I -B research/complex-block-rank-optimum/verify.py
python3 scripts/research_package.py --package research/single-connector-cap-obstruction-seed653bd5 --check-only
make selected-record-check
```

The first command prints:

```text
PASS_SINGLE_CONNECTOR_CAP_OBSTRUCTION selected_blocks=12 selected_pairs=48 all_blocks=36 all_pairs=144 rank8_joins=6 rank9_joins=30 positive_control=1 cap_mutation_rejected=1
```

The predecessor checker prints `PASS_FIXED_BLOCK_MOMENT_PREMISES` and checks
the stored source-bound certificate. The package metadata command checks
source pins; it is not a mathematical acceptance check. No full selected
construction replay is part of this contribution.

## Coordination and nearby results

The focused claim is [Discussion #1771](https://github.com/CrocSwap/integer-mult-bounds/discussions/1771).
The 2026-10-14 09:28 UTC overlap refresh covered 442 open PRs and 407
Discussion/comment/reply records with complete pagination and no warnings.
The refreshed records showed related but different work: [PR #1522's centered
BIT source tour](https://github.com/CrocSwap/integer-mult-bounds/discussions/1493),
[PR #1717's paired dirty-output delta](https://github.com/CrocSwap/integer-mult-bounds/pull/1717),
and [PR #1739's source/map transition](https://github.com/CrocSwap/integer-mult-bounds/pull/1739).
The close geometric predecessor is [PR #781's six-source coded helper](https://github.com/CrocSwap/integer-mult-bounds/pull/781)
and its provider-cost follow-up [PR #855](https://github.com/CrocSwap/integer-mult-bounds/pull/855),
documented in `research/complex-packet-borrowing23`. That construction serves
a separate all-K packet cell with one coded helper and multiple target pairs;
this result tests the full join of all eight independent inputs in a selected
four-port late block. No priority claim is made for source tours, coded helpers
or connector extensions generally.

The frame data and source-specific interface come from
`research/complex-block-rank-optimum`, whose proof credits Thomas DiFiore's
helper-basis screen and Douglas Colkitt's fixed-word packing work. The generic
dirty-connector interface descends from Ross Richardson's PR #934. This result
adds only the frame-join/cap incompatibility lemma and its exact replay.

## Open next questions

- Can two or more accumulators partition the external inputs so each partial
  source join lies in the caps of the targets it must still serve? A first
  step is to specify the partition, each frame itinerary, and all transfers,
  then compute a complete hosting/restoration bill.

Authored by Cinna Davis with substantial OpenAI Codex assistance in scoping,
proof development, exact verification and exposition.
