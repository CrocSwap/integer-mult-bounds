# Branch 2: coordinated frame-schedule search

No larger verified kappa was found. Submit the inherited PR615 witness at
`1626010676080313/1000000000000000000`. `candidate/` is a byte-identical copy of
`package/`; no verifier, recipe, owner map, vendor, or proof assumption was changed.

The distinct direction was paid frame scheduling of the existing scalar word,
rather than another search for helper endpoints. Helper widths, dispatch and owner
assignments stayed fixed. Both JP8 and ATM3 final words were examined.

| Neighborhood | JP8 | ATM3 | Improving nominations |
|---|---:|---:|---:|
| Single-gate maximal frame enlargement | 4,169 gates, 185 strict legal changes | 4,205 gates, 111 strict legal changes | 0 |
| Single-gate minimal frame contraction | 4,169 gates, 248 strict legal changes | 4,205 gates, 160 strict legal changes | 0 |
| Delay across commuting gates, then enlarge | 3,139 shared-register destinations | 3,153 shared-register destinations | 0 |
| Maximal connected same-frame component enlargement | 1,336 components, 142 strict legal changes | 1,340 components, 68 strict legal changes | 0 |
| Seed enlargement with forward propagation | 7,051 seeds, 14 legal distinct changes | 7,123 seeds, 14 legal distinct changes | 0 |
| Seed contraction with backward propagation | 6,963 seeds, 56 legal distinct changes | 7,007 seeds, 64 legal distinct changes | 0 |

These are bounded searches, not an optimality theorem. In particular, the
propagation neighborhoods use the next/previous distinct frame on each operand
as seeds; they do not enumerate every subspace or every multi-gate rewrite.
The retiming search considers rightward commuting moves inside A or B only.
The component search promotes maximal connected components, not all subsets.
The cold-end cone, scalar/native, and phase checks would still be required for
any changed construction. No changed construction was admitted.

The search surrogate is `sum_r count_r * r * log(73/r)`, with fixed rank mass.
For a profile delta d, a decrease in this surrogate is equivalent to
`product_r r^(r*d_r) > 1`. This product is computed with exact Fractions. All 43
recorded delta classes give a product at most one. This is a statement about the
surrogate and the tested neighborhoods, not a claim that the full exact moment
engine rules out every such schedule. No floating-point value is used as a
certificate or submitted kappa.

`research/check_evidence.py` verifies byte identity of both packages, all 42
inherited stage log hashes, all 43 receipt artifact hashes, pinned manifests,
and final constructed-word/native-word identity. Its positive control starts
from ATM3 before the inherited frame-coalescence step and recovers exactly all
six recipe positions, each with delta `{1:-2,2:+1}` and exact proxy ratio `4`.

Reproduce the search with Python 3 standard library:

```sh
python3 -B research/frame_scan.py
python3 -B research/lower_scan.py
python3 -B research/retime_scan.py
python3 -B research/block_scan.py
python3 -B research/propagate_scan.py
python3 -B research/backward_scan.py
python3 -B research/check_evidence.py
```

The original complete replay is `verified/RESULT.json` and `verified/RECEIPT.json`.
The branch replay completed successfully in 89.617 seconds;
`branch-verified/RESULT.json` reports the same exact kappa.
The branch replay uses all unchanged constructor/control code, and reuses only
byte-identical baseline/native artifacts:

```sh
python3 -B candidate/verify.py --work NEW_WORK_DIR \
  --reuse-baseline verified/baseline558 \
  --reuse-local jp8=verified/jp8-local --reuse-local atm3=verified/atm3-local \
  --source multicold=vendor/multicold \
  --source structural_gain=vendor/structural_gain \
  --source larger_gain=vendor/larger_gain \
  --source joint_prefix=vendor/joint_prefix \
  --source frame_coalescing=vendor/frame_coalescing
```

For a completely fresh independent replay, omit the three `--reuse-*` options.
The conditional all-size compiler, interface/native realization, whole-call
hosting, precision/tape and analytic assumptions are unchanged; no unconditional
multiplication theorem is asserted.
