# Discovery of the post-Design-T selections (not run by verify.sh)

Run from a scratch directory, with `W` = #354's final word (`data/designt` plus the Design T run's `frames.json` and
`249-states.json`, as produced in step 2 of `verify.sh`) and `C` = the `discovery/coll` directory of our #329 package
(`research/five-stage-p10b-transcript-stages`, PR #329).

| step | command | result |
| --- | --- | --- |
| kernel census | `census249.py W H.pkl` | 5,930 σ = 0 helpers, all reads before all touches |
| entrance pools | `C/lines.py H.pkl L.pkl 5`, `C/planes.py H.pkl P.pkl 15` | 16,793 lines; 7,039 rank 2–10 intersections |
| shared-donor closure | `ORDERS=4 NT=3 NOISE=0.5 SEED=5 C/closure_pack.py H.pkl L.pkl P.pkl K.json`, then `C/trim5.py H.pkl K.json K5.json` | 323 entries, rank 435, φ −386.03 (8 seeds: −385.14 to −386.03) |
| retiming | `to_d2pkl.py WK labels.json WK.pkl`, then `descent2_search.py WK.pkl D2.json 6` (#329's `discovery/`) | 47 gates, φ −49.68 |
| reorder | `reorder_screen.py WKD R1.json`, then the same on its output | 130 moves (φ −296.89), then 2 (φ −5.55), then 0 |

Each result is wrapped as `stages/<name>-selection.json` together with its input and output records sha256.
