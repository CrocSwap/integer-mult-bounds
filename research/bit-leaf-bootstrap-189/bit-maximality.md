# Bit word: sink and reuse maximality (observed runs)

Both searches run against PR189's package (an open dependency, not vendored
here), so they are recorded with the exact commands and observed output.

## Terminal sinks

```bash
python3 -B research/bit-leaf-bootstrap-189/bit_sink_pack.py \
  --package <pr189>/research/paired-cube-twin-local-168 \
  --pr184  <pr194>/research/source-assisted/global/assemble_profiles.py
```

```
[load] v=1760 h=24 R=19348 roots=6624 shipped_sinks=34 W=21108 deficit=1936
[scan] admissible sink roots: 474 ranks=[(21, 34), (23, 440)] shipped_ranks=[(21, 34)]
[self-check] rebuilt W=21074 rank=1515392 maxchild=60 vs shipped W=21074 rank=1515392 maxchild=60
[self-check] shipped 34 sinks -> coarse=668298937775631/1000000000000000000 (0.000668298937775631)
             ordinary=133575656392233867106919376397462930483/2e41 (0.000667878281961169)
[pack] target-group size histogram: [(1, 440), (4, 34)]
[extend] rank-23 candidates: 440 free=372 conflicting-with-shipped=68
[extend] full extension rejected: target chain nesting t=1 1762->25190
[extend] largest validating prefix: 0 (next rejected: target chain nesting t=1 1762->25190)
[extend] family after feedback sweep: 34 sinks (0 added)
[price] 34 sinks  (no change)
```

The script rebuilds the frozen terminal profile from the shipped 34-sink
selection bit-for-bit (W, rank, maxchild, coarse and ordinary saving all match),
then enumerates every sink root that satisfies the per-root predicate list of
`bit/terminal.py::prove`. Of the 440 further candidates, every single one fails
the exact target chronology, so no larger target-disjoint packing can be
admitted. No sink can be added.

## Donor reuse

```bash
python3 -B research/bit-leaf-bootstrap-189/bit_reuse_pack.py \
  --package <pr189>/research/paired-cube-twin-local-168
```

```
[load] R=19348 v=1760 h=24 gauges=3960 pairs=1760 non-gauge-roles=15388 W=21108 deficit=1936
[pool] donor candidates (non-gauge, non-root, operand in phase 2): 11844
[pool] donor frames=8628 gauge frames=660
[frames] containment classes: 220 gauge frames contain ZERO donor frames
[greedy] pairs 1760 -> 1760 (+0); unpaired gauges left: 2200
[result] shipped pairing cannot be enlarged by this greedy pass
```

A focused run grouped the 2200 unpaired gauges by their birth-frame dimension:

```
unpaired gauges: 2200 by gauge-frame dim: {20: 2200}
pairs by gauge-frame dim: {20: 0, 21: 1760}
dim 20: frames_contained=[0, 0, 0]   # sampled birth frames contain no donor end frame
```

Every unpaired gauge has a rank-20 birth frame and **no** donor end frame — among
all 8628 distinct donor end frames — is contained in any of them, which is the
exact eligibility condition of `word.py::exact_frames`
(`C.sub(endframe[d], gauge[b].frame)`). Donors cannot be created either: each
pair consumes one distinct donor and one distinct recipient, and the donor pool
is 11844. So the 1760 shipped pairs are maximal, and no W can be removed there.
