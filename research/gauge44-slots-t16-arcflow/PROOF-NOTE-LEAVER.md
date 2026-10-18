# PROOF-NOTE-LEAVER: no-helper mutable-leaver all-K cells, re-stacked layers, hybrids and a frame re-optimisation (k8)

Construction: LeaverSAT (cells, layer re-indexing, frozen recipes) and LeaverSAT2 (frame re-optimisation).
Drivers: `construction/leaver/reproduce_leaver.py` (cell word) and `construction/leaver/reproduce_leaver_chain.py`
(everything after it). Reviews: PromoReviewer (leaver chain, k8 cells and frames, k8 clean rebuild), SW4Reviewer (hybrid structure), Q6Reviewer
(`layer_end_controls_leaver.py` v2, `LEC-REASON-PINS-k8.json`), LecReviewer (`LEC-REASON-PINS-STACK-k8.json`).

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

**Set k8:** all eight cells (01±, 23±, 45±, 67±), R = 480. The cores are in `construction/leaver/cells-k8/` (documentary;
the driver re-derives every scaled gate from `CODED-CELLS-k8.json`). The regroup word is `00aeefe0…` and the cell word is
cold44 `58e14a02…`. Its pairing ranks are pinned to [0,0,0,4,4,4,4,4,4,4,4,0,0,0] in `cold44x.py` and checked again in
the driver.

## 2. Re-stacked layers (LeaverSAT; signed builders unchanged, recipes re-indexed)
| step | recipe (data) | word |
|---|---|---|
| pivot swaps (6), mapped through the leaver helper map | `PIVOT-SWAP-k8.json` | `377ab10c…` |
| HPE, greedy (22) | `HPE-RECIPE-k8.json` | `598543fa…` |
| cold44, exact (same ends, premix and tails as the unswapped cell word) | — | — |
| NP layers (s4, x30, b6, q4) | `COLD-LAYERS-RECIPE-NP-k8` | `2c1740f6…` |
| p6n ends | `COLD-LAYERS-RECIPE-P6N-k8` | `25c40614…` |
| promotions (16, minimal) | `PROMO-RECIPE-k8.json` | `84d4da2e…` |
| joint exchange (re-indexed X4) | `RECIPE-X4-k8.json` | `84d4da2e…` (identity) |
| U8-style hybrids ×6 (NewBArch's builder; instances 62, 226, 228, 230, 231, 232) | `RECIPE-U8-k8.json` | `c836d892…` |
| frame re-optimisation (exact global frame optimum, gopt2; 137 B and 2 T frames) | `FRAME-RECIPE-LV-k8.json` | **`db2c7cfb…`** |

Three steps don't apply to k8. The sw4 exchanges use copy helpers 461, 581, 591 and 603, which the cells drop. Of
#741's eight frames, none survives. All four X4 exchange groups use dropped helpers, so the joint exchange is the
identity (0 raises, 0 frames); it is still run, with its three remaining controls (C0, C1, N3) at their pins.

The two cold-layer recipes are LeaverSAT's frozen k8 recipes (`fea82fb8…`, `76aedf23…` as .gz) with one key added,
`input_content_sha256` = the swapped HPE word `598543fa…`, as in the k5 package. Removing the key gives the frozen
recipe content exactly.

## 3. Controls rerun on every rebuild
- **Cell stage:** the exact clean-map check; native audit, ledgers, local replay, wrappers and phases on the cell word.
- **Pivot swaps:** the swap constructor's 30 controls.
- **Promotions:** BlockInvert's `promo_controls.py`, 11 mutants rejected at pinned sites.
- **Joint exchange:** the 3 `RECIPE-X4-k8` controls reproduce their pinned outcomes.
- **Hybrids:** `run_controls.py` gives 30 outcomes, all required. These are C0, the recipe word passing audit_local,
  and 4 mutants, each run both globally and per instance.
- **Frames:** `build_frames_lv.py`'s 3 pin controls. LeaverSAT2's 6 frame-recipe mutants are rejected by the builder;
  that receipt was reviewed by PromoReviewer and is not rerun.
- **Layer-end controls:** `layer_end_controls_leaver.py` v2 (`4ba676f1…`), Q6Reviewer-signed. It is the signed
  per-end controls with per-word reason re-pins and **declared not-applicable sites**. A vacuous mutant site is never
  skipped silently: the pins file must declare it, the declared set must equal the detected set, an identity is proven by
  sha equality of the mutated and honest words, and a same-class substitute mutant is built and must be rejected at the
  class's pinned reason. The count stays 95 on every word. The controls run on all five words:
  - p6n, promoted, jx and hybrid words, with `LEC-REASON-PINS-STACK-k8.json`: `extra_end` only. h0 273's first
    premixed partner 282 is already cold-ended at h0's frame, so the mutant is the identity (sha-proven per word); the
    substitute is partner 281, cold-ended at h0's frame.
  - the re-framed final word, with `LEC-REASON-PINS-k8.json`: `extra_end` as above, and `other_hp:554`. The frame
    re-optimisation lowers entering end 554's tail frame to dimension 5, and no helper_final frame has dimension 5, so
    the 'end at another hyperplane' mutant cannot be built; the substitute moves 554's end to another dim-8 frame and
    must be rejected at the cone pre-check. This replaces the interim skip of research/gauge44-leaver.
  No reason re-pins are needed on the k8 words. The receipts (`COLD-END-CONTROLS.json`) carry the not-applicable list;
  the counts, the not-applicable sites with their reasons and the sha256 of each pins file (`LEC-REASON-PINS-STACK-k8.json`
  d87ed7b5…, signed by LecReviewer; `LEC-REASON-PINS-k8.json` b07279e4…, signed by Q6Reviewer) are pinned in
  `CHAIN-PINS-k8.json`.
- **Native chain on the final word:** the canonical word, local programs and Clifford recipes are pinned in
  `CHAIN-PINS-k8.json`, which also pins every count above.

## 4. Cell mutants (evidence, not rerun)
LeaverSAT2's `CELL-MUTANTS-LV.json` (in `evidence/leaver/`) records PromoReviewer's cell mutants M1–M6, generalised
to every cell sign. All 42 are rejected by both audit_local and the native audit, on single-cell builds.

## 5. Strict
The owner map is G44Pack3's K8c8: its pattern-flow LNS on the R = 480 k8 word. Admitted on this package's own code,
with SPEC `width_spot_helpers` [258,270,282,294] and `pivot_swap` → `construction/leaver/PIVOT-SWAP-k8.json` (NEWWORD
discovery, freeze, strict), it gives κ 0.001671387264390146. That is +7.154e-6 over research/gauge44-leaver (k5,
0.001664233607446043).
