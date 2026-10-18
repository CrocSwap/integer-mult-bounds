# The in-repo HPE checkers do not bind the pre-wrapper recipe

**Interface audit; no new kappa.** `hpe_word_exact` concludes that a hyperplane-ended
helper stream ends as `C₇ ⊗ id` only after hypothesis `hrec`. That hypothesis
includes the existing fact `factor_iff_pre`: the pre-wrapper that ran must be
the `(E, U)` recipe, not a different recipe such as `(E, FULL)`.

The two checkers that ship in this repository do not read that recipe. This
note states the missing boundary implication and gives a synthetic witness.
It does not reprove the Clifford identities.

```sh
python3 -B research/hpe-prewrapper-binding/verify.py
```

Expected:

```text
PASS_HPE_PREWRAPPER_BINDING full_recipe_accepted=true record_optional=true phase_rejected=true coefficient_rejected=true pairs=3
```

Python 3.10+. No Lean build and no emitted HPE run.

## The boundary lemma

Let (N) hold for a certified pair (E, U): T_U T_E^{-1} = L (C_7 ⊗ id) R, with C_7 invertible. If the pre-wrapper that ran executed R'^{-1}, then L^{-1} T_U T_E^{-1} R'^{-1} = C_7 ⊗ id if and only if R' = R. A FULL recipe fails this equality when it differs from R.

This is the statement already proved as `factor_iff_pre` in
`research/hyperplane-end-lean/HyperplaneEnd/Labels.lean`. `hpe_word_exact` in
`Exact.lean` still takes `hrec` after it discharges (N) for the three certified
pairs. The arithmetic is not repeated here.

## What the checkers accept

`scripts/verify_hpe_lean_binding.py` compares `RESIDUAL-ADAPTERS.json` monomials
with the three literal Lean pairs and rejects a changed phase.
`research/hyperplane-end-lean/code/check_hpe_pairs.py` checks tail shape,
frame dimensions, the wrapper-status string, and membership in those same
pairs. Neither function reads a pre-wrapper record.

The witness is synthetic, not an emitted word. It has 38 tail gates, split
24/8/6 across the three Lean pairs, with matching adapter monomials and
`PASS_RESIDUAL_WRAPPERS_ARE_EXACT`. Every pre-wrapper record names `E:FULL`.
Both checkers accept it. Deleting the record also leaves both accepting.
Changing one adapter phase, or turning one gate into `h += p`, is rejected.
So the checkers do see monomials and the tail coefficient. They do not see
`R'`.

Acceptance of those two checkers therefore does not prove `R' = R`, and does
not discharge `hrec` in `hpe_word_exact`.

## Open next questions

Where is the control `hpe_pre_wrapper_resolved_to_full_recipe` stored, and
does a shipped artifact show that the executed pre-wrapper was the `(E, U)`
recipe? That would supply the `hrec` conjunct this audit leaves open. The
first step is to search the retained HPE tool sources for that control and
the fifth wrapper field. It is blocked here because that replay is not in
this package, and this audit does not invent its result.

## Credit and limits

The Lean interface is Jeremy Kothe's, with the multi-gate extension retained
beside it. The two checkers are the existing maintainer and instance checks.
This package only separates their acceptance from `factor_iff_pre`.

No selected certificate or kappa changes. The selected baseline was not rerun:
this sparse checkout does not contain `research/community-frontier1094-audit/ASSEMBLY.json`.
The selected record sha256 remains
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Footprints, well-labelled prefixes, the unit row, and the external wrapper
replay remain assumptions. All-size, hosting, precision and analytic assumptions
of the selected construction remain open.

Prepared by Riquelme Soares (@hevlyo) with substantial AI assistance.
Apache-2.0. No independent human peer review is asserted.
