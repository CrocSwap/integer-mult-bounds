# Branch 3 handoff

Selected package: `package/`. Exact inherited conditional kappa: **1626010676080313/1000000000000000000**. No improvement claimed. Search frozen after 478 seconds (480-second limit).

`candidate/` is a byte-identical copy of the original package. All experiments are under `search/`; no package or vendor file changed.

## Verification

Fresh `--check-pins` passed. `search/check_baseline.py` checked 50 package files, 43 receipt artifacts, all 42 successful stage logs, all five source manifest hashes, and the exact inherited result. The complete native replay is inherited from `verified/`, not represented as newly executed here.

## Bounded negative result

All gain comparisons in the final frame screens use integers: at fixed rank mass, improvement of the first-order cost sum r log(73/r) is equivalent to product r^(r delta[r]) > 1. This is only a nomination screen, not a kappa proof.

| Screen | JP8 tested | ATM3 tested | Improving nominations |
|---|---:|---:|---:|
| Single gate interval endpoints and adjacent-rank subspaces | 795 | 633 | 0 |
| Commuting single-gate moves, endpoint frames | 6476 | 6428 | 0 |
| Equal-frame connected block endpoint changes | 198 | 108 | 0 |
| One-vector upward propagation seeds | 362543 | 362635 | 0 |
| One-hyperplane downward propagation seeds | 197727 | 200275 | 0 |

Upward propagation retained 1081 JP8 and 877 ATM3 distinct valid closures; downward propagation retained 838 and 510. These screens retain baseline start/end and cut boundaries. Single-gate move screens additionally retain every register frame at each A/B section boundary. For boundary events, the chain tally permits virtual boundary climbs; consequently it is a relaxation, and passing the screen would still require native realization and cone checks. No candidate passed the screen.

The positive control scans the pre-coalescence ATM3 word and recovers exactly the six changes in the inherited `atm3-step2-frame_coalesce.json` recipe. Cleanup equal-addition fusion across commuting gates also found zero merges (5641 JP8 and 5554 ATM3 FULL-remainder gates).

These finite searches do not exclude new paid scalar constructions, joint mutations, endpoint changes, or owner schedules. No verifier was weakened and no assumption was added.

## Reproduction

Run the commands listed in `SUBMISSION.json` from this branch directory. `FRAME-SCAN.json`, `MOVE-SCAN.json`, `BLOCK-SCAN.json`, `CLOSURE-SCAN.json`, `DOWN-CLOSURE-SCAN.json`, and `POSITIVE-CONTROL.json` contain the machine-readable results. Full inherited verification uses `package/verify.py --work <fresh-output>` and the same five `--source NAME=vendor/NAME` overrides.

No active search process remains.
