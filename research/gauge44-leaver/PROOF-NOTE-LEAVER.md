# PROOF-NOTE-LEAVER: no-helper mutable-leaver all-K cells, re-stacked layers, hybrids and a frame re-optimisation (fo_hyb)

Construction: LeaverSAT (cells, layer re-indexing, frozen recipes) and LeaverSAT2 (frame re-optimisation).
Drivers: `construction/leaver/reproduce_leaver.py` (cell word) and `construction/leaver/reproduce_leaver_chain.py`
(everything after it). Reviews: PromoReviewer (leaver chain and frames), SW4Reviewer (k5 hybrids), Q6Reviewer
(`layer_end_controls_leaver.py`).

## 1. The cell (set model, LeaverSAT)
In #781's all-K cell, a pair p with sign e replaces three face events and three packet copies. Direct delivery uses
15 reads y_i += c x_j. LeaverSAT's 21-gate circuit uses the six leaver sources x_j (face-event operands with no later
reads, restored at FULL by the inherited cleanup) as mutable intermediates. It has 3 leaver gates x_k += c x_m,
3 target gates y_a += c y_b (inverted at frame zero in the precondition and scatter, #781's recipe) and 15 reads.
Coefficients are rescaled exactly per cell, C_ij = r_i c_j. The driver re-derives the scaled gates from the unit
circuit and checks the clean map Y_i = Σ_j C_ij X_j in exact rationals.

Native legality needs one relabelling: the plain circuit fails the native audit, because a y += y source carries
port-stage entering-helper dirt. Each cell is therefore relabelled by S6 so that y–y sources avoid targets carrying
entering dirt at that time.

**Set k5:** five cells (01+, 23+, 45+, 67+, 67−), R = 489. The cell word is cold44 `e10817e0…`. Its pairing ranks are
pinned to [2,2,1,4,4,4,4,4,4,4,4,2,1,1] in `cold44x.py` and checked again in the driver.

## 2. Re-stacked layers (LeaverSAT; signed builders unchanged, recipes re-indexed)
| step | recipe (data) | word |
|---|---|---|
| pivot swaps (6), mapped through the leaver helper map | `PIVOT-SWAP-k5.json` | `c3d4ecfe…` |
| HPE, greedy (31) | `HPE-RECIPE-k5.json` | `0a2c596e…` |
| cold44, exact (same ends, premix and tails as the unswapped cell word) | — | — |
| NP layers (s4, x30, b6, q4) | `COLD-LAYERS-RECIPE-NP-k5` | `ead98631…` |
| p6n ends | `COLD-LAYERS-RECIPE-P6N-k5` | `13de8d32…` |
| promotions (16, minimal) | `PROMO-RECIPE-k5.json` | `b88d5abe…` |
| joint exchange (re-indexed X4; 0 of #741's frames survive) | `RECIPE-X4-k5.json` | `d54668aa…` |
| U8-style hybrids ×7 (NewBArch's builder) | `RECIPE-U8-k5.json` | `2997cede…` |
| frame re-optimisation (exact global frame optimum, gopt2) | `FRAME-RECIPE-LV-k5.json` | **`238be1fc…`** |

Two steps don't apply to k5. The sw4 exchanges use copy helpers 461, 581, 591 and 603, which the cells drop. Of
#741's eight frames, none survives.

## 3. Controls rerun on every rebuild
- **Cell stage:** the exact clean-map check; native audit, ledgers, local replay, wrappers and phases on the cell word.
- **Pivot swaps:** the swap constructor's 30 controls.
- **Promotions:** BlockInvert's `promo_controls.py`, 11 mutants rejected at pinned sites.
- **Joint exchange:** all 7 `RECIPE-X4-k5` controls reproduce their pinned outcomes.
- **Hybrids:** `run_controls.py` gives 34 outcomes, all required. These are C0, the recipe word passing audit_local,
  and 4 mutants, each run both globally and per instance.
- **Frames:** `build_frames_lv.py`'s 3 pin controls. LeaverSAT2's 6 frame-recipe mutants are rejected by the builder;
  that receipt was reviewed by PromoReviewer and is not rerun.
- **Layer-end controls:** `layer_end_controls_leaver.py`, Q6Reviewer-signed. It is the signed per-end controls with
  one change: the expected reason of two mutants (premix_dropped, into_full) is re-pinned to the arbitrary-dirt
  endpoint, because on the leaver words those mutants are caught there first (`LEC-REASON-PINS-k5.json`). Every
  mutant must still be rejected. Each count is 95 on the p6n, promoted, jx and hybrid words. On the re-framed final word
  the controls are not run (interim skip, approved by Q6Reviewer): the frame re-optimisation lowers entering end 559's
  tail frame below the hyperplane, so the control generator cannot build its 'end at another hyperplane' mutant. The
  ends, helper_final, starts and scalar program are unchanged from the hybrid word, and the native audit of the final
  word is pinned.
- **Native chain on the final word:** the canonical word, local programs and Clifford recipes are pinned in
  `CHAIN-PINS-k5.json`, which also pins every count above.

## 4. Cell mutants (evidence, not rerun)
LeaverSAT2's `CELL-MUTANTS-LV.json` (in `evidence/leaver/`) records PromoReviewer's cell mutants M1–M6, generalised
to every cell sign. All 42 are rejected by both audit_local and the native audit, on single-cell builds.

## 5. Strict
The owner map is G44Pack3's FO_c1: its pattern-flow LNS, rebound to the R = 489 word. Admitted on this package's
own code, with SPEC `width_spot_helpers` [263,275,287,299] and `pivot_swap` → `construction/leaver/PIVOT-SWAP-k5.json`
(NEWWORD discovery, freeze, strict), it gives κ 0.001664233607446043. That is +2.599e-6 over research/gauge44-frames-x.
