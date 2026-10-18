# Validation and Verification Guide

**Package:** `research/u8-cleanup-markowitz-lpr-seed30`  
**Base Commit:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`  
**Assignment Seed:** `30` (Track `20–39: Complex supplier`)

---

## 1. Reproducible Verification Commands

Run the complete self-contained verification suite (including `independent.py`, `test_package.py`, and the 4-stage upstream local pipeline) under both standard isolated mode and optimized mode (`-O`, where Python `assert` statements are stripped):

```bash
python3 -I -B research/u8-cleanup-markowitz-lpr-seed30/verify.py
python3 -I -O -B research/u8-cleanup-markowitz-lpr-seed30/verify.py
```

You can also run the code-disjoint integer-lattice verifier and the 12-control adversarial mutation suite standalone:

```bash
python3 -I -B research/u8-cleanup-markowitz-lpr-seed30/independent.py
python3 -I -B research/u8-cleanup-markowitz-lpr-seed30/test_package.py
```

---

## 2. Expected Output of `verify.py`

```json
{
  "status": "PASS_U8_CLEANUP_MARKOWITZ_LPR_REFACTORIZATION",
  "seed": 30,
  "track": "20-39: Complex supplier",
  "base_commit": "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf",
  "changes_kappa": false,
  "cleanup_macros_before": 6105,
  "cleanup_macros_after": 3525,
  "cleanup_macros_saved_per_orientation": 2580,
  "cleanup_real_primitives_before": 68714,
  "cleanup_real_primitives_after": 31394,
  "cleanup_real_primitives_saved_per_orientation": 37320,
  "full_local_real_primitives_saved_pair": 74640,
  "forward_prefix_bits": {
    "before": 55,
    "after": 51,
    "delta": -4
  },
  "backward_prefix_bits": {
    "before": 72,
    "after": 54,
    "delta": -18
  },
  "independent_verifier": "PASS_INDEPENDENT_INTEGER_LATTICE_VERIFICATION",
  "negative_controls": {
    "upstream_local_rejected": 25,
    "upstream_wrapper_rejected": 17,
    "package_controls_rejected": 12
  }
}
```

---

## 3. What Is Checked

1. **Pin Verification (`SOURCES.json`):**
   - Verifies SHA-256 digests of `certificates/selected-result.json`, `research/community-frontier942-audit/t37-replay.tar.gz`, its internal members (`native/barch/FULL-WORD.json.gz`, `native/local/CANONICAL-WORD.json.gz`, `native/local/RESIDUAL-ADAPTERS.json`), `RECIPE.json`, and all upstream verifier scripts.
2. **From-Scratch Synthesis Reproduction (`verify.py`):**
   - Reconstructs $M_0 \in GL_{728}(\mathbb{Z}[1/2])$ from the baseline 6,105-gate `cleanup`, runs the seed-30 two-sided Markowitz $R^{-1} P L^{-1}$ Weyl-cycle solver (`trial = 16`, `swap_pen = 6`, `scale_pen = 0`), and checks gate-for-gate equality with `RECIPE.json` (`3,525` gates = `1,744` $R^{-1}$ + `406` $P$ across `61` cycles + `1,375` $L^{-1}$).
3. **Upstream 4-Stage Local Pipeline (`hpe_audit_and_transport.py`, `hpe_emit_local.py`, `hpe_audit_local.py`, `hpe_adapters_local.py`):**
   - Splices the 3,525-gate `FULL`-frame cleanup into the raw U8 word while preserving the exact relative positions of the 171 `early_cleanup` gates (`163` before, `8` after).
   - Verifies exact arbitrary-dirt endpoint replay across all 728 columns in both orientations, native frame monotonicity (`1,005` frames, `2,949` directed edges), paid recursive child profile (`{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}`, rank mass `5,634`), byte-identical `RESIDUAL-ADAPTERS.json` (`8b06181f...`), `25` upstream local mutation controls, and `17` upstream Clifford wrapper controls.
4. **Code-Disjoint Pure-Integer Lattice Verifier (`independent.py`):**
   - Uses pure integer scaled-row arithmetic `(coeffs_dict, shift)` without `fractions.Fraction` to verify operator equality $\operatorname{Mat}(W_{\text{LPR}}) = \operatorname{Mat}(W_{\text{baseline}})$ in both forward and dual orientations, target/HPE isolation, full 16,609-gate raw U8 endpoint exactness, and binary Horner real-component primitive counts.
5. **12-Control Package Negative Suite (`test_package.py`):**
   - Verifies that `drop_R_inv_gate`, `drop_P_cycle_gate`, `drop_L_inv_gate`, `flip_weyl_cycle_sign`, `reverse_R_inv_order`, `cleanup_touches_target`, `cleanup_touches_hpe_helper`, `cleanup_wrong_frame`, `non_dyadic_add_denominator`, `non_power_of_two_scale_numerator`, `self_addition_gate`, and `partial_e4_promotion_claim` are all rejected with their expected failure reasons.
