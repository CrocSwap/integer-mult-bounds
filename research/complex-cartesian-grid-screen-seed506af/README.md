# Cartesian source-destination grid blocks: a scoped cost obstruction

**Exact block identity and negative cost screen. No selected-word change or new κ.**

Assignment: seed 506af17109f2b8945b6b47236c53520b, track
complex-mechanisms, task complex-rank-shape-decoder, priority revision 3,
scope key cad3ba853d7f324f16fa. Exact base:
0b1cccf86e2f5132ed286a26ef0a681a495740ea. Selected-record SHA-256:
10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32.
The coordination claim is
[Discussion #1167 comment 18924220](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18924220).

## Result

Let X₁, …, Xᵣ and Y₁, …, Yᵣ be n × n block operands. Place them in the
first block column and first block row:

- A(i,1) = Xᵢ
- B(1,j) = Yⱼ
- all other blocks are zero.

Then the ordinary block product satisfies C(i,j) = XᵢYⱼ for every ordered
source-destination pair (i,j). This is a Cartesian-grid mechanism. It differs
from diagonal batching, one-source fanout, and one-destination gather.

The cost model charges a generic width-r matrix-product child by r^(2−a)
size-n child units. Computing the r² products separately costs r². The
recursive-work ratio is

    r^(2−a) / r² = r^(−a).

The selected outer guard permits r ≤ 51. Throughout the target range
0 ≤ a ≤ 1/99, the largest saving occurs at r = 51 and a = 1/99. The exact
integer inequality

    51 · 19^99 < 20^99

implies 51^(−1/99) > 19/20. Even this most favorable grid therefore saves
less than **5%** of its own recursive work. An integer 99th-root certificate
bounds the maximum saving near **3.8937091284%**. The first integer width
reaching 5% at a = 1/99 is r = 161, outside the guard.

This is a scoped obstruction for one generic width-r block-child contract.
Input gathering, source access, copies, helper use, frame changes, output
storage, dirty-state restoration, hosting, precision, and interface
transitions are all assigned zero cost. The screen gives the proposed block
every advantage. It does not establish a replacement ceiling for the selected
word, prove that its exact provider contains Cartesian grids, exclude a
different bilinear algorithm for a grid, or change κ. The selected profile
still needs a separate admissible per-call interface before this mechanism
can be used.

## Evidence and reproduction

The verifier checks the block identity as formal polynomials for 15 width and
block-size pairs. It rejects two mutated block placements, proves the 5%
boundary with integer powers, and certifies the decimal interval with an
integer 99th-root computation.

From the repository root:

    python3 -I -B research/complex-cartesian-grid-screen-seed506af/verify.py
    python3 scripts/research_package.py --package research/complex-cartesian-grid-screen-seed506af --check-only

Expected verifier prefix:

    PASS_CARTESIAN_GRID_COST_SCREEN identity_fixtures=15 rank_domain=2..51 exponent_domain=0..1/99

Exact base, selected record, catalogue, and live explanatory sources are
pinned in SOURCES.json. The changed-scope declaration and evidence are in
TASK.json.

## Related constructions and limits

- PR #1779 studies diagonal batches of rank-one climbs across distinct
  destinations.
- PR #1814 studies three sources feeding one destination.
- PR #1865 studies one source feeding three destinations.
- PR #1764 and PR #1836 study joint boundary children at one or two lanes.

Those mechanisms have different output patterns. The recent dependency-DAG
claim on Discussion #1596 was released after applying the PR #679 support
obstruction to the diagonal-batch family; this package does not replay or
extend that audit.

## Open next questions

Could a changed child contract exploit a Cartesian grid through a bilinear
algorithm cheaper than the generic width-r product while still admitting the
selected provider's arbitrary dirty state and frame endpoints? This matters
because only a changed recursive interface could evade the cost ratio above.
The first step is an exact small-width tensor decomposition with source and
output supports and a complete copy, frame, and restoration invoice. The
blocker is that no such native interface or admissible selected-word window
is supplied here.

## Credit

Credit the selected #1094/#1042 complex supplier lineage and the distinct
fanout, gather, diagonal-batch, and joint-boundary predecessors above.
Prepared by Cinna Davis with substantial OpenAI Codex assistance in choosing
the construction, deriving its cost screen, writing the verifier, and
packaging the result. New work is Apache-2.0.

