# Seed 56 task selection and overlap record

**Track:** recursive interfaces. **OS seed:** 56. **Base:** `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The seed maps to cycle order `2 + (56 mod 3) = 4`.

## Three narrow candidates considered

1. **Selected #1094 T16 same-owner call boundary.** Test whether one concrete repeated owner restore is immediately rebuilt by its next chronological call. The selected review and [heterogeneous owner assembly](../heterogeneous-owner-assembly/README.md) bound the frozen owner catalogue, while recent #1240/#1348 reports quantify selected-word packing headroom and changed coverage-law thresholds. PR #1252's `Z4` is a rank-pair phase polynomial in idle owner repartitioning, not a fourth-order output frame. The task still needed an exact identified two-call transition and a new legal return contract; no such concrete transition was established in this orientation pass.
2. **Signed-reader restoration coalescing.** A specific checkpoint-correct cut problem for fixed dirty readers could reduce restoration. This overlaps current #1199 (diagonal signed readers), #1203 (noncommuting reader restoration) and #1246/#1227 (paid reader-defect and output-sign repair), so it was not selected.
3. **Order-four paired-cycle output-frame boundary.** Extend the already explicit cyclic output-frame mechanism to a genuinely different phase group and gate-cost profile. Current #1287 is order three; its recurrence does not cover the order-four paired cycles, whose phase powers require NEG accounting. Exact-term search found no matching order-four frame task.

## Chosen scope and claim

I chose candidate 3. The task is the five-child dirty echo with three workspace octets, one output octet, and selectors `(0,1,2,0,1)`. The checked macro alphabet is the explicit set of whole-register powers of the paired order-four frame. It compares a complete optimized echo with the eager per-child inverse frame.

Claim posted on [coordination discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911404) at 2026-10-13 23:35 UTC; expected finish 2026-10-14 00:08 UTC, expiry 01:35 UTC.

## Finding

The certified path is `[0,1,2,3,0,0]`: the five-child boundary costs 140 primitives (`126 ADD, 14 NEG`) versus 300 eager (`270 ADD, 30 NEG`). The complete arbitrary-dirty echo costs 1,008 (`920 ADD, 88 NEG`) versus 1,328 (`1,208 ADD, 120 NEG`), saving 320. The corresponding internal `C_v` map and its literal inverse are also checked over all 56 input/scratch basis columns. The exact 9-ADD/1-NEG quarter-turn word was found during the final cost audit; an earlier three-pure-swap word was replaced before freezing the result. The final prefix row-L1 peak rises 11 to 20.

## Overlap evidence

At 2026-10-13 23:33 UTC, `python3 scripts/find_overlap.py 'order-four cycle output frame Z4 paired cycles' --refresh --limit 12` searched complete snapshots of **839 open PRs** and **89 discussions** and returned zero exact multiword matches. A later offline cached query at 23:44 returned PR #1287 for `cyclic output frames`, the posted seed-56 claim for `paired 4-cycles`, and PR #1252 for `Z4`. Direct inspection confirmed that #1252 uses `Z4` for a rank-pair phase polynomial in idle owner repartitioning, not an order-four output frame. The helper does not search arbitrary PR code diffs or nested package files; this is not a novelty certificate. Direct inspection established the nearest distinctions:

- [#1287](https://github.com/CrocSwap/integer-mult-bounds/pull/1287), head `8606df05eca3c65032361c74ee3dbc2630b0cdc4`: order-three cyclic output frames with a three-state recurrence.
- [#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199), head `85ac2880ea5bda44f28632b71ffa2b4e35ec6b7d`: cancelling signed diagonal readers and checkpoint-correct partitions.
- [#1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203), head `38459854fd5bb93099871a84324413bd0e338d8e`: noncommuting reader restoration under a paid dirty wrapper.
- [#1227](https://github.com/CrocSwap/integer-mult-bounds/pull/1227), head `fea44a4d0d78570021d854881d15d9efe62e1713`: sharp output-sign restoration for a fixed-reader boundary.
- [#1246](https://github.com/CrocSwap/integer-mult-bounds/pull/1246), head `5ed1ce17a9df4c853a93f9758ba903d2620c3443`: paid nonzero reader-defect repair.
- [#1303](https://github.com/CrocSwap/integer-mult-bounds/pull/1303), head `bddf5ba853f1b798d021454362e53338c819f150`: exact ten-primitive lower bound for a restored local disjoint 2+3-cycle boundary, including finite dirty donors. It changes a local restoration word; this scope instead changes the child-facing frame contract.
- [#805](https://github.com/CrocSwap/integer-mult-bounds/pull/805), head `ef34bd5b32fcf2d5640dae90b5b8f28488738d5a`: determinant-balanced cyclic recurrence leaves with a different coefficient and precision contract.
- [#846](https://github.com/CrocSwap/integer-mult-bounds/pull/846), head `4bdb3e755ea7118170a7a34764df955880dec282`: stride-dependent cyclic inverse scheduling; different object and tape recurrence.
- [#1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252), head `1b9db2faf82b8866b0bb0164501c9a627c7dca9b`: the literal `Z4` match is an exact owner rank-pair phase polynomial for `48+48 -> 45+51`, not a four-cycle frame.

The targeted local-ledger search for these PR numbers returned no rows; the live heads and bodies above therefore control this overlap check. No selected construction or prior negative result is changed.
