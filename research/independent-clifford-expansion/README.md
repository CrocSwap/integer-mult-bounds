# Exhaustive nearest-Clifford steps on the round-three contact graph

**Finite local obstruction; no higher κ.** On the pinned PR4610 round-three
word, no distance-one Clifford chart change in either of the two declared
move domains improves the complete recursive moment for any saving
`0 <= C <= .005`. The selected conditional κ remains **0.00302015**.

This changes the common-axis binary-switch model of
[general-gaussian-contact-search](../general-gaussian-contact-search/README.md):
each moved node can choose any neighboring Lagrangian, changing its subspace
and phase together. The optional discovery composes independent Pauli axes
at different nodes. This also changes the fixed-subspace hypothesis of
[phase-rank-debt](../phase-rank-debt/README.md). Neither predecessor's result
is claimed as new here.

| Source-bound move domain | Movable nodes/groups | Complete moves | Signed rank polynomials |
|---|---:|---:|---:|
| All original zero edges constrained to stay equal | 800 | 817,600 | 417 |
| One chronological node, with new zero-edge costs charged | 18,240 | 18,641,280 | 157 |

There are exactly 1,022 distinct nearest Lagrangian charts at each nine-axis
node. Both censuses include all of them. Frozen main, adapter and owned
contacts stay fixed. Every native warp is repriced, and helper rewards use
the whole relative Clifford rank. All 408 helpers remain distinct arbitrary
inputs, and all eight rank-eight centers stay paid. The baseline is exactly

```
paid    {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}
helpers {4:28, 7:7, 8:47, 9:326}.
```

[PROOF.md](PROOF.md) gives the complete finite argument and claim boundaries.
[RESULT.json](RESULT.json) contains the full rank-polynomial histograms,
witnesses, multiplicities, graph hashes and integer interval certificates.
Most patterns satisfy exact concave dominance; rigorous outward integer
bounds prove the rest on the entire saving interval. This is not an inference
from a sampled exponent or a floating solver's optimum status.

## Reproduce

Python 3.12 or later and a C++17 compiler (`g++` or `clang++`) are required;
there are no Python package or network dependencies. Run from repository root:

```sh
python3 -B scripts/research_package.py --package research/independent-clifford-expansion
python3 -I -O -B research/independent-clifford-expansion/verify.py
```

The registered command recompiles and reruns both full censuses in a temporary
directory. Python independently checks every histogram bucket's witness.
The checker enumerates all 153 Lagrangians in dimensions one through three,
compares all nonzero-axis images, and checks 5,661 independent-axis physical
rank pairs plus 1,143 sequential compositions with literal Clifford circuits.
Three corruption controls must reject, and a real rank-improving fixture
must pass. The commands are read-only and remain active with Python `-O`.
`--write` regenerates the receipt for authoring only.

Optional discovery is separate from the registered exact certificate:

```sh
python3 -B research/independent-clifford-expansion/discover.py \
  --rounds 30 --plateau --output /tmp/independent-charts.json
```

The final-source runs in [DISCOVERY.json](DISCOVERY.json) record seeds,
compiler/environment, graph/source hashes and every accepted move. One strict
pass and 34 plateau passes found no paid/helper-profile change. The 1,960
accepted plateau moves do not exclude other paths or simultaneous moves.
Floating discovery comparisons are not used in the exact interval proof.

## Scope and attribution

This is an exact finite result about a named geometric invoice model and
source. It does not exclude coordinated changes of several different groups,
arbitrary independent Clifford assignments, larger moves, changed scalar
words, changed native maps or new owned-center protocols. No new physical
supplier, uniform compiler, ordinary BIT admission, outer ledger, practical
runtime, full multiplication theorem or formal proof-kernel result is claimed.
The inherited inverse-chart/native tariff and source all-column ABI are
explicit premises. The selected record is unchanged.

Credit Cao Yifan / PR4610 for the round-three word; Dugongue / PR4654 for
inverse-chart phase geometry; Cinna Davis's general contact model, PR4470 and
query-thinned controller lineage; zxv's native/compiler machinery; Jacob
Alan Sussman's mixed-target recursion; and all retained E8, Clifford, BIT,
scalar, precision and outer contributors. The literal quarter-turn circuit
is reused from the credited general contact verifier. New census, independent
chart composition, histogram replay and interval certificate prepared for
Cinna Davis / 1337isnot1337 with substantial OpenAI Codex assistance. No
subagents or independent human acceptance are claimed. Apache-2.0.

## Open next questions

Can a coordinated change of several different groups beat the complete
invoice? Start with two actual groups and emit their changed charts and every
incident rank, including newly paid warps and lost helper credit. A favorable
exact moment must precede native implementation; none is supplied here.

Can a changed scalar contact or owned-center protocol remove paid work?
Specify the full arbitrary-input block, owner lifetimes and dirty restoration,
then price it against the same demanded outputs. Such a change leaves this
certificate's move domain and is the appropriate next mechanism to test.
