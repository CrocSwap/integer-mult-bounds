# SIZEY (Nov 20, Sonnet): size YFIRST's "each Y gets all deliveries on ONE chart, served by swap-couriers". Code: t1..t8.py (stdlib, run from ../yfirst; read ../fewstops/load.py; PRICEKIT histogram edit as YF size.py). t7669 ref kappa .0037214260.
Labels [C] = computed exactly on t7669's program; kappa edits are optimistic histogram edits (mains untouched, n unchanged).
## 1. Delivery charts per Y [C] (200 Y/Y2 mains; Y finals all dim 8, 104 distinct final charts, 96 Y/Y2 pairs share one)
Chains: (0,2,7,8) 63, (0,2,6,7,8) 45, (0,2,5,7,8) 34, longer 58. Y<->helper meetings at dim>=1: 876 ops (vs 26,615 at dim 0).
Distinct dim>=1 charts per Y with a helper delivery: 1:29, 2:50, 3:63, 4:53, 5:5 Ys (mean 2.78); ops per chart: 1:297, 2:221, 3+:37 charts.
Charts by dim (Y,chart pairs): d1 19, d2 101, d3 16, d5 48, d6 25, d7 148, d8 198 (357 below the final chart). Helper-Y stops: 722 of 3346 interior helper stops (21%);
584 helpers have one (466), two (98) or three (20).
Typical Y: (2:1 op, 5:1, 7:1, 8:2 ops). Pickups and deposits balance (in/out ~equal at every dim).
## 2. kappa (t7669 .0037214260)
| scenario | kappa | vs t7669 |
| V1 decoder unchanged, drop pure-Y helper stops dim 1-7 (183 stops), free couriers, no replacement stop | .0037930 | +1.9% |
| V1y drop every Y-meeting stop dim<8 (325 stops) | .0038438 | +3.3% |
| V2 drop all pure-Y stops incl dim 8 (467) | .0038632 | +3.8% |
| V3 V2 + owned-only/Y+O stops (614) = decoder charts re-chosen, Y side + owned | .0039159 | +5.2% |
| V4 V3 + X-only dim1 reads (1178 stops) = every stop with no helper partner | .0041213 | +10.7% (X-side, NOT Y consolidation) |
| chart-checked: A (70 helpers, single final chart F, top stop in F; F-stop added) | .0037326 | +0.3% |
| A+B (60 more: re-chart their tops into F) | .0037304 | +0.2% |
| A+B+C (105 helpers serving >=2 distinct F, treated free) | .0037749 | +1.4% |
| same, extra courier per extra F paid (helper 0->8->9) | .0037055 | -0.4% |
| V1y with one paid courier [0,d,8] per (Y,chart) | .0036221 | -2.7% |
| V2 with paid couriers | .0037266 | +0.1% |
Couriers add registers; they are free only in the optimistic rows.
## 3. What blocks it [P+C]
Consolidated delivery at F_s=q_s^perp needs helper (all stops) inside F_s then a jump to 9 [P: chain + ascent]. So a helper with deliveries to Ys with
different final charts cannot serve both at final charts: 105 of 235 helpers with a droppable Y stop (81 serve 2 final charts, 21 serve 3, 3 serve 4).
Pairs (s,t) share one helper's rows, i.e. multi-port decoder rows. Another 60 have a non-Y stop not inside F: 40ish are H gather-tree stops at dims 3,4,6 or X reads at dim 3,4
(XY-forced boundary of YF item 5), the rest H-only/owned at dim 6-8. Only 70/235 are chart-feasible directly.
The Y-delivery stops are only 21% of helper stops: H-H gather-tree stops (dims 2,3,6,7: ~1500) and X reads at dim 1 (~400) dominate and consolidation cannot touch them.
## Verdict
Decoder unchanged: +0.3% (chart-feasible) to +1.4% (optimistic, dubious). Decoder charts fully re-chosen, Y-side + owned, free couriers: <= +5.2%. Below the ~10% bar; only the X/tree side
(V4, +10.7%) is bigger and it is not what the redesign targets. Not worth a joint decoder+helper redesign on this prize alone. The leverage is the helper-helper tree (stop count), not Y delivery charts.
