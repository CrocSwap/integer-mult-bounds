# PROOF-NOTE-PROMO: entrance promotions E4 → E5 on the p6n word

Construction by BlockInvert (`construction/promo/`); driver `construction/promo/reproduce_promo.py`.

## What a promotion is
An entering helper h starts at an entrance frame E (its `start_extra`) and climbs to its final frame. Promotion
enlarges E to E′ ⊃ E (here dim 4 → dim 5). That removes one paid climb from h's chain (width −1 per helper) at the
cost of re-choosing the frames of the gates on h's early chain. It is the time-reverse dual of end deepening. Two
conditions make it legal:
1. **Zero target response for h's dirt.** This condition does not depend on E, so it is inherited unchanged from the
   input word.
2. **Monotone frames.** Every gate's frame must contain its registers' current frames.
Only frame annotations and start frames change. The scalar program (every gate's registers and coefficients) is
untouched, so the endpoint, every cone and the compensation are those of the input word.

## The recipe (`PROMO-RECIPE-p6n-k3.json`, data only, minimal)
- Input: the p6n word `34b683fa…` (`PROOF-NOTE-P6N.md`), pinned.
- `entrances`: the 12 entering helpers 627, 629–631, 635, 637–639, 651 and 653–655 (three E4 kernel groups) go E4 → E5.
- `gate_frames`: 36 frame re-choices, the promotion's own entry-gate raises (12 per group); each records the old frame,
  which must equal the input's exactly. This is BlockInvert's **minimal** recipe: the deterministic rule
  E′ = E + ⟨smallest x⟩ on each group's entry gates (PromoReviewer). Unlike research/gauge44-promo's k3 recipe, it
  carries none of the 72 price-neutral CP-SAT re-choices.
- `expected`: output `a38bb414…`, profile {1:2564, 2:334, 3:434, 4:190, 5:56, 8:8}, widths
  {4:76, 5:36, 7:54, 8:122, 9:216} (width 3782). Against p6n the delta is {1:+24, 2:−24, 3:−12, 4:+12}, width −12.

## Checks rerun on every rebuild (`reproduce_promo.py`)
- `build_promotion.py`: input pin; each old frame matches; each new entrance strictly contains the old one; the
  profile and widths are recomputed from the chains, including target end climbs; output pins.
- `promo_controls.py`: the honest word passes #645's independent `audit_local.py` (exact forward and dual endpoint
  frames, entrances, cones). For p6n-k3, 10 mutants are rejected at pinned sites (the count is pinned in `LOCAL-PINS-p6n-k3.json`):
  - entrance outside the first gate frame;
  - raised gate missing, once per promoted group;
  - entrance reverted, so the profile does not match;
  - ungrouped promotion;
  - a recipe gate whose old frame is wrong;
  - a recipe entry that is not a promotion;
  - a tampered input word (the constructor's own `__main__` must refuse it at the input pin);
  - a scalar tamper on a raised gate.
- The per-end layer-end controls (`../layers_p6n/layer_end_controls.py`, Q6Reviewer-signed): 95 rejected.
- PR635's native chain: transport audit (all columns, native frames), ledgers, local replay (192-bit payload),
  wrappers and phases, with the canonical word, local programs and Clifford recipes pinned (`LOCAL-PINS-p6n-k3.json`).

## Search (not run by the rebuild)
`make_recipe.py` writes the recipe from BlockInvert's CP-SAT solution (`prom.py` with `exactframe2.py`, using MinCutSel's
chain model). These promotions were priced negative before (MinCutSel #3, under a fixed-window arc-flow packer). Under
near-ideal packing (G44Pack's dissolve/gapmerge) they price positive; the strict replay confirms the gain.
