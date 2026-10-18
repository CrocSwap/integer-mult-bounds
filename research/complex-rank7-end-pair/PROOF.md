# The end pair and its complete cost

All indices below refer to PR869's pinned U8 raw word. The recipe records both
the old and new value at every changed position and checks the complete input
and output content hashes.

For both helper registers 588 and 589, replace the old dimension-eight end
with the subspace

```
U = span_GF(2) {256, 128, 96, 17, 9, 5, 3}.
```

The integers encode vectors in GF(2)^9. The seven generators are independent,
so U has 128 points. In the exact scalar prefix, inverse row 588 is
`e588 - e412`, and inverse row 589 is `e589 - e414`. Each of the two helper
dirt columns has only its diagonal entry. For each helper, the required
end-of-B frames from its inverse row span precisely U. Thus U contains the
complete inverse-row and dirt-column cones required by the retained residual
wrapper contract.

The new end requires eight B-frame changes, at zero-based positions
1018, 1019, 1050, 1051, 1130, 1131, 1162, and 1163. The two early-cleanup
frames at entries 148 and 149 also become U. No scalar gate changes. The
independent point audit checks containment for every adjacent frame, every
source and target boundary, the center interface, all paid jumps, and the
unchanged scalar program. The unchanged native auditors independently derive
the scalar prefix and check both end cones and both complete orientations.

There are eight paid changes from rank 3 to rank 2, ten from rank 1 to rank 2,
and four from rank 2 to rank 1. Therefore the local profile change is exactly

```
ΔH_local = {1:-6, 2:+14, 3:-8}.
```

Both helpers have empty entrances. Each end reduction releases one coordinate,
so the helper width becomes 3776 per call. The width inventory is
`{4:80, 5:32, 7:56, 8:120, 9:216}`. Keeping the predecessor owner assignment
would increase the complete cost. The new assignment is an essential part of
the construction.

The frozen flow lists width patterns and call counts for the 144 existing
physical windows, each with 112 ports. For a pattern used N times, each width
slot receives N items and each call supplies at most N items. Split the width
counts between those slots and add dummy slots to obtain an N-regular
bipartite multigraph. Repeated perfect matchings give N colors. Each color is
one physical bin with the stated width pattern and at most one item from any
call. Dummy slots do not create helper roles.

`build_owners.py` performs this integer construction deterministically. It
then checks the literal assignment separately: all 36,288 call/helper pairs
occur exactly once; families are distinct within each call; every role uses
a valid window; and the coordinate intervals are disjoint and fit the stated
capacity. The retained global auditor independently reconstructs the physical
windows and checks the final assignment against the native helper widths.
The complete unused-space profile is exactly `{48:2400}`.

Across all 72 calls, the global profile change from the U8 construction is

```
ΔH_global = {1:-433, 2:+1008, 3:-577, 44:-1, 48:+4}.
```

The rank mass does not change:
`-433 + 2*1008 - 3*577 - 44 + 4*48 = 0`.
The resulting mass is 520704, retaining the deficit 2560 and the same physical
geometry. The certified global prefix bound is 257 bits, within the retained
512-bit allowance. The physical row coefficient is 16467, below 20161.
Admission checks both retained rational interval engines and the complete
precision and tape invoice.

The native complex recurrence is accepted at
`b = 6659172436825204659 / 4000000000000000000000`
and rejected at `b + 10^-24`. The complete bit profile retains its bad-residue
surcharge. Both moment engines and all 47 outer inequalities certify

```
κ = 166202617947539 / 100000000000000000.
```

This exceeds the selected PR942 value by exactly
`65631761443 / 1000000000000000000`. PR942's all-replica bound fixes the
previous U8 profile and width inventory. The new helper ends change both,
so that bound does not exclude this construction.

The scalar program and its finite envelopes retain their source predicates.
The new frames, wrapper ranks, local profile, owner map, global profile,
moments, and outer witness are freshly admitted. This establishes a finite
conditional improvement under the predecessor interfaces, with the scope
stated in `README.md`.
