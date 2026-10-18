# Branch 4 submission

Verified exact conditional kappa: **1626010676080313339567/1000000000000000000000000** (`0.001626010676080313339567`). Exact improvement over the inherited baseline: **339567/1000000000000000000000000**.

This is an outer-witness rounding refinement. It preserves every local construction, frame schedule, owner assignment, paid cost, moment endpoint, bootstrap step, and inherited assumption. The final rational grid changes from `10^-18` to `10^-24`; the corresponding next-grid rejection becomes stricter. All 47 outer inequalities remain byte-identical in the pinned original engine. This is a small formal gain, not evidence for a better supplier.

## Evidence

- `candidate-package/`: complete copied candidate package; original `package/` retained.
- `candidate-verified/RESULT.json` and `RECEIPT.json`: successful **42-stage full fresh replay**, no baseline or local reuse, 266.8374337500427 seconds.
- All **114 assembly mutation controls** rejected; physical controller, exact native phases, moment engines, timing, and generated-identity controls passed.
- `REFINEMENT-CERTIFICATE.json`: independent exact comparison, rehashed baseline and candidate receipts, seven bootstrap steps and finite cutoffs recomputed for both models, both sets of 47 inequalities pass, next fine-grid endpoint and invalid parameter controls rejected.
- `PROOF-REFINEMENT.md`: mathematical scope and exact change.

## Reproduction

Run from this branch directory, choosing a new output directory:

```sh
python3 -B candidate-package/verify.py --work NEW_OUTPUT_DIRECTORY --source multicold=vendor/multicold --source structural_gain=vendor/structural_gain --source larger_gain=vendor/larger_gain --source joint_prefix=vendor/joint_prefix --source frame_coalescing=vendor/frame_coalescing
python3 -B verify_refinement.py
```

`verify_refinement.py` currently checks the shipped `candidate-verified/` evidence and enforces that the only package code difference is the two final-grid expressions. The new full replay can be compared against that receipt/result independently.

No outstanding computational gap remains for this refinement. The inherited all-size, interface, native realization and analytic transfer assumptions remain unchanged. No unconditional theorem is claimed.

Elapsed branch time at submission: 402 seconds. No active search or verification process remains.
