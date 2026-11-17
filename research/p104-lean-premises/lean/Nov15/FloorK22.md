# FloorK22.lean (+ FloorK22Data.lean): whole-floor R5's class-K(S22) floor, formalised. No sorry, 8 s / 2.9 GB (Data: 6 s / 1.6 GB)
Sources: internal notes, AUDIT5.md, r5cd.py, r5k.py; generator internal notes (+ nums.py). Imports FloorD0, JointCeiling (CallerCost), FloorEndToEnd (R1_row).
Axioms: all FloorK22 theorems [propext, Classical.choice, Quot.sound]; Data certificates [propext] or none. No native_decide. Build: Data first (`-o .lake/build/lib/lean/Nov15/FloorK22Data.olean`).

## What is a theorem
- `ClassK22` = K(S22) as AUDIT5 item 4 asks: `ClassK` for S22's kept data with `Kfin = Pub \ H` (finals of ALL kept enders, Y-enders included, are kept rows), kept arrival rows/births/snapshots fixed (K1, K2, R), per-chart kept counts and rank (`rank_ge`, `count_le`, `oa_le`), kept (main+owned) routes fixed as the multiset of |Δdim| (`keptP`: 968x1, 366x2, 103x3, 127x4, 147x5, 10x6 = 1,721 MOVEs); helpers free, verifier-accepted. "Ascending only" is not an extra restriction: public MOVEs climb in every accepted word.
- **R1 with Y in the quotient = R1_row with Kfin = all kept enders.** `R1Y_row`: hd(c) >= rk - (ka+kb) - oa. Since rk = |Y| + need and ka+kb = |Y| + kp, this is need_c - kept passers - owned entries (R5's form). It needs no new word lemma; the 748 (vs RANKSTEINER's local 685) comes from putting the Y-ender finals into K. Data check: both forms agree on all 978 charts (`control`).
- `forced_sum` (decide +kernel): sum over 978 charts of max(0, rk-ab-oa) = **748**; `forced_by_dim` = 0/122/150/109/40/29/94/96/108 (dims 0..8); `control`: kp<=ab, |Y|<=rk, need<=sigma on all 978 charts; `sums`: sum ab 2074, oa 47, kp 1274, need 2063.
- `stays_ge_748` (word level): every K22 word has >= 748 paid helper stays (sum_hd + R1Y_row + sum_fin_get + Equiv.sum_comp). `helperD0_ge_748`: helper D0 >= 748 * 2 ln 2 >= 1036.948.
- `D0_K22`: invoice D0 >= 240,134.84 (caller 270,812.8174 [numeric input `CallerD0Input`, exact 270,812.81745] + 17(748*2ln2 - kept cost); kept cost 1808 ln2 + 369 ln3 + 735 ln5 <= 2841.53492 proved: `keptExp_D0`, `log3_lt`, `log5_lt` from exp series). `D0_of_stops N` generalises; `D0_K22_R6` gives 242,420.84 CONDITIONAL on R6's 845-stop dual (not formalised).
- `helperF_le`: for every s in (0,1] and every accepted word, helper F(s) = sum (T-P) r^s <= -(2 - 2^s) * #stays (FloorD0.helperD0_ge with f = -x^s, concavity of x^s). So the F-form native floor is derived, not assumed, for class K22.
- `ceiling22`: for K22 words, F_invoice(s) < 0 for 0 < s <= 1 - tbar22, tbar22 = .0060197405, i.e. kappa <= .0060197405 (F(1-t)<0 for t in [tbar22,1)), given `NumCert22` (interval crossing of the histogram nK22 = kept P + T[2]+=748, P[1]+=1496, caller `caller 6 7`; r5k.py `cert`; hypothesis, as in JointCeiling) and the cost-model link `hF`.
- AUDIT5 scope fix: `entries_are_registers` (every helper enters a chart <= once, from l.51 via hOnce_proj) is why events = registers in dim I_C <= births + entries; `reentry_two_events` is the one-chart counterexample without ascent (1 register, 2 entry events, legal). dim I_C = sigma (registers) only because helpers ascend; owned registers may re-enter, so `oa` counts events.

## Hypotheses left (named)
1. `ClassK22.rank_ge` (+ K1/K2/R): the rank of the kept rows at each chart is >= rk. The 378-coordinate rows are not exported (as FloorEndToEnd item 2); rank mod p = 2^31-1 in r5cd.py, independently re-derived by AUDIT5.
2. Cost-model links `hnat` (D0) and `hF` (F): the word's native histogram = helper regD0 minus kept MOVE charges (the price checker; FloorD0.md).
3. `CallerD0Input` (numeric: ~70 logs of the #7113 caller) and `NumCert22` (40-digit interval covers).
4. R6's 845: LP dual over the first-hop rows; would need a new FloorCert-style export for S22 (not done).

## Statements imprecise as written (found)
- R5.md §3 composition "270,812.82 - 46,300.0 - 2,006.0 + 17 x 1,036.95 => 240,134.84" is arithmetically 240,134.97 (`recipe_as_written`). Exact: mains are -46,300.09 (4 x rounding), caller 270,812.8175, kept credits -48,306.0933 (= 17 x 2841.5349), stops +17,628.1191 (17 x 748 x 2ln2, not 17 x 1,036.95 = 17,628.15): total 240,134.843. The floor 240,134.84 is right; the displayed recipe is off by 0.13.
- AUDIT5 Fix A/B reproduced: "timing adds exactly 0" is a statement about this derivation only; events vs registers needs ascent (above).
