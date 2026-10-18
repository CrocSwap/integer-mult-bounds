# Seed 32: temporal gauge on the nonzero-static helper L259

**Result:** a finite scalar circuit improvement on the frozen PR1263 k8 word. The exact temporal schedule saves 111 real / 222 complex lowerer primitives per orientation. No new `κ`, native supplier admission, or hosted improvement is claimed.

## Assignment and task choice

- Track: complex supplier.
- OS-random assignment seed: `32`.
- Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Seed selection: PR1263 has 237 eligible helpers in sorted order; index `32 mod 237` selects `L259`. It has a nonzero static exponent in both orientations and lies outside PR1259's seed-37 slice `[37,53]`.

Three candidates were compared against current claims and PRs: a P120 rank-nine singleton completion (adjacent to #1212/#1213/#1360), a new helper inventory (overlap in #1240/#1348 and active claim #1328), and a temporal schedule for one nonzero-static helper. The third was selected. It studies L259, distinct from PR1350/L253, PR1353/L248, and PR1369's census of the complementary zero-static helpers.

The repository card `complex-new-helper-inventory` is marked as a changed scope in `TASK.json`: this is the user-assigned circuit/profile optimization track, and the result does not claim that its helper-inventory acceptance gate has been met.

## Reproduce

From the repository root, run:

```sh
python3 -I -O -B research/k8-l259-temporal-seed32/verify.py
```

Expected output:

```text
PASS_K8_L259_TEMPORAL_SEED32
forward helper=259 delta_real -111 complex 136002 -> 135780 scales 21 work 24 columns 712
backward helper=259 delta_real -111 complex 136018 -> 135796 scales 21 work 24 columns 712
```

`CERTIFICATE.json` freezes the 144 ADD exponents, exact finite domains, complete invoices, transition charges, paid-profile equality, and endpoint hashes. The verifier rebuilds the parent construction, checks all source pins, and includes zero-schedule, omitted-transition, constant-gauge, and small exhaustive DP controls.

## Scope and provenance

The source inventory pins the repository base and selected certificate. `DEPENDENCIES.json` pins the vendored PR1263 source blobs, PR1263 head `5fbaca13028846bddbb001e8e07addc2ab8e5816`, and the PR1259 method head `61367611154266a982fe25e1a6243a8aad77227d`. PR1263 reconstructs the frozen 218-helper scalar word; only the one seed-selected L259 schedule is varied here.

This complements Sagar Thakrar's PR1259 temporal-gauge method and Philipp / @mightyOil's PR1263 word. It is disjoint in helper and static class from PR1350/L253, PR1353/L248, and PR1369's zero-static census. Those schedules are not combined. Contributor: Cinna Davis. Substantial OpenAI Codex assistance was used for the new exact DP, event transformation, verification, and packaging.

## Open next questions

- Does a native hosted supplier realize this exact L259 word under the same precision and operation charges? This matters for a supplier admission; first integrate the schedule into the native emitter and recalculate the full hosted invoice. That integration is outside this result.
