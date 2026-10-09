# Bit word: sink and reuse maximality (recorded runs)

Both levers on the binding bit word were searched against PR189's package
(`research/paired-cube-twin-local-168`, an open dependency of this PR and not
vendored here). The harnesses ship in this package; the observed output is
recorded below with timings elided.

## Terminal sinks: 34 of 34

```bash
python3 -B bit_sink_pack.py \
  --package <checkout>/research/paired-cube-twin-local-168 \
  --pr184  <checkout>/research/source-assisted/global/assemble_profiles.py
```

```
[load] v=1760 h=24 R=19348 roots=6624 shipped_sinks=34 W=21108 deficit=1936
[scan] admissible sink roots: 474 ranks=[(21, 34), (23, 440)] shipped_ranks=[(21, 34)]
[scan] candidate ranks: [(21, 34), (23, 440)]  shipped ranks: [(21, 34)]
[self-check] rebuilt W=21074 rank=1515392 maxchild=60 vs shipped W=21074 rank=1515392 maxchild=60
[self-check] shipped 34 sinks -> coarse=668298937775631/1000000000000000000 (0.000668298937775631) ordinary=133575656392233867106919376397462930483/200000000000000000000000000000000000000000 (0.000667878281961169)
[pack] target-group size histogram: [(1, 440), (4, 34)]
[pack] greedy packings: max=440 min=406 (shipped 34)
[extend] rank-23 candidates: 440 free=372 conflicting-with-shipped=68
[extend] full extension rejected: target chain nesting t=1 1762->25190
[extend] largest validating prefix: 0 (next rejected: target chain nesting t=1 1762->25190)
[extend] family after feedback sweep: 34 sinks (0 added)
[price] 34 sinks coarse=668298937775631/1000000000000000000 (0.000668298937775631) ordinary=133575656392233867106919376397462930483/200000000000000000000000000000000000000000 (0.000667878281961169)
[price] gain coarse=+0.0000% ordinary=+0.0000%  kappa 0.000667432518278 -> 0.000667432518278
```

The script rebuilds the frozen terminal profile from the shipped 34-sink
selection bit-for-bit (W, rank, maxchild, coarse and ordinary saving all match),
then enumerates every sink root satisfying the per-root predicate list of
`bit/terminal.py::prove`. Each of the 440 further candidates is rejected by the
exact target chronology (`target chain nesting`), so no larger target-disjoint
packing can be admitted, even though a packing of all 440 is target-disjoint.

## Donor reuse: 1760 of 3960 gauges

```bash
python3 -B bit_reuse_maximal.py --package <checkout>/research/paired-cube-twin-local-168
```

```
gauges=3960 pairs=1760 unpaired=2200
unpaired by birth-frame dim: {20: 2200}
paired   by birth-frame dim: {21: 1760}
distinct donor end frames (non-gauge, non-root, phase-2 operands): 8628
unpaired birth frames: 220; of these, containing at least one donor end frame: 0
verdict: no unpaired gauge can receive a donor
```

Every unpaired gauge has a rank-20 birth frame, every paired gauge a rank-21
one, and **no** donor end frame — among all 8628 distinct donor end frames — is
contained in any of the 220 unpaired birth frames. That containment is the exact
geometry condition of `word.py::exact_frames`
(`C.sub(endframe[d], gauge[b].frame)`), so no donor can be aliased into an
unpaired gauge: the 1760 pairs are maximal and no W can be removed there. The
same run also shows why a greedy extension cannot help — the shipped pairing is
already the whole of the paired side.

A complementary run of `bit_reuse_pack.py` (four-dimensional scarcity-ordered
greedy with per-insertion validation) reaches the same conclusion:

```bash
python3 -B bit_reuse_pack.py --package <checkout>/research/paired-cube-twin-local-168
```

```
[load] R=19348 v=1760 h=24 gauges=3960 pairs=1760 non-gauge-roles=15388 W=21108 deficit=1936
[pool] donor pool=11844 donor frames=8628 gauge frames=660
[frames] containment classes sized (gauge frame -> #donor frames): [(0, 220), (42, 50), (43, 46), (44, 4), ...]
[greedy] pairs 1760 -> 1760 (+0); unpaired gauges left: 2200
[result] shipped pairing cannot be enlarged by this greedy pass
```
