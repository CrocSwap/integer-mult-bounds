# Validation and handoff

- **Base commit**: `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
- **Environment**: macOS arm64; Python 3 standard library only.
  No Linux or hosted-CI pass is implied by these local checks.

## Executed checks

1. `python3 -I -B research/u8-two-sided-biforest-seed35/verify.py`:
   - Deterministic reproduction of `RECIPE.json` and `EXPECTED.json`.
   - Exhaustive evaluation of all `12,544` target-graph edges and `46,656`
     helper-graph edges across the 5 alternating MST steps (`10,883 -> 8,373 -> 8,220 -> 8,107 -> 8,095 -> 8,021 -> 8,008 -> 7,962 -> 7,946 -> 7,930`),
     plus all `92,880` ordered helper-pair/sign cases in the PR917-style disjoint
     helper-pair comparator (`684` profitable cases, `86` disjoint pairs selected,
     panel price `8,967`).
   - Independent `check_recipe` in `independent.py` verifies `T0` (`10,883`),
     the disjoint-pair comparator (`8,967`), one-pass `H1` (`8,373`), and
     coordinate-wise MST optimality of `T5` (`12,544` target cycle-exchange
     inequalities + Prim on $C H_5^{-1}$) and `H5` (`46,656` helper cycle-exchange
     inequalities + Prim on $T_5 C$), plus two-sided matrix associativity
     $(T_5 C) H_5^{-1} = T_5 (C H_5^{-1})$.
   - Full `737`-column (`728` logical + `8` center + `1` work) forward and
     backward scalar replay under both `Fraction` and sparse integer-dyadic
     arithmetic (`193,306 -> 139,710` forward, `193,354 -> 139,758` backward,
     `53,596` real primitives saved per orientation; positive prefix peaks
     `57` bits forward and `73` bits backward; maximum exact denominator powers
     `3` forward and `19` backward).
   - Unchanged native U8 emitter (`research/complex-sw4-frame8/local/hpe_emit_local.py`)
     and auditor (`research/complex-sw4-frame8/local/hpe_audit_local.py`) pass on
     all `728` logical columns with unchanged paid profile
     `{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}` and all **25** native
     negative controls rejected.
   - **12** package negative controls rejected:
     `omitted_target_preparation` (which passes a helper-only check on `224..727`
     and fails the full `737`-column check), `omitted_helper_preparation`,
     `omitted_helper_restoration`, `omitted_target_restoration`,
     `reversed_target_preparation`, `reversed_target_restoration`,
     `reversed_helper_preparation`, `reversed_helper_restoration`,
     `wrong_helper_preparation_sign`, `wrong_residual_sign`,
     `cold_wrapped_helper_access`, and `omitted_initial_work_clear`.
2. `python3 -I -B research/u8-two-sided-biforest-seed35/test_independent.py`:
   **8 tests pass**, including depth-2 leaf-before-parent helper forest ordering,
   MST cycle-exchange and depth-order rejection, dirty private registers, and
   malformed instruction rejection.
3. `python3 -I -B research/u8-two-sided-biforest-seed35/test_package.py`:
   **7 tests pass**, including relocated source-closure verification in a
   temporary path containing spaces after gzip recompression, corrupted/missing
   source rejection, exact dirty-work replay of every emitted dyadic coefficient,
   non-scalar event preservation, and recipe tamper rejection.
4. All three commands (`verify.py`, `test_independent.py`, `test_package.py`)
   also pass under `python3 -I -B -O`.
5. `make selected-record-check` and `python3 -m unittest tests/test_selected_result.py`
   pass on the unchanged selected PR942 frontier record.

## Scope

Only `research/u8-two-sided-biforest-seed35/` is added. `upstream/`,
`certificates/selected-result.json`, and all existing files are untouched.
No new $\kappa$, no claim of joint global two-sided optimality beyond the
coordinate-wise MST fixed point, and no formal proof of the asymptotic
multiplication theorem are claimed.

Handoff PR: [CrocSwap/integer-mult-bounds#1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080).
