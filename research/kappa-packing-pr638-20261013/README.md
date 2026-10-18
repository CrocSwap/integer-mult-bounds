# Three exchanges attain the fixed-dispatch packing bound

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.

Starting from verified PR638, three exchanges consolidate idle ranks `{1:1,35:1,48:2229}` into `{36:1,48:2229}`. Supplier widths, paid local profiles, and dispatch remain unchanged: 71 JP8 calls and one CK call at time5, stage2, forward orientation. This is an ownership improvement only.

The exchanged roles `(time, helper)` are `(9,10)` with `(21,423)`, then `(25,230)` with `(16,9)`, then `(22,268)` with `(16,36)`. Their widths are respectively4↔5,7↔8,8↔9. The first two exchanges move the rank1 gap without changing the idle profile; the last joins it to the rank35 gap. Intervals are then compacted chronologically in each owner.

`replay_owner_map.py` reconstructs the exact map from recorded changed rows. `replay_three_swaps.py` independently reconstructs it directly from the three exchanges. Both require the same canonical payload hash. The exporter checks every role, owner interval, window, family, width and paid profile using integer arithmetic, and offers four corruption controls. The admission path has no third-party dependencies and remains effective under optimized Python. Regenerated gzip containers may differ across zlib versions; their decompressed canonical payload is the portability check.

```sh
python3 replay_owner_map.py --base-data /path/to/PR638/witness637/data --out /tmp/owner-export --negative-controls
python3 -O replay_owner_map.py --base-data /path/to/PR638/witness637/data --out /tmp/owner-export-opt --negative-controls
python3 replay_three_swaps.py --base-data /path/to/PR638/witness637/data --out /tmp/three-swaps
```

## Optimality scope

With these fixed suppliers and dispatch, total idle rank is107028, each owner has capacity at most48, and the supplier contribution to the moment is fixed. For any exponent0<q<1, the variable cost is the sum of `r**(1-q)` over positive idle ranks. This is minimized by concentrating the ranks subject to the cap48. Indeed, transferring one unit from a smaller positive rank to a larger rank below48 cannot increase the sum, because the increments of the strictly concave function `r**(1-q)` decrease with r. Repeating this yields2229 ranks48 and one rank36, since107028=2229×48+36. Our feasible map attains this unconstrained lower bound, hence also attains the constrained minimum for this geometry and fixed dispatch. The moment is strictly increasing in q here, so its positive root, and consequently κ=q/(1+q), are maximal for this fixed setup. This does not bound improvements to suppliers, dispatch, geometry, or the overall integer multiplication construction.

The scalar construction underlying PR637 is credited to Jeremy Kothe (`jeremykothe2`); inherited inputs include Jeremy Diviney's PR627 and Jeremy Kothe's PR629. PR638's owner improvement and these three further exchanges are by Chi Zhao with substantial OpenAI Codex assistance. Exact native and global moment checks belong to the enclosing witness; exploratory floating values are not certification.
