## Problem and result

The source-bound complete Core needs original phase-pure interiors. Small
explicitly admitted partitions do not establish that the production carve has
a nonempty interior at every original position. Identity holes also make a
target interval different from the same interval in source indices.

This package gives an exact closed-form decision for the actual source:
invert the selected target map, compute the largest phase-pure selected run M
from clipped endpoint cells and the complete-middle total, then apply
`I nonempty iff M>6W` for the unchanged capped carve. It uses a fixed number of
integer operations without enumerating phases or rows.

The uniform sufficient guard is

`S>=e(6W+1), L>=12W+2`.

Every ordinary original target start is covered, including short endpoint
half-cells. Both integer thresholds have one-unit adverse families that retain
`N-L>=W`. Sharpness is for ordinary integer windows, not dyadic-aligned
production windows. Source cap/alignment/complementary-gap admissions remain.

In the cited conservative theta<=p^-2, W=O(sqrt(p) polylog p), L>=p^400 family,
these inequalities hold eventually. Thus I and J need no separate nonemptiness
assumption at each original context. The guard costs O(d^2) bit work for d-bit
descriptors. One check per axis covers K contexts when that axis's source and
width descriptors are common; heterogeneous descriptors retain their own
checks, up to the complete O(K g d^2) setup bill.

## Novelty and exact sources

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Three unchanged executable inputs on main: rational Reference, Core partition,
and authenticated capped carve. No unmerged executable dependency is used.
SOURCES.json binds exact Git blobs/SHA256 and the canonical task.

Nick Petalas's CrocSwap/integer-mult-bounds#6259 owns phase cuts and endpoint
lengths for the different 4w physical-source carve. The capped phase-fusion
lineage already supplies cap, separation and asymptotic density. This adds the
target-coordinate/identity-hole decision and finite sharp guard for the 6W
source. It does not reclaim prior floor identities or density order. Current
complete-Core and source-halo joins remain credited predecessor work.

## Reproduction and checks

```sh
python3 -B scripts/research_package.py --package research/core-production-nonempty
python3 -B scripts/check_research_commit.py --package research/core-production-nonempty --check-modes
```

Ordinary and optimized runs compare their entire receipt with RESULTS.json.
Independent literal rational coordinates cover all 772,850 ordinary windows
for S=2 through 40 and every excess/start/length. Original authenticated source
geometry/partition/carve bodies check 77,793 configurations, including 855
uniform-guard admissions. Sixteen W values check each sharp family; 17 controls
detect wrong coordinates/origins/width/ties, invalid domains and corruption of
each source input. Descriptors reach 1024 bits without enumeration. The written
proof carries the universal theorem.

## Scope, limits and credit

**No new kappa; all five foundational assumptions remain.** This is one
geometric source admission. It supplies no row gap, matrix/Schur formation,
conditioning, precision/compiler/native/ownership admission, whole halo run or
final recovery. The verifier projects the exact Reference geometry prefix and
interior method; it does not produce Gaussian coefficients or execute native
payloads. Genuinely empty short windows need their own complete solver.

Prepared for **@CubeJerry** with substantial OpenAI assistance. Credit Jose
Manuel / jmbarrancoml, Nick Petalas, Vlado Vojdanovski, Cinna Davis, Jeremy Kothe,
Mason Hale, Dugongue and the retained source contributors. The root separately
reviewed the proof and refined the complementary-gap sharpness control. Full
notices and scopes are retained. Apache-2.0; no human or proof-kernel acceptance.
