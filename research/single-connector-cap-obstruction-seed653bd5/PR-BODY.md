## Result

Scoped negative result for one added dirty accumulator in the selected late complex block. If the single added array reads all eight independent external inputs and is the sole carrier of their `Qz` terms to the four retained additive ports, monotone frame growth makes the route infeasible: the joined input frame is not contained in any rank-eight target cap. Existing helpers may still carry the retained `Ry` and dirty-endpoint work, but cannot store external `Qz` terms. The last external input contributes to two distinct ports, so after the connector has read all eight inputs at least one required output update would force its target to rank nine.

The exact checker covers the 12 blocks in the selected word and 24 blocks from two pinned PR1319 comparison words: 36 block instances and 144 target-cap pairs. Every pair has `dim(span(F_1,...,F_8) + H_j) = 9`; the six rank-eight joins across the three words also differ from every cap. No scalar schedule, gate count or connector tour can evade this frame obstruction inside the stated class.

This is not a general connector lower bound, a result about multiple `Qz` accumulators or direct source-to-target routes, a selected-supplier replacement, or a new `kappa`.

## Provenance and scope

The exact base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; the selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. `SOURCES.json` pins the selected review, source manifest, assembly certificate, task catalogue, block certificate and compressed block sources.

The closest neighboring constructions are PR #1522's centered BIT source tour, PR #1717's paired dirty-output delta, PR #1739's source/map transition, and PR #781/#855's separate six-source coded-helper packet cell and provider-cost analysis. Those results and their authors remain credited; this result is only the all-eight-input frame-join obstruction for the selected four-port block interface.

## Reproduction

From the repository root:

```sh
python3 -I -B research/single-connector-cap-obstruction-seed653bd5/verify.py
python3 -I -B research/complex-block-rank-optimum/verify.py
python3 scripts/research_package.py --package research/single-connector-cap-obstruction-seed653bd5 --check-only
make selected-record-check
```

The local replay passed on Python 3.14.7:

```text
PASS_SINGLE_CONNECTOR_CAP_OBSTRUCTION selected_blocks=12 selected_pairs=48 all_blocks=36 all_pairs=144 rank8_joins=6 rank9_joins=30 positive_control=1 cap_mutation_rejected=1
PASS_FIXED_BLOCK_MOMENT_PREMISES blocks=36 subsets=9180 minors=36 controls=12
PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)
PASS selected record, exact kappa, original source inventory and proof supplement: 836330098538459/500000000000000000
```

The full research-package wrapper is configured for Python 3.12; the generic metadata check and direct verifiers were run locally. No full selected-construction cold replay is claimed.

Authored by Cinna Davis with substantial OpenAI Codex assistance in scoping, proof development, exact verification, source handling and writing.
