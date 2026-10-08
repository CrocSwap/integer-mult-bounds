# Reordering the rank-pair physical compilation

This experiment changes the schedule of equal-rank regions in PR #63's
composition of the PR #62 scalar graph and PR #60 rank-first compiler. The
23-axis uses increasing `(rank, cover, core)`; the 25-axis uses increasing rank
and decreasing minimum node number. The scalar identities, matched carrier
candidates, synthesis, and descending-rank retirement policy are unchanged.

Reordering changes which retired physical roles are available when a region
is compiled. The resulting words have the same 27,918 and 36,586 physical
roles, but different paid fixed-I+J profiles. The selected schedules came
from a bounded comparison of reverse-node, core-cover, cover-core, and
reverse-core-cover orders. Core-cover was screened only; the other three
23-axis words and the reverse-node 25-axis word were independently replayed
and physically profiled before selection. Reversing both axes was weaker
than the selected mixed schedule. These finite tests do not prove optimality.

## Why the schedule remains valid

Every region retains its exact original envelope and its original linear
map. The wrapper checks every incoming inter-region dependency and every
selected-candidate direction against the new order. Thus all required inputs
are available, and retained carriers still travel forward. The admissibility argument uses these explicit dependency inequalities;
rank ties alone do not certify topological order, especially for source
frames. The complete serialized physical word is replayed on every input
and dirty basis vector in both orientations, and all frame inclusions and
actual fixed-basis profiles are independently regenerated.

The literal rank identity and all paid endpoint/data/exterior terms use the
unchanged inherited profile constructor. No histogram estimate substitutes
for the physical word. The general transfer, routing, analytic, recovery,
and fixed-tape hypotheses remain inherited conditions; this is a finite
conditional certificate rather than a new formal proof of those hypotheses.

## Reproduce

From the repository root, with assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/reordered-rank-pair/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 research/reordered-rank-pair/verify.py --rebuild
PYTHONDONTWRITEBYTECODE=1 python3 research/reordered-rank-pair/test_negative.py
```

The first command checks source/artifact hashes, independently replays both
committed words, rebuilds their fixed-I+J profiles, and recomposes the paid
global profile. `--rebuild` also recompiles both words and requires exact
byte equality with the committed decompressed witnesses. Disposable output
goes under `build/reordered-rank-pair` (or `--work-dir`). The tests reject a
missing physical XOR, understated physical role count, changed word/profile
digests, a backward region dependency, and execution with Python assertions
disabled. Arithmetic witnesses and their
independent controls are in `arithmetic/`.

## Attribution

The graph is Avi Eisenberg's PR #62 interval-strip/core-aware pair assembly,
prepared with Claude assistance, with its retained credits to PR #53, #48,
#44, #46, #41, #43, and earlier icekylinx work. Chafik Boukhalfa's PR #60
rank-first compiler derives from eumemic's PR #57 joint frame compiler,
both with OpenAI Codex assistance. Dominik Scholz's PR #63 combines those
sources, with OpenAI GPT-6 Astra assistance. Alejandro Zarzuelo Urdiales's
PR #61 supplies precedent for rational parameter refinement. This bounded
region-order experiment and its packaging are by Rohan Arun with OpenAI
Codex assistance. Original Apache-2.0 notices remain applicable.

## Live comparison at publication

PR #64 (`790a14e28e935398072b9a9a68694ce7fba8940f`, @rfu08) reports
`20411033624901463/400000000000000000000` for the unchanged #63 profiles,
with additional independent verification and scoped Lean formalization.
The present changed-schedule bound exceeds that reported value; exact
arithmetic and the source pin are in `current-comparison.json`. This is only
a bound comparison, not a comparison of formal proof coverage.
