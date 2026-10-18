# Five ten-piece P112 beta exclusions from a coordinate budget

Ten independent P112 pieces with code intersection dimension at least five
cannot have any of these weight profiles:

```
2,2,4,5,6^6
2,2,5^3,6^5
2,3,4^2,6^6
2,3,4,5^2,6^5
2,4^3,5,6^5.
```

The theorem holds over every characteristic-zero field. These profiles occur
in the pinned TWOSIDE `(b,t)=(5,5)` residue. They are not excluded by the
weight-certified eight-cut, ten-cut or twelve-cut rank-four-anchor rules
audited here. No claim of a complete current residue count is made.

Four small pieces leave six affine root-simplex vertices. The new step counts
the 112 available coordinates: six endpoint values with k nonzero entries
have at most 4k+1 unequal pairs. The required incidence inequality becomes

```
795 <= 112 + 8s + 4U,
```

where s is the small-support union size and U is the sum of the six remaining
support sizes. The five profile bounds give right sides 784,784,768,768,768,
with contradiction margins 11,11,27,27,27. The original endpoint-only count
fails on the first three profiles. [PROOF.md](PROOF.md) gives all hypotheses,
the characteristic-zero argument and the exact relationship to predecessors.

[RESULT.json](RESULT.json) records the complete 4,097,782-flat replay,
7,140 root-plane checks, 960 reflections, original 38-shape weight residue,
five applications and an explicit overlap control. Sixteen behavioral groups
include an independently coded cover oracle, all endpoint equality patterns,
input mutations and valid support budgets where the contradiction fails.
The third initial candidate `3^3,4,6^6` was rejected as already covered by
PR3167 and remains a required control.

This advances five finite decoder-floor cases. Full C5, `C(P112)>=64`,
supplier admission and an improved kappa remain open. The selected conditional
kappa remains `0.001672660197076918`.

## Reproduce

Requires Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-ten-piece-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-ten-piece-simplex
```

An existing Python 3.12 executable can replace the `uv run` prefix. The
registered replay checks exact sources, reconstructs the mathematical receipt,
compares it to the committed JSON, and runs the behavioral controls with
optimization enabled. Both commands are bounded to 120 seconds and run
sequentially. Direct Git-free replay uses `verify.py` and `test_verify.py`
with this package and the single declared P112 input at its repository path.
`verify.py --output NEW_PATH` writes a new external receipt and refuses to
overwrite an existing path. No build, network or native dependency is needed
for the direct replay. [CHECKS.json](CHECKS.json) records environments and limits.

## Open next questions

Can the same coordinate accounting exclude `4,5^9`, another pinned ten-piece
survivor? The present four-small-piece support allowance is 44, and adding one
remaining weight-five support gives 56, above the distance 53. First find a
valid quotient normalization using the actual supports or prove a replacement
for that independence step. The current argument cannot assume that step.

Can the root-simplex and endpoint-count lemmas be kernel-verified separately
from the finite E8 input? Start with six endpoint values and the root inner
products, then bind a verified label-capacity receipt. This package supplies
no proof-assistant environment. Structured questions are in [TASK.json](TASK.json).

## Credit and scope

Nick Petalas contributed the coordinate-budget strengthening and these five
ten-piece applications. DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
supplies TWOSIDE and the open conjecture map. Nick Petalas's
[PR3164](https://github.com/CrocSwap/integer-mult-bounds/pull/3164) supplies the
root-simplex argument, geometry code and earlier nine-piece exclusions;
[PR3161](https://github.com/CrocSwap/integer-mult-bounds/pull/3161),
[PR3162](https://github.com/CrocSwap/integer-mult-bounds/pull/3162) and
[PR3167](https://github.com/CrocSwap/integer-mult-bounds/pull/3167) supply the
audited prior cover contracts. Geometry and label reconstruction retain the
E8/P112 and one-sided decoder lineage, including DreamingOfClouds's source
packages and joaqcoo's original decoder model. Exact heads, paths, Git blobs,
hashes and code origins are in [SOURCES.json](SOURCES.json). Historical source
records were checked locally; the replay uses the self-contained proof/code
and declared P112 input. Required provenance uses canonical main only, so
fresh CI needs no unrelated unmerged PR commits or preserved merge strategy.
Predecessor files are unchanged. New work and reused code are Apache-2.0.

Internal read-only mathematical review corroborated the counting argument and
separately enumerated the prior covers. Independent human review, proof-kernel
verification and hosted CI are separate; none is claimed here. The Weyl-chamber
theorem is an explicit mathematical dependency. [ENGINEERING.md](ENGINEERING.md)
records implementation bounds and the decisions shaped by the engineering skills.
