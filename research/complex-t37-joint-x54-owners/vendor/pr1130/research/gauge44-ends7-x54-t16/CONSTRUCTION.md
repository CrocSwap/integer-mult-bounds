# Complete eight-slot k8 / rank-seven-end construction

The inherited gauge44, mutable-leaver, promotion, U8 and seven-slot stages are the checked baseline. Their original recipes and proof notices remain in `construction/` and the corresponding `PROOF-NOTE-*` files. They are NOT the final provider of this package.

The reproducible changed chain is:

`checked seven-slot k8 baseline (c2b29430) → rank-seven ends574/575 (f64e0942) → X54 eighth slot (9fca1fc6) → native canonical/program/phase compilation → strict T8 → strict T16`.

`construction/ends7/verify_ends7.py` is the binding verifier. Its CLI is retained for existing dispatch, but its output marker is `PASS_RANK7_ENDS_AND_X54_ON_CHECKED_SLOT_BASELINE`. It runs the intermediate ends7 negative controls BEFORE X54, then the X54-specific builder and controls, composite native pins, independent exact audit, full PR1049 premise, and both global replays.

## Exact intermediate and final pins

- The baseline is pinned by `construction/slots/SLOT-PINS-k8.json` and must be a completed successful slot replay.
- The ends7 intermediate is pinned by `construction/ends7/ENDS7-PINS-k8.json` and `RECIPE-ENDS7-k8.json`. Its old result numbers are provenance for that stage; they are not the final bound.
- The final composite is pinned by `construction/ends7/x54/X54-PINS.json` and `RECIPE-X54-ends7.json`. The triangle builder checks both input and output content hashes.
- Binding final T8/T16 owner/spec data is `data/T8`, `data/SPEC-T8.json`, and `data/{PLAN.json,OWNERS.json.gz,SPEC.json}`.

## X54 implementation

X54/E589 is the S-register image of the existing X62 slot. The incoming arbitrary helper value is absorbed with donation922→holder367 before read1197 and donation933→holder335 before read1213 (indices refer to the U15 search word). Read assignment is {922:E,933:X,1196:E,1212:X}. The admitted native recipe uses one FULL cleanup prepend for holder335 and one rank-eight early restoration for holder367. Moving the latter to FULL fails the exact endpoint check.

Final paid profile is {1:2406,2:432,3:426,4:138,5:84,8:8}, with480 helpers and residual width3728. Helper widths are {4:56,5:32,7:32,8:120,9:240}; X54 does not change the ends7 width supply.

The unchanged scalar endpoint and inverse-transpose orientation are checked on every native column, with arbitrary dirt and all entrance/end frames. No isolated set-model estimate is used as an admission result. The PR589 bit supplier and inherited conditional assumptions remain unchanged.
